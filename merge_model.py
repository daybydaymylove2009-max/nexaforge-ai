import os

# 配置 HuggingFace 镜像源（中国区加速）
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

def merge_and_save():
    print("="*50)
    print("模型合并工具：将 LoRA 权重合并至基础模型")
    print("="*50)
    
    base_model_id = "unsloth/gemma-2b-it"
    lora_weights_dir = "./gemma-2b-finetuned-lora"
    output_dir = "./gemma-2b-merged"

    # 检查 LoRA 权重是否存在
    if not os.path.exists(lora_weights_dir):
        print(f"错误: 找不到 LoRA 权重目录 '{lora_weights_dir}'。请先运行 finetune.py 训练模型。")
        return

    print("1. 正在加载分词器...")
    tokenizer = AutoTokenizer.from_pretrained(lora_weights_dir)

    print("2. 正在加载基础模型 (为了合并，使用 float32 和 CPU 加载)...")
    # 因为您是 CPU 环境且显存只有 1G，我们强制用 CPU 内存加载
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_id,
        device_map="cpu",
        torch_dtype=torch.float32
    )

    print("3. 正在加载 LoRA 权重...")
    model = PeftModel.from_pretrained(base_model, lora_weights_dir)

    print("4. 正在执行合并 (Merge and Unload)... 这可能需要几分钟。")
    # 将 LoRA 层的权重永久叠加到基础模型的权重上
    model = model.merge_and_unload()

    print(f"5. 正在将合并后的完整模型保存至 {output_dir} ...")
    # 必须保存为 safetensors 格式，以供 Ollama 读取
    model.save_pretrained(output_dir, safe_serialization=True)
    tokenizer.save_pretrained(output_dir)

    print("\n合并完成！您可以继续使用 Ollama 导入该模型了。")

if __name__ == "__main__":
    merge_and_save()
