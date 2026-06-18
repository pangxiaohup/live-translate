"""
Pipeline Orchestrator — the central coordinator.
Wires together: AudioCapture → VAD → STT → SentenceSegmenter → TranslationQueue → SubtitleQueue
"""

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, AsyncIterator

from utils.logger import get_logger
from utils.metrics import metrics

logger = get_logger(__name__)


class PipelineStatus(Enum):
    IDLE = "idle"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    ERROR = "error"
    DEGRADED = "degraded"


@dataclass
class TranscriptSegment:
    """A segment of transcribed text."""
    id: str
    text: str
    language: str
    start_ms: int
    end_ms: int
    is_partial: bool = False
    confidence: float = 1.0


@dataclass
class TranslationResult:
    """A translated segment."""
    id: str
    original_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    start_ms: int
    end_ms: int
    is_partial: bool = False
    backend: str = "libretranslate"


@dataclass
class PipelineState:
    """Current state of the pipeline."""
    status: PipelineStatus = PipelineStatus.IDLE
    source_language: str = "auto"
    target_languages: list[str] = field(default_factory=list)
    total_delay_seconds: float = 5.0
    start_time: Optional[float] = None
    segments_processed: int = 0
    errors: list[str] = field(default_factory=list)


class PipelineOrchestrator:
    """
    Central orchestrator for the live translation pipeline.

    Coordinates:
    1. Audio input → RingBuffer
    2. VAD processing → speech segments
    3. STT transcription
    4. Sentence segmentation
    5. Translation to target languages
    6. Output via SubtitleQueue → WebSocket broadcast
    """

    def __init__(self):
        self.state = PipelineState()
        self._stop_event = asyncio.Event()
        self._audio_queue: asyncio.Queue = asyncio.Queue(maxsize=1000)
        self._output_queue: asyncio.Queue = asyncio.Queue(maxsize=500)

        # Components (initialized lazily)
        self._vad = None
        self._stt_engine = None
        self._translator = None
        self._sentence_segmenter = None

    async def start(
        self,
        source_lang: str = "auto",
        target_langs: list[str] | None = None,
        delay_seconds: float = 5.0,
    ) -> None:
        """Start the pipeline."""
        if self.state.status == PipelineStatus.RUNNING:
            logger.warning("Pipeline already running")
            return

        self.state.status = PipelineStatus.STARTING
        self.state.source_language = source_lang
        self.state.target_languages = target_langs or ["en"]
        self.state.total_delay_seconds = delay_seconds
        self.state.start_time = time.time()
        self.state.segments_processed = 0
        self._stop_event.clear()

        logger.info(
            "Starting pipeline",
            source_lang=source_lang,
            target_langs=target_langs,
            delay=delay_seconds,
        )

        try:
            # Initialize components
            await self._init_components()

            self.state.status = PipelineStatus.RUNNING
            metrics.pipeline_status = "running"

            # Run the main loop
            await self._run_loop()

        except Exception as e:
            logger.error("Pipeline error", error=str(e))
            self.state.status = PipelineStatus.ERROR
            self.state.errors.append(str(e))
            metrics.pipeline_status = "error"
            raise

    async def stop(self) -> None:
        """Stop the pipeline gracefully."""
        logger.info("Stopping pipeline...")
        self.state.status = PipelineStatus.STOPPING
        self._stop_event.set()
        self.state.status = PipelineStatus.IDLE
        metrics.pipeline_status = "idle"
        logger.info("Pipeline stopped")

    async def pause(self) -> None:
        """Pause the pipeline (keeps buffer)."""
        self.state.status = PipelineStatus.PAUSED

    async def resume(self) -> None:
        """Resume a paused pipeline."""
        if self.state.status == PipelineStatus.PAUSED:
            self.state.status = PipelineStatus.RUNNING

    async def feed_audio(self, audio_chunk: bytes) -> None:
        """Feed raw PCM audio data into the pipeline."""
        try:
            self._audio_queue.put_nowait(audio_chunk)
        except asyncio.QueueFull:
            # Backpressure: drop oldest chunk
            try:
                self._audio_queue.get_nowait()
                self._audio_queue.put_nowait(audio_chunk)
            except (asyncio.QueueEmpty, asyncio.QueueFull):
                pass
            logger.debug("Audio queue full, dropping oldest chunk")

    async def get_output(self) -> AsyncIterator[TranscriptSegment | TranslationResult]:
        """Get pipeline output as an async iterator."""
        while not self._stop_event.is_set():
            try:
                item = await asyncio.wait_for(
                    self._output_queue.get(), timeout=0.5
                )
                yield item
            except asyncio.TimeoutError:
                continue

    async def _init_components(self) -> None:
        """Initialize pipeline components (placeholders for now)."""
        # These will be fully implemented in Phase 2
        logger.info("Pipeline components initialized (skeleton mode)")

    async def _run_loop(self) -> None:
        """Main pipeline processing loop."""
        logger.info("Pipeline main loop started")

        while not self._stop_event.is_set():
            try:
                # Get audio chunk
                chunk = await asyncio.wait_for(
                    self._audio_queue.get(), timeout=1.0
                )

                # TODO: Full pipeline processing
                # 1. VAD → detect speech/silence
                # 2. Accumulate speech segments
                # 3. STT → transcribe
                # 4. Sentence segmentation
                # 5. Translation → fan-out to N languages
                # 6. SubtitleQueue → push to output

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error("Pipeline loop error", error=str(e))
                self.state.errors.append(str(e))
                if len(self.state.errors) > 5:
                    self.state.status = PipelineStatus.DEGRADED
                    metrics.pipeline_status = "degraded"

        logger.info("Pipeline main loop ended")


# Global orchestrator instance
orchestrator = PipelineOrchestrator()
