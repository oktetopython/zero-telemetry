#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度隐私分析工具
检查补丁后的文件是否还有隐私泄露风险
"""

import re

def analyze_patched_file():
    """分析已补丁的文件"""
    ext_path = r'C:\Users\pestxo\.vscode\extensions\augment.vscode-augment-0.527.1\out\extension.js'
    
    print("🔍 深度隐私分析 - 已补丁文件")
    print("="*60)
    
    try:
        with open(ext_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"✅ 文件加载成功: {len(content):,} 字符")
        
        # 1. 检查补丁代码位置和内容
        print("\n🛡️ 补丁代码分析:")
        
        # 查找补丁插入位置
        patch_markers = [
            'const endpoint = typeof s',
            'TELEMETRY DEBUG',
            'sensitiveFields'
        ]
        
        for marker in patch_markers:
            pos = content.find(marker)
            if pos != -1:
                print(f"  ✅ 找到补丁标记: {marker} (位置: {pos})")
                # 显示补丁代码上下文
                start = max(0, pos - 50)
                end = min(len(content), pos + 200)
                context = content[start:end].replace('\n', '\\n')
                print(f"     上下文: ...{context}...")
            else:
                print(f"  ❌ 未找到补丁标记: {marker}")
        
        # 2. 分析 reportEvent 调用是否被拦截
        print("\n📡 reportEvent 调用分析:")
        report_events = list(re.finditer(r'reportEvent\s*\([^)]*\)', content))
        
        print(f"  发现 {len(report_events)} 个 reportEvent 调用")
        
        # 检查这些调用是否在补丁保护范围内
        protected_calls = 0
        unprotected_calls = 0
        
        for i, match in enumerate(report_events[:10]):  # 检查前10个
            call_pos = match.start()
            
            # 查找最近的 callApi 函数
            before_text = content[max(0, call_pos - 2000):call_pos]
            callapi_matches = list(re.finditer(r'async\s+callApi\s*\([^)]*\)\s*\{', before_text))
            
            if callapi_matches:
                # 找到最近的 callApi 函数
                nearest_callapi = callapi_matches[-1]
                callapi_start = call_pos - 2000 + nearest_callapi.end()
                
                # 检查这个 callApi 函数是否有我们的补丁
                callapi_body = content[callapi_start:callapi_start + 1000]
                
                if 'const endpoint = typeof s' in callapi_body or 'TELEMETRY DEBUG' in callapi_body:
                    protected_calls += 1
                    print(f"    ✅ 调用 #{i+1} (位置 {call_pos}): 受补丁保护")
                else:
                    unprotected_calls += 1
                    print(f"    ⚠️ 调用 #{i+1} (位置 {call_pos}): 可能未受保护")
            else:
                print(f"    ❓ 调用 #{i+1} (位置 {call_pos}): 无法确定保护状态")
        
        print(f"  📊 保护状态: {protected_calls} 个受保护, {unprotected_calls} 个可能未保护")
        
        # 3. 检查敏感字段是否被处理
        print("\n🔒 敏感字段处理分析:")
        
        sensitive_fields = ['machineId', 'deviceId', 'sessionId', 'userId', 'clientId']
        
        for field in sensitive_fields:
            field_matches = list(re.finditer(rf'\b{field}\b', content))
            print(f"  📊 {field}: {len(field_matches)} 次使用")
            
            # 检查是否在补丁保护的上下文中
            protected_usage = 0
            for match in field_matches[:5]:  # 检查前5个使用
                pos = match.start()
                context = content[max(0, pos - 200):pos + 200]
                
                if 'sensitiveFields' in context or 'stealth-' in context or 'debug-' in context:
                    protected_usage += 1
            
            if protected_usage > 0:
                print(f"    ✅ 其中 {protected_usage} 个使用受到补丁保护")
        
        # 4. 检查网络请求是否被拦截
        print("\n🌐 网络请求分析:")
        
        fetch_calls = list(re.finditer(r'fetch\s*\([^)]*\)', content))
        print(f"  发现 {len(fetch_calls)} 个 fetch 调用")
        
        # 检查是否有遥测相关的 URL
        telemetry_urls = []
        for match in fetch_calls[:10]:
            start = max(0, match.start() - 100)
            end = min(len(content), match.end() + 100)
            context = content[start:end]
            
            telemetry_keywords = ['telemetry', 'analytics', 'tracking', 'metrics', 'report']
            if any(keyword in context.lower() for keyword in telemetry_keywords):
                telemetry_urls.append(match.start())
        
        if telemetry_urls:
            print(f"  ⚠️ 发现 {len(telemetry_urls)} 个可能的遥测相关请求")
        else:
            print(f"  ✅ 未发现明显的遥测相关请求")
        
        # 5. 检查用户代理访问
        print("\n🕵️ 用户代理访问分析:")
        
        ua_matches = list(re.finditer(r'navigator\.userAgent', content))
        print(f"  发现 {len(ua_matches)} 个 navigator.userAgent 访问")
        
        # 检查是否被我们的补丁清空
        ua_cleared = 0
        for match in ua_matches:
            pos = match.start()
            context = content[max(0, pos - 500):pos + 500]
            
            if 'this._userAgent = ""' in context:
                ua_cleared += 1
        
        print(f"  ✅ 其中 {ua_cleared} 个访问被补丁清空")
        
        # 6. 总体风险评估
        print("\n🎯 总体隐私风险评估:")
        
        risk_score = 0
        
        if unprotected_calls > 0:
            risk_score += unprotected_calls * 10
            print(f"  🔴 未保护的 reportEvent 调用: +{unprotected_calls * 10} 风险分")
        
        if len(telemetry_urls) > 0:
            risk_score += len(telemetry_urls) * 5
            print(f"  🟡 可疑的网络请求: +{len(telemetry_urls) * 5} 风险分")
        
        if ua_cleared < len(ua_matches):
            uncovered_ua = len(ua_matches) - ua_cleared
            risk_score += uncovered_ua * 3
            print(f"  🟡 未清空的用户代理访问: +{uncovered_ua * 3} 风险分")
        
        print(f"\n📊 总风险评分: {risk_score}")
        
        if risk_score == 0:
            print("🎉 优秀！未发现明显的隐私泄露风险")
        elif risk_score < 20:
            print("✅ 良好！隐私保护基本到位，风险较低")
        elif risk_score < 50:
            print("⚠️ 中等！存在一些隐私风险，建议进一步优化")
        else:
            print("🚨 高风险！存在严重的隐私泄露风险，需要立即处理")
        
        return risk_score
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        return -1

if __name__ == "__main__":
    analyze_patched_file()