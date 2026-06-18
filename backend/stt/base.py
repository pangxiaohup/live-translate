"""
Abstract base class for STT (Speech-to-Text) engines.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class STTResult:
    """Result from STT transcription."""
    text: str
    language: str
    start_ms: int
    end_ms: int
    confidence: float = 1.0
    is_partial: bool = False
    words: list[dict] | None = None  # Word-level timestamps


class AbstractSTTEngine(ABC):
    """
    Abstract base for STT engines.

    Implementations:
    - FasterWhisperEngine: faster-whisper (CTranslate2), primary
    - WhisperCppEngine: whisper.cpp, CPU fallback
    """

    @abstractmethod
    async def load_model(self, size: str = "small", device: str = "auto") -> None:
        """Load the STT model."""
        ...

    @abstractmethod
    async def transcribe(self, audio: bytes, language: str = "auto") -> STTResult:
        """
        Transcribe audio bytes to text.

        Args:
            audio: Raw PCM bytes (16kHz, mono, 16-bit)
            language: Language code or 'auto'

        Returns:
            STTResult with transcribed text and timestamps
        """
        ...

    @abstractmethod
    async def warmup(self) -> None:
        """Warm up the model (run a dummy transcription)."""
        ...

    @property
    @abstractmethod
    def model_size(self) -> str:
        """Current model size."""
        ...

    @property
    @abstractmethod
    def is_loaded(self) -> bool:
        """Whether model is loaded."""
        ...
