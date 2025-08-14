#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AugmentCode Extension.js 反编译分析工具
详细分析压缩混淆的JavaScript代码结构和功能
"""

import re
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import Counter

class ExtensionAnalyzer:
    """Extension.js 文件分析器"""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.content = ""
        self.analysis_results = {}
        
    def load_file(self):
        """加载文件内容"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
            print(f"✅ 文件加载成功: {self.file_path}")
            print(f"📊 文件大小: {len(self.content):,} 字符")
            return True
        except Exception as e:
            print(f"❌ 文件加载失败: {e}")
            return False
    
    def basic_analysis(self):
        """基础文件分析"""
        print("\n" + "="*60)
        print("📋 基础文件分析")
        print("="*60)
        
        # 文件基本信息
        file_size = len(self.content)
        lines = self.content.count('\n') + 1
        
        print(f"📁 文件路径: {self.file_path}")
        print(f"📏 文件大小: {file_size:,} 字符 ({file_size/1024/1024:.2f} MB)")
        print(f"📄 行数: {lines:,}")
        print(f"🔤 平均行长度: {file_size/lines:.0f} 字符/行")
        
        # 检查文件格式
        if lines == 1:
            print("🔍 文件格式: 单行压缩代码 (Minified)")
        else:
            print("🔍 文件格式: 多行代码")
        
        # 检查是否使用严格模式
        if self.content.startswith('"use strict"'):
            print("✅ 使用严格模式 (use strict)")
        
        self.analysis_results['basic'] = {
            'size': file_size,
            'lines': lines,
            'avg_line_length': file_size/lines,
            'is_minified': lines == 1,
            'use_strict': self.content.startswith('"use strict"')
        }
    
    def detect_obfuscation(self):
        """检测代码混淆程度"""
        print("\n" + "="*60)
        print("🔒 代码混淆检测")
        print("="*60)
        
        # 检测混淆特征
        obfuscation_indicators = {
            'short_var_names': len(re.findall(r'\b[a-zA-Z_$][a-zA-Z0-9_$]{0,2}\b', self.content[:10000])),
            'hex_strings': len(re.findall(r'\\x[0-9a-fA-F]{2}', self.content)),
            'unicode_escapes': len(re.findall(r'\\u[0-9a-fA-F]{4}', self.content)),
            'eval_usage': self.content.count('eval('),
            'function_expressions': len(re.findall(r'function\s*\(', self.content)),
            'arrow_functions': len(re.findall(r'=>', self.content)),
            'ternary_operators': self.content.count('?'),
            'semicolons': self.content.count(';'),
        }
        
        # 分析混淆程度
        print(f"🔤 短变量名 (≤3字符): {obfuscation_indicators['short_var_names']:,}")
        print(f"🔢 十六进制转义: {obfuscation_indicators['hex_strings']:,}")
        print(f"🌐 Unicode转义: {obfuscation_indicators['unicode_escapes']:,}")
        print(f"⚡ eval() 调用: {obfuscation_indicators['eval_usage']:,}")
        print(f"🔧 函数表达式: {obfuscation_indicators['function_expressions']:,}")
        print(f"➡️ 箭头函数: {obfuscation_indicators['arrow_functions']:,}")
        print(f"❓ 三元操作符: {obfuscation_indicators['ternary_operators']:,}")
        print(f"➖ 分号数量: {obfuscation_indicators['semicolons']:,}")
        
        # 计算混淆评分
        obfuscation_score = 0
        if obfuscation_indicators['short_var_names'] > 1000:
            obfuscation_score += 3
        if obfuscation_indicators['hex_strings'] > 100:
            obfuscation_score += 2
        if obfuscation_indicators['unicode_escapes'] > 50:
            obfuscation_score += 2
        if obfuscation_indicators['eval_usage'] > 0:
            obfuscation_score += 3
        
        print(f"\n🎯 混淆评分: {obfuscation_score}/10")
        if obfuscation_score >= 7:
            print("🔴 高度混淆")
        elif obfuscation_score >= 4:
            print("🟡 中度混淆")
        else:
            print("🟢 轻度混淆")
        
        self.analysis_results['obfuscation'] = obfuscation_indicators
        self.analysis_results['obfuscation']['score'] = obfuscation_score
    
    def analyze_structure(self):
        """分析代码结构"""
        print("\n" + "="*60)
        print("🏗️ 代码结构分析")
        print("="*60)
        
        # 查找主要的代码模式
        patterns = {
            'var_declarations': r'\bvar\s+\w+',
            'let_declarations': r'\blet\s+\w+',
            'const_declarations': r'\bconst\s+\w+',
            'function_declarations': r'\bfunction\s+\w+',
            'class_declarations': r'\bclass\s+\w+',
            'require_calls': r'require\s*\(',
            'exports_assignments': r'exports\.',
            'module_exports': r'module\.exports',
            'async_functions': r'\basync\s+function',
            'await_calls': r'\bawait\s+',
            'promise_then': r'\.then\s*\(',
            'promise_catch': r'\.catch\s*\(',
            'try_catch': r'\btry\s*\{',
            'throw_statements': r'\bthrow\s+',
        }
        
        structure_stats = {}
        for name, pattern in patterns.items():
            matches = re.findall(pattern, self.content)
            structure_stats[name] = len(matches)
            print(f"📌 {name.replace('_', ' ').title()}: {len(matches):,}")
        
        # 分析模块化程度
        is_commonjs = structure_stats['require_calls'] > 0 or structure_stats['module_exports'] > 0
        is_es6_modules = 'import ' in self.content or 'export ' in self.content
        
        print(f"\n📦 模块系统:")
        print(f"   CommonJS: {'✅' if is_commonjs else '❌'}")
        print(f"   ES6 Modules: {'✅' if is_es6_modules else '❌'}")
        
        # 分析异步编程模式
        async_patterns = structure_stats['async_functions'] + structure_stats['await_calls']
        promise_patterns = structure_stats['promise_then'] + structure_stats['promise_catch']
        
        print(f"\n⚡ 异步编程:")
        print(f"   Async/Await: {async_patterns:,}")
        print(f"   Promises: {promise_patterns:,}")
        
        self.analysis_results['structure'] = structure_stats
    
    def find_key_functions(self):
        """查找关键函数"""
        print("\n" + "="*60)
        print("🔍 关键函数识别")
        print("="*60)
        
        # 查找重要的函数模式
        key_patterns = {
            'callApi': r'(async\s+)?callApi\s*\([^)]*\)\s*\{',
            'fetch_calls': r'fetch\s*\(',
            'xhr_usage': r'XMLHttpRequest',
            'websocket': r'WebSocket',
            'event_listeners': r'addEventListener\s*\(',
            'dom_queries': r'querySelector\s*\(',
            'local_storage': r'localStorage\.',
            'session_storage': r'sessionStorage\.',
            'crypto_usage': r'crypto\.',
            'btoa_atob': r'\b(btoa|atob)\s*\(',
        }
        
        found_functions = {}
        for name, pattern in key_patterns.items():
            matches = list(re.finditer(pattern, self.content))
            found_functions[name] = len(matches)
            
            if matches:
                print(f"🎯 {name}: {len(matches)} 个匹配")
                # 显示第一个匹配的上下文
                first_match = matches[0]
                start = max(0, first_match.start() - 50)
                end = min(len(self.content), first_match.end() + 100)
                context = self.content[start:end].replace('\n', '\\n')
                print(f"   📍 位置 {first_match.start()}: ...{context[:100]}...")
        
        # 特别关注 callApi 函数
        callapi_matches = re.finditer(r'async\s+callApi\s*\([^)]*\)\s*\{', self.content)
        for i, match in enumerate(callapi_matches):
            print(f"\n🚀 CallApi 函数 #{i+1}:")
            print(f"   📍 位置: {match.start()}-{match.end()}")
            print(f"   🔤 签名: {match.group()}")
            
            # 分析函数参数
            params_match = re.search(r'\(([^)]*)\)', match.group())
            if params_match:
                params = params_match.group(1)
                param_list = [p.strip() for p in params.split(',') if p.strip()]
                print(f"   📋 参数数量: {len(param_list)}")
                print(f"   📝 参数列表: {param_list}")
        
        self.analysis_results['key_functions'] = found_functions
    
    def analyze_strings_and_urls(self):
        """分析字符串和URL"""
        print("\n" + "="*60)
        print("🔗 字符串和URL分析")
        print("="*60)
        
        # 查找字符串字面量
        string_patterns = {
            'double_quoted': r'"([^"\\\\]|\\\\.)*"',
            'single_quoted': r"'([^'\\\\]|\\\\.)*'",
            'template_literals': r'`([^`\\\\]|\\\\.)*`',
        }
        
        all_strings = []
        for pattern_name, pattern in string_patterns.items():
            matches = re.findall(pattern, self.content)
            print(f"📝 {pattern_name.replace('_', ' ').title()}: {len(matches):,}")
            all_strings.extend(matches)
        
        # 查找URL和域名
        url_patterns = {
            'http_urls': r'https?://[^\s"\'`<>]+',
            'domain_names': r'[a-zA-Z0-9-]+\.[a-zA-Z]{2,}',
            'api_endpoints': r'/api/[^\s"\'`<>]+',
            'file_paths': r'[./][a-zA-Z0-9_/-]+\.[a-zA-Z0-9]+',
        }
        
        found_urls = {}
        for pattern_name, pattern in url_patterns.items():
            matches = list(set(re.findall(pattern, self.content)))
            found_urls[pattern_name] = matches
            print(f"🌐 {pattern_name.replace('_', ' ').title()}: {len(matches)}")
            
            # 显示前几个匹配
            for url in matches[:5]:
                print(f"   📎 {url}")
            if len(matches) > 5:
                print(f"   ... 还有 {len(matches) - 5} 个")
        
        # 查找可疑的字符串
        suspicious_patterns = {
            'base64_like': r'[A-Za-z0-9+/]{20,}={0,2}',
            'hex_strings': r'[0-9a-fA-F]{16,}',
            'tokens': r'(token|key|secret|password|auth)["\']?\s*[:=]\s*["\'][^"\']+["\']',
        }
        
        print(f"\n🚨 可疑字符串:")
        for pattern_name, pattern in suspicious_patterns.items():
            matches = re.findall(pattern, self.content, re.IGNORECASE)
            if matches:
                print(f"⚠️ {pattern_name.replace('_', ' ').title()}: {len(matches)}")
                for match in matches[:3]:
                    print(f"   🔍 {str(match)[:50]}...")
        
        self.analysis_results['strings'] = {
            'counts': {name: len(re.findall(pattern, self.content)) for name, pattern in string_patterns.items()},
            'urls': found_urls
        }
    
    def detect_telemetry_code(self):
        """检测遥测相关代码"""
        print("\n" + "="*60)
        print("📊 遥测代码检测")
        print("="*60)
        
        # 遥测相关关键词
        telemetry_keywords = [
            'telemetry', 'analytics', 'tracking', 'metrics', 'usage',
            'report', 'record', 'log', 'event', 'session', 'user-agent',
            'fingerprint', 'identifier', 'uuid', 'guid', 'machineId',
            'deviceId', 'sessionId', 'userId', 'clientId'
        ]
        
        found_telemetry = {}
        for keyword in telemetry_keywords:
            # 不区分大小写搜索
            pattern = re.compile(keyword, re.IGNORECASE)
            matches = pattern.findall(self.content)
            if matches:
                found_telemetry[keyword] = len(matches)
                print(f"📡 {keyword}: {len(matches)} 次")
        
        # 查找遥测相关的函数调用
        telemetry_functions = [
            r'report[A-Z]\w*\s*\(',
            r'track[A-Z]\w*\s*\(',
            r'log[A-Z]\w*\s*\(',
            r'send[A-Z]\w*\s*\(',
            r'collect[A-Z]\w*\s*\(',
        ]
        
        print(f"\n🔧 遥测函数:")
        for pattern in telemetry_functions:
            matches = re.findall(pattern, self.content)
            if matches:
                print(f"⚙️ {pattern}: {len(matches)} 个匹配")
                for match in matches[:3]:
                    print(f"   📞 {match}")
        
        # 查找数据收集相关的代码
        data_collection_patterns = {
            'user_agent': r'navigator\.userAgent',
            'screen_info': r'screen\.(width|height|availWidth|availHeight)',
            'timezone': r'Intl\.DateTimeFormat\(\)\.resolvedOptions\(\)\.timeZone',
            'language': r'navigator\.language',
            'platform': r'navigator\.platform',
            'cookies': r'document\.cookie',
            'local_storage_access': r'localStorage\.(getItem|setItem)',
        }
        
        print(f"\n🕵️ 数据收集模式:")
        for name, pattern in data_collection_patterns.items():
            matches = re.findall(pattern, self.content)
            if matches:
                print(f"🎯 {name.replace('_', ' ').title()}: {len(matches)} 次")
        
        self.analysis_results['telemetry'] = {
            'keywords': found_telemetry,
            'data_collection': {name: len(re.findall(pattern, self.content)) 
                              for name, pattern in data_collection_patterns.items()}
        }
    
    def analyze_patch_points(self):
        """分析可能的补丁点"""
        print("\n" + "="*60)
        print("🎯 补丁点分析")
        print("="*60)
        
        # 查找 callApi 函数的详细信息
        callapi_pattern = r'async\s+callApi\s*\([^)]*\)\s*\{'
        matches = list(re.finditer(callapi_pattern, self.content))
        
        if matches:
            for i, match in enumerate(matches):
                print(f"\n🚀 CallApi 函数 #{i+1} 详细分析:")
                print(f"   📍 起始位置: {match.start()}")
                print(f"   📍 结束位置: {match.end()}")
                
                # 分析函数体的开始部分
                func_start = match.end()
                func_body_preview = self.content[func_start:func_start+500]
                
                print(f"   📝 函数体预览:")
                print(f"   {repr(func_body_preview[:200])}...")
                
                # 查找函数体中的关键模式
                body_patterns = {
                    'if_statements': r'\bif\s*\(',
                    'return_statements': r'\breturn\s+',
                    'variable_assignments': r'\w+\s*=\s*',
                    'function_calls': r'\w+\s*\(',
                    'string_checks': r'startsWith\s*\(',
                }
                
                print(f"   🔍 函数体模式:")
                for pattern_name, pattern in body_patterns.items():
                    pattern_matches = re.findall(pattern, func_body_preview)
                    if pattern_matches:
                        print(f"     {pattern_name}: {len(pattern_matches)}")
                
                # 检查是否已经被补丁
                patch_indicators = [
                    'startsWith("report-")',
                    'startsWith("record-")',
                    'randSessionId',
                    'this._userAgent = ""'
                ]
                
                is_patched = False
                for indicator in patch_indicators:
                    if indicator in func_body_preview:
                        is_patched = True
                        print(f"   ✅ 发现补丁标识: {indicator}")
                
                if is_patched:
                    print(f"   🎯 状态: 已补丁")
                else:
                    print(f"   🎯 状态: 未补丁")
                    print(f"   💡 建议补丁位置: 位置 {func_start} (函数开始大括号后)")
        else:
            print("❌ 未找到 callApi 函数")
        
        # 查找其他可能的补丁点
        other_patch_points = {
            'fetch_calls': r'fetch\s*\([^)]*\)',
            'xhr_send': r'\.send\s*\(',
            'websocket_send': r'\.send\s*\(',
            'postMessage': r'postMessage\s*\(',
        }
        
        print(f"\n🔧 其他潜在补丁点:")
        for name, pattern in other_patch_points.items():
            matches = list(re.finditer(pattern, self.content))
            if matches:
                print(f"🎯 {name}: {len(matches)} 个位置")
                for match in matches[:3]:
                    print(f"   📍 位置 {match.start()}: {match.group()}")
    
    def generate_report(self):
        """生成分析报告"""
        print("\n" + "="*60)
        print("📋 分析报告生成")
        print("="*60)
        
        report = {
            'file_info': {
                'path': str(self.file_path),
                'size': len(self.content),
                'analysis_timestamp': __import__('datetime').datetime.now().isoformat()
            },
            'analysis_results': self.analysis_results
        }
        
        # 保存报告到JSON文件
        report_file = self.file_path.parent / f"{self.file_path.stem}_analysis_report.json"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"✅ 分析报告已保存: {report_file}")
        except Exception as e:
            print(f"❌ 保存报告失败: {e}")
        
        # 生成摘要
        print(f"\n📊 分析摘要:")
        print(f"   📁 文件大小: {len(self.content):,} 字符")
        print(f"   🔒 混淆评分: {self.analysis_results.get('obfuscation', {}).get('score', 0)}/10")
        
        if 'key_functions' in self.analysis_results:
            callapi_count = self.analysis_results['key_functions'].get('callApi', 0)
            print(f"   🚀 CallApi 函数: {callapi_count} 个")
        
        if 'telemetry' in self.analysis_results:
            telemetry_keywords = len(self.analysis_results['telemetry']['keywords'])
            print(f"   📡 遥测关键词: {telemetry_keywords} 种")
        
        return report

def main():
    """主函数"""
    print("🔍 AugmentCode Extension.js 反编译分析工具")
    print("="*60)
    
    # 分析项目目录中的 extension.js
    file_path = "extension.js"
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return
    
    analyzer = ExtensionAnalyzer(file_path)
    
    # 执行分析步骤
    if analyzer.load_file():
        analyzer.basic_analysis()
        analyzer.detect_obfuscation()
        analyzer.analyze_structure()
        analyzer.find_key_functions()
        analyzer.analyze_strings_and_urls()
        analyzer.detect_telemetry_code()
        analyzer.analyze_patch_points()
        analyzer.generate_report()
    
    print(f"\n✅ 分析完成!")

if __name__ == "__main__":
    main()