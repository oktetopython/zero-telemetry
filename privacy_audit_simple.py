#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版隐私审计工具
"""

import re
import json
import os
from pathlib import Path

class SimplePrivacyAuditor:
    """简化隐私审计器"""
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.content = ""
        self.results = {}
        
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
    
    def audit_telemetry_patterns(self):
        """审计遥测模式"""
        print("\n🔍 遥测模式审计")
        print("-" * 60)
        
        patterns = {
            'telemetry_calls': r'telemetry\w*\s*\(',
            'report_calls': r'report\w*\s*\(',
            'track_calls': r'track\w*\s*\(',
            'analytics_calls': r'analytics\w*\s*\(',
            'send_calls': r'send\w*\s*\(',
            'collect_calls': r'collect\w*\s*\(',
            'log_calls': r'log\w*\s*\(',
        }
        
        total_matches = 0
        for name, pattern in patterns.items():
            matches = list(re.finditer(pattern, self.content, re.IGNORECASE))
            if matches:
                print(f"  📊 {name}: {len(matches)} 个匹配")
                total_matches += len(matches)
                # 显示前几个匹配的上下文
                for i, match in enumerate(matches[:3]):
                    start = max(0, match.start() - 50)
                    end = min(len(self.content), match.end() + 50)
                    context = self.content[start:end].replace('\n', '\\n')
                    print(f"    📍 {context[:80]}...")
            else:
                print(f"  ✅ {name}: 未发现")
        
        print(f"\n📊 遥测调用总计: {total_matches}")
        return total_matches
    
    def audit_data_collection(self):
        """审计数据收集"""
        print("\n🔍 数据收集审计")
        print("-" * 60)
        
        patterns = {
            'user_agent': r'navigator\.userAgent',
            'platform_info': r'navigator\.platform',
            'language_info': r'navigator\.language',
            'screen_info': r'screen\.\w+',
            'process_info': r'process\.\w+',
            'os_info': r'os\.\w+',
            'uuid_generation': r'uuid\(\)|randomUUID|generateUUID',
            'machine_id': r'machineId|deviceId|hardwareId',
        }
        
        total_matches = 0
        for name, pattern in patterns.items():
            matches = list(re.finditer(pattern, self.content, re.IGNORECASE))
            if matches:
                print(f"  📊 {name}: {len(matches)} 个匹配")
                total_matches += len(matches)
            else:
                print(f"  ✅ {name}: 未发现")
        
        print(f"\n📊 数据收集总计: {total_matches}")
        return total_matches
    
    def audit_network_requests(self):
        """审计网络请求"""
        print("\n🔍 网络请求审计")
        print("-" * 60)
        
        patterns = {
            'fetch_requests': r'fetch\s*\(',
            'xhr_requests': r'XMLHttpRequest',
            'websocket': r'WebSocket',
            'http_methods': r'method\s*:\s*["\'](?:POST|PUT|PATCH)["\']',
            'external_urls': r'https?://[^\s"\'`<>]+',
        }
        
        total_matches = 0
        for name, pattern in patterns.items():
            matches = list(re.finditer(pattern, self.content, re.IGNORECASE))
            if matches:
                print(f"  📊 {name}: {len(matches)} 个匹配")
                total_matches += len(matches)
                if name == 'external_urls' and matches:
                    # 显示找到的URL
                    urls = set()
                    for match in matches[:5]:
                        url = match.group()
                        if len(url) > 20:
                            urls.add(url[:50] + "...")
                        else:
                            urls.add(url)
                    for url in list(urls)[:3]:
                        print(f"    🌐 {url}")
            else:
                print(f"  ✅ {name}: 未发现")
        
        print(f"\n📊 网络请求总计: {total_matches}")
        return total_matches
    
    def audit_patch_signatures(self):
        """审计补丁签名"""
        print("\n🔍 补丁签名审计")
        print("-" * 60)
        
        signatures = [
            'TELEMETRY BLOCKED',
            'TELEMETRY RANDOMIZED', 
            'TELEMETRY EMPTIED',
            'TELEMETRY STEALTHED',
            'sensitiveFields',
            'randSessionId',
            'this._userAgent = ""',
        ]
        
        found_signatures = 0
        for signature in signatures:
            if signature in self.content:
                found_signatures += 1
                print(f"  ✅ 找到补丁签名: {signature}")
            else:
                print(f"  ❌ 未找到签名: {signature}")
        
        coverage = found_signatures / len(signatures) * 100
        print(f"\n🛡️ 补丁覆盖率: {coverage:.1f}% ({found_signatures}/{len(signatures)})")
        return coverage
    
    def run_full_audit(self):
        """运行完整审计"""
        print("🔍 开始全面隐私审计")
        print("=" * 80)
        
        if not self.load_file():
            return None
        
        # 执行各项审计
        telemetry_count = self.audit_telemetry_patterns()
        collection_count = self.audit_data_collection()
        network_count = self.audit_network_requests()
        patch_coverage = self.audit_patch_signatures()
        
        # 生成总结
        print("\n" + "=" * 80)
        print("📋 审计总结")
        print("=" * 80)
        
        total_issues = telemetry_count + collection_count + network_count
        
        print(f"📊 遥测调用: {telemetry_count}")
        print(f"📊 数据收集: {collection_count}")
        print(f"📊 网络请求: {network_count}")
        print(f"🛡️ 补丁覆盖: {patch_coverage:.1f}%")
        print(f"⚠️ 总问题数: {total_issues}")
        
        # 风险评估
        if patch_coverage >= 80:
            risk_level = "低"
        elif patch_coverage >= 50:
            risk_level = "中"
        else:
            risk_level = "高"
        
        print(f"🎯 风险等级: {risk_level}")
        
        # 保存结果
        results = {
            'telemetry_count': telemetry_count,
            'collection_count': collection_count,
            'network_count': network_count,
            'patch_coverage': patch_coverage,
            'total_issues': total_issues,
            'risk_level': risk_level
        }
        
        try:
            with open('privacy_audit_results.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"\n✅ 结果已保存到: privacy_audit_results.json")
        except Exception as e:
            print(f"❌ 保存结果失败: {e}")
        
        return results

def main():
    """主函数"""
    file_path = "extension.js"
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return
    
    auditor = SimplePrivacyAuditor(file_path)
    results = auditor.run_full_audit()
    
    if results:
        print(f"\n🎉 审计完成! 风险等级: {results['risk_level']}")
    else:
        print(f"\n❌ 审计失败")

if __name__ == "__main__":
    main()