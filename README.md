# 智核万炼® NexaForge AI - 智能微调训练平台

<p align="center">
  <img src="https://img.shields.io/badge/智核万炼-NexaForge%20AI-blue?style=for-the-badge" alt="智核万炼">
  <img src="https://img.shields.io/badge/版本-v1.0.0-green?style=for-the-badge" alt="版本">
  <img src="https://img.shields.io/badge/许可证-MIT-yellow?style=for-the-badge" alt="许可证">
</p>

<p align="center">
  <b>开箱即用，智核万炼</b><br>
  <i>Out-of-the-box, Intelligent Core Refinement</i>
</p>

---

## 🎯 设计理念

**智核万炼**致力于降低AI模型训练的技术门槛，让每个人都能轻松训练和微调自己的AI模型。

### 核心特性

- 🚀 **开箱即用** - 无需复杂配置，一键启动训练
- 🤖 **智能适配** - 自动检测硬件，智能选择最优训练配置
- 🎛️ **多模式训练** - 支持5种训练模式，适配不同硬件环境
- 📊 **实时监控** - 训练过程资源监控，智能调优
- 🌐 **中文优化** - 针对中文用户优化，支持国内镜像加速

---

## 📦 快速开始

### 方式一：一键启动 (推荐)

**Windows:**
```bash
双击 start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

### 方式二：命令行启动

```bash
# 全自动模式 (推荐)
python nexaforge.py --auto

# 交互式模式
python nexaforge.py --interactive

# 指定数据集
python nexaforge.py --dataset datasets/your_data.jsonl
```

---

## 🔧 安装指南

### 环境要求

- Python 3.8+
- 内存: 8GB+ (推荐16GB+)
- 存储: 10GB+ 可用空间
- GPU: 可选 (NVIDIA GPU可加速训练)

### 手动安装

```bash
# 克隆项目
git clone https://github.com/yourusername/nexaforge-ai.git
cd nexaforge-ai

# 创建虚拟环境
python -m venv venv

# 激活环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

---

## 📊 训练模式

智核万炼提供5种智能训练模式，系统自动根据您的硬件配置推荐最优方案：

| 模式 | 名称 | 适用场景 | 预估时间 |
|------|------|----------|----------|
| 💰 | 穷人模式 | CPU < 4核, 内存 < 8GB | 4-8小时/轮 |
| ⚖️ | 常态模式 | CPU >= 4核, 内存 >= 16GB | 1-2小时/轮 |
| 💎 | 富人模式 | CPU >= 8核, 内存 >= 32GB | 30-60分钟/轮 |
| 👑 | 土豪模式 | GPU >= 16GB | 10-20分钟/轮 |
| 🚀 | 最大模式 | 多卡A100/H100 | 2-5分钟/轮 |

---

## 📁 项目结构

```
nexaforge-ai/
├── nexaforge.py          # 主入口程序
├── finetune.py           # 智能训练核心
├── hardware_analyzer.py  # 硬件分析器
├── smart_trainer.py      # 智能训练管理器
├── start.bat             # Windows启动脚本
├── start.sh              # Linux/Mac启动脚本
├── requirements.txt      # 依赖配置
├── datasets/             # 数据集目录
│   └── example.jsonl     # 示例数据
├── outputs/              # 模型输出目录
├── logs/                 # 日志目录
└── configs/              # 配置文件目录
```

---

## 📝 数据格式

训练数据使用JSONL格式，每条记录包含以下字段：

```json
{
  "instruction": "任务描述",
  "input": "输入内容 (可选)",
  "output": "期望输出"
}
```

### 示例数据

```json
{"instruction": "请介绍智核万炼AI训练平台", "input": "", "output": "智核万炼是一款开箱即用的AI模型微调训练平台..."}
{"instruction": "翻译为英文", "input": "今天天气很好", "output": "The weather is very good today."}
```

---

## 🎮 使用示例

### 示例1：全自动训练

```bash
python nexaforge.py --auto
```

系统自动检测硬件 → 选择最优配置 → 开始训练 → 保存模型

### 示例2：使用自定义数据

```bash
# 准备数据集 datasets/my_data.jsonl
python nexaforge.py --dataset datasets/my_data.jsonl --auto
```

### 示例3：交互式模式

```bash
python nexaforge.py --interactive
```

根据提示选择训练模式、配置参数。

---

## 🔬 硬件检测

智核万炼会自动检测以下硬件信息：

- **CPU**: 核心数、频率、架构
- **内存**: 总容量、可用容量
- **GPU**: 型号、显存、CUDA版本
- **磁盘**: 可用空间

并生成详细的硬件报告和训练建议。

---

## 📈 训练报告

每次训练完成后，系统会生成详细的训练报告：

```json
{
  "timestamp": "2024-01-01T12:00:00",
  "training_config": { ... },
  "hardware": { ... },
  "training_result": {
    "total_time": "1h 23m",
    "status": "success"
  },
  "resource_usage": {
    "peak_memory": "12.5GB",
    "peak_cpu": "85%"
  }
}
```

---

## 🛠️ 高级配置

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `AUTO_TRAIN` | 启用自动训练模式 | `false` |
| `DATASET_PATH` | 数据集路径 | `datasets/example.jsonl` |
| `HF_ENDPOINT` | HuggingFace镜像 | `https://hf-mirror.com` |

### 自定义训练参数

编辑 `smart_trainer.py` 中的 `TrainingConfig` 可自定义训练参数。

---

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

---

## 📄 许可证

本项目基于 MIT 许可证开源 - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

- [Hugging Face](https://huggingface.co/) - 提供优秀的Transformer库
- [PyTorch](https://pytorch.org/) - 深度学习框架
- [PEFT](https://github.com/huggingface/peft) - 参数高效微调
- [TRL](https://github.com/huggingface/trl) - Transformer强化学习

---

<p align="center">
  <b>智核万炼® NexaForge AI</b><br>
  让AI训练变得简单
</p>
