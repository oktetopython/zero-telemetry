#!/usr/bin/env python3
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
    
    choice = input("\n请选择 (1-4): ").strip()
    
    if choice == '1':
        print("\n启动持续监控...")
        monitor.start_monitoring()
        
        try:
            while True:
                input("\n按 Enter 查看仪表板 (Ctrl+C 退出)...")
                dashboard.display_dashboard()
        except KeyboardInterrupt:
            print("\n停止监控...")
            monitor.stop_monitoring()
            
    elif choice == '2':
        print("\n执行快速检查...")
        monitor.start_monitoring()
        import time
        time.sleep(2)  # 等待收集一些数据
        dashboard.display_dashboard()
        monitor.stop_monitoring()
        
    elif choice == '3':
        print("\n查看详细统计...")
        monitor.start_monitoring()
        import time
        time.sleep(2)
        dashboard.display_detailed_statistics()
        monitor.stop_monitoring()
        
    else:
        print("退出监控")

if __name__ == "__main__":
    main()
