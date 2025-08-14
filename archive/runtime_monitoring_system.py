#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行时监控系统
实时监控补丁效果和扩展运行状态
"""

import os
import re
import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, deque

class RuntimeMonitoringSystem:
    """运行时监控系统"""
    
    def __init__(self):
        self.monitoring_active = False
        self.log_buffer = deque(maxlen=1000)  # 保留最近1000条日志
        self.statistics = defaultdict(int)
        self.alerts = []
        self.start_time = None
        
        # VSCode 日志路径
        self.vscode_log_paths = [
            os.path.expanduser("~/.vscode/logs"),
            os.path.expanduser("~/AppData/Roaming/Code/logs"),
            os.path.expanduser("~/Library/Application Support/Code/logs"),
        ]
        
        # 监控配置
        self.monitoring_config = {
            'check_interval': 5,  # 检查间隔（秒）
            'alert_threshold': 10,  # 错误阈值
            'log_retention_hours': 24,  # 日志保留时间
        }
    
    def start_monitoring(self):
        """启动监控"""
        print("🔍 启动运行时监控系统")
        print("=" * 60)
        
        self.monitoring_active = True
        self.start_time = datetime.now()
        
        # 启动监控线程
        monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        monitor_thread.start()
        
        print(f"✅ 监控系统已启动")
        print(f"📊 监控间隔: {self.monitoring_config['check_interval']} 秒")
        print(f"⚠️ 错误阈值: {self.monitoring_config['alert_threshold']} 个")
        
        return True
    
    def _monitoring_loop(self):
        """监控主循环"""
        while self.monitoring_active:
            try:
                # 检查 VSCode 日志
                self._check_vscode_logs()
                
                # 检查扩展状态
                self._check_extension_status()
                
                # 分析统计数据
                self._analyze_statistics()
                
                # 生成警报
                self._generate_alerts()
                
                time.sleep(self.monitoring_config['check_interval'])
                
            except Exception as e:
                self._log_event('ERROR', f"监控循环错误: {e}")
    
    def _check_vscode_logs(self):
        """检查 VSCode 日志"""
        for log_path in self.vscode_log_paths:
            if os.path.exists(log_path):
                self._scan_log_directory(log_path)
    
    def _scan_log_directory(self, log_dir):
        """扫描日志目录"""
        try:
            # 查找最新的日志文件
            log_files = []
            for root, dirs, files in os.walk(log_dir):
                for file in files:
                    if file.endswith('.log'):
                        file_path = os.path.join(root, file)
                        log_files.append((file_path, os.path.getmtime(file_path)))
            
            # 按修改时间排序，取最新的几个
            log_files.sort(key=lambda x: x[1], reverse=True)
            
            for file_path, _ in log_files[:3]:  # 只检查最新的3个日志文件
                self._analyze_log_file(file_path)
                
        except Exception as e:
            self._log_event('ERROR', f"扫描日志目录失败 {log_dir}: {e}")
    
    def _analyze_log_file(self, file_path):
        """分析日志文件"""
        try:
            # 只读取最近的日志内容
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # 读取文件末尾的内容
                f.seek(0, 2)  # 移到文件末尾
                file_size = f.tell()
                
                # 读取最后 10KB 的内容
                read_size = min(10240, file_size)
                f.seek(file_size - read_size)
                content = f.read()
            
            # 分析日志内容
            self._parse_log_content(content, file_path)
            
        except Exception as e:
            self._log_event('ERROR', f"分析日志文件失败 {file_path}: {e}")
    
    def _parse_log_content(self, content, file_path):
        """解析日志内容"""
        # 查找补丁相关的日志
        patch_patterns = {
            'critical_block': r'\[CRITICAL BLOCK\]',
            'high_block': r'\[HIGH BLOCK\]',
            'network_monitor': r'\[NETWORK MONITOR\]',
            'error_monitor': r'\[ERROR MONITOR\]',
            'evidence_patch': r'\[EVIDENCE-BASED PATCH\]',
        }
        
        # 查找错误模式
        error_patterns = {
            'extension_error': r'Extension.*error',
            'activation_failed': r'activation.*failed',
            'command_error': r'command.*error',
            'network_error': r'network.*error',
            'timeout_error': r'timeout',
        }
        
        lines = content.split('\n')
        for line in lines[-100:]:  # 只分析最后100行
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            # 检查补丁活动
            for pattern_name, pattern in patch_patterns.items():
                if re.search(pattern, line, re.IGNORECASE):
                    self.statistics[f'patch_{pattern_name}'] += 1
                    self._log_event('PATCH', f"{pattern_name}: {line.strip()[:100]}")
            
            # 检查错误
            for error_name, pattern in error_patterns.items():
                if re.search(pattern, line, re.IGNORECASE):
                    self.statistics[f'error_{error_name}'] += 1
                    self._log_event('ERROR', f"{error_name}: {line.strip()[:100]}")
    
    def _check_extension_status(self):
        """检查扩展状态"""
        # 检查扩展文件是否存在
        if os.path.exists("extension.js"):
            file_size = os.path.getsize("extension.js")
            self.statistics['extension_file_size'] = file_size
            
            # 检查补丁签名是否还在
            try:
                with open("extension.js", 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'EVIDENCE-BASED PATCH APPLIED' in content:
                    self.statistics['patch_integrity'] = 1
                    self._log_event('STATUS', "补丁完整性检查通过")
                else:
                    self.statistics['patch_integrity'] = 0
                    self._log_event('WARNING', "补丁签名丢失！")
                    
            except Exception as e:
                self._log_event('ERROR', f"检查扩展文件失败: {e}")
    
    def _analyze_statistics(self):
        """分析统计数据"""
        if not self.start_time:
            return
        
        runtime = datetime.now() - self.start_time
        
        # 计算关键指标
        total_blocks = sum(v for k, v in self.statistics.items() if k.startswith('patch_'))
        total_errors = sum(v for k, v in self.statistics.items() if k.startswith('error_'))
        
        self.statistics['runtime_minutes'] = runtime.total_seconds() / 60
        self.statistics['total_patch_activities'] = total_blocks
        self.statistics['total_errors'] = total_errors
        
        # 计算错误率
        if total_blocks > 0:
            error_rate = (total_errors / (total_blocks + total_errors)) * 100
            self.statistics['error_rate'] = error_rate
    
    def _generate_alerts(self):
        """生成警报"""
        current_time = datetime.now()
        
        # 检查错误阈值
        if self.statistics['total_errors'] > self.monitoring_config['alert_threshold']:
            alert = {
                'timestamp': current_time,
                'level': 'HIGH',
                'message': f"错误数量超过阈值: {self.statistics['total_errors']}",
                'recommendation': "建议检查 VSCode 日志或恢复原始扩展文件"
            }
            self.alerts.append(alert)
            self._log_event('ALERT', alert['message'])
        
        # 检查补丁完整性
        if self.statistics.get('patch_integrity', 1) == 0:
            alert = {
                'timestamp': current_time,
                'level': 'CRITICAL',
                'message': "补丁完整性检查失败",
                'recommendation': "补丁可能被覆盖，需要重新应用"
            }
            self.alerts.append(alert)
            self._log_event('ALERT', alert['message'])
        
        # 检查错误率
        error_rate = self.statistics.get('error_rate', 0)
        if error_rate > 20:  # 错误率超过20%
            alert = {
                'timestamp': current_time,
                'level': 'MEDIUM',
                'message': f"错误率过高: {error_rate:.1f}%",
                'recommendation': "建议调整补丁策略或检查兼容性"
            }
            self.alerts.append(alert)
    
    def _log_event(self, level, message):
        """记录事件"""
        event = {
            'timestamp': datetime.now(),
            'level': level,
            'message': message
        }
        self.log_buffer.append(event)
    
    def get_monitoring_report(self):
        """获取监控报告"""
        if not self.start_time:
            return None
        
        runtime = datetime.now() - self.start_time
        
        report = {
            'monitoring_status': 'ACTIVE' if self.monitoring_active else 'STOPPED',
            'runtime': {
                'started_at': self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                'duration_minutes': runtime.total_seconds() / 60,
            },
            'statistics': dict(self.statistics),
            'recent_events': list(self.log_buffer)[-20:],  # 最近20个事件
            'alerts': self.alerts[-10:],  # 最近10个警报
            'summary': {
                'total_patch_activities': self.statistics.get('total_patch_activities', 0),
                'total_errors': self.statistics.get('total_errors', 0),
                'error_rate': self.statistics.get('error_rate', 0),
                'patch_integrity': 'OK' if self.statistics.get('patch_integrity', 0) == 1 else 'FAILED',
            }
        }
        
        return report
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring_active = False
        self._log_event('INFO', "监控系统已停止")

class MonitoringDashboard:
    """监控仪表板"""
    
    def __init__(self, monitor_system):
        self.monitor = monitor_system
    
    def display_dashboard(self):
        """显示监控仪表板"""
        report = self.monitor.get_monitoring_report()
        if not report:
            print("❌ 监控系统未启动")
            return
        
        print("\n" + "=" * 80)
        print("📊 运行时监控仪表板")
        print("=" * 80)
        
        # 基本状态
        print(f"🔍 监控状态: {report['monitoring_status']}")
        print(f"⏰ 运行时间: {report['runtime']['duration_minutes']:.1f} 分钟")
        print(f"📅 开始时间: {report['runtime']['started_at']}")
        
        # 关键指标
        summary = report['summary']
        print(f"\n📈 关键指标:")
        print(f"  🛡️ 补丁活动: {summary['total_patch_activities']} 次")
        print(f"  ❌ 错误总数: {summary['total_errors']} 个")
        print(f"  📊 错误率: {summary['error_rate']:.1f}%")
        print(f"  🔒 补丁完整性: {summary['patch_integrity']}")
        
        # 最近事件
        print(f"\n📋 最近事件:")
        for event in report['recent_events'][-5:]:
            timestamp = event['timestamp'].strftime('%H:%M:%S')
            level_icon = {'INFO': 'ℹ️', 'WARNING': '⚠️', 'ERROR': '❌', 'PATCH': '🛡️', 'STATUS': '📊', 'ALERT': '🚨'}.get(event['level'], '📝')
            print(f"  {level_icon} {timestamp} [{event['level']}] {event['message'][:60]}...")
        
        # 警报
        if report['alerts']:
            print(f"\n🚨 活跃警报:")
            for alert in report['alerts'][-3:]:
                timestamp = alert['timestamp'].strftime('%H:%M:%S')
                level_icon = {'LOW': '🟡', 'MEDIUM': '🟠', 'HIGH': '🔴', 'CRITICAL': '💀'}.get(alert['level'], '⚠️')
                print(f"  {level_icon} {timestamp} [{alert['level']}] {alert['message']}")
                print(f"    💡 建议: {alert['recommendation']}")
        else:
            print(f"\n✅ 无活跃警报")
    
    def display_detailed_statistics(self):
        """显示详细统计"""
        report = self.monitor.get_monitoring_report()
        if not report:
            return
        
        print(f"\n📊 详细统计数据:")
        print("-" * 60)
        
        stats = report['statistics']
        
        # 补丁活动统计
        patch_stats = {k: v for k, v in stats.items() if k.startswith('patch_')}
        if patch_stats:
            print(f"🛡️ 补丁活动:")
            for key, value in patch_stats.items():
                activity_name = key.replace('patch_', '').replace('_', ' ').title()
                print(f"  • {activity_name}: {value} 次")
        
        # 错误统计
        error_stats = {k: v for k, v in stats.items() if k.startswith('error_')}
        if error_stats:
            print(f"\n❌ 错误统计:")
            for key, value in error_stats.items():
                error_name = key.replace('error_', '').replace('_', ' ').title()
                print(f"  • {error_name}: {value} 次")
        
        # 其他统计
        other_stats = {k: v for k, v in stats.items() if not k.startswith(('patch_', 'error_'))}
        if other_stats:
            print(f"\n📈 其他指标:")
            for key, value in other_stats.items():
                metric_name = key.replace('_', ' ').title()
                if isinstance(value, float):
                    print(f"  • {metric_name}: {value:.2f}")
                else:
                    print(f"  • {metric_name}: {value}")

def create_monitoring_script():
    """创建监控脚本"""
    script_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速监控脚本
用于快速检查补丁状态和扩展运行情况
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from runtime_monitoring_system import RuntimeMonitoringSystem, MonitoringDashboard

def main():
    """主函数"""
    print("🔍 VSCode Augment 扩展监控")
    print("=" * 50)
    
    monitor = RuntimeMonitoringSystem()
    dashboard = MonitoringDashboard(monitor)
    
    print("选择操作:")
    print("1. 启动持续监控")
    print("2. 快速状态检查")
    print("3. 查看详细统计")
    print("4. 退出")
    
    choice = input("\\n请选择 (1-4): ").strip()
    
    if choice == '1':
        print("\\n启动持续监控...")
        monitor.start_monitoring()
        
        try:
            while True:
                input("\\n按 Enter 查看仪表板 (Ctrl+C 退出)...")
                dashboard.display_dashboard()
        except KeyboardInterrupt:
            print("\\n停止监控...")
            monitor.stop_monitoring()
            
    elif choice == '2':
        print("\\n执行快速检查...")
        monitor.start_monitoring()
        import time
        time.sleep(2)  # 等待收集一些数据
        dashboard.display_dashboard()
        monitor.stop_monitoring()
        
    elif choice == '3':
        print("\\n查看详细统计...")
        monitor.start_monitoring()
        import time
        time.sleep(2)
        dashboard.display_detailed_statistics()
        monitor.stop_monitoring()
        
    else:
        print("退出监控")

if __name__ == "__main__":
    main()
'''
    
    with open('quick_monitor.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("✅ 快速监控脚本已创建: quick_monitor.py")

def main():
    """主函数"""
    print("🔍 运行时监控系统")
    print("=" * 60)
    
    # 创建监控系统
    monitor = RuntimeMonitoringSystem()
    dashboard = MonitoringDashboard(monitor)
    
    # 创建快速监控脚本
    create_monitoring_script()
    
    print("\n💡 监控使用方法:")
    print("1. 运行 'python quick_monitor.py' 进行快速监控")
    print("2. 选择持续监控模式实时观察补丁效果")
    print("3. 查看仪表板了解运行状态")
    print("4. 关注错误率和警报信息")
    
    print("\n🎯 监控重点:")
    print("• 补丁拦截活动 - 确认隐私保护生效")
    print("• 扩展错误 - 发现功能问题")
    print("• 网络请求 - 监控数据传输")
    print("• 补丁完整性 - 确保保护持续有效")
    
    print("\n⚠️ 警报触发条件:")
    print(f"• 错误数量 > {monitor.monitoring_config['alert_threshold']} 个")
    print("• 补丁签名丢失")
    print("• 错误率 > 20%")
    
    return monitor, dashboard

if __name__ == "__main__":
    main()