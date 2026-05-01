import os
import sys
import json
import platform
import subprocess
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class HardwareInfo:
    """硬件信息数据类"""
    cpu_count: int
    cpu_freq_mhz: float
    total_ram_gb: float
    available_ram_gb: float
    has_gpu: bool
    gpu_name: str
    gpu_vram_gb: float
    gpu_count: int
    disk_free_gb: float
    os_name: str
    python_version: str
    torch_version: str
    cuda_available: bool
    cuda_version: str

@dataclass
class TrainingConfig:
    """训练配置数据类"""
    mode_name: str
    mode_desc: str
    device: str
    batch_size: int
    gradient_accumulation_steps: int
    epochs: int
    learning_rate: float
    max_seq_length: int
    lora_r: int
    lora_alpha: int
    lora_dropout: float
    quantization: Optional[str]
    optimizer: str
    estimated_time_per_epoch: str
    estimated_vram_gb: float
    recommended_for: str

class HardwareAnalyzer:
    """硬件分析器 - 全面检测系统硬件资源"""
    
    def __init__(self):
        self.info = self._gather_hardware_info()
        self.modes = self._generate_training_modes()
        
    def _gather_hardware_info(self) -> HardwareInfo:
        """收集全面的硬件信息"""
        # CPU 信息
        cpu_count = os.cpu_count() or 1
        cpu_freq = 0.0
        try:
            import psutil
            cpu_freq = psutil.cpu_freq().max if psutil.cpu_freq() else 0
            mem = psutil.virtual_memory()
            total_ram = mem.total / (1024**3)
            available_ram = mem.available / (1024**3)
            disk = psutil.disk_usage('.')
            disk_free = disk.free / (1024**3)
        except ImportError:
            total_ram = 0
            available_ram = 0
            disk_free = 0
            
        # GPU 信息
        has_gpu = False
        gpu_name = "无"
        gpu_vram = 0.0
        gpu_count = 0
        cuda_available = False
        cuda_version = "N/A"
        
        try:
            import torch
            cuda_available = torch.cuda.is_available()
            if cuda_available:
                has_gpu = True
                gpu_count = torch.cuda.device_count()
                gpu_name = torch.cuda.get_device_name(0)
                gpu_vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                cuda_version = torch.version.cuda or "未知"
        except ImportError:
            pass
            
        # 系统信息
        os_name = f"{platform.system()} {platform.release()}"
        python_ver = sys.version.split()[0]
        
        torch_ver = "未安装"
        try:
            import torch
            torch_ver = torch.__version__
        except ImportError:
            pass
            
        return HardwareInfo(
            cpu_count=cpu_count,
            cpu_freq_mhz=cpu_freq,
            total_ram_gb=total_ram,
            available_ram_gb=available_ram,
            has_gpu=has_gpu,
            gpu_name=gpu_name,
            gpu_vram_gb=gpu_vram,
            gpu_count=gpu_count,
            disk_free_gb=disk_free,
            os_name=os_name,
            python_version=python_ver,
            torch_version=torch_ver,
            cuda_available=cuda_available,
            cuda_version=cuda_version
        )
    
    def _generate_training_modes(self) -> Dict[str, TrainingConfig]:
        """基于硬件生成五种训练模式配置"""
        info = self.info
        modes = {}
        
        # 计算硬件评分 (0-100)
        hardware_score = self._calculate_hardware_score()
        
        # 1. 穷人模式 (最小资源)
        modes["poor"] = TrainingConfig(
            mode_name="💰 穷人模式 (Minimal)",
            mode_desc="最低资源占用，可在老旧设备上运行，速度最慢但最稳定",
            device="cpu",
            batch_size=1,
            gradient_accumulation_steps=16,
            epochs=1,
            learning_rate=1e-4,
            max_seq_length=256,
            lora_r=4,
            lora_alpha=8,
            lora_dropout=0.1,
            quantization=None,
            optimizer="adamw_torch",
            estimated_time_per_epoch="4-8小时",
            estimated_vram_gb=0,
            recommended_for="CPU < 4核, 内存 < 8GB, 无GPU"
        )
        
        # 2. 常态模式 (推荐)
        if info.has_gpu and info.gpu_vram_gb >= 6:
            # 有中等GPU
            modes["normal"] = TrainingConfig(
                mode_name="⚖️ 常态模式 (Recommended)",
                mode_desc="平衡性能与资源，适合大多数用户",
                device="cuda",
                batch_size=2,
                gradient_accumulation_steps=4,
                epochs=3,
                learning_rate=2e-4,
                max_seq_length=512,
                lora_r=8,
                lora_alpha=16,
                lora_dropout=0.05,
                quantization="4bit",
                optimizer="paged_adamw_8bit",
                estimated_time_per_epoch="20-40分钟",
                estimated_vram_gb=4.5,
                recommended_for="GPU 6-12GB VRAM, 内存 >= 16GB"
            )
        elif info.has_gpu and info.gpu_vram_gb >= 4:
            modes["normal"] = TrainingConfig(
                mode_name="⚖️ 常态模式 (Recommended)",
                mode_desc="平衡性能与资源，适合大多数用户",
                device="cuda",
                batch_size=1,
                gradient_accumulation_steps=8,
                epochs=3,
                learning_rate=2e-4,
                max_seq_length=512,
                lora_r=8,
                lora_alpha=16,
                lora_dropout=0.05,
                quantization="4bit",
                optimizer="paged_adamw_8bit",
                estimated_time_per_epoch="30-60分钟",
                estimated_vram_gb=3.5,
                recommended_for="GPU 4-6GB VRAM, 内存 >= 16GB"
            )
        else:
            # CPU模式
            modes["normal"] = TrainingConfig(
                mode_name="⚖️ 常态模式 (Recommended)",
                mode_desc="平衡性能与资源，适合大多数用户",
                device="cpu",
                batch_size=1,
                gradient_accumulation_steps=8,
                epochs=3,
                learning_rate=2e-4,
                max_seq_length=512,
                lora_r=8,
                lora_alpha=16,
                lora_dropout=0.05,
                quantization=None,
                optimizer="adamw_torch",
                estimated_time_per_epoch="1-2小时",
                estimated_vram_gb=0,
                recommended_for="CPU >= 4核, 内存 >= 16GB, 无GPU或GPU显存 < 4GB"
            )
        
        # 3. 富人模式 (优选)
        if info.has_gpu and info.gpu_vram_gb >= 12:
            modes["rich"] = TrainingConfig(
                mode_name="💎 富人模式 (Premium)",
                mode_desc="更高质量训练，适合追求更好效果的用户",
                device="cuda",
                batch_size=4,
                gradient_accumulation_steps=2,
                epochs=5,
                learning_rate=2e-4,
                max_seq_length=1024,
                lora_r=16,
                lora_alpha=32,
                lora_dropout=0.05,
                quantization="4bit",
                optimizer="paged_adamw_8bit",
                estimated_time_per_epoch="15-30分钟",
                estimated_vram_gb=8.0,
                recommended_for="GPU >= 12GB VRAM, 内存 >= 32GB"
            )
        elif info.has_gpu and info.gpu_vram_gb >= 8:
            modes["rich"] = TrainingConfig(
                mode_name="💎 富人模式 (Premium)",
                mode_desc="更高质量训练，适合追求更好效果的用户",
                device="cuda",
                batch_size=2,
                gradient_accumulation_steps=4,
                epochs=5,
                learning_rate=2e-4,
                max_seq_length=1024,
                lora_r=16,
                lora_alpha=32,
                lora_dropout=0.05,
                quantization="4bit",
                optimizer="paged_adamw_8bit",
                estimated_time_per_epoch="20-40分钟",
                estimated_vram_gb=6.0,
                recommended_for="GPU 8-12GB VRAM, 内存 >= 32GB"
            )
        else:
            modes["rich"] = TrainingConfig(
                mode_name="💎 富人模式 (Premium)",
                mode_desc="更高质量训练，适合追求更好效果的用户",
                device="cpu",
                batch_size=2,
                gradient_accumulation_steps=4,
                epochs=5,
                learning_rate=2e-4,
                max_seq_length=1024,
                lora_r=16,
                lora_alpha=32,
                lora_dropout=0.05,
                quantization=None,
                optimizer="adamw_torch",
                estimated_time_per_epoch="2-4小时",
                estimated_vram_gb=0,
                recommended_for="CPU >= 8核, 内存 >= 32GB"
            )
        
        # 4. 土豪模式 (最大)
        if info.has_gpu and info.gpu_vram_gb >= 24:
            modes["tycoon"] = TrainingConfig(
                mode_name="👑 土豪模式 (Tycoon)",
                mode_desc="极致性能，最快训练速度，适合高端设备",
                device="cuda",
                batch_size=8,
                gradient_accumulation_steps=1,
                epochs=10,
                learning_rate=3e-4,
                max_seq_length=2048,
                lora_r=32,
                lora_alpha=64,
                lora_dropout=0.03,
                quantization="8bit",
                optimizer="adamw_torch",
                estimated_time_per_epoch="5-10分钟",
                estimated_vram_gb=20.0,
                recommended_for="GPU >= 24GB VRAM (RTX 3090/4090/A100), 内存 >= 64GB"
            )
        elif info.has_gpu and info.gpu_vram_gb >= 16:
            modes["tycoon"] = TrainingConfig(
                mode_name="👑 土豪模式 (Tycoon)",
                mode_desc="极致性能，最快训练速度，适合高端设备",
                device="cuda",
                batch_size=4,
                gradient_accumulation_steps=2,
                epochs=10,
                learning_rate=3e-4,
                max_seq_length=2048,
                lora_r=32,
                lora_alpha=64,
                lora_dropout=0.03,
                quantization="8bit",
                optimizer="adamw_torch",
                estimated_time_per_epoch="10-20分钟",
                estimated_vram_gb=14.0,
                recommended_for="GPU >= 16GB VRAM (RTX 4080/A4000), 内存 >= 64GB"
            )
        else:
            modes["tycoon"] = TrainingConfig(
                mode_name="👑 土豪模式 (Tycoon)",
                mode_desc="极致性能，最快训练速度，适合高端设备",
                device="cpu",
                batch_size=4,
                gradient_accumulation_steps=2,
                epochs=10,
                learning_rate=3e-4,
                max_seq_length=2048,
                lora_r=32,
                lora_alpha=64,
                lora_dropout=0.03,
                quantization=None,
                optimizer="adamw_torch",
                estimated_time_per_epoch="4-8小时",
                estimated_vram_gb=0,
                recommended_for="CPU >= 16核, 内存 >= 64GB (服务器级)"
            )
        
        # 5. 最大模式 (极限)
        if info.has_gpu and info.gpu_vram_gb >= 40:
            modes["max"] = TrainingConfig(
                mode_name="🚀 最大模式 (Maximum)",
                mode_desc="极限配置，榨干所有硬件资源，适合专业训练",
                device="cuda",
                batch_size=16,
                gradient_accumulation_steps=1,
                epochs=20,
                learning_rate=5e-4,
                max_seq_length=4096,
                lora_r=64,
                lora_alpha=128,
                lora_dropout=0.01,
                quantization=None,
                optimizer="adamw_torch",
                estimated_time_per_epoch="2-5分钟",
                estimated_vram_gb=35.0,
                recommended_for="多卡 A100/H100 或 RTX 4090 24GB x2, 内存 >= 128GB"
            )
        elif info.has_gpu and info.gpu_vram_gb >= 24:
            modes["max"] = TrainingConfig(
                mode_name="🚀 最大模式 (Maximum)",
                mode_desc="极限配置，榨干所有硬件资源，适合专业训练",
                device="cuda",
                batch_size=8,
                gradient_accumulation_steps=1,
                epochs=20,
                learning_rate=5e-4,
                max_seq_length=4096,
                lora_r=64,
                lora_alpha=128,
                lora_dropout=0.01,
                quantization=None,
                optimizer="adamw_torch",
                estimated_time_per_epoch="5-10分钟",
                estimated_vram_gb=22.0,
                recommended_for="RTX 3090/4090 24GB, 内存 >= 128GB"
            )
        else:
            modes["max"] = TrainingConfig(
                mode_name="🚀 最大模式 (Maximum)",
                mode_desc="极限配置，榨干所有硬件资源，适合专业训练",
                device="cpu",
                batch_size=8,
                gradient_accumulation_steps=1,
                epochs=20,
                learning_rate=5e-4,
                max_seq_length=4096,
                lora_r=64,
                lora_alpha=128,
                lora_dropout=0.01,
                quantization=None,
                optimizer="adamw_torch",
                estimated_time_per_epoch="8-16小时",
                estimated_vram_gb=0,
                recommended_for="服务器级 CPU (32+核), 内存 >= 128GB"
            )
            
        return modes
    
    def _calculate_hardware_score(self) -> int:
        """计算硬件综合评分 (0-100)"""
        score = 0
        info = self.info
        
        # CPU评分 (最高30分)
        if info.cpu_count >= 32:
            score += 30
        elif info.cpu_count >= 16:
            score += 25
        elif info.cpu_count >= 8:
            score += 20
        elif info.cpu_count >= 4:
            score += 15
        else:
            score += 10
            
        # 内存评分 (最高25分)
        if info.total_ram_gb >= 128:
            score += 25
        elif info.total_ram_gb >= 64:
            score += 20
        elif info.total_ram_gb >= 32:
            score += 15
        elif info.total_ram_gb >= 16:
            score += 10
        else:
            score += 5
            
        # GPU评分 (最高45分)
        if info.has_gpu:
            if info.gpu_vram_gb >= 40:
                score += 45
            elif info.gpu_vram_gb >= 24:
                score += 40
            elif info.gpu_vram_gb >= 16:
                score += 35
            elif info.gpu_vram_gb >= 12:
                score += 30
            elif info.gpu_vram_gb >= 8:
                score += 25
            elif info.gpu_vram_gb >= 6:
                score += 20
            elif info.gpu_vram_gb >= 4:
                score += 15
            else:
                score += 10
        else:
            score += 0
            
        return min(score, 100)
    
    def get_recommended_mode(self) -> str:
        """根据硬件评分推荐最佳模式"""
        score = self._calculate_hardware_score()
        if score >= 80:
            return "tycoon"
        elif score >= 60:
            return "rich"
        elif score >= 40:
            return "normal"
        elif score >= 20:
            return "poor"
        else:
            return "poor"
    
    def print_hardware_report(self):
        """打印硬件检测报告"""
        info = self.info
        score = self._calculate_hardware_score()
        
        print("\n" + "="*70)
        print("🔍 系统硬件全面检测报告")
        print("="*70)
        print(f"📅 检测时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"💻 操作系统: {info.os_name}")
        print(f"🐍 Python版本: {info.python_version}")
        print(f"🔥 PyTorch版本: {info.torch_version}")
        print("-"*70)
        
        print("\n📊 CPU 信息:")
        print(f"   • 核心数: {info.cpu_count} 核")
        if info.cpu_freq_mhz > 0:
            print(f"   • 频率: {info.cpu_freq_mhz:.0f} MHz")
        
        print("\n🧠 内存 信息:")
        print(f"   • 总内存: {info.total_ram_gb:.1f} GB")
        print(f"   • 可用内存: {info.available_ram_gb:.1f} GB")
        
        print("\n🎮 GPU 信息:")
        if info.has_gpu:
            print(f"   • CUDA可用: ✅")
            print(f"   • CUDA版本: {info.cuda_version}")
            print(f"   • GPU数量: {info.gpu_count}")
            print(f"   • GPU型号: {info.gpu_name}")
            print(f"   • 显存大小: {info.gpu_vram_gb:.1f} GB")
        else:
            print(f"   • CUDA可用: ❌")
            print(f"   • 状态: 未检测到 NVIDIA GPU")
        
        print("\n💾 磁盘 信息:")
        print(f"   • 可用空间: {info.disk_free_gb:.1f} GB")
        
        print("\n📈 硬件综合评分: ", end="")
        if score >= 80:
            print(f"🌟 {score}/100 (顶级配置)")
        elif score >= 60:
            print(f"✨ {score}/100 (优秀配置)")
        elif score >= 40:
            print(f"⚡ {score}/100 (良好配置)")
        elif score >= 20:
            print(f"💡 {score}/100 (基础配置)")
        else:
            print(f"⚠️ {score}/100 (入门配置)")
        
        print("="*70)
    
    def print_training_modes(self):
        """打印所有训练模式详情"""
        print("\n" + "="*70)
        print("🎯 可用训练模式配置")
        print("="*70)
        
        for key, mode in self.modes.items():
            print(f"\n{mode.mode_name}")
            print(f"   描述: {mode.mode_desc}")
            print(f"   设备: {'🎮 GPU' if mode.device == 'cuda' else '🖥️ CPU'}")
            print(f"   Batch Size: {mode.batch_size}")
            print(f"   梯度累积: {mode.gradient_accumulation_steps}")
            print(f"   训练轮数: {mode.epochs}")
            print(f"   序列长度: {mode.max_seq_length}")
            print(f"   LoRA秩: r={mode.lora_r}, alpha={mode.lora_alpha}")
            print(f"   量化: {mode.quantization or '无'}")
            print(f"   优化器: {mode.optimizer}")
            print(f"   预估每轮时间: {mode.estimated_time_per_epoch}")
            print(f"   预估显存占用: {mode.estimated_vram_gb:.1f} GB")
            print(f"   适用场景: {mode.recommended_for}")
            print("-"*70)
    
    def generate_full_report(self, output_file: str = "hardware_report.json"):
        """生成完整报告并保存到文件"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "hardware": asdict(self.info),
            "hardware_score": self._calculate_hardware_score(),
            "recommended_mode": self.get_recommended_mode(),
            "modes": {k: asdict(v) for k, v in self.modes.items()}
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 完整报告已保存至: {output_file}")
        return report


def main():
    """主函数 - 演示硬件分析器功能"""
    print("\n" + "🚀"*35)
    print("   Gemma 2B 智能硬件分析与训练模式推荐系统")
    print("🚀"*35)
    
    analyzer = HardwareAnalyzer()
    
    # 打印硬件报告
    analyzer.print_hardware_report()
    
    # 打印训练模式
    analyzer.print_training_modes()
    
    # 推荐模式
    recommended = analyzer.get_recommended_mode()
    mode = analyzer.modes[recommended]
    
    print("\n" + "="*70)
    print(f"🎯 推荐训练模式: {mode.mode_name}")
    print(f"   原因: {mode.mode_desc}")
    print(f"   预计每轮训练时间: {mode.estimated_time_per_epoch}")
    print("="*70)
    
    # 生成JSON报告
    report = analyzer.generate_full_report()
    
    return analyzer, report


if __name__ == "__main__":
    main()
