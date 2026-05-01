import os
import sys

# 配置 HuggingFace 镜像源（中国区加速）
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
)
# 尝试导入 bitsandbytes，如果 GPU 模式下需要用到
try:
    from transformers import BitsAndBytesConfig
    from peft import prepare_model_for_kbit_training
    has_bnb = True
except ImportError:
    has_bnb = False

from peft import LoraConfig, get_peft_model
from trl import SFTTrainer

import json
import time
from datetime import datetime
from smart_trainer import SmartTrainer, SmartResourceManager, AdaptiveTrainingConfig
from backend.data_analyzer import DataHealthChecker


def run_smart_training():
    """运行智能训练流程 - 完全自动化的AI训练环境配置与执行"""
    print("\n" + "="*70)
    print("🤖 Gemma 2B 全自动智能微调训练系统")
    print("   功能: 硬件分析 · 智能推荐 · 自动配置 · 资源监控")
    print("="*70)
    
    # 检测运行模式
    is_auto_mode = (
        not sys.stdin.isatty() or
        os.environ.get('AUTO_TRAIN', '').lower() == 'true' or
        os.environ.get('CI', '').lower() == 'true'
    )
    
    # 初始化智能训练器
    smart_trainer = SmartTrainer(auto_mode=is_auto_mode)
    
    # 设置训练环境（自动分析硬件并选择最佳配置）
    env_config = smart_trainer.setup_training_environment()
    selected_mode = env_config["config"]
    
    # --- 数据准备与智能体检 ---
    print("\n【1. 数据智能体检阶段】")
    dataset_path = os.environ.get('DATASET_PATH', 'dataset.jsonl')
    
    # 初始化数据分析师
    health_checker = DataHealthChecker(dataset_path)
    health_report = health_checker.check_and_fix()
    
    if not health_report["is_healthy"] and health_report["total_samples"] > 0:
        print("⚠️ 数据集存在严重问题，尝试自动修复并清洗...")
        dataset_path = health_checker.save_cleaned_data()
    
    # 打印数据建议
    data_advice = health_checker.get_smart_advice()
    for tip in data_advice:
        print(f"   {tip}")
    
    if not os.path.exists(dataset_path):
        print(f"⚠️ 找不到数据集 '{dataset_path}'，自动生成模板数据...")
        sample_data = [
            {"instruction": "你好", "input": "", "output": "你好！我是您的专属AI助手。"},
            {"instruction": "什么是机器学习？", "input": "", "output": "机器学习是人工智能的一个分支，它使计算机能够从数据中学习，而无需明确编程。"},
            {"instruction": "翻译为英文", "input": "今天天气很好", "output": "The weather is very good today."},
            {"instruction": "写一首关于春天的诗", "input": "", "output": "春风拂面柳丝长，\n桃花映日满园香。\n燕子归来寻旧垒，\n儿童散学放风筝。"}
        ]
        with open(dataset_path, 'w', encoding='utf-8') as f:
            for entry in sample_data:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        print(f"✅ 已生成模板数据：{dataset_path} (共 {len(sample_data)} 条)")
    
    # --- 加载数据集 ---
    print(f"\n正在加载数据集: {dataset_path}")
    try:
        dataset = load_dataset('json', data_files=dataset_path, split='train')
        print(f"✅ 成功加载数据集，共 {len(dataset)} 条样本")
    except Exception as e:
        print(f"❌ 加载数据集失败: {e}")
        exit(1)
    
    def format_instruction(sample):
        prompt = f"<start_of_turn>user\n{sample['instruction']}"
        if sample.get('input'):
             prompt += f"\n{sample['input']}"
        prompt += f"<end_of_turn>\n<start_of_turn>model\n{sample['output']}<end_of_turn>"
        return {"text": prompt}
    
    print("正在格式化数据集...")
    formatted_dataset = dataset.map(format_instruction, remove_columns=dataset.column_names)
    print("✅ 数据集格式化完成")
    
    # --- 加载模型 ---
    print(f"\n正在加载 Gemma 模型 (设备: {'CPU' if selected_mode.device == 'cpu' else 'GPU'})...")
    model_id = "unsloth/gemma-2b-it"
    
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    
    # 量化配置
    quantization_config = None
    if selected_mode.device == 'cuda' and selected_mode.quantization:
        if selected_mode.quantization == '4bit' and has_bnb:
            print("🔧 配置 4-bit 量化...")
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
            )
        elif selected_mode.quantization == '8bit' and has_bnb:
            print("🔧 配置 8-bit 量化...")
            quantization_config = BitsAndBytesConfig(load_in_8bit=True)
    
    # 加载模型
    if selected_mode.device == 'cpu':
        print("🖥️ 使用 CPU 模式加载模型...")
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            device_map="cpu",
            torch_dtype=torch.float32
        )
    else:
        print("🎮 使用 GPU 模式加载模型...")
        if quantization_config:
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                quantization_config=quantization_config,
                device_map="auto",
                torch_dtype=torch.float16
            )
            if has_bnb:
                model = prepare_model_for_kbit_training(model)
        else:
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                device_map="auto",
                torch_dtype=torch.float16
            )
    
    print("✅ 模型加载完成")
    
    # --- 智能参数锁定 ---
    print("\n【2. 智能参数锁定阶段】")
    optimal_args = smart_trainer.adaptive_config.precompute_optimal_args()
    
    # --- 配置 LoRA ---
    print(f"\n🔧 配置 LoRA (r={selected_mode.lora_r}, alpha={selected_mode.lora_alpha})...")
    lora_config = LoraConfig(
        r=selected_mode.lora_r,
        lora_alpha=selected_mode.lora_alpha,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout=selected_mode.lora_dropout,
        bias="none",
        task_type="CAUSAL_LM"
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    
    # --- 训练参数 (使用智能预测结果) ---
    output_dir = "./gemma-2b-finetuned-lora"
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=optimal_args["per_device_train_batch_size"], # 注意：此处应为 epochs，修正逻辑
        per_device_train_batch_size=optimal_args["per_device_train_batch_size"],
        gradient_accumulation_steps=optimal_args["gradient_accumulation_steps"],
        optim=optimal_args["optim"],
        learning_rate=optimal_args["learning_rate"],
        logging_steps=10,
        save_strategy="epoch",
        fp16=optimal_args["fp16"],
        bf16=optimal_args["bf16"],
        gradient_checkpointing=optimal_args["gradient_checkpointing"],
        max_grad_norm=0.3,
        warmup_ratio=optimal_args["warmup_ratio"],
        lr_scheduler_type=optimal_args["lr_scheduler_type"],
        group_by_length=True,
        report_to="none"
    )
    # 修正 epochs
    training_args.num_train_epochs = selected_mode.epochs
    
    # --- 启动资源监控 ---
    smart_trainer.start_training_monitor()
    
    # --- 开始训练 ---
    print("\n" + "="*70)
    print("🚀 开始智能训练!")
    print(f"   模式: {selected_mode.mode_name}")
    print(f"   设备: {'CPU' if selected_mode.device == 'cpu' else 'GPU'}")
    print(f"   轮数: {selected_mode.epochs}")
    print(f"   Batch: {selected_mode.batch_size} (累积: {selected_mode.gradient_accumulation_steps})")
    print(f"   学习率: {selected_mode.learning_rate}")
    print(f"   序列长度: {selected_mode.max_seq_length}")
    print("="*70 + "\n")
    
    start_time = time.time()
    
    try:
        trainer = SFTTrainer(
            model=model,
            train_dataset=formatted_dataset,
            args=training_args
        )
        
        trainer.train()
        
        # 计算训练时间
        training_time = time.time() - start_time
        hours = int(training_time // 3600)
        minutes = int((training_time % 3600) // 60)
        seconds = int(training_time % 60)
        
        print("\n" + "="*70)
        print("✅ 训练完成!")
        print(f"   总训练时间: {hours}小时 {minutes}分钟 {seconds}秒")
        print("="*70)
        
        # 保存模型
        print(f"\n💾 正在保存模型到 {output_dir}...")
        trainer.save_model(output_dir)
        print("✅ 模型保存完成!")
        
        # 停止监控并获取资源摘要
        resource_summary = smart_trainer.stop_training_monitor()
        
        # 生成完整训练报告
        training_report = {
            "timestamp": datetime.now().isoformat(),
            "model_id": model_id,
            "output_dir": output_dir,
            "training_config": {
                "mode_name": selected_mode.mode_name,
                "device": selected_mode.device,
                "epochs": selected_mode.epochs,
                "batch_size": selected_mode.batch_size,
                "gradient_accumulation_steps": selected_mode.gradient_accumulation_steps,
                "learning_rate": selected_mode.learning_rate,
                "max_seq_length": selected_mode.max_seq_length,
                "lora_r": selected_mode.lora_r,
                "lora_alpha": selected_mode.lora_alpha,
                "quantization": selected_mode.quantization,
                "optimizer": selected_mode.optimizer
            },
            "hardware": {
                "score": smart_trainer.analyzer._calculate_hardware_score(),
                "device": selected_mode.device,
                "cpu_count": smart_trainer.analyzer.info.cpu_count,
                "total_ram_gb": smart_trainer.analyzer.info.total_ram_gb,
                "gpu_vram_gb": smart_trainer.analyzer.info.gpu_vram_gb
            },
            "dataset": {
                "path": dataset_path,
                "samples": len(dataset)
            },
            "training_result": {
                "total_time_seconds": training_time,
                "total_time_formatted": f"{hours}h {minutes}m {seconds}s",
                "status": "success"
            },
            "resource_usage": resource_summary
        }
        
        report_path = "training_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(training_report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 智能训练报告已保存至: {report_path}")
        
        print("\n" + "="*70)
        print("🎉 智能训练全部完成!")
        print("   下一步建议:")
        print("   1. 运行 merge_model.py 合并 LoRA 权重")
        print("   2. 运行 inference.py 测试模型效果")
        print("   3. 使用 Ollama 部署模型")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ 训练过程中出现错误: {e}")
        smart_trainer.stop_training_monitor()
        import traceback
        traceback.print_exc()
        exit(1)


# 主入口
if __name__ == "__main__":
    run_smart_training()
