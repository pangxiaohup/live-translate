"""
WebSocket handler for real-time communication between Python backend and Electron renderer.
"""

import asyncio
import json
import time
from typing import Any

from fastapi import WebSocket
from utils.logger import get_logger
from utils.metrics import metrics

logger = get_logger(__name__)


class WebSocketHandler:
    """Manages WebSocket connections and message routing."""

    def __init__(self):
        self._connections: dict[str, WebSocket] = {}
        self._pipeline_task: asyncio.Task | None = None
        self._pipeline_status = "idle"

    @property
    def pipeline_status(self) -> str:
        return self._pipeline_status

    async def connect(self, ws: WebSocket) -> None:
        """Accept a new WebSocket connection."""
        await ws.accept()
        client_id = f"{ws.client.host}:{ws.client.port}"
        self._connections[client_id] = ws
        logger.info("WebSocket client connected", client_id=client_id)

        # Send initial status
        await ws.send_json({
            "type": "status",
            "data": {
                "pipeline": self._pipeline_status,
                "server_version": "0.1.0",
                "timestamp": time.time(),
            }
        })

    async def disconnect(self, ws: WebSocket) -> None:
        """Handle client disconnect."""
        client_id = f"{ws.client.host}:{ws.client.port}"
        self._connections.pop(client_id, None)
        logger.info("WebSocket client disconnected", client_id=client_id)

    async def handle_message(self, ws: WebSocket, data: dict) -> None:
        """Route incoming messages based on type."""
        msg_type = data.get("type", "")

        handlers = {
            "start_pipeline": self._handle_start_pipeline,
            "stop_pipeline": self._handle_stop_pipeline,
            "pause_pipeline": self._handle_pause_pipeline,
            "resume_pipeline": self._handle_resume_pipeline,
            "update_config": self._handle_update_config,
            "ping": self._handle_ping,
            "audio_chunk": self._handle_audio_chunk,
        }

        handler = handlers.get(msg_type)
        if handler:
            await handler(ws, data)
        else:
            logger.warning("Unknown message type", type=msg_type)

    async def broadcast(self, msg: dict) -> None:
        """Send a message to all connected clients."""
        disconnected = []
        for client_id, ws in self._connections.items():
            try:
                await ws.send_json(msg)
            except Exception:
                disconnected.append(client_id)

        for client_id in disconnected:
            self._connections.pop(client_id, None)

    async def broadcast_transcript(self, segment: dict) -> None:
        """Broadcast a transcript segment update."""
        await self.broadcast({
            "type": "transcript_update",
            "data": segment,
        })

    async def broadcast_translation(self, translation: dict) -> None:
        """Broadcast a translation update."""
        await self.broadcast({
            "type": "translation_update",
            "data": translation,
        })

    async def broadcast_status(self) -> None:
        """Broadcast current pipeline status to all clients."""
        await self.broadcast({
            "type": "status",
            "data": {
                "pipeline": self._pipeline_status,
                "metrics": metrics.to_dict(),
                "timestamp": time.time(),
            }
        })

    async def shutdown(self) -> None:
        """Shutdown all connections and cleanup."""
        logger.info("Shutting down WebSocket handler")
        if self._pipeline_task and not self._pipeline_task.done():
            self._pipeline_task.cancel()

        for client_id, ws in list(self._connections.items()):
            try:
                await ws.close()
            except Exception:
                pass
        self._connections.clear()
        logger.info("WebSocket handler shut down")

    # ── Message Handlers ──────────────────────────────────────

    async def _handle_start_pipeline(self, ws: WebSocket, data: dict) -> None:
        self._pipeline_status = "running"
        await self.broadcast_status()
        logger.info("Pipeline started via WebSocket")

    async def _handle_stop_pipeline(self, ws: WebSocket, data: dict) -> None:
        self._pipeline_status = "idle"
        await self.broadcast_status()
        logger.info("Pipeline stopped via WebSocket")

    async def _handle_pause_pipeline(self, ws: WebSocket, data: dict) -> None:
        self._pipeline_status = "paused"
        await self.broadcast_status()

    async def _handle_resume_pipeline(self, ws: WebSocket, data: dict) -> None:
        self._pipeline_status = "running"
        await self.broadcast_status()

    async def _handle_update_config(self, ws: WebSocket, data: dict) -> None:
        # Config updates will be handled in later phases
        logger.info("Config update received", config=data.get("config", {}))

    async def _handle_ping(self, ws: WebSocket, data: dict) -> None:
        await ws.send_json({"type": "pong", "timestamp": time.time()})

    async def _handle_audio_chunk(self, ws: WebSocket, data: dict) -> None:
        # Audio chunks from Streamer Mode (Electron → Python)
        # Will be wired to orchestrator in Phase 2
        pass
