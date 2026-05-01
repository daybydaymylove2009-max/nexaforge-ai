import os
import sys
import time
import json
import threading
import psutil
from typing import Dict, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from hardware_analyzer import HardwareAnalyzer, TrainingConfig

@dataclass
class TrainingMetrics:
    """训练指标数据类"""
    epoch: int
    loss: float
    learning_rate: float
    throughput: float  # samples/sec
    memory_used_gb: float
    cpu_percent: float
    timestamp: str

class SmartResourceManager:
    """智能资源管理器 - 动态分配和监控训练资源"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.monitoring = False
        self.metrics_history: list = []
        self.peak_memory_gb = 0.0
        self.peak_cpu_percent = 0.0
        self.start_time = None
        
    def start_monitoring(self):
        """启动资源监控线程"""
        self.monitoring = True
        self.start_time = time.time()
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("✅ 智能资源监控已启动")
        
    def stop_monitoring(self):
        """停止资源监控"""
        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=2)
        print("✅ 智能资源监控已停止")
        
    def _monitor_loop(self):
        """监控循环 - 每秒收集一次资源使用情况"""
        while self.monitoring:
            try:
                # 获取系统资源使用情况
                memory = psutil.virtual_memory()
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_used_gb = (memory.total - memory.available) / (1024**3)
                
                # 更新峰值
                self.peak_memory_gb = max(self.peak_memory_gb, memory_used_gb)
                self.peak_cpu_percent = max(self.peak_cpu_percent, cpu_percent)
                
                # 如果内存使用超过90%，发出警告
                if memory.percent > 90:
                    print(f"\n⚠️ 警告: 内存使用率达到 {memory.percent:.1f}%，建议降低 batch_size 或序列长度")
                    
            except Exception as e:
                pass
                
    def get_resource_summary(self) -> Dict:
        """获取资源使用摘要"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        return {
            "peak_memory_gb": self.peak_memory_gb,
            "peak_cpu_percent": self.peak_cpu_percent,
            "elapsed_time_seconds": elapsed,
            "elapsed_time_formatted": self._format_time(elapsed)
        }
    
    @staticmethod
    def _format_time(seconds: float) -> str:
        """格式化时间"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours}h {minutes}m {secs}s"


class AdaptiveTrainingConfig:
    """自适应训练配置 - 根据硬件和训练状态动态调整参数"""
    
    def __init__(self, base_config: TrainingConfig, hardware_info):
        self.base = base_config
        self.hardware = hardware_info
        self.adaptive_enabled = True
        self.current_batch_size = base_config.batch_size
        self.current_max_seq_length = base_config.max_seq_length
        self.oom_count = 0
        
    def adjust_for_oom(self):
        """遇到OOM时自动调整配置"""
        self.oom_count += 1
        print(f"\n⚠️ 检测到内存不足 (OOM #{self.oom_count})，正在自动调整配置...")
        
        if self.current_batch_size > 1:
            self.current_batch_size = max(1, self.current_batch_size // 2)
            print(f"   Batch Size 调整为: {self.current_batch_size}")
        elif self.current_max_seq_length > 128:
            self.current_max_seq_length = max(128, self.current_max_seq_length // 2)
            print(f"   序列长度调整为: {self.current_max_seq_length}")
        else:
            print("   已降至最低配置，建议启用梯度检查点或量化")

    def precompute_optimal_args(self, epochs=3, learning_rate=2e-4):
        gpu_info = self.analyzer.get_gpu_info()
        vram = gpu_info["vram_total_gb"] if gpu_info else 0
        cpu_cores = self.analyzer.get_cpu_info()["physical_cores"]
        
        # 基础配置
        config = {
            "batch_size": 1,
            "gradient_accumulation_steps": 4,
            "use_4bit": True,
            "use_nested_quant": True,
            "bnb_4bit_compute_dtype": "float16",
            "optim": "paged_adamw_32bit",
            "gradient_checkpointing": True,
            "bf16": False,
            "fp16": True,
            "max_seq_length": 512,
            "report_to": "none"
        }
        
        # 优化矩阵
        optimization_notes = []
        
        if vram >= 80: # H100 / A100 80GB
            config.update({
                "batch_size": 16,
                "gradient_accumulation_steps": 1,
                "use_4bit": False,
                "bf16": True,
                "optim": "adamw_torch_fused", # 开启融合优化器加速
                "max_seq_length": 4096
            })
            optimization_notes.append("🚀 检测到顶级算力卡 H100/A100，已激活 4K 上下文及融合优化器 (Fused Optimizer)。")
        elif vram >= 24: # RTX 3090 / 4090 / A10
            config.update({
                "batch_size": 4,
                "gradient_accumulation_steps": 1,
                "use_4bit": False,
                "bf16": True,
                "optim": "adamw_torch",
                "max_seq_length": 2048
            })
            optimization_notes.append("🚀 监测到高性能 GPU，已自动开启 BF16 原生训练以获得最高精度。")
        elif vram >= 12: # RTX 3060 / 4070
            config.update({
                "batch_size": 2,
                "gradient_accumulation_steps": 2,
                "optim": "paged_adamw_8bit",
                "max_seq_length": 1024
            })
            optimization_notes.append("⚖️ 监测到中端 GPU，已平衡 BatchSize 与 8-bit 优化。")
        elif vram >= 1: # 低显存显卡
            config.update({
                "batch_size": 1,
                "gradient_accumulation_steps": 8,
                "use_4bit": True,
                "optim": "paged_adamw_8bit",
                "max_seq_length": 256
            })
            optimization_notes.append("🛡️ 警告: 显存极低，已强制开启极限 QLoRA 模式，训练速度将受限。")
        else: # 纯 CPU 模式
            config.update({
                "batch_size": 1,
                "gradient_accumulation_steps": 4,
                "use_4bit": False, # CPU 不支持量化算子 (bnb)
                "fp16": False,
                "bf16": False,
                "optim": "adamw_torch",
                "max_seq_length": 128,
                "device": "cpu"
            })
            optimization_notes.append("💻 监测到无可用 GPU，已自动切换至“纯 CPU 炼制模式”。注意：炼制速度将显著变慢。")
            
        if gpu_info and gpu_info.get("support_flash_attn"):
            config["attn_implementation"] = "flash_attention_2"
            optimization_notes.append("⚡ 开启 FlashAttention-2 硬件加速。")

        return config, optimization_notes
            
    def get_current_config(self) -> Dict:
        """获取当前生效的配置"""
        return {
            "batch_size": self.current_batch_size,
            "max_seq_length": self.current_max_seq_length,
            "gradient_accumulation_steps": self.base.gradient_accumulation_steps,
            "learning_rate": self.base.learning_rate,
            "lora_r": self.base.lora_r,
            "lora_alpha": self.base.lora_alpha,
            "epochs": self.base.epochs
        }


class SmartTrainer:
    """智能训练器 - 集成硬件分析、资源管理和自适应训练"""
    
    def __init__(self, auto_mode: bool = True):
        self.auto_mode = auto_mode
        self.analyzer = HardwareAnalyzer()
        self.resource_manager: Optional[SmartResourceManager] = None
        self.adaptive_config: Optional[AdaptiveTrainingConfig] = None
        self.training_callbacks: list = []
        
    def analyze_and_recommend(self) -> Dict:
        """分析硬件并生成智能推荐"""
        print("\n" + "="*70)
        print("🔬 智能训练环境分析中...")
        print("="*70)
        
        # 获取硬件报告
        self.analyzer.print_hardware_report()
        
        # 获取推荐模式
        recommended_key = self.analyzer.get_recommended_mode()
        recommended_mode = self.analyzer.modes[recommended_key]
        
        # 生成智能推荐报告
        score = self.analyzer._calculate_hardware_score()
        
        print("\n" + "="*70)
        print("🧠 AI训练智能推荐报告")
        print("="*70)
        
        # 硬件适配分析
        print(f"\n📊 硬件适配分析:")
        print(f"   综合评分: {score}/100")
        
        if self.analyzer.info.has_gpu:
            gpu_vram = self.analyzer.info.gpu_vram_gb
            if gpu_vram >= 24:
                print(f"   GPU能力: 🌟 顶级 (可支持全量微调)")
            elif gpu_vram >= 12:
                print(f"   GPU能力: ✨ 优秀 (推荐QLoRA微调)")
            elif gpu_vram >= 6:
                print(f"   GPU能力: ⚡ 良好 (支持4-bit量化训练)")
            else:
                print(f"   GPU能力: 💡 基础 (建议CPU训练或更低配置)")
        else:
            cpu_count = self.analyzer.info.cpu_count
            if cpu_count >= 16:
                print(f"   CPU能力: ⚡ 良好 (多核CPU可胜任训练)")
            elif cpu_count >= 8:
                print(f"   CPU能力: 💡 基础 (训练速度较慢但可行)")
            else:
                print(f"   CPU能力: ⚠️ 有限 (建议使用云端GPU)")
                
        # 内存分析
        total_ram = self.analyzer.info.total_ram_gb
        if total_ram >= 64:
            print(f"   内存容量: 🌟 充足 (可加载大模型)")
        elif total_ram >= 32:
            print(f"   内存容量: ✨ 良好 (适合大多数训练任务)")
        elif total_ram >= 16:
            print(f"   内存容量: ⚡ 标准 (建议降低序列长度)")
        else:
            print(f"   内存容量: ⚠️ 紧张 (需启用量化)")
            
        # 推荐配置详情
        print(f"\n🎯 推荐训练配置:")
        print(f"   模式: {recommended_mode.mode_name}")
        print(f"   设备: {'GPU' if recommended_mode.device == 'cuda' else 'CPU'}")
        print(f"   量化: {recommended_mode.quantization or '无'}")
        print(f"   预估时间: {recommended_mode.estimated_time_per_epoch}/epoch")
        print(f"   预估显存: {recommended_mode.estimated_vram_gb:.1f} GB")
        
        # 自动优化建议
        print(f"\n💡 智能优化建议:")
        if not self.analyzer.info.has_gpu and total_ram >= 32:
            print(f"   • 检测到充足内存({total_ram:.1f}GB)，可尝试增大batch_size提升效率")
        if self.analyzer.info.has_gpu and gpu_vram >= 16:
            print(f"   • GPU显存充足，可尝试关闭量化以提升模型质量")
        if self.analyzer.info.cpu_count >= 16:
            print(f"   • 多核CPU({self.analyzer.info.cpu_count}核)可启用数据并行")
            
        print("="*70)
        
        return {
            "recommended_mode": recommended_key,
            "recommended_config": recommended_mode,
            "hardware_score": score,
            "auto_selected": self.auto_mode
        }
    
    def setup_training_environment(self, mode_key: Optional[str] = None) -> Dict:
        """设置训练环境 - 自动或手动选择模式"""
        recommendation = self.analyze_and_recommend()
        
        if self.auto_mode or mode_key is None:
            selected_key = recommendation["recommended_mode"]
            print(f"\n🤖 自动选择模式: {self.analyzer.modes[selected_key].mode_name}")
        else:
            selected_key = mode_key
            print(f"\n👤 手动选择模式: {self.analyzer.modes[selected_key].mode_name}")
            
        selected_mode = self.analyzer.modes[selected_key]
        
        # 创建自适应配置
        self.adaptive_config = AdaptiveTrainingConfig(selected_mode, self.analyzer.info)
        
        # 创建资源管理器
        self.resource_manager = SmartResourceManager(asdict(selected_mode))
        
        # 配置环境变量
        if selected_mode.device == 'cpu':
            os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
            import torch
            torch.set_num_threads(self.analyzer.info.cpu_count)
            print(f"✅ CPU环境配置完成 (使用 {self.analyzer.info.cpu_count} 线程)")
        else:
            print(f"✅ GPU环境配置完成")
            
        # 保存配置报告
        self._save_config_report(selected_key, selected_mode)
        
        return {
            "mode_key": selected_key,
            "config": selected_mode,
            "adaptive_config": self.adaptive_config,
            "hardware_info": self.analyzer.info
        }

    def __init__(self):
        self.info = {
            "has_gpu": torch.cuda.is_available(),
            "gpu_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
            "gpu_name": "Unknown",
            "gpu_vram_gb": 0.0,
            "compute_cap": "0.0",
            "platform": sys.platform
        }
        self._scan_hardware()

    def _scan_hardware(self):
        if self.info["has_gpu"]:
            gpu_id = torch.cuda.current_device()
            props = torch.cuda.get_device_properties(gpu_id)
            self.info["gpu_name"] = props.name
            self.info["gpu_vram_gb"] = round(props.total_memory / (1024**3), 2)
            major, minor = torch.cuda.get_device_capability(gpu_id)
            self.info["compute_cap"] = f"{major}.{minor}"
        
        mem = psutil.virtual_memory()
        self.info["ram_total_gb"] = round(mem.total / (1024**3), 2)
        self.info["cpu_count"] = psutil.cpu_count(logical=False)
    
    def _save_config_report(self, mode_key: str, config: TrainingConfig):
        """保存配置报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "auto_mode": self.auto_mode,
            "selected_mode": mode_key,
            "hardware": asdict(self.analyzer.info),
            "hardware_score": self.analyzer._calculate_hardware_score(),
            "training_config": asdict(config),
            "adaptive_enabled": True
        }
        
        with open("smart_training_config.json", 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
            
    def start_training_monitor(self):
        """启动训练监控"""
        if self.resource_manager:
            self.resource_manager.start_monitoring()
            
    def stop_training_monitor(self):
        """停止训练监控"""
        if self.resource_manager:
            self.resource_manager.stop_monitoring()
            summary = self.resource_manager.get_resource_summary()
            print(f"\n📊 资源使用摘要:")
            print(f"   峰值内存: {summary['peak_memory_gb']:.1f} GB")
            print(f"   峰值CPU: {summary['peak_cpu_percent']:.1f}%")
            print(f"   运行时间: {summary['elapsed_time_formatted']}")
            return summary
        return {}
        
    def get_training_advice(self) -> list:
        """获取训练建议"""
        advice = []
        info = self.analyzer.info
        
        if not info.has_gpu:
            advice.append("💡 CPU训练建议: 使用较小的max_seq_length(256-512)以提升速度")
            advice.append("💡 考虑使用Intel MKL或OpenBLAS加速CPU计算")
            
        if info.total_ram_gb < 16:
            advice.append("⚠️ 内存不足警告: 建议启用4-bit量化或减少batch_size")
            
        if info.has_gpu and info.gpu_vram_gb < 8:
            advice.append("💡 显存优化: 系统已自动启用 gradient_checkpointing，可节省约 30% 显存")
            advice.append("💡 显存优化: 系统已自动切换至分页优化器，防止碎片化导致 OOM")
            
        if info.has_gpu and info.gpu_vram_gb >= 16:
            advice.append("🚀 性能飞跃: 您的硬件支持 BF16 混合精度，训练速度将提升约 20%")
            
        return advice


def main():
    """演示智能训练器功能"""
    print("\n" + "🚀"*35)
    print("   Gemma 2B 智能训练环境配置系统")
    print("   (自动分析 · 智能推荐 · 无人干预)")
    print("🚀"*35)
    
    # 创建智能训练器（自动模式）
    trainer = SmartTrainer(auto_mode=True)
    
    # 设置训练环境
    env_config = trainer.setup_training_environment()
    
    # 打印训练建议
    advice = trainer.get_training_advice()
    if advice:
        print("\n📚 训练优化建议:")
        for tip in advice:
            print(f"   {tip}")
    
    print("\n✅ 智能训练环境配置完成！")
    print(f"   配置文件已保存: smart_training_config.json")
    
    return trainer, env_config


if __name__ == "__main__":
    main()
