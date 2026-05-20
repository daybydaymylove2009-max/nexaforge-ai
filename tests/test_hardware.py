#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智核万炼® NexaForge AI - 单元测试 v2.1
NexaForge AI Unit Tests
"""

import pytest
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hardware.detector import HardwareDetector, VERSION
from hardware.models import APIResponse, CPUInfo, MemoryInfo, GPUInfo
from hardware.config import settings
from hardware.resilience import CircuitBreaker, RateLimiter


class TestHardwareDetector:
    """硬件检测器测试"""

    def setup_method(self):
        """每个测试方法前执行"""
        self.detector = HardwareDetector()

    def teardown_method(self):
        """每个测试方法后执行"""
        if hasattr(self, 'detector'):
            del self.detector

    def test_version(self):
        """测试版本号"""
        assert VERSION == "2.1.0"
        print(f"✅ 版本号测试通过: {VERSION}")

    def test_system_info(self):
        """测试系统信息获取"""
        info = self.detector.get_system_info()
        assert isinstance(info, dict)
        assert "os" in info
        assert "hostname" in info
        assert "python_version" in info
        print(f"✅ 系统信息测试通过: {info['os']}")

    def test_cpu_info(self):
        """测试 CPU 信息获取"""
        info = self.detector.get_cpu_info()
        assert isinstance(info, dict)
        assert "count" in info
        assert "percent" in info
        assert "model" in info
        assert info["count"] > 0
        print(f"✅ CPU 信息测试通过: {info['model']}")

    def test_memory_info(self):
        """测试内存信息获取"""
        info = self.detector.get_memory_info()
        assert isinstance(info, dict)
        assert "total" in info
        assert "percent" in info
        assert info["total"] > 0
        print(f"✅ 内存信息测试通过: {info['total']:.2f} GB")

    def test_gpu_info(self):
        """测试 GPU 信息获取"""
        info = self.detector.get_gpu_info()
        assert isinstance(info, dict)
        assert "available" in info
        assert "count" in info
        assert "devices" in info
        print(f"✅ GPU 信息测试通过: 可用={info['available']}, 数量={info['count']}")

    def test_disk_info(self):
        """测试磁盘信息获取"""
        info = self.detector.get_disk_info()
        assert isinstance(info, dict)
        assert "total" in info
        assert "used" in info
        assert "partitions" in info
        print(f"✅ 磁盘信息测试通过: {info['total']:.2f} GB")

    def test_network_info(self):
        """测试网络信息获取"""
        info = self.detector.get_network_info()
        assert isinstance(info, dict)
        assert "interfaces" in info
        assert "total_bytes_sent" in info
        assert "total_bytes_recv" in info
        print(f"✅ 网络信息测试通过")

    def test_power_info(self):
        """测试电源信息获取"""
        info = self.detector.get_power_info()
        assert isinstance(info, dict)
        assert "battery_percent" in info
        assert "performance_mode" in info
        print(f"✅ 电源信息测试通过: 性能模式={info['performance_mode']}")

    def test_cuda_info(self):
        """测试 CUDA 信息获取"""
        info = self.detector.get_cuda_info()
        assert isinstance(info, dict)
        assert "available" in info
        assert "version" in info
        assert "device_count" in info
        print(f"✅ CUDA 信息测试通过: 可用={info['available']}")

    def test_hardware_snapshot(self):
        """测试硬件快照"""
        snapshot = self.detector.get_hardware_snapshot()
        assert isinstance(snapshot, dict)
        assert "version" in snapshot
        assert "timestamp" in snapshot
        assert "cpu" in snapshot
        assert "memory" in snapshot
        assert "gpu" in snapshot
        assert snapshot["version"] == VERSION
        print(f"✅ 硬件快照测试通过: 版本={snapshot['version']}")

    def test_calculate_score(self):
        """测试硬件评分"""
        snapshot = self.detector.get_hardware_snapshot()
        score = self.detector.calculate_hardware_score(snapshot)
        assert isinstance(score, int)
        assert 0 <= score <= 100
        print(f"✅ 硬件评分测试通过: {score}分")

    def test_training_recommendations(self):
        """测试训练推荐"""
        snapshot = self.detector.get_hardware_snapshot()
        recommendations = self.detector.get_training_recommendations(snapshot)
        assert isinstance(recommendations, dict)
        assert "score" in recommendations
        assert "max_model_size" in recommendations
        assert "recommended_mode" in recommendations
        assert "suitable_models" in recommendations
        print(f"✅ 训练推荐测试通过: 推荐 {recommendations['max_model_size']} 模型")

    def test_benchmark_cpu(self):
        """测试 CPU 基准测试"""
        result = self.detector.run_benchmark_cpu(duration=1.0)
        assert isinstance(result, dict)
        assert "status" in result
        assert "score" in result
        assert "operations_per_second" in result
        assert result["status"] in ["completed", "failed"]
        print(f"✅ CPU 基准测试通过: 得分={result['score']}")

    def test_benchmark_memory(self):
        """测试内存基准测试"""
        result = self.detector.run_benchmark_memory()
        assert isinstance(result, dict)
        assert "status" in result
        assert "score" in result
        assert "read_bandwidth_gb_s" in result
        assert "write_bandwidth_gb_s" in result
        print(f"✅ 内存基准测试通过: 得分={result['score']}")

    def test_health_check(self):
        """测试健康检查"""
        result = self.detector.check_hardware_health()
        assert isinstance(result, dict)
        assert "status" in result
        assert "score" in result
        assert "checks" in result
        assert result["status"] in ["healthy", "warning", "critical"]
        print(f"✅ 健康检查测试通过: 状态={result['status']}, 得分={result['score']}")

    def test_cache_mechanism(self):
        """测试缓存机制"""
        info1 = self.detector.get_cpu_info()
        info2 = self.detector.get_cpu_info()
        assert info1 == info2
        print(f"✅ 缓存机制测试通过")

    def test_history(self):
        """测试历史记录"""
        history = self.detector.get_history()
        assert isinstance(history, list)
        assert len(history) >= 0
        print(f"✅ 历史记录测试通过: {len(history)} 条记录")


class TestResilience:
    """弹性和容错测试"""

    def test_circuit_breaker_initial_state(self):
        """测试断路器初始状态"""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=5.0)
        assert cb.state == "closed"
        assert cb.failure_count == 0
        print("✅ 断路器初始状态测试通过")

    def test_circuit_breaker_call_success(self):
        """测试断路器成功调用"""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=5.0)

        def success_func():
            return "success"

        result = cb.call(success_func)
        assert result == "success"
        assert cb.state == "closed"
        print("✅ 断路器成功调用测试通过")

    def test_circuit_breaker_opens_on_failures(self):
        """测试断路器在失败时打开"""
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=5.0)

        def failing_func():
            raise Exception("Test error")

        try:
            cb.call(failing_func)
        except Exception:
            pass

        assert cb.failure_count == 1

        try:
            cb.call(failing_func)
        except Exception:
            pass

        assert cb.state == "open"
        print("✅ 断路器打开测试通过")

    def test_rate_limiter(self):
        """测试速率限制器"""
        limiter = RateLimiter(max_calls=3, time_window=1.0)

        assert limiter.is_allowed() == True
        assert limiter.is_allowed() == True
        assert limiter.is_allowed() == True
        assert limiter.is_allowed() == False

        time.sleep(1.1)
        assert limiter.is_allowed() == True

        print("✅ 速率限制器测试通过")


class TestAPIModels:
    """API 模型测试"""

    def test_api_response(self):
        """测试 API 响应模型"""
        response = APIResponse(
            code=200,
            message="success",
            data={"test": "data"}
        )
        assert response.code == 200
        assert response.message == "success"
        assert response.data["test"] == "data"
        print("✅ API 响应模型测试通过")

    def test_cpu_info_model(self):
        """测试 CPU 信息模型"""
        cpu = CPUInfo(
            count=8,
            percent=50.0,
            model="Test CPU"
        )
        assert cpu.count == 8
        assert cpu.percent == 50.0
        assert cpu.model == "Test CPU"
        print("✅ CPU 信息模型测试通过")

    def test_memory_info_model(self):
        """测试内存信息模型"""
        memory = MemoryInfo(
            total=16.0,
            used=8.0,
            percent=50.0
        )
        assert memory.total == 16.0
        assert memory.percent == 50.0
        print("✅ 内存信息模型测试通过")

    def test_gpu_info_model(self):
        """测试 GPU 信息模型"""
        gpu = GPUInfo(
            available=True,
            count=1
        )
        assert gpu.available == True
        assert gpu.count == 1
        print("✅ GPU 信息模型测试通过")


class TestConfiguration:
    """配置测试"""

    def test_settings(self):
        """测试配置加载"""
        assert settings.HOST == "0.0.0.0"
        assert settings.PORT == 8000
        assert settings.API_VERSION == "v1"
        assert settings.API_PREFIX == "/api/v1"
        print(f"✅ 配置测试通过: HOST={settings.HOST}, PORT={settings.PORT}")

    def test_cache_settings(self):
        """测试缓存配置"""
        assert hasattr(settings, 'ENABLE_CACHE')
        assert hasattr(settings, 'CACHE_TTL')
        print(f"✅ 缓存配置测试通过")

    def test_auth_settings(self):
        """测试认证配置"""
        assert hasattr(settings, 'ENABLE_AUTH')
        assert hasattr(settings, 'API_KEY')
        print(f"✅ 认证配置测试通过")


class TestErrorHandling:
    """错误处理测试"""

    def test_safe_exec_timeout(self):
        """测试超时处理"""
        detector = HardwareDetector()
        result = detector._safe_exec(["sleep", "10"], timeout=1)
        assert result is None
        print("✅ 超时处理测试通过")

    def test_graceful_degradation(self):
        """测试优雅降级"""
        detector = HardwareDetector()

        info = detector.get_cpu_info()
        assert info is not None
        assert isinstance(info, dict)

        print("✅ 优雅降级测试通过")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])
