"""
Live Translate — Python Backend Entry Point
FastAPI + WebSocket server for real-time audio processing pipeline.
"""

import asyncio
import os
import sys
import signal
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from config import config
from utils.logger import setup_logging, get_logger
from utils.hardware_detect import HardwareDetector
from pipeline.websocket_handler import WebSocketHandler

# ─── App Setup ─────────────────────────────────────────────────

app = FastAPI(
    title="Live Translate Backend",
    version="0.1.0",
    docs_url=None,        # Disable docs in production
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = get_logger(__name__)

# Global state
ws_handler = WebSocketHandler()
pipeline_task: asyncio.Task | None = None


# ─── WebSocket Endpoint ────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """Main WebSocket endpoint for real-time transcript streaming."""
    await ws_handler.connect(ws)
    try:
        while True:
            # Receive messages from client (control commands, audio chunks)
            data = await ws.receive_json()
            await ws_handler.handle_message(ws, data)
    except WebSocketDisconnect:
        await ws_handler.disconnect(ws)
    except Exception as e:
        logger.error("WebSocket error", error=str(e))
        await ws_handler.disconnect(ws)


# ─── REST Endpoints ────────────────────────────────────────────

@app.get("/health")
async def health_check():
    """Health check endpoint for Electron main process."""
    return {
        "status": "ok",
        "version": "0.1.0",
        "pipeline": ws_handler.pipeline_status,
    }


@app.get("/hardware")
async def hardware_info():
    """Return hardware detection results."""
    detector = HardwareDetector()
    return detector.detect()


@app.get("/config")
async def get_config():
    """Return current configuration (safe subset)."""
    return config.to_dict()


# ─── Shutdown ──────────────────────────────────────────────────

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global pipeline_task
    logger.info("Shutting down backend...")
    if pipeline_task and not pipeline_task.done():
        pipeline_task.cancel()
        try:
            await pipeline_task
        except asyncio.CancelledError:
            pass
    await ws_handler.shutdown()


# ─── Entry Point ───────────────────────────────────────────────

def main():
    """Entry point for Electron to spawn the Python backend."""
    setup_logging(config.log_level)

    port = int(os.environ.get("LIVE_TRANSLATE_PORT", "0"))
    host = os.environ.get("LIVE_TRANSLATE_HOST", "127.0.0.1")

    logger.info("Starting Live Translate backend", host=host, port=port or "auto")

    uvicorn.run(
        "main:app",
        host=host,
        port=port if port else 0,
        log_level=config.log_level.lower(),
        access_log=False,
    )


if __name__ == "__main__":
    main()
