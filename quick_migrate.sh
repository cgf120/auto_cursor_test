#!/bin/bash

# ComfyUI Migration Tool - Quick Start Script
# ===========================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "ComfyUI Windows to Linux Migration Tool"
    echo "======================================"
    echo ""
    echo "Usage: $0 <source_path> [target_path] [options]"
    echo ""
    echo "Arguments:"
    echo "  source_path    Path to Windows ComfyUI installation"
    echo "  target_path    Target path for Linux (optional, default: ~/ComfyUI)"
    echo ""
    echo "Options:"
    echo "  --dry-run      Preview migration without making changes"
    echo "  --verbose      Enable verbose output"
    echo "  --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 /mnt/windows/ComfyUI"
    echo "  $0 /mnt/windows/ComfyUI /home/user/custom/comfyui"
    echo "  $0 /mnt/windows/ComfyUI --dry-run"
    echo ""
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Python 3 is available
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.7 or higher."
        exit 1
    fi
    
    # Check Python version
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    required_version="3.7"
    
    if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
        print_error "Python version $python_version is too old. Please install Python 3.7 or higher."
        exit 1
    fi
    
    print_success "Python $python_version found"
    
    # Check if migration tool exists
    if [ ! -f "comfyui_migration_tool.py" ]; then
        print_error "Migration tool (comfyui_migration_tool.py) not found in current directory."
        exit 1
    fi
    
    print_success "Migration tool found"
}

# Function to validate source path
validate_source_path() {
    local source_path="$1"
    
    if [ ! -d "$source_path" ]; then
        print_error "Source path does not exist: $source_path"
        exit 1
    fi
    
    # Check if it looks like a ComfyUI installation
    if [ ! -f "$source_path/main.py" ] && [ ! -f "$source_path/ComfyUI.exe" ]; then
        print_warning "Source path doesn't appear to be a ComfyUI installation"
        print_warning "Continuing anyway..."
    fi
    
    print_success "Source path validated: $source_path"
}

# Function to estimate disk space
estimate_disk_space() {
    local source_path="$1"
    local target_path="$2"
    
    print_status "Estimating required disk space..."
    
    # Get source directory size
    source_size=$(du -sb "$source_path" 2>/dev/null | cut -f1 || echo "0")
    
    # Convert to human readable
    if [ "$source_size" -gt 1073741824 ]; then
        source_size_human=$(echo "scale=1; $source_size / 1073741824" | bc -l 2>/dev/null || echo "unknown")
        source_size_human="${source_size_human}GB"
    elif [ "$source_size" -gt 1048576 ]; then
        source_size_human=$(echo "scale=1; $source_size / 1048576" | bc -l 2>/dev/null || echo "unknown")
        source_size_human="${source_size_human}MB"
    else
        source_size_human=$(echo "scale=1; $source_size / 1024" | bc -l 2>/dev/null || echo "unknown")
        source_size_human="${source_size_human}KB"
    fi
    
    print_status "Source directory size: $source_size_human"
    
    # Check available space on target
    target_dir=$(dirname "$target_path")
    available_space=$(df -B1 "$target_dir" 2>/dev/null | tail -1 | awk '{print $4}' || echo "0")
    
    if [ "$available_space" -lt "$source_size" ]; then
        print_warning "Available space ($available_space bytes) may be insufficient"
        print_warning "Source size: $source_size bytes"
    else
        print_success "Sufficient disk space available"
    fi
}

# Function to run migration
run_migration() {
    local source_path="$1"
    local target_path="$2"
    local dry_run="$3"
    local verbose="$4"
    
    print_status "Starting migration process..."
    
    # Build command
    cmd="python3 comfyui_migration_tool.py \"$source_path\""
    
    if [ -n "$target_path" ]; then
        cmd="$cmd -t \"$target_path\""
    fi
    
    if [ "$dry_run" = "true" ]; then
        cmd="$cmd --dry-run"
        print_status "Running in DRY RUN mode (no files will be modified)"
    fi
    
    if [ "$verbose" = "true" ]; then
        cmd="$cmd --verbose"
    fi
    
    print_status "Executing: $cmd"
    echo ""
    
    # Run migration
    if eval "$cmd"; then
        if [ "$dry_run" = "true" ]; then
            print_success "Dry run completed successfully!"
        else
            print_success "Migration completed successfully!"
        fi
    else
        print_error "Migration failed!"
        exit 1
    fi
}

# Function to show post-migration instructions
show_post_migration_instructions() {
    local target_path="$1"
    
    echo ""
    echo "=========================================="
    echo "Migration completed! Next steps:"
    echo "=========================================="
    echo ""
    echo "1. Navigate to the target directory:"
    echo "   cd \"$target_path\""
    echo ""
    echo "2. Install system dependencies:"
    echo "   chmod +x install_dependencies.sh"
    echo "   ./install_dependencies.sh"
    echo ""
    echo "3. Install Python dependencies:"
    echo "   pip3 install -r requirements.txt"
    echo ""
    echo "4. Run ComfyUI:"
    echo "   chmod +x run_linux.sh"
    echo "   ./run_linux.sh"
    echo ""
    echo "5. Check the migration report:"
    echo "   cat migration_report.txt"
    echo ""
    echo "Note: You may need to adjust model paths in configuration files"
    echo "if your models are stored in different locations on Linux."
    echo ""
}

# Main script
main() {
    # Parse arguments
    source_path=""
    target_path=""
    dry_run=false
    verbose=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                dry_run=true
                shift
                ;;
            --verbose)
                verbose=true
                shift
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            -*)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
            *)
                if [ -z "$source_path" ]; then
                    source_path="$1"
                elif [ -z "$target_path" ]; then
                    target_path="$1"
                else
                    print_error "Too many arguments"
                    show_usage
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    # Check if source path is provided
    if [ -z "$source_path" ]; then
        print_error "Source path is required"
        show_usage
        exit 1
    fi
    
    # Set default target path if not provided
    if [ -z "$target_path" ]; then
        target_path="$HOME/ComfyUI"
    fi
    
    # Show migration plan
    echo "ComfyUI Migration Plan"
    echo "====================="
    echo "Source: $source_path"
    echo "Target: $target_path"
    echo "Dry Run: $dry_run"
    echo "Verbose: $verbose"
    echo ""
    
    # Check prerequisites
    check_prerequisites
    
    # Validate source path
    validate_source_path "$source_path"
    
    # Estimate disk space
    estimate_disk_space "$source_path" "$target_path"
    
    # Confirm migration
    if [ "$dry_run" = "false" ]; then
        echo ""
        read -p "Do you want to proceed with the migration? (y/N): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_status "Migration cancelled by user"
            exit 0
        fi
    fi
    
    # Run migration
    run_migration "$source_path" "$target_path" "$dry_run" "$verbose"
    
    # Show post-migration instructions
    if [ "$dry_run" = "false" ]; then
        show_post_migration_instructions "$target_path"
    fi
}

# Run main function with all arguments
main "$@"