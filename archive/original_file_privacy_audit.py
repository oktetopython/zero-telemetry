#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
原始文件隐私审计工具
全面检查项目目录中的原始 extension.js 文件，识别所有隐私收集点
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

class OriginalFilePrivacyAuditor:
    """原始文件隐私审计器"""
    
    def __init__(self):
        self.extension_file = "extension.js"  # 项目目录中的原始文件
        self.content = ""
        self.privacy_risks = []
        self.telemetry_points = []
        
    def load_original_file(self):
        """加载原始文件"""
        try:
            with open(self.extension_file, 'r', encoding='utf-8') as f:
                self.content = f.read()
            print(f"✅ 已加载原始文件: {len(self.content):,} 字符")
            return True
        except Exception as e:
            print(f"❌ 文件加载失败: {e}")
            return False
    
    def find_all_callapi_functions(self):
        """查找所有 callApi 函数"""
        print("\n" + "="*60)
        print("🎯 CallApi 函数全面分析")
        print("="*60)
        
        # 查找所有可能的 callApi 函数变体
        callapi_patterns = [
            r'async\s+callApi\s*\([^)]*\)\s*\{',
            r'callApi\s*:\s*async\s*\([^)]*\)\s*=>\s*\{',
            r'callApi\s*=\s*async\s*\([^)]*\)\s*=>\s*\{',
            r'\.callApi\s*=\s*async\s*\([^)]*\)\s*=>\s*\{',
        ]
        
        all_callapi_functions = []
        
        for i, pattern in enumerate(callapi_patterns):
            matches = list(re.finditer(pattern, self.content))
            if matches:
                print(f"\\n📋 模式 #{i+1}: {pattern}")
                print(f"   找到 {len(matches)} 个匹配")
                
                for j, match in enumerate(matches):
                    print(f"\\n🚀 CallApi 函数 #{len(all_callapi_functions)+1}:")
                    print(f"   📍 位置: {match.start()}-{match.end()}")
                    print(f"   🔤 签名: {match.group()}")
                    
                    # 分析参数
                    params_match = re.search(r'\\(([^)]*)\\)', match.group())
                    if params_match:
                        params = params_match.group(1)
                        param_list = [p.strip() for p in params.split(',') if p.strip()]
                        print(f"   📋 参数数量: {len(param_list)}")
                        print(f"   📝 参数列表: {param_list}")
                        
                        # 分析第3个参数（通常是端点参数）
                        if len(param_list) >= 3:
                            third_param = param_list[2].split('=')[0].strip()
                            print(f"   🎯 第3个参数 (端点): {third_param}")
                        
                        all_callapi_functions.append({
                            'position': match.start(),
                            'signature': match.group(),
                            'parameters': param_list,
                            'third_param': param_list[2].split('=')[0].strip() if len(param_list) >= 3 else None
                        })
        
        print(f"\\n📊 总计找到 {len(all_callapi_functions)} 个 callApi 函数")
        return all_callapi_functions
    
    def analyze_telemetry_patterns(self):
        """分析遥测模式"""
        print("\\n" + "="*60)
        print("📡 遥测模式全面分析")
        print("="*60)
        
        # 定义所有可能的遥测模式
        telemetry_patterns = {
            # API 端点前缀
            'api_prefixes': [
                r'"report-[^"]*"',
                r'"record-[^"]*"',
                r'"track-[^"]*"',
                r'"log-[^"]*"',
                r'"send-[^"]*"',
                r'"collect-[^"]*"',
                r'"analytics-[^"]*"',
                r'"telemetry-[^"]*"',
                r'"metrics-[^"]*"',
                r'"usage-[^"]*"'
            ],
            
            # 遥测关键词
            'telemetry_keywords': [
                r'\\btelemetry\\b',
                r'\\banalytics\\b', 
                r'\\btracking\\b',
                r'\\bmetrics\\b',
                r'\\busage\\b',
                r'\\bfingerprint\\b',
                r'\\bevent\\b',
                r'\\breport\\b',
                r'\\brecord\\b'
            ],
            
            # 函数调用
            'function_calls': [
                r'\\.reportEvent\\s*\\(',
                r'\\.reportError\\s*\\(',
                r'\\.reportTiming\\s*\\(',
                r'\\.trackEvent\\s*\\(',
                r'\\.trackUsage\\s*\\(',
                r'\\.logEvent\\s*\\(',
                r'\\.sendTelemetry\\s*\\(',
                r'\\.collectMetrics\\s*\\('
            ],
            
            # 数据收集
            'data_collection': [
                r'navigator\\.userAgent',
                r'navigator\\.platform',
                r'navigator\\.language',
                r'screen\\.(width|height)',
                r'Date\\.now\\(\\)',
                r'performance\\.now\\(\\)',
                r'crypto\\.getRandomValues'
            ],
            
            # 标识符
            'identifiers': [
                r'machineId\\s*[:=]',
                r'deviceId\\s*[:=]',
                r'sessionId\\s*[:=]',
                r'userId\\s*[:=]',
                r'clientId\\s*[:=]',
                r'uuid\\s*[:=]',
                r'guid\\s*[:=]'
            ]
        }
        
        total_risks = 0
        
        for category, patterns in telemetry_patterns.items():
            print(f"\\n📋 {category.replace('_', ' ').title()}:")
            category_risks = []
            
            for pattern in patterns:
                matches = list(re.finditer(pattern, self.content, re.IGNORECASE))
                if matches:
                    print(f"  🚨 {pattern}: {len(matches)} 个匹配")
                    total_risks += len(matches)
                    
                    # 显示前3个匹配的上下文
                    for match in matches[:3]:
                        start = max(0, match.start() - 50)
                        end = min(len(self.content), match.end() + 50)
                        context = self.content[start:end].replace('\\n', '\\\\n')
                        print(f"    📍 位置 {match.start()}: ...{context[:80]}...")
                        
                        category_risks.append({
                            'pattern': pattern,
                            'position': match.start(),
                            'match': match.group(),
                            'context': context[:100]
                        })
                else:
                    print(f"  ✅ {pattern}: 无匹配")
            
            if category_risks:
                self.privacy_risks.extend(category_risks)
        
        print(f"\\n📊 发现的隐私风险点: {total_risks}")
        return total_risks
    
    def analyze_network_requests(self):
        """分析网络请求"""
        print("\\n" + "="*60)
        print("🌐 网络请求分析")
        print("="*60)
        
        network_patterns = {
            'fetch_requests': r'fetch\\s*\\([^)]*\\)',
            'xhr_requests': r'new\\s+XMLHttpRequest\\s*\\(\\)',
            'websocket_connections': r'new\\s+WebSocket\\s*\\(',
            'beacon_requests': r'navigator\\.sendBeacon\\s*\\(',
            'post_messages': r'\\.postMessage\\s*\\('
        }
        
        total_network_calls = 0
        
        for pattern_name, pattern in network_patterns.items():
            matches = list(re.finditer(pattern, self.content))
            if matches:
                print(f"\\n🔍 {pattern_name.replace('_', ' ').title()}: {len(matches)} 个")
                total_network_calls += len(matches)
                
                # 分析每个网络请求的上下文
                telemetry_related = 0
                for match in matches[:5]:
                    start = max(0, match.start() - 200)
                    end = min(len(self.content), match.end() + 200)
                    context = self.content[start:end].lower()
                    
                    # 检查是否与遥测相关
                    telemetry_keywords = ['telemetry', 'analytics', 'tracking', 'metrics', 'usage', 'report', 'event', 'log']
                    if any(keyword in context for keyword in telemetry_keywords):
                        telemetry_related += 1
                        print(f"  🚨 位置 {match.start()}: 可能的遥测请求")
                    else:
                        print(f"  ℹ️ 位置 {match.start()}: 常规网络请求")
                
                if telemetry_related > 0:
                    print(f"  ⚠️ 其中 {telemetry_related} 个可能与遥测相关")
        
        print(f"\\n📊 网络请求总数: {total_network_calls}")
        return total_network_calls
    
    def check_data_structures(self):
        """检查数据结构"""
        print("\\n" + "="*60)
        print("📊 数据结构分析")
        print("="*60)
        
        # 查找包含敏感信息的对象结构
        sensitive_object_patterns = [
            r'\\{[^}]*(?:machineId|deviceId|sessionId|userId|clientId)[^}]*\\}',
            r'\\{[^}]*(?:fingerprint|userAgent|platform)[^}]*\\}',
            r'\\{[^}]*(?:analytics|telemetry|tracking)[^}]*\\}',
            r'\\{[^}]*(?:metrics|usage|stats)[^}]*\\}',
            r'\\{[^}]*(?:timestamp|time|date)[^}]*\\}'
        ]
        
        total_sensitive_objects = 0
        
        for pattern in sensitive_object_patterns:
            matches = list(re.finditer(pattern, self.content, re.IGNORECASE))
            if matches:
                print(f"🔍 {pattern}: {len(matches)} 个匹配")
                total_sensitive_objects += len(matches)
                
                for match in matches[:3]:
                    obj_content = match.group()
                    print(f"  📊 位置 {match.start()}: {obj_content[:60]}...")
        
        return total_sensitive_objects
    
    def generate_patch_requirements(self, callapi_functions):
        """生成补丁需求"""
        print("\\n" + "="*60)
        print("🛠️ 补丁需求分析")
        print("="*60)
        
        print("基于分析结果，我们的补丁需要覆盖:")
        
        # 分析每个 callApi 函数的参数名
        unique_param_names = set()
        for func in callapi_functions:
            if func['third_param']:
                unique_param_names.add(func['third_param'])
        
        print(f"\\n🎯 需要支持的端点参数名: {list(unique_param_names)}")
        
        # 检查我们当前的补丁是否覆盖了所有参数名
        from augment_tools_core.patch_manager import PatchManager
        pm = PatchManager()
        
        # 检查 DEBUG 模式补丁
        debug_patch = pm.patches[pm.PatchMode.DEBUG] if hasattr(pm, 'patches') else ""
        
        print("\\n📋 当前补丁覆盖检查:")
        for param_name in unique_param_names:
            if f'typeof {param_name} ===' in debug_patch:
                print(f"  ✅ 参数 '{param_name}': 已覆盖")
            else:
                print(f"  ❌ 参数 '{param_name}': 未覆盖")
        
        # 生成完整的补丁建议
        param_check_code = " || ".join([f'(typeof {param} === "string" ? {param} : "")' for param in unique_param_names])
        
        comprehensive_patch = f'''
        // 全面参数兼容补丁
        const endpoint = {param_check_code};
        
        // 1. 拦截所有遥测相关API调用
        if (endpoint && /^(report-|record-|track-|log-|send-|collect-|analytics-|telemetry-|metrics-|usage-)/.test(endpoint)) {{
            console.log("[TELEMETRY BLOCKED]", endpoint);
            return {{ success: true, blocked: true }};
        }}
        
        // 2. 拦截包含遥测关键词的调用
        if (endpoint && /(telemetry|analytics|tracking|metrics|usage|fingerprint|event|log|report|record)/i.test(endpoint)) {{
            console.log("[TELEMETRY BLOCKED]", endpoint);
            return {{ success: true, blocked: true }};
        }}
        
        // 3. 拦截订阅和认证查询
        if (endpoint && /(subscription|auth|license|activation|billing)/i.test(endpoint)) {{
            console.log("[AUTH INTERCEPTED]", endpoint);
            return {{ 
                success: true, 
                subscription: {{ 
                    Enterprise: {{}}, 
                    ActiveSubscription: {{ 
                        end_date: "2026-12-31", 
                        usage_balance_depleted: false 
                    }} 
                }} 
            }};
        }}
        
        // 4. 清理敏感数据字段
        if (typeof i === "object" && i !== null) {{
            const sensitiveFields = ["machineId", "deviceId", "sessionId", "userId", "clientId", "uuid", "guid", "fingerprint", "userAgent", "platform", "language", "timezone"];
            let hasSensitive = false;
            for (const field of sensitiveFields) {{
                if (field in i) {{
                    i[field] = "blocked-" + Math.random().toString(36).substring(2, 10);
                    hasSensitive = true;
                }}
            }}
            if (hasSensitive) {{
                console.log("[DATA SANITIZED]", Object.keys(i));
            }}
        }}
        
        // 5. 会话和身份随机化
        const chars = "0123456789abcdef";
        let randSessionId = "";
        for (let idx = 0; idx < 36; idx++) {{
            randSessionId += idx === 8 || idx === 13 || idx === 18 || idx === 23 ? "-" : 
                           idx === 14 ? "4" : 
                           idx === 19 ? chars[8 + Math.floor(4 * Math.random())] : 
                           chars[Math.floor(16 * Math.random())];
        }}
        this.sessionId = randSessionId;
        this._userAgent = "";
        
        // 6. 功能增强和限制移除
        this.maxUploadSizeBytes = 999999999;
        this.maxTrackableFileCount = 999999;
        this.completionTimeoutMs = 999999;
        this.diffBudget = 999999;
        this.messageBudget = 999999;
        this.enableDebugFeatures = true;
        '''
        
        print("\\n💾 建议的全面补丁:")
        print(comprehensive_patch[:500] + "...")
        
        # 保存完整补丁
        with open("comprehensive_patch_recommendation.js", "w", encoding="utf-8") as f:
            f.write(comprehensive_patch)
        
        print("\\n✅ 完整补丁已保存到: comprehensive_patch_recommendation.js")
        
        return comprehensive_patch
    
    def audit_all_privacy_risks(self):
        """审计所有隐私风险"""
        print("\\n" + "="*60)
        print("🚨 全面隐私风险审计")
        print("="*60)
        
        # 定义所有隐私风险模式
        risk_categories = {
            # 设备指纹
            'device_fingerprinting': [
                r'navigator\\.userAgent',
                r'navigator\\.platform', 
                r'navigator\\.language',
                r'navigator\\.languages',
                r'navigator\\.hardwareConcurrency',
                r'screen\\.(width|height|availWidth|availHeight|colorDepth)',
                r'window\\.devicePixelRatio',
                r'canvas\\.getContext',
                r'WebGL'
            ],
            
            # 系统信息
            'system_info': [
                r'process\\.platform',
                r'process\\.arch',
                r'process\\.version',
                r'os\\.(platform|arch|release|version|hostname)',
                r'require\\(["\']os["\']\\)'
            ],
            
            # 时间和位置
            'temporal_location': [
                r'Date\\.now\\(\\)',
                r'new Date\\(\\)',
                r'performance\\.now\\(\\)',
                r'Intl\\.DateTimeFormat',
                r'timezone',
                r'locale',
                r'navigator\\.geolocation'
            ],
            
            # 唯一标识符
            'unique_identifiers': [
                r'machineId',
                r'deviceId', 
                r'sessionId',
                r'userId',
                r'clientId',
                r'uuid',
                r'guid',
                r'fingerprint',
                r'crypto\\.randomUUID',
                r'Math\\.random\\(\\)'
            ],
            
            # 网络和存储
            'network_storage': [
                r'localStorage\\.',
                r'sessionStorage\\.',
                r'indexedDB\\.',
                r'document\\.cookie',
                r'fetch\\s*\\(',
                r'XMLHttpRequest',
                r'WebSocket',
                r'navigator\\.sendBeacon'
            ],
            
            # 用户行为追踪
            'behavior_tracking': [
                r'addEventListener\\s*\\(["\'](?:click|keydown|keyup|mousedown|mouseup|scroll|resize|focus|blur)["\']',
                r'onclick\\s*=',
                r'onkeydown\\s*=',
                r'onscroll\\s*=',
                r'visibilitychange'
            ]
        }
        
        total_risk_count = 0
        high_risk_items = []
        
        for category, patterns in risk_categories.items():
            print(f"\\n📋 {category.replace('_', ' ').title()}:")
            category_count = 0
            
            for pattern in patterns:
                matches = list(re.finditer(pattern, self.content, re.IGNORECASE))
                if matches:
                    category_count += len(matches)
                    print(f"  🚨 {pattern}: {len(matches)} 个")
                    
                    # 标记高风险项目
                    if any(high_risk in pattern for high_risk in ['machineId', 'deviceId', 'userAgent', 'fingerprint']):
                        high_risk_items.extend(matches)
                else:
                    print(f"  ✅ {pattern}: 无")
            
            total_risk_count += category_count
            print(f"  📊 {category} 小计: {category_count} 个风险点")
        
        print(f"\\n🎯 隐私风险总计: {total_risk_count}")
        print(f"🔴 高风险项目: {len(high_risk_items)}")
        
        return total_risk_count, high_risk_items
    
    def compare_with_current_patches(self):
        """与当前补丁进行对比"""
        print("\\n" + "="*60)
        print("🔍 补丁覆盖对比分析")
        print("="*60)
        
        try:
            from augment_tools_core.patch_manager import PatchManager, PatchMode
            pm = PatchManager()
            
            print("当前补丁模式分析:")
            for mode in PatchMode:
                patch_code = pm.patches[mode]
                print(f"\\n📋 {mode.value.upper()} 模式:")
                
                # 检查参数兼容性
                if 'typeof s ===' in patch_code and 'typeof n ===' in patch_code:
                    print("  ✅ 多参数兼容")
                elif 'typeof s ===' in patch_code:
                    print("  ⚠️ 仅支持参数 's'")
                else:
                    print("  ❌ 参数支持不明")
                
                # 检查关键词覆盖
                keywords_covered = []
                telemetry_keywords = ['telemetry', 'analytics', 'tracking', 'metrics', 'usage', 'fingerprint', 'event', 'log']
                for keyword in telemetry_keywords:
                    if keyword in patch_code.lower():
                        keywords_covered.append(keyword)
                
                print(f"  📊 覆盖关键词: {len(keywords_covered)}/{len(telemetry_keywords)}")
                if keywords_covered:
                    print(f"     {', '.join(keywords_covered)}")
                
                # 检查敏感字段处理
                if 'sensitiveFields' in patch_code:
                    print("  ✅ 敏感字段处理")
                else:
                    print("  ❌ 无敏感字段处理")
                
                # 检查功能增强
                if 'maxUploadSizeBytes' in patch_code:
                    print("  ✅ 功能限制移除")
                else:
                    print("  ❌ 无功能增强")
        
        except Exception as e:
            print(f"❌ 补丁对比失败: {e}")
    
    def generate_final_audit_report(self):
        """生成最终审计报告"""
        print("\\n" + "="*60)
        print("📋 最终隐私审计报告")
        print("="*60)
        
        # 执行所有检查
        callapi_functions = self.find_all_callapi_functions()
        telemetry_count = self.analyze_telemetry_patterns()
        network_count = self.analyze_network_requests()
        sensitive_count = self.check_data_structures()
        
        # 对比当前补丁
        self.compare_with_current_patches()
        
        # 生成补丁建议
        comprehensive_patch = self.generate_patch_requirements(callapi_functions)
        
        # 计算风险评分
        total_risks = len(self.privacy_risks)
        if total_risks == 0:
            risk_level = "🟢 无风险"
            protection_needed = "最小"
        elif total_risks <= 50:
            risk_level = "🟡 低风险"
            protection_needed = "标准"
        elif total_risks <= 200:
            risk_level = "🟠 中风险" 
            protection_needed = "增强"
        else:
            risk_level = "🔴 高风险"
            protection_needed = "军工级"
        
        print(f"\\n🎯 最终评估:")
        print(f"  📊 发现的隐私风险: {total_risks}")
        print(f"  🛡️ 风险级别: {risk_level}")
        print(f"  🔒 需要保护级别: {protection_needed}")
        print(f"  🚀 CallApi 函数数量: {len(callapi_functions)}")
        print(f"  🌐 网络请求数量: {network_count}")
        
        # 保存详细报告
        report = {
            'audit_timestamp': __import__('datetime').datetime.now().isoformat(),
            'file_size': len(self.content),
            'total_privacy_risks': total_risks,
            'risk_level': risk_level,
            'protection_needed': protection_needed,
            'callapi_functions': callapi_functions,
            'privacy_risks': self.privacy_risks[:100],  # 限制大小
            'recommendations': [
                "使用 DEBUG 模式获得最全面的保护",
                "确保所有 callApi 函数都被补丁覆盖",
                "定期检查扩展更新后的新风险点",
                "考虑网络层面的额外保护措施"
            ]
        }
        
        with open("original_file_privacy_audit.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\\n💾 详细报告已保存: original_file_privacy_audit.json")
        
        return report

def main():
    """主函数"""
    print("🔍 原始文件全面隐私审计")
    print("="*60)
    print("🎯 目标: 识别所有隐私收集点")
    print("🛡️ 确保: 补丁覆盖完整性")
    print()
    
    auditor = OriginalFilePrivacyAuditor()
    
    if auditor.load_original_file():
        report = auditor.generate_final_audit_report()
        
        print("\\n" + "="*60)
        if report['total_privacy_risks'] > 0:
            print("⚠️ 发现隐私风险点，需要补丁保护")
            print("🛠️ 建议使用 DEBUG 模式获得最全面保护")
        else:
            print("✅ 未发现明显隐私风险")
        print("="*60)

if __name__ == "__main__":
    main()