#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试新模块"""

import sys
sys.path.insert(0, '.')

try:
    print("测试1: 导入 HardwareDetector...")
    from hardware import HardwareDetector
    print("✅ 导入成功")

    print("\n测试2: 初始化检测器...")
    detector = HardwareDetector()
    print("✅ 初始化成功")

    print("\n测试3: 获取硬件快照...")
    snapshot = detector.get_hardware_snapshot()
    print(f"✅ 快照获取成功，版本: {snapshot.get('version')}")

    print("\n测试4: 测试 CPU 信息...")
    cpu = detector.get_cpu_info()
    print(f"✅ CPU: {cpu.get('model')}, 核心数: {cpu.get('count')}")

    print("\n测试5: 测试内存信息...")
    memory = detector.get_memory_info()
    print(f"✅ 内存: {memory.get('total'):.2f} GB")

    print("\n测试6: 测试 GPU 信息...")
    gpu = detector.get_gpu_info()
    print(f"✅ GPU: 可用={gpu.get('available')}, 数量={gpu.get('count')}")

    print("\n测试7: 测试硬件评分...")
    score = detector.calculate_hardware_score(snapshot)
    print(f"✅ 硬件评分: {score}/100")

    print("\n测试8: 测试训练推荐...")
    recs = detector.get_training_recommendations(snapshot)
    print(f"✅ 推荐模型: {recs.get('max_model_size')}, 模式: {recs.get('recommended_mode')}")

    print("\n" + "=" * 60)
    print("🎉 所有测试通过！系统运行正常！")
    print("=" * 60)

except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
