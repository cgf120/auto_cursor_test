#!/bin/bash

# ComfyUI Migration Tool Installer
# ================================

set -e

echo "🚀 ComfyUI Migration Tool 安装程序"
echo "=================================="

# 检查Python版本
echo "🔍 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装，请先安装Python3"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "✅ Python版本: $PYTHON_VERSION"

# 检查pip
echo "🔍 检查pip..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3未安装，请先安装pip3"
    exit 1
fi

echo "✅ pip3已安装"

# 安装Python依赖
echo "📦 安装Python依赖..."
pip3 install pyyaml pathlib

# 设置脚本权限
echo "🔧 设置脚本权限..."
chmod +x comfyui_migrate.py
chmod +x comfyui_migration_tool.py
chmod +x comfyui_config_migrator.py
chmod +x comfyui_model_migrator.py

echo "✅ 脚本权限设置完成"

# 创建示例配置文件
echo "📝 创建示例配置..."
cat > example_config.yaml << 'EOF'
# ComfyUI 模型路径配置示例
# 请根据实际情况修改路径

checkpoints: "/path/to/models/checkpoints"
loras: "/path/to/models/loras"
embeddings: "/path/to/models/embeddings"
vae: "/path/to/models/vae"
controlnet: "/path/to/models/controlnet"
upscale_models: "/path/to/models/upscale_models"
clip: "/path/to/models/clip"
clip_vision: "/path/to/models/clip_vision"
gligen: "/path/to/models/gligen"
unclip: "/path/to/models/unclip"
style_models: "/path/to/models/style_models"
ipadapter: "/path/to/models/ipadapter"
insightface: "/path/to/models/insightface"
ultralytics: "/path/to/models/ultralytics"
EOF

echo "✅ 示例配置文件创建完成"

# 创建快速启动脚本
echo "🚀 创建快速启动脚本..."
cat > migrate_comfyui.sh << 'EOF'
#!/bin/bash

# ComfyUI 快速迁移脚本
# 使用方法: ./migrate_comfyui.sh <源目录> <目标目录>

if [ $# -ne 2 ]; then
    echo "使用方法: $0 <源目录> <目标目录>"
    echo "示例: $0 /mnt/windows/comfyui /home/user/comfyui"
    exit 1
fi

SOURCE_DIR="$1"
TARGET_DIR="$2"

echo "🚀 开始ComfyUI迁移..."
echo "源目录: $SOURCE_DIR"
echo "目标目录: $TARGET_DIR"

# 检查源目录
if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ 源目录不存在: $SOURCE_DIR"
    exit 1
fi

# 创建目标目录
mkdir -p "$TARGET_DIR"

# 执行迁移
python3 comfyui_migrate.py "$SOURCE_DIR" "$TARGET_DIR"

echo "🎉 迁移完成！"
echo "📁 目标目录: $TARGET_DIR"
echo "🚀 启动命令: cd $TARGET_DIR && ./start_comfyui.sh"
EOF

chmod +x migrate_comfyui.sh

echo "✅ 快速启动脚本创建完成"

# 显示使用说明
echo ""
echo "🎉 安装完成！"
echo "=============="
echo ""
echo "📖 使用方法:"
echo "1. 基本迁移:"
echo "   python3 comfyui_migrate.py <源目录> <目标目录>"
echo ""
echo "2. 快速迁移:"
echo "   ./migrate_comfyui.sh <源目录> <目标目录>"
echo ""
echo "3. 预览迁移计划:"
echo "   python3 comfyui_migrate.py <源目录> <目标目录> --dry-run"
echo ""
echo "4. 估算迁移大小:"
echo "   python3 comfyui_migrate.py <源目录> <目标目录> --estimate-only"
echo ""
echo "📁 可用工具:"
echo "- comfyui_migrate.py (主控制脚本)"
echo "- comfyui_migration_tool.py (主程序迁移)"
echo "- comfyui_config_migrator.py (配置迁移)"
echo "- comfyui_model_migrator.py (模型迁移)"
echo ""
echo "📝 更多信息请查看 README.md"
echo ""