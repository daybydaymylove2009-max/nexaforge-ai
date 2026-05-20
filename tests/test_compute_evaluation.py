#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智核万炼 NexaForge AI - 算力评估单元测试
"""

import pytest
from hardware import ComputeEvaluator, GPUDatabase, ModelDatabase
from hardware.detector import HardwareDetector


class TestGPUDatabase:
    """GPU数据库测试"""

    def test_gpu_database_size(self):
        """测试GPU数据库大小"""
        gpus = GPUDatabase.get_all_gpus()
        assert len(gpus) > 0
        print(f"✅ GPU数据库包含 {len(gpus)} 个GPU")

    def test_gpu_matching(self):
        """测试GPU匹配"""
        gpu = GPUDatabase.match_gpu("RTX 4090")
        assert gpu is not None
        assert gpu.name == "NVIDIA GeForce RTX 4090"
        print(f"✅ GPU匹配测试通过: {gpu.name}")

    def test_gpu_specs(self):
        """测试GPU规格"""
        gpu = GPUDatabase.match_gpu("RTX 4090")
        assert gpu.tflops_fp16_tensor > 0
        assert gpu.vram_gb > 0
        assert gpu.bandwidth_gb_s > 0
        print(f"✅ GPU规格测试通过: {gpu.tflops_fp16_tensor} TFLOPS, {gpu.vram_gb} GB")


class TestModelDatabase:
    """模型数据库测试"""

    def test_model_database_size(self):
        """测试模型数据库大小"""
        models = ModelDatabase.get_all_models()
        assert len(models) > 0
        print(f"✅ 模型数据库包含 {len(models)} 个模型")

    def test_model_retrieval(self):
        """测试模型获取"""
        model = ModelDatabase.get_model("Llama-2-7B")
        assert model is not None
        assert model.params == 7_000_000_000
        print(f"✅ 模型获取测试通过: {model.name}")

    def test_custom_model_adding(self):
        """测试添加自定义模型"""
        model = ModelDatabase.add_custom_model(
            name="TestModel",
            params=5_000_000_000,
            recommended_vram_gb=10
        )
        assert model.name == "TestModel"
        assert model.params == 5_000_000_000
        print(f"✅ 添加自定义模型测试通过: {model.name}")


class TestComputeEvaluator:
    """算力评估器测试"""

    def setup_method(self):
        """每个测试前初始化"""
        self.detector = HardwareDetector()
        self.snapshot = self.detector.get_hardware_snapshot()
        self.evaluator = ComputeEvaluator(self.snapshot)

    def test_gpu_detection(self):
        """测试GPU检测"""
        gpu_name = self.evaluator.detect_gpu_model()
        assert isinstance(gpu_name, str)
        print(f"✅ GPU检测测试通过: {gpu_name}")

    def test_vram_detection(self):
        """测试显存检测"""
        vram = self.evaluator.get_vram_gb()
        assert vram >= 0
        print(f"✅ 显存检测测试通过: {vram:.1f} GB")

    def test_gpu_tflops_estimation(self):
        """测试GPU算力估算"""
        tflops, info = self.evaluator.estimate_gpu_tflops()
        assert tflops >= 0
        assert "source" in info
        print(f"✅ GPU算力估算测试通过: {tflops:.1f} TFLOPS (来源: {info['source']})")

    def test_comprehensive_report(self):
        """测试综合报告生成"""
        report = self.evaluator.generate_comprehensive_report()
        assert "overall_score" in report
        assert "pretraining_assessment" in report
        assert "finetuning_assessment" in report
        assert "self_improvement_assessment" in report
        print(f"✅ 综合报告测试通过: 评分 {report['overall_score']['grade']}")

    def test_pretraining_evaluation(self):
        """测试预训练评估"""
        result = self.evaluator.evaluate_pretraining_capability()
        assert "capable_models" in result
        assert "gpu_tflops_fp16" in result
        print(f"✅ 预训练评估测试通过: {len(result['capable_models'])} 个模型可训练")

    def test_finetuning_evaluation(self):
        """测试微调评估"""
        result = self.evaluator.evaluate_finetuning_capability()
        assert "qlora_finetuning_feasible_count" in result
        print(f"✅ 微调评估测试通过: {result['qlora_finetuning_feasible_count']} 个模型可QLoRA微调")

    def test_self_improvement_evaluation(self):
        """测试自进化评估"""
        result = self.evaluator.evaluate_self_improvement_capability()
        assert "capabilities" in result
        assert "recommended_capabilities" in result
        print(f"✅ 自进化评估测试通过: {len(result['recommended_capabilities'])} 种能力可行")

    def test_gpu_ranking(self):
        """测试GPU排名"""
        rankings = self.evaluator.get_gpu_ranking()
        assert len(rankings) > 0
        assert rankings[0]["tflops_fp16"] >= rankings[-1]["tflops_fp16"]
        print(f"✅ GPU排名测试通过: {len(rankings)} 个GPU")

    def test_overall_score(self):
        """测试综合评分"""
        score = self.evaluator._calculate_overall_score(80, 24)
        assert "total" in score
        assert "grade" in score
        assert "description" in score
        print(f"✅ 综合评分测试通过: {score['grade']} ({score['total']}分)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])
