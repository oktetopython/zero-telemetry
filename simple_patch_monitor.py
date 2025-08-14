#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单补丁监控器
实时监控补丁状态和扩展健康度
"""

import os
import re
import time
import json
from datetime import datetime
from pathlib import Path

class SimplePatchMonitor:
    """简单补丁监控器"""
    
    def __init__(self):
        self.extension_file = "extension.js"
        self.monitoring_data = {
            'patch_status': 'unknown',
            'last_check': None,
            'issues_found': [],
            'recommendations': []
        }
    
    def check_patch_integrity(self):
        """检查补丁完整性"""
        print("🔍 检查补丁完整性...")
        
        if not os.path.exists(self.extension_file):
            self.monitoring_data['patch_status'] = 'file_missing'
            self.monitoring_data['issues_found'].append("扩展文件不存在")
            return False
        
        try:
            with open(self.extension_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查关键补丁签名
            required_signatures = [
                'EVIDENCE-BASED PATCH APPLIED',
                'CRITICAL THREATS BLOCKED',
                'Segment.io 分析调用被拦截',
                '敏感ID字段',
                'UserAgent 访问被拦截'
            ]
            
            missing_signatures = []
            for signature in required_signatures:
                if signature not in content:
                    missing_signatures.append(signature)
            
            if missing_signatures:
                self.monitoring_data['patch_status'] = 'incomplete'
                self.monitoring_data['issues_found'].extend([f"缺失签名: {sig}" for sig in missing_signatures])
                print(f"  ⚠️ 补丁不完整，缺失 {len(missing_signatures)} 个签名")
                return False
            else:
                self.monitoring_data['patch_status'] = 'healthy'
                print(f"  ✅ 补丁完整性检查通过")
                return True
                
        except Exception as e:
            self.monitoring_data['patch_status'] = 'error'
            self.monitoring_data['issues_found'].append(f"检查失败: {e}")
            print(f"  ❌ 检查失败: {e}")
            return False
    
    def check_vscode_console_logs(self):
        """检查 VSCode 控制台日志（模拟）"""
        print("🔍 检查控制台日志...")
        
        # 这里我们检查是否有补丁相关的日志输出代码
        try:
            with open(self.extension_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找日志输出代码
            log_patterns = [
                r'console\.log.*CRITICAL BLOCK',
                r'console\.log.*HIGH BLOCK', 
                r'console\.log.*NETWORK MONITOR',
                r'console\.log.*EVIDENCE-BASED PATCH'
            ]
            
            log_count = 0
            for pattern in log_patterns:
                matches = len(re.findall(pattern, content, re.IGNORECASE))
                log_count += matches
            
            if log_count > 0:
                print(f"  ✅ 找到 {log_count} 个日志输出点")
                print(f"  💡 在 VSCode 开发者控制台中查看实时日志")
                return True
            else:
                print(f"  ⚠️ 未找到日志输出代码")
                self.monitoring_data['issues_found'].append("缺少日志输出")
                return False
                
        except Exception as e:
            print(f"  ❌ 检查日志代码失败: {e}")
            return False
    
    def check_extension_functionality(self):
        """检查扩展功能完整性"""
        print("🔍 检查扩展功能完整性...")
        
        try:
            with open(self.extension_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查核心功能是否被保留
            core_functions = {
                'file_operations': r'(readFile|writeFile|fs\.)',
                'vscode_apis': r'vscode\.',
                'command_handlers': r'(registerCommand|executeCommand)',
                'language_features': r'(completion|hover|diagnostic)'
            }
            
            preserved_functions = 0
            for func_name, pattern in core_functions.items():
                matches = len(re.findall(pattern, content, re.IGNORECASE))
                if matches > 0:
                    preserved_functions += 1
                    print(f"  ✅ {func_name}: {matches} 个使用点")
                else:
                    print(f"  ⚠️ {func_name}: 未检测到")
            
            preservation_rate = (preserved_functions / len(core_functions)) * 100
            print(f"  📊 功能保留率: {preservation_rate:.1f}%")
            
            if preservation_rate >= 50:
                return True
            else:
                self.monitoring_data['issues_found'].append(f"功能保留率过低: {preservation_rate:.1f}%")
                return False
                
        except Exception as e:
            print(f"  ❌ 检查功能完整性失败: {e}")
            return False
    
    def generate_recommendations(self):
        """生成建议"""
        print("\n💡 生成监控建议...")
        
        recommendations = []
        
        # 基于补丁状态生成建议
        if self.monitoring_data['patch_status'] == 'healthy':
            recommendations.extend([
                "✅ 补丁状态良好，继续正常使用",
                "🔍 定期运行监控检查补丁完整性",
                "👁️ 在 VSCode 开发者控制台观察拦截日志"
            ])
        elif self.monitoring_data['patch_status'] == 'incomplete':
            recommendations.extend([
                "⚠️ 补丁不完整，建议重新应用补丁",
                "🔧 运行: python evidence_based_patch_generator.py",
                "🔍 检查是否有其他进程修改了扩展文件"
            ])
        elif self.monitoring_data['patch_status'] == 'file_missing':
            recommendations.extend([
                "❌ 扩展文件丢失，需要重新安装扩展",
                "📦 重新安装 VSCode Augment 扩展",
                "🔧 然后重新应用隐私补丁"
            ])
        
        # 基于发现的问题生成建议
        if self.monitoring_data['issues_found']:
            recommendations.append("🔧 解决发现的问题:")
            for issue in self.monitoring_data['issues_found']:
                recommendations.append(f"  • {issue}")
        
        # 通用监控建议
        recommendations.extend([
            "",
            "📋 日常监控建议:",
            "• 每天运行一次补丁完整性检查",
            "• 观察 VSCode 控制台的拦截日志",
            "• 注意扩展功能是否正常工作",
            "• 如有异常立即运行完整验证"
        ])
        
        self.monitoring_data['recommendations'] = recommendations
        
        for rec in recommendations:
            print(f"  {rec}")
    
    def save_monitoring_report(self):
        """保存监控报告"""
        self.monitoring_data['last_check'] = datetime.now().isoformat()
        
        report_file = f"patch_monitoring_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.monitoring_data, f, indent=2, ensure_ascii=False)
            print(f"\n✅ 监控报告已保存: {report_file}")
        except Exception as e:
            print(f"\n❌ 保存报告失败: {e}")
    
    def run_quick_check(self):
        """运行快速检查"""
        print("🚀 运行快速补丁监控检查")
        print("=" * 60)
        
        # 清空之前的数据
        self.monitoring_data['issues_found'] = []
        self.monitoring_data['recommendations'] = []
        
        # 执行检查
        integrity_ok = self.check_patch_integrity()
        logs_ok = self.check_vscode_console_logs()
        functionality_ok = self.check_extension_functionality()
        
        # 生成建议
        self.generate_recommendations()
        
        # 保存报告
        self.save_monitoring_report()
        
        # 总结
        print("\n" + "=" * 60)
        print("📊 监控检查总结")
        print("=" * 60)
        
        checks = [
            ("补丁完整性", integrity_ok),
            ("日志输出", logs_ok),
            ("功能完整性", functionality_ok)
        ]
        
        passed_checks = sum(1 for _, ok in checks if ok)
        total_checks = len(checks)
        
        for check_name, ok in checks:
            status = "✅ 通过" if ok else "❌ 失败"
            print(f"  {check_name}: {status}")
        
        print(f"\n🎯 总体状态: {passed_checks}/{total_checks} 项检查通过")
        
        if passed_checks == total_checks:
            print("🎉 所有检查通过，补丁运行良好！")
            return True
        elif passed_checks >= total_checks * 0.7:
            print("⚠️ 大部分检查通过，但需要关注问题")
            return True
        else:
            print("❌ 多项检查失败，需要立即处理")
            return False

def create_monitoring_schedule():
    """创建监控计划脚本"""
    schedule_script = '''@echo off
REM 补丁监控计划脚本
REM 每小时运行一次补丁检查

echo 开始定时补丁监控...
python simple_patch_monitor.py

REM 等待用户查看结果
pause
'''
    
    with open('monitor_schedule.bat', 'w', encoding='utf-8') as f:
        f.write(schedule_script)
    
    print("✅ 监控计划脚本已创建: monitor_schedule.bat")

def main():
    """主函数"""
    monitor = SimplePatchMonitor()
    
    print("🔍 简单补丁监控器")
    print("=" * 50)
    print("选择操作:")
    print("1. 运行快速检查")
    print("2. 创建监控计划")
    print("3. 查看监控指南")
    print("4. 退出")
    
    choice = input("\n请选择 (1-4): ").strip()
    
    if choice == '1':
        success = monitor.run_quick_check()
        
        if success:
            print("\n💡 下一步:")
            print("• 重启 VSCode 测试扩展功能")
            print("• 打开开发者控制台 (Ctrl+Shift+I)")
            print("• 查看是否有 [CRITICAL BLOCK] 等日志")
        else:
            print("\n🔧 需要处理的问题:")
            for issue in monitor.monitoring_data['issues_found']:
                print(f"  • {issue}")
    
    elif choice == '2':
        create_monitoring_schedule()
        print("\n💡 使用方法:")
        print("• 双击 monitor_schedule.bat 运行定时检查")
        print("• 或设置 Windows 任务计划程序定时执行")
    
    elif choice == '3':
        print("\n📋 监控指南:")
        print("=" * 50)
        print("🎯 监控目标:")
        print("• 确保补丁完整性不被破坏")
        print("• 验证隐私保护功能正常工作")
        print("• 检测扩展功能是否受影响")
        print("• 及时发现和解决问题")
        
        print("\n🔍 监控方法:")
        print("1. 定期运行快速检查 (建议每天1次)")
        print("2. 观察 VSCode 开发者控制台日志")
        print("3. 测试扩展的核心功能")
        print("4. 关注 VSCode 的错误提示")
        
        print("\n⚠️ 警报信号:")
        print("• 扩展功能异常或无法使用")
        print("• 控制台出现大量错误")
        print("• 补丁签名检查失败")
        print("• 网络请求未被拦截")
        
        print("\n🔧 问题处理:")
        print("• 补丁丢失 → 重新应用补丁")
        print("• 功能异常 → 检查兼容性或恢复原文件")
        print("• 错误过多 → 调整补丁策略")
    
    else:
        print("退出监控器")

if __name__ == "__main__":
    main()