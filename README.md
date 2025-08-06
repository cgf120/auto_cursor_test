# ComfyUI Windows to Linux Migration Tool

这是一个专门用于将ComfyUI从Windows系统迁移到Linux系统的工具。该工具会自动处理路径转换、文件权限、配置文件更新等迁移过程中的常见问题。

## 功能特性

- 🔄 **自动路径转换**: 将Windows路径格式转换为Linux路径格式
- 📁 **智能文件迁移**: 自动排除Windows特定文件，保留必要文件
- ⚙️ **配置修复**: 自动修复配置文件中的路径问题
- 🔐 **权限设置**: 自动设置Linux系统所需的文件权限
- 📊 **详细报告**: 生成完整的迁移报告和日志
- 🛡️ **安全模式**: 支持dry-run模式，预览迁移结果而不实际修改文件

## 系统要求

- Linux系统 (推荐Ubuntu 18.04+)
- Python 3.7+
- 足够的磁盘空间 (建议至少10GB可用空间)

## 安装和使用

### 1. 下载工具

```bash
# 克隆或下载迁移工具
git clone <repository-url>
cd comfyui-migration-tool
```

### 2. 运行迁移

#### 基本用法

```bash
# 迁移到默认位置 (~/ComfyUI)
python3 comfyui_migration_tool.py /path/to/windows/comfyui

# 迁移到指定位置
python3 comfyui_migration_tool.py /path/to/windows/comfyui -t /home/user/custom/comfyui

# 预览模式 (不实际迁移)
python3 comfyui_migration_tool.py /path/to/windows/comfyui --dry-run

# 详细输出
python3 comfyui_migration_tool.py /path/to/windows/comfyui -v
```

#### 参数说明

- `source_path`: Windows ComfyUI安装路径 (必需)
- `-t, --target`: Linux目标路径 (可选，默认为 ~/ComfyUI)
- `--dry-run`: 预览模式，不实际修改文件
- `-v, --verbose`: 详细输出模式

### 3. 迁移后设置

迁移完成后，按照以下步骤完成设置：

```bash
# 1. 进入目标目录
cd ~/ComfyUI

# 2. 安装系统依赖
chmod +x install_dependencies.sh
./install_dependencies.sh

# 3. 安装Python依赖
pip3 install -r requirements.txt

# 4. 运行ComfyUI
chmod +x run_linux.sh
./run_linux.sh
```

## 迁移内容

### 自动迁移的文件和目录

- ✅ **模型文件**: `models/` 目录下的所有AI模型
- ✅ **自定义节点**: `custom_nodes/` 目录
- ✅ **配置文件**: `config.json`, `user_config.json` 等
- ✅ **输出文件**: `output/` 目录
- ✅ **输入文件**: `input/` 目录
- ✅ **脚本文件**: `scripts/` 目录
- ✅ **Web界面**: `web/` 目录
- ✅ **核心代码**: Python源代码文件

### 自动排除的文件

- ❌ Windows可执行文件 (`.exe`, `.bat`, `.cmd`)
- ❌ Windows快捷方式 (`.lnk`)
- ❌ Windows系统文件 (`Thumbs.db`, `desktop.ini`)
- ❌ 临时文件 (`.tmp`, `.log`)

### 自动添加的Linux文件

- ✅ `run_linux.sh`: Linux运行脚本
- ✅ `install_dependencies.sh`: 依赖安装脚本

## 路径转换规则

工具会自动转换以下路径格式：

| Windows格式 | Linux格式 |
|------------|-----------|
| `C:\Users\...` | `/mnt/c/Users/...` |
| `D:\Models\...` | `/mnt/d/Models/...` |
| `\\server\share` | `/mnt/server/share` |
| `C:\Program Files\...` | `/mnt/c/Program Files/...` |

## 常见问题解决

### 1. 模型路径问题

如果模型文件路径不正确，手动编辑配置文件：

```bash
# 编辑配置文件
nano ~/ComfyUI/config.json

# 或使用图形编辑器
gedit ~/ComfyUI/config.json
```

### 2. 权限问题

如果遇到权限错误：

```bash
# 修复文件权限
chmod -R 755 ~/ComfyUI
chmod -R 644 ~/ComfyUI/*.py
chmod +x ~/ComfyUI/*.sh
```

### 3. 依赖问题

如果Python依赖安装失败：

```bash
# 创建虚拟环境
python3 -m venv comfyui_env
source comfyui_env/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 4. CUDA支持

如果需要CUDA支持：

```bash
# 检查NVIDIA驱动
nvidia-smi

# 安装CUDA版本的PyTorch
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## 迁移报告

迁移完成后，工具会生成详细的迁移报告，包含：

- 📊 迁移统计信息
- ⚠️ 发现的问题
- ❌ 迁移错误
- 📋 后续步骤说明

报告保存在 `~/ComfyUI/migration_report.txt`

## 日志文件

工具运行时会生成详细的日志文件：

- `comfyui_migration.log`: 详细的迁移日志
- 包含所有操作步骤和错误信息

## 高级用法

### 自定义排除模式

```python
# 在代码中自定义排除模式
exclude_patterns = [
    "*.exe", "*.bat", "*.tmp",
    "large_models/*.safetensors"  # 排除特定大文件
]
```

### 批量迁移

```bash
# 批量迁移多个ComfyUI安装
for dir in /mnt/windows/ComfyUI*; do
    python3 comfyui_migration_tool.py "$dir" -t "/home/user/$(basename $dir)"
done
```

## 故障排除

### 迁移失败

1. 检查源路径是否存在
2. 确保有足够的磁盘空间
3. 检查文件权限
4. 查看详细日志文件

### 运行失败

1. 检查Python版本 (需要3.7+)
2. 安装缺失的依赖
3. 检查CUDA驱动 (如果使用GPU)
4. 查看ComfyUI错误日志

## 贡献

欢迎提交Issue和Pull Request来改进这个工具。

## 许可证

MIT License

## 支持

如果遇到问题，请：

1. 查看本文档的故障排除部分
2. 检查迁移日志文件
3. 提交Issue并提供详细信息