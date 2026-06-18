"""
Pipeline metrics collection: latency, buffer levels, throughput.
"""

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PipelineMetrics:
    """Real-time metrics for the translation pipeline."""

    # Latency (ms)
    audio_capture_latency_ms: float = 0
    vad_latency_ms: float = 0
    stt_latency_ms: float = 0
    translation_latency_ms: float = 0
    total_e2e_latency_ms: float = 0

    # Buffer
    ring_buffer_level: float = 0.0  # 0.0 - 1.0
    subtitle_queue_size: int = 0

    # Throughput
    audio_bytes_per_sec: float = 0
    stt_chars_per_sec: float = 0
    translations_per_sec: float = 0

    # Status
    pipeline_status: str = "idle"  # idle | running | error | degraded
    errors: list[str] = field(default_factory=list)

    # Timing history (for rolling averages)
    _stt_latencies: deque = field(default_factory=lambda: deque(maxlen=30))
    _translation_latencies: deque = field(default_factory=lambda: deque(maxlen=30))

    def record_stt_latency(self, ms: float) -> None:
        self.stt_latency_ms = ms
        self._stt_latencies.append(ms)

    def record_translation_latency(self, ms: float) -> None:
        self.translation_latency_ms = ms
        self._translation_latencies.append(ms)

    def record_e2e_latency(self, start_time: float) -> None:
        self.total_e2e_latency_ms = (time.time() - start_time) * 1000

    @property
    def avg_stt_latency_ms(self) -> float:
        if not self._stt_latencies:
            return 0
        return sum(self._stt_latencies) / len(self._stt_latencies)

    @property
    def avg_translation_latency_ms(self) -> float:
        if not self._translation_latencies:
            return 0
        return sum(self._translation_latencies) / len(self._translation_latencies)

    def to_dict(self) -> dict:
        return {
            "audio_capture_latency_ms": self.audio_capture_latency_ms,
            "stt_latency_ms": self.stt_latency_ms,
            "avg_stt_latency_ms": round(self.avg_stt_latency_ms, 1),
            "translation_latency_ms": self.translation_latency_ms,
            "avg_translation_latency_ms": round(self.avg_translation_latency_ms, 1),
            "total_e2e_latency_ms": self.total_e2e_latency_ms,
            "ring_buffer_level": round(self.ring_buffer_level, 2),
            "subtitle_queue_size": self.subtitle_queue_size,
            "pipeline_status": self.pipeline_status,
        }


# Global metrics instance
metrics = PipelineMetrics()
