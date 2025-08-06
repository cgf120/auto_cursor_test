# ComfyUI Windows to Linux Migration Tool

这是一个完整的ComfyUI从Windows迁移到Linux的工具套件，包含多个专门的迁移工具，能够处理ComfyUI迁移过程中的各种需求。

## 🚀 功能特性

- **完整迁移**: 支持ComfyUI主程序、配置文件、模型文件的完整迁移
- **路径转换**: 自动将Windows路径转换为Linux路径格式
- **文件验证**: 支持文件完整性验证，确保迁移的准确性
- **依赖管理**: 自动设置Python环境和安装必要的依赖包
- **自定义节点**: 支持自定义节点的迁移和配置
- **进度报告**: 提供详细的迁移进度和结果报告
- **灵活配置**: 支持选择性迁移和自定义配置

## 📁 工具组成

### 1. 主迁移工具 (`comfyui_migration_tool.py`)
- 处理ComfyUI主程序文件的迁移
- 设置Python虚拟环境
- 安装依赖包
- 创建启动脚本
- 生成迁移报告

### 2. 配置迁移工具 (`comfyui_config_migrator.py`)
- 迁移ComfyUI配置文件
- 更新路径设置
- 处理模型路径配置
- 创建配置模板

### 3. 模型迁移工具 (`comfyui_model_migrator.py`)
- 迁移模型文件（checkpoints、loras、embeddings等）
- 支持大文件传输
- 文件完整性验证
- 按类别组织模型文件

### 4. 主控制脚本 (`comfyui_migrate.py`)
- 整合所有迁移工具
- 提供统一的迁移接口
- 创建迁移计划
- 生成完整报告

## 🛠️ 安装要求

### 系统要求
- Linux系统（Ubuntu 18.04+, CentOS 7+, 或其他主流发行版）
- Python 3.7+
- 足够的磁盘空间（根据模型文件大小）

### Python依赖
```bash
pip install pyyaml pathlib
```

## 📖 使用方法

### 1. 快速开始

```bash
# 基本迁移命令
python3 comfyui_migrate.py /path/to/windows/comfyui /path/to/linux/comfyui

# 预览迁移计划（不实际执行）
python3 comfyui_migrate.py /path/to/windows/comfyui /path/to/linux/comfyui --dry-run

# 仅估算迁移大小
python3 comfyui_migrate.py /path/to/windows/comfyui /path/to/linux/comfyui --estimate-only
```

### 2. 分步迁移

#### 仅迁移配置文件
```bash
python3 comfyui_config_migrator.py /path/to/windows/comfyui /path/to/linux/comfyui
```

#### 仅迁移模型文件
```bash
# 估算模型文件大小
python3 comfyui_model_migrator.py /path/to/windows/comfyui /path/to/linux/comfyui --estimate-only

# 创建模型文件清单
python3 comfyui_model_migrator.py /path/to/windows/comfyui /path/to/linux/comfyui --create-inventory

# 迁移模型文件（跳过验证以加快速度）
python3 comfyui_model_migrator.py /path/to/windows/comfyui /path/to/linux/comfyui --no-verify
```

#### 仅迁移主程序
```bash
python3 comfyui_migration_tool.py /path/to/windows/comfyui /path/to/linux/comfyui
```

### 3. 高级用法

#### 跳过特定步骤
```bash
python3 comfyui_migrate.py /path/to/windows/comfyui /path/to/linux/comfyui --skip-steps "模型文件迁移"
```

#### 自定义迁移
```bash
# 使用dry-run模式查看将要执行的操作
python3 comfyui_migration_tool.py /path/to/windows/comfyui /path/to/linux/comfyui --dry-run
```

## 📋 迁移流程

### 1. 前置条件检查
- 验证源目录和目标目录
- 检查Python环境
- 验证必要的依赖包
- 确认迁移工具可用

### 2. 配置文件迁移
- 复制ComfyUI配置文件
- 更新路径设置（Windows → Linux）
- 处理模型路径配置
- 创建配置模板

### 3. 模型文件迁移
- 扫描模型文件
- 按类别组织文件
- 复制模型文件
- 验证文件完整性

### 4. 主程序迁移
- 复制ComfyUI主程序文件
- 设置Python虚拟环境
- 安装依赖包
- 创建启动脚本

## 📊 支持的模型类型

### 检查点模型 (Checkpoints)
- `.safetensors`
- `.ckpt`
- `.pt`
- `.pth`

### LoRA模型
- `.safetensors`
- `.pt`
- `.pth`

### 嵌入模型 (Embeddings)
- `.safetensors`
- `.pt`
- `.pth`
- `.bin`

### VAE模型
- `.safetensors`
- `.pt`
- `.pth`

### ControlNet模型
- `.safetensors`
- `.pt`
- `.pth`
- `.onnx`

### 其他模型类型
- 人脸识别模型
- 超分辨率模型
- CLIP模型
- 各种AI模型文件

## 🔧 配置文件处理

### 支持的配置文件
- `extra_model_paths.yaml` / `extra_model_paths.json`
- `config.yaml` / `config.json`
- `user_config.yaml` / `user_config.json`

### 路径转换规则
- Windows反斜杠 `\` → Linux正斜杠 `/`
- 驱动器盘符 `C:` → `/media/user/c`
- 相对路径处理
- 绝对路径转换

## 📝 迁移报告

迁移完成后会生成以下报告：

### 1. 完整迁移报告 (`COMPLETE_MIGRATION_REPORT.md`)
- 迁移统计信息
- 执行结果
- 下一步操作指南
- 常见问题解决方案

### 2. 模型迁移报告 (`MODEL_MIGRATION_REPORT.md`)
- 模型文件迁移统计
- 按类别分类的结果
- 失败文件列表

### 3. 配置文件报告 (`MIGRATION_REPORT.md`)
- 配置文件更新情况
- 路径转换记录
- 配置模板

## ⚠️ 注意事项

### 1. 磁盘空间
- 确保目标磁盘有足够的空间
- 模型文件通常很大（几GB到几十GB）
- 建议预留至少50%的额外空间

### 2. 网络传输
- 如果通过网络传输，确保网络稳定
- 大文件传输可能需要较长时间
- 建议使用断点续传工具

### 3. 文件权限
- 确保有足够的文件读写权限
- 迁移后检查文件权限设置
- 启动脚本需要执行权限

### 4. 路径配置
- 迁移后检查配置文件中的路径
- 确保模型文件路径正确
- 验证自定义节点路径

## 🐛 常见问题

### Q: 迁移过程中断怎么办？
A: 工具支持断点续传，重新运行命令会跳过已完成的文件。

### Q: 模型文件很大，传输很慢怎么办？
A: 可以使用 `--no-verify` 参数跳过验证，或使用外部工具如rsync进行传输。

### Q: 迁移后ComfyUI无法启动怎么办？
A: 检查Python环境、依赖包安装、文件权限等，查看迁移报告中的错误信息。

### Q: 自定义节点不工作怎么办？
A: 检查自定义节点的依赖是否已安装，可能需要手动安装特定的包。

### Q: 模型文件路径错误怎么办？
A: 检查配置文件中的路径设置，确保模型文件路径正确。

## 🔄 更新日志

### v1.0.0
- 初始版本发布
- 支持完整的ComfyUI迁移
- 包含所有主要功能

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个工具。

## 📞 支持

如果遇到问题，请：
1. 查看迁移报告中的错误信息
2. 检查常见问题部分
3. 提交Issue描述具体问题

---

**注意**: 使用此工具前请备份重要的ComfyUI配置和模型文件。