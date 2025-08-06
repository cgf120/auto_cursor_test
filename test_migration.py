#!/usr/bin/env python3
"""
Test script for ComfyUI Migration Tool
"""

import os
import tempfile
import shutil
from pathlib import Path
from comfyui_migration_tool import ComfyUIMigrationTool

def create_test_comfyui_structure(base_path: Path):
    """Create a test ComfyUI structure for testing"""
    
    # Create directories
    dirs = [
        "models/checkpoints",
        "models/loras", 
        "custom_nodes",
        "output",
        "input",
        "temp",
        "scripts",
        "web",
        "nodes"
    ]
    
    for dir_name in dirs:
        (base_path / dir_name).mkdir(parents=True, exist_ok=True)
    
    # Create test files
    test_files = {
        "main.py": "# ComfyUI main file\n",
        "requirements.txt": "torch>=1.9.0\ntorchvision>=0.10.0\n",
        "config.json": '{"model_paths": {"checkpoints": "C:\\\\Users\\\\test\\\\models\\\\checkpoints"}}',
        "user_config.json": '{"output_path": "D:\\\\output", "input_path": "C:\\\\input"}',
        "models/checkpoints/test_model.safetensors": "fake model data",
        "custom_nodes/test_node.py": "# Test custom node\n",
        "run.bat": "@echo off\necho Starting ComfyUI\n",
        "ComfyUI.exe": "fake exe data",
        "Thumbs.db": "fake thumbs data"
    }
    
    for file_path, content in test_files.items():
        full_path = base_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)

def test_migration_tool():
    """Test the migration tool"""
    
    print("Testing ComfyUI Migration Tool...")
    
    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create source (Windows-like) structure
        source_path = temp_path / "windows_comfyui"
        create_test_comfyui_structure(source_path)
        
        # Create target directory
        target_path = temp_path / "linux_comfyui"
        
        print(f"Created test structure in: {source_path}")
        print(f"Target path: {target_path}")
        
        # Test analysis
        print("\n1. Testing analysis...")
        migration_tool = ComfyUIMigrationTool(str(source_path), str(target_path))
        analysis = migration_tool.analyze_source()
        
        print(f"Source exists: {analysis['exists']}")
        print(f"Directories found: {list(analysis['directories'].keys())}")
        print(f"Config files found: {list(analysis['config_files'].keys())}")
        
        # Test path conversion
        print("\n2. Testing path conversion...")
        test_paths = [
            r"C:\Users\test\models",
            r"D:\output\images",
            r"\\server\share\models",
            r"C:\Program Files\ComfyUI"
        ]
        
        for path in test_paths:
            converted = migration_tool.convert_paths(path)
            print(f"  {path} -> {converted}")
        
        # Test dry run
        print("\n3. Testing dry run...")
        result = migration_tool.run_migration(dry_run=True)
        print(f"Dry run result: {result.get('mode', 'unknown')}")
        
        # Test actual migration
        print("\n4. Testing actual migration...")
        result = migration_tool.run_migration(dry_run=False)
        
        if result.get('success'):
            print("✅ Migration completed successfully!")
            print(f"Migrated files: {result['migration_stats']['migrated_files']}")
            print(f"Skipped files: {result['migration_stats']['skipped_files']}")
            
            # Check if target files exist
            expected_files = [
                "main.py",
                "requirements.txt", 
                "config.json",
                "user_config.json",
                "run_linux.sh",
                "install_dependencies.sh"
            ]
            
            print("\n5. Verifying migrated files...")
            for file_name in expected_files:
                file_path = target_path / file_name
                if file_path.exists():
                    print(f"  ✅ {file_name}")
                else:
                    print(f"  ❌ {file_name} (missing)")
            
            # Check if Windows files were excluded
            excluded_files = ["ComfyUI.exe", "run.bat", "Thumbs.db"]
            print("\n6. Verifying excluded files...")
            for file_name in excluded_files:
                file_path = target_path / file_name
                if not file_path.exists():
                    print(f"  ✅ {file_name} (correctly excluded)")
                else:
                    print(f"  ❌ {file_name} (should be excluded)")
            
            # Check path conversion in config files
            print("\n7. Verifying config file conversion...")
            config_path = target_path / "config.json"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    content = f.read()
                    if "/mnt/c/Users" in content:
                        print("  ✅ Path conversion in config.json successful")
                    else:
                        print("  ❌ Path conversion in config.json failed")
            
        else:
            print(f"❌ Migration failed: {result.get('error', 'Unknown error')}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_migration_tool()