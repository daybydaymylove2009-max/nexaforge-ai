#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智核万炼® NexaForge AI - 单元测试
NexaForge AI Unit Tests
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hardware.detector import HardwareDetector
from hardware.models import APIResponse, CPUInfo, MemoryInfo, GPUInfo
from hardware.config import settings


class TestHardwareDetector:
    """硬件检测器测试"""

    def setup_method(self):
        """每个测试方法前执行"""
        self.detector = HardwareDetector()

    def test_system_info(self):
        """测试系统信息获取"""
        info = self.detector.get_system_info()
        assert isinstance(info, dict)
        assert "os" in info
        assert "hostname" in info
        print(f"✅ 系统信息测试通过: {info['os']}")

    def test_cpu_info(self):
        """测试 CPU 信息获取"""
        info = self.detector.get_cpu_info()
        assert isinstance(info, dict)
        assert "count" in info
        assert "percent" in info
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

    def test_hardware_snapshot(self):
        """测试硬件快照"""
        snapshot = self.detector.get_hardware_snapshot()
        assert isinstance(snapshot, dict)
        assert "version" in snapshot
        assert "timestamp" in snapshot
        assert "cpu" in snapshot
        assert "memory" in snapshot
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
        print(f"✅ 训练推荐测试通过: 推荐 {recommendations['max_model_size']} 模型")

    def test_benchmark_cpu(self):
        """测试 CPU 基准测试"""
        result = self.detector.run_benchmark_cpu(duration=1.0)
        assert isinstance(result, dict)
        assert "status" in result
        assert "score" in result
        assert result["status"] in ["completed", "failed"]
        print(f"✅ CPU 基准测试通过: 得分={result['score']}")

    def test_benchmark_memory(self):
        """测试内存基准测试"""
        result = self.detector.run_benchmark_memory()
        assert isinstance(result, dict)
        assert "status" in result
        assert "score" in result
        print(f"✅ 内存基准测试通过: 得分={result['score']}")

    def test_health_check(self):
        """测试健康检查"""
        result = self.detector.check_hardware_health()
        assert isinstance(result, dict)
        assert "status" in result
        assert "score" in result
        assert result["status"] in ["healthy", "warning", "critical"]
        print(f"✅ 健康检查测试通过: 状态={result['status']}, 得分={result['score']}")


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


class TestConfiguration:
    """配置测试"""

    def test_settings(self):
        """测试配置加载"""
        assert settings.HOST == "0.0.0.0"
        assert settings.PORT == 8000
        assert settings.API_VERSION == "v1"
        print(f"✅ 配置测试通过: HOST={settings.HOST}, PORT={settings.PORT}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
