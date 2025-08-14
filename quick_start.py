#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速开始脚本
一键完成隐私保护的完整流程
"""

import os
import sys
import time

def print_banner():
    """打印横幅"""
    print("🛡️" + "=" * 60 + "🛡️")
    print("    VSCode Augment 隐私保护工具 - 快速开始")
    print("🛡️" + "=" * 60 + "🛡️")

def check_requirements():
    """检查环境要求"""
    print("\n🔍 检查环境要求...")
    
    # 检查 Python 版本
    if sys.version_info < (3, 7):
        print("❌ Python 版本过低，需要 Python 3.7+")
        return False
    
    print(f"✅ Python 版本: {sys.version.split()[0]}")
    
    # 检查扩展文件
    if not os.path.exists("extension.js"):
        print("❌ 未找到 extension.js 文件")
        print("💡 请将 VSCode Augment 扩展的 extension.js 文件复制到当前目录")
        print("📍 扩展文件位置:")
        print("   Windows: %USERPROFILE%\\.vscode\\extensions\\augment.vscode-augment-*\\out\\extension.js")
        print("   macOS: ~/.vscode/extensions/augment.vscode-augment-*/out/extension.js")
        print("   Linux: ~/.vscode/extensions/augment.vscode-augment-*/out/extension.js")
        return False
    
    print("✅ 找到 extension.js 文件")
    
    # 检查核心工具
    required_tools = [
        "smart_js_analyzer.py",
        "evidence_based_patch_generator.py", 
        "evidence_patch_verifier.py",
        "simple_patch_monitor.py"
    ]
    
    for tool in required_tools:
        if not os.path.exists(tool):
            print(f"❌ 缺少核心工具: {tool}")
            return False
    
    print("✅ 所有核心工具就绪")
    return True

def run_step(step_name, command, description):
    """运行步骤"""
    print(f"\n{'='*60}")
    print(f"📋 步骤: {step_name}")
    print(f"📝 说明: {description}")
    print(f"🔧 命令: {command}")
    print(f"{'='*60}")
    
    input("按 Enter 继续...")
    
    try:
        result = os.system(command)
        if result == 0:
            print(f"✅ {step_name} 完成")
            return True
        else:
            print(f"❌ {step_name} 失败 (退出码: {result})")
            return False
    except Exception as e:
        print(f"❌ {step_name} 异常: {e}")
        return False

def main():
    """主函数"""
    print_banner()
    
    # 检查环境
    if not check_requirements():
        print("\n❌ 环境检查失败，请解决上述问题后重试")
        input("按 Enter 退出...")
        return
    
    print("\n🎯 准备开始隐私保护流程...")
    print("📋 流程包括:")
    print("  1. 智能分析扩展代码")
    print("  2. 应用基于证据的补丁")
    print("  3. 验证补丁效果")
    print("  4. 启动监控系统")
    
    proceed = input("\n是否继续? (y/N): ").strip().lower()
    if proceed not in ['y', 'yes']:
        print("取消操作")
        return
    
    # 执行步骤
    steps = [
        {
            "name": "智能代码分析",
            "command": "python smart_js_analyzer.py",
            "description": "深度分析扩展代码，识别核心功能和隐私威胁"
        },
        {
            "name": "应用隐私补丁", 
            "command": "python evidence_based_patch_generator.py",
            "description": "基于分析结果应用精确的隐私保护补丁"
        },
        {
            "name": "验证补丁效果",
            "command": "python evidence_patch_verifier.py", 
            "description": "全面验证补丁应用效果和保护程度"
        }
    ]
    
    success_count = 0
    for i, step in enumerate(steps, 1):
        print(f"\n🚀 开始第 {i}/{len(steps)} 步...")
        
        if run_step(step["name"], step["command"], step["description"]):
            success_count += 1
        else:
            print(f"\n⚠️ 第 {i} 步失败，是否继续?")
            continue_choice = input("继续 (y) 或 退出 (N): ").strip().lower()
            if continue_choice not in ['y', 'yes']:
                break
    
    # 总结
    print(f"\n{'='*60}")
    print("📊 流程总结")
    print(f"{'='*60}")
    print(f"✅ 成功完成: {success_count}/{len(steps)} 个步骤")
    
    if success_count == len(steps):
        print("🎉 隐私保护流程全部完成!")
        print("\n💡 下一步:")
        print("  1. 将 extension.js 部署回扩展目录")
        print("  2. 重启 VSCode")
        print("  3. 测试扩展功能")
        print("  4. 运行日常监控")
        
        print(f"\n🔧 部署命令示例:")
        print(f"  # 备份原文件")
        print(f"  cp \"扩展路径/extension.js\" \"扩展路径/extension.js.backup\"")
        print(f"  # 部署补丁文件")
        print(f"  cp ./extension.js \"扩展路径/extension.js\"")
        
        print(f"\n👁️ 日常监控:")
        print(f"  python simple_patch_monitor.py")
        
    elif success_count > 0:
        print("⚠️ 部分步骤完成，建议检查失败的步骤")
    else:
        print("❌ 所有步骤都失败了，请检查环境和文件")
    
    print(f"\n📚 更多帮助:")
    print(f"  • 查看 README.md 获取详细说明")
    print(f"  • 查看 docs/ 目录获取技术文档")
    print(f"  • 查看 reports/ 目录获取分析报告")
    
    input("\n按 Enter 退出...")

if __name__ == "__main__":
    main()