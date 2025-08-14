#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
精确遥测补丁 - 只拦截遥测，不影响正常功能
"""

import os
import shutil
from datetime import datetime

def apply_precise_telemetry_patch():
    """应用精确的遥测补丁，不影响正常功能"""
    
    print("🎯 应用精确遥测补丁")
    print("=" * 60)
    
    # 读取原始文件
    with open("extension.js", 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📊 原始文件大小: {len(content):,} 字符")
    
    # 精确的遥测拦截补丁 - 只针对明确的遥测调用
    precise_patch = '''
// ========== 精确遥测拦截补丁 ==========
// 只拦截明确的遥测调用，保护正常功能

(function() {
    "use strict";
    
    console.log("[PRECISE TELEMETRY PATCH] 精确遥测拦截已激活");
    
    // 1. 只拦截明确的遥测函数名
    const telemetryFunctionNames = [
        'reportEvent', 'trackEvent', 'logTelemetry', 'sendTelemetry',
        'collectTelemetry', 'recordTelemetry', 'submitTelemetry'
    ];
    
    telemetryFunctionNames.forEach(funcName => {
        if (typeof globalThis[funcName] === 'function') {
            const original = globalThis[funcName];
            globalThis[funcName] = function(...args) {
                console.log(`[TELEMETRY BLOCKED] ${funcName} 调用被拦截:`, args[0]);
                return { success: true, telemetryBlocked: true };
            };
        }
    });
    
    // 2. 只拦截明确包含遥测关键词的 URL
    const originalFetch = globalThis.fetch;
    if (originalFetch) {
        globalThis.fetch = function(url, options = {}) {
            const urlStr = typeof url === 'string' ? url : url.toString();
            
            // 只拦截明确的遥测域名和路径
            const telemetryPatterns = [
                /segment\.io.*\/track/i,
                /analytics\..*\/collect/i,
                /telemetry\..*\/report/i,
                /.*\/telemetry\//i,
                /.*\/analytics\//i,
                /.*\/tracking\//i
            ];
            
            const isTelemetryRequest = telemetryPatterns.some(pattern => pattern.test(urlStr));
            
            if (isTelemetryRequest) {
                console.log("[TELEMETRY BLOCKED] 遥测请求被拦截:", urlStr);
                return Promise.resolve(new Response('{"success": true, "blocked": true}', {
                    status: 200,
                    headers: { 'Content-Type': 'application/json' }
                }));
            }
            
            // 允许所有其他请求正常通过
            return originalFetch.call(this, url, options);
        };
    }
    
    // 3. 只拦截明确的遥测相关 XMLHttpRequest
    const originalXHROpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function(method, url, ...args) {
        // 只拦截明确的遥测 URL
        const telemetryPatterns = [
            /segment\.io.*\/track/i,
            /analytics\..*\/collect/i,
            /telemetry\..*\/report/i
        ];
        
        const isTelemetryUrl = telemetryPatterns.some(pattern => pattern.test(url));
        
        if (isTelemetryUrl) {
            console.log("[TELEMETRY BLOCKED] XHR 遥测请求被拦截:", url);
            // 创建假的成功响应
            setTimeout(() => {
                Object.defineProperty(this, 'readyState', { value: 4 });
                Object.defineProperty(this, 'status', { value: 200 });
                Object.defineProperty(this, 'responseText', { value: '{"success": true}' });
                if (this.onreadystatechange) this.onreadystatechange();
            }, 1);
            return;
        }
        
        // 允许所有其他请求正常通过
        return originalXHROpen.call(this, method, url, ...args);
    };
    
    // 4. 只伪装用户代理，不影响其他功能
    if (typeof navigator !== 'undefined') {
        const originalUserAgent = navigator.userAgent;
        Object.defineProperty(navigator, 'userAgent', {
            get: function() {
                // 返回一个通用的用户代理，而不是空字符串
                return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36';
            },
            configurable: true
        });
    }
    
    console.log("[PRECISE TELEMETRY PATCH] 精确拦截完成 - 正常功能不受影响");
    
})();

// ========== 补丁标识符 ==========
// TELEMETRY BLOCKED - PRECISE INTERCEPTION
// NORMAL FUNCTIONS PRESERVED

'''
    
    # 在文件开头插入精确补丁
    patched_content = precise_patch + "\n" + content
    
    # 写入修补后的文件
    with open("extension.js", 'w', encoding='utf-8') as f:
        f.write(patched_content)
    
    print(f"✅ 精确补丁已应用")
    print(f"📊 修补后文件大小: {len(patched_content):,} 字符")
    print(f"📈 增加了 {len(patched_content) - len(content):,} 字符的保护代码")
    
    return True

def main():
    """主函数"""
    print("🔧 修复过度拦截问题")
    print("=" * 60)
    
    if apply_precise_telemetry_patch():
        print("\n✅ 精确遥测补丁应用成功!")
        print("🎯 现在只拦截明确的遥测调用，正常功能不受影响")
        print("🔍 运行验证测试...")
        
        # 运行验证
        os.system("python privacy_audit_simple.py")
    else:
        print("\n❌ 补丁应用失败")

if __name__ == "__main__":
    main()