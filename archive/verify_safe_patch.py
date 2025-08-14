#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证安全补丁 - 确认补丁不会破坏正常功能
"""

import re

def verify_safe_patch():
    """验证补丁是否安全"""
    
    print("🔍 验证补丁安全性")
    print("=" * 60)
    
    with open("extension.js", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查补丁特征
    print("📋 检查补丁特征:")
    
    # 1. 检查是否只是监控而不拦截
    monitoring_patterns = [
        r'console\.log.*TELEMETRY MONITOR',
        r'return original\.apply\(this, args\)',
        r'return originalFetch\.call\(this, url, options\)',
    ]
    
    monitoring_found = 0
    for pattern in monitoring_patterns:
        matches = len(re.findall(pattern, content, re.IGNORECASE))
        if matches > 0:
            print(f"  ✅ 监控模式: {pattern} - {matches} 个")
            monitoring_found += 1
        else:
            print(f"  ❌ 监控模式: {pattern} - 未找到")
    
    # 2. 检查是否有破坏性拦截
    blocking_patterns = [
        r'return.*blocked.*true',
        r'return Promise\.resolve.*blocked',
        r'throw.*blocked',
    ]
    
    blocking_found = 0
    for pattern in blocking_patterns:
        matches = len(re.findall(pattern, content, re.IGNORECASE))
        if matches > 0:
            print(f"  ⚠️ 拦截模式: {pattern} - {matches} 个")
            blocking_found += 1
    
    # 3. 检查核心功能保留
    print(f"\n📋 核心功能检查:")
    
    essential_functions = [
        (r'fetch\s*\(', 'Fetch API'),
        (r'XMLHttpRequest', 'XHR'),
        (r'WebSocket', 'WebSocket'),
        (r'callApi', 'API调用'),
        (r'vscode\.', 'VSCode API'),
    ]
    
    functions_ok = 0
    for pattern, name in essential_functions:
        matches = len(re.findall(pattern, content, re.IGNORECASE))
        if matches > 0:
            print(f"  ✅ {name}: {matches} 个引用")
            functions_ok += 1
        else:
            print(f"  ❌ {name}: 未找到")
    
    # 4. 检查补丁标识
    print(f"\n📋 补丁标识检查:")
    
    patch_signatures = [
        'CONSERVATIVE TELEMETRY MONITOR',
        'TELEMETRY BLOCKED',
    ]
    
    signatures_found = 0
    for signature in patch_signatures:
        if signature in content:
            print(f"  ✅ 找到标识: {signature}")
            signatures_found += 1
        else:
            print(f"  ❌ 未找到标识: {signature}")
    
    # 总结
    print(f"\n📊 安全性评估:")
    print(f"  监控功能: {monitoring_found}/3 ({'✅ 正常' if monitoring_found >= 2 else '⚠️ 不完整'})")
    print(f"  破坏性拦截: {blocking_found} ({'⚠️ 存在' if blocking_found > 0 else '✅ 无'})")
    print(f"  核心功能: {functions_ok}/{len(essential_functions)} ({'✅ 完整' if functions_ok == len(essential_functions) else '⚠️ 不完整'})")
    print(f"  补丁标识: {signatures_found}/{len(patch_signatures)} ({'✅ 完整' if signatures_found == len(patch_signatures) else '⚠️ 不完整'})")
    
    # 最终判断
    is_safe = (monitoring_found >= 2 and 
               blocking_found == 0 and 
               functions_ok == len(essential_functions) and 
               signatures_found >= 1)
    
    if is_safe:
        print(f"\n🎉 补丁安全性验证通过!")
        print(f"✅ 插件应该可以正常工作")
        print(f"🔍 补丁只会监控遥测调用，不会破坏正常功能")
    else:
        print(f"\n⚠️ 补丁可能存在问题")
        if blocking_found > 0:
            print(f"❌ 发现破坏性拦截，可能影响正常功能")
        if functions_ok < len(essential_functions):
            print(f"❌ 核心功能可能受影响")
    
    return is_safe

def main():
    """主函数"""
    is_safe = verify_safe_patch()
    
    if is_safe:
        print(f"\n💡 使用建议:")
        print(f"  1. 重启 VSCode")
        print(f"  2. 测试插件功能是否正常")
        print(f"  3. 打开开发者控制台查看遥测监控日志")
        print(f"  4. 如果看到 '[TELEMETRY MONITOR]' 日志，说明监控生效")
        print(f"  5. 如果插件功能正常，说明补丁成功")
    else:
        print(f"\n🔧 如果插件仍有问题:")
        print(f"  1. 可以恢复原始文件: copy extension_backup_*.js extension.js")
        print(f"  2. 或者尝试更轻量的补丁")

if __name__ == "__main__":
    main()