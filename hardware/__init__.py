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
from .compute_evaluator import ComputeEvaluator, GPUDatabase, ModelDatabase
from .compute_routes import router as compute_router

__version__ = "2.1.0"
__all__ = [
    "HardwareDetector",
    "ComputeEvaluator",
    "GPUDatabase",
    "ModelDatabase",
    "compute_router",
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
