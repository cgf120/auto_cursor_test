#!/usr/bin/env python3
"""
ComfyUI Complete Migration Tool
===============================

主控制脚本，整合所有ComfyUI迁移工具，提供完整的迁移解决方案。
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

class ComfyUIMigrationController:
    def __init__(self, source_dir: str, target_dir: str):
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        
        # 迁移工具脚本
        self.migration_tools = {
            'main': 'comfyui_migration_tool.py',
            'config': 'comfyui_config_migrator.py',
            'model': 'comfyui_model_migrator.py'
        }
    
    def check_prerequisites(self) -> bool:
        """检查迁移前置条件"""
        print("🔍 检查迁移前置条件...")
        
        # 检查源目录
        if not self.source_dir.exists():
            print(f"❌ 源目录不存在: {self.source_dir}")
            return False
        
        # 检查目标目录
        if not self.target_dir.exists():
            print(f"📁 创建目标目录: {self.target_dir}")
            self.target_dir.mkdir(parents=True, exist_ok=True)
        
        # 检查Python环境
        try:
            result = subprocess.run(['python3', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ Python3未安装")
                return False
            print(f"✅ Python版本: {result.stdout.strip()}")
        except Exception as e:
            print(f"❌ 检查Python环境失败: {e}")
            return False
        
        # 检查必要的Python包
        required_packages = ['yaml', 'pathlib']
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ {package} 已安装")
            except ImportError:
                print(f"❌ {package} 未安装，尝试安装...")
                try:
                    subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                                 check=True)
                    print(f"✅ {package} 安装成功")
                except Exception as e:
                    print(f"❌ 安装 {package} 失败: {e}")
                    return False
        
        # 检查迁移工具脚本
        for tool_name, script_name in self.migration_tools.items():
            script_path = Path(script_name)
            if not script_path.exists():
                print(f"❌ 迁移工具脚本不存在: {script_name}")
                return False
            print(f"✅ 迁移工具脚本存在: {script_name}")
        
        print("✅ 前置条件检查通过")
        return True
    
    def run_migration_tool(self, tool_name: str, args: List[str]) -> bool:
        """运行指定的迁移工具"""
        script_name = self.migration_tools.get(tool_name)
        if not script_name:
            print(f"❌ 未知的迁移工具: {tool_name}")
            return False
        
        script_path = Path(script_name)
        if not script_path.exists():
            print(f"❌ 迁移工具脚本不存在: {script_name}")
            return False
        
        try:
            cmd = [sys.executable, str(script_path)] + args
            print(f"🚀 运行 {tool_name} 迁移工具...")
            print(f"📋 命令: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, check=True)
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            print(f"❌ 运行 {tool_name} 迁移工具失败: {e}")
            return False
        except Exception as e:
            print(f"❌ 运行 {tool_name} 迁移工具出错: {e}")
            return False
    
    def estimate_migration_size(self) -> Dict[str, str]:
        """估算迁移大小"""
        print("📊 估算迁移大小...")
        
        # 估算模型文件大小
        model_args = [str(self.source_dir), str(self.target_dir), '--estimate-only']
        self.run_migration_tool('model', model_args)
        
        # 计算目录大小
        total_size = 0
        file_count = 0
        
        try:
            for root, dirs, files in os.walk(self.source_dir):
                for file in files:
                    file_path = Path(root) / file
                    try:
                        total_size += file_path.stat().st_size
                        file_count += 1
                    except Exception:
                        pass
        except Exception as e:
            print(f"⚠️  计算目录大小失败: {e}")
        
        size_gb = total_size / (1024**3)
        
        return {
            'total_size': f"{size_gb:.2f} GB",
            'file_count': str(file_count),
            'source_dir': str(self.source_dir),
            'target_dir': str(self.target_dir)
        }
    
    def create_migration_plan(self) -> Dict:
        """创建迁移计划"""
        print("📋 创建迁移计划...")
        
        plan = {
            'source_dir': str(self.source_dir),
            'target_dir': str(self.target_dir),
            'steps': [
                {
                    'name': '前置条件检查',
                    'description': '检查Python环境、依赖包、迁移工具等',
                    'tool': 'prerequisites'
                },
                {
                    'name': '配置文件迁移',
                    'description': '迁移ComfyUI配置文件，更新路径设置',
                    'tool': 'config'
                },
                {
                    'name': '模型文件迁移',
                    'description': '迁移模型文件，包括checkpoints、loras等',
                    'tool': 'model'
                },
                {
                    'name': '主程序迁移',
                    'description': '迁移ComfyUI主程序文件，设置Python环境',
                    'tool': 'main'
                }
            ],
            'estimated_size': self.estimate_migration_size()
        }
        
        return plan
    
    def execute_migration_plan(self, plan: Dict, skip_steps: List[str] = None) -> Dict[str, bool]:
        """执行迁移计划"""
        if skip_steps is None:
            skip_steps = []
        
        results = {}
        
        print("🚀 开始执行迁移计划...")
        
        for step in plan['steps']:
            step_name = step['name']
            tool_name = step['tool']
            
            if step_name in skip_steps:
                print(f"⏭️  跳过步骤: {step_name}")
                results[step_name] = True
                continue
            
            print(f"\n📋 执行步骤: {step_name}")
            print(f"📝 描述: {step['description']}")
            
            if tool_name == 'prerequisites':
                results[step_name] = self.check_prerequisites()
            elif tool_name in self.migration_tools:
                args = [str(self.source_dir), str(self.target_dir)]
                results[step_name] = self.run_migration_tool(tool_name, args)
            else:
                print(f"⚠️  未知的工具: {tool_name}")
                results[step_name] = False
            
            if results[step_name]:
                print(f"✅ 步骤完成: {step_name}")
            else:
                print(f"❌ 步骤失败: {step_name}")
                if not self.ask_continue():
                    break
        
        return results
    
    def ask_continue(self) -> bool:
        """询问是否继续执行"""
        while True:
            response = input("\n❓ 是否继续执行后续步骤? (y/n): ").lower().strip()
            if response in ['y', 'yes', '是']:
                return True
            elif response in ['n', 'no', '否']:
                return False
            else:
                print("请输入 y 或 n")
    
    def create_final_report(self, plan: Dict, results: Dict[str, bool]) -> bool:
        """创建最终迁移报告"""
        try:
            report_content = "# ComfyUI完整迁移报告\n\n"
            report_content += f"## 迁移信息\n"
            report_content += f"- 源目录: {plan['source_dir']}\n"
            report_content += f"- 目标目录: {plan['target_dir']}\n"
            report_content += f"- 估算大小: {plan['estimated_size']['total_size']}\n"
            report_content += f"- 文件数量: {plan['estimated_size']['file_count']}\n\n"
            
            report_content += f"## 执行结果\n"
            successful_steps = 0
            total_steps = len(results)
            
            for step_name, success in results.items():
                status = "✅ 成功" if success else "❌ 失败"
                report_content += f"- {step_name}: {status}\n"
                if success:
                    successful_steps += 1
            
            report_content += f"\n**统计**: {successful_steps}/{total_steps} 步骤成功\n"
            report_content += f"**成功率**: {(successful_steps/total_steps*100):.1f}%\n\n"
            
            if successful_steps == total_steps:
                report_content += "## 🎉 迁移成功完成！\n\n"
                report_content += "### 下一步操作\n"
                report_content += "1. 检查目标目录中的文件\n"
                report_content += "2. 验证配置文件路径设置\n"
                report_content += "3. 测试ComfyUI启动\n"
                report_content += "4. 检查自定义节点功能\n\n"
                
                report_content += "### 启动ComfyUI\n"
                report_content += f"```bash\n"
                report_content += f"cd {plan['target_dir']}\n"
                report_content += f"./start_comfyui.sh\n"
                report_content += f"```\n\n"
            else:
                report_content += "## ⚠️ 迁移部分完成\n\n"
                report_content += "### 需要手动处理的步骤\n"
                for step_name, success in results.items():
                    if not success:
                        report_content += f"- {step_name}\n"
                report_content += "\n"
            
            report_content += "## 常见问题解决\n"
            report_content += "1. **权限问题**: 运行 `chmod +x start_comfyui.sh`\n"
            report_content += "2. **模型加载失败**: 检查模型文件路径配置\n"
            report_content += "3. **依赖问题**: 重新安装Python依赖包\n"
            report_content += "4. **自定义节点问题**: 检查节点依赖安装\n"
            report_content += "5. **路径问题**: 更新配置文件中的路径设置\n"
            
            report_path = self.target_dir / "COMPLETE_MIGRATION_REPORT.md"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            print(f"✅ 创建最终迁移报告: {report_path}")
            return True
            
        except Exception as e:
            print(f"❌ 创建最终迁移报告失败: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='ComfyUI Complete Migration Tool')
    parser.add_argument('source_dir', help='Windows ComfyUI安装目录')
    parser.add_argument('target_dir', help='Linux目标目录')
    parser.add_argument('--dry-run', action='store_true', help='仅显示迁移计划，不实际执行')
    parser.add_argument('--skip-steps', nargs='+', help='跳过的步骤名称')
    parser.add_argument('--estimate-only', action='store_true', help='仅估算迁移大小')
    
    args = parser.parse_args()
    
    controller = ComfyUIMigrationController(args.source_dir, args.target_dir)
    
    if args.estimate_only:
        size_info = controller.estimate_migration_size()
        print(f"\n📊 迁移大小估算:")
        print(f"总大小: {size_info['total_size']}")
        print(f"文件数量: {size_info['file_count']}")
        return
    
    # 创建迁移计划
    plan = controller.create_migration_plan()
    
    if args.dry_run:
        print("🔍 预览模式 - 迁移计划:")
        print(f"源目录: {plan['source_dir']}")
        print(f"目标目录: {plan['target_dir']}")
        print(f"估算大小: {plan['estimated_size']['total_size']}")
        print(f"文件数量: {plan['estimated_size']['file_count']}")
        print("\n执行步骤:")
        for i, step in enumerate(plan['steps'], 1):
            print(f"{i}. {step['name']}: {step['description']}")
        return
    
    # 执行迁移
    results = controller.execute_migration_plan(plan, args.skip_steps)
    
    # 创建最终报告
    controller.create_final_report(plan, results)
    
    # 显示结果
    successful_steps = sum(1 for success in results.values() if success)
    total_steps = len(results)
    
    print(f"\n🎉 迁移完成！")
    print(f"📊 成功步骤: {successful_steps}/{total_steps}")
    print(f"📈 成功率: {(successful_steps/total_steps*100):.1f}%")
    
    if successful_steps == total_steps:
        print(f"\n✅ 所有步骤执行成功！")
        print(f"📁 目标目录: {args.target_dir}")
        print(f"🚀 启动命令: cd {args.target_dir} && ./start_comfyui.sh")
    else:
        print(f"\n⚠️  部分步骤失败，请查看迁移报告了解详情。")

if __name__ == "__main__":
    main()