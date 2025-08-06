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
import platform
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse
import logging

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
    """ComfyUI Windows to Linux Migration Tool"""
    
    def __init__(self, source_path: str, target_path: str = None):
        self.source_path = Path(source_path)
        self.target_path = Path(target_path) if target_path else Path.home() / "ComfyUI"
        self.migration_config = {}
        
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
        
        # Windows-specific files to exclude
        self.exclude_patterns = [
            "*.exe", "*.bat", "*.cmd", "*.lnk", "Thumbs.db", 
            "desktop.ini", "*.tmp", "*.log"
        ]
        
        # Linux-specific files to add
        self.linux_files = {
            "run_linux.sh": self._generate_run_script(),
            "install_dependencies.sh": self._generate_install_script()
        }

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

    def analyze_source(self) -> Dict:
        """Analyze the source ComfyUI installation"""
        logger.info(f"Analyzing source ComfyUI installation: {self.source_path}")
        
        analysis = {
            "source_path": str(self.source_path),
            "target_path": str(self.target_path),
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
        # Check for Windows-specific files
        windows_files = list(self.source_path.rglob("*.exe"))
        if windows_files:
            analysis["issues"].append(f"Found {len(windows_files)} Windows executable files")
        
        # Check for hardcoded Windows paths
        path_patterns = [r"C:\\", r"D:\\", r"E:\\", r"F:\\"]
        for pattern in path_patterns:
            # This would need more sophisticated text file scanning
            pass

    def convert_paths(self, text: str) -> str:
        """Convert Windows paths to Linux paths"""
        # Convert Windows path separators (handle both single and double backslashes)
        text = text.replace("\\\\", "/")  # Handle escaped backslashes first
        text = text.replace("\\", "/")    # Handle single backslashes
        
        # Convert drive letters to Linux paths
        # This is a simplified conversion - in practice, you'd need to map drives
        text = text.replace("C:/", "/mnt/c/")
        text = text.replace("D:/", "/mnt/d/")
        text = text.replace("E:/", "/mnt/e/")
        text = text.replace("F:/", "/mnt/f/")
        
        # Remove Windows-specific path prefixes
        text = text.replace("\\\\?\\", "")
        text = text.replace("\\\\.\\", "")
        
        return text

    def migrate_config_files(self) -> Dict:
        """Migrate configuration files"""
        logger.info("Migrating configuration files...")
        
        migrated_files = {}
        
        for config_file in self.config_files:
            source_config = self.source_path / config_file
            if not source_config.exists():
                continue
            
            try:
                # Read the original config
                with open(source_config, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Convert paths in the content
                converted_content = self.convert_paths(content)
                
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
        # Handle different config file structures
        if isinstance(config_data, dict):
            # Fix model paths
            if "model_paths" in config_data:
                for key, path in config_data["model_paths"].items():
                    if isinstance(path, str):
                        config_data["model_paths"][key] = self.convert_paths(path)
            
            # Fix custom nodes paths
            if "custom_nodes" in config_data:
                for node in config_data["custom_nodes"]:
                    if isinstance(node, dict) and "path" in node:
                        node["path"] = self.convert_paths(node["path"])
            
            # Fix output paths
            if "output_path" in config_data:
                config_data["output_path"] = self.convert_paths(config_data["output_path"])
            
            # Fix input paths
            if "input_path" in config_data:
                config_data["input_path"] = self.convert_paths(config_data["input_path"])
        
        return config_data

    def migrate_files(self, exclude_patterns: List[str] = None) -> Dict:
        """Migrate files from Windows to Linux"""
        logger.info(f"Migrating files from {self.source_path} to {self.target_path}")
        
        if exclude_patterns is None:
            exclude_patterns = self.exclude_patterns
        
        migration_stats = {
            "total_files": 0,
            "migrated_files": 0,
            "skipped_files": 0,
            "errors": [],
            "migrated_dirs": []
        }
        
        try:
            # Create target directory
            self.target_path.mkdir(parents=True, exist_ok=True)
            
            # Copy files recursively
            for item in self.source_path.rglob("*"):
                if item.is_file():
                    migration_stats["total_files"] += 1
                    
                    # Check if file should be excluded
                    if self._should_exclude_file(item, exclude_patterns):
                        migration_stats["skipped_files"] += 1
                        continue
                    
                    # Calculate relative path
                    relative_path = item.relative_to(self.source_path)
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
                
                elif item.is_dir():
                    relative_path = item.relative_to(self.source_path)
                    target_dir = self.target_path / relative_path
                    
                    if target_dir not in migration_stats["migrated_dirs"]:
                        migration_stats["migrated_dirs"].append(str(target_dir))
            
            # Add Linux-specific files
            self._add_linux_files()
            
            logger.info(f"Migration completed: {migration_stats['migrated_files']} files migrated")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            migration_stats["errors"].append(str(e))
        
        return migration_stats

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
        
        for filename, content in self.linux_files.items():
            file_path = self.target_path / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Make scripts executable
            if filename.endswith('.sh'):
                os.chmod(file_path, 0o755)
            
            logger.info(f"Added Linux file: {filename}")

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

    def generate_migration_report(self, analysis: Dict, migration_stats: Dict) -> str:
        """Generate a migration report"""
        report = []
        report.append("=" * 60)
        report.append("ComfyUI Windows to Linux Migration Report")
        report.append("=" * 60)
        report.append("")
        
        # Source and target information
        report.append(f"Source Path: {analysis['source_path']}")
        report.append(f"Target Path: {analysis['target_path']}")
        report.append("")
        
        # Migration statistics
        report.append("Migration Statistics:")
        report.append(f"  Total Files: {migration_stats['total_files']}")
        report.append(f"  Migrated Files: {migration_stats['migrated_files']}")
        report.append(f"  Skipped Files: {migration_stats['skipped_files']}")
        report.append("")
        
        # Issues found
        if analysis['issues']:
            report.append("Issues Found:")
            for issue in analysis['issues']:
                report.append(f"  - {issue}")
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
        
        # Analyze source
        analysis = self.analyze_source()
        
        if not analysis['exists']:
            logger.error("Source path does not exist")
            return {"error": "Source path does not exist"}
        
        if dry_run:
            logger.info("DRY RUN MODE - No files will be modified")
            return {
                "mode": "dry_run",
                "analysis": analysis,
                "would_migrate": True
            }
        
        # Create target directory
        self.target_path.mkdir(parents=True, exist_ok=True)
        
        # Migrate files
        migration_stats = self.migrate_files()
        
        # Migrate config files
        config_migration = self.migrate_config_files()
        
        # Fix permissions
        self.fix_permissions()
        
        # Generate report
        report = self.generate_migration_report(analysis, migration_stats)
        
        # Save report
        report_path = self.target_path / "migration_report.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"Migration completed. Report saved to: {report_path}")
        
        return {
            "analysis": analysis,
            "migration_stats": migration_stats,
            "config_migration": config_migration,
            "report_path": str(report_path),
            "success": True
        }

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="ComfyUI Windows to Linux Migration Tool")
    parser.add_argument("source_path", help="Path to Windows ComfyUI installation")
    parser.add_argument("-t", "--target", help="Target path for Linux installation (default: ~/ComfyUI)")
    parser.add_argument("--dry-run", action="store_true", help="Analyze without making changes")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Check if running on Linux
    if platform.system() != "Linux":
        logger.warning("This tool is designed for Linux. Running on: " + platform.system())
    
    # Create migration tool
    migration_tool = ComfyUIMigrationTool(args.source_path, args.target)
    
    # Run migration
    result = migration_tool.run_migration(dry_run=args.dry_run)
    
    if "error" in result:
        logger.error(f"Migration failed: {result['error']}")
        sys.exit(1)
    
    if result.get("success"):
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