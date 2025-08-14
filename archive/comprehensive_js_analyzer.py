#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面 JavaScript 分析器
深度分析 extension.js 文件，精确区分必须保留和必须禁止的功能
"""

import re
import json
import ast
from typing import Dict, List, Set, Tuple
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict

@dataclass
class FunctionInfo:
    """函数信息数据类"""
    name: str
    type: str  # 'core', 'telemetry', 'utility', 'unknown'
    importance: int  # 1-4 (4=essential, 1=optional)
    privacy_risk: int  # 1-4 (4=critical, 1=low)
    line_start: int
    line_end: int
    calls_made: List[str]  # 调用的其他函数
    called_by: List[str]  # 被哪些函数调用
    network_calls: List[str]  # 网络调用
    vscode_apis: List[str]  # VSCode API 使用
    data_access: List[str]  # 数据访问模式

@dataclass
class ThreatInfo:
    """威胁信息数据类"""
    threat_id: str
    severity: int  # 1-4
    category: str
    description: str
    functions: List[str]
    data_collected: List[str]
    mitigation: str

class ComprehensiveJSAnalyzer:
    """全面 JavaScript 分析器"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.content = ""
        self.lines = []
        self.functions = {}
        self.threats = []
        self.analysis_results = {}
        
        # 定义关键模式
        self.vscode_api_patterns = {
            'commands': r'vscode\.commands\.',
            'workspace': r'vscode\.workspace\.',
            'window': r'vscode\.window\.',
            'languages': r'vscode\.languages\.',
            'debug': r'vscode\.debug\.',
            'extensions': r'vscode\.extensions\.',
            'env': r'vscode\.env\.',
            'Uri': r'vscode\.Uri\.',
        }
        
        self.telemetry_patterns = {
            'analytics': r'(analytics|segment|mixpanel|amplitude)',
            'telemetry': r'(telemetry|reportEvent|trackEvent)',
            'tracking': r'(track|collect|report|send|submit).*(?:usage|event|metric|data)',
            'identification': r'(userId|deviceId|machineId|sessionId|clientId)',
            'fingerprinting': r'(fingerprint|userAgent|platform|hardware|screen)',
        }
        
        self.network_patterns = {
            'fetch': r'fetch\s*\(',
            'xhr': r'XMLHttpRequest|xhr',
            'websocket': r'WebSocket|ws://',
            'http_post': r'method\s*:\s*["\']POST["\']',
            'external_url': r'https?://[^\s"\'`<>]+',
        }
        
    def load_and_prepare(self):
        """加载和预处理文件"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
            self.lines = self.content.split('\n')
            print(f"✅ 文件加载成功: {len(self.content):,} 字符, {len(self.lines):,} 行")
            return True
        except Exception as e:
            print(f"❌ 文件加载失败: {e}")
            return False
    
    def extract_functions(self):
        """提取所有函数定义"""
        print("\n🔍 提取函数定义")
        print("-" * 60)
        
        # 函数定义模式
        function_patterns = [
            r'function\s+(\w+)\s*\([^)]*\)\s*{',
            r'(\w+)\s*:\s*function\s*\([^)]*\)\s*{',
            r'(\w+)\s*=\s*function\s*\([^)]*\)\s*{',
            r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>\s*{',
            r'let\s+(\w+)\s*=\s*\([^)]*\)\s*=>\s*{',
            r'var\s+(\w+)\s*=\s*\([^)]*\)\s*=>\s*{',
        ]
        
        functions_found = set()
        
        for pattern in function_patterns:
            matches = re.finditer(pattern, self.content, re.MULTILINE)
            for match in matches:
                func_name = match.group(1)
                if func_name and len(func_name) > 1:  # 过滤单字符变量
                    functions_found.add(func_name)
                    
                    # 找到函数的行号
                    start_pos = match.start()
                    line_num = self.content[:start_pos].count('\n') + 1
                    
                    self.functions[func_name] = FunctionInfo(
                        name=func_name,
                        type='unknown',
                        importance=2,  # 默认重要性
                        privacy_risk=1,  # 默认低风险
                        line_start=line_num,
                        line_end=line_num,  # 稍后计算
                        calls_made=[],
                        called_by=[],
                        network_calls=[],
                        vscode_apis=[],
                        data_access=[]
                    )
        
        print(f"📊 找到 {len(functions_found)} 个函数定义")
        
        # 显示前10个函数
        for i, func_name in enumerate(list(functions_found)[:10]):
            print(f"  {i+1}. {func_name} (行 {self.functions[func_name].line_start})")
        
        if len(functions_found) > 10:
            print(f"  ... 还有 {len(functions_found) - 10} 个函数")
            
        return functions_found
    
    def analyze_vscode_api_usage(self):
        """分析 VSCode API 使用情况"""
        print("\n🔍 分析 VSCode API 使用")
        print("-" * 60)
        
        api_usage = defaultdict(list)
        
        for api_name, pattern in self.vscode_api_patterns.items():
            matches = list(re.finditer(pattern, self.content, re.IGNORECASE))
            if matches:
                print(f"  📋 {api_name}: {len(matches)} 个使用")
                api_usage[api_name] = matches
                
                # 显示前几个使用示例
                for i, match in enumerate(matches[:3]):
                    start = max(0, match.start() - 30)
                    end = min(len(self.content), match.end() + 30)
                    context = self.content[start:end].replace('\n', '\\n')
                    print(f"    📍 {context[:60]}...")
        
        # 更新函数信息
        for func_name, func_info in self.functions.items():
            for api_name, matches in api_usage.items():
                for match in matches:
                    # 检查这个 API 调用是否在这个函数附近
                    match_line = self.content[:match.start()].count('\n') + 1
                    if abs(match_line - func_info.line_start) < 50:  # 假设函数不超过50行
                        func_info.vscode_apis.append(api_name)
                        func_info.type = 'core'  # 使用 VSCode API 的通常是核心功能
                        func_info.importance = max(func_info.importance, 3)
        
        return api_usage
    
    def analyze_telemetry_threats(self):
        """分析遥测威胁"""
        print("\n🚨 分析遥测威胁")
        print("-" * 60)
        
        threats_found = []
        
        for threat_type, pattern in self.telemetry_patterns.items():
            matches = list(re.finditer(pattern, self.content, re.IGNORECASE))
            if matches:
                print(f"  ⚠️ {threat_type}: {len(matches)} 个威胁")
                
                threat = ThreatInfo(
                    threat_id=f"threat_{len(threats_found)+1}",
                    severity=self._assess_threat_severity(threat_type),
                    category=threat_type,
                    description=f"检测到 {threat_type} 相关代码",
                    functions=[],
                    data_collected=[],
                    mitigation="需要拦截或监控"
                )
                
                # 显示威胁示例
                for i, match in enumerate(matches[:3]):
                    start = max(0, match.start() - 40)
                    end = min(len(self.content), match.end() + 40)
                    context = self.content[start:end].replace('\n', '\\n')
                    print(f"    🔍 {context[:80]}...")
                    
                    # 尝试关联到函数
                    match_line = self.content[:match.start()].count('\n') + 1
                    for func_name, func_info in self.functions.items():
                        if abs(match_line - func_info.line_start) < 20:
                            threat.functions.append(func_name)
                            func_info.type = 'telemetry'
                            func_info.privacy_risk = max(func_info.privacy_risk, threat.severity)
                
                threats_found.append(threat)
        
        self.threats = threats_found
        print(f"\n🚨 总计发现 {len(threats_found)} 类威胁")
        return threats_found
    
    def analyze_network_communications(self):
        """分析网络通信"""
        print("\n🌐 分析网络通信")
        print("-" * 60)
        
        network_usage = defaultdict(list)
        
        for comm_type, pattern in self.network_patterns.items():
            matches = list(re.finditer(pattern, self.content, re.IGNORECASE))
            if matches:
                print(f"  📡 {comm_type}: {len(matches)} 个使用")
                network_usage[comm_type] = matches
                
                # 特别关注外部 URL
                if comm_type == 'external_url':
                    urls = set()
                    for match in matches[:10]:  # 只显示前10个
                        url = match.group()
                        if len(url) > 20:
                            urls.add(url[:50] + "...")
                        else:
                            urls.add(url)
                    
                    for url in list(urls)[:5]:
                        print(f"    🌐 {url}")
        
        # 更新函数信息
        for func_name, func_info in self.functions.items():
            for comm_type, matches in network_usage.items():
                for match in matches:
                    match_line = self.content[:match.start()].count('\n') + 1
                    if abs(match_line - func_info.line_start) < 30:
                        func_info.network_calls.append(comm_type)
                        # 网络调用可能是核心功能也可能是遥测
                        if func_info.type == 'unknown':
                            func_info.type = 'utility'
        
        return network_usage
    
    def _assess_threat_severity(self, threat_type: str) -> int:
        """评估威胁严重程度"""
        severity_map = {
            'identification': 4,  # 用户身份识别 - 严重
            'fingerprinting': 4,  # 设备指纹 - 严重
            'analytics': 3,       # 分析服务 - 高
            'telemetry': 3,       # 遥测 - 高
            'tracking': 2,        # 行为追踪 - 中
        }
        return severity_map.get(threat_type, 1)
    
    def classify_functions(self):
        """对函数进行最终分类"""
        print("\n📊 函数分类结果")
        print("-" * 60)
        
        classification = {
            'core': [],      # 核心功能，必须保留
            'telemetry': [], # 遥测功能，必须禁止
            'utility': [],   # 工具功能，可选保留
            'unknown': []    # 未知功能，需要人工审查
        }
        
        for func_name, func_info in self.functions.items():
            # 基于分析结果调整分类
            if func_info.vscode_apis:
                func_info.type = 'core'
                func_info.importance = 4
            elif func_info.privacy_risk >= 3:
                func_info.type = 'telemetry'
                func_info.importance = 1
            
            classification[func_info.type].append(func_name)
        
        # 显示分类结果
        for category, functions in classification.items():
            if functions:
                print(f"  📋 {category.upper()}: {len(functions)} 个函数")
                for func in functions[:5]:  # 显示前5个
                    func_info = self.functions[func]
                    print(f"    • {func} (重要性:{func_info.importance}, 风险:{func_info.privacy_risk})")
                if len(functions) > 5:
                    print(f"    ... 还有 {len(functions) - 5} 个")
        
        return classification
    
    def generate_protection_strategy(self):
        """生成保护策略"""
        print("\n🛡️ 生成保护策略")
        print("-" * 60)
        
        strategy = {
            'preserve_completely': [],  # 完全保留
            'monitor_only': [],         # 只监控
            'block_conditionally': [],  # 条件拦截
            'block_completely': [],     # 完全拦截
            'sanitize_data': []         # 数据脱敏
        }
        
        for func_name, func_info in self.functions.items():
            if func_info.type == 'core' and func_info.importance >= 3:
                strategy['preserve_completely'].append(func_name)
            elif func_info.type == 'telemetry' and func_info.privacy_risk >= 3:
                strategy['block_completely'].append(func_name)
            elif func_info.type == 'telemetry' and func_info.privacy_risk >= 2:
                strategy['block_conditionally'].append(func_name)
            elif func_info.privacy_risk >= 2:
                strategy['monitor_only'].append(func_name)
            else:
                strategy['sanitize_data'].append(func_name)
        
        # 显示策略
        for action, functions in strategy.items():
            if functions:
                print(f"  🎯 {action.replace('_', ' ').upper()}: {len(functions)} 个函数")
        
        return strategy
    
    def run_comprehensive_analysis(self):
        """运行全面分析"""
        print("🔬 开始全面 JavaScript 分析")
        print("=" * 80)
        
        if not self.load_and_prepare():
            return None
        
        # 执行各项分析
        functions = self.extract_functions()
        api_usage = self.analyze_vscode_api_usage()
        threats = self.analyze_telemetry_threats()
        network = self.analyze_network_communications()
        classification = self.classify_functions()
        strategy = self.generate_protection_strategy()
        
        # 汇总结果
        self.analysis_results = {
            'file_info': {
                'path': self.file_path,
                'size': len(self.content),
                'lines': len(self.lines)
            },
            'functions': {name: asdict(info) for name, info in self.functions.items()},
            'threats': [asdict(threat) for threat in self.threats],
            'classification': classification,
            'protection_strategy': strategy,
            'summary': {
                'total_functions': len(functions),
                'core_functions': len(classification['core']),
                'telemetry_functions': len(classification['telemetry']),
                'threats_found': len(threats),
                'vscode_api_usage': len(api_usage),
            }
        }
        
        return self.analysis_results
    
    def save_analysis_report(self, output_file: str = 'comprehensive_analysis_report.json'):
        """保存分析报告"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.analysis_results, f, indent=2, ensure_ascii=False)
            print(f"\n✅ 分析报告已保存: {output_file}")
        except Exception as e:
            print(f"❌ 保存报告失败: {e}")

def main():
    """主函数"""
    analyzer = ComprehensiveJSAnalyzer("extension.js")
    results = analyzer.run_comprehensive_analysis()
    
    if results:
        analyzer.save_analysis_report()
        
        print("\n" + "=" * 80)
        print("📋 分析总结")
        print("=" * 80)
        
        summary = results['summary']
        print(f"📊 总函数数: {summary['total_functions']}")
        print(f"🔧 核心功能: {summary['core_functions']} 个 (必须保留)")
        print(f"📡 遥测功能: {summary['telemetry_functions']} 个 (必须禁止)")
        print(f"⚠️ 威胁发现: {summary['threats_found']} 类")
        print(f"🎯 VSCode API: {summary['vscode_api_usage']} 类使用")
        
        print(f"\n🎉 全面分析完成! 现在可以基于分析结果制定精确的补丁策略。")
    else:
        print(f"\n❌ 分析失败")

if __name__ == "__main__":
    main()