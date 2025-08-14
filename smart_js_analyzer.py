#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能 JavaScript 分析器
高效分析 extension.js，重点识别关键功能和威胁
"""

import re
import json
from collections import defaultdict

class SmartJSAnalyzer:
    """智能 JavaScript 分析器"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.content = ""
        self.analysis = {}
        
    def load_file(self):
        """加载文件"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
            print(f"✅ 文件加载: {len(self.content):,} 字符")
            return True
        except Exception as e:
            print(f"❌ 加载失败: {e}")
            return False
    
    def analyze_critical_functions(self):
        """分析关键功能"""
        print("\n🔍 分析关键功能")
        print("-" * 60)
        
        # 必须保留的核心功能模式
        core_patterns = {
            'vscode_commands': r'vscode\.commands\.(register|execute)',
            'vscode_workspace': r'vscode\.workspace\.',
            'vscode_window': r'vscode\.window\.',
            'vscode_languages': r'vscode\.languages\.',
            'file_operations': r'(readFile|writeFile|fs\.)',
            'extension_activation': r'(activate|deactivate)\s*\(',
            'command_handlers': r'registerCommand|executeCommand',
            'language_features': r'(completion|hover|diagnostic|definition)',
        }
        
        core_functions = {}
        for name, pattern in core_patterns.items():
            matches = len(re.findall(pattern, self.content, re.IGNORECASE))
            if matches > 0:
                core_functions[name] = matches
                print(f"  ✅ {name}: {matches} 个使用")
        
        return core_functions
    
    def analyze_privacy_threats(self):
        """分析隐私威胁"""
        print("\n🚨 分析隐私威胁")
        print("-" * 60)
        
        # 必须禁止的隐私威胁模式
        threat_patterns = {
            'segment_analytics': r'segment\.io|analytics\.track|analytics\.identify',
            'telemetry_reporting': r'reportEvent|trackEvent|sendTelemetry',
            'user_identification': r'(userId|deviceId|machineId|clientId|sessionId)',
            'device_fingerprinting': r'(navigator\.userAgent|navigator\.platform|screen\.|hardware)',
            'usage_tracking': r'(usage|metrics|statistics).*(?:collect|send|report)',
            'error_reporting': r'(sentry|bugsnag|crashlytics|errorReporting)',
            'external_analytics': r'(google-analytics|mixpanel|amplitude|hotjar)',
        }
        
        threats = {}
        for name, pattern in threat_patterns.items():
            matches = list(re.finditer(pattern, self.content, re.IGNORECASE))
            if matches:
                threats[name] = {
                    'count': len(matches),
                    'severity': self._get_threat_severity(name),
                    'examples': []
                }
                
                # 收集示例
                for match in matches[:3]:
                    start = max(0, match.start() - 50)
                    end = min(len(self.content), match.end() + 50)
                    context = self.content[start:end].replace('\n', ' ')
                    threats[name]['examples'].append(context[:100])
                
                print(f"  ⚠️ {name}: {len(matches)} 个威胁 (严重度: {threats[name]['severity']})")
        
        return threats
    
    def analyze_network_communications(self):
        """分析网络通信"""
        print("\n🌐 分析网络通信")
        print("-" * 60)
        
        network_patterns = {
            'api_calls': r'fetch\s*\(|XMLHttpRequest',
            'websockets': r'WebSocket|ws://|wss://',
            'external_domains': r'https?://(?!localhost|127\.0\.0\.1)[^\s"\'`<>]+',
            'post_requests': r'method\s*:\s*["\']POST["\']',
        }
        
        network_usage = {}
        for name, pattern in network_patterns.items():
            matches = list(re.finditer(pattern, self.content, re.IGNORECASE))
            if matches:
                network_usage[name] = len(matches)
                print(f"  📡 {name}: {len(matches)} 个")
                
                # 对于外部域名，显示具体的域名
                if name == 'external_domains':
                    domains = set()
                    for match in matches[:10]:
                        url = match.group()
                        domain = re.search(r'https?://([^/\s"\'`<>]+)', url)
                        if domain:
                            domains.add(domain.group(1))
                    
                    for domain in list(domains)[:5]:
                        print(f"    🌐 {domain}")
        
        return network_usage
    
    def identify_function_categories(self):
        """识别函数类别"""
        print("\n📊 识别函数类别")
        print("-" * 60)
        
        # 通过关键词识别函数用途
        function_categories = {
            'core_business': {
                'patterns': [r'(completion|hover|diagnostic|definition|format|refactor)',
                           r'(workspace|document|editor|selection)',
                           r'(command|menu|statusbar|notification)'],
                'functions': []
            },
            'telemetry_analytics': {
                'patterns': [r'(track|report|analytics|telemetry|metrics)',
                           r'(segment|mixpanel|amplitude)',
                           r'(collect|send|submit).*(?:data|event|usage)'],
                'functions': []
            },
            'network_communication': {
                'patterns': [r'(fetch|request|http|api|call)',
                           r'(websocket|socket|connection)',
                           r'(upload|download|sync)'],
                'functions': []
            },
            'system_integration': {
                'patterns': [r'(vscode|extension|activate|deactivate)',
                           r'(register|dispose|subscribe)',
                           r'(configuration|settings|preferences)'],
                'functions': []
            }
        }
        
        # 简化的函数提取（只提取明显的函数名）
        function_names = re.findall(r'function\s+(\w+)|(\w+)\s*:\s*function|const\s+(\w+)\s*=.*function', 
                                  self.content, re.IGNORECASE)
        
        # 扁平化函数名列表
        all_functions = []
        for match in function_names:
            for group in match:
                if group and len(group) > 2:  # 过滤短名称
                    all_functions.append(group)
        
        print(f"  📋 提取到 {len(set(all_functions))} 个函数名")
        
        # 根据函数名和周围代码分类
        for func_name in set(all_functions):
            # 查找函数定义周围的代码
            func_pattern = rf'\b{re.escape(func_name)}\b'
            matches = list(re.finditer(func_pattern, self.content))
            
            if matches:
                # 取第一个匹配周围的代码
                match = matches[0]
                start = max(0, match.start() - 200)
                end = min(len(self.content), match.end() + 200)
                context = self.content[start:end].lower()
                
                # 根据上下文分类
                for category, info in function_categories.items():
                    for pattern in info['patterns']:
                        if re.search(pattern, context, re.IGNORECASE):
                            info['functions'].append(func_name)
                            break
        
        # 显示分类结果
        for category, info in function_categories.items():
            if info['functions']:
                print(f"  📋 {category}: {len(info['functions'])} 个函数")
        
        return function_categories
    
    def generate_protection_recommendations(self):
        """生成保护建议"""
        print("\n🛡️ 生成保护建议")
        print("-" * 60)
        
        recommendations = {
            'preserve_completely': [
                'vscode API 调用',
                '文件操作功能', 
                '扩展激活/停用',
                '命令处理器',
                '语言功能'
            ],
            'block_completely': [
                'segment.io 分析',
                '遥测报告',
                '用户身份识别',
                '设备指纹采集',
                '外部分析服务'
            ],
            'monitor_carefully': [
                '网络请求',
                '错误报告',
                '使用统计',
                '性能指标'
            ],
            'sanitize_data': [
                '用户代理字符串',
                '系统信息',
                '环境变量',
                '硬件信息'
            ]
        }
        
        for action, items in recommendations.items():
            print(f"  🎯 {action.replace('_', ' ').upper()}:")
            for item in items:
                print(f"    • {item}")
        
        return recommendations
    
    def _get_threat_severity(self, threat_name: str) -> int:
        """获取威胁严重程度"""
        severity_map = {
            'segment_analytics': 4,      # 严重
            'user_identification': 4,    # 严重
            'device_fingerprinting': 4,  # 严重
            'telemetry_reporting': 3,    # 高
            'usage_tracking': 3,         # 高
            'error_reporting': 2,        # 中
            'external_analytics': 3,     # 高
        }
        return severity_map.get(threat_name, 1)
    
    def run_smart_analysis(self):
        """运行智能分析"""
        print("🧠 智能 JavaScript 分析")
        print("=" * 80)
        
        if not self.load_file():
            return None
        
        # 执行关键分析
        core_functions = self.analyze_critical_functions()
        threats = self.analyze_privacy_threats()
        network = self.analyze_network_communications()
        categories = self.identify_function_categories()
        recommendations = self.generate_protection_recommendations()
        
        # 汇总分析结果
        self.analysis = {
            'file_info': {
                'path': self.file_path,
                'size': len(self.content)
            },
            'core_functions': core_functions,
            'privacy_threats': threats,
            'network_usage': network,
            'function_categories': categories,
            'recommendations': recommendations,
            'summary': {
                'core_function_types': len(core_functions),
                'threat_types': len(threats),
                'total_threats': sum(t['count'] for t in threats.values()),
                'network_types': len(network),
                'high_severity_threats': len([t for t in threats.values() if t['severity'] >= 3])
            }
        }
        
        return self.analysis
    
    def save_report(self, filename: str = 'smart_analysis_report.json'):
        """保存分析报告"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.analysis, f, indent=2, ensure_ascii=False)
            print(f"\n✅ 报告已保存: {filename}")
        except Exception as e:
            print(f"❌ 保存失败: {e}")

def main():
    """主函数"""
    analyzer = SmartJSAnalyzer("extension.js")
    results = analyzer.run_smart_analysis()
    
    if results:
        analyzer.save_report()
        
        print("\n" + "=" * 80)
        print("📋 智能分析总结")
        print("=" * 80)
        
        summary = results['summary']
        print(f"🔧 核心功能类型: {summary['core_function_types']} 种")
        print(f"⚠️ 威胁类型: {summary['threat_types']} 种")
        print(f"🚨 总威胁数量: {summary['total_threats']} 个")
        print(f"🔥 高危威胁: {summary['high_severity_threats']} 种")
        print(f"🌐 网络通信类型: {summary['network_types']} 种")
        
        # 显示关键建议
        print(f"\n💡 关键建议:")
        print(f"  ✅ 必须保留: VSCode API、文件操作、扩展功能")
        print(f"  ❌ 必须禁止: 分析服务、用户识别、设备指纹")
        print(f"  👁️ 需要监控: 网络请求、错误报告")
        print(f"  🔒 需要脱敏: 用户代理、系统信息")
        
        print(f"\n🎉 智能分析完成! 基于此结果可以制定精确的隐私保护策略。")
    else:
        print(f"\n❌ 分析失败")

if __name__ == "__main__":
    main()