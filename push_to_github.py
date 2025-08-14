#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub 推送脚本
自动推送项目到 GitHub 仓库
"""

import os
import subprocess
import sys

def run_command(command, description):
    """运行命令并显示结果"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} 成功")
            if result.stdout.strip():
                print(f"   输出: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} 失败")
            if result.stderr.strip():
                print(f"   错误: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} 异常: {e}")
        return False

def check_git_status():
    """检查 Git 状态"""
    print("🔍 检查 Git 状态...")
    
    # 检查是否有未提交的更改
    result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        print("⚠️ 发现未提交的更改:")
        print(result.stdout)
        return False
    
    print("✅ 所有更改已提交")
    return True

def main():
    """主函数"""
    print("🚀 GitHub 推送脚本")
    print("=" * 50)
    
    print("📋 推送前检查清单:")
    print("1. ✅ 已在 GitHub 创建 zero-telemetry 仓库")
    print("2. ✅ 仓库设置为 Public")
    print("3. ✅ 未添加 README、.gitignore 或 LICENSE")
    
    confirm = input("\n以上条件都满足了吗? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("\n📝 请先完成以下步骤:")
        print("1. 访问 https://github.com/oktetopython")
        print("2. 点击 'New repository'")
        print("3. 仓库名: zero-telemetry")
        print("4. 描述: 🛡️ Zero Telemetry - Advanced Privacy Protection Toolkit")
        print("5. 设置为 Public")
        print("6. 不要勾选任何额外选项")
        print("7. 点击 'Create repository'")
        print("\n完成后重新运行此脚本")
        return
    
    # 检查 Git 状态
    if not check_git_status():
        print("❌ Git 状态检查失败，请先提交所有更改")
        return
    
    # 推送到 GitHub
    print(f"\n🚀 开始推送到 GitHub...")
    
    success = run_command(
        "git push -u origin main",
        "推送到 GitHub"
    )
    
    if success:
        print(f"\n🎉 推送成功!")
        print(f"📍 仓库地址: https://github.com/oktetopython/zero-telemetry")
        print(f"📚 README 预览: https://github.com/oktetopython/zero-telemetry#readme")
        
        print(f"\n💡 后续建议:")
        print(f"1. 访问仓库页面检查内容")
        print(f"2. 设置仓库描述和标签")
        print(f"3. 启用 Issues 和 Discussions")
        print(f"4. 分享给需要隐私保护的用户")
        
    else:
        print(f"\n❌ 推送失败")
        print(f"💡 可能的原因:")
        print(f"1. GitHub 仓库尚未创建")
        print(f"2. 网络连接问题")
        print(f"3. 认证问题")
        
        print(f"\n🔧 解决方案:")
        print(f"1. 确认已创建 zero-telemetry 仓库")
        print(f"2. 检查网络连接")
        print(f"3. 配置 GitHub 认证 (Personal Access Token)")

if __name__ == "__main__":
    main()