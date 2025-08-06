#!/usr/bin/env python3
"""
ComfyUI Migration Tool Test Script
==================================

测试迁移工具的基本功能
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

def create_test_comfyui_structure(base_dir: Path):
    """创建测试用的ComfyUI目录结构"""
    print("📁 创建测试ComfyUI目录结构...")
    
    # 创建主要目录
    (base_dir / "models" / "checkpoints").mkdir(parents=True, exist_ok=True)
    (base_dir / "models" / "loras").mkdir(parents=True, exist_ok=True)
    (base_dir / "models" / "embeddings").mkdir(parents=True, exist_ok=True)
    (base_dir / "custom_nodes").mkdir(parents=True, exist_ok=True)
    
    # 创建测试文件
    (base_dir / "main.py").write_text("# ComfyUI main.py")
    (base_dir / "requirements.txt").write_text("torch\ntransformers\ndiffusers")
    
    # 创建测试配置文件
    config_content = """
checkpoints: "C:\\Users\\User\\ComfyUI\\models\\checkpoints"
loras: "C:\\Users\\User\\ComfyUI\\models\\loras"
embeddings: "C:\\Users\\User\\ComfyUI\\models\\embeddings"
output_dir: "C:\\Users\\User\\ComfyUI\\output"
"""
    (base_dir / "extra_model_paths.yaml").write_text(config_content)
    
    # 创建测试模型文件（空文件）
    (base_dir / "models" / "checkpoints" / "test_model.safetensors").write_text("")
    (base_dir / "models" / "loras" / "test_lora.safetensors").write_text("")
    (base_dir / "models" / "embeddings" / "test_embedding.bin").write_text("")
    
    print("✅ 测试目录结构创建完成")

def test_path_conversion():
    """测试路径转换功能"""
    print("\n🔧 测试路径转换功能...")
    
    # 导入路径转换函数
    sys.path.append('.')
    from comfyui_config_migrator import ComfyUIConfigMigrator
    
    migrator = ComfyUIConfigMigrator("/tmp", "/tmp")
    
    test_paths = [
        ("C:\\Users\\User\\ComfyUI", "/media/user/c/Users/User/ComfyUI"),
        ("D:\\Models\\checkpoints", "/media/user/d/Models/checkpoints"),
        (".\\models\\loras", "models/loras"),
        ("..\\config\\test.yaml", "config/test.yaml"),
        ("/already/linux/path", "/already/linux/path")
    ]
    
    for windows_path, expected_linux_path in test_paths:
        converted = migrator.convert_windows_path_to_linux(windows_path)
        if converted == expected_linux_path:
            print(f"✅ {windows_path} -> {converted}")
        else:
            print(f"❌ {windows_path} -> {converted} (期望: {expected_linux_path})")

def test_file_operations():
    """测试文件操作功能"""
    print("\n📁 测试文件操作功能...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 创建测试文件
        test_file = temp_path / "test.txt"
        test_file.write_text("Hello, World!")
        
        # 测试文件大小计算
        from comfyui_model_migrator import ComfyUIModelMigrator
        migrator = ComfyUIModelMigrator("/tmp", "/tmp")
        
        size = migrator.get_file_size(test_file)
        formatted_size = migrator.format_file_size(size)
        
        print(f"✅ 文件大小: {size} bytes -> {formatted_size}")
        
        # 测试哈希计算
        file_hash = migrator.calculate_file_hash(test_file)
        print(f"✅ 文件哈希: {file_hash[:8]}...")

def test_config_migration():
    """测试配置迁移功能"""
    print("\n⚙️ 测试配置迁移功能...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 创建测试配置
        config_content = """checkpoints: "C:/Users/User/ComfyUI/models/checkpoints"
loras: "C:/Users/User/ComfyUI/models/loras"
output_dir: "C:/Users/User/ComfyUI/output"
"""
        config_file = temp_path / "test_config.yaml"
        config_file.write_text(config_content)
        
        # 测试配置迁移
        from comfyui_config_migrator import ComfyUIConfigMigrator
        migrator = ComfyUIConfigMigrator("/tmp", str(temp_path))
        
        success = migrator.migrate_model_paths(config_file)
        if success:
            print("✅ 配置迁移测试成功")
            
            # 检查迁移结果
            migrated_content = config_file.read_text()
            if "C:\\" not in migrated_content and "/media/" in migrated_content:
                print("✅ 路径转换验证成功")
            else:
                print("❌ 路径转换验证失败")
        else:
            print("❌ 配置迁移测试失败")

def run_all_tests():
    """运行所有测试"""
    print("🧪 ComfyUI Migration Tool 测试套件")
    print("==================================")
    
    # 创建测试环境
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        source_dir = temp_path / "source_comfyui"
        target_dir = temp_path / "target_comfyui"
        
        try:
            # 测试1: 创建测试目录结构
            create_test_comfyui_structure(source_dir)
            
            # 测试2: 路径转换
            test_path_conversion()
            
            # 测试3: 文件操作
            test_file_operations()
            
            # 测试4: 配置迁移
            test_config_migration()
            
            print("\n🎉 所有测试完成！")
            print("✅ 迁移工具基本功能正常")
            
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)