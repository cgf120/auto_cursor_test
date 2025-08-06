#!/usr/bin/env python3
"""
ComfyUI Windows to Linux Migration Tool
=======================================

This tool helps migrate ComfyUI installations from Windows to Linux,
handling path conversions, file permissions, and configuration updates.
"""

import os
import sys
import json
import shutil
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re

class ComfyUIMigrationTool:
    def __init__(self, source_path: str, target_path: str):
        self.source_path = Path(source_path)
        self.target_path = Path(target_path)
        self.config_files = [
            "extra_model_paths.yaml",
            "extra_model_paths.json",
            "config.yaml",
            "config.json"
        ]
        
    def validate_paths(self) -> bool:
        """验证源路径和目标路径"""
        if not self.source_path.exists():
            print(f"❌ 源路径不存在: {self.source_path}")
            return False
            
        if not self.target_path.exists():
            print(f"📁 创建目标目录: {self.target_path}")
            self.target_path.mkdir(parents=True, exist_ok=True)
            
        return True
    
    def convert_windows_path_to_linux(self, path: str) -> str:
        """将Windows路径转换为Linux路径"""
        # 替换反斜杠为正斜杠
        path = path.replace('\\', '/')
        
        # 处理驱动器盘符
        if re.match(r'^[A-Za-z]:', path):
            # 移除驱动器盘符，假设挂载在/media/username/drive
            path = path[2:]  # 移除 "C:"
            path = f"/media/user/{path.lower()[0]}{path[1:]}"
        
        # 处理相对路径
        if path.startswith('./'):
            path = path[2:]
        elif path.startswith('../'):
            path = path[3:]
            
        return path
    
    def update_config_file(self, config_path: Path) -> bool:
        """更新配置文件中的路径"""
        try:
            if config_path.suffix == '.json':
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            elif config_path.suffix == '.yaml':
                import yaml
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
            else:
                return False
                
            updated = False
            
            def update_paths(obj):
                nonlocal updated
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if isinstance(value, str) and ('\\' in value or ':' in value):
                            new_path = self.convert_windows_path_to_linux(value)
                            if new_path != value:
                                obj[key] = new_path
                                updated = True
                                print(f"  📝 更新路径: {value} -> {new_path}")
                        elif isinstance(value, (dict, list)):
                            update_paths(value)
                elif isinstance(obj, list):
                    for item in obj:
                        update_paths(item)
            
            update_paths(config)
            
            if updated:
                if config_path.suffix == '.json':
                    with open(config_path, 'w', encoding='utf-8') as f:
                        json.dump(config, f, indent=2, ensure_ascii=False)
                elif config_path.suffix == '.yaml':
                    with open(config_path, 'w', encoding='utf-8') as f:
                        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
                        
            return updated
            
        except Exception as e:
            print(f"⚠️  更新配置文件失败 {config_path}: {e}")
            return False
    
    def copy_file_with_permissions(self, src: Path, dst: Path) -> bool:
        """复制文件并设置正确的权限"""
        try:
            # 复制文件
            shutil.copy2(src, dst)
            
            # 设置可执行权限（如果是脚本文件）
            if dst.suffix in ['.py', '.sh', '.bash']:
                dst.chmod(0o755)
            else:
                dst.chmod(0o644)
                
            return True
        except Exception as e:
            print(f"❌ 复制文件失败 {src} -> {dst}: {e}")
            return False
    
    def copy_directory(self, src: Path, dst: Path, exclude_dirs: List[str] = None) -> int:
        """复制目录，排除指定目录"""
        if exclude_dirs is None:
            exclude_dirs = ['__pycache__', '.git', 'node_modules', 'venv', 'env']
            
        copied_files = 0
        
        try:
            if not dst.exists():
                dst.mkdir(parents=True, exist_ok=True)
                
            for item in src.iterdir():
                if item.name in exclude_dirs:
                    continue
                    
                target = dst / item.name
                
                if item.is_file():
                    if self.copy_file_with_permissions(item, target):
                        copied_files += 1
                elif item.is_dir():
                    copied_files += self.copy_directory(item, target, exclude_dirs)
                    
        except Exception as e:
            print(f"❌ 复制目录失败 {src} -> {dst}: {e}")
            
        return copied_files
    
    def setup_python_environment(self) -> bool:
        """设置Python环境"""
        try:
            print("🐍 设置Python环境...")
            
            # 检查Python版本
            result = subprocess.run(['python3', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ Python3未安装")
                return False
                
            print(f"✅ Python版本: {result.stdout.strip()}")
            
            # 创建虚拟环境
            venv_path = self.target_path / "venv"
            if not venv_path.exists():
                print("📦 创建虚拟环境...")
                subprocess.run(['python3', '-m', 'venv', str(venv_path)], 
                             check=True)
            
            # 激活虚拟环境并安装依赖
            pip_path = venv_path / "bin" / "pip"
            if pip_path.exists():
                print("📦 安装ComfyUI依赖...")
                requirements_file = self.target_path / "requirements.txt"
                if requirements_file.exists():
                    subprocess.run([str(pip_path), 'install', '-r', str(requirements_file)], 
                                 check=True)
                else:
                    # 安装基本依赖
                    basic_deps = [
                        'torch', 'torchvision', 'torchaudio',
                        'transformers', 'diffusers', 'accelerate',
                        'safetensors', 'opencv-python', 'pillow',
                        'numpy', 'scipy', 'matplotlib'
                    ]
                    subprocess.run([str(pip_path), 'install'] + basic_deps, 
                                 check=True)
                                 
            return True
            
        except Exception as e:
            print(f"❌ 设置Python环境失败: {e}")
            return False
    
    def setup_custom_nodes(self) -> bool:
        """设置自定义节点"""
        try:
            custom_nodes_dir = self.target_path / "custom_nodes"
            if not custom_nodes_dir.exists():
                return True
                
            print("🔧 设置自定义节点...")
            
            # 查找并安装自定义节点的依赖
            for node_dir in custom_nodes_dir.iterdir():
                if node_dir.is_dir():
                    requirements_file = node_dir / "requirements.txt"
                    if requirements_file.exists():
                        print(f"📦 安装 {node_dir.name} 的依赖...")
                        pip_path = self.target_path / "venv" / "bin" / "pip"
                        subprocess.run([str(pip_path), 'install', '-r', str(requirements_file)], 
                                     check=True)
                                     
            return True
            
        except Exception as e:
            print(f"⚠️  设置自定义节点失败: {e}")
            return False
    
    def create_launch_script(self) -> bool:
        """创建启动脚本"""
        try:
            script_content = f"""#!/bin/bash
# ComfyUI启动脚本

cd "{self.target_path}"

# 激活虚拟环境
source venv/bin/activate

# 启动ComfyUI
python main.py --listen 0.0.0.0 --port 8188
"""
            
            script_path = self.target_path / "start_comfyui.sh"
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
                
            # 设置可执行权限
            script_path.chmod(0o755)
            
            print(f"✅ 创建启动脚本: {script_path}")
            return True
            
        except Exception as e:
            print(f"❌ 创建启动脚本失败: {e}")
            return False
    
    def create_migration_report(self, stats: Dict) -> bool:
        """创建迁移报告"""
        try:
            report_content = f"""# ComfyUI迁移报告

## 迁移统计
- 复制的文件数量: {stats.get('copied_files', 0)}
- 更新的配置文件: {stats.get('updated_configs', 0)}
- 迁移时间: {stats.get('migration_time', 'N/A')}

## 迁移的目录
- 源路径: {self.source_path}
- 目标路径: {self.target_path}

## 注意事项
1. 请检查模型文件路径是否正确
2. 确保所有依赖都已正确安装
3. 检查自定义节点是否正常工作
4. 验证配置文件中的路径设置

## 启动方法
```bash
cd {self.target_path}
./start_comfyui.sh
```

## 常见问题解决
1. 如果遇到权限问题，请运行: chmod +x start_comfyui.sh
2. 如果模型加载失败，请检查模型文件路径
3. 如果自定义节点不工作，请重新安装依赖
"""
            
            report_path = self.target_path / "MIGRATION_REPORT.md"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
                
            print(f"✅ 创建迁移报告: {report_path}")
            return True
            
        except Exception as e:
            print(f"❌ 创建迁移报告失败: {e}")
            return False
    
    def migrate(self) -> bool:
        """执行完整的迁移过程"""
        print("🚀 开始ComfyUI迁移...")
        print(f"📁 源路径: {self.source_path}")
        print(f"📁 目标路径: {self.target_path}")
        
        if not self.validate_paths():
            return False
            
        stats = {
            'copied_files': 0,
            'updated_configs': 0,
            'migration_time': 'N/A'
        }
        
        try:
            # 1. 复制主要文件
            print("\n📋 步骤1: 复制ComfyUI文件...")
            stats['copied_files'] = self.copy_directory(self.source_path, self.target_path)
            print(f"✅ 复制了 {stats['copied_files']} 个文件")
            
            # 2. 更新配置文件
            print("\n📋 步骤2: 更新配置文件...")
            for config_name in self.config_files:
                config_path = self.target_path / config_name
                if config_path.exists():
                    if self.update_config_file(config_path):
                        stats['updated_configs'] += 1
                        print(f"✅ 更新配置文件: {config_name}")
                    else:
                        print(f"ℹ️  配置文件无需更新: {config_name}")
            
            # 3. 设置Python环境
            print("\n📋 步骤3: 设置Python环境...")
            if not self.setup_python_environment():
                print("⚠️  Python环境设置失败，请手动安装依赖")
            
            # 4. 设置自定义节点
            print("\n📋 步骤4: 设置自定义节点...")
            self.setup_custom_nodes()
            
            # 5. 创建启动脚本
            print("\n📋 步骤5: 创建启动脚本...")
            self.create_launch_script()
            
            # 6. 创建迁移报告
            print("\n📋 步骤6: 创建迁移报告...")
            self.create_migration_report(stats)
            
            print("\n🎉 迁移完成！")
            print(f"📁 目标目录: {self.target_path}")
            print("🚀 启动命令: ./start_comfyui.sh")
            
            return True
            
        except Exception as e:
            print(f"❌ 迁移失败: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='ComfyUI Windows to Linux Migration Tool')
    parser.add_argument('source', help='Windows ComfyUI安装路径')
    parser.add_argument('target', help='Linux目标路径')
    parser.add_argument('--dry-run', action='store_true', help='仅显示将要执行的操作，不实际执行')
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("🔍 预览模式 - 不会实际执行迁移")
        tool = ComfyUIMigrationTool(args.source, args.target)
        if tool.validate_paths():
            print("✅ 路径验证通过")
            print("📋 将执行以下操作:")
            print("  1. 复制ComfyUI文件")
            print("  2. 更新配置文件中的路径")
            print("  3. 设置Python环境")
            print("  4. 配置自定义节点")
            print("  5. 创建启动脚本")
            print("  6. 生成迁移报告")
        else:
            print("❌ 路径验证失败")
        return
    
    tool = ComfyUIMigrationTool(args.source, args.target)
    success = tool.migrate()
    
    if success:
        print("\n✅ 迁移成功完成！")
        sys.exit(0)
    else:
        print("\n❌ 迁移失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()