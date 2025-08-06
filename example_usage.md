# ComfyUI迁移工具使用示例

## 快速开始

### 1. 安装工具

```bash
# 运行安装脚本
./install.sh
```

### 2. 基本迁移

```bash
# 完整迁移
python3 comfyui_migrate.py /mnt/windows/comfyui /home/user/comfyui

# 或使用快速脚本
./migrate_comfyui.sh /mnt/windows/comfyui /home/user/comfyui
```

### 3. 预览迁移计划

```bash
# 查看将要执行的操作（不实际执行）
python3 comfyui_migrate.py /mnt/windows/comfyui /home/user/comfyui --dry-run
```

### 4. 估算迁移大小

```bash
# 估算需要迁移的文件大小
python3 comfyui_migrate.py /mnt/windows/comfyui /home/user/comfyui --estimate-only
```

## 分步迁移示例

### 仅迁移配置文件

```bash
python3 comfyui_config_migrator.py /mnt/windows/comfyui /home/user/comfyui
```

### 仅迁移模型文件

```bash
# 估算模型文件大小
python3 comfyui_model_migrator.py /mnt/windows/comfyui /home/user/comfyui --estimate-only

# 创建模型文件清单
python3 comfyui_model_migrator.py /mnt/windows/comfyui /home/user/comfyui --create-inventory

# 迁移模型文件（跳过验证以加快速度）
python3 comfyui_model_migrator.py /mnt/windows/comfyui /home/user/comfyui --no-verify
```

### 仅迁移主程序

```bash
python3 comfyui_migration_tool.py /mnt/windows/comfyui /home/user/comfyui
```

## 实际使用场景

### 场景1: 从Windows硬盘迁移

```bash
# 假设Windows硬盘挂载在/mnt/windows
# 目标目录为/home/user/comfyui

# 1. 检查源目录
ls -la /mnt/windows/comfyui

# 2. 估算迁移大小
python3 comfyui_migrate.py /mnt/windows/comfyui /home/user/comfyui --estimate-only

# 3. 执行完整迁移
python3 comfyui_migrate.py /mnt/windows/comfyui /home/user/comfyui

# 4. 启动ComfyUI
cd /home/user/comfyui
./start_comfyui.sh
```

### 场景2: 从网络共享迁移

```bash
# 假设网络共享挂载在/mnt/share
# 目标目录为/home/user/comfyui

# 1. 挂载网络共享
sudo mount -t cifs //server/share /mnt/share -o username=user,password=pass

# 2. 执行迁移
python3 comfyui_migrate.py /mnt/share/comfyui /home/user/comfyui

# 3. 卸载网络共享
sudo umount /mnt/share
```

### 场景3: 选择性迁移

```bash
# 跳过模型文件迁移（如果模型文件很大）
python3 comfyui_migrate.py /mnt/windows/comfyui /home/user/comfyui --skip-steps "模型文件迁移"

# 只迁移配置文件
python3 comfyui_config_migrator.py /mnt/windows/comfyui /home/user/comfyui

# 手动复制模型文件
rsync -av --progress /mnt/windows/comfyui/models/ /home/user/comfyui/models/
```

## 迁移后验证

### 1. 检查文件结构

```bash
# 检查目标目录结构
tree /home/user/comfyui -L 3

# 检查模型文件
ls -la /home/user/comfyui/models/checkpoints/
ls -la /home/user/comfyui/models/loras/
```

### 2. 检查配置文件

```bash
# 查看迁移后的配置文件
cat /home/user/comfyui/extra_model_paths.yaml

# 检查路径是否正确
grep -r "C:" /home/user/comfyui/  # 不应该有Windows路径
```

### 3. 测试启动

```bash
# 进入目标目录
cd /home/user/comfyui

# 检查启动脚本权限
ls -la start_comfyui.sh

# 启动ComfyUI
./start_comfyui.sh
```

### 4. 检查日志

```bash
# 查看启动日志
tail -f /home/user/comfyui/logs/comfyui.log

# 检查错误信息
grep -i error /home/user/comfyui/logs/comfyui.log
```

## 故障排除

### 权限问题

```bash
# 设置正确的文件权限
chmod +x /home/user/comfyui/start_comfyui.sh
chmod -R 755 /home/user/comfyui/
```

### 路径问题

```bash
# 检查配置文件中的路径
grep -r "path" /home/user/comfyui/*.yaml

# 手动修正路径
sed -i 's|/media/user/c|/home/user|g' /home/user/comfyui/extra_model_paths.yaml
```

### 依赖问题

```bash
# 重新安装依赖
cd /home/user/comfyui
source venv/bin/activate
pip install -r requirements.txt
```

### 模型加载问题

```bash
# 检查模型文件路径
python3 -c "
import yaml
with open('extra_model_paths.yaml', 'r') as f:
    config = yaml.safe_load(f)
    for key, path in config.items():
        print(f'{key}: {path}')
        if path and not path.startswith('/'):
            print(f'  WARNING: Relative path detected')
"
```

## 性能优化

### 大文件传输优化

```bash
# 使用rsync进行大文件传输
rsync -av --progress --partial /mnt/windows/comfyui/models/ /home/user/comfyui/models/

# 使用tar进行压缩传输
tar -czf comfyui_models.tar.gz -C /mnt/windows/comfyui models/
tar -xzf comfyui_models.tar.gz -C /home/user/comfyui/
```

### 并行处理

```bash
# 使用GNU parallel进行并行复制（需要安装parallel）
find /mnt/windows/comfyui/models/ -name "*.safetensors" | \
parallel -j 4 cp {} /home/user/comfyui/models/
```

## 备份和恢复

### 创建备份

```bash
# 备份原始配置
cp /mnt/windows/comfyui/extra_model_paths.yaml /mnt/windows/comfyui/extra_model_paths.yaml.backup

# 备份迁移报告
cp /home/user/comfyui/COMPLETE_MIGRATION_REPORT.md /home/user/comfyui/COMPLETE_MIGRATION_REPORT.md.backup
```

### 恢复配置

```bash
# 恢复原始配置
cp /mnt/windows/comfyui/extra_model_paths.yaml.backup /home/user/comfyui/extra_model_paths.yaml

# 重新运行配置迁移
python3 comfyui_config_migrator.py /mnt/windows/comfyui /home/user/comfyui
```