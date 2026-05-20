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

## 📋 项目简介

智核万炼® NexaForge AI 是一个专为从普通到专业企业级用户设计的AI模型微调训练平台。通过智能硬件检测和自适应配置，让每个人都能轻松完成AI训练，无需专业技术背景。

### ✨ 核心特性

- 🤖 **智能硬件检测** - 全自动检测CPU、内存、GPU等硬件资源
- 🎯 **智能训练推荐** - 根据硬件配置自动推荐最佳训练模式
- ⚡ **实时资源监控** - Web界面实时监控训练时的资源使用情况
- 🚀 **五种训练模式** - 从入门到顶级配置全覆盖
- 📊 **完整训练报告** - 自动生成详细的训练和硬件评估报告
- 🎨 **友好用户界面** - 美观的Web监控界面和CLI操作体验
- 🔌 **一键启动** - 真正的开箱即用，零配置开始训练
- 🏭 **工业级健壮性** - 企业级监控、弹性机制和自动化测试

---

## 🛠️ 环境要求与安装

### 系统要求

| 组件 | 最低要求 | 推荐配置 |
|------|---------|---------|
| **操作系统** | Windows 10+ / Linux / macOS | Windows 11 / Ubuntu 22.04+ |
| **Python** | 3.8+ | 3.10+ |
| **内存** | 8 GB | 32 GB+ |
| **存储** | 20 GB 可用空间 | 100 GB+ SSD |
| **GPU** | 可选 | NVIDIA GPU 8 GB+ |

### 依赖安装

#### 方式一：使用 pip 安装核心依赖

```bash
# 核心依赖
pip install fastapi uvicorn psutil pydantic pydantic-settings
pip install cachetools tenacity python-dotenv websockets
pip install prometheus-fastapi-instrumentator

# GPU 支持（推荐）
pip install nvidia-ml-py3 py3nvml

# AI 框架（推荐）
pip install torch torchaudio torchvision

# Windows 特定依赖
pip install pywin32 wmi pythonnet

# 前端依赖
cd frontend
npm install
```

#### 方式二：使用 requirements.txt

```bash
# 创建 requirements.txt（项目已包含）
pip install -r requirements.txt
```

#### 方式三：使用 pyproject.toml（推荐）

```bash
# 安装项目（开发模式）
pip install -e .

# 或使用 pip-tools
pip-compile pyproject.toml
pip install -r requirements.txt
```

### 完整依赖列表

```toml
# 核心依赖
fastapi>=0.100.0
uvicorn>=0.23.0
psutil>=5.9.0
pydantic>=2.0.0
pydantic-settings>=2.0.0

# 监控和弹性
cachetools>=5.3.0
tenacity>=8.0.0
python-dotenv>=1.0.0
prometheus-fastapi-instrumentator>=7.0.0
websockets>=13.1

# GPU 支持
nvidia-ml-py3>=7.352.0
py3nvml>=0.2.7

# AI 框架
torch>=2.0.0
torchaudio>=2.0.0
torchvision>=0.15.0

# Windows 特定
pywin32>=306
wmi>=1.5.1
pythonnet>=3.0.5
```

### 验证安装

```bash
# 检查 Python 版本
python --version

# 测试核心模块
python -c "from hardware import HardwareDetector; print('✅ 模块导入成功')"

# 运行单元测试
python -m pytest tests/test_hardware.py -v

# 启动服务
python hardware_server.py
```

---

## 🚀 快速开始

### 方式一：一键启动（推荐）

#### Windows 用户

```bash
# 启动训练服务
双击 start.bat

# 启动硬件监控服务
双击 start-monitor.bat
```

#### Linux/Mac 用户

```bash
# 启动训练服务
chmod +x start.sh
./start.sh
```

### 方式二：命令行启动

```bash
# 智能训练模式（全自动）
python nexaforge.py --auto

# 交互式训练模式
python nexaforge.py --interactive

# 启动硬件监控服务
python hardware_server.py
```

### 访问监控界面

启动硬件监控服务后，在浏览器中打开：

```
🌐 主界面: http://localhost:8000
📚 API文档: http://localhost:8000/docs
```

---

## 📦 项目结构

```
nexaforge-ai/
├── nexaforge.py              # 智能训练主程序
├── finetune.py               # 微调训练核心
├── hardware_monitor.py       # 硬件侦测模块
├── hardware_server.py        # 硬件监控Web服务
├── smart_trainer.py          # 智能训练器
├── hardware_analyzer.py      # 硬件分析器
├── start.bat                 # Windows一键启动训练
├── start.sh                  # Linux/Mac一键启动训练
├── start-monitor.bat         # Windows一键启动监控
├── requirements.txt          # 依赖包列表
├── README.md                 # 项目文档
├── dataset.jsonl             # 示例训练数据
└── outputs/                  # 模型输出目录（自动创建）
```

---

## 🎯 五种训练模式

智核万炼提供五种智能训练模式，系统会根据您的硬件自动推荐最佳模式：

| 模式 | 名称 | 适用场景 | 预估时间/轮 |
|------|------|----------|------------|
| 💰 | 穷人模式 | CPU < 4核, 内存 < 8GB | 4-8小时 |
| ⚖️ | 常态模式 | CPU >= 4核, 内存 >= 16GB | 1-2小时 |
| 💎 | 富人模式 | CPU >= 8核, 内存 >= 32GB | 30-60分钟 |
| 👑 | 土豪模式 | GPU >= 16GB VRAM | 10-20分钟 |
| 🚀 | 最大模式 | 多卡A100/H100 | 2-5分钟 |

### 硬件评分标准

系统会根据硬件配置给出综合评分（0-100分）：

- 🌟 **顶级配置** (80-100分) - 推荐土豪/最大模式
- ✨ **优秀配置** (60-79分) - 推荐富人模式
- ⚡ **良好配置** (40-59分) - 推荐常态模式
- 💡 **基础配置** (20-39分) - 推荐穷人/常态模式
- ⚠️ **入门配置** (0-19分) - 建议升级硬件

---

## 📊 硬件监控API

### 实时监控接口

#### WebSocket 实时数据
```
ws://localhost:8000/ws
```
每秒推送一次硬件快照数据。

#### REST API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 主监控界面 |
| `/api/snapshot` | GET | 获取当前硬件快照 |
| `/api/recommendations` | GET | 获取训练推荐 |
| `/api/history` | GET | 获取历史数据 |
| `/docs` | GET | API文档 (Swagger UI) |

#### 数据格式示例

```json
{
  "snapshot": {
    "timestamp": "2024-01-01T12:00:00",
    "system": {
      "os": "Windows 11",
      "python_version": "3.10.0"
    },
    "cpu": {
      "count": 24,
      "percent": 35.5
    },
    "memory": {
      "total": 31.8,
      "percent": 45.2
    },
    "gpu": {
      "available": true,
      "devices": [
        {
          "name": "NVIDIA GeForce RTX 4090",
          "memory_total": 24.0
        }
      ]
    }
  },
  "recommendations": {
    "score": 75,
    "recommended_mode": "rich"
  }
}
```

---

## 📝 训练数据格式

使用JSONL格式，每条数据包含：

```json
{
  "instruction": "任务描述（必填）",
  "input": "输入内容（可选）",
  "output": "期望输出（必填）"
}
```

### 示例数据

```json
{
  "instruction": "介绍一下智核万炼AI平台",
  "input": "",
  "output": "智核万炼是一个开箱即用的AI模型微调训练平台，让每个人都能轻松训练自己的AI模型。"
}

{
  "instruction": "翻译成英文",
  "input": "今天天气真好",
  "output": "The weather is so nice today."
}
```

---

## 🔧 安装说明

### 环境要求

- Python 3.8 或更高版本
- 8GB+ 内存（推荐16GB+）
- 10GB+ 可用磁盘空间
- （可选）NVIDIA GPU + CUDA

### 依赖安装

```bash
# 基础依赖
pip install -r requirements.txt

# AI 框架（CPU版本）
pip install torch torchaudio torchvision

# AI 框架（CUDA版本，推荐有NVIDIA GPU的用户）
pip install torch torchaudio torchvision --index-url https://download.pytorch.org/whl/cu126
```

---

## 🎨 界面预览

### 硬件监控界面

- 实时显示CPU、内存、GPU使用情况
- 硬件综合评分展示
- 智能训练模式推荐
- 美观的进度条和可视化

### CLI 交互界面

- 彩色输出，友好提示
- 进度可视化
- 错误处理和恢复

---

## 📈 训练流程

1. **硬件检测** - 自动分析系统硬件资源
2. **模式推荐** - 根据硬件推荐最佳训练配置
3. **数据加载** - 自动加载和预处理训练数据
4. **模型微调** - 使用QLoRA进行高效微调
5. **资源监控** - 实时监控训练资源使用
6. **报告生成** - 自动生成训练和硬件评估报告

---

## 🔌 开发指南

### 扩展训练模式

编辑 `hardware_monitor.py` 中的 `get_training_recommendations` 方法。

### 自定义模型

修改 `finetune.py` 中的模型加载代码。

### 添加监控指标

在 `hardware_monitor.py` 中扩展 `HardwareDetector` 类。

---

## 🤝 贡献指南

欢迎参与智核万炼的开发！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

---

## 📄 许可证

本项目基于 MIT 许可证开源 - 详见 [LICENSE](LICENSE) 文件。

---

## 📞 联系方式

- 项目主页：https://github.com/daybydaymylove2009-max/nexaforge-ai
- 问题反馈：https://github.com/daybydaymylove2009-max/nexaforge-ai/issues

---

## 🙏 致谢

感谢以下开源项目：

- [Hugging Face Transformers](https://huggingface.co/transformers/)
- [torch (PyTorch)](https://pytorch.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [PEFT](https://github.com/huggingface/peft)

---

<p align="center">
  <b>智核万炼® NexaForge AI</b><br>
  让AI训练变得简单，人人都能训练自己的AI模型！
</p>
