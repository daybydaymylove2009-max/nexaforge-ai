#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智核万炼® NexaForge AI - 硬件检测系统 Pydantic 数据模型
NexaForge AI Hardware Detection System Pydantic Models
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class APIResponse(BaseModel):
    """统一 API 响应格式"""
    code: int = Field(default=200, description="状态码")
    message: str = Field(default="success", description="响应消息")
    data: Optional[Any] = Field(default=None, description="响应数据")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="时间戳")


class SystemInfo(BaseModel):
    """系统信息模型"""
    os: str = "未知"
    os_version: str = ""
    hostname: str = ""
    python_version: str = ""
    platform: str = ""
    architecture: str = ""
    boot_time: float = 0
    uptime: float = 0


class CPUInfo(BaseModel):
    """CPU 信息模型"""
    count: int = 0
    percent: float = 0.0
    freq_current: float = 0.0
    freq_max: float = 0.0
    cores: List[float] = []
    load_avg: List[float] = [0.0, 0.0, 0.0]
    model: str = "未知"
    architecture: str = "未知"


class MemoryInfo(BaseModel):
    """内存信息模型"""
    total: float = 0.0
    available: float = 0.0
    used: float = 0.0
    percent: float = 0.0
    swap_total: float = 0.0
    swap_used: float = 0.0
    swap_percent: float = 0.0


class GPUDevice(BaseModel):
    """GPU 设备信息模型"""
    id: int = 0
    name: str = "未知"
    memory_total: float = 0.0
    memory_used: float = 0.0
    memory_free: float = 0.0
    utilization: float = 0.0
    temperature: float = 0.0
    power_draw: float = 0.0
    cuda_version: str = ""


class GPUInfo(BaseModel):
    """GPU 信息模型"""
    available: bool = False
    count: int = 0
    devices: List[GPUDevice] = []
    cuda_available: bool = False
    cuda_version: str = ""


class DiskInfo(BaseModel):
    """磁盘信息模型"""
    total: float = 0.0
    used: float = 0.0
    free: float = 0.0
    percent: float = 0.0
    partitions: List[Dict[str, Any]] = []


class NetworkInfo(BaseModel):
    """网络信息模型"""
    interfaces: List[Dict[str, Any]] = []
    total_bytes_sent: int = 0
    total_bytes_recv: int = 0


class TemperatureInfo(BaseModel):
    """温度信息模型"""
    cpu_temp: float = 0.0
    gpu_temp: float = 0.0
    available: bool = False
    details: Dict[str, Any] = {}


class PowerInfo(BaseModel):
    """电源信息模型"""
    battery_percent: int = 0
    battery_charging: bool = False
    power_plugged: bool = False
    performance_mode: str = "未知"
    power_plan: str = ""


class CudaInfo(BaseModel):
    """CUDA 信息模型"""
    available: bool = False
    version: str = ""
    cudnn_version: str = ""
    device_count: int = 0
    devices: List[Dict[str, Any]] = []


class AIFrameworkInfo(BaseModel):
    """AI 框架信息模型"""
    torch_available: bool = False
    torch_version: str = ""
    tensorflow_available: bool = False
    tensorflow_version: str = ""
    packages: List[Dict[str, str]] = []


class HardwareSnapshot(BaseModel):
    """硬件快照完整模型"""
    version: str = "2.0.0"
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    heartbeat: int = 0
    uptime_seconds: int = 0
    system: SystemInfo = SystemInfo()
    cpu: CPUInfo = CPUInfo()
    memory: MemoryInfo = MemoryInfo()
    gpu: GPUInfo = GPUInfo()
    disk: DiskInfo = DiskInfo()
    network: NetworkInfo = NetworkInfo()
    temperature: TemperatureInfo = TemperatureInfo()
    power: PowerInfo = PowerInfo()
    cuda: CudaInfo = CudaInfo()
    ai_frameworks: AIFrameworkInfo = AIFrameworkInfo()


class TaskStatus(BaseModel):
    """异步任务状态模型"""
    task_id: str = ""
    status: str = "pending"  # pending, running, completed, failed
    progress: int = 0
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None


class BenchmarkResult(BaseModel):
    """基准测试结果模型"""
    status: str = "pending"
    score: int = 0
    operations_per_second: int = 0
    duration: float = 0.0
    error: Optional[str] = None
    details: Dict[str, Any] = {}


class HealthCheckResult(BaseModel):
    """健康检查结果模型"""
    status: str = "healthy"
    score: int = 100
    checks: List[Dict[str, Any]] = []
    warnings: List[str] = []
    errors: List[str] = []


class TrainingRecommendation(BaseModel):
    """训练推荐模型"""
    score: int = 0
    max_model_size: str = "1B"
    recommended_mode: str = "standard"
    mode_details: Dict[str, Any] = {}
    suitable_models: List[str] = []
    estimated_time: str = ""
    suggestions: List[str] = []


class EnterpriseReport(BaseModel):
    """企业级报告模型"""
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    summary: Dict[str, Any] = {}
    hardware_details: Dict[str, Any] = {}
    ai_readiness: Dict[str, Any] = {}
    recommendations: List[Dict[str, Any]] = []
    benchmark_results: Dict[str, Any] = {}
    score: int = 0
