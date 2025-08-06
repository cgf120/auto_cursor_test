#!/usr/bin/env python3
"""
ComfyUI Cross-Platform Migration Demo
=====================================

This script demonstrates the cross-platform migration workflow:
1. Create a demo Windows ComfyUI installation
2. Create a migration package (simulating Windows)
3. Import the package (simulating Linux)
"""

import os
import tempfile
import shutil
import zipfile
from pathlib import Path
from comfyui_migration_tool import ComfyUIMigrationTool

def create_demo_windows_comfyui():
    """Create a realistic demo Windows ComfyUI installation"""
    
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

def simulate_windows_package_creation(source_path: str) -> str:
    """Simulate Windows package creation"""
    print("🔧 Simulating Windows package creation...")
    
    # Create a temporary directory for the package
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)
    
    # Copy files to temp directory (simulating package creation)
    migration_stats = {
        "total_files": 0,
        "migrated_files": 0,
        "skipped_files": 0,
        "errors": []
    }
    
    source_path = Path(source_path)
    exclude_patterns = ["*.exe", "*.bat", "*.cmd", "*.lnk", "Thumbs.db", "desktop.ini", "*.tmp", "*.log"]
    
    try:
        for item in source_path.rglob("*"):
            if item.is_file():
                migration_stats["total_files"] += 1
                
                # Check if file should be excluded
                file_name = item.name
                should_exclude = False
                for pattern in exclude_patterns:
                    if pattern.startswith("*."):
                        extension = pattern[1:]
                        if file_name.endswith(extension):
                            should_exclude = True
                            break
                    elif pattern in file_name:
                        should_exclude = True
                        break
                
                if should_exclude:
                    migration_stats["skipped_files"] += 1
                    continue
                
                # Calculate relative path
                relative_path = item.relative_to(source_path)
                target_file = temp_path / relative_path
                
                try:
                    # Create target directory if needed
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy file
                    shutil.copy2(item, target_file)
                    migration_stats["migrated_files"] += 1
                    
                except Exception as e:
                    error_msg = f"Error copying {item}: {e}"
                    migration_stats["errors"].append(error_msg)
        
        # Create package manifest
        manifest = {
            "source_platform": "windows",
            "target_platform": "linux",
            "created_at": str(Path().cwd()),
            "migration_stats": migration_stats,
            "instructions": [
                "1. Extract this package on your Linux system",
                "2. Run: python3 comfyui_migration_tool.py extracted_folder --mode linux_import",
                "3. Follow the instructions in the generated report"
            ]
        }
        
        # Save manifest
        with open(temp_path / "migration_manifest.json", 'w') as f:
            import json
            json.dump(manifest, f, indent=2)
        
        # Create zip package
        package_path = "demo_migration_package.zip"
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in temp_path.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(temp_path)
                    zipf.write(file_path, arcname)
        
        print(f"✅ Package created: {package_path}")
        print(f"   Migrated files: {migration_stats['migrated_files']}")
        print(f"   Skipped files: {migration_stats['skipped_files']}")
        return package_path
        
    except Exception as e:
        print(f"❌ Package creation failed: {e}")
        return None

def simulate_linux_package_import(package_path: str) -> str:
    """Simulate Linux package import"""
    print("🐧 Simulating Linux package import...")
    
    # Create target path
    target_path = Path.home() / "demo_linux_comfyui"
    
    # Create migration tool in Linux mode
    migration_tool = ComfyUIMigrationTool(package_path, str(target_path), mode="linux_import")
    
    # Import package
    result = migration_tool.import_migration_package(package_path)
    
    if result.get("success"):
        print(f"✅ Package imported to: {target_path}")
        return str(target_path)
    else:
        print(f"❌ Import failed: {result.get('error', 'Unknown error')}")
        return None

def run_cross_platform_demo():
    """Run the complete cross-platform migration demo"""
    
    print("=" * 70)
    print("ComfyUI Cross-Platform Migration Tool Demo")
    print("=" * 70)
    print()
    
    # Step 1: Create demo Windows ComfyUI
    print("1. Creating demo Windows ComfyUI installation...")
    windows_comfyui_path = create_demo_windows_comfyui()
    print(f"   Created at: {windows_comfyui_path}")
    print()
    
    # Step 2: Simulate Windows package creation
    print("2. Simulating Windows package creation...")
    package_path = simulate_windows_package_creation(windows_comfyui_path)
    print()
    
    # Step 3: Simulate Linux package import
    print("3. Simulating Linux package import...")
    linux_comfyui_path = simulate_linux_package_import(package_path)
    print()
    
    if linux_comfyui_path:
        # Step 4: Verify migration results
        print("4. Verifying migration results...")
        verify_migration_results(linux_comfyui_path)
        print()
        
        # Step 5: Show next steps
        print("5. Migration workflow summary:")
        print("   📦 Windows: Created migration package")
        print("   📤 Transfer: Package transferred to Linux")
        print("   📥 Linux: Package imported successfully")
        print("   ✅ Ready: ComfyUI ready to run on Linux")
        print()
        
        print("=" * 70)
        print("Cross-platform migration demo completed successfully!")
        print("=" * 70)
        print()
        print("Real-world workflow:")
        print("1. On Windows: python comfyui_migration_tool.py C:\\ComfyUI --create-package")
        print("2. Transfer the generated zip file to Linux")
        print("3. On Linux: python3 comfyui_migration_tool.py package.zip --mode linux_import")
        print()
    else:
        print("❌ Demo failed during package import")

def verify_migration_results(linux_path: str):
    """Verify that the migration was successful"""
    linux_path = Path(linux_path)
    
    # Check expected files
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
    
    print("   Checking migrated files:")
    for file_name in expected_files:
        file_path = linux_path / file_name
        if file_path.exists():
            print(f"   ✅ {file_name}")
        else:
            print(f"   ❌ {file_name} (missing)")
    
    # Check excluded files
    excluded_files = ["ComfyUI.exe", "run.bat", "Thumbs.db"]
    print("   Checking excluded files:")
    for file_name in excluded_files:
        file_path = linux_path / file_name
        if not file_path.exists():
            print(f"   ✅ {file_name} (correctly excluded)")
        else:
            print(f"   ❌ {file_name} (should be excluded)")
    
    # Check path conversion
    print("   Checking path conversion:")
    config_path = linux_path / "config.json"
    if config_path.exists():
        with open(config_path, 'r') as f:
            content = f.read()
            if "/mnt/c/Users" in content:
                print("   ✅ Windows paths converted to Linux paths")
            else:
                print("   ❌ Path conversion failed")

if __name__ == "__main__":
    run_cross_platform_demo()