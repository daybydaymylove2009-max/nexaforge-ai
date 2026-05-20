#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试综合算力评估"""

from hardware import ComputeEvaluator
from hardware.detector import HardwareDetector

print("🔍 测试综合算力评估...")
detector = HardwareDetector()
snapshot = detector.get_hardware_snapshot()
evaluator = ComputeEvaluator(snapshot)

print(f"GPU: {evaluator.detect_gpu_model()}")
print(f"显存: {evaluator.get_vram_gb():.1f} GB")

tflops, info = evaluator.estimate_gpu_tflops()
print(f"算力: {tflops:.1f} TFLOPS")
print(f"数据源: {info['source']}")

report = evaluator.generate_comprehensive_report()
print(f"\n综合评分: {report['overall_score']['grade']} ({report['overall_score']['total']}分)")
print(f"描述: {report['overall_score']['description']}")

print(f"\n预训练能力: {len(report['pretraining_assessment']['capable_models'])} 个模型可训练")
print(f"微调能力: {report['finetuning_assessment']['qlora_finetuning_feasible_count']} 个模型可QLoRA微调")
print(f"自进化能力: {len(report['self_improvement_assessment']['recommended_capabilities'])} 种可行")

print("\n✅ 综合算力评估测试成功!")
