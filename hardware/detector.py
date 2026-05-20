#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智核万炼® NexaForge AI - 硬件检测核心模块 (v2.0)
Hardware Detection Core Module
"""

import os
import time
import platform
import json
import sqlite3
import subprocess
import logging
import math
import random
from typing import Dict, Any, List, Optional
from datetime import datetime
from functools import lru_cache
from cachetools import TTLCache

from .config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler("nexaforge_core.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("HardwareDetector")

VERSION = "2.0.0"

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil 不可用，部分功能可能受影响")

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import tensorflow as tf
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

try:
    import pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False

try:
    import win32com.client
    WIN32COM_AVAILABLE = True
except ImportError:
    WIN32COM_AVAILABLE = False


class HardwareDetector:
    """硬件实时检测器 v2.0"""

    def __init__(self):
        self.db_file = settings.DB_FILE
        self.max_history = settings.MAX_HISTORY
        self._init_db()
        self.history = self._load_history()
        self.app_start_time = time.time()
        self.last_disk_io = None
        self.last_disk_time = 0
        self.numa_nodes = -1
        self.heartbeat_count = 0

        # 缓存机制
        if settings.ENABLE_CACHE:
            self.cache = TTLCache(maxsize=100, ttl=settings.CACHE_TTL)
        else:
            self.cache = {}

        logger.info(f"硬件检测引擎 v{VERSION} 初始化完成")

    def _init_db(self):
        """初始化数据库"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS snapshots (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        score REAL,
                        vram_usage REAL,
                        cpu_usage REAL,
                        data_json TEXT
                    )
                ''')
                conn.commit()
                logger.info(f"数据库 {self.db_file} 初始化成功")
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")

    def _load_history(self) -> List[Dict[str, Any]]:
        """从数据库加载历史记录"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT data_json FROM snapshots ORDER BY id DESC LIMIT ?', (self.max_history,))
                rows = cursor.fetchall()
                history = [json.loads(row['data_json']) for row in rows]
                return history[::-1]
        except Exception as e:
            logger.error(f"加载历史失败: {e}")
        return []

    def _save_history(self, snapshot: Dict[str, Any]):
        """保存快照到数据库"""
        try:
            score = snapshot.get("score", 0)
            vram = snapshot.get("gpu", {}).get("vram_usage", 0)
            cpu = snapshot.get("cpu", {}).get("percent", 0)

            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO snapshots (timestamp, score, vram_usage, cpu_usage, data_json) VALUES (?, ?, ?, ?, ?)",
                    (snapshot["timestamp"], score, vram, cpu, json.dumps(snapshot, ensure_ascii=False))
                )
                conn.commit()

                cursor.execute("DELETE FROM snapshots WHERE id <= (SELECT MAX(id) - ? FROM snapshots)", (self.max_history,))
                conn.commit()
        except Exception as e:
            logger.error(f"保存历史失败: {e}")

    def _safe_exec(self, cmd: List[str], timeout: int = 5) -> Optional[str]:
        """安全的子进程执行"""
        try:
            result = subprocess.check_output(
                cmd,
                stderr=subprocess.STDOUT,
                timeout=timeout,
                shell=False
            ).decode('utf-8', errors='ignore')
            return result
        except subprocess.TimeoutExpired:
            logger.warning(f"命令执行超时: {' '.join(cmd)}")
            return None
        except Exception as e:
            logger.error(f"执行命令失败: {' '.join(cmd)}: {e}")
            return None

    def _get_from_cache(self, key: str) -> Optional[Any]:
        """从缓存获取"""
        if settings.ENABLE_CACHE and hasattr(self, 'cache'):
            return self.cache.get(key)
        return None

    def _set_cache(self, key: str, value: Any):
        """设置缓存"""
        if settings.ENABLE_CACHE and hasattr(self, 'cache'):
            self.cache[key] = value

    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        cached = self._get_from_cache("system_info")
        if cached:
            return cached

        try:
            boot_time = psutil.boot_time() if PSUTIL_AVAILABLE else 0
            info = {
                "os": f"{platform.system()} {platform.release()}",
                "os_version": platform.version(),
                "hostname": platform.node(),
                "python_version": platform.python_version(),
                "platform": platform.platform(),
                "architecture": platform.machine(),
                "boot_time": boot_time,
                "uptime": time.time() - boot_time if boot_time > 0 else 0
            }
            self._set_cache("system_info", info)
            return info
        except Exception as e:
            logger.error(f"获取系统信息失败: {e}")
            return {}

    def get_cpu_info(self) -> Dict[str, Any]:
        """获取CPU信息"""
        cached = self._get_from_cache("cpu_info")
        if cached:
            return cached

        cpu_info = {
            "count": os.cpu_count() or 0,
            "percent": 0.0,
            "freq_current": 0.0,
            "freq_max": 0.0,
            "cores": [],
            "load_avg": [0.0, 0.0, 0.0],
            "model": "未知",
            "architecture": platform.machine() or "未知"
        }

        try:
            if platform.system() == "Windows":
                import winreg
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
                cpu_info["model"] = winreg.QueryValueEx(key, "ProcessorNameString")[0]
                winreg.CloseKey(key)
        except Exception:
            pass

        if PSUTIL_AVAILABLE:
            try:
                cpu_info["percent"] = psutil.cpu_percent(interval=0.1, percpu=False)
                cpu_info["cores"] = psutil.cpu_percent(interval=0.1, percpu=True)
                freq = psutil.cpu_freq()
                if freq:
                    cpu_info["freq_current"] = freq.current
                    cpu_info["freq_max"] = freq.max
            except Exception:
                pass

        self._set_cache("cpu_info", cpu_info)
        return cpu_info

    def get_memory_info(self) -> Dict[str, Any]:
        """获取内存信息"""
        cached = self._get_from_cache("memory_info")
        if cached:
            return cached

        mem_info = {
            "total": 0.0,
            "available": 0.0,
            "used": 0.0,
            "percent": 0.0,
            "swap_total": 0.0,
            "swap_used": 0.0,
            "swap_percent": 0.0
        }

        if PSUTIL_AVAILABLE:
            try:
                mem = psutil.virtual_memory()
                swap = psutil.swap_memory()
                mem_info["total"] = mem.total / (1024**3)
                mem_info["available"] = mem.available / (1024**3)
                mem_info["used"] = mem.used / (1024**3)
                mem_info["percent"] = mem.percent
                mem_info["swap_total"] = swap.total / (1024**3)
                mem_info["swap_used"] = swap.used / (1024**3)
                mem_info["swap_percent"] = swap.percent
            except Exception as e:
                logger.error(f"获取内存信息失败: {e}")

        self._set_cache("memory_info", mem_info)
        return mem_info

    def get_gpu_info(self) -> Dict[str, Any]:
        """获取GPU信息"""
        cached = self._get_from_cache("gpu_info")
        if cached:
            return cached

        gpu_info = {
            "available": False,
            "count": 0,
            "devices": [],
            "cuda_available": False,
            "cuda_version": ""
        }

        if PYNVML_AVAILABLE:
            try:
                pynvml.nvmlInit()
                gpu_info["cuda_available"] = True
                driver_version = pynvml.nvmlSystemGetDriverVersion()
                gpu_info["cuda_version"] = driver_version
                device_count = pynvml.nvmlDeviceGetCount()
                gpu_info["count"] = device_count
                gpu_info["available"] = device_count > 0

                for i in range(device_count):
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    name = pynvml.nvmlDeviceGetName(handle)
                    memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)

                    device = {
                        "id": i,
                        "name": name,
                        "memory_total": memory_info.total / (1024**3),
                        "memory_used": memory_info.used / (1024**3),
                        "memory_free": memory_info.free / (1024**3),
                        "utilization": utilization.gpu,
                        "memory_percent": (memory_info.used / memory_info.total) * 100 if memory_info.total > 0 else 0,
                        "temperature": 0,
                        "power_draw": 0
                    }

                    try:
                        device["temperature"] = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                    except Exception:
                        pass

                    try:
                        power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0
                        device["power_draw"] = power
                    except Exception:
                        pass

                    gpu_info["devices"].append(device)

                pynvml.nvmlShutdown()
            except Exception as e:
                logger.warning(f"GPU 检测失败: {e}")

        self._set_cache("gpu_info", gpu_info)
        return gpu_info

    def get_disk_info(self) -> Dict[str, Any]:
        """获取磁盘信息"""
        disk_info = {
            "total": 0.0,
            "used": 0.0,
            "free": 0.0,
            "percent": 0.0,
            "partitions": []
        }

        if PSUTIL_AVAILABLE:
            try:
                partitions = psutil.disk_partitions()
                for partition in partitions:
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        disk_info["partitions"].append({
                            "device": partition.device,
                            "mountpoint": partition.mountpoint,
                            "fstype": partition.fstype,
                            "total": usage.total / (1024**3),
                            "used": usage.used / (1024**3),
                            "free": usage.free / (1024**3),
                            "percent": usage.percent
                        })
                        disk_info["total"] += usage.total / (1024**3)
                        disk_info["used"] += usage.used / (1024**3)
                        disk_info["free"] += usage.free / (1024**3)
                    except Exception:
                        pass
                if disk_info["total"] > 0:
                    disk_info["percent"] = (disk_info["used"] / disk_info["total"]) * 100
            except Exception as e:
                logger.error(f"获取磁盘信息失败: {e}")

        return disk_info

    def get_network_info(self) -> Dict[str, Any]:
        """获取网络信息"""
        network_info = {
            "interfaces": [],
            "total_bytes_sent": 0,
            "total_bytes_recv": 0
        }

        if PSUTIL_AVAILABLE:
            try:
                net_io = psutil.net_io_counters()
                network_info["total_bytes_sent"] = net_io.bytes_sent
                network_info["total_bytes_recv"] = net_io.bytes_recv

                interfaces = psutil.net_if_addrs()
                for iface, addrs in interfaces.items():
                    for addr in addrs:
                        if addr.family.name == 'AF_INET':
                            network_info["interfaces"].append({
                                "name": iface,
                                "address": addr.address,
                                "netmask": addr.netmask
                            })
            except Exception as e:
                logger.error(f"获取网络信息失败: {e}")

        return network_info

    def get_temperature_info(self) -> Dict[str, Any]:
        """获取温度信息"""
        temp_info = {
            "cpu_temp": 0.0,
            "gpu_temp": 0.0,
            "available": False,
            "details": {}
        }

        if PSUTIL_AVAILABLE:
            try:
                try:
                    temps = psutil.sensors_temperatures()
                    if temps:
                        for name, entries in temps.items():
                            for entry in entries:
                                if 'cpu' in name.lower():
                                    temp_info["cpu_temp"] = entry.current
                                temp_info["details"][name] = entry.current
                        temp_info["available"] = True
                except Exception:
                    pass
            except Exception as e:
                logger.error(f"获取温度信息失败: {e}")

        return temp_info

    def get_power_info(self) -> Dict[str, Any]:
        """获取电源信息"""
        power_info = {
            "battery_percent": 0,
            "battery_charging": False,
            "power_plugged": False,
            "performance_mode": "未知",
            "power_plan": ""
        }

        if PSUTIL_AVAILABLE:
            try:
                battery = psutil.sensors_battery()
                if battery:
                    power_info["battery_percent"] = battery.percent
                    power_info["battery_charging"] = battery.is_charging
                    power_info["power_plugged"] = battery.power_plugged
            except Exception:
                pass

        if platform.system() == "Windows":
            try:
                result = self._safe_exec(
                    ["powershell", "-Command",
                     "powercfg /getactivescheme"],
                    timeout=3
                )
                if result:
                    power_info["power_plan"] = result.split("(")[-1].split(")")[0] if "(" in result else ""
                    if "High performance" in result or "高性能" in result:
                        power_info["performance_mode"] = "高性能"
                    elif "Ultimate Performance" in result or "卓越性能" in result:
                        power_info["performance_mode"] = "卓越性能"
                    elif "Balanced" in result or "平衡" in result:
                        power_info["performance_mode"] = "平衡"
                    elif "Power saver" in result or "节能" in result:
                        power_info["performance_mode"] = "节能"
            except Exception:
                pass

        return power_info

    def get_cuda_info(self) -> Dict[str, Any]:
        """获取CUDA信息"""
        cuda_info = {
            "available": False,
            "version": "",
            "cudnn_version": "",
            "device_count": 0,
            "devices": []
        }

        if TORCH_AVAILABLE:
            try:
                cuda_info["available"] = torch.cuda.is_available()
                if cuda_info["available"]:
                    cuda_info["version"] = torch.version.cuda
                    cuda_info["device_count"] = torch.cuda.device_count()
                    for i in range(cuda_info["device_count"]):
                        device_props = torch.cuda.get_device_properties(i)
                        cuda_info["devices"].append({
                            "id": i,
                            "name": device_props.name,
                            "total_memory": device_props.total_memory / (1024**3),
                            "compute_capability": f"{device_props.major}.{device_props.minor}"
                        })
            except Exception as e:
                logger.warning(f"PyTorch CUDA 检测失败: {e}")

        return cuda_info

    def get_ai_framework_info(self) -> Dict[str, Any]:
        """获取AI框架信息"""
        framework_info = {
            "torch_available": TORCH_AVAILABLE,
            "torch_version": "",
            "tensorflow_available": TENSORFLOW_AVAILABLE,
            "tensorflow_version": "",
            "packages": []
        }

        if TORCH_AVAILABLE:
            try:
                framework_info["torch_version"] = torch.__version__
                framework_info["packages"].append({
                    "name": "PyTorch",
                    "version": torch.__version__
                })
            except Exception:
                pass

        if TENSORFLOW_AVAILABLE:
            try:
                framework_info["tensorflow_version"] = tf.__version__
                framework_info["packages"].append({
                    "name": "TensorFlow",
                    "version": tf.__version__
                })
            except Exception:
                pass

        return framework_info

    def get_numa_nodes(self) -> int:
        """获取NUMA节点数"""
        if self.numa_nodes >= 0:
            return self.numa_nodes

        if PSUTIL_AVAILABLE:
            try:
                self.numa_nodes = len(psutil.cpu_count(logical=False) or os.cpu_count())
            except Exception:
                self.numa_nodes = 1
        else:
            self.numa_nodes = 1

        return self.numa_nodes

    def calculate_hardware_score(self, snapshot: Dict[str, Any]) -> int:
        """计算硬件综合评分"""
        score = 0

        cpu_count = snapshot["cpu"]["count"]
        if cpu_count >= 64:
            score += 35
        elif cpu_count >= 32:
            score += 30
        elif cpu_count >= 16:
            score += 25
        elif cpu_count >= 8:
            score += 20
        elif cpu_count >= 4:
            score += 15
        else:
            score += 10

        memory_gb = snapshot["memory"]["total"]
        if memory_gb >= 256:
            score += 30
        elif memory_gb >= 128:
            score += 25
        elif memory_gb >= 64:
            score += 20
        elif memory_gb >= 32:
            score += 15
        elif memory_gb >= 16:
            score += 10
        else:
            score += 5

        gpu_available = snapshot["gpu"]["available"]
        if gpu_available:
            gpu_devices = snapshot["gpu"]["devices"]
            if gpu_devices:
                vram = gpu_devices[0].get("memory_total", 0)
                if vram >= 40:
                    score += 35
                elif vram >= 24:
                    score += 30
                elif vram >= 12:
                    score += 25
                elif vram >= 8:
                    score += 20
                elif vram >= 4:
                    score += 15
                else:
                    score += 10

        return min(100, score)

    def get_training_recommendations(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """获取训练推荐"""
        score = self.calculate_hardware_score(snapshot)
        gpu_available = snapshot["gpu"]["available"]
        max_model = "1B"
        mode = "standard"
        estimated_time = "1-2小时"

        if score >= 90 and gpu_available:
            max_model = "70B+"
            mode = "premium"
            estimated_time = "5-15分钟"
        elif score >= 75 and gpu_available:
            max_model = "34B"
            mode = "enterprise"
            estimated_time = "15-30分钟"
        elif score >= 60 and gpu_available:
            max_model = "13B"
            mode = "professional"
            estimated_time = "30-60分钟"
        elif score >= 40:
            max_model = "7B"
            mode = "standard"
            estimated_time = "1-2小时"
        elif score >= 25:
            max_model = "3B"
            mode = "basic"
            estimated_time = "2-4小时"
        else:
            max_model = "1B"
            mode = "entry"
            estimated_time = "4-8小时"

        return {
            "score": score,
            "max_model_size": max_model,
            "recommended_mode": mode,
            "estimated_time": estimated_time,
            "gpu_accelerated": gpu_available,
            "suitable_models": self._get_suitable_models(snapshot)
        }

    def _get_suitable_models(self, snapshot: Dict[str, Any]) -> List[str]:
        """获取适合的模型列表"""
        models = []
        gpu_available = snapshot["gpu"]["available"]

        if gpu_available:
            gpu_devices = snapshot["gpu"]["devices"]
            if gpu_devices:
                vram = gpu_devices[0].get("memory_total", 0)
                if vram >= 40:
                    models = ["Llama-70B", "Mistral-70B", "Qwen-72B", "Gemma-70B"]
                elif vram >= 24:
                    models = ["Llama-34B", "Mistral-8x7B", "Qwen-32B"]
                elif vram >= 12:
                    models = ["Llama-13B", "Mistral-7B", "Qwen-14B", "Gemma-9B"]
                elif vram >= 8:
                    models = ["Llama-7B", "Gemma-7B", "Qwen-7B", "TinyLlama"]
                else:
                    models = ["TinyLlama-1B", "Gemma-2B", "Qwen-1.8B"]
        else:
            models = ["TinyLlama-1B", "Gemma-2B"]

        return models

    def get_hardware_snapshot(self) -> Dict[str, Any]:
        """获取完整硬件快照 (v2.0 - 唯一版本)"""
        self.heartbeat_count += 1

        try:
            snapshot = {
                "version": VERSION,
                "timestamp": datetime.now().isoformat(),
                "heartbeat": self.heartbeat_count,
                "uptime_seconds": int(time.time() - self.app_start_time),
                "score": 0,
                "system": self.get_system_info(),
                "cpu": self.get_cpu_info(),
                "memory": self.get_memory_info(),
                "gpu": self.get_gpu_info(),
                "disk": self.get_disk_info(),
                "network": self.get_network_info(),
                "temperature": self.get_temperature_info(),
                "power": self.get_power_info(),
                "cuda": self.get_cuda_info(),
                "ai_frameworks": self.get_ai_framework_info(),
                "numa_nodes": self.get_numa_nodes()
            }

            snapshot["score"] = self.calculate_hardware_score(snapshot)
            recommendations = self.get_training_recommendations(snapshot)
            snapshot["recommendations"] = recommendations

            self.history.append(snapshot)
            if len(self.history) > self.max_history:
                self.history.pop(0)

            if self.heartbeat_count % 5 == 0:
                self._save_history(snapshot)

            return snapshot
        except Exception as e:
            logger.error(f"生成快照失败: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    def get_history(self) -> List[Dict[str, Any]]:
        """获取历史数据"""
        return self.history

    def run_benchmark_cpu(self, duration: float = 5.0) -> Dict[str, Any]:
        """CPU性能基准测试"""
        result = {
            "status": "running",
            "score": 0,
            "operations_per_second": 0,
            "duration": 0,
            "error": None
        }

        try:
            start_time = time.time()
            operations = 0

            while time.time() - start_time < duration / 2:
                for _ in range(10000):
                    x = random.random()
                    y = random.random()
                    z = math.sin(x) * math.cos(y) + math.sqrt(x * x + y * y)
                operations += 10000

            array = list(range(10000))
            while time.time() - start_time < duration:
                sum_val = sum(x * x for x in array)
                operations += 10000

            elapsed = time.time() - start_time
            ops_per_sec = int(operations / elapsed)
            score = min(100, int(ops_per_sec / 10000))

            result["status"] = "completed"
            result["score"] = score
            result["operations_per_second"] = ops_per_sec
            result["duration"] = elapsed

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)

        return result

    def run_benchmark_memory(self) -> Dict[str, Any]:
        """内存性能基准测试"""
        result = {
            "status": "running",
            "score": 0,
            "read_bandwidth_gb_s": 0,
            "write_bandwidth_gb_s": 0,
            "error": None
        }

        try:
            import time
            data_size = 100 * 1024 * 1024
            data = bytearray(data_size)

            start = time.time()
            for _ in range(100):
                _ = bytes(data)
            read_time = time.time() - start
            read_bw = (data_size * 100) / (read_time * (1024**3))

            start = time.time()
            for _ in range(100):
                data = bytearray(data_size)
            write_time = time.time() - start
            write_bw = (data_size * 100) / (write_time * (1024**3))

            score = min(100, int((read_bw + write_bw) / 20))

            result["status"] = "completed"
            result["score"] = score
            result["read_bandwidth_gb_s"] = round(read_bw, 2)
            result["write_bandwidth_gb_s"] = round(write_bw, 2)

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)

        return result

    def check_hardware_health(self) -> Dict[str, Any]:
        """硬件健康检查"""
        snapshot = self.get_hardware_snapshot()
        health = {
            "status": "healthy",
            "score": 100,
            "checks": [],
            "warnings": [],
            "errors": []
        }

        if snapshot["cpu"]["percent"] > 90:
            health["warnings"].append(f"CPU 使用率过高: {snapshot['cpu']['percent']}%")

        if snapshot["memory"]["percent"] > 90:
            health["warnings"].append(f"内存使用率过高: {snapshot['memory']['percent']}%")

        if snapshot["gpu"]["available"]:
            gpu = snapshot["gpu"]["devices"][0]
            if gpu.get("temperature", 0) > 85:
                health["warnings"].append(f"GPU 温度过高: {gpu['temperature']}°C")
            if gpu.get("memory_percent", 0) > 95:
                health["warnings"].append("GPU 显存几乎用尽")

        if health["warnings"]:
            health["status"] = "warning"
            health["score"] = max(50, 100 - len(health["warnings"]) * 10)

        if health["errors"]:
            health["status"] = "critical"
            health["score"] = max(0, 50 - len(health["errors"]) * 20)

        return health

    def generate_enterprise_report(self) -> Dict[str, Any]:
        """生成企业级报告"""
        snapshot = self.get_hardware_snapshot()
        report = {
            "timestamp": datetime.now().isoformat(),
            "version": VERSION,
            "summary": {
                "hardware_score": snapshot["score"],
                "ai_readiness": snapshot["score"] >= 60,
                "gpu_available": snapshot["gpu"]["available"]
            },
            "hardware_details": snapshot,
            "recommendations": []
        }

        if snapshot["score"] < 40:
            report["recommendations"].append({
                "priority": "high",
                "message": "建议升级硬件以获得更好的 AI 训练体验"
            })

        if not snapshot["gpu"]["available"]:
            report["recommendations"].append({
                "priority": "high",
                "message": "建议配置 NVIDIA GPU 以加速模型训练"
            })

        return report


# 全局单例
detector = HardwareDetector()
