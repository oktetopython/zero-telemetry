#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面隐私审计工具
深度检查 extension.js 文件中的所有隐私相关内容
"""

import re
import json
from pathlib import Path
from collections import defaultdict

class ComprehensivePrivacyAuditor:
    """全面隐私审计器"""
    
    def __init__(self, file_path="extension.js"):
        self.file_path = file_path
        self.content = ""
        self.audit_results = {}
        self.privacy_violations = []
        self.load_file()
    
    def load_file(self):
        """加载文件"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
            print(f"✅ 文件加载成功: {len(self.content):,} 字符")
            return True
        except Exception as e:
            print(f"❌ 文件加载失败: {e}")
            return False
    
    def audit_data_collection_apis(self):
        """审计数据收集 API"""
        print("\n" + "="*80)
        print("🔍 数据收集 API 审计")
        print("="*80)
        
        # 定义数据收集相关的 API 模式
        collection_patterns = {
            # 网络请求相关
            'fetch_requests': r'fetch\s*\([^)]*\)',
            'xhr_requests': r'new\s+XMLHttpRequest\s*\(\)',
            'websocket_connections': r'new\s+WebSocket\s*\([^)]*\)',
            
            # 数据发送相关
            'post_requests': r'method\s*:\s*["\']POST["\']',
            'put_requests': r'method\s*:\s*["\']PUT["\']',
            'send_methods': r'\.send\s*\([^)]*\)',
            
            # API 调用相关
            'api_calls': r'callApi\s*\([^)]*\)',
            'http_calls': r'http[s]?://[^\s"\'`<>]+',
            
            # 事件发送
            'event_emitters': r'\.emit\s*\([^)]*\)',
            'event_dispatchers': r'dispatchEvent\s*\([^)]*\)',
            
            # 消息传递
            'post_message': r'postMessage\s*\([^)]*\)',
            'send_message': r'sendMessage\s*\([^)]*\)',
        }
        
        collection_results = {}
        
        for pattern_name, pattern in collection_patterns.items():
            matches = list(re.finditer(pattern, self.content, re.IGNORECASE))
            collection_results[pattern_name] = len(matches)
            
            if matches:
                print(f"\n📡 {pattern_name.replace('_', ' ').title()}: {len(matches)} 个")
                
                # 分析每个匹配的上下文
                privacy_related = 0
                for match in matches[:5]:  # 只显示前5个
                    start = max(0, match.start() - 100)
                    end = min(len(self.content), match.end() + 100)
                    context = self.content[start:end]
                    
                    # 检查上下文中是否包含隐私相关关键词
                    privacy_keywords = [
                        'telemetry', 'analytics', 'tracking', 'metrics', 'usage',
                        'report', 'record', 'log', 'event', 'session', 'user',
                        'machine', 'device', 'client', 'fingerprint', 'id'
                    ]
                    
                    has_privacy_content = any(keyword in context.lower() for keyword in privacy_keywords)
                    if has_privacy_content:
                        privacy_related += 1
                        print(f"  ⚠️ 位置 {match.start()}: {match.group()[:50]}...")
                        
                        # 记录隐私违规
                        self.privacy_violations.append({
                            'type': 'data_collection_api',
                            'pattern': pattern_name,
                            'position': match.start(),
                            'content': match.group(),
                            'context': context[:200]
                        })
                
                if privacy_related > 0:
                    print(f"  🚨 其中 {privacy_related} 个可能涉及隐私数据")
        
        self.audit_results['data_collection_apis'] = collection_results
        return collection_results
    
    def audit_identifier_generation(self):
        """审计标识符生成"""
        print("\n" + "="*80)
        print("🆔 标识符生成审计")
        print("="*80)
        
        # 标识符生成模式
        identifier_patterns = {
            # UUID 相关
            'uuid_generation': r'uuid\s*\(\)|generateUUID|randomUUID',
            'guid_generation': r'guid\s*\(\)|generateGUID',
            
            # 随机ID生成
            'random_id': r'Math\.random\s*\(\).*toString\s*\(36\)',
            'crypto_random': r'crypto\.getRandomValues|crypto\.randomUUID',
            
            # 时间戳ID
            'timestamp_id': r'Date\.now\s*\(\).*toString|timestamp.*id',
            
            # 机器/设备ID
            'machine_id': r'machineId|machine_id|deviceId|device_id',
            'client_id': r'clientId|client_id|sessionId|session_id',
            'user_id': r'userId|user_id|customerId|customer_id',
            
            # 指纹相关
            'fingerprint': r'fingerprint|getFingerprint|generateFingerprint',
            'browser_info': r'navigator\.(userAgent|platform|language|vendor)',
            'screen_info': r'screen\.(width|height|availWidth|availHeight)',
            'timezone_info': r'Intl\.DateTimeFormat.*timeZone|getTimezoneOffset',
        }
        
        identifier_results = {}
        
        for pattern_name, pattern in identifier_patterns.items():
            matches = list(re.finditer(pattern, self.content, re.IGNORECASE))
            identifier_results[pattern_name] = len(matches)
            
            if matches:
                print(f"\n🔢 {pattern_name.replace('_', ' ').title()}: {len(matches)} 个")
                
                for match in matches[:3]:  # 显示前3个
                    start = max(0, match.start() - 50)
                    end = min(len(self.content), match.end() + 50)
                    context = self.content[start:end].replace('\n', '\\n')
                    print(f"  📍 位置 {match.start()}: ...{context}...")
                    
                    # 记录潜在隐私问题
                    self.privacy_violations.append({
                        'type': 'identifier_generation',
                        'pattern': pattern_name,
                        'position': match.start(),
                        'content': match.group(),
                        'severity': 'high' if any(x in pattern_name for x in ['machine', 'device', 'fingerprint']) else 'medium'
                    })
        
        self.audit_results['identifier_generation'] = identifier_results
        return identifier_results
    
    def audit_usage_limits_and_restrictions(self):
        """审计使用限制和约束"""
        print("\n" + "="*80)
        print("🚫 使用限制和约束审计")
        print("="*80)
        
        # 限制相关模式
        limit_patterns = {
            # 文件和大小限制
            'file_size_limits': r'maxFileSize|max_file_size|fileSizeLimit|FILE_SIZE_LIMIT',
            'file_count_limits': r'maxFileCount|max_file_count|fileCountLimit|maxFiles',
            'upload_limits': r'maxUploadSize|max_upload_size|uploadLimit|UPLOAD_LIMIT',
            
            # 请求和时间限制
            'request_limits': r'maxRequests|max_requests|requestLimit|REQUEST_LIMIT',
            'timeout_limits': r'timeout|TIMEOUT|timeoutMs|requestTimeout',
            'rate_limits': r'rateLimit|rate_limit|throttle|THROTTLE',
            
            # 使用量限制
            'usage_limits': r'usageLimit|usage_limit|quotaLimit|QUOTA_LIMIT',
            'api_limits': r'apiLimit|api_limit|callLimit|CALL_LIMIT',
            'token_limits': r'tokenLimit|token_limit|maxTokens|MAX_TOKENS',
            
            # 功能限制
            'feature_limits': r'featureLimit|feature_limit|enabledFeatures|ENABLED_FEATURES',
            'subscription_checks': r'subscription|premium|pro|enterprise|paid',
            'license_checks': r'license|LICENSE|activation|ACTIVATION',
            
            # 计数器和统计
            'counters': r'count\+\+|counter\+\+|increment.*count|usage.*count',
            'statistics': r'stats\.|statistics\.|metrics\.|telemetry\.',
            'tracking_vars': r'track.*count|usage.*track|session.*count',
        }
        
        limit_results = {}
        
        for pattern_name, pattern in limit_patterns.items():
            matches = list(re.finditer(pattern, self.content, re.IGNORECASE))
            limit_results[pattern_name] = len(matches)
            
            if matches:
                print(f"\n🔒 {pattern_name.replace('_', ' ').title()}: {len(matches)} 个")
                
                for match in matches[:3]:  # 显示前3个
                    start = max(0, match.start() - 80)
                    end = min(len(self.content), match.end() + 80)
                    context = self.content[start:end].replace('\n', '\\n')
                    print(f"  📍 位置 {match.start()}: ...{context[:120]}...")
                    
                    # 记录限制相关问题
                    self.privacy_violations.append({
                        'type': 'usage_restriction',
                        'pattern': pattern_name,
                        'position': match.start(),
                        'content': match.group(),
                        'severity': 'medium'
                    })
        
        self.audit_results['usage_limits'] = limit_results
        return limit_results
    
    def audit_data_storage_and_persistence(self):
        """审计数据存储和持久化"""
        print("\n" + "="*80)
        print("💾 数据存储和持久化审计")
        print("="*80)
        
        # 存储相关模式
        storage_patterns = {
            # 本地存储
            'local_storage': r'localStorage\.(setItem|getItem|removeItem)',
            'session_storage': r'sessionStorage\.(setItem|getItem|removeItem)',
            'indexed_db': r'indexedDB|IDBDatabase|openDatabase',
            'web_sql': r'openDatabase|executeSql',
            
            # Cookie 操作
            'cookie_operations': r'document\.cookie|setCookie|getCookie',
            
            # 缓存操作
            'cache_operations': r'cache\.(put|add|match)|caches\.open',
            'memory_cache': r'memoryCache|inMemoryCache|cache\.set',
            
            # 文件系统操作
            'file_operations': r'writeFile|readFile|fs\.(write|read)',
            'temp_files': r'tmpdir|tempFile|createTempFile',
            
            # 数据库操作
            'database_operations': r'INSERT|UPDATE|DELETE|SELECT.*FROM',
            'sqlite_operations': r'sqlite|\.db|database\.exec',
            
            # 配置存储
            'config_storage': r'config\.(set|get|save)|settings\.(set|get|save)',
            'preference_storage': r'preferences\.(set|get)|prefs\.(set|get)',
        }
        
        storage_results = {}
        
        for pattern_name, pattern in storage_patterns.items():
            matches = list(re.finditer(pattern, self.content, re.IGNORECASE))
            storage_results[pattern_name] = len(matches)
            
            if matches:
                print(f"\n💿 {pattern_name.replace('_', ' ').title()}: {len(matches)} 个")
                
                # 分析存储的数据类型
                sensitive_storage = 0
                for match in matches[:3]:
                    start = max(0, match.start() - 100)
                    end = min(len(self.content), match.end() + 100)
                    context = self.content[start:end]
                    
                    # 检查是否存储敏感数据
                    sensitive_keywords = [
                        'id', 'token', 'key', 'secret', 'password', 'auth',
                        'session', 'user', 'machine', 'device', 'fingerprint'
                    ]
                    
                    has_sensitive = any(keyword in context.lower() for keyword in sensitive_keywords)
                    if has_sensitive:
                        sensitive_storage += 1
                        print(f"  ⚠️ 位置 {match.start()}: 可能存储敏感数据")
                        
                        self.privacy_violations.append({
                            'type': 'sensitive_data_storage',
                            'pattern': pattern_name,
                            'position': match.start(),
                            'content': match.group(),
                            'severity': 'high'
                        })
                
                if sensitive_storage > 0:
                    print(f"  🚨 其中 {sensitive_storage} 个可能涉及敏感数据存储")
        
        self.audit_results['data_storage'] = storage_results
        return storage_results
    
    def audit_network_communications(self):
        """审计网络通信"""
        print("\n" + "="*80)
        print("🌐 网络通信审计")
        print("="*80)
        
        # 网络通信模式
        network_patterns = {
            # HTTP/HTTPS 请求
            'http_requests': r'https?://[^\s"\'`<>]+',
            'api_endpoints': r'/api/[^\s"\'`<>]+|/v\d+/[^\s"\'`<>]+',
            
            # 域名和服务器
            'external_domains': r'[a-zA-Z0-9-]+\.(com|net|org|io|dev|ai)[^\s"\'`<>]*',
            'tracking_domains': r'(analytics|tracking|metrics|telemetry)\.[a-zA-Z0-9-]+\.[a-zA-Z]{2,}',
            
            # 数据传输
            'json_data': r'JSON\.(stringify|parse)',
            'form_data': r'FormData|multipart/form-data',
            'binary_data': r'ArrayBuffer|Uint8Array|Blob',
            
            # 认证和授权
            'auth_headers': r'Authorization|Bearer|Basic|Token',
            'api_keys': r'api[_-]?key|apikey|x-api-key',
            'oauth_tokens': r'oauth|access_token|refresh_token',
            
            # WebSocket 通信
            'websocket_urls': r'wss?://[^\s"\'`<>]+',
            'socket_events': r'socket\.(emit|on|send)',
            
            # 第三方服务
            'analytics_services': r'google-analytics|segment|mixpanel|amplitude',
            'cdn_services': r'cdn\.|cloudflare|amazonaws|azure',
        }
        
        network_results = {}
        
        for pattern_name, pattern in network_patterns.items():
            matches = list(re.finditer(pattern, self.content, re.IGNORECASE))
            network_results[pattern_name] = len(matches)
            
            if matches:
                print(f"\n🔗 {pattern_name.replace('_', ' ').title()}: {len(matches)} 个")
                
                # 显示具体的网络目标
                unique_matches = list(set([match.group() for match in matches]))[:5]
                for match_text in unique_matches:
                    print(f"  📡 {match_text}")
                    
                    # 检查是否为可疑的网络通信
                    suspicious_keywords = [
                        'telemetry', 'analytics', 'tracking', 'metrics',
                        'report', 'collect', 'gather', 'send'
                    ]
                    
                    if any(keyword in match_text.lower() for keyword in suspicious_keywords):
                        self.privacy_violations.append({
                            'type': 'suspicious_network_communication',
                            'pattern': pattern_name,
                            'content': match_text,
                            'severity': 'high'
                        })
        
        self.audit_results['network_communications'] = network_results
        return network_results
    
    def audit_patch_effectiveness(self):
        """审计补丁有效性"""
        print("\n" + "="*80)
        print("🛡️ 补丁有效性审计")
        print("="*80)
        
        # 检查补丁签名
        patch_signatures = [
            'TELEMETRY BLOCKED',
            'TELEMETRY RANDOMIZED', 
            'TELEMETRY EMPTIED',
            'TELEMETRY STEALTHED',
            'TELEMETRY DEBUG',
            'typeof s === "string" ? s : (typeof n === "string" ? n',
            'sensitiveFields',
            'randSessionId',
            'this._userAgent = ""'
        ]
        
        patch_status = {}
        
        for signature in patch_signatures:
            if signature in self.content:
                patch_status[signature] = True
                print(f"✅ 找到补丁签名: {signature}")
            else:
                patch_status[signature] = False
                print(f"❌ 未找到补丁签名: {signature}")
        
        # 检查是否有未被拦截的遥测调用
        unpatched_patterns = [
            r'reportEvent\s*\([^)]*\)',
            r'trackEvent\s*\([^)]*\)',
            r'sendTelemetry\s*\([^)]*\)',
            r'collectMetrics\s*\([^)]*\)',
        ]
        
        unpatched_calls = {}
        for pattern in unpatched_patterns:
            matches = re.findall(pattern, self.content)
            if matches:
                unpatched_calls[pattern] = len(matches)
                print(f"⚠️ 发现未拦截的调用: {pattern} ({len(matches)} 个)")
        
        self.audit_results['patch_effectiveness'] = {
            'signatures_found': patch_status,
            'unpatched_calls': unpatched_calls
        }
        
        return patch_status, unpatched_calls
    
    def generate_comprehensive_report(self):
        """生成全面审计报告"""
        print("\n" + "="*80)
        print("📋 全面隐私审计报告")
        print("="*80)
        
        # 统计隐私违规
        violation_by_type = defaultdict(int)
        violation_by_severity = defaultdict(int)
        
        for violation in self.privacy_violations:
            violation_by_type[violation['type']] += 1
            violation_by_severity[violation.get('severity', 'unknown')] += 1
        
        print(f"\n📊 隐私违规统计:")
        print(f"  总计: {len(self.privacy_violations)} 个潜在问题")
        
        for vtype, count in violation_by_type.items():
            print(f"  {vtype}: {count} 个")
        
        print(f"\n🚨 严重程度分布:")
        for severity, count in violation_by_severity.items():
            print(f"  {severity}: {count} 个")
        
        # 生成建议
        recommendations = []
        
        if violation_by_severity['high'] > 0:
            recommendations.append("🔴 发现高风险隐私问题，需要立即处理")
        
        if 'data_collection_api' in violation_by_type:
            recommendations.append("📡 建议加强 API 调用拦截")
        
        if 'identifier_generation' in violation_by_type:
            recommendations.append("🆔 建议增强标识符生成拦截")
        
        if 'usage_restriction' in violation_by_type:
            recommendations.append("🚫 建议移除或绕过使用限制")
        
        if 'sensitive_data_storage' in violation_by_type:
            recommendations.append("💾 建议阻止敏感数据存储")
        
        print(f"\n💡 改进建议:")
        for rec in recommendations:
            print(f"  {rec}")
        
        # 保存详细报告
        report = {
            'audit_timestamp': __import__('datetime').datetime.now().isoformat(),
            'file_info': {
                'path': self.file_path,
                'size': len(self.content)
            },
            'audit_results': self.audit_results,
            'privacy_violations': self.privacy_violations,
            'violation_summary': {
                'total': len(self.privacy_violations),
                'by_type': dict(violation_by_type),
                'by_severity': dict(violation_by_severity)
            },
            'recommendations': recommendations
        }
        
        with open('comprehensive_privacy_audit_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 详细报告已保存: comprehensive_privacy_audit_report.json")
        
        return report
    
    def run_full_audit(self):
        """运行完整审计"""
        print("🔍 开始全面隐私审计")
        print("="*80)
        
        # 执行各项审计
        self.audit_data_collection_apis()
        self.audit_identifier_generation()
        self.audit_usage_limits_and_restrictions()
        self.audit_data_storage_and_persistence()
        self.audit_network_communications()
        self.audit_patch_effectiveness()
        
        # 生成报告
        report = self.generate_comprehensive_report()
        
        print(f"\n🎯 审计完成!")
        return report

def main():
    """主函数"""
    print("🔍 全面隐私审计工具启动")
    print("="*80)
    
    file_path = "extension.js"
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return
    
    auditor = ComprehensivePrivacyAuditor(file_path)
    
    try:
        report = auditor.run_full_audit()
        
        # 输出关键结论
        total_violations = len(auditor.privacy_violations)
        if total_violations == 0:
            print(f"\n🎉 恭喜！未发现明显的隐私问题")
        else:
            print(f"\n⚠️ 发现 {total_violations} 个潜在隐私问题，请查看详细报告")
            
    except Exception as e:
        print(f"❌ 审计过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()