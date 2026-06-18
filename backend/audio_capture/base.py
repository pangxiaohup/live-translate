"""
Abstract base class for audio capture sources.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class AudioDevice:
    """Audio device information."""
    id: str
    name: str
    is_default: bool = False
    sample_rate: int = 48000
    channels: int = 2


class AbstractCaptureSource(ABC):
    """
    Abstract base for audio capture sources.

    Implementations:
    - SystemAudioCapture (default): System audio loopback
    - DirectStreamCapture: yt-dlp/streamlink direct URL
    - MicrophoneCapture: getUserMedia mic input
    - WebSocketAudioCapture: Audio received from Electron (Streamer Mode)
    """

    @abstractmethod
    async def start(self) -> None:
        """Start audio capture."""
        ...

    @abstractmethod
    async def stop(self) -> None:
        """Stop audio capture."""
        ...

    @abstractmethod
    async def read_chunk(self) -> bytes:
        """
        Read the next audio chunk.
        Returns raw PCM bytes (16kHz, mono, 16-bit).
        """
        ...

    @abstractmethod
    async def list_devices(self) -> list[AudioDevice]:
        """List available audio devices."""
        ...

    @property
    @abstractmethod
    def is_capturing(self) -> bool:
        """Whether capture is active."""
        ...

    @property
    @abstractmethod
    def sample_rate(self) -> int:
        """Output sample rate (always 16000 after normalization)."""
        ...
