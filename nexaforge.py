#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智核万炼® NexaForge AI - 智能微调训练平台
NexaForge AI - Intelligent Fine-tuning Platform

设计理念: 开箱即用，智核万炼
Design Philosophy: Out-of-the-box, Intelligent Core Refinement

功能特性:
- 全自动硬件检测与智能配置
- 一键启动AI模型微调训练
- 多模式资源自适应分配
- 实时监控与智能调优
- 零配置开箱即用体验
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path

# 品牌标识
BRAND = {
    "name_cn": "智核万炼",
    "name_en": "NexaForge AI",
    "version": "1.0.0",
    "slogan": "开箱即用，智核万炼",
    "slogan_en": "Out-of-the-box, Intelligent Core Refinement"
}


def print_banner():
    """打印品牌横幅"""
    banner = f"""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║     ██╗   ██╗███████╗██╗  ██╗ █████╗ ███████╗ ██████╗ ██████╗      ║
║     ╚██╗ ██╔╝██╔════╝╚██╗██╔╝██╔══██╗██╔════╝██╔═══██╗██╔══██╗     ║
║      ╚████╔╝ █████╗   ╚███╔╝ ███████║█████╗  ██║   ██║██████╔╝     ║
║       ╚██╔╝  ██╔══╝   ██╔██╗ ██╔══██║██╔══╝  ██║   ██║██╔══██╗     ║
║        ██║   ███████╗██╔╝ ██╗██║  ██║██║     ╚██████╔╝██║  ██║     ║
║        ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝      ╚═════╝ ╚═╝  ╚═╝     ║
║                                                                      ║
║              {BRAND['name_cn']}® {BRAND['name_en']} v{BRAND['version']}              ║
║                                                                      ║
║                    {BRAND['slogan']}                     ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_environment():
    """检查运行环境并自动安装依赖"""
    print("🔍 正在检查运行环境...")
    
    required_packages = [
        "torch", "transformers", "datasets", "peft", "trl", "psutil",
        "accelerate", "bitsandbytes"
    ]
    
    missing = []
    for pkg in required_packages:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print(f"⚠️ 检测到缺少依赖: {', '.join(missing)}")
        print("🔄 正在自动安装缺失的依赖...")
        
        # 使用清华镜像加速安装
        cmd = [sys.executable, "-m", "pip", "install", "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"]
        cmd.extend(missing)
        
        try:
            subprocess.run(cmd, check=True)
            print("✅ 依赖安装完成!")
        except subprocess.CalledProcessError:
            print("❌ 依赖安装失败，请手动运行: pip install -r requirements.txt")
            return False
    else:
        print("✅ 所有依赖已就绪")
    
    return True


def setup_workspace():
    """设置工作空间"""
    print("\n📁 正在初始化工作空间...")
    
    # 创建工作目录
    dirs = ["models", "datasets", "outputs", "logs", "configs"]
    for d in dirs:
        Path(d).mkdir(exist_ok=True)
    
    # 创建示例数据集
    dataset_file = "datasets/example.jsonl"
    if not os.path.exists(dataset_file):
        sample_data = [
            {
                "instruction": "请介绍智核万炼AI训练平台",
                "input": "",
                "output": "智核万炼(NexaForge AI)是一款开箱即用的AI模型微调训练平台，支持全自动硬件检测、智能资源配置和多模式训练，让AI训练变得简单高效。"
            },
            {
                "instruction": "什么是机器学习？",
                "input": "",
                "output": "机器学习是人工智能的一个分支，它使计算机能够从数据中学习规律和模式，而无需进行明确的编程。"
            },
            {
                "instruction": "翻译以下句子为英文",
                "input": "智核万炼让AI训练变得简单",
                "output": "NexaForge AI makes training simple and efficient."
            },
            {
                "instruction": "写一首关于AI的诗",
                "input": "",
                "output": "硅基智慧启新程，\n神经网络织梦行。\n万千数据炼真核，\n智核万炼铸辉煌。"
            }
        ]
        
        with open(dataset_file, 'w', encoding='utf-8') as f:
            for entry in sample_data:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        
        print(f"✅ 已创建示例数据集: {dataset_file}")
    
    print("✅ 工作空间初始化完成")
    return dataset_file


def print_quick_start():
    """打印快速开始指南"""
    guide = """
╔══════════════════════════════════════════════════════════════════════╗
║                        🚀 快速开始指南                               ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  1️⃣  准备数据                                                        ║
║      将您的训练数据放入 datasets/ 目录下，格式为 JSONL               ║
║      每条记录包含: instruction, input, output 字段                   ║
║                                                                      ║
║  2️⃣  启动训练                                                        ║
║      方式A - 全自动模式 (推荐):                                      ║
║          python nexaforge.py --auto                                  ║
║                                                                      ║
║      方式B - 交互式模式:                                             ║
║          python nexaforge.py --interactive                           ║
║                                                                      ║
║      方式C - 指定数据集:                                             ║
║          python nexaforge.py --dataset datasets/your_data.jsonl      ║
║                                                                      ║
║  3️⃣  查看结果                                                        ║
║      训练完成后，模型保存在 outputs/ 目录                            ║
║      训练报告保存在 training_report.json                             ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """
    print(guide)


def run_training(auto_mode=True, dataset_path=None):
    """运行训练流程"""
    # 设置环境变量
    os.environ['AUTO_TRAIN'] = 'true' if auto_mode else 'false'
    if dataset_path:
        os.environ['DATASET_PATH'] = dataset_path
    
    # 导入并运行智能训练
    try:
        from finetune import run_smart_training
        run_smart_training()
    except Exception as e:
        print(f"\n❌ 训练失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主入口 - 智核万炼 AI训练平台"""
    print_banner()
    
    # 解析命令行参数
    args = sys.argv[1:]
    
    # 帮助信息
    if '--help' in args or '-h' in args:
        print_quick_start()
        return
    
    # 版本信息
    if '--version' in args or '-v' in args:
        print(f"{BRAND['name_cn']}® {BRAND['name_en']} v{BRAND['version']}")
        return
    
    # 检查环境
    if not check_environment():
        print("❌ 环境检查失败，请修复后重试")
        return
    
    # 设置工作空间
    default_dataset = setup_workspace()
    
    # 确定运行模式
    auto_mode = '--auto' in args or '--interactive' not in args
    dataset_path = None
    
    # 解析数据集路径
    for i, arg in enumerate(args):
        if arg == '--dataset' and i + 1 < len(args):
            dataset_path = args[i + 1]
            break
    
    # 如果不是自动模式，显示快速开始指南
    if not auto_mode:
        print_quick_start()
        print("\n💡 按提示进行操作...\n")
    else:
        print(f"\n🤖 启动全自动训练模式...")
        print(f"📊 系统将自动检测硬件并选择最优配置\n")
    
    # 运行训练
    run_training(auto_mode=auto_mode, dataset_path=dataset_path or default_dataset)


if __name__ == "__main__":
    main()
