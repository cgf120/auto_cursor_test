#!/usr/bin/env python3
"""
ComfyUI Configuration Migration Tool
====================================

专门处理ComfyUI配置文件的迁移，包括模型路径、自定义节点配置等。
"""

import os
import json
import yaml
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

class ComfyUIConfigMigrator:
    def __init__(self, source_dir: str, target_dir: str):
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        
        # ComfyUI常见的配置文件
        self.config_files = {
            'extra_model_paths.yaml': self.migrate_model_paths,
            'extra_model_paths.json': self.migrate_model_paths,
            'config.yaml': self.migrate_general_config,
            'config.json': self.migrate_general_config,
            'user_config.yaml': self.migrate_user_config,
            'user_config.json': self.migrate_user_config
        }
        
        # 常见的模型目录
        self.model_dirs = [
            'models/checkpoints',
            'models/loras',
            'models/embeddings',
            'models/vae',
            'models/controlnet',
            'models/upscale_models',
            'models/clip',
            'models/clip_vision',
            'models/gligen',
            'models/unclip',
            'models/style_models',
            'models/ipadapter',
            'models/insightface',
            'models/ultralytics',
            'models/bbox',
            'models/segm',
            'models/face_restoration',
            'models/face_parsing',
            'models/face_recognition',
            'models/face_enhancement',
            'models/face_swap',
            'models/face_detection',
            'models/face_alignment',
            'models/face_landmarks',
            'models/face_mesh',
            'models/face_segmentation',
            'models/face_3d',
            'models/face_reconstruction',
            'models/face_tracking',
            'models/face_analysis',
            'models/face_synthesis',
            'models/face_manipulation',
            'models/face_editing',
            'models/face_generation',
            'models/face_transfer',
            'models/face_morphing',
            'models/face_animation',
            'models/face_expression',
            'models/face_emotion',
            'models/face_age',
            'models/face_gender',
            'models/face_ethnicity',
            'models/face_pose',
            'models/face_lighting',
            'models/face_occlusion',
            'models/face_quality',
            'models/face_attributes',
            'models/face_verification',
            'models/face_identification',
            'models/face_recognition_models',
            'models/face_detection_models',
            'models/face_alignment_models',
            'models/face_landmarks_models',
            'models/face_mesh_models',
            'models/face_segmentation_models',
            'models/face_3d_models',
            'models/face_reconstruction_models',
            'models/face_tracking_models',
            'models/face_analysis_models',
            'models/face_synthesis_models',
            'models/face_manipulation_models',
            'models/face_editing_models',
            'models/face_generation_models',
            'models/face_transfer_models',
            'models/face_morphing_models',
            'models/face_animation_models',
            'models/face_expression_models',
            'models/face_emotion_models',
            'models/face_age_models',
            'models/face_gender_models',
            'models/face_ethnicity_models',
            'models/face_pose_models',
            'models/face_lighting_models',
            'models/face_occlusion_models',
            'models/face_quality_models',
            'models/face_attributes_models',
            'models/face_verification_models',
            'models/face_identification_models'
        ]
    
    def convert_windows_path_to_linux(self, path: str) -> str:
        """将Windows路径转换为Linux路径"""
        if not path:
            return path
            
        # 替换反斜杠为正斜杠
        path = path.replace('\\', '/')
        
        # 处理驱动器盘符
        if re.match(r'^[A-Za-z]:', path):
            # 移除驱动器盘符，假设挂载在/media/username/drive
            drive_letter = path[0].lower()
            path = path[2:]  # 移除 "C:"
            path = f"/media/user/{drive_letter}{path}"
        
        # 处理相对路径
        if path.startswith('./'):
            path = path[2:]
        elif path.startswith('../'):
            path = path[3:]
            
        return path
    
    def migrate_model_paths(self, config_path: Path) -> bool:
        """迁移模型路径配置"""
        try:
            print(f"🔧 迁移模型路径配置: {config_path.name}")
            
            # 读取配置文件
            if config_path.suffix == '.json':
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
            
            updated = False
            
            # 处理不同的配置格式
            if isinstance(config, dict):
                # 处理键值对格式
                for key, value in config.items():
                    if isinstance(value, str):
                        new_path = self.convert_windows_path_to_linux(value)
                        if new_path != value:
                            config[key] = new_path
                            updated = True
                            print(f"  📝 更新路径: {key} -> {new_path}")
                    elif isinstance(value, dict):
                        # 递归处理嵌套字典
                        if self._update_nested_paths(value):
                            updated = True
            elif isinstance(config, list):
                # 处理列表格式
                for i, item in enumerate(config):
                    if isinstance(item, str):
                        new_path = self.convert_windows_path_to_linux(item)
                        if new_path != item:
                            config[i] = new_path
                            updated = True
                            print(f"  📝 更新路径: {item} -> {new_path}")
                    elif isinstance(item, dict):
                        if self._update_nested_paths(item):
                            updated = True
            
            if updated:
                # 保存更新后的配置
                if config_path.suffix == '.json':
                    with open(config_path, 'w', encoding='utf-8') as f:
                        json.dump(config, f, indent=2, ensure_ascii=False)
                else:
                    with open(config_path, 'w', encoding='utf-8') as f:
                        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
                
                print(f"✅ 模型路径配置已更新")
                return True
            else:
                print(f"ℹ️  模型路径配置无需更新")
                return False
                
        except Exception as e:
            print(f"❌ 迁移模型路径配置失败: {e}")
            return False
    
    def _update_nested_paths(self, obj: Any) -> bool:
        """递归更新嵌套对象中的路径"""
        updated = False
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str) and ('\\' in value or ':' in value):
                    new_path = self.convert_windows_path_to_linux(value)
                    if new_path != value:
                        obj[key] = new_path
                        updated = True
                        print(f"  📝 更新嵌套路径: {key} -> {new_path}")
                elif isinstance(value, (dict, list)):
                    if self._update_nested_paths(value):
                        updated = True
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                if isinstance(item, str) and ('\\' in item or ':' in item):
                    new_path = self.convert_windows_path_to_linux(item)
                    if new_path != item:
                        obj[i] = new_path
                        updated = True
                        print(f"  📝 更新列表路径: {item} -> {new_path}")
                elif isinstance(item, (dict, list)):
                    if self._update_nested_paths(item):
                        updated = True
        
        return updated
    
    def migrate_general_config(self, config_path: Path) -> bool:
        """迁移通用配置"""
        try:
            print(f"🔧 迁移通用配置: {config_path.name}")
            
            # 读取配置文件
            if config_path.suffix == '.json':
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
            
            updated = False
            
            # 处理常见的配置项
            if isinstance(config, dict):
                # 处理输出目录
                if 'output_dir' in config:
                    new_path = self.convert_windows_path_to_linux(config['output_dir'])
                    if new_path != config['output_dir']:
                        config['output_dir'] = new_path
                        updated = True
                        print(f"  📝 更新输出目录: {config['output_dir']} -> {new_path}")
                
                # 处理临时目录
                if 'temp_dir' in config:
                    new_path = self.convert_windows_path_to_linux(config['temp_dir'])
                    if new_path != config['temp_dir']:
                        config['temp_dir'] = new_path
                        updated = True
                        print(f"  📝 更新临时目录: {config['temp_dir']} -> {new_path}")
                
                # 处理日志目录
                if 'log_dir' in config:
                    new_path = self.convert_windows_path_to_linux(config['log_dir'])
                    if new_path != config['log_dir']:
                        config['log_dir'] = new_path
                        updated = True
                        print(f"  📝 更新日志目录: {config['log_dir']} -> {new_path}")
                
                # 递归处理其他路径
                if self._update_nested_paths(config):
                    updated = True
            
            if updated:
                # 保存更新后的配置
                if config_path.suffix == '.json':
                    with open(config_path, 'w', encoding='utf-8') as f:
                        json.dump(config, f, indent=2, ensure_ascii=False)
                else:
                    with open(config_path, 'w', encoding='utf-8') as f:
                        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
                
                print(f"✅ 通用配置已更新")
                return True
            else:
                print(f"ℹ️  通用配置无需更新")
                return False
                
        except Exception as e:
            print(f"❌ 迁移通用配置失败: {e}")
            return False
    
    def migrate_user_config(self, config_path: Path) -> bool:
        """迁移用户配置"""
        try:
            print(f"🔧 迁移用户配置: {config_path.name}")
            
            # 读取配置文件
            if config_path.suffix == '.json':
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
            
            updated = False
            
            # 处理用户特定的配置
            if isinstance(config, dict):
                # 处理自定义节点路径
                if 'custom_nodes_path' in config:
                    new_path = self.convert_windows_path_to_linux(config['custom_nodes_path'])
                    if new_path != config['custom_nodes_path']:
                        config['custom_nodes_path'] = new_path
                        updated = True
                        print(f"  📝 更新自定义节点路径: {config['custom_nodes_path']} -> {new_path}")
                
                # 处理工作流保存路径
                if 'workflow_dir' in config:
                    new_path = self.convert_windows_path_to_linux(config['workflow_dir'])
                    if new_path != config['workflow_dir']:
                        config['workflow_dir'] = new_path
                        updated = True
                        print(f"  📝 更新工作流目录: {config['workflow_dir']} -> {new_path}")
                
                # 递归处理其他路径
                if self._update_nested_paths(config):
                    updated = True
            
            if updated:
                # 保存更新后的配置
                if config_path.suffix == '.json':
                    with open(config_path, 'w', encoding='utf-8') as f:
                        json.dump(config, f, indent=2, ensure_ascii=False)
                else:
                    with open(config_path, 'w', encoding='utf-8') as f:
                        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
                
                print(f"✅ 用户配置已更新")
                return True
            else:
                print(f"ℹ️  用户配置无需更新")
                return False
                
        except Exception as e:
            print(f"❌ 迁移用户配置失败: {e}")
            return False
    
    def create_model_paths_template(self) -> bool:
        """创建模型路径配置模板"""
        try:
            template = {
                "checkpoints": "/path/to/models/checkpoints",
                "loras": "/path/to/models/loras", 
                "embeddings": "/path/to/models/embeddings",
                "vae": "/path/to/models/vae",
                "controlnet": "/path/to/models/controlnet",
                "upscale_models": "/path/to/models/upscale_models",
                "clip": "/path/to/models/clip",
                "clip_vision": "/path/to/models/clip_vision",
                "gligen": "/path/to/models/gligen",
                "unclip": "/path/to/models/unclip",
                "style_models": "/path/to/models/style_models",
                "ipadapter": "/path/to/models/ipadapter",
                "insightface": "/path/to/models/insightface",
                "ultralytics": "/path/to/models/ultralytics",
                "bbox": "/path/to/models/bbox",
                "segm": "/path/to/models/segm",
                "face_restoration": "/path/to/models/face_restoration",
                "face_parsing": "/path/to/models/face_parsing",
                "face_recognition": "/path/to/models/face_recognition",
                "face_enhancement": "/path/to/models/face_enhancement",
                "face_swap": "/path/to/models/face_swap",
                "face_detection": "/path/to/models/face_detection",
                "face_alignment": "/path/to/models/face_alignment",
                "face_landmarks": "/path/to/models/face_landmarks",
                "face_mesh": "/path/to/models/face_mesh",
                "face_segmentation": "/path/to/models/face_segmentation",
                "face_3d": "/path/to/models/face_3d",
                "face_reconstruction": "/path/to/models/face_reconstruction",
                "face_tracking": "/path/to/models/face_tracking",
                "face_analysis": "/path/to/models/face_analysis",
                "face_synthesis": "/path/to/models/face_synthesis",
                "face_manipulation": "/path/to/models/face_manipulation",
                "face_editing": "/path/to/models/face_editing",
                "face_generation": "/path/to/models/face_generation",
                "face_transfer": "/path/to/models/face_transfer",
                "face_morphing": "/path/to/models/face_morphing",
                "face_animation": "/path/to/models/face_animation",
                "face_expression": "/path/to/models/face_expression",
                "face_emotion": "/path/to/models/face_emotion",
                "face_age": "/path/to/models/face_age",
                "face_gender": "/path/to/models/face_gender",
                "face_ethnicity": "/path/to/models/face_ethnicity",
                "face_pose": "/path/to/models/face_pose",
                "face_lighting": "/path/to/models/face_lighting",
                "face_occlusion": "/path/to/models/face_occlusion",
                "face_quality": "/path/to/models/face_quality",
                "face_attributes": "/path/to/models/face_attributes",
                "face_verification": "/path/to/models/face_verification",
                "face_identification": "/path/to/models/face_identification"
            }
            
            template_path = self.target_dir / "extra_model_paths_template.yaml"
            with open(template_path, 'w', encoding='utf-8') as f:
                yaml.dump(template, f, default_flow_style=False, allow_unicode=True)
            
            print(f"✅ 创建模型路径配置模板: {template_path}")
            return True
            
        except Exception as e:
            print(f"❌ 创建模型路径配置模板失败: {e}")
            return False
    
    def migrate_all_configs(self) -> Dict[str, bool]:
        """迁移所有配置文件"""
        results = {}
        
        print("🚀 开始迁移ComfyUI配置文件...")
        
        for config_name, migrate_func in self.config_files.items():
            source_config = self.source_dir / config_name
            target_config = self.target_dir / config_name
            
            if source_config.exists():
                # 复制配置文件到目标目录
                try:
                    import shutil
                    shutil.copy2(source_config, target_config)
                    print(f"📋 复制配置文件: {config_name}")
                    
                    # 迁移配置
                    results[config_name] = migrate_func(target_config)
                    
                except Exception as e:
                    print(f"❌ 处理配置文件失败 {config_name}: {e}")
                    results[config_name] = False
            else:
                print(f"ℹ️  配置文件不存在: {config_name}")
                results[config_name] = False
        
        # 创建模型路径配置模板
        self.create_model_paths_template()
        
        return results

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='ComfyUI Configuration Migration Tool')
    parser.add_argument('source_dir', help='Windows ComfyUI安装目录')
    parser.add_argument('target_dir', help='Linux目标目录')
    
    args = parser.parse_args()
    
    migrator = ComfyUIConfigMigrator(args.source_dir, args.target_dir)
    results = migrator.migrate_all_configs()
    
    print("\n📊 迁移结果:")
    for config_name, success in results.items():
        status = "✅ 成功" if success else "❌ 失败"
        print(f"  {config_name}: {status}")
    
    print("\n🎉 配置文件迁移完成！")
    print("📝 请检查生成的配置文件并根据需要调整路径。")

if __name__ == "__main__":
    main()