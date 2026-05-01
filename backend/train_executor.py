import os
import sys
import io

# 强制设置 Windows 终端输出编码为 UTF-8
if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

# 配置 HuggingFace 镜像源（中国区加速）
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

import torch
import json
import time
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    TrainerCallback,
    BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model
from trl import SFTTrainer
from smart_trainer import SmartTrainer
from backend.data_analyzer import DataHealthChecker

class ProgressCallback(TrainerCallback):
    def __init__(self, queue):
        self.queue = queue

    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs:
            progress_data = {
                "step": state.global_step,
                "total_steps": state.max_steps,
                "loss": logs.get("loss", 0),
                "learning_rate": logs.get("learning_rate", 0),
                "epoch": state.epoch,
                "status": "training"
            }
            self.queue.put(progress_data)

def run_fine_tune(config, progress_queue):
    """
    [智核万炼：核心执行引擎]
    实现从硬件扫描到模型调优的全链路自动化
    """
    try:
        # --- 1. 智核硬件体检与策略生成 ---
        progress_queue.put({"status": "analyzing", "message": "正在深度扫描硬件算力矩阵与软件环境..."})
        smart_trainer = SmartTrainer(auto_mode=True)
        
        # 预计算最优训练参数矩阵
        optimal_args, optimization_notes = smart_trainer.adaptive_config.precompute_optimal_args(
            epochs=config.get('epochs', 3),
            learning_rate=config.get('learning_rate', 2e-4)
        )
        
        gpu_info = smart_trainer.analyzer.get_gpu_info()
        progress_queue.put({
            "status": "env_report",
            "gpu": gpu_info["name"] if gpu_info else "CPU Mode",
            "vram": f"{gpu_info['vram_total_gb']}GB" if gpu_info else "N/A",
            "cap": gpu_info["compute_capability"] if gpu_info else "N/A",
            "count": gpu_info["count"] if gpu_info else 0,
            "notes": optimization_notes
        })
        time.sleep(1.0)
        
        # --- 2. 数据智能体检与自愈 ---
        progress_queue.put({"status": "analyzing", "message": "正在执行数据集智能体检..."})
        dataset_path = config["dataset_path"]
        health_checker = DataHealthChecker(dataset_path)
        health_report = health_checker.check_and_fix()
        
        if not health_report["is_healthy"] and health_report["total_samples"] > 0:
            dataset_path = health_checker.save_cleaned_data()
            progress_queue.put({"status": "info", "message": "发现数据漏洞，智核已自动执行自愈清洗"})

        # --- 3. 智核驱动的模型加载调优 ---
        model_id = "unsloth/gemma-2b-it"
        output_dir = "./gemma-2b-finetuned-lora"
        
        # --- 3. 智核驱动的跨平台自适应加载 ---
        is_cpu_mode = optimal_args.get("device") == "cpu"
        device_label = "CPU Cluster" if is_cpu_mode else f"GPU Group ({gpu_info['count']} nodes)"
        progress_queue.put({"status": "loading_model", "message": f"正在构建 {device_label} 炼制环境..."})
        
        # 显存/内存管理优化
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
        
        # 动态计算计算精度与设备分配
        if is_cpu_mode:
            torch_dtype = torch.float32 
            q_config = None # CPU 不支持 bnb 量化
            device_map = {"": "cpu"}
        else:
            torch_dtype = torch.bfloat16 if optimal_args.get("bf16") else torch.float16
            device_map = "auto"
            q_config = None
            if optimal_args.get("use_4bit"):
                q_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch_dtype,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_use_double_quant=True,
                )

        # 多卡显存配额 (仅在 GPU 模式下生效)
        max_memory = None
        if not is_cpu_mode and gpu_info and gpu_info["count"] > 1:
            max_memory = {i: f"{int(torch.cuda.get_device_properties(i).total_memory / 1024**3 * 0.9)}GiB" for i in range(gpu_info["count"])}
            progress_queue.put({"status": "info", "message": "已激活多卡显存均衡策略 (Load Balancing)"})

        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            device_map=device_map,
            max_memory=max_memory,
            quantization_config=q_config,
            torch_dtype=torch_dtype,
            attn_implementation=optimal_args.get("attn_implementation", "eager"),
            trust_remote_code=True
        )
        
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        tokenizer.pad_token = tokenizer.eos_token
        
        # --- 4. 动态 LoRA 适配 ---
        peft_config = LoraConfig(
            r=8 if is_cpu_mode or (gpu_info and gpu_info['vram_total_gb'] < 12) else 16,
            lora_alpha=32,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM",
        )
        model = get_peft_model(model, peft_config)

        # --- 5. 参数全量注入 ---
        training_args = TrainingArguments(
            output_dir=output_dir,
            per_device_train_batch_size=optimal_args['batch_size'],
            gradient_accumulation_steps=optimal_args['gradient_accumulation_steps'],
            learning_rate=config.get('learning_rate', 2e-4),
            num_train_epochs=config.get('epochs', 3),
            logging_steps=1,
            save_steps=100,
            evaluation_strategy="no",
            optim=optimal_args['optim'],
            fp16=optimal_args.get('fp16', True) if not is_cpu_mode else False,
            bf16=optimal_args.get('bf16', False) if not is_cpu_mode else False,
            gradient_checkpointing=optimal_args.get('gradient_checkpointing', True),
            report_to="none",
            remove_unused_columns=False,
            no_cuda=is_cpu_mode
        )

        # 加载数据
        dataset = load_dataset('json', data_files=dataset_path, split='train')
        def format_instruction(sample):
            p = f"<start_of_turn>user\n{sample['instruction']}"
            if sample.get('input'): p += f"\n{sample['input']}"
            p += f"<end_of_turn>\n<start_of_turn>model\n{sample['output']}<end_of_turn>"
            return {"text": p}
        formatted_dataset = dataset.map(format_instruction, remove_columns=dataset.column_names)

        # --- 6. 执行炼制 ---
        trainer = SFTTrainer(
            model=model,
            train_dataset=formatted_dataset,
            args=training_args,
            callbacks=[ProgressCallback(progress_queue)]
        )

        progress_queue.put({"status": "starting", "message": "智核适配完成，开始神经元权重炼制..."})
        trainer.train()
        
        trainer.save_model(output_dir)
        progress_queue.put({"status": "completed", "message": "智核万炼圆满完成，权重已固化。"})

    except Exception as e:
        progress_queue.put({"status": "error", "message": str(e)})
