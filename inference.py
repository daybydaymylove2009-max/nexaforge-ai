import os

# 配置 HuggingFace 镜像源（中国区加速）
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

def configure_hardware():
    print("="*60)
    print("✨ Gemma 2B 推理系统 (智能诊断版) ✨")
    print("="*60)
    
    cpu_count = os.cpu_count()
    has_gpu = torch.cuda.is_available()
    
    print("\n【硬件环境扫描】")
    print(f"🖥️  CPU核心数: {cpu_count}")
    if has_gpu:
        gpu_name = torch.cuda.get_device_name(0)
        gpu_vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"🎮 检测到 GPU: {gpu_name} (显存: {gpu_vram:.1f} GB)")
    else:
        print("🎮 状态: 未检测到 NVIDIA GPU。")

    print("\n--- 💡 推理运行建议 ---")
    recommendation = "CPU"
    if not has_gpu or gpu_vram < 2.5:
        print("💡 建议：使用 [CPU] 模式。您的 32G 内存足以流畅运行合并后的模型。")
    else:
        print("💡 建议：使用 [GPU] 模式，响应速度会更快。")
        recommendation = "GPU"

    print("-" * 60)
    choice = input(f"请选择计算设备 (c=强制CPU, g=使用GPU) [推荐: {'c' if recommendation=='CPU' else 'g'}]: ").strip().lower()
    
    use_cpu = True
    if choice == 'g' and has_gpu:
        use_cpu = False
    elif choice == 'c':
        use_cpu = True
    else:
        use_cpu = (recommendation == "CPU")
            
    if use_cpu:
        os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
        threads = input(f"配置 CPU 线程数 (1-{cpu_count}) [默认: {cpu_count}]: ").strip()
        if threads.isdigit():
            torch.set_num_threads(int(threads))
        print(f"✅ 已设定为 CPU 模式 ({torch.get_num_threads()} 线程)")
    else:
        print("✅ 已设定为 GPU 模式")
        
    print("="*60 + "\n")
    return use_cpu

USE_CPU = configure_hardware()

# 1. 基础配置
base_model_id = "unsloth/gemma-2b-it"
lora_weights_dir = "./gemma-2b-finetuned-lora"

print("正在加载分词器...")
tokenizer = AutoTokenizer.from_pretrained(lora_weights_dir)

print(f"正在加载基础模型 ({'CPU, float32' if USE_CPU else 'GPU, fp16'})...")
if USE_CPU:
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_id,
        device_map="cpu",
        torch_dtype=torch.float32
    )
else:
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_id,
        torch_dtype=torch.float16,
        device_map="auto"
    )

print("正在将 LoRA 权重合并到基础模型...")
# 加载 LoRA 适配器
model = PeftModel.from_pretrained(base_model, lora_weights_dir)

def generate_response(instruction, input_text=""):
    """
    生成回复
    """
    # 构造与训练时完全一致的 prompt
    prompt = f"<start_of_turn>user\n{instruction}"
    if input_text:
         prompt += f"\n{input_text}"
    prompt += f"<end_of_turn>\n<start_of_turn>model\n"
    
    device_str = "cpu" if USE_CPU else model.device
    inputs = tokenizer(prompt, return_tensors="pt").to(device_str)
    
    print("\n[模型思考中... (CPU 计算较慢，请耐心等待)]" if USE_CPU else "\n[模型思考中...]")
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=512,       # 生成最大长度
            temperature=0.7,          # 创造性 (0.0 更精确，1.0 更随机)
            do_sample=True,
            top_k=50,
            top_p=0.9,
            repetition_penalty=1.1    # 避免重复生成
        )
    
    # 截取新生成的部分（去掉输入的 prompt）
    input_length = inputs.input_ids.shape[1]
    generated_tokens = outputs[0][input_length:]
    
    response = tokenizer.decode(generated_tokens, skip_special_tokens=True)
    return response

if __name__ == "__main__":
    print("\n--- Gemma 2B LoRA 推理测试 ---")
    print("输入 'quit' 或 'exit' 退出程序。")
    
    while True:
        try:
            instruction = input("\n[User 问题或指令]: ")
            if instruction.lower() in ['quit', 'exit']:
                break
                
            input_text = input("[补充内容 (可选，直接回车跳过)]: ")
            
            response = generate_response(instruction, input_text)
            print(f"\n[Gemma 回复]:\n{response}")
            print("-" * 50)
            
        except KeyboardInterrupt:
            break
            
    print("\n测试结束。")
