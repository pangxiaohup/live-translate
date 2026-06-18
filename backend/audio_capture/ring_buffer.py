"""
Thread-safe ring buffer for audio data.
"""

import threading
from collections import deque
from dataclasses import dataclass


@dataclass
class BufferStats:
    """Ring buffer statistics."""
    capacity_sec: float
    current_sec: float
    fill_level: float  # 0.0 - 1.0
    total_written_bytes: int
    total_read_bytes: int
    dropped_chunks: int


class RingBuffer:
    """
    Thread-safe ring buffer for audio PCM data.

    Stores raw PCM bytes with configurable capacity in seconds.
    Supports backpressure: when buffer exceeds high watermark,
    oldest chunks are dropped.
    """

    def __init__(
        self,
        capacity_sec: float = 10.0,
        sample_rate: int = 16000,
        sample_width: int = 2,
        high_watermark: float = 0.8,
    ):
        bytes_per_sec = sample_rate * sample_width
        capacity_bytes = int(capacity_sec * bytes_per_sec)

        self._buffer: deque[bytes] = deque()
        self._capacity_bytes = capacity_bytes
        self._current_bytes: int = 0
        self._sample_rate = sample_rate
        self._sample_width = sample_width
        self._high_watermark = high_watermark
        self._lock = threading.Lock()

        # Stats
        self._total_written: int = 0
        self._total_read: int = 0
        self._dropped_chunks: int = 0

    def write(self, data: bytes) -> None:
        """Write audio data to the buffer."""
        with self._lock:
            # Check backpressure
            if self._current_bytes + len(data) > self._capacity_bytes * self._high_watermark:
                # Drop oldest chunk(s) until we're under watermark
                while (
                    self._current_bytes + len(data) > self._capacity_bytes * self._high_watermark
                    and self._buffer
                ):
                    old = self._buffer.popleft()
                    self._current_bytes -= len(old)
                    self._dropped_chunks += 1

            self._buffer.append(data)
            self._current_bytes += len(data)
            self._total_written += len(data)

    def read(self, max_bytes: int | None = None) -> bytes:
        """Read audio data from the buffer. Returns empty bytes if no data."""
        with self._lock:
            if not self._buffer:
                return b""

            chunk = self._buffer.popleft()
            self._current_bytes -= len(chunk)
            self._total_read += len(chunk)

            if max_bytes and len(chunk) > max_bytes:
                # Put back the excess
                excess = chunk[max_bytes:]
                self._buffer.appendleft(excess)
                self._current_bytes += len(excess)
                self._total_read -= len(excess)
                chunk = chunk[:max_bytes]

            return chunk

    def read_all(self) -> bytes:
        """Read all available data from the buffer."""
        with self._lock:
            data = b"".join(self._buffer)
            self._total_read += self._current_bytes
            self._current_bytes = 0
            self._buffer.clear()
            return data

    @property
    def stats(self) -> BufferStats:
        """Get current buffer statistics."""
        with self._lock:
            bytes_per_sec = self._sample_rate * self._sample_width
            return BufferStats(
                capacity_sec=self._capacity_bytes / bytes_per_sec,
                current_sec=self._current_bytes / bytes_per_sec,
                fill_level=self._current_bytes / self._capacity_bytes
                if self._capacity_bytes > 0
                else 0,
                total_written_bytes=self._total_written,
                total_read_bytes=self._total_read,
                dropped_chunks=self._dropped_chunks,
            )

    def clear(self) -> None:
        """Clear the buffer."""
        with self._lock:
            self._buffer.clear()
            self._current_bytes = 0
