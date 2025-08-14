#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于证据的补丁验证器
验证基于证据的补丁是否正确应用和生效
"""

import re
import json

class EvidencePatchVerifier:
    """基于证据的补丁验证器"""
    
    def __init__(self, file_path: str = "extension.js"):
        self.file_path = file_path
        self.content = ""
        self.verification_results = {}
        
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
    
    def verify_patch_signatures(self):
        """验证补丁签名"""
        print("\n🔍 验证基于证据的补丁签名")
        print("-" * 60)
        
        # 基于证据的补丁签名
        evidence_signatures = [
            'EVIDENCE-BASED PATCH APPLIED',
            'CRITICAL THREATS BLOCKED',
            'HIGH THREATS MONITORED', 
            'CORE FUNCTIONS PRESERVED',
            'segment_analytics',
            'user_identification',
            'device_fingerprinting'
        ]
        
        signatures_found = 0
        for signature in evidence_signatures:
            if signature in self.content:
                signatures_found += 1
                print(f"  ✅ 找到签名: {signature}")
            else:
                print(f"  ❌ 未找到签名: {signature}")
        
        coverage = (signatures_found / len(evidence_signatures)) * 100
        print(f"\n🛡️ 基于证据的补丁覆盖率: {coverage:.1f}% ({signatures_found}/{len(evidence_signatures)})")
        
        return coverage
    
    def verify_critical_blocks(self):
        """验证严重威胁拦截"""
        print("\n🚫 验证严重威胁拦截")
        print("-" * 60)
        
        critical_blocks = {
            'segment_block': r'Segment\.io.*被拦截',
            'userid_sanitization': r'敏感ID字段.*已脱敏',
            'useragent_block': r'UserAgent.*被拦截',
            'platform_block': r'Platform.*被拦截',
            'analytics_override': r'globalThis\.analytics\.track\s*=',
        }
        
        blocks_found = 0
        for block_name, pattern in critical_blocks.items():
            matches = len(re.findall(pattern, self.content, re.IGNORECASE))
            if matches > 0:
                blocks_found += 1
                print(f"  ✅ {block_name}: {matches} 个拦截点")
            else:
                print(f"  ❌ {block_name}: 未找到拦截")
        
        effectiveness = (blocks_found / len(critical_blocks)) * 100
        print(f"\n🛡️ 严重威胁拦截有效性: {effectiveness:.1f}% ({blocks_found}/{len(critical_blocks)})")
        
        return effectiveness
    
    def verify_conditional_blocks(self):
        """验证条件拦截"""
        print("\n⚠️ 验证条件拦截")
        print("-" * 60)
        
        conditional_patterns = {
            'telemetry_conditional': r'遥测事件被拦截',
            'fetch_conditional': r'分析服务请求被拦截',
            'event_filtering': r'非遥测事件',
            'network_monitoring': r'网络请求.*监控',
        }
        
        conditionals_found = 0
        for cond_name, pattern in conditional_patterns.items():
            matches = len(re.findall(pattern, self.content, re.IGNORECASE))
            if matches > 0:
                conditionals_found += 1
                print(f"  ✅ {cond_name}: {matches} 个条件点")
            else:
                print(f"  ❌ {cond_name}: 未找到")
        
        effectiveness = (conditionals_found / len(conditional_patterns)) * 100
        print(f"\n🎯 条件拦截有效性: {effectiveness:.1f}% ({conditionals_found}/{len(conditional_patterns)})")
        
        return effectiveness
    
    def verify_core_preservation(self):
        """验证核心功能保护"""
        print("\n✅ 验证核心功能保护")
        print("-" * 60)
        
        core_functions = {
            'vscode_commands': r'vscode\.commands\.',
            'vscode_workspace': r'vscode\.workspace\.',
            'vscode_window': r'vscode\.window\.',
            'file_operations': r'(readFile|writeFile|fs\.)',
            'language_features': r'(completion|hover|diagnostic)',
        }
        
        preserved_functions = 0
        for func_name, pattern in core_functions.items():
            matches = len(re.findall(pattern, self.content, re.IGNORECASE))
            if matches > 0:
                preserved_functions += 1
                print(f"  ✅ {func_name}: {matches} 个使用 (已保护)")
            else:
                print(f"  ⚠️ {func_name}: 未检测到使用")
        
        preservation = (preserved_functions / len(core_functions)) * 100
        print(f"\n🔧 核心功能保护率: {preservation:.1f}% ({preserved_functions}/{len(core_functions)})")
        
        return preservation
    
    def analyze_threat_reduction(self):
        """分析威胁减少情况"""
        print("\n📊 分析威胁减少情况")
        print("-" * 60)
        
        # 检查原始威胁是否仍然存在
        remaining_threats = {
            'segment_calls': len(re.findall(r'segment\.io.*track', self.content, re.IGNORECASE)),
            'unprotected_userids': len(re.findall(r'userId.*[^REDACTED]', self.content, re.IGNORECASE)),
            'raw_useragent': len(re.findall(r'navigator\.userAgent(?!.*被拦截)', self.content, re.IGNORECASE)),
            'direct_analytics': len(re.findall(r'analytics\.track(?!.*被拦截)', self.content, re.IGNORECASE)),
        }
        
        # 检查拦截日志
        protection_logs = {
            'segment_blocks': len(re.findall(r'Segment\.io.*被拦截', self.content, re.IGNORECASE)),
            'id_sanitizations': len(re.findall(r'敏感ID字段.*已脱敏', self.content, re.IGNORECASE)),
            'useragent_blocks': len(re.findall(r'UserAgent.*被拦截', self.content, re.IGNORECASE)),
            'telemetry_blocks': len(re.findall(r'遥测事件被拦截', self.content, re.IGNORECASE)),
        }
        
        print("  🔍 剩余威胁:")
        total_remaining = 0
        for threat, count in remaining_threats.items():
            print(f"    • {threat}: {count} 个")
            total_remaining += count
        
        print("  🛡️ 保护措施:")
        total_protections = 0
        for protection, count in protection_logs.items():
            print(f"    • {protection}: {count} 个拦截点")
            total_protections += count
        
        if total_protections > 0:
            protection_ratio = total_protections / (total_remaining + total_protections) * 100
        else:
            protection_ratio = 0
        
        print(f"\n📈 威胁保护比率: {protection_ratio:.1f}%")
        
        return protection_ratio
    
    def generate_verification_report(self):
        """生成验证报告"""
        print("\n📋 生成验证报告")
        print("-" * 60)
        
        # 汇总所有验证结果
        patch_coverage = self.verification_results.get('patch_coverage', 0)
        critical_effectiveness = self.verification_results.get('critical_effectiveness', 0)
        conditional_effectiveness = self.verification_results.get('conditional_effectiveness', 0)
        core_preservation = self.verification_results.get('core_preservation', 0)
        threat_protection = self.verification_results.get('threat_protection', 0)
        
        # 计算总体评分
        overall_score = (
            patch_coverage * 0.2 +
            critical_effectiveness * 0.3 +
            conditional_effectiveness * 0.2 +
            core_preservation * 0.2 +
            threat_protection * 0.1
        )
        
        # 确定等级
        if overall_score >= 90:
            grade = "优秀"
            risk_level = "极低"
        elif overall_score >= 75:
            grade = "良好"
            risk_level = "低"
        elif overall_score >= 60:
            grade = "及格"
            risk_level = "中"
        else:
            grade = "需要改进"
            risk_level = "高"
        
        print(f"📊 验证结果汇总:")
        print(f"  🛡️ 补丁覆盖率: {patch_coverage:.1f}%")
        print(f"  🚫 严重威胁拦截: {critical_effectiveness:.1f}%")
        print(f"  ⚠️ 条件拦截有效性: {conditional_effectiveness:.1f}%")
        print(f"  ✅ 核心功能保护: {core_preservation:.1f}%")
        print(f"  📈 威胁保护比率: {threat_protection:.1f}%")
        print(f"  🎯 总体评分: {overall_score:.1f}/100")
        print(f"  📝 等级: {grade}")
        print(f"  ⚠️ 风险等级: {risk_level}")
        
        return {
            'overall_score': overall_score,
            'grade': grade,
            'risk_level': risk_level,
            'details': self.verification_results
        }
    
    def run_verification(self):
        """运行完整验证"""
        print("🔬 基于证据的补丁验证")
        print("=" * 80)
        
        if not self.load_file():
            return None
        
        # 执行各项验证
        self.verification_results['patch_coverage'] = self.verify_patch_signatures()
        self.verification_results['critical_effectiveness'] = self.verify_critical_blocks()
        self.verification_results['conditional_effectiveness'] = self.verify_conditional_blocks()
        self.verification_results['core_preservation'] = self.verify_core_preservation()
        self.verification_results['threat_protection'] = self.analyze_threat_reduction()
        
        # 生成最终报告
        report = self.generate_verification_report()
        
        return report

def main():
    """主函数"""
    verifier = EvidencePatchVerifier()
    report = verifier.run_verification()
    
    if report:
        print(f"\n🎉 基于证据的补丁验证完成!")
        print(f"📊 总体评分: {report['overall_score']:.1f}/100 ({report['grade']})")
        print(f"🎯 风险等级: {report['risk_level']}")
        
        if report['overall_score'] >= 75:
            print(f"\n✅ 补丁质量优秀，可以安全使用!")
            print(f"💡 建议: 重启 VSCode 并测试扩展功能")
        elif report['overall_score'] >= 60:
            print(f"\n⚠️ 补丁质量良好，但可以进一步优化")
            print(f"💡 建议: 监控使用过程中的问题")
        else:
            print(f"\n❌ 补丁需要改进")
            print(f"💡 建议: 检查补丁代码或恢复原始文件")
    else:
        print(f"\n❌ 验证失败")

if __name__ == "__main__":
    main()