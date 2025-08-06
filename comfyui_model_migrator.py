#!/usr/bin/env python3
"""
ComfyUI Model Migration Tool
============================

专门处理ComfyUI模型文件的迁移，包括大文件传输、路径映射等。
"""

import os
import sys
import json
import shutil
import hashlib
import argparse
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
import subprocess
import time

class ComfyUIModelMigrator:
    def __init__(self, source_dir: str, target_dir: str):
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        
        # 模型文件扩展名
        self.model_extensions = {
            '.safetensors',
            '.ckpt',
            '.pt',
            '.pth',
            '.bin',
            '.onnx',
            '.tflite',
            '.pb',
            '.h5',
            '.hdf5',
            '.pkl',
            '.joblib',
            '.npy',
            '.npz',
            '.pkl',
            '.pickle',
            '.model',
            '.weights',
            '.state_dict',
            '.checkpoint',
            '.snapshot',
            '.backup',
            '.bak',
            '.tmp',
            '.temp'
        }
        
        # 模型目录结构
        self.model_dirs = {
            'checkpoints': ['*.safetensors', '*.ckpt', '*.pt', '*.pth'],
            'loras': ['*.safetensors', '*.pt', '*.pth'],
            'embeddings': ['*.safetensors', '*.pt', '*.pth', '*.bin'],
            'vae': ['*.safetensors', '*.pt', '*.pth'],
            'controlnet': ['*.safetensors', '*.pt', '*.pth', '*.onnx'],
            'upscale_models': ['*.pth', '*.pt', '*.safetensors'],
            'clip': ['*.safetensors', '*.pt', '*.pth'],
            'clip_vision': ['*.safetensors', '*.pt', '*.pth'],
            'gligen': ['*.safetensors', '*.pt', '*.pth'],
            'unclip': ['*.safetensors', '*.pt', '*.pth'],
            'style_models': ['*.safetensors', '*.pt', '*.pth'],
            'ipadapter': ['*.safetensors', '*.pt', '*.pth'],
            'insightface': ['*.onnx', '*.pth', '*.pt'],
            'ultralytics': ['*.pt', '*.pth', '*.onnx'],
            'bbox': ['*.pt', '*.pth', '*.onnx'],
            'segm': ['*.pt', '*.pth', '*.onnx'],
            'face_restoration': ['*.pth', '*.pt', '*.onnx'],
            'face_parsing': ['*.pth', '*.pt', '*.onnx'],
            'face_recognition': ['*.pth', '*.pt', '*.onnx'],
            'face_enhancement': ['*.pth', '*.pt', '*.onnx'],
            'face_swap': ['*.pth', '*.pt', '*.onnx'],
            'face_detection': ['*.pth', '*.pt', '*.onnx'],
            'face_alignment': ['*.pth', '*.pt', '*.onnx'],
            'face_landmarks': ['*.pth', '*.pt', '*.onnx'],
            'face_mesh': ['*.pth', '*.pt', '*.onnx'],
            'face_segmentation': ['*.pth', '*.pt', '*.onnx'],
            'face_3d': ['*.pth', '*.pt', '*.onnx'],
            'face_reconstruction': ['*.pth', '*.pt', '*.onnx'],
            'face_tracking': ['*.pth', '*.pt', '*.onnx'],
            'face_analysis': ['*.pth', '*.pt', '*.onnx'],
            'face_synthesis': ['*.pth', '*.pt', '*.onnx'],
            'face_manipulation': ['*.pth', '*.pt', '*.onnx'],
            'face_editing': ['*.pth', '*.pt', '*.onnx'],
            'face_generation': ['*.pth', '*.pt', '*.onnx'],
            'face_transfer': ['*.pth', '*.pt', '*.onnx'],
            'face_morphing': ['*.pth', '*.pt', '*.onnx'],
            'face_animation': ['*.pth', '*.pt', '*.onnx'],
            'face_expression': ['*.pth', '*.pt', '*.onnx'],
            'face_emotion': ['*.pth', '*.pt', '*.onnx'],
            'face_age': ['*.pth', '*.pt', '*.onnx'],
            'face_gender': ['*.pth', '*.pt', '*.onnx'],
            'face_ethnicity': ['*.pth', '*.pt', '*.onnx'],
            'face_pose': ['*.pth', '*.pt', '*.onnx'],
            'face_lighting': ['*.pth', '*.pt', '*.onnx'],
            'face_occlusion': ['*.pth', '*.pt', '*.onnx'],
            'face_quality': ['*.pth', '*.pt', '*.onnx'],
            'face_attributes': ['*.pth', '*.pt', '*.onnx'],
            'face_verification': ['*.pth', '*.pt', '*.onnx'],
            'face_identification': ['*.pth', '*.pt', '*.onnx']
        }
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """计算文件的MD5哈希值"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"⚠️  计算文件哈希失败 {file_path}: {e}")
            return ""
    
    def get_file_size(self, file_path: Path) -> int:
        """获取文件大小"""
        try:
            return file_path.stat().st_size
        except Exception:
            return 0
    
    def format_file_size(self, size_bytes: int) -> str:
        """格式化文件大小显示"""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.2f}{size_names[i]}"
    
    def find_model_files(self, directory: Path) -> List[Path]:
        """查找目录中的模型文件"""
        model_files = []
        
        try:
            for root, dirs, files in os.walk(directory):
                root_path = Path(root)
                for file in files:
                    file_path = root_path / file
                    if file_path.suffix.lower() in self.model_extensions:
                        model_files.append(file_path)
        except Exception as e:
            print(f"⚠️  查找模型文件失败 {directory}: {e}")
        
        return model_files
    
    def copy_model_file(self, src: Path, dst: Path, verify: bool = True) -> bool:
        """复制模型文件并验证"""
        try:
            # 确保目标目录存在
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            # 如果目标文件已存在，检查是否需要覆盖
            if dst.exists():
                src_size = self.get_file_size(src)
                dst_size = self.get_file_size(dst)
                
                if src_size == dst_size:
                    print(f"ℹ️  文件已存在且大小相同，跳过: {dst.name}")
                    return True
                else:
                    print(f"⚠️  文件已存在但大小不同，覆盖: {dst.name}")
            
            # 复制文件
            print(f"📋 复制文件: {src.name} ({self.format_file_size(self.get_file_size(src))})")
            shutil.copy2(src, dst)
            
            # 验证复制
            if verify:
                src_hash = self.calculate_file_hash(src)
                dst_hash = self.calculate_file_hash(dst)
                
                if src_hash and dst_hash and src_hash == dst_hash:
                    print(f"✅ 文件复制成功并验证通过: {dst.name}")
                    return True
                else:
                    print(f"❌ 文件复制验证失败: {dst.name}")
                    return False
            else:
                print(f"✅ 文件复制成功: {dst.name}")
                return True
                
        except Exception as e:
            print(f"❌ 复制文件失败 {src} -> {dst}: {e}")
            return False
    
    def create_model_inventory(self, directory: Path) -> Dict[str, Dict]:
        """创建模型文件清单"""
        inventory = {}
        
        print(f"📋 扫描模型文件: {directory}")
        model_files = self.find_model_files(directory)
        
        for file_path in model_files:
            relative_path = file_path.relative_to(directory)
            file_info = {
                'path': str(relative_path),
                'size': self.get_file_size(file_path),
                'hash': self.calculate_file_hash(file_path),
                'modified': file_path.stat().st_mtime
            }
            inventory[str(relative_path)] = file_info
        
        print(f"📊 找到 {len(model_files)} 个模型文件")
        return inventory
    
    def save_inventory(self, inventory: Dict, file_path: Path):
        """保存模型文件清单"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(inventory, f, indent=2, ensure_ascii=False)
            print(f"✅ 保存模型清单: {file_path}")
        except Exception as e:
            print(f"❌ 保存模型清单失败: {e}")
    
    def load_inventory(self, file_path: Path) -> Dict:
        """加载模型文件清单"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  加载模型清单失败: {e}")
            return {}
    
    def migrate_models_by_category(self, category: str, source_models_dir: Path, target_models_dir: Path) -> Dict[str, bool]:
        """按类别迁移模型文件"""
        results = {}
        
        source_category_dir = source_models_dir / category
        target_category_dir = target_models_dir / category
        
        if not source_category_dir.exists():
            print(f"ℹ️  源目录不存在: {source_category_dir}")
            return results
        
        print(f"\n📁 迁移 {category} 模型...")
        
        # 查找该类别下的模型文件
        model_files = []
        if category in self.model_dirs:
            extensions = self.model_dirs[category]
            for ext in extensions:
                model_files.extend(source_category_dir.glob(f"**/{ext}"))
        else:
            # 如果没有预定义扩展名，查找所有模型文件
            model_files = self.find_model_files(source_category_dir)
        
        if not model_files:
            print(f"ℹ️  未找到 {category} 模型文件")
            return results
        
        # 复制文件
        for model_file in model_files:
            relative_path = model_file.relative_to(source_category_dir)
            target_file = target_category_dir / relative_path
            
            success = self.copy_model_file(model_file, target_file)
            results[str(relative_path)] = success
        
        return results
    
    def migrate_all_models(self, verify: bool = True) -> Dict[str, Dict[str, bool]]:
        """迁移所有模型文件"""
        all_results = {}
        
        source_models_dir = self.source_dir / "models"
        target_models_dir = self.target_dir / "models"
        
        if not source_models_dir.exists():
            print(f"❌ 源模型目录不存在: {source_models_dir}")
            return all_results
        
        # 创建目标模型目录
        target_models_dir.mkdir(parents=True, exist_ok=True)
        
        print("🚀 开始迁移ComfyUI模型文件...")
        print(f"📁 源目录: {source_models_dir}")
        print(f"📁 目标目录: {target_models_dir}")
        
        # 按类别迁移
        for category in self.model_dirs.keys():
            results = self.migrate_models_by_category(category, source_models_dir, target_models_dir)
            if results:
                all_results[category] = results
        
        # 处理其他模型文件
        other_results = {}
        for item in source_models_dir.iterdir():
            if item.is_dir() and item.name not in self.model_dirs:
                print(f"\n📁 迁移其他模型目录: {item.name}")
                other_files = self.find_model_files(item)
                for model_file in other_files:
                    relative_path = model_file.relative_to(source_models_dir)
                    target_file = target_models_dir / relative_path
                    success = self.copy_model_file(model_file, target_file, verify)
                    other_results[str(relative_path)] = success
        
        if other_results:
            all_results['others'] = other_results
        
        return all_results
    
    def create_migration_report(self, results: Dict[str, Dict[str, bool]]) -> bool:
        """创建迁移报告"""
        try:
            total_files = 0
            successful_files = 0
            failed_files = 0
            
            report_content = "# ComfyUI模型迁移报告\n\n"
            report_content += f"## 迁移统计\n"
            report_content += f"- 源目录: {self.source_dir}\n"
            report_content += f"- 目标目录: {self.target_dir}\n\n"
            
            for category, category_results in results.items():
                report_content += f"## {category.upper()}\n"
                category_success = 0
                category_failed = 0
                
                for file_path, success in category_results.items():
                    total_files += 1
                    if success:
                        successful_files += 1
                        category_success += 1
                        status = "✅ 成功"
                    else:
                        failed_files += 1
                        category_failed += 1
                        status = "❌ 失败"
                    
                    report_content += f"- {file_path}: {status}\n"
                
                report_content += f"\n**统计**: {category_success} 成功, {category_failed} 失败\n\n"
            
            report_content += f"## 总体统计\n"
            report_content += f"- 总文件数: {total_files}\n"
            report_content += f"- 成功迁移: {successful_files}\n"
            report_content += f"- 失败迁移: {failed_files}\n"
            report_content += f"- 成功率: {(successful_files/total_files*100):.1f}%\n\n"
            
            report_content += "## 注意事项\n"
            report_content += "1. 请检查失败的模型文件，可能需要手动复制\n"
            report_content += "2. 确保所有模型文件路径在配置中正确设置\n"
            report_content += "3. 验证模型文件完整性\n"
            report_content += "4. 检查磁盘空间是否充足\n"
            
            report_path = self.target_dir / "MODEL_MIGRATION_REPORT.md"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            print(f"✅ 创建迁移报告: {report_path}")
            return True
            
        except Exception as e:
            print(f"❌ 创建迁移报告失败: {e}")
            return False
    
    def estimate_migration_size(self) -> int:
        """估算迁移所需的总大小"""
        total_size = 0
        source_models_dir = self.source_dir / "models"
        
        if not source_models_dir.exists():
            return 0
        
        print("📊 估算迁移大小...")
        model_files = self.find_model_files(source_models_dir)
        
        for file_path in model_files:
            total_size += self.get_file_size(file_path)
        
        return total_size

def main():
    parser = argparse.ArgumentParser(description='ComfyUI Model Migration Tool')
    parser.add_argument('source_dir', help='Windows ComfyUI安装目录')
    parser.add_argument('target_dir', help='Linux目标目录')
    parser.add_argument('--no-verify', action='store_true', help='跳过文件验证')
    parser.add_argument('--estimate-only', action='store_true', help='仅估算迁移大小')
    parser.add_argument('--create-inventory', action='store_true', help='创建模型文件清单')
    
    args = parser.parse_args()
    
    migrator = ComfyUIModelMigrator(args.source_dir, args.target_dir)
    
    if args.estimate_only:
        total_size = migrator.estimate_migration_size()
        print(f"📊 估算迁移大小: {migrator.format_file_size(total_size)}")
        return
    
    if args.create_inventory:
        inventory = migrator.create_model_inventory(migrator.source_dir / "models")
        inventory_path = migrator.target_dir / "model_inventory.json"
        migrator.save_inventory(inventory, inventory_path)
        return
    
    # 执行完整迁移
    results = migrator.migrate_all_models(verify=not args.no_verify)
    
    # 创建迁移报告
    migrator.create_migration_report(results)
    
    # 显示统计信息
    total_files = sum(len(category_results) for category_results in results.values())
    successful_files = sum(
        sum(1 for success in category_results.values() if success)
        for category_results in results.values()
    )
    
    print(f"\n🎉 模型迁移完成！")
    print(f"📊 总文件数: {total_files}")
    print(f"✅ 成功迁移: {successful_files}")
    print(f"❌ 失败迁移: {total_files - successful_files}")
    print(f"📈 成功率: {(successful_files/total_files*100):.1f}%" if total_files > 0 else "📈 成功率: 0%")

if __name__ == "__main__":
    main()