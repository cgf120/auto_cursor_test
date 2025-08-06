#!/usr/bin/env python3
"""
ComfyUI Cross-Platform Migration Tool
=====================================

This tool helps migrate ComfyUI installations between Windows and Linux systems.
It can run on both Windows and Linux to handle different migration scenarios.
"""

import os
import sys
import json
import shutil
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse
import logging
import zipfile
import tempfile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('comfyui_migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ComfyUIMigrationTool:
    """ComfyUI Cross-Platform Migration Tool"""
    
    def __init__(self, source_path: str, target_path: str = None, mode: str = "auto"):
        self.source_path = Path(source_path)
        self.target_path = Path(target_path) if target_path else None
        self.current_platform = platform.system()
        self.mode = mode
        
        # Detect migration mode
        if mode == "auto":
            if self.current_platform == "Windows":
                self.mode = "windows_to_linux"
            elif self.current_platform == "Linux":
                self.mode = "linux_import"
            else:
                raise ValueError(f"Unsupported platform: {self.current_platform}")
        
        # Common ComfyUI directories and files
        self.comfyui_dirs = [
            "models", "custom_nodes", "output", "input", "temp", 
            "scripts", "web", "nodes", "configs"
        ]
        
        # Files that need path conversion
        self.config_files = [
            "config.json", "user_config.json", "extra_model_paths.yaml",
            "extra_model_paths.json", "comfy_config.yaml"
        ]
        
        # Platform-specific files to exclude
        if self.current_platform == "Windows":
            self.exclude_patterns = [
                "*.exe", "*.bat", "*.cmd", "*.lnk", "Thumbs.db", 
                "desktop.ini", "*.tmp", "*.log"
            ]
        else:
            self.exclude_patterns = [
                "*.sh", "*.pyc", "__pycache__", "*.tmp", "*.log"
            ]

    def analyze_source(self) -> Dict:
        """Analyze the source ComfyUI installation"""
        logger.info(f"Analyzing source ComfyUI installation: {self.source_path}")
        
        analysis = {
            "source_path": str(self.source_path),
            "target_path": str(self.target_path) if self.target_path else None,
            "current_platform": self.current_platform,
            "migration_mode": self.mode,
            "exists": self.source_path.exists(),
            "directories": {},
            "files": {},
            "config_files": {},
            "issues": []
        }
        
        if not self.source_path.exists():
            analysis["issues"].append("Source path does not exist")
            return analysis
        
        # Analyze directories
        for dir_name in self.comfyui_dirs:
            dir_path = self.source_path / dir_name
            if dir_path.exists():
                analysis["directories"][dir_name] = {
                    "path": str(dir_path),
                    "size": self._get_dir_size(dir_path),
                    "file_count": len(list(dir_path.rglob("*")))
                }
            else:
                analysis["directories"][dir_name] = {"exists": False}
        
        # Analyze config files
        for config_file in self.config_files:
            config_path = self.source_path / config_file
            if config_path.exists():
                analysis["config_files"][config_file] = {
                    "path": str(config_path),
                    "size": config_path.stat().st_size
                }
        
        # Check for common issues
        self._check_common_issues(analysis)
        
        return analysis

    def _get_dir_size(self, path: Path) -> int:
        """Get directory size in bytes"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
        except Exception as e:
            logger.warning(f"Error calculating size for {path}: {e}")
        return total_size

    def _check_common_issues(self, analysis: Dict):
        """Check for common migration issues"""
        if self.current_platform == "Windows":
            # Check for Windows-specific files
            windows_files = list(self.source_path.rglob("*.exe"))
            if windows_files:
                analysis["issues"].append(f"Found {len(windows_files)} Windows executable files")
        else:
            # Check for Linux-specific files
            linux_files = list(self.source_path.rglob("*.sh"))
            if linux_files:
                analysis["issues"].append(f"Found {len(linux_files)} Linux shell scripts")

    def convert_paths(self, text: str, from_platform: str = "windows", to_platform: str = "linux") -> str:
        """Convert paths between platforms"""
        if from_platform == "windows" and to_platform == "linux":
            # Convert Windows paths to Linux paths
            text = text.replace("\\\\", "/")  # Handle escaped backslashes first
            text = text.replace("\\", "/")    # Handle single backslashes
            
            # Convert drive letters to Linux paths
            text = text.replace("C:/", "/mnt/c/")
            text = text.replace("D:/", "/mnt/d/")
            text = text.replace("E:/", "/mnt/e/")
            text = text.replace("F:/", "/mnt/f/")
            
            # Remove Windows-specific path prefixes
            text = text.replace("\\\\?\\", "")
            text = text.replace("\\\\.\\", "")
            
        elif from_platform == "linux" and to_platform == "windows":
            # Convert Linux paths to Windows paths
            text = text.replace("/mnt/c/", "C:/")
            text = text.replace("/mnt/d/", "D:/")
            text = text.replace("/mnt/e/", "E:/")
            text = text.replace("/mnt/f/", "F:/")
            text = text.replace("/", "\\")
        
        return text

    def create_migration_package(self, output_path: str = None) -> str:
        """Create a migration package for cross-platform transfer"""
        if self.current_platform != "Windows":
            raise ValueError("Migration package creation is only supported on Windows")
        
        if output_path is None:
            output_path = f"comfyui_migration_package_{platform.node()}.zip"
        
        logger.info(f"Creating migration package: {output_path}")
        
        # Create temporary directory for package
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Copy files to temp directory
            migration_stats = self._copy_files_to_temp(temp_path)
            
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
                json.dump(manifest, f, indent=2)
            
            # Create zip package
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in temp_path.rglob("*"):
                    if file_path.is_file():
                        arcname = file_path.relative_to(temp_path)
                        zipf.write(file_path, arcname)
            
            logger.info(f"Migration package created: {output_path}")
            return output_path

    def _copy_files_to_temp(self, temp_path: Path) -> Dict:
        """Copy files to temporary directory for packaging"""
        migration_stats = {
            "total_files": 0,
            "migrated_files": 0,
            "skipped_files": 0,
            "errors": []
        }
        
        try:
            for item in self.source_path.rglob("*"):
                if item.is_file():
                    migration_stats["total_files"] += 1
                    
                    # Check if file should be excluded
                    if self._should_exclude_file(item, self.exclude_patterns):
                        migration_stats["skipped_files"] += 1
                        continue
                    
                    # Calculate relative path
                    relative_path = item.relative_to(self.source_path)
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
                        logger.error(error_msg)
        
        except Exception as e:
            logger.error(f"Error during file copying: {e}")
            migration_stats["errors"].append(str(e))
        
        return migration_stats

    def import_migration_package(self, package_path: str) -> Dict:
        """Import a migration package on Linux"""
        if self.current_platform != "Linux":
            raise ValueError("Package import is only supported on Linux")
        
        logger.info(f"Importing migration package: {package_path}")
        
        # Extract package
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            with zipfile.ZipFile(package_path, 'r') as zipf:
                zipf.extractall(temp_path)
            
            # Read manifest
            manifest_path = temp_path / "migration_manifest.json"
            if manifest_path.exists():
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                logger.info(f"Package created on: {manifest.get('created_at', 'Unknown')}")
            
            # Set target path if not specified
            if self.target_path is None:
                self.target_path = Path.home() / "ComfyUI"
            
            # Migrate files
            migration_stats = self.migrate_files_from_temp(temp_path)
            
            # Migrate config files
            config_migration = self.migrate_config_files_from_temp(temp_path)
            
            # Fix permissions
            self.fix_permissions()
            
            # Generate report
            report = self.generate_migration_report(manifest, migration_stats)
            
            # Save report
            report_path = self.target_path / "migration_report.txt"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            
            logger.info(f"Migration completed. Report saved to: {report_path}")
            
            return {
                "manifest": manifest,
                "migration_stats": migration_stats,
                "config_migration": config_migration,
                "report_path": str(report_path),
                "success": True
            }

    def migrate_files_from_temp(self, temp_path: Path) -> Dict:
        """Migrate files from temporary directory"""
        logger.info(f"Migrating files from {temp_path} to {self.target_path}")
        
        migration_stats = {
            "total_files": 0,
            "migrated_files": 0,
            "skipped_files": 0,
            "errors": []
        }
        
        try:
            # Create target directory
            self.target_path.mkdir(parents=True, exist_ok=True)
            
            # Copy files recursively
            for item in temp_path.rglob("*"):
                if item.is_file() and item.name != "migration_manifest.json":
                    migration_stats["total_files"] += 1
                    
                    # Calculate relative path
                    relative_path = item.relative_to(temp_path)
                    target_file = self.target_path / relative_path
                    
                    try:
                        # Create target directory if needed
                        target_file.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Copy file
                        shutil.copy2(item, target_file)
                        
                        # Set proper permissions for Linux
                        os.chmod(target_file, 0o644)
                        
                        migration_stats["migrated_files"] += 1
                        
                    except Exception as e:
                        error_msg = f"Error copying {item}: {e}"
                        migration_stats["errors"].append(error_msg)
                        logger.error(error_msg)
            
            # Add Linux-specific files
            self._add_linux_files()
            
            logger.info(f"Migration completed: {migration_stats['migrated_files']} files migrated")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            migration_stats["errors"].append(str(e))
        
        return migration_stats

    def migrate_config_files_from_temp(self, temp_path: Path) -> Dict:
        """Migrate configuration files from temp directory"""
        logger.info("Migrating configuration files...")
        
        migrated_files = {}
        
        for config_file in self.config_files:
            source_config = temp_path / config_file
            if not source_config.exists():
                continue
            
            try:
                # Read the original config
                with open(source_config, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Convert paths in the content
                converted_content = self.convert_paths(content, "windows", "linux")
                
                # Try to parse as JSON and fix any remaining issues
                try:
                    config_data = json.loads(converted_content)
                    # Fix common configuration issues
                    config_data = self._fix_config_data(config_data)
                    converted_content = json.dumps(config_data, indent=2, ensure_ascii=False)
                except json.JSONDecodeError:
                    # Not JSON, keep as is
                    pass
                
                # Write to target
                target_config = self.target_path / config_file
                target_config.parent.mkdir(parents=True, exist_ok=True)
                
                with open(target_config, 'w', encoding='utf-8') as f:
                    f.write(converted_content)
                
                migrated_files[config_file] = {
                    "source": str(source_config),
                    "target": str(target_config),
                    "status": "migrated"
                }
                
                logger.info(f"Migrated config file: {config_file}")
                
            except Exception as e:
                logger.error(f"Error migrating {config_file}: {e}")
                migrated_files[config_file] = {
                    "source": str(source_config),
                    "status": "error",
                    "error": str(e)
                }
        
        return migrated_files

    def _fix_config_data(self, config_data: Dict) -> Dict:
        """Fix common configuration data issues"""
        if isinstance(config_data, dict):
            # Fix model paths
            if "model_paths" in config_data:
                for key, path in config_data["model_paths"].items():
                    if isinstance(path, str):
                        config_data["model_paths"][key] = self.convert_paths(path, "windows", "linux")
            
            # Fix custom nodes paths
            if "custom_nodes" in config_data:
                for node in config_data["custom_nodes"]:
                    if isinstance(node, dict) and "path" in node:
                        node["path"] = self.convert_paths(node["path"], "windows", "linux")
            
            # Fix output paths
            if "output_path" in config_data:
                config_data["output_path"] = self.convert_paths(config_data["output_path"], "windows", "linux")
            
            # Fix input paths
            if "input_path" in config_data:
                config_data["input_path"] = self.convert_paths(config_data["input_path"], "windows", "linux")
        
        return config_data

    def _should_exclude_file(self, file_path: Path, exclude_patterns: List[str]) -> bool:
        """Check if file should be excluded based on patterns"""
        file_name = file_path.name
        for pattern in exclude_patterns:
            if pattern.startswith("*."):
                extension = pattern[1:]
                if file_name.endswith(extension):
                    return True
            elif pattern in file_name:
                return True
        return False

    def _add_linux_files(self):
        """Add Linux-specific files"""
        logger.info("Adding Linux-specific files...")
        
        linux_files = {
            "run_linux.sh": self._generate_run_script(),
            "install_dependencies.sh": self._generate_install_script()
        }
        
        for filename, content in linux_files.items():
            file_path = self.target_path / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Make scripts executable
            if filename.endswith('.sh'):
                os.chmod(file_path, 0o755)
            
            logger.info(f"Added Linux file: {filename}")

    def _generate_run_script(self) -> str:
        """Generate Linux run script"""
        return '''#!/bin/bash
# ComfyUI Linux Run Script

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export COMFYUI_PATH="$(pwd)"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed. Please install pip3."
    exit 1
fi

# Install/upgrade required packages
echo "Installing/upgrading required packages..."
pip3 install --upgrade pip
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip3 install -r requirements.txt

# Run ComfyUI
echo "Starting ComfyUI..."
python3 main.py --listen 0.0.0.0 --port 8188
'''

    def _generate_install_script(self) -> str:
        """Generate Linux installation script"""
        return '''#!/bin/bash
# ComfyUI Linux Dependencies Installation Script

echo "Installing ComfyUI dependencies for Linux..."

# Update package list
sudo apt update

# Install system dependencies
sudo apt install -y python3 python3-pip python3-venv git wget curl

# Install CUDA dependencies (if NVIDIA GPU is available)
if command -v nvidia-smi &> /dev/null; then
    echo "NVIDIA GPU detected. Installing CUDA dependencies..."
    sudo apt install -y nvidia-cuda-toolkit
fi

# Install additional system libraries
sudo apt install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev

echo "System dependencies installed successfully!"
echo "Now run: python3 -m pip install -r requirements.txt"
'''

    def fix_permissions(self):
        """Fix file permissions for Linux"""
        logger.info("Fixing file permissions for Linux...")
        
        try:
            # Make Python files executable
            for py_file in self.target_path.rglob("*.py"):
                if py_file.name in ["main.py", "server.py"]:
                    os.chmod(py_file, 0o755)
            
            # Make shell scripts executable
            for sh_file in self.target_path.rglob("*.sh"):
                os.chmod(sh_file, 0o755)
            
            # Set directory permissions
            for dir_path in self.target_path.rglob("*"):
                if dir_path.is_dir():
                    os.chmod(dir_path, 0o755)
            
            logger.info("File permissions fixed successfully")
            
        except Exception as e:
            logger.error(f"Error fixing permissions: {e}")

    def generate_migration_report(self, manifest: Dict, migration_stats: Dict) -> str:
        """Generate a migration report"""
        report = []
        report.append("=" * 60)
        report.append("ComfyUI Cross-Platform Migration Report")
        report.append("=" * 60)
        report.append("")
        
        # Package information
        report.append(f"Package created on: {manifest.get('created_at', 'Unknown')}")
        report.append(f"Source platform: {manifest.get('source_platform', 'Unknown')}")
        report.append(f"Target platform: {manifest.get('target_platform', 'Unknown')}")
        report.append("")
        
        # Migration statistics
        report.append("Migration Statistics:")
        report.append(f"  Total Files: {migration_stats['total_files']}")
        report.append(f"  Migrated Files: {migration_stats['migrated_files']}")
        report.append(f"  Skipped Files: {migration_stats['skipped_files']}")
        report.append("")
        
        # Errors during migration
        if migration_stats['errors']:
            report.append("Migration Errors:")
            for error in migration_stats['errors']:
                report.append(f"  - {error}")
            report.append("")
        
        # Next steps
        report.append("Next Steps:")
        report.append("1. Navigate to the target directory")
        report.append("2. Run: chmod +x install_dependencies.sh")
        report.append("3. Run: ./install_dependencies.sh")
        report.append("4. Run: chmod +x run_linux.sh")
        report.append("5. Run: ./run_linux.sh")
        report.append("")
        report.append("Note: You may need to adjust model paths in configuration files")
        report.append("if your models are stored in different locations on Linux.")
        
        return "\n".join(report)

    def run_migration(self, dry_run: bool = False) -> Dict:
        """Run the complete migration process"""
        logger.info("Starting ComfyUI migration process...")
        
        if self.mode == "windows_to_linux":
            # Windows mode: create migration package
            if dry_run:
                logger.info("DRY RUN MODE - Package creation would be simulated")
                return {
                    "mode": "dry_run",
                    "operation": "create_package",
                    "would_create": True
                }
            
            package_path = self.create_migration_package()
            return {
                "mode": "windows_to_linux",
                "package_path": package_path,
                "success": True
            }
        
        elif self.mode == "linux_import":
            # Linux mode: import migration package
            if not self.source_path.exists():
                logger.error("Source path does not exist")
                return {"error": "Source path does not exist"}
            
            if dry_run:
                logger.info("DRY RUN MODE - Import would be simulated")
                return {
                    "mode": "dry_run",
                    "operation": "import_package",
                    "would_import": True
                }
            
            result = self.import_migration_package(str(self.source_path))
            return result
        
        else:
            raise ValueError(f"Unknown migration mode: {self.mode}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="ComfyUI Cross-Platform Migration Tool")
    parser.add_argument("source_path", help="Path to source (Windows ComfyUI or migration package)")
    parser.add_argument("-t", "--target", help="Target path for Linux installation (default: ~/ComfyUI)")
    parser.add_argument("--mode", choices=["auto", "windows_to_linux", "linux_import"], 
                       default="auto", help="Migration mode")
    parser.add_argument("--create-package", help="Create migration package (Windows only)")
    parser.add_argument("--dry-run", action="store_true", help="Analyze without making changes")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create migration tool
    migration_tool = ComfyUIMigrationTool(args.source_path, args.target, args.mode)
    
    # Handle package creation mode
    if args.create_package:
        if platform.system() != "Windows":
            logger.error("Package creation is only supported on Windows")
            sys.exit(1)
        
        package_path = migration_tool.create_migration_package(args.create_package)
        print(f"\nMigration package created: {package_path}")
        print("Transfer this file to your Linux system and run:")
        print(f"python3 comfyui_migration_tool.py {package_path} --mode linux_import")
        return
    
    # Run migration
    result = migration_tool.run_migration(dry_run=args.dry_run)
    
    if "error" in result:
        logger.error(f"Migration failed: {result['error']}")
        sys.exit(1)
    
    if result.get("success"):
        if result.get("mode") == "windows_to_linux":
            print("\n" + "=" * 60)
            print("Migration package created successfully!")
            print("=" * 60)
            print(f"Package: {result['package_path']}")
            print("\nNext steps:")
            print("1. Transfer the package to your Linux system")
            print("2. Run: python3 comfyui_migration_tool.py <package> --mode linux_import")
        else:
            print("\n" + "=" * 60)
            print("Migration completed successfully!")
            print("=" * 60)
            print(f"Check the migration report at: {result['report_path']}")
    elif result.get("mode") == "dry_run":
        print("\n" + "=" * 60)
        print("Dry run completed!")
        print("=" * 60)
        print("No files were modified. Use --dry-run to see what would be migrated.")

if __name__ == "__main__":
    main()