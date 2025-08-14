#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试插件功能是否正常
"""

import re

def test_plugin_functionality():
    """测试插件核心功能是否被保留"""
    
    print("🧪 测试插件功能完整性")
    print("=" * 60)
    
    with open("extension.js", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查核心功能是否被保留
    core_functions = {
        'API调用功能': [
            r'fetch\s*\(',
            r'XMLHttpRequest',
            r'callApi',
            r'request\s*\(',
        ],
        'WebSocket通信': [
            r'WebSocket',
            r'ws://',
            r'wss://',
        ],
        '文件操作': [
            r'readFile',
            r'writeFile',
            r'fs\.',
        ],
        '事件处理': [
            r'addEventListener',
            r'on\w+\s*:',
            r'emit\s*\(',
        ],
        '扩展激活': [
            r'activate\s*\(',
            r'deactivate\s*\(',
            r'vscode\.',
        ]
    }
    
    print("🔍 检查核心功能保留情况:")
    
    all_functions_preserved = True
    
    for category, patterns in core_functions.items():
        print(f"\n📋 {category}:")
        category_preserved = False
        
        for pattern in patterns:
            matches = len(re.findall(pattern, content, re.IGNORECASE))
            if matches > 0:
                print(f"  ✅ {pattern}: {matches} 个匹配")
                category_preserved = True
            else:
                print(f"  ❌ {pattern}: 未找到")
        
        if category_preserved:
            print(f"  🎯 {category}: 功能保留")
        else:
            print(f"  ⚠️ {category}: 可能受影响")
            all_functions_preserved = False
    
    # 检查是否有过度拦截
    print(f"\n🔍 检查过度拦截情况:")
    
    # 检查我们的补丁是否过于激进
    aggressive_patterns = [
        r'globalThis\.fetch\s*=.*return.*blocked',
        r'XMLHttpRequest.*=.*blocked',
        r'WebSocket.*=.*blocked',
    ]
    
    over_blocking = False
    for pattern in aggressive_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
        if matches:
            print(f"  ⚠️ 发现可能的过度拦截: {pattern}")
            over_blocking = True
    
    if not over_blocking:
        print("  ✅ 未发现过度拦截")
    
    # 检查精确拦截是否生效
    print(f"\n🎯 检查精确遥测拦截:")
    
    telemetry_blocks = [
        r'TELEMETRY BLOCKED',
        r'reportEvent.*blocked',
        r'trackEvent.*blocked',
        r'segment\.io.*blocked',
    ]
    
    telemetry_protected = False
    for pattern in telemetry_blocks:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            print(f"  ✅ 遥测拦截生效: {len(matches)} 个")
            telemetry_protected = True
    
    # 总结
    print(f"\n📊 功能测试总结:")
    print(f"  核心功能保留: {'✅ 是' if all_functions_preserved else '❌ 否'}")
    print(f"  过度拦截检查: {'❌ 发现问题' if over_blocking else '✅ 正常'}")
    print(f"  遥测拦截生效: {'✅ 是' if telemetry_protected else '❌ 否'}")
    
    if all_functions_preserved and not over_blocking and telemetry_protected:
        print(f"\n🎉 插件功能测试通过！")
        return True
    else:
        print(f"\n⚠️ 插件功能可能存在问题")
        return False

def main():
    """主函数"""
    success = test_plugin_functionality()
    
    if success:
        print("\n✅ 插件应该可以正常工作了")
        print("💡 建议:")
        print("  1. 重启 VSCode")
        print("  2. 测试插件的核心功能")
        print("  3. 检查控制台是否有遥测拦截日志")
    else:
        print("\n❌ 插件可能仍有问题，需要进一步调整")

if __name__ == "__main__":
    main()