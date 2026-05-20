"""
智核万炼® NexaForge AI - 硬件检测系统
NexaForge AI Hardware Detection System

模块化硬件检测核心，提供企业级的硬件信息获取和性能评估功能。
"""

from .models import (
    APIResponse,
    SystemInfo,
    CPUInfo,
    MemoryInfo,
    GPUInfo,
    GPUDevice,
    DiskInfo,
    NetworkInfo,
    TemperatureInfo,
    PowerInfo,
    CudaInfo,
    AIFrameworkInfo,
    HardwareSnapshot,
    TaskStatus,
    BenchmarkResult,
    HealthCheckResult,
    TrainingRecommendation,
    EnterpriseReport,
)

from .detector import HardwareDetector

__version__ = "2.0.0"
__all__ = [
    "HardwareDetector",
    "APIResponse",
    "SystemInfo",
    "CPUInfo",
    "MemoryInfo",
    "GPUInfo",
    "GPUDevice",
    "DiskInfo",
    "NetworkInfo",
    "TemperatureInfo",
    "PowerInfo",
    "CudaInfo",
    "AIFrameworkInfo",
    "HardwareSnapshot",
    "TaskStatus",
    "BenchmarkResult",
    "HealthCheckResult",
    "TrainingRecommendation",
    "EnterpriseReport",
]
