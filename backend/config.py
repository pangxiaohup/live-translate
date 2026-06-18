"""
Configuration management for Python backend.
Reads from environment variables with sensible defaults.
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Config:
    # ── Server ──
    host: str = "127.0.0.1"
    port: int = 0  # 0 = auto-assign

    # ── Logging ──
    log_level: str = "INFO"

    # ── Pipeline ──
    sample_rate: int = 16000
    channels: int = 1
    sample_width: int = 2  # 16-bit
    ring_buffer_duration_sec: float = 10.0
    ring_buffer_high_watermark: float = 0.8

    # ── VAD ──
    vad_threshold: float = 0.5
    vad_min_speech_duration_ms: int = 250
    vad_min_silence_duration_ms: int = 300
    vad_speech_pad_ms: int = 100
    vad_max_segment_duration_ms: int = 5000

    # ── STT ──
    stt_model_size: str = "small"  # tiny | small | medium | large-v3
    stt_backend: str = "faster-whisper"  # faster-whisper | whisper-cpp
    stt_device: str = "auto"  # auto | cpu | cuda
    stt_compute_type: str = "auto"  # auto | float16 | int8

    # ── Translation ──
    translation_backends: list = field(default_factory=lambda: [
        {"name": "libretranslate", "enabled": True, "priority": 1},
        {"name": "argos", "enabled": True, "priority": 2},
        {"name": "deepl", "enabled": False, "priority": 3},
        {"name": "gpt-4o-mini", "enabled": False, "priority": 4},
    ])
    translation_cache_ttl_sec: int = 30
    translation_cache_max_entries: int = 2000
    translation_timeout_sec: float = 3.0

    # ── Delay ──
    total_delay_seconds: float = 5.0

    # ── Paths ──
    models_dir: str = field(default_factory=lambda: os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "resources", "models"
    ))

    def to_dict(self) -> dict:
        """Return safe subset of config."""
        return {
            "sample_rate": self.sample_rate,
            "stt_model_size": self.stt_model_size,
            "stt_backend": self.stt_backend,
            "stt_device": self.stt_device,
            "translation_backends": self.translation_backends,
            "total_delay_seconds": self.total_delay_seconds,
        }

    @classmethod
    def from_env(cls) -> "Config":
        """Create config from environment variables."""
        return cls(
            host=os.environ.get("LIVE_TRANSLATE_HOST", "127.0.0.1"),
            port=int(os.environ.get("LIVE_TRANSLATE_PORT", "0")),
            log_level=os.environ.get("LIVE_TRANSLATE_LOG_LEVEL", "INFO"),
            stt_model_size=os.environ.get("LIVE_TRANSLATE_STT_MODEL", "small"),
            stt_device=os.environ.get("LIVE_TRANSLATE_STT_DEVICE", "auto"),
            total_delay_seconds=float(
                os.environ.get("LIVE_TRANSLATE_DELAY", "5.0")
            ),
        )


# Global config instance
config = Config.from_env()
