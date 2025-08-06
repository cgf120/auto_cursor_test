#!/usr/bin/env python3
"""
ComfyUI Migration Tool Demo
==========================

This script demonstrates how to use the ComfyUI migration tool
with a sample Windows ComfyUI installation.
"""

import os
import tempfile
import shutil
from pathlib import Path
from comfyui_migration_tool import ComfyUIMigrationTool

def create_demo_comfyui():
    """Create a realistic demo ComfyUI installation"""
    
    # Create a temporary directory that persists for the demo
    temp_dir = tempfile.mkdtemp()
    base_path = Path(temp_dir) / "demo_windows_comfyui"
    
    # Create realistic directory structure
    dirs = [
        "models/checkpoints",
        "models/loras", 
        "models/vae",
        "models/embeddings",
        "models/controlnet",
        "models/upscale_models",
        "custom_nodes/ComfyUI-Manager",
        "custom_nodes/ComfyUI-Impact-Pack",
        "output/ComfyUI_00001_",
        "input",
        "temp",
        "scripts",
        "web",
        "nodes"
    ]
    
    for dir_name in dirs:
        (base_path / dir_name).mkdir(parents=True, exist_ok=True)
        
        # Create realistic files
        files = {
            "main.py": '''#!/usr/bin/env python3
import sys
import os

# ComfyUI main entry point
if __name__ == "__main__":
    print("Starting ComfyUI...")
    # Main ComfyUI code would go here
''',
            
            "requirements.txt": '''torch>=1.9.0
torchvision>=0.10.0
torchaudio>=0.9.0
numpy>=1.21.0
Pillow>=8.3.0
opencv-python>=4.5.0
scipy>=1.7.0
requests>=2.25.0
websockets>=10.0
aiohttp>=3.8.0
''',
            
            "config.json": '''{
  "model_paths": {
    "checkpoints": "C:\\\\Users\\\\demo\\\\ComfyUI\\\\models\\\\checkpoints",
    "loras": "C:\\\\Users\\\\demo\\\\ComfyUI\\\\models\\\\loras",
    "vae": "C:\\\\Users\\\\demo\\\\ComfyUI\\\\models\\\\vae",
    "embeddings": "C:\\\\Users\\\\demo\\\\ComfyUI\\\\models\\\\embeddings",
    "controlnet": "C:\\\\Users\\\\demo\\\\ComfyUI\\\\models\\\\controlnet",
    "upscale_models": "C:\\\\Users\\\\demo\\\\ComfyUI\\\\models\\\\upscale_models"
  },
  "output_path": "D:\\\\ComfyUI\\\\output",
  "input_path": "C:\\\\Users\\\\demo\\\\ComfyUI\\\\input",
  "temp_path": "C:\\\\Users\\\\demo\\\\ComfyUI\\\\temp",
  "custom_nodes_path": "C:\\\\Users\\\\demo\\\\ComfyUI\\\\custom_nodes"
}''',
            
            "user_config.json": '''{
  "server_settings": {
    "listen": "127.0.0.1",
    "port": 8188,
    "enable_cors_header": false,
    "max_upload_size": 100
  },
  "gpu_settings": {
    "use_cuda": true,
    "use_cpu": false,
    "precision": "normal"
  },
  "memory_settings": {
    "max_models": 3,
    "max_vram": 0
  }
}''',
            
            "models/checkpoints/sd_xl_base_1.0.safetensors": "fake model data for SDXL",
            "models/loras/sd_xl_offset.safetensors": "fake LoRA data",
            "models/vae/sdxl_vae.safetensors": "fake VAE data",
            
            "custom_nodes/ComfyUI-Manager/__init__.py": "# ComfyUI Manager custom node",
            "custom_nodes/ComfyUI-Impact-Pack/__init__.py": "# Impact Pack custom node",
            
            "output/ComfyUI_00001_/sample_image.png": "fake image data",
            
            "run.bat": '''@echo off
echo Starting ComfyUI...
python main.py --listen 0.0.0.0 --port 8188
pause
''',
            
            "ComfyUI.exe": "fake executable data",
            "Thumbs.db": "fake thumbs data",
            "desktop.ini": "[.ShellClassInfo]\nIconResource=C:\\Windows\\System32\\shell32.dll,45"
        }
        
        for file_path, content in files.items():
            full_path = base_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return str(base_path)

def run_demo():
    """Run the migration demo"""
    
    print("=" * 60)
    print("ComfyUI Windows to Linux Migration Tool Demo")
    print("=" * 60)
    print()
    
    # Create demo ComfyUI installation
    print("1. Creating demo Windows ComfyUI installation...")
    source_path = create_demo_comfyui()
    print(f"   Created at: {source_path}")
    
    # Create target path
    target_path = Path.home() / "demo_linux_comfyui"
    print(f"   Target path: {target_path}")
    print()
    
    # Analyze source
    print("2. Analyzing source installation...")
    migration_tool = ComfyUIMigrationTool(source_path, str(target_path))
    analysis = migration_tool.analyze_source()
    
    print(f"   Source exists: {analysis['exists']}")
    print(f"   Directories found: {len([d for d in analysis['directories'].values() if d.get('exists', False)])}")
    print(f"   Config files found: {len(analysis['config_files'])}")
    print()
    
    # Show what would be migrated
    print("3. Previewing migration (dry run)...")
    result = migration_tool.run_migration(dry_run=True)
    print(f"   Dry run completed successfully")
    print()
    
    # Perform actual migration
    print("4. Performing actual migration...")
    result = migration_tool.run_migration(dry_run=False)
    
    if result.get('success'):
        print("   ✅ Migration completed successfully!")
        print(f"   Migrated files: {result['migration_stats']['migrated_files']}")
        print(f"   Skipped files: {result['migration_stats']['skipped_files']}")
        print(f"   Report saved to: {result['report_path']}")
        print()
        
        # Show some migrated files
        print("5. Checking migrated files...")
        expected_files = [
            "main.py",
            "requirements.txt", 
            "config.json",
            "user_config.json",
            "run_linux.sh",
            "install_dependencies.sh",
            "models/checkpoints/sd_xl_base_1.0.safetensors",
            "custom_nodes/ComfyUI-Manager/__init__.py"
        ]
        
        for file_name in expected_files:
            file_path = target_path / file_name
            if file_path.exists():
                print(f"   ✅ {file_name}")
            else:
                print(f"   ❌ {file_name} (missing)")
        
        print()
        
        # Show path conversion example
        print("6. Path conversion example:")
        original_config = Path(source_path) / "config.json"
        migrated_config = target_path / "config.json"
        
        if migrated_config.exists():
            with open(migrated_config, 'r') as f:
                content = f.read()
                if "/mnt/c/Users" in content:
                    print("   ✅ Windows paths converted to Linux paths")
                else:
                    print("   ❌ Path conversion failed")
        
        print()
        print("=" * 60)
        print("Demo completed successfully!")
        print("=" * 60)
        print()
        print("Next steps:")
        print(f"1. cd {target_path}")
        print("2. chmod +x install_dependencies.sh")
        print("3. ./install_dependencies.sh")
        print("4. pip3 install -r requirements.txt")
        print("5. chmod +x run_linux.sh")
        print("6. ./run_linux.sh")
        print()
        
    else:
        print(f"   ❌ Migration failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    run_demo()