#!/bin/bash
# 智核万炼 NexaForge AI - Linux/Mac 启动脚本

# 设置UTF-8编码
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                                                                      ║"
echo "║              智核万炼® NexaForge AI 智能训练平台                      ║"
echo "║                                                                      ║"
echo "║                    开箱即用，智核万炼                                 ║"
echo "║                                                                      ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# 检查Python环境
echo "🔍 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 未检测到Python3，请先安装Python 3.8+"
    exit 1
fi

echo "✅ Python环境正常"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "🔄 创建虚拟环境..."
    python3 -m venv venv
fi

echo "🔄 激活虚拟环境..."
source venv/bin/activate

# 运行智核万炼
echo ""
echo "🚀 启动智核万炼 AI训练平台..."
echo ""

python3 nexaforge.py --auto

echo ""
read -p "按回车键退出..."
