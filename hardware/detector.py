#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智核万炼® NexaForge AI - 硬件检测核心模块 (v2.1)
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
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .config import settings
from .resilience import CircuitBreaker, retry_on_failure

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler("nexaforge_core.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("HardwareDetector")

VERSION = "2.1.0"

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
    """硬件实时检测器 v2.1 - 增强版"""

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
        self.last_snapshot = None

        # 缓存机制
        if settings.ENABLE_CACHE:
            self.cache = TTLCache(maxsize=100, ttl=settings.CACHE_TTL)
        else:
            self.cache = {}

        # 断路器 - 防止级联故障
        self.gpu_circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60.0)
        self.db_circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30.0)

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

    def get_motherboard_info(self) -> Dict[str, Any]:
        mb_info = {
            "manufacturer": "未知",
            "model": "未知",
            "version": "未知",
            "serial_number": "未知",
            "bios_vendor": "未知",
            "bios_version": "未知",
            "bios_release_date": "未知",
            "chipset": "未知",
            "cpu_model": "未知"
        }

        try:
            if platform.system() == "Windows":
                ps_commands = [
                    "Get-WmiObject -Class Win32_BaseBoard | Select-Object -Property Manufacturer,Product,Version,SerialNumber | ConvertTo-Json",
                    "Get-WmiObject -Class Win32_BIOS | Select-Object -Property Manufacturer,SMBIOSBIOSVersion,ReleaseDate | ConvertTo-Json",
                    "Get-WmiObject -Class Win32_Processor | Select-Object -Property Name | ConvertTo-Json"
                ]

                for cmd in ps_commands:
                    try:
                        result = self._safe_exec(
                            ["powershell", "-Command", cmd],
                            timeout=10
                        )
                        if result and result.strip():
                            import json as _json
                            try:
                                data = _json.loads(result)
                                if isinstance(data, list):
                                    data = data[0]
                                if 'Manufacturer' in data and 'Product' in data:
                                    mb_info["manufacturer"] = data.get('Manufacturer', '').strip() or "未知"
                                    mb_info["model"] = data.get('Product', '').strip() or "未知"
                                    mb_info["version"] = data.get('Version', '').strip() or "未知"
                                    mb_info["serial_number"] = data.get('SerialNumber', '').strip() or "未知"
                                elif 'SMBIOSBIOSVersion' in data:
                                    mb_info["bios_vendor"] = data.get('Manufacturer', '').strip() or "未知"
                                    mb_info["bios_version"] = data.get('SMBIOSBIOSVersion', '').strip() or "未知"
                                    mb_info["bios_release_date"] = data.get('ReleaseDate', '').strip() or "未知"
                                elif 'Name' in data:
                                    mb_info["cpu_model"] = data.get('Name', '').strip() or "未知"
                            except _json.JSONDecodeError:
                                pass
                    except Exception:
                        pass

            elif platform.system() == "Linux":
                try:
                    with open('/sys/class/dmi/id/board_vendor', 'r') as f:
                        mb_info["manufacturer"] = f.read().strip()
                except Exception:
                    pass
                try:
                    with open('/sys/class/dmi/id/board_name', 'r') as f:
                        mb_info["model"] = f.read().strip()
                except Exception:
                    pass
                try:
                    with open('/sys/class/dmi/id/board_version', 'r') as f:
                        mb_info["version"] = f.read().strip()
                except Exception:
                    pass
                try:
                    with open('/sys/class/dmi/id/bios_vendor', 'r') as f:
                        mb_info["bios_vendor"] = f.read().strip()
                except Exception:
                    pass
                try:
                    with open('/sys/class/dmi/id/bios_version', 'r') as f:
                        mb_info["bios_version"] = f.read().strip()
                except Exception:
                    pass
                try:
                    with open('/proc/cpuinfo', 'r') as f:
                        for line in f:
                            if line.startswith('model name'):
                                mb_info["cpu_model"] = line.split(':')[1].strip()
                                break
                except Exception:
                    pass

        except Exception:
            pass

        return mb_info

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
        disk_info = {
            "total": 0.0,
            "used": 0.0,
            "free": 0.0,
            "percent": 0.0,
            "partitions": [],
            "main": None,
            "read_mbs": 0.0,
            "write_mbs": 0.0
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

                main_disk = None
                for part in disk_info["partitions"]:
                    if "C:" in part["device"] or "/" == part["mountpoint"]:
                        main_disk = dict(part)
                        break

                if main_disk:
                    main_disk["type"] = "Unknown"
                    if platform.system() == "Windows":
                        try:
                            cmd = "Get-PhysicalDisk | Select-Object DeviceId, MediaType | ConvertTo-Json"
                            stdout = self._safe_exec(["powershell", "-Command", cmd], timeout=5)
                            if stdout and stdout.strip():
                                import json as _json
                                disk_data = _json.loads(stdout)
                                if isinstance(disk_data, list):
                                    if len(disk_data) > 0 and disk_data[0]:
                                        main_disk["type"] = disk_data[0].get("MediaType", "Unknown")
                                elif disk_data:
                                    main_disk["type"] = disk_data.get("MediaType", "Unknown")
                        except Exception:
                            pass
                    elif platform.system() == "Linux":
                        try:
                            for dev in os.listdir('/sys/block'):
                                if dev.startswith('sd') or dev.startswith('nvme'):
                                    with open(f'/sys/block/{dev}/queue/rotational', 'r') as f:
                                        is_rotational = f.read().strip() == '1'
                                        main_disk["type"] = "HDD" if is_rotational else "SSD"
                                        if dev.startswith('nvme'):
                                            main_disk["type"] = "NVMe SSD"
                                        break
                        except Exception:
                            pass

                if main_disk:
                    disk_info["main"] = main_disk
            except Exception as e:
                logger.error(f"获取磁盘信息失败: {e}")

        if PSUTIL_AVAILABLE:
            try:
                current_time = time.time()
                current_io = psutil.disk_io_counters()
                if current_io and self.last_disk_io and self.last_disk_time > 0:
                    time_diff = current_time - self.last_disk_time
                    if time_diff > 0:
                        read_bytes = current_io.read_bytes - self.last_disk_io.read_bytes
                        write_bytes = current_io.write_bytes - self.last_disk_io.write_bytes
                        disk_info["read_mbs"] = max(0, (read_bytes / time_diff) / (1024 * 1024))
                        disk_info["write_mbs"] = max(0, (write_bytes / time_diff) / (1024 * 1024))

                self.last_disk_io = current_io
                self.last_disk_time = current_time
            except Exception:
                pass

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

    def _wake_gpu_read_temp(self) -> int:
        try:
            import threading
            import time as _time

            result_temp = [0]

            def _gpu_stress():
                try:
                    import ctypes
                    d3d9 = ctypes.windll.LoadLibrary("d3d9.dll")
                    d3d9.Direct3DCreate9(31)
                    _time.sleep(1.5)
                except Exception:
                    pass

            stress_thread = threading.Thread(target=_gpu_stress, daemon=True)
            stress_thread.start()
            _time.sleep(0.5)

            if PYNVML_AVAILABLE:
                try:
                    pynvml.nvmlInit()
                    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                    for _ in range(5):
                        temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                        if temp > 0:
                            result_temp[0] = temp
                            break
                        _time.sleep(0.5)
                    pynvml.nvmlShutdown()
                except Exception:
                    pass

            if result_temp[0] == 0:
                try:
                    result = self._safe_exec(
                        ["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader,nounits"],
                        timeout=5
                    )
                    if result and result.strip().isdigit():
                        t = int(result.strip())
                        if t > 0:
                            result_temp[0] = t
                except Exception:
                    pass

            stress_thread.join(timeout=3)
            return result_temp[0]
        except Exception:
            return 0

    def get_temperature_info(self) -> Dict[str, Any]:
        temp_info = {
            "cpu_temp": 0.0,
            "gpu_temp": 0.0,
            "available": False,
            "details": {},
            "cpu": "未知",
            "gpu": "待机中",
            "motherboard": "未知",
            "sources": []
        }

        try:
            if platform.system() == "Windows" and WIN32COM_AVAILABLE:
                try:
                    import win32com.client
                    wmi = win32com.client.GetObject("winmgmts:")

                    for sensor in wmi.InstancesOf("Win32_TemperatureProbe"):
                        try:
                            name = str(sensor.Name).lower() if sensor.Name else ""
                            current_temp = sensor.CurrentReading
                            if current_temp and current_temp > 0:
                                temp_celsius = current_temp / 10.0
                                temp_info["sources"].append(f"WMI: {sensor.Name}")

                                if "cpu" in name or "processor" in name:
                                    if temp_info["cpu"] == "未知":
                                        temp_info["cpu"] = f"{round(temp_celsius)}°C"
                                        temp_info["cpu_temp"] = temp_celsius
                                elif "motherboard" in name or "system" in name or "board" in name:
                                    if temp_info["motherboard"] == "未知":
                                        temp_info["motherboard"] = f"{round(temp_celsius)}°C"
                        except Exception:
                            pass
                except Exception:
                    pass

            if platform.system() == "Windows":
                try:
                    result = self._safe_exec(
                        ["powershell", "-Command",
                         "Get-WmiObject -Class Win32_PerfFormattedData_Counters_ThermalZoneInformation | Select-Object -Property Name,Temperature | ConvertTo-Json"],
                        timeout=10
                    )
                    if result and result.strip():
                        import json as _json
                        try:
                            data = _json.loads(result)
                            if isinstance(data, list):
                                data = data[0]
                            if 'Temperature' in data and data['Temperature'] > 0:
                                temp_celsius = data['Temperature'] / 10.0
                                if temp_info["cpu"] == "未知":
                                    temp_info["cpu"] = f"{round(temp_celsius)}°C"
                                    temp_info["cpu_temp"] = temp_celsius
                                temp_info["sources"].append("PowerShell: Win32_PerfFormattedData")
                        except _json.JSONDecodeError:
                            pass
                except Exception:
                    pass

            if PSUTIL_AVAILABLE and hasattr(psutil, 'sensors_temperatures'):
                try:
                    temps = psutil.sensors_temperatures()
                    if temps:
                        if 'coretemp' in temps:
                            cpu_temps = [t.current for t in temps['coretemp']]
                            if cpu_temps:
                                avg_temp = sum(cpu_temps) / len(cpu_temps)
                                if temp_info["cpu"] == "未知":
                                    temp_info["cpu"] = f"{round(avg_temp)}°C"
                                    temp_info["cpu_temp"] = avg_temp
                                temp_info["sources"].append("psutil: coretemp")

                        if 'acpitz' in temps:
                            mb_temps = [t.current for t in temps['acpitz']]
                            if mb_temps and temp_info["motherboard"] == "未知":
                                temp_info["motherboard"] = f"{round(sum(mb_temps)/len(mb_temps))}°C"
                                temp_info["sources"].append("psutil: acpitz")

                        for name, entries in temps.items():
                            for entry in entries:
                                temp_info["details"][name] = entry.current

                        temp_info["available"] = True
                except Exception:
                    pass

            if platform.system() == "Linux":
                try:
                    import glob as _glob
                    for path in _glob.glob('/sys/class/hwmon/hwmon*/temp1_input'):
                        try:
                            with open(path, 'r') as f:
                                temp = int(f.read().strip()) / 1000
                                if temp > 0 and temp_info["motherboard"] == "未知":
                                    temp_info["motherboard"] = f"{round(temp)}°C"
                                    temp_info["sources"].append("sysfs: motherboard")
                        except Exception:
                            pass
                except Exception:
                    pass

            gpu_temp_obtained = False
            if PYNVML_AVAILABLE:
                try:
                    pynvml.nvmlInit()
                    device_count = pynvml.nvmlDeviceGetCount()
                    if device_count > 0:
                        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                        temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                        if temp > 0:
                            temp_info["gpu"] = f"{temp}°C"
                            temp_info["gpu_temp"] = float(temp)
                            temp_info["sources"].append("NVML")
                            gpu_temp_obtained = True
                        else:
                            try:
                                power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0
                                utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
                                pstate = ""
                                try:
                                    pstate_result = self._safe_exec(
                                        ["nvidia-smi", "--query-gpu=pstate", "--format=csv,noheader"],
                                        timeout=3
                                    )
                                    if pstate_result:
                                        pstate = pstate_result.strip()
                                except Exception:
                                    pass

                                if "P8" in pstate or power < 5:
                                    temp_info["gpu"] = "待机中 (P8)"
                                    temp_info["gpu_temp"] = 0.0
                                    temp_info["sources"].append("NVML+P8检测")
                                    gpu_temp_obtained = True

                                    try:
                                        wake_temp = self._wake_gpu_read_temp()
                                        if wake_temp > 0:
                                            temp_info["gpu"] = f"{wake_temp}°C"
                                            temp_info["gpu_temp"] = float(wake_temp)
                                            temp_info["sources"].append("NVML+GPU唤醒探测")
                                    except Exception:
                                        pass
                                elif power > 1 or utilization.gpu > 1:
                                    temp_info["gpu"] = f"{temp}°C (传感器待机)"
                                    temp_info["gpu_temp"] = float(temp)
                                    temp_info["sources"].append("NVML")
                                    gpu_temp_obtained = True
                            except Exception:
                                pass
                    pynvml.nvmlShutdown()
                except Exception:
                    pass

            if not gpu_temp_obtained:
                try:
                    result = self._safe_exec(
                        ["nvidia-smi", "--query-gpu=temperature.gpu,power.draw,fan.speed,utilization.gpu", "--format=csv,noheader,nounits"],
                        timeout=5
                    )
                    if result and result.strip():
                        parts = result.strip().split(',')
                        if parts:
                            temp_value = parts[0].strip()
                            if temp_value.isdigit():
                                temp_int = int(temp_value)
                                if temp_int > 0:
                                    temp_info["gpu"] = f"{temp_int}°C"
                                    temp_info["gpu_temp"] = float(temp_int)
                                    temp_info["sources"].append("nvidia-smi")
                                    gpu_temp_obtained = True
                                elif len(parts) > 1 and parts[1].strip():
                                    try:
                                        power = float(parts[1].strip())
                                        if power > 1:
                                            temp_info["gpu"] = "低功耗模式"
                                            temp_info["sources"].append("nvidia-smi")
                                            gpu_temp_obtained = True
                                    except Exception:
                                        pass
                except Exception:
                    pass

            if not gpu_temp_obtained:
                temp_info["gpu"] = "不支持"

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
                logger.warning(f"torch CUDA 检测失败: {e}")

        return cuda_info

    def get_ai_framework_info(self) -> Dict[str, Any]:
        framework_info = {
            "torch_available": TORCH_AVAILABLE,
            "torch_version": "",
            "tensorflow_available": TENSORFLOW_AVAILABLE,
            "tensorflow_version": "",
            "packages": [],
            "python_packages": []
        }

        if TORCH_AVAILABLE:
            try:
                framework_info["torch_version"] = torch.__version__
                framework_info["packages"].append({
                    "name": "torch",
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

        common_packages = [
            "torch", "torchaudio", "torchvision",
            "transformers", "datasets", "accelerate", "peft", "bitsandbytes",
            "flash_attn", "xformers", "deepspeed", "trl",
            "numpy", "pandas", "scipy", "scikit-learn", "matplotlib",
            "pillow", "opencv-python", "sentencepiece", "tiktoken"
        ]

        for pkg in common_packages:
            try:
                import importlib.metadata
                version = importlib.metadata.version(pkg)
                framework_info["python_packages"].append({
                    "name": pkg,
                    "version": version,
                    "available": True
                })
            except Exception:
                framework_info["python_packages"].append({
                    "name": pkg,
                    "version": "未安装",
                    "available": False
                })

        return framework_info

    def get_gpu_topology(self) -> Dict[str, Any]:
        topology = {
            "nvlink_detected": False,
            "interconnects": [],
            "max_link_count": 0,
            "topology_type": "PCIe (Single/Multi)",
            "bottlenecks": [],
            "raw_matrix": []
        }

        try:
            stdout = self._safe_exec(["nvidia-smi", "topo", "-m"], timeout=5)
            if not stdout:
                return topology

            lines = stdout.strip().split('\n')
            topology["raw_matrix"] = lines[:12]

            header = []
            matrix_start_idx = -1
            for idx, line in enumerate(lines):
                if "GPU" in line and "CPU Affinity" in line:
                    header = line.split()
                    matrix_start_idx = idx + 1
                    break

            if matrix_start_idx == -1 or not header:
                if "NV" in (stdout or ""):
                    topology["nvlink_detected"] = True
                return topology

            gpu_cols = [h for h in header if h.startswith("GPU")]
            num_gpus = len(gpu_cols)

            nvlink_connections = 0
            for i in range(num_gpus):
                line_idx = matrix_start_idx + i
                if line_idx >= len(lines):
                    break
                row_parts = lines[line_idx].split()
                for j in range(num_gpus):
                    if i == j:
                        continue
                    if j + 1 < len(row_parts):
                        conn_code = row_parts[j + 1]
                        if i < j:
                            topology["interconnects"].append({
                                "from": f"GPU{i}", "to": f"GPU{j}", "type": conn_code,
                                "quality": "high" if "NV" in conn_code else "medium" if "PX" in conn_code or "PI" in conn_code else "low"
                            })
                        if "NV" in conn_code:
                            topology["nvlink_detected"] = True
                            nvlink_connections += 1
                            try:
                                link_num = int(''.join(filter(str.isdigit, conn_code)))
                                topology["max_link_count"] = max(topology["max_link_count"], link_num)
                            except Exception:
                                pass
                        if conn_code in ["SYS", "NODE"]:
                            topology["bottlenecks"].append(f"GPU{i} <-> GPU{j} 跨 Socket 通讯，可能存在严重的 P2P 延迟")

            if topology["nvlink_detected"]:
                topology["topology_type"] = "NVLink Fully Connected (Mesh)" if nvlink_connections >= (num_gpus * (num_gpus - 1)) else "NVLink Partial Connected / Ring"
            elif num_gpus > 1:
                topology["topology_type"] = "PCIe Switch/Bridge Cascade"
            else:
                topology["topology_type"] = "Single Device (No Interconnect)"

            topology["bottlenecks"] = list(set(topology["bottlenecks"]))
        except Exception as e:
            logger.error(f"GPU 拓扑解析失败: {str(e)}")

        return topology

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

        modes = {
            "premium": {
                "name": "最大模式",
                "name_en": "Premium",
                "desc": "多卡A100/H100，极速训练",
                "icon": "🚀"
            },
            "enterprise": {
                "name": "土豪模式",
                "name_en": "Enterprise",
                "desc": "高端GPU，高效训练",
                "icon": "👑"
            },
            "professional": {
                "name": "富人模式",
                "name_en": "Professional",
                "desc": "中高端GPU，稳定训练",
                "icon": "💎"
            },
            "standard": {
                "name": "常态模式",
                "name_en": "Standard",
                "desc": "标准配置，常规训练",
                "icon": "⚖️"
            },
            "basic": {
                "name": "穷人模式",
                "name_en": "Basic",
                "desc": "基础配置，耐心训练",
                "icon": "💰"
            },
            "entry": {
                "name": "入门模式",
                "name_en": "Entry",
                "desc": "入门配置，长期训练",
                "icon": "🌱"
            }
        }

        return {
            "score": score,
            "max_model_size": max_model,
            "recommended_mode": mode,
            "estimated_time": estimated_time,
            "gpu_accelerated": gpu_available,
            "suitable_models": self._get_suitable_models(snapshot),
            "modes": modes,
            "model_recommendation": {
                "max_model_size": max_model,
                "estimated_time": estimated_time
            }
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
                "numa_nodes": self.get_numa_nodes(),
                "motherboard": self.get_motherboard_info(),
                "gpu_topology": self.get_gpu_topology()
            }

            snapshot["score"] = self.calculate_hardware_score(snapshot)
            snapshot["compute_ladder"] = self._get_compute_ladder(snapshot)
            snapshot["storage_prediction"] = self.predict_storage_bottleneck(snapshot)
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

    def _get_compute_ladder(self, snapshot: Dict[str, Any]) -> List[Dict[str, Any]]:
        reference_devices = [
            {"name": "NVIDIA H200 (141GB)", "score": 130, "tier": "Enterprise"},
            {"name": "AMD MI300X (192GB)", "score": 115, "tier": "Enterprise"},
            {"name": "NVIDIA H100 (80GB)", "score": 100, "tier": "Enterprise"},
            {"name": "NVIDIA RTX 5090 (32GB)", "score": 92, "tier": "Consumer Next-Gen"},
            {"name": "NVIDIA RTX 5090D (32GB)", "score": 82, "tier": "Consumer Next-Gen"},
            {"name": "NVIDIA A100 (80GB)", "score": 75, "tier": "Enterprise"},
            {"name": "HUAWEI Ascend 910B", "score": 72, "tier": "Enterprise"},
            {"name": "NVIDIA RTX 5080 (16GB)", "score": 68, "tier": "Consumer Next-Gen"},
            {"name": "NVIDIA RTX 4090 (24GB)", "score": 55, "tier": "Consumer"},
            {"name": "NVIDIA RTX 4090D (24GB)", "score": 49, "tier": "Consumer"},
            {"name": "NVIDIA L40S (48GB)", "score": 52, "tier": "Enterprise"},
            {"name": "NVIDIA RTX 5070 Ti (16GB)", "score": 46, "tier": "Consumer Next-Gen"},
            {"name": "NVIDIA RTX 4080 (16GB)", "score": 40, "tier": "Consumer"},
            {"name": "NVIDIA RTX 3090 (24GB)", "score": 35, "tier": "Consumer"},
            {"name": "Apple M3 Max (128GB Unified)", "score": 28, "tier": "Edge/Workstation"},
            {"name": "Loongson 3A6000 (CPU)", "score": 5, "tier": "Edge"},
        ]

        gpu_devices = snapshot.get("gpu", {}).get("devices", [])
        if not gpu_devices:
            current_score = 2
            current_name = snapshot.get("cpu", {}).get("model", "当前 CPU")
        else:
            main_gpu = gpu_devices[0]
            name = main_gpu.get("name", "未知显卡")
            vram = main_gpu.get("memory_total", 0)
            upper_name = name.upper()

            if "H200" in upper_name:
                current_score = 130
            elif "H100" in upper_name:
                current_score = 100
            elif "5090D" in upper_name:
                current_score = 82
            elif "5090" in upper_name:
                current_score = 92
            elif "A100" in upper_name:
                current_score = 75
            elif "910B" in upper_name or "ASCEND 910" in upper_name:
                current_score = 72
            elif "5080" in upper_name:
                current_score = 68
            elif "4090D" in upper_name:
                current_score = 49
            elif "4090" in upper_name:
                current_score = 55
            elif "5070" in upper_name:
                current_score = 46
            elif "3090" in upper_name:
                current_score = 35
            elif "MI300" in upper_name:
                current_score = 115
            elif "A800" in upper_name:
                current_score = 70
            elif "H800" in upper_name:
                current_score = 90
            elif "V100" in upper_name:
                current_score = 40
            elif "RTX 4080" in upper_name:
                current_score = 42
            elif "RTX 3080" in upper_name:
                current_score = 30
            elif "L40" in upper_name:
                current_score = 50
            elif "A10" in upper_name:
                current_score = 35
            else:
                current_score = min(30, int(vram * 1.2))

            current_name = f"当前设备: {name}"

        ladder = reference_devices + [{"name": current_name, "score": current_score, "is_current": True, "tier": "Your Device"}]
        ladder.sort(key=lambda x: x["score"], reverse=True)
        max_score = max(x["score"] for x in ladder)
        for item in ladder:
            item["display_percent"] = int((item["score"] / max_score) * 100)

        return ladder

    def predict_storage_bottleneck(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        disk = snapshot.get("disk", {})
        main = disk.get("main", {})
        if not main:
            return {"risk": "low", "message": "未发现活跃主磁盘"}

        usage_percent = main.get("percent", 0)
        free_gb = main.get("free", 0)

        if free_gb < 50 or usage_percent > 90:
            return {
                "risk": "critical",
                "message": f"存储告急！剩余 {free_gb:.1f}GB，可能导致训练中断。"
            }
        elif usage_percent > 80:
            return {
                "risk": "warning",
                "message": "存储空间紧张，建议扩容。"
            }
        return {"risk": "healthy", "message": "存储空间充足"}

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
