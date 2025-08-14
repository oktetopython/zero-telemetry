#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
遥测缺口分析工具
对比分析报告和当前补丁，识别遗漏的遥测点
"""

import re
import json
from pathlib import Path

class TelemetryGapAnalyzer:
    """遥测缺口分析器"""
    
    def __init__(self):
        self.extension_file = "extension.js"
        self.analysis_report = "extension_analysis_report.json"
        self.current_patches = self._load_current_patches()
        self.gaps_found = []
        
    def _load_current_patches(self):
        """加载当前的补丁模式"""
        return {
            'BLOCK': 'if (typeof s === "string" && (s.startsWith("report-") || s.startsWith("record-"))) { return { success: true }; }',
            'RANDOM': 'if (typeof s === "string" && (s.startsWith("report-") || s.startsWith("record-"))) { i = { timestamp: Date.now(), version: Math.random().toString(36).substring(2, 8) }; }',
            'EMPTY': 'if (typeof s === "string" && (s.startsWith("report-") || s.startsWith("record-"))) { i = {}; }',
            'STEALTH': 'if (typeof s === "string" && (s.startsWith("report-") || s.startsWith("record-"))) { i = { timestamp: Date.now(), session: Math.random().toString(36).substring(2, 10), events: [] }; }',
            'DEBUG': 'if (typeof s === "string" && (s.startsWith("report-") || s.startsWith("record-"))) { i = { timestamp: Date.now(), version: Math.random().toString(36).substring(2, 8) }; } if (typeof s === "string" && s === "subscription-info") { return { success: true, subscription: { Enterprise: {}, ActiveSubscription: { end_date: "2026-12-31", usage_balance_depleted: false } } }; } this.maxUploadSizeBytes = 999999999; this.maxTrackableFileCount = 999999; this.completionTimeoutMs = 999999; this.diffBudget = 999999; this.messageBudget = 999999; this.enableDebugFeatures = true;'
        }
    
    def analyze_current_coverage(self):
        """分析当前补丁的覆盖范围"""
        print("🔍 当前补丁覆盖范围分析")
        print("="*60)
        
        covered_patterns = []
        
        # 分析每个补丁模式覆盖的内容
        for mode, patch_code in self.current_patches.items():
            print(f"\n📋 {mode} 模式覆盖:")
            
            # 检查覆盖的API调用模式
            if 'startsWith("report-")' in patch_code:
                covered_patterns.append('report-*')
                print("  ✅ report-* API 调用")
            
            if 'startsWith("record-")' in patch_code:
                covered_patterns.append('record-*')
                print("  ✅ record-* API 调用")
            
            if 'subscription-info' in patch_code:
                covered_patterns.append('subscription-info')
                print("  ✅ subscription-info 查询")
            
            # 检查参数拦截
            if 'typeof s === "string"' in patch_code:
                print("  ✅ 字符串参数拦截")
            
            # 检查数据替换
            if 'i = {}' in patch_code:
                print("  ✅ 空数据替换")
            elif 'i = {' in patch_code:
                print("  ✅ 假数据替换")
            
            # 检查直接返回
            if 'return {' in patch_code:
                print("  ✅ 直接返回拦截")
        
        return covered_patterns
    
    def find_uncovered_telemetry_patterns(self):
        """查找未覆盖的遥测模式"""
        print("\n🚨 未覆盖遥测模式分析")
        print("="*60)
        
        if not Path(self.extension_file).exists():
            print("❌ extension.js 文件不存在")
            return
        
        with open(self.extension_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 定义需要检查的遥测模式
        telemetry_patterns = {
            # API 端点模式
            'api_endpoints': [
                r'"[^"]*telemetry[^"]*"',
                r'"[^"]*analytics[^"]*"',
                r'"[^"]*tracking[^"]*"',
                r'"[^"]*metrics[^"]*"',
                r'"[^"]*usage[^"]*"',
                r'"[^"]*log[^"]*"',
                r'"[^"]*event[^"]*"',
            ],
            
            # 函数调用模式
            'function_calls': [
                r'\.reportEvent\s*\(',
                r'\.reportTiming\s*\(',
                r'\.reportError\s*\(',
                r'\.trackUsage\s*\(',
                r'\.trackEvent\s*\(',
                r'\.logEvent\s*\(',
                r'\.sendTelemetry\s*\(',
                r'\.collectMetrics\s*\(',
            ],
            
            # 数据收集模式
            'data_collection': [
                r'navigator\.userAgent',
                r'navigator\.platform',
                r'navigator\.language',
                r'screen\.width',
                r'screen\.height',
                r'Date\.now\(\)',
                r'performance\.now\(\)',
                r'crypto\.getRandomValues',
            ],
            
            # 标识符生成
            'identifiers': [
                r'machineId\s*[:=]',
                r'deviceId\s*[:=]',
                r'sessionId\s*[:=]',
                r'userId\s*[:=]',
                r'clientId\s*[:=]',
                r'uuid\s*[:=]',
                r'guid\s*[:=]',
            ],
            
            # 网络请求
            'network_requests': [
                r'fetch\s*\([^)]*["\'][^"\']*(?:telemetry|analytics|tracking|metrics|usage|log|event)[^"\']*["\']',
                r'XMLHttpRequest\s*\(',
                r'\.send\s*\([^)]*(?:telemetry|analytics|tracking)',
            ]
        }
        
        uncovered_patterns = {}
        
        for category, patterns in telemetry_patterns.items():
            print(f"\n📊 {category.replace('_', ' ').title()}:")
            category_matches = []
            
            for pattern in patterns:
                matches = list(re.finditer(pattern, content, re.IGNORECASE))
                if matches:
                    category_matches.extend(matches)
                    print(f"  🔍 {pattern}: {len(matches)} 个匹配")
                    
                    # 显示前几个匹配的上下文
                    for i, match in enumerate(matches[:3]):
                        start = max(0, match.start() - 30)
                        end = min(len(content), match.end() + 30)
                        context = content[start:end].replace('\n', '\\n')
                        print(f"    📍 位置 {match.start()}: ...{context}...")
            
            if category_matches:
                uncovered_patterns[category] = category_matches
        
        return uncovered_patterns
    
    def analyze_callapi_parameters(self):
        """分析 callApi 函数的参数使用"""
        print("\n🎯 CallApi 参数分析")
        print("="*60)
        
        if not Path(self.extension_file).exists():
            return
        
        with open(self.extension_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找 callApi 函数
        callapi_pattern = r'async\s+callApi\s*\([^)]*\)\s*\{'
        matches = list(re.finditer(callapi_pattern, content))
        
        for i, match in enumerate(matches):
            print(f"\n🚀 CallApi 函数 #{i+1} 参数使用分析:")
            
            # 分析函数体中参数的使用
            func_start = match.end()
            # 尝试找到函数结束（简化版本，查找下一个函数或大段空白）
            func_end = min(func_start + 5000, len(content))  # 限制搜索范围
            func_body = content[func_start:func_end]
            
            # 提取参数名
            params_match = re.search(r'\(([^)]*)\)', match.group())
            if params_match:
                params_str = params_match.group(1)
                param_names = [p.strip().split('=')[0] for p in params_str.split(',') if p.strip()]
                
                print(f"  📋 参数列表: {param_names}")
                
                # 分析每个参数的使用
                for param in param_names:
                    if param and param != '':
                        # 查找参数在函数体中的使用
                        param_usage = len(re.findall(rf'\b{re.escape(param)}\b', func_body))
                        print(f"    📌 {param}: 使用 {param_usage} 次")
                        
                        # 查找参数相关的字符串操作
                        string_ops = re.findall(rf'{re.escape(param)}\.(?:startsWith|includes|indexOf|match)\s*\([^)]*\)', func_body)
                        if string_ops:
                            print(f"      🔍 字符串操作: {len(string_ops)} 次")
                            for op in string_ops[:3]:
                                print(f"        - {op}")
                
                # 检查我们的补丁是否覆盖了正确的参数
                print(f"\n  🎯 补丁覆盖分析:")
                if len(param_names) >= 3:
                    third_param = param_names[2] if len(param_names) > 2 else "未知"
                    print(f"    第3个参数 ({third_param}) - 我们的补丁检查: 's'")
                    if third_param != 's':
                        print(f"    ⚠️ 警告: 参数名不匹配! 实际: {third_param}, 补丁中: s")
                        self.gaps_found.append(f"CallApi #{i+1}: 参数名不匹配 ({third_param} vs s)")
    
    def check_fetch_and_xhr_coverage(self):
        """检查 fetch 和 XHR 请求的覆盖情况"""
        print("\n🌐 网络请求覆盖分析")
        print("="*60)
        
        if not Path(self.extension_file).exists():
            return
        
        with open(self.extension_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找所有网络请求
        network_patterns = {
            'fetch_calls': r'fetch\s*\([^)]*\)',
            'xhr_requests': r'new\s+XMLHttpRequest\s*\(\)',
            'xhr_send': r'\.send\s*\([^)]*\)',
            'websocket': r'new\s+WebSocket\s*\(',
        }
        
        for pattern_name, pattern in network_patterns.items():
            matches = list(re.finditer(pattern, content))
            print(f"\n📡 {pattern_name.replace('_', ' ').title()}: {len(matches)} 个")
            
            # 分析每个匹配的上下文，查找遥测相关内容
            telemetry_related = 0
            for match in matches:
                start = max(0, match.start() - 200)
                end = min(len(content), match.end() + 200)
                context = content[start:end].lower()
                
                # 检查上下文中是否包含遥测关键词
                telemetry_keywords = ['telemetry', 'analytics', 'tracking', 'metrics', 'usage', 'report', 'record', 'log', 'event']
                if any(keyword in context for keyword in telemetry_keywords):
                    telemetry_related += 1
            
            if telemetry_related > 0:
                print(f"  ⚠️ 其中 {telemetry_related} 个可能与遥测相关")
                print(f"  💡 建议: 考虑在这些网络请求中添加额外的拦截逻辑")
                self.gaps_found.append(f"{pattern_name}: {telemetry_related} 个潜在遥测请求未被拦截")
    
    def analyze_string_patterns(self):
        """分析字符串模式，查找遗漏的API端点"""
        print("\n🔤 字符串模式分析")
        print("="*60)
        
        if not Path(self.extension_file).exists():
            return
        
        with open(self.extension_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找可疑的字符串模式
        suspicious_patterns = {
            'api_paths': r'"[^"]*(?:/api/|/v\d+/)[^"]*(?:telemetry|analytics|tracking|metrics|usage|report|record|log|event)[^"]*"',
            'endpoint_names': r'"[^"]*(?:telemetry|analytics|tracking|metrics|usage)-[^"]*"',
            'action_names': r'"(?:report|record|track|log|send|collect)[A-Z][^"]*"',
            'data_keys': r'"(?:machineId|deviceId|sessionId|userId|clientId|uuid|guid|fingerprint)[^"]*"',
        }
        
        found_patterns = {}
        
        for pattern_name, pattern in suspicious_patterns.items():
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            if matches:
                found_patterns[pattern_name] = matches
                print(f"\n🔍 {pattern_name.replace('_', ' ').title()}: {len(matches)} 个")
                
                for match in matches[:5]:  # 显示前5个
                    matched_string = match.group()
                    print(f"  📝 {matched_string}")
                
                if len(matches) > 5:
                    print(f"  ... 还有 {len(matches) - 5} 个")
                
                # 检查这些模式是否被我们的补丁覆盖
                covered = False
                for matched_string in [m.group() for m in matches]:
                    if 'report-' in matched_string or 'record-' in matched_string:
                        covered = True
                        break
                
                if not covered:
                    print(f"  ⚠️ 警告: 这些模式可能未被当前补丁覆盖!")
                    self.gaps_found.append(f"{pattern_name}: {len(matches)} 个未覆盖的模式")
        
        return found_patterns
    
    def generate_enhanced_patches(self):
        """生成增强的补丁建议"""
        print("\n🛠️ 增强补丁建议")
        print("="*60)
        
        if not self.gaps_found:
            print("✅ 未发现明显的遥测缺口，当前补丁覆盖良好")
            return
        
        print("基于分析发现的缺口，建议以下增强:")
        
        # 生成更全面的补丁
        enhanced_patch = '''
        // 增强的遥测拦截补丁
        
        // 1. 拦截所有以 report-, record-, track-, log-, send-, collect- 开头的API调用
        if (typeof s === "string" && /^(report-|record-|track-|log-|send-|collect-)/.test(s)) {
            console.log("[TELEMETRY BLOCKED]", s);
            return { success: true, blocked: true };
        }
        
        // 2. 拦截包含遥测关键词的API调用
        if (typeof s === "string" && /(telemetry|analytics|tracking|metrics|usage|fingerprint)/i.test(s)) {
            console.log("[TELEMETRY BLOCKED]", s);
            return { success: true, blocked: true };
        }
        
        // 3. 拦截订阅和认证相关查询
        if (typeof s === "string" && /(subscription|auth|license|activation)/i.test(s)) {
            console.log("[AUTH INTERCEPTED]", s);
            return { 
                success: true, 
                subscription: { 
                    Enterprise: {}, 
                    ActiveSubscription: { 
                        end_date: "2026-12-31", 
                        usage_balance_depleted: false 
                    } 
                } 
            };
        }
        
        // 4. 清空或替换数据载荷
        if (typeof i === "object" && i !== null) {
            // 检查数据对象中的敏感字段
            const sensitiveFields = ['machineId', 'deviceId', 'sessionId', 'userId', 'clientId', 'uuid', 'guid', 'fingerprint', 'userAgent'];
            let hasSensitiveData = false;
            
            for (const field of sensitiveFields) {
                if (field in i) {
                    hasSensitiveData = true;
                    break;
                }
            }
            
            if (hasSensitiveData) {
                console.log("[DATA SANITIZED]", Object.keys(i));
                i = { timestamp: Date.now(), sanitized: true };
            }
        }
        '''
        
        print("📋 建议的增强补丁代码:")
        print(enhanced_patch)
        
        # 保存增强补丁到文件
        with open("enhanced_patch_suggestion.js", "w", encoding="utf-8") as f:
            f.write(enhanced_patch)
        
        print("\n💾 增强补丁已保存到: enhanced_patch_suggestion.js")
    
    def generate_gap_report(self):
        """生成缺口分析报告"""
        print("\n📋 遥测缺口分析报告")
        print("="*60)
        
        report = {
            "analysis_timestamp": __import__('datetime').datetime.now().isoformat(),
            "gaps_found": self.gaps_found,
            "recommendations": [
                "扩展补丁模式以覆盖更多API调用前缀",
                "添加对网络请求的额外拦截",
                "增强数据载荷的敏感字段检测",
                "考虑拦截 fetch() 和 XMLHttpRequest 调用",
                "添加对 WebSocket 连接的监控"
            ],
            "current_patch_coverage": [
                "report-* API 调用",
                "record-* API 调用", 
                "subscription-info 查询",
                "会话ID随机化",
                "用户代理清空"
            ]
        }
        
        # 保存报告
        with open("telemetry_gap_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📊 发现的潜在缺口: {len(self.gaps_found)}")
        for gap in self.gaps_found:
            print(f"  ⚠️ {gap}")
        
        print(f"\n✅ 完整报告已保存到: telemetry_gap_report.json")
        
        return report

def main():
    """主函数"""
    print("🔍 遥测缺口分析工具")
    print("="*60)
    
    analyzer = TelemetryGapAnalyzer()
    
    # 执行分析
    analyzer.analyze_current_coverage()
    analyzer.find_uncovered_telemetry_patterns()
    analyzer.analyze_callapi_parameters()
    analyzer.check_fetch_and_xhr_coverage()
    analyzer.analyze_string_patterns()
    analyzer.generate_enhanced_patches()
    analyzer.generate_gap_report()
    
    print(f"\n✅ 分析完成!")

if __name__ == "__main__":
    main()