"""
Hardware detection and model recommendation.
Detects CPU, GPU, VRAM, CUDA, disk space, and recommends appropriate STT model.
"""

import os
from dataclasses import dataclass, field
from typing import Optional

try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

try:
    import GPUtil

    HAS_GPUTIL = True
except ImportError:
    HAS_GPUTIL = False


@dataclass
class HardwareInfo:
    cpu_model: str = "Unknown"
    cpu_cores: int = 0
    cpu_threads: int = 0
    total_ram_gb: float = 0
    available_ram_gb: float = 0
    gpu_model: str = "None"
    gpu_vram_gb: float = 0
    cuda_version: str = "Not installed"
    cuda_available: bool = False
    disk_free_gb: float = 0
    recommended_model: str = "small"
    estimated_latency_sec: float = 3.0
    warnings: list[str] = field(default_factory=list)


class HardwareDetector:
    """Detect system hardware and recommend STT model."""

    def detect(self) -> dict:
        """Run full hardware detection and return results."""
        info = HardwareInfo()

        # ── CPU ──
        if HAS_PSUTIL:
            info.cpu_cores = psutil.cpu_count(logical=False) or 0
            info.cpu_threads = psutil.cpu_count(logical=True) or 0
            info.total_ram_gb = round(psutil.virtual_memory().total / (1024**3), 1)
            info.available_ram_gb = round(
                psutil.virtual_memory().available / (1024**3), 1
            )
            info.disk_free_gb = round(
                psutil.disk_usage(os.path.expanduser("~")).free / (1024**3), 1
            )

        # CPU model string
        try:
            import subprocess
            if os.name == "nt":
                result = subprocess.run(
                    ["wmic", "cpu", "get", "name"],
                    capture_output=True, text=True
                )
                lines = result.stdout.strip().split("\n")
                if len(lines) > 1:
                    info.cpu_model = lines[1].strip()
            elif os.uname().sysname == "Darwin":
                result = subprocess.run(
                    ["sysctl", "-n", "machdep.cpu.brand_string"],
                    capture_output=True, text=True
                )
                info.cpu_model = result.stdout.strip()
            else:
                with open("/proc/cpuinfo") as f:
                    for line in f:
                        if "model name" in line:
                            info.cpu_model = line.split(":")[1].strip()
                            break
        except Exception:
            info.cpu_model = "Unknown"

        # ── GPU ──
        if HAS_GPUTIL:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    info.gpu_model = gpu.name
                    info.gpu_vram_gb = round(gpu.memoryTotal / 1024, 1)
            except Exception:
                pass

        # CUDA
        try:
            import torch
            info.cuda_available = torch.cuda.is_available()
            if info.cuda_available:
                info.cuda_version = torch.version.cuda or "Unknown"
                if info.gpu_vram_gb == 0:
                    info.gpu_vram_gb = round(
                        torch.cuda.get_device_properties(0).total_memory / (1024**3), 1
                    )
        except ImportError:
            pass

        # ── Model Recommendation ──
        info.recommended_model, info.estimated_latency_sec = self._recommend_model(info)
        info.warnings = self._check_warnings(info)

        return {
            "cpu": {
                "model": info.cpu_model,
                "cores": info.cpu_cores,
                "threads": info.cpu_threads,
            },
            "memory": {
                "total_gb": info.total_ram_gb,
                "available_gb": info.available_ram_gb,
            },
            "gpu": {
                "model": info.gpu_model,
                "vram_gb": info.gpu_vram_gb,
                "cuda_version": info.cuda_version,
                "cuda_available": info.cuda_available,
            },
            "disk": {
                "free_gb": info.disk_free_gb,
            },
            "recommendation": {
                "model": info.recommended_model,
                "estimated_latency_sec": info.estimated_latency_sec,
            },
            "warnings": info.warnings,
        }

    def _recommend_model(self, info: HardwareInfo) -> tuple[str, float]:
        """Recommend model size based on hardware."""
        if info.cuda_available and info.gpu_vram_gb >= 6:
            return ("medium", 2.5)
        elif info.cuda_available and info.gpu_vram_gb >= 4:
            return ("small", 3.0)
        elif info.available_ram_gb >= 8:
            return ("small", 4.5)
        elif info.available_ram_gb >= 4:
            return ("tiny", 5.0)
        else:
            return ("tiny", 8.0)

    def _check_warnings(self, info: HardwareInfo) -> list[str]:
        """Check for hardware issues."""
        warnings = []
        if info.available_ram_gb < 4:
            warnings.append("内存不足 4GB，翻译可能较慢")
        if info.disk_free_gb < 5:
            warnings.append("磁盘空间不足 5GB，可能无法下载模型")
        if not info.cuda_available and info.cpu_cores < 4:
            warnings.append("无 GPU 且 CPU 核心数少，延迟可能 > 5 秒")
        return warnings
