#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
终极隐私补丁生成器
创建最全面的隐私保护补丁，拦截所有可能的数据收集点
"""

import re

def generate_ultimate_patch():
    """生成终极隐私保护补丁"""
    
    # 终极补丁代码 - 在文件开头插入全局拦截器
    ultimate_patch = '''
// ========== 终极隐私保护补丁 ==========
// 全局函数拦截器 - 拦截所有遥测相关函数

(function() {
    "use strict";
    
    console.log("[ULTIMATE PRIVACY PATCH] 已激活全面隐私保护");
    
    // 1. 拦截所有 reportEvent 调用
    const originalReportEvent = window.reportEvent || globalThis.reportEvent;
    if (typeof originalReportEvent === 'function') {
        window.reportEvent = globalThis.reportEvent = function(...args) {
            console.log("[BLOCKED] reportEvent 调用被拦截:", args[0]?.eventName || args[0]);
            return { success: true, blocked: true };
        };
    }
    
    // 2. 拦截所有 trackEvent 调用
    const originalTrackEvent = window.trackEvent || globalThis.trackEvent;
    if (typeof originalTrackEvent === 'function') {
        window.trackEvent = globalThis.trackEvent = function(...args) {
            console.log("[BLOCKED] trackEvent 调用被拦截:", args);
            return { success: true, blocked: true };
        };
    }
    
    // 3. 拦截 fetch 请求中的遥测数据
    const originalFetch = globalThis.fetch;
    if (originalFetch) {
        globalThis.fetch = function(url, options = {}) {
            const urlStr = typeof url === 'string' ? url : url.toString();
            
            // 检查是否为遥测相关请求
            if (/(telemetry|analytics|tracking|metrics|report|collect|usage|event)/i.test(urlStr)) {
                console.log("[BLOCKED] 遥测相关 fetch 请求被拦截:", urlStr);
                return Promise.resolve(new Response('{"success": true, "blocked": true}', {
                    status: 200,
                    headers: { 'Content-Type': 'application/json' }
                }));
            }
            
            // 检查请求体中的敏感数据
            if (options.body) {
                try {
                    const bodyStr = typeof options.body === 'string' ? options.body : JSON.stringify(options.body);
                    if (/(machineId|deviceId|sessionId|userId|clientId|fingerprint|userAgent)/i.test(bodyStr)) {
                        console.log("[BLOCKED] 包含敏感数据的请求被拦截");
                        return Promise.resolve(new Response('{"success": true, "sanitized": true}', {
                            status: 200,
                            headers: { 'Content-Type': 'application/json' }
                        }));
                    }
                } catch (e) {
                    // 忽略解析错误
                }
            }
            
            return originalFetch.call(this, url, options);
        };
    }
    
    // 4. 拦截 XMLHttpRequest
    const originalXHRSend = XMLHttpRequest.prototype.send;
    XMLHttpRequest.prototype.send = function(data) {
        if (data) {
            const dataStr = typeof data === 'string' ? data : JSON.stringify(data);
            if (/(telemetry|analytics|tracking|metrics|report|machineId|deviceId|sessionId)/i.test(dataStr)) {
                console.log("[BLOCKED] XMLHttpRequest 敏感数据被拦截");
                return;
            }
        }
        return originalXHRSend.call(this, data);
    };
    
    // 5. 拦截 navigator.userAgent 访问
    if (typeof navigator !== 'undefined') {
        Object.defineProperty(navigator, 'userAgent', {
            get: function() {
                console.log("[BLOCKED] navigator.userAgent 访问被拦截");
                return "";
            },
            configurable: false
        });
    }
    
    // 6. 拦截其他敏感信息访问
    const sensitiveNavigatorProps = ['platform', 'language', 'languages', 'vendor', 'product'];
    sensitiveNavigatorProps.forEach(prop => {
        if (typeof navigator !== 'undefined' && navigator[prop]) {
            Object.defineProperty(navigator, prop, {
                get: function() {
                    console.log(`[BLOCKED] navigator.${prop} 访问被拦截`);
                    return "";
                },
                configurable: false
            });
        }
    });
    
    // 7. 拦截屏幕信息访问
    if (typeof screen !== 'undefined') {
        ['width', 'height', 'availWidth', 'availHeight'].forEach(prop => {
            Object.defineProperty(screen, prop, {
                get: function() {
                    console.log(`[BLOCKED] screen.${prop} 访问被拦截`);
                    return 1920; // 返回通用值
                },
                configurable: false
            });
        });
    }
    
    // 8. 拦截时区信息
    if (typeof Intl !== 'undefined' && Intl.DateTimeFormat) {
        const originalResolvedOptions = Intl.DateTimeFormat.prototype.resolvedOptions;
        Intl.DateTimeFormat.prototype.resolvedOptions = function() {
            const options = originalResolvedOptions.call(this);
            if (options.timeZone) {
                console.log("[BLOCKED] 时区信息访问被拦截");
                options.timeZone = 'UTC';
            }
            return options;
        };
    }
    
    // 9. 拦截 crypto.getRandomValues (防止指纹生成)
    if (typeof crypto !== 'undefined' && crypto.getRandomValues) {
        const originalGetRandomValues = crypto.getRandomValues;
        crypto.getRandomValues = function(array) {
            console.log("[INTERCEPTED] crypto.getRandomValues 调用被监控");
            return originalGetRandomValues.call(this, array);
        };
    }
    
    console.log("[ULTIMATE PRIVACY PATCH] 全局拦截器设置完成");
})();

// ========== 原有补丁代码继续 ==========
'''
    
    return ultimate_patch

def create_enhanced_patch_manager():
    """创建增强的补丁管理器代码"""
    
    enhanced_code = '''
    def _generate_ultimate_privacy_patch(self) -> str:
        """生成终极隐私保护补丁"""
        return """
        // 终极隐私保护 - 全局拦截器
        (function() {
            const originalReportEvent = globalThis.reportEvent;
            if (originalReportEvent) {
                globalThis.reportEvent = function(...args) {
                    console.log("[ULTIMATE BLOCKED] reportEvent:", args[0]?.eventName);
                    return { success: true, blocked: true };
                };
            }
            
            // 拦截所有可能的遥测函数
            const telemetryFunctions = ['reportEvent', 'trackEvent', 'logEvent', 'sendTelemetry', 'collectMetrics'];
            telemetryFunctions.forEach(funcName => {
                if (typeof globalThis[funcName] === 'function') {
                    const original = globalThis[funcName];
                    globalThis[funcName] = function(...args) {
                        console.log(`[ULTIMATE BLOCKED] ${funcName}:`, args);
                        return { success: true, blocked: true };
                    };
                }
            });
            
            console.log("[ULTIMATE PRIVACY] 全局拦截器已激活");
        })();
        
        // 原有的 callApi 拦截继续...
        const endpoint = typeof s === "string" ? s : (typeof n === "string" ? n : (typeof r === "string" ? r : ""));
        
        if (endpoint && (endpoint.startsWith("report-") || endpoint.startsWith("record-") || /(telemetry|analytics|tracking|metrics|usage|fingerprint|event|log)/i.test(endpoint))) {
            console.log("[CALLAPI BLOCKED]", endpoint);
            return { success: true, blocked: true };
        }
        """.strip()
    '''
    
    print("📋 增强补丁管理器代码:")
    print(enhanced_code)
    
    return enhanced_code

def main():
    """主函数"""
    print("🛡️ 终极隐私补丁生成器")
    print("="*60)
    
    # 生成终极补丁
    ultimate_patch = generate_ultimate_patch()
    
    # 保存到文件
    with open("ultimate_privacy_patch.js", "w", encoding="utf-8") as f:
        f.write(ultimate_patch)
    
    print("✅ 终极隐私补丁已生成: ultimate_privacy_patch.js")
    
    # 生成增强的补丁管理器
    enhanced_manager = create_enhanced_patch_manager()
    
    print("\n💡 建议:")
    print("1. 将终极补丁代码集成到 PatchManager 中")
    print("2. 在文件开头插入全局拦截器")
    print("3. 同时保留 callApi 函数内的拦截")
    print("4. 测试所有遥测调用是否被有效拦截")

if __name__ == "__main__":
    main()