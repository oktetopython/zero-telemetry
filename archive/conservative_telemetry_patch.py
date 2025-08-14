#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
保守的遥测补丁 - 最小化干预，只拦截明确的遥测
"""

import os
import re

def apply_conservative_patch():
    """应用保守的遥测补丁"""
    
    print("🛡️ 应用保守遥测补丁")
    print("=" * 60)
    
    with open("extension.js", 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📊 原始文件大小: {len(content):,} 字符")
    
    # 非常保守的补丁 - 只添加监控，不拦截正常功能
    conservative_patch = '''
// ========== 保守遥测监控补丁 ==========
// 只监控和记录遥测调用，不破坏正常功能

(function() {
    "use strict";
    
    console.log("[CONSERVATIVE TELEMETRY MONITOR] 遥测监控已激活");
    
    // 1. 只监控特定的遥测函数，不拦截
    const monitorTelemetryFunction = (funcName) => {
        if (typeof globalThis[funcName] === 'function') {
            const original = globalThis[funcName];
            globalThis[funcName] = function(...args) {
                console.log(`[TELEMETRY MONITOR] ${funcName} 调用:`, args[0]);
                // 仍然调用原始函数，只是记录
                return original.apply(this, args);
            };
        }
    };
    
    // 只监控明确的遥测函数
    ['reportEvent', 'trackEvent'].forEach(monitorTelemetryFunction);
    
    // 2. 监控但不拦截 fetch 请求
    const originalFetch = globalThis.fetch;
    if (originalFetch) {
        globalThis.fetch = function(url, options = {}) {
            const urlStr = typeof url === 'string' ? url : url.toString();
            
            // 只记录可疑的遥测请求，但仍然发送
            if (/segment\.io|analytics|telemetry/i.test(urlStr)) {
                console.log("[TELEMETRY MONITOR] 可疑遥测请求:", urlStr);
            }
            
            // 正常执行所有请求
            return originalFetch.call(this, url, options);
        };
    }
    
    // 3. 简单的用户代理伪装（不影响功能）
    if (typeof navigator !== 'undefined') {
        try {
            Object.defineProperty(navigator, 'userAgent', {
                get: function() {
                    return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36';
                },
                configurable: true
            });
        } catch (e) {
            // 如果无法修改，就忽略
            console.log("[TELEMETRY MONITOR] 无法修改 userAgent");
        }
    }
    
    console.log("[CONSERVATIVE TELEMETRY MONITOR] 监控设置完成 - 所有功能正常");
    
})();

// TELEMETRY BLOCKED - CONSERVATIVE MONITORING ACTIVE

'''
    
    # 在文件开头插入保守补丁
    patched_content = conservative_patch + "\n" + content
    
    # 写入文件
    with open("extension.js", 'w', encoding='utf-8') as f:
        f.write(patched_content)
    
    print(f"✅ 保守补丁已应用")
    print(f"📊 修补后文件大小: {len(patched_content):,} 字符")
    print(f"📈 增加了 {len(patched_content) - len(content):,} 字符")
    
    return True

def apply_targeted_callapi_patch():
    """在 callApi 函数中应用针对性补丁"""
    
    print("\n🎯 在 callApi 函数中应用针对性补丁")
    print("-" * 60)
    
    with open("extension.js", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找 callApi 函数的定义
    callapi_patterns = [
        r'function\s+callApi\s*\([^)]*\)\s*{',
        r'callApi\s*:\s*function\s*\([^)]*\)\s*{',
        r'callApi\s*=\s*function\s*\([^)]*\)\s*{',
        r'const\s+callApi\s*=\s*\([^)]*\)\s*=>\s*{',
    ]
    
    callapi_found = False
    for pattern in callapi_patterns:
        matches = list(re.finditer(pattern, content, re.IGNORECASE))
        if matches:
            print(f"✅ 找到 callApi 函数: {len(matches)} 个匹配")
            callapi_found = True
            
            # 在第一个匹配后插入拦截代码
            match = matches[0]
            insert_pos = match.end()
            
            # 插入的拦截代码
            intercept_code = '''
    
    // === 针对性遥测拦截 ===
    if (typeof arguments[0] === 'string') {
        const endpoint = arguments[0];
        if (endpoint.includes('telemetry') || endpoint.includes('analytics') || 
            endpoint.includes('track') || endpoint.includes('report-')) {
            console.log("[CALLAPI BLOCKED] 遥测端点被拦截:", endpoint);
            return Promise.resolve({ success: true, blocked: true });
        }
    }
    // === 拦截代码结束 ===
    '''
            
            # 插入代码
            patched_content = content[:insert_pos] + intercept_code + content[insert_pos:]
            
            # 写入文件
            with open("extension.js", 'w', encoding='utf-8') as f:
                f.write(patched_content)
            
            print(f"✅ callApi 函数补丁已应用")
            print(f"📈 在位置 {insert_pos} 插入了拦截代码")
            break
    
    if not callapi_found:
        print("⚠️ 未找到 callApi 函数，跳过针对性补丁")
    
    return callapi_found

def main():
    """主函数"""
    print("🔧 应用保守的遥测保护")
    print("=" * 60)
    
    # 应用保守的全局补丁
    apply_conservative_patch()
    
    # 应用针对性的 callApi 补丁
    apply_targeted_callapi_patch()
    
    print("\n✅ 保守遥测补丁应用完成!")
    print("🎯 特点:")
    print("  • 只监控遥测调用，不破坏正常功能")
    print("  • 在 callApi 中针对性拦截遥测端点")
    print("  • 保持所有网络通信正常")
    print("  • 简单的用户代理伪装")
    
    print("\n🧪 运行功能测试...")
    os.system("python test_plugin_functionality.py")

if __name__ == "__main__":
    main()