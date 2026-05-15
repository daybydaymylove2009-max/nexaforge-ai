#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智核万炼® NexaForge AI - 硬件检测核心模块
Hardware Detection Core Module
"""

import os
import time
import platform
import subprocess
from typing import Dict, Any
from datetime import datetime

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import win32com.client
    WIN32COM_AVAILABLE = True
except ImportError:
    WIN32COM_AVAILABLE = False


class HardwareDetector:
    """硬件实时检测器"""
    
    def __init__(self):
        self.history = []
        self.max_history = 60
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """获取CPU信息"""
        cpu_info = {
            "count": os.cpu_count() or 0,
            "percent": 0.0,
            "freq_current": 0.0,
            "freq_max": 0.0,
            "cores": [],
            "load_avg": [0.0, 0.0, 0.0]
        }
        
        if PSUTIL_AVAILABLE:
            try:
                cpu_info["percent"] = psutil.cpu_percent(interval=0.1, percpu=False)
                cpu_info["cores"] = psutil.cpu_percent(interval=0.1, percpu=True)
                freq = psutil.cpu_freq()
                if freq:
                    cpu_info["freq_current"] = freq.current
                    cpu_info["freq_max"] = freq.max
                if hasattr(psutil, 'getloadavg'):
                    cpu_info["load_avg"] = list(psutil.getloadavg())
            except Exception:
                pass
        
        return cpu_info
    
    def get_memory_info(self) -> Dict[str, Any]:
        """获取内存信息"""
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
                mem_info["total"] = mem.total / (1024 ** 3)
                mem_info["available"] = mem.available / (1024 ** 3)
                mem_info["used"] = mem.used / (1024 ** 3)
                mem_info["percent"] = mem.percent
                swap = psutil.swap_memory()
                mem_info["swap_total"] = swap.total / (1024 ** 3)
                mem_info["swap_used"] = swap.used / (1024 ** 3)
                mem_info["swap_percent"] = swap.percent
            except Exception:
                pass
        
        return mem_info
    
    def get_gpu_info(self) -> Dict[str, Any]:
        """获取GPU信息"""
        gpu_info = {
            "available": False,
            "count": 0,
            "devices": []
        }
        
        if TORCH_AVAILABLE:
            try:
                if torch.cuda.is_available():
                    gpu_info["available"] = True
                    gpu_info["count"] = torch.cuda.device_count()
                    for i in range(gpu_info["count"]):
                        device = {
                            "index": i,
                            "name": torch.cuda.get_device_name(i),
                            "memory_total": torch.cuda.get_device_properties(i).total_memory / (1024 ** 3),
                            "memory_allocated": 0.0,
                            "memory_reserved": 0.0,
                            "memory_free": 0.0,
                            "utilization": 0.0,
                            "temperature": 0.0,
                            "power_usage": 0.0
                        }
                        if hasattr(torch.cuda, 'memory_stats'):
                            try:
                                mem_stats = torch.cuda.memory_stats(i)
                                device["memory_allocated"] = mem_stats.get('allocated_bytes.all.current', 0) / (1024 ** 3)
                                device["memory_reserved"] = mem_stats.get('reserved_bytes.all.current', 0) / (1024 ** 3)
                                device["memory_free"] = device["memory_total"] - device["memory_reserved"]
                            except Exception:
                                pass
                        gpu_info["devices"].append(device)
            except Exception:
                pass
        
        if not gpu_info["available"]:
            try:
                result = subprocess.run(
                    ["nvidia-smi", "--query-gpu=name,memory.total,memory.used,memory.free,temperature.gpu", "--format=csv,noheader,nounits"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    gpu_info["available"] = True
                    gpu_info["count"] = len(lines)
                    for i, line in enumerate(lines):
                        parts = [p.strip() for p in line.split(',')]
                        if len(parts) >= 4:
                            device = {
                                "index": i,
                                "name": parts[0],
                                "memory_total": float(parts[1]) / 1024,
                                "memory_used": float(parts[2]) / 1024,
                                "memory_free": float(parts[3]) / 1024,
                                "temperature": float(parts[4]) if len(parts) > 4 else 0.0,
                                "utilization": 0.0,
                                "power_usage": 0.0
                            }
                            gpu_info["devices"].append(device)
            except Exception:
                pass
        
        return gpu_info
    
    def get_disk_info(self) -> Dict[str, Any]:
        """获取磁盘信息"""
        disk_info = {
            "partitions": []
        }
        
        if PSUTIL_AVAILABLE:
            try:
                partitions = psutil.disk_partitions()
                for part in partitions:
                    try:
                        usage = psutil.disk_usage(part.mountpoint)
                        disk_info["partitions"].append({
                            "device": part.device,
                            "mountpoint": part.mountpoint,
                            "fstype": part.fstype,
                            "total": usage.total / (1024 ** 3),
                            "used": usage.used / (1024 ** 3),
                            "free": usage.free / (1024 ** 3),
                            "percent": usage.percent
                        })
                    except Exception:
                        continue
                
                main_disk = None
                for part in disk_info["partitions"]:
                    if "C:" in part["device"] or "/" == part["mountpoint"]:
                        main_disk = part
                        break
                if main_disk:
                    disk_info["main"] = main_disk
            except Exception:
                pass
        
        return disk_info
    
    def get_network_info(self) -> Dict[str, Any]:
        """获取网络信息"""
        net_info = {
            "interfaces": [],
            "bytes_sent": 0,
            "bytes_recv": 0
        }
        
        if PSUTIL_AVAILABLE:
            try:
                if_addrs = psutil.net_if_addrs()
                for name, addrs in if_addrs.items():
                    for addr in addrs:
                        if addr.family == 2:
                            net_info["interfaces"].append({
                                "name": name,
                                "address": addr.address
                            })
                            break
                net_io = psutil.net_io_counters()
                net_info["bytes_sent"] = net_io.bytes_sent
                net_info["bytes_recv"] = net_io.bytes_recv
            except Exception:
                pass
        
        return net_info
    
    def _get_windows_version(self) -> str:
        """获取Windows版本名称"""
        version = platform.version()
        # Windows版本号格式: 10.0.build_number
        # Windows 11: 10.0.22000+
        # Windows 10: 10.0.10240 - 10.0.21996
        try:
            parts = version.split('.')
            if len(parts) >= 3:
                build_number = int(parts[2])
                if build_number >= 22000:
                    return f"Windows 11 (Build {build_number})"
                elif build_number >= 10240:
                    return f"Windows 10 (Build {build_number})"
        except Exception:
            pass
        return f"Windows {version}"
    
    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        os_name = platform.system()
        os_version = platform.version()
        
        # 特殊处理Windows版本识别
        if os_name == "Windows":
            os_display = self._get_windows_version()
        else:
            os_display = f"{os_name} {os_version}"
        
        sys_info = {
            "os": os_name,
            "os_version": os_version,
            "os_display": os_display,
            "architecture": platform.architecture()[0],
            "machine": platform.machine(),
            "python_version": platform.python_version(),
            "hostname": platform.node(),
            "boot_time": 0.0,
            "uptime": 0.0
        }
        
        if PSUTIL_AVAILABLE:
            try:
                sys_info["boot_time"] = psutil.boot_time()
                sys_info["uptime"] = time.time() - psutil.boot_time()
            except Exception:
                pass
        
        return sys_info
    
    def get_motherboard_info(self) -> Dict[str, Any]:
        """获取主板信息"""
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
                # 使用PowerShell获取主板信息（更可靠）
                ps_commands = [
                    "Get-WmiObject -Class Win32_BaseBoard | Select-Object -Property Manufacturer,Product,Version,SerialNumber | ConvertTo-Json",
                    "Get-WmiObject -Class Win32_BIOS | Select-Object -Property Manufacturer,SMBIOSBIOSVersion,ReleaseDate | ConvertTo-Json",
                    "Get-WmiObject -Class Win32_Processor | Select-Object -Property Name | ConvertTo-Json"
                ]
                
                for cmd in ps_commands:
                    try:
                        result = subprocess.run(
                            ["powershell", "-Command", cmd],
                            capture_output=True,
                            text=True,
                            timeout=10,
                            encoding='utf-8'
                        )
                        if result.returncode == 0 and result.stdout.strip():
                            import json
                            try:
                                data = json.loads(result.stdout)
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
                            except json.JSONDecodeError:
                                pass
                    except Exception:
                        pass
            
            elif platform.system() == "Linux":
                # Linux系统读取sysfs
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
                # CPU信息
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
    
    def _download_openhardwaremonitor(self) -> str:
        """下载 OpenHardwareMonitor 库"""
        import os
        import urllib.request
        
        lib_dir = os.path.join(os.path.dirname(__file__), 'libs')
        os.makedirs(lib_dir, exist_ok=True)
        
        dll_path = os.path.join(lib_dir, 'OpenHardwareMonitorLib.dll')
        
        if not os.path.exists(dll_path):
            try:
                url = "https://github.com/openhardwaremonitor/openhardwaremonitor/raw/master/OpenHardwareMonitorLib/bin/Release/OpenHardwareMonitorLib.dll"
                urllib.request.urlretrieve(url, dll_path)
                return dll_path
            except Exception:
                return ""
        return dll_path
    
    def _get_temperature_from_ohm(self) -> Dict[str, Any]:
        """使用 OpenHardwareMonitor 获取温度"""
        result = {
            "cpu": "未知",
            "cpu_cores": [],
            "gpu": "未知",
            "motherboard": "未知",
            "disks": [],
            "success": False
        }
        
        if platform.system() != "Windows":
            return result
        
        try:
            dll_path = self._download_openhardwaremonitor()
            if not dll_path:
                return result
            
            import clr
            clr.AddReference(dll_path)
            
            from OpenHardwareMonitor.Hardware import Computer
            
            computer = Computer()
            computer.CPUEnabled = True
            computer.GPUEnabled = True
            computer.MainboardEnabled = True
            computer.HDDEnabled = True
            computer.Open()
            
            for hardware in computer.Hardware:
                hardware.Update()
                
                for sensor in hardware.Sensors:
                    if sensor.SensorType == 0:  # Temperature
                        name = sensor.Name
                        value = sensor.Value
                        
                        if value is not None:
                            temp = round(value)
                            temp_str = f"{temp}°C"
                            
                            if "CPU" in hardware.Name or "Processor" in hardware.Name:
                                if "Core" in name:
                                    result["cpu_cores"].append(f"{name}: {temp_str}")
                                else:
                                    if result["cpu"] == "未知":
                                        result["cpu"] = temp_str
                            
                            elif "GPU" in hardware.Name or "Graphics" in hardware.Name:
                                if result["gpu"] == "未知":
                                    result["gpu"] = temp_str
                            
                            elif "Mainboard" in hardware.Name or "Motherboard" in hardware.Name:
                                if result["motherboard"] == "未知":
                                    result["motherboard"] = temp_str
                            
                            elif "HDD" in hardware.Name or "SSD" in hardware.Name:
                                result["disks"].append({
                                    "device": hardware.Name,
                                    "model": hardware.Name,
                                    "temperature": temp_str
                                })
            
            computer.Close()
            result["success"] = True
            
        except Exception:
            pass
        
        return result
    
    def get_temperature_info(self) -> Dict[str, Any]:
        """获取温度信息"""
        temp_info = {
            "cpu": "未知",
            "cpu_cores": [],
            "gpu": "未知",
            "motherboard": "未知",
            "disks": [],
            "sources": [],
            "method": "unknown"
        }
        
        # 优先使用 OpenHardwareMonitor
        ohm_result = self._get_temperature_from_ohm()
        if ohm_result["success"]:
            temp_info.update(ohm_result)
            temp_info["sources"].append("OpenHardwareMonitor")
            temp_info["method"] = "ohm"
            return temp_info
        
        try:
            # 方法2: 使用WMI获取温度（Windows）
            if platform.system() == "Windows" and WIN32COM_AVAILABLE:
                try:
                    import win32com.client
                    wmi = win32com.client.GetObject("winmgmts:")
                    
                    # 获取温度传感器
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
                                elif "motherboard" in name or "system" in name or "board" in name:
                                    if temp_info["motherboard"] == "未知":
                                        temp_info["motherboard"] = f"{round(temp_celsius)}°C"
                        except Exception:
                            pass
                except Exception:
                    pass
            
            # 方法3: 使用PowerShell获取温度（更可靠）
            if platform.system() == "Windows":
                try:
                    result = subprocess.run(
                        ["powershell", "-Command", 
                         "Get-WmiObject -Class Win32_PerfFormattedData_Counters_ThermalZoneInformation | Select-Object -Property Name,Temperature | ConvertTo-Json"],
                        capture_output=True,
                        text=True,
                        timeout=10,
                        encoding='utf-8'
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        import json
                        try:
                            data = json.loads(result.stdout)
                            if isinstance(data, list):
                                data = data[0]
                            if 'Temperature' in data and data['Temperature'] > 0:
                                temp_celsius = data['Temperature'] / 10.0
                                if temp_info["cpu"] == "未知":
                                    temp_info["cpu"] = f"{round(temp_celsius)}°C"
                                temp_info["sources"].append("PowerShell: Win32_PerfFormattedData")
                        except json.JSONDecodeError:
                            pass
                except Exception:
                    pass
            
            # 方法4: 使用psutil获取温度（Linux/macOS为主）
            if PSUTIL_AVAILABLE and hasattr(psutil, 'sensors_temperatures'):
                temps = psutil.sensors_temperatures()
                
                # CPU温度
                if 'coretemp' in temps:
                    cpu_temps = [t.current for t in temps['coretemp']]
                    if cpu_temps:
                        avg_temp = sum(cpu_temps) / len(cpu_temps)
                        if temp_info["cpu"] == "未知":
                            temp_info["cpu"] = f"{round(avg_temp)}°C"
                        temp_info["cpu_cores"] = [f"核心{i}: {round(t)}°C" for i, t in enumerate(cpu_temps)]
                        temp_info["sources"].append("psutil: coretemp")
                
                # 主板温度
                if 'acpitz' in temps:
                    mb_temps = [t.current for t in temps['acpitz']]
                    if mb_temps and temp_info["motherboard"] == "未知":
                        temp_info["motherboard"] = f"{round(sum(mb_temps)/len(mb_temps))}°C"
                        temp_info["sources"].append("psutil: acpitz")
                
                # 主板温度（其他传感器）
                for sensor_name in ['asus', 'gigabyte', 'msi']:
                    if sensor_name in temps:
                        sensor_temps = [t.current for t in temps[sensor_name] if 'temp' in t.label.lower()]
                        if sensor_temps and temp_info["motherboard"] == "未知":
                            temp_info["motherboard"] = f"{round(sum(sensor_temps)/len(sensor_temps))}°C"
                            temp_info["sources"].append(f"psutil: {sensor_name}")
            
            # 方法5: Linux主板温度（通过sysfs）
            if platform.system() == "Linux":
                # 主板南桥温度
                try:
                    with open('/sys/class/hwmon/hwmon*/temp1_input', 'r') as f:
                        temp = int(f.read().strip()) / 1000
                        if temp > 0 and temp_info["motherboard"] == "未知":
                            temp_info["motherboard"] = f"{round(temp)}°C"
                            temp_info["sources"].append("sysfs: motherboard")
                except Exception:
                    pass
                
                # 芯片组温度
                try:
                    with open('/sys/class/hwmon/hwmon*/temp2_input', 'r') as f:
                        temp = int(f.read().strip()) / 1000
                        if temp > 0 and temp_info["motherboard"] == "未知":
                            temp_info["motherboard"] = f"{round(temp)}°C"
                            temp_info["sources"].append("sysfs: chipset")
                except Exception:
                    pass
            
            # 方法6: 获取GPU温度（通过NVIDIA ML库，更准确）
            gpu_temp_obtained = False
            try:
                import pynvml
                pynvml.nvmlInit()
                device_count = pynvml.nvmlDeviceGetCount()
                
                if device_count > 0:
                    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                    temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                    
                    if temp > 0:
                        temp_info["gpu"] = f"{temp}°C"
                        temp_info["sources"].append("NVML")
                        gpu_temp_obtained = True
                    else:
                        try:
                            power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0
                            utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
                            fan_speed = pynvml.nvmlDeviceGetFanSpeed(handle)
                            
                            if power > 1 or utilization.gpu > 1 or fan_speed > 0:
                                temp_info["gpu"] = f"{temp}°C (低功耗)"
                                temp_info["sources"].append("NVML")
                                gpu_temp_obtained = True
                        except Exception:
                            pass
                
                pynvml.nvmlShutdown()
            except Exception:
                pass
            
            if not gpu_temp_obtained:
                try:
                    result = subprocess.run(
                        ["nvidia-smi", "--query-gpu=temperature.gpu,power.draw,fan.speed,utilization.gpu", "--format=csv,noheader,nounits"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        parts = result.stdout.strip().split(',')
                        if parts:
                            temp_value = parts[0].strip()
                            if temp_value.isdigit():
                                temp_int = int(temp_value)
                                if temp_int > 0:
                                    temp_info["gpu"] = f"{temp_int}°C"
                                    temp_info["sources"].append("nvidia-smi")
                                    gpu_temp_obtained = True
                                elif len(parts) > 1 and parts[1].strip():
                                    try:
                                        power = float(parts[1].strip())
                                        fan = float(parts[2].strip()) if len(parts) > 2 else 0
                                        if power > 1 or fan > 0:
                                            temp_info["gpu"] = "低功耗模式"
                                            temp_info["sources"].append("nvidia-smi")
                                            gpu_temp_obtained = True
                                    except Exception:
                                        pass
                except Exception:
                    pass
            
            if not gpu_temp_obtained:
                temp_info["gpu"] = "不支持"
                temp_info["sources"].append("无法获取")
            
            # 方法6: Linux/macOS GPU温度
            if platform.system() in ["Linux", "Darwin"]:
                # NVIDIA GPU温度 (Linux)
                try:
                    with open('/sys/class/drm/card0/device/hwmon/hwmon*/temp1_input', 'r') as f:
                        temp = int(f.read().strip()) / 1000
                        if temp > 0 and temp_info["gpu"] == "未知":
                            temp_info["gpu"] = f"{round(temp)}°C"
                            temp_info["sources"].append("sysfs: nvidia")
                except Exception:
                    pass
                
                # AMD GPU温度 (Linux)
                try:
                    with open('/sys/class/drm/card0/device/hwmon/hwmon*/temp2_input', 'r') as f:
                        temp = int(f.read().strip()) / 1000
                        if temp > 0 and temp_info["gpu"] == "未知":
                            temp_info["gpu"] = f"{round(temp)}°C"
                            temp_info["sources"].append("sysfs: amd")
                except Exception:
                    pass
            
            # 方法7: 获取磁盘信息
            if platform.system() == "Windows":
                try:
                    result = subprocess.run(
                        ["wmic", "diskdrive", "get", "DeviceID,Model", "/format:csv"],
                        capture_output=True,
                        text=True,
                        timeout=10,
                        encoding='utf-8'
                    )
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')[1:]
                        for line in lines:
                            if line.strip():
                                parts = line.split(',')
                                if len(parts) >= 2:
                                    temp_info["disks"].append({
                                        "device": parts[0].strip(),
                                        "model": parts[1].strip(),
                                        "temperature": "未知"
                                    })
                except Exception:
                    pass
        
        except Exception as e:
            temp_info["sources"].append(f"Error: {str(e)[:50]}")
        
        return temp_info
    
    def get_hardware_snapshot(self) -> Dict[str, Any]:
        """获取硬件实时快照"""
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "system": self.get_system_info(),
            "cpu": self.get_cpu_info(),
            "memory": self.get_memory_info(),
            "gpu": self.get_gpu_info(),
            "disk": self.get_disk_info(),
            "network": self.get_network_info(),
            "motherboard": self.get_motherboard_info(),
            "temperature": self.get_temperature_info()
        }
        
        self.history.append(snapshot)
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        return snapshot
    
    def get_history(self) -> list:
        """获取历史数据"""
        return self.history
    
    def calculate_hardware_score(self, snapshot: Dict[str, Any]) -> int:
        """计算硬件综合评分"""
        score = 0
        
        cpu_count = snapshot["cpu"]["count"]
        if cpu_count >= 32:
            score += 30
        elif cpu_count >= 16:
            score += 25
        elif cpu_count >= 8:
            score += 20
        elif cpu_count >= 4:
            score += 15
        else:
            score += 10
        
        mem_total = snapshot["memory"]["total"]
        if mem_total >= 128:
            score += 25
        elif mem_total >= 64:
            score += 20
        elif mem_total >= 32:
            score += 15
        elif mem_total >= 16:
            score += 10
        else:
            score += 5
        
        if snapshot["gpu"]["available"] and snapshot["gpu"]["count"] > 0:
            gpu = snapshot["gpu"]["devices"][0]
            gpu_mem = gpu.get("memory_total", 0)
            if gpu_mem >= 40:
                score += 45
            elif gpu_mem >= 24:
                score += 40
            elif gpu_mem >= 16:
                score += 35
            elif gpu_mem >= 12:
                score += 30
            elif gpu_mem >= 8:
                score += 25
            elif gpu_mem >= 6:
                score += 20
            elif gpu_mem >= 4:
                score += 15
            else:
                score += 10
        
        return min(score, 100)
    
    def get_training_recommendations(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """获取训练推荐配置"""
        score = self.calculate_hardware_score(snapshot)
        
        modes = {
            "poor": {
                "name": "穷人模式",
                "name_en": "Minimal",
                "icon": "💰",
                "device": "cpu",
                "batch_size": 1,
                "gradient_accumulation_steps": 16,
                "epochs": 1,
                "max_seq_length": 256,
                "lora_r": 4,
                "quantization": None,
                "estimated_time": "4-8小时",
                "suitable": score < 30
            },
            "normal": {
                "name": "常态模式",
                "name_en": "Recommended",
                "icon": "⚖️",
                "device": "cpu",
                "batch_size": 1,
                "gradient_accumulation_steps": 8,
                "epochs": 3,
                "max_seq_length": 512,
                "lora_r": 8,
                "quantization": None,
                "estimated_time": "1-2小时",
                "suitable": 30 <= score < 60
            },
            "rich": {
                "name": "富人模式",
                "name_en": "Premium",
                "icon": "💎",
                "device": "cpu",
                "batch_size": 2,
                "gradient_accumulation_steps": 4,
                "epochs": 5,
                "max_seq_length": 1024,
                "lora_r": 16,
                "quantization": None,
                "estimated_time": "30-60分钟",
                "suitable": 60 <= score < 80
            },
            "tycoon": {
                "name": "土豪模式",
                "name_en": "Tycoon",
                "icon": "👑",
                "device": "cuda",
                "batch_size": 4,
                "gradient_accumulation_steps": 2,
                "epochs": 10,
                "max_seq_length": 2048,
                "lora_r": 32,
                "quantization": "4bit",
                "estimated_time": "10-20分钟",
                "suitable": 80 <= score < 95
            },
            "max": {
                "name": "最大模式",
                "name_en": "Maximum",
                "icon": "🚀",
                "device": "cuda",
                "batch_size": 8,
                "gradient_accumulation_steps": 1,
                "epochs": 20,
                "max_seq_length": 4096,
                "lora_r": 64,
                "quantization": None,
                "estimated_time": "2-5分钟",
                "suitable": score >= 95
            }
        }
        
        if snapshot["gpu"]["available"]:
            gpu = snapshot["gpu"]["devices"][0]
            gpu_mem = gpu.get("memory_total", 0)
            if gpu_mem >= 6:
                modes["normal"]["device"] = "cuda"
                modes["normal"]["quantization"] = "4bit"
                modes["normal"]["estimated_time"] = "30-60分钟"
            if gpu_mem >= 12:
                modes["rich"]["device"] = "cuda"
                modes["rich"]["quantization"] = "4bit"
                modes["rich"]["estimated_time"] = "15-30分钟"
        
        recommended_key = None
        for key, mode in modes.items():
            if mode["suitable"]:
                recommended_key = key
                break
        
        if not recommended_key:
            recommended_key = "normal"
        
        return {
            "score": score,
            "recommended_mode": recommended_key,
            "modes": modes,
            "tips": self._generate_tips(snapshot, score)
        }
    
    def _generate_tips(self, snapshot: Dict[str, Any], score: int) -> list:
        """生成硬件优化建议"""
        tips = []
        
        if not snapshot["gpu"]["available"]:
            tips.append({"icon": "💡", "text": "未检测到GPU，建议使用CPU模式或添加NVIDIA显卡"})
        
        if snapshot["memory"]["total"] < 16:
            tips.append({"icon": "⚠️", "text": "内存不足，建议升级到16GB+"})
        
        if snapshot["cpu"]["count"] < 4:
            tips.append({"icon": "⚠️", "text": "CPU核心较少，建议降低训练参数"})
        
        if snapshot["gpu"]["available"]:
            gpu = snapshot["gpu"]["devices"][0]
            if gpu.get("memory_total", 0) < 8:
                tips.append({"icon": "💡", "text": "GPU显存较小，建议使用4-bit量化"})
        
        return tips


detector = HardwareDetector()
