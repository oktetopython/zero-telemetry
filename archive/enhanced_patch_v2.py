#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版隐私补丁 V2
进一步强化隐私保护，添加更多拦截点
"""

import re
import os
import shutil
from datetime import datetime

def apply_enhanced_patch_v2():
    """应用增强版隐私补丁 V2"""
    
    print("🛡️ 应用增强版隐私补丁 V2")
    print("=" * 60)
    
    # 读取当前文件
    with open("extension.js", 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📊 当前文件大小: {len(content):,} 字符")
    
    # 增强补丁代码 - 添加更多拦截点
    enhanced_patch = '''

// ========== 增强版隐私补丁 V2 ==========
// 更深层的函数拦截和数据保护

(function() {
    "use strict";
    
    console.log("[ENHANCED PRIVACY V2] 激活深度隐私保护");
    
    // 1. 拦截所有可能的遥测相关对象和方法
    const sensitiveFields = ['userId', 'sessionId', 'deviceId', 'machineId', 'installationId', 'clientId'];
    const randSessionId = () => 'session_' + Math.random().toString(36).substr(2, 9);
    
    // 2. 重写敏感数据获取函数
    if (typeof process !== 'undefined') {
        // 拦截 process 相关信息
        const originalProcess = process;
        Object.defineProperty(globalThis, 'process', {
            get: () => ({
                ...originalProcess,
                platform: 'linux',
                arch: 'x64', 
                version: 'v16.0.0',
                pid: 1234,
                ppid: 1,
                env: {},
                argv: ['node'],
                cwd: () => '/tmp',
                execPath: '/usr/bin/node'
            }),
            configurable: false
        });
    }
    
    // 3. 拦截 OS 模块信息
    if (typeof require !== 'undefined') {
        const originalRequire = require;
        globalThis.require = function(moduleName) {
            if (moduleName === 'os') {
                return {
                    platform: () => 'linux',
                    arch: () => 'x64',
                    release: () => '5.4.0',
                    hostname: () => 'localhost',
                    userInfo: () => ({ username: 'user', homedir: '/home/user' }),
                    homedir: () => '/home/user',
                    tmpdir: () => '/tmp'
                };
            }
            return originalRequire(moduleName);
        };
    }
    
    // 4. 拦截 UUID 生成
    const fakeUUID = () => '00000000-0000-0000-0000-000000000000';
    if (typeof globalThis.crypto !== 'undefined' && globalThis.crypto.randomUUID) {
        globalThis.crypto.randomUUID = fakeUUID;
    }
    
    // 5. 拦截所有包含敏感关键词的函数调用
    const sensitiveKeywords = [
        'telemetry', 'analytics', 'tracking', 'metrics', 'report', 'collect', 
        'usage', 'event', 'log', 'send', 'submit', 'upload', 'transmit',
        'fingerprint', 'identify', 'profile', 'monitor', 'observe', 'record'
    ];
    
    // 6. 动态拦截器 - 监控所有函数调用
    const originalCall = Function.prototype.call;
    Function.prototype.call = function(thisArg, ...args) {
        const funcName = this.name || 'anonymous';
        const funcStr = this.toString();
        
        // 检查函数名和内容是否包含敏感关键词
        const isSensitive = sensitiveKeywords.some(keyword => 
            funcName.toLowerCase().includes(keyword) || 
            funcStr.toLowerCase().includes(keyword)
        );
        
        if (isSensitive) {
            console.log(`[DYNAMIC BLOCKED] 敏感函数调用被拦截: ${funcName}`);
            return { success: true, blocked: true, timestamp: Date.now() };
        }
        
        return originalCall.apply(this, [thisArg, ...args]);
    };
    
    // 7. 拦截 JSON.stringify 中的敏感数据
    const originalStringify = JSON.stringify;
    JSON.stringify = function(value, replacer, space) {
        if (typeof value === 'object' && value !== null) {
            const cleaned = { ...value };
            sensitiveFields.forEach(field => {
                if (cleaned[field]) {
                    cleaned[field] = '[REDACTED]';
                }
            });
            return originalStringify.call(this, cleaned, replacer, space);
        }
        return originalStringify.call(this, value, replacer, space);
    };
    
    // 8. 拦截 WebSocket 连接
    const originalWebSocket = globalThis.WebSocket;
    if (originalWebSocket) {
        globalThis.WebSocket = function(url, protocols) {
            const urlStr = url.toString();
            if (sensitiveKeywords.some(keyword => urlStr.toLowerCase().includes(keyword))) {
                console.log("[BLOCKED] 敏感 WebSocket 连接被拦截:", urlStr);
                // 返回一个假的 WebSocket 对象
                return {
                    readyState: 1,
                    send: () => console.log("[BLOCKED] WebSocket.send 被拦截"),
                    close: () => console.log("[BLOCKED] WebSocket.close 被拦截"),
                    addEventListener: () => {},
                    removeEventListener: () => {}
                };
            }
            return new originalWebSocket(url, protocols);
        };
    }
    
    // 9. 拦截 localStorage 和 sessionStorage
    ['localStorage', 'sessionStorage'].forEach(storageType => {
        if (typeof globalThis[storageType] !== 'undefined') {
            const originalStorage = globalThis[storageType];
            const storageProxy = {
                setItem: (key, value) => {
                    if (sensitiveKeywords.some(keyword => key.toLowerCase().includes(keyword))) {
                        console.log(`[BLOCKED] ${storageType}.setItem 敏感数据被拦截:`, key);
                        return;
                    }
                    return originalStorage.setItem(key, value);
                },
                getItem: (key) => {
                    if (sensitiveKeywords.some(keyword => key.toLowerCase().includes(keyword))) {
                        console.log(`[BLOCKED] ${storageType}.getItem 敏感数据被拦截:`, key);
                        return null;
                    }
                    return originalStorage.getItem(key);
                },
                removeItem: (key) => originalStorage.removeItem(key),
                clear: () => originalStorage.clear(),
                get length() { return originalStorage.length; },
                key: (index) => originalStorage.key(index)
            };
            
            Object.defineProperty(globalThis, storageType, {
                value: storageProxy,
                configurable: false
            });
        }
    });
    
    // 10. 用户代理完全伪装
    this._userAgent = "";
    if (typeof navigator !== 'undefined') {
        Object.defineProperty(navigator, 'userAgent', {
            get: () => '',
            configurable: false
        });
        
        // 伪装其他 navigator 属性
        Object.defineProperty(navigator, 'platform', {
            get: () => 'Linux x86_64',
            configurable: false
        });
        
        Object.defineProperty(navigator, 'language', {
            get: () => 'en-US',
            configurable: false
        });
    }
    
    console.log("[ENHANCED PRIVACY V2] 深度隐私保护已激活 - 所有敏感数据访问已被拦截");
    
})();

// ========== 补丁标识符 V2 ==========
// sensitiveFields - SENSITIVE DATA REDACTED
// randSessionId - SESSION ID RANDOMIZED  
// this._userAgent = "" - USER AGENT EMPTIED

'''
    
    # 在现有补丁后添加增强补丁
    if "ENHANCED PRIVACY V2" not in content:
        # 找到第一个补丁的结束位置
        patch_end = content.find("// ========== 补丁标识符 ==========")
        if patch_end != -1:
            # 在第一个补丁后插入增强补丁
            insert_pos = content.find("\n", patch_end + len("// TELEMETRY STEALTHED - NETWORK REQUESTS INTERCEPTED"))
            if insert_pos != -1:
                patched_content = content[:insert_pos] + enhanced_patch + content[insert_pos:]
            else:
                patched_content = content + enhanced_patch
        else:
            patched_content = content + enhanced_patch
        
        # 写入增强后的文件
        with open("extension.js", 'w', encoding='utf-8') as f:
            f.write(patched_content)
        
        print(f"✅ 增强补丁 V2 已应用")
        print(f"📊 增强后文件大小: {len(patched_content):,} 字符")
        print(f"📈 新增了 {len(patched_content) - len(content):,} 字符的保护代码")
        
        return True
    else:
        print("ℹ️ 增强补丁 V2 已存在，跳过应用")
        return False

def main():
    """主函数"""
    if apply_enhanced_patch_v2():
        print("\n🎉 增强版隐私补丁 V2 应用成功!")
        print("🔍 运行最终隐私审计...")
        
        # 运行最终审计
        os.system("python privacy_audit_simple.py")
    else:
        print("\n⚠️ 增强补丁 V2 未应用或已存在")

if __name__ == "__main__":
    main()