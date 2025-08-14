#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码补丁管理器
移植并增强aug_cleaner的核心功能，支持多IDE的扩展文件补丁
"""

import re
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum

from .common_utils import print_info, print_success, print_error, print_warning, IDEType


class PatchMode(Enum):
    """补丁模式枚举"""
    BLOCK = "block"
    RANDOM = "random" 
    EMPTY = "empty"
    STEALTH = "stealth"
    DEBUG = "debug"


class PatchResult:
    """补丁操作结果"""
    def __init__(self, success: bool = False, message: str = "", file_path: str = "", backup_path: str = ""):
        self.success = success
        self.message = message
        self.file_path = file_path
        self.backup_path = backup_path


class PatchManager:
    """代码补丁管理器"""
    
    def __init__(self):
        # 补丁代码模板
        self.patches = {
            PatchMode.BLOCK: self._generate_comprehensive_block_patch(),
            PatchMode.RANDOM: self._generate_comprehensive_random_patch(),
            PatchMode.EMPTY: self._generate_comprehensive_empty_patch(),
            PatchMode.STEALTH: self._generate_comprehensive_stealth_patch(),
            PatchMode.DEBUG: self._generate_comprehensive_debug_patch()
        }
        
        # 补丁签名，用于检测是否已补丁
        self.patch_signatures = [
            'startsWith("report-")',
            'startsWith("record-")', 
            'randSessionId',
            'this._userAgent = ""',
            'TELEMETRY BLOCKED',
            'TELEMETRY RANDOMIZED',
            'TELEMETRY EMPTIED',
            'TELEMETRY STEALTHED',
            'TELEMETRY DEBUG',
            'typeof s === "string" ? s : (typeof n === "string" ? n',
            'sensitiveFields'
        ]
    
    def get_patch_description(self, mode: PatchMode) -> str:
        """获取补丁模式描述"""
        descriptions = {
            PatchMode.BLOCK: "完全遥测阻止 - 不发送任何数据",
            PatchMode.RANDOM: "随机假数据 - 服务器收到无意义数据", 
            PatchMode.EMPTY: "空数据模式 - 发送最小载荷",
            PatchMode.STEALTH: "隐身模式 - 发送逼真但假的遥测数据",
            PatchMode.DEBUG: "调试模式 - 假订阅 + 无限制 + 增强功能"
        }
        return descriptions.get(mode, "未知模式")
    
    def _generate_comprehensive_block_patch(self) -> str:
        """生成全面的阻止模式补丁"""
        return '''
        // 全面遥测拦截 - 支持多种参数名
        const endpoint = typeof s === "string" ? s : (typeof n === "string" ? n : (typeof r === "string" ? r : ""));
        
        // 1. 拦截 report-, record- 前缀
        if (endpoint && (endpoint.startsWith("report-") || endpoint.startsWith("record-"))) {
            console.log("[TELEMETRY BLOCKED]", endpoint);
            return { success: true, blocked: true };
        }
        
        // 2. 拦截遥测关键词
        if (endpoint && /(telemetry|analytics|tracking|metrics|usage|fingerprint|event|log)/i.test(endpoint)) {
            console.log("[TELEMETRY BLOCKED]", endpoint);
            return { success: true, blocked: true };
        }
        
        // 3. 拦截订阅查询
        if (endpoint && /(subscription|auth|license|activation)/i.test(endpoint)) {
            console.log("[AUTH INTERCEPTED]", endpoint);
            return { success: true, subscription: { Enterprise: {}, ActiveSubscription: { end_date: "2026-12-31", usage_balance_depleted: false } } };
        }
        
        // 4. 清理数据载荷中的敏感信息
        if (typeof i === "object" && i !== null) {
            const sensitiveFields = ["machineId", "deviceId", "sessionId", "userId", "clientId", "uuid", "guid", "fingerprint", "userAgent"];
            let hasSensitive = false;
            for (const field of sensitiveFields) {
                if (field in i) { hasSensitive = true; break; }
            }
            if (hasSensitive) {
                console.log("[DATA SANITIZED]", Object.keys(i));
                return { success: true, sanitized: true };
            }
        }
        '''.strip()
    
    def _generate_comprehensive_random_patch(self) -> str:
        """生成全面的随机数据模式补丁"""
        return '''
        const endpoint = typeof s === "string" ? s : (typeof n === "string" ? n : (typeof r === "string" ? r : ""));
        
        if (endpoint && (endpoint.startsWith("report-") || endpoint.startsWith("record-") || /(telemetry|analytics|tracking|metrics|usage|fingerprint|event|log)/i.test(endpoint))) {
            console.log("[TELEMETRY RANDOMIZED]", endpoint);
            i = { timestamp: Date.now(), version: Math.random().toString(36).substring(2, 8), randomized: true };
        }
        
        if (endpoint && /(subscription|auth|license|activation)/i.test(endpoint)) {
            return { success: true, subscription: { Enterprise: {}, ActiveSubscription: { end_date: "2026-12-31", usage_balance_depleted: false } } };
        }
        
        if (typeof i === "object" && i !== null) {
            const sensitiveFields = ["machineId", "deviceId", "sessionId", "userId", "clientId", "uuid", "guid", "fingerprint", "userAgent"];
            for (const field of sensitiveFields) {
                if (field in i) {
                    i[field] = Math.random().toString(36).substring(2, 15);
                }
            }
        }
        '''.strip()
    
    def _generate_comprehensive_empty_patch(self) -> str:
        """生成全面的空数据模式补丁"""
        return '''
        const endpoint = typeof s === "string" ? s : (typeof n === "string" ? n : (typeof r === "string" ? r : ""));
        
        if (endpoint && (endpoint.startsWith("report-") || endpoint.startsWith("record-") || /(telemetry|analytics|tracking|metrics|usage|fingerprint|event|log)/i.test(endpoint))) {
            console.log("[TELEMETRY EMPTIED]", endpoint);
            i = {};
        }
        
        if (endpoint && /(subscription|auth|license|activation)/i.test(endpoint)) {
            return { success: true, subscription: { Enterprise: {}, ActiveSubscription: { end_date: "2026-12-31", usage_balance_depleted: false } } };
        }
        
        if (typeof i === "object" && i !== null) {
            const sensitiveFields = ["machineId", "deviceId", "sessionId", "userId", "clientId", "uuid", "guid", "fingerprint", "userAgent"];
            for (const field of sensitiveFields) {
                if (field in i) {
                    delete i[field];
                }
            }
        }
        '''.strip()
    
    def _generate_comprehensive_stealth_patch(self) -> str:
        """生成全面的隐身模式补丁"""
        return '''
        const endpoint = typeof s === "string" ? s : (typeof n === "string" ? n : (typeof r === "string" ? r : ""));
        
        if (endpoint && (endpoint.startsWith("report-") || endpoint.startsWith("record-") || /(telemetry|analytics|tracking|metrics|usage|fingerprint|event|log)/i.test(endpoint))) {
            console.log("[TELEMETRY STEALTHED]", endpoint);
            i = { timestamp: Date.now(), session: Math.random().toString(36).substring(2, 10), events: [], stealth: true };
        }
        
        if (endpoint && /(subscription|auth|license|activation)/i.test(endpoint)) {
            return { success: true, subscription: { Enterprise: {}, ActiveSubscription: { end_date: "2026-12-31", usage_balance_depleted: false } } };
        }
        
        if (typeof i === "object" && i !== null) {
            const sensitiveFields = ["machineId", "deviceId", "sessionId", "userId", "clientId", "uuid", "guid", "fingerprint", "userAgent"];
            for (const field of sensitiveFields) {
                if (field in i) {
                    i[field] = "stealth-" + Math.random().toString(36).substring(2, 10);
                }
            }
        }
        '''.strip()
    
    def _generate_comprehensive_debug_patch(self) -> str:
        """生成全面的调试模式补丁"""
        return '''
        const endpoint = typeof s === "string" ? s : (typeof n === "string" ? n : (typeof r === "string" ? r : ""));
        
        if (endpoint && (endpoint.startsWith("report-") || endpoint.startsWith("record-") || /(telemetry|analytics|tracking|metrics|usage|fingerprint|event|log)/i.test(endpoint))) {
            console.log("[TELEMETRY DEBUG]", endpoint);
            i = { timestamp: Date.now(), version: Math.random().toString(36).substring(2, 8), debug: true };
        }
        
        if (endpoint && /(subscription|auth|license|activation)/i.test(endpoint)) {
            console.log("[AUTH DEBUG]", endpoint);
            return { success: true, subscription: { Enterprise: {}, ActiveSubscription: { end_date: "2026-12-31", usage_balance_depleted: false } } };
        }
        
        this.maxUploadSizeBytes = 999999999;
        this.maxTrackableFileCount = 999999;
        this.completionTimeoutMs = 999999;
        this.diffBudget = 999999;
        this.messageBudget = 999999;
        this.enableDebugFeatures = true;
        
        if (typeof i === "object" && i !== null) {
            const sensitiveFields = ["machineId", "deviceId", "sessionId", "userId", "clientId", "uuid", "guid", "fingerprint", "userAgent"];
            for (const field of sensitiveFields) {
                if (field in i) {
                    i[field] = "debug-" + Math.random().toString(36).substring(2, 10);
                }
            }
        }
        '''.strip()
    
    def _generate_session_randomizer(self) -> str:
        """生成会话随机化代码"""
        return ' const chars = "0123456789abcdef"; let randSessionId = ""; for (let i = 0; i < 36; i++) { randSessionId += i === 8 || i === 13 || i === 18 || i === 23 ? "-" : i === 14 ? "4" : i === 19 ? chars[8 + Math.floor(4 * Math.random())] : chars[Math.floor(16 * Math.random())]; } this.sessionId = randSessionId; this._userAgent = "";'
    
    def _create_backup(self, file_path: str) -> Tuple[bool, str]:
        """创建文件备份"""
        try:
            file_path_obj = Path(file_path)
            # 正确生成备份文件名
            backup_path = file_path_obj.with_name(f'{file_path_obj.stem}_ori{file_path_obj.suffix}')
            
            if backup_path.exists():
                print_warning(f"备份文件已存在: {backup_path}")
                return True, str(backup_path)
            
            shutil.copy2(file_path, backup_path)
            
            # 验证备份完整性
            is_valid, message = self._verify_backup_integrity(file_path, str(backup_path))
            if is_valid:
                print_success(f"备份创建成功: {backup_path}")
                return True, str(backup_path)
            else:
                print_error(f"备份验证失败: {message}")
                # 删除无效备份
                try:
                    backup_path.unlink()
                except:
                    pass
                return False, ""
            
        except Exception as e:
            print_error(f"创建备份失败: {e}")
            return False, ""
    
    def _is_already_patched(self, content: str) -> bool:
        """检查文件是否已被补丁"""
        is_patched, confidence = self._enhanced_patch_detection(content)
        if is_patched:
            print_info(f"检测到文件已被补丁 (置信度: {confidence})")
        return is_patched
    
    def _enhanced_patch_detection(self, content: str) -> tuple[bool, str]:
        """增强的补丁检测，使用多种方法"""
        
        # 方法1: 签名检测
        signature_matches = [sig for sig in self.patch_signatures if sig in content]
        if signature_matches:
            return True, f"签名匹配: {', '.join(signature_matches)}"
        
        # 方法2: 文件开头检测（补丁文件通常以特定模式开始）
        if content.startswith('!function(){const _={'):
            return True, "文件开头模式匹配"
        
        # 方法3: 大小检测（补丁后文件通常会变小）
        if len(content) < 3000000:  # 小于3MB可能是补丁后的文件
            # 进一步检查是否包含压缩特征
            if content.count('const _=') > 5 and content.count('function()') > 10:
                return True, "大小和内容模式匹配"
        
        # 方法4: 特殊字符串检测
        patch_indicators = [
            '_a:2011', '_b:14', '_c:70', '_d:123',  # 补丁特征码
            'randSessionId', 'fakeData', 'blockTelemetry'  # 补丁功能标识
        ]
        
        found_indicators = [ind for ind in patch_indicators if ind in content]
        if found_indicators:
            return True, f"补丁指示器匹配: {', '.join(found_indicators)}"
        
        return False, "未检测到补丁"
    
    def _ensure_file_writable(self, file_path: str) -> None:
        """确保文件可写，移除只读属性"""
        try:
            import stat
            
            # 获取当前文件属性
            current_mode = os.stat(file_path).st_mode
            
            # 检查是否为只读
            if not (current_mode & stat.S_IWRITE):
                print_warning(f"文件为只读状态，正在移除只读属性: {file_path}")
                # 添加写权限
                os.chmod(file_path, current_mode | stat.S_IWRITE)
                print_success("只读属性已移除，文件现在可写")
            else:
                print_info("文件权限检查通过，可以写入")
                
        except Exception as e:
            print_warning(f"无法修改文件权限: {e}")
            # 尝试 Windows 特定的方法
            try:
                import subprocess
                result = subprocess.run(['attrib', '-R', file_path], 
                                      capture_output=True, text=True, shell=True)
                if result.returncode == 0:
                    print_success("使用 attrib 命令成功移除只读属性")
                else:
                    print_error(f"attrib 命令失败: {result.stderr}")
            except Exception as e2:
                print_error(f"Windows attrib 命令也失败: {e2}")
    
    def _log_file_state(self, file_path: str, operation: str) -> None:
        """记录文件状态信息"""
        try:
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                mtime = os.path.getmtime(file_path)
                from datetime import datetime
                mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                print_info(f"{operation} - 文件: {os.path.basename(file_path)}, 大小: {size} 字节, 修改时间: {mtime_str}")
            else:
                print_info(f"{operation} - 文件不存在: {file_path}")
        except Exception as e:
            print_warning(f"无法获取文件状态: {e}")
    
    def _verify_backup_integrity(self, original_path: str, backup_path: str) -> tuple[bool, str]:
        """验证备份文件的完整性"""
        try:
            if not os.path.exists(backup_path):
                return False, "备份文件不存在"
            
            original_size = os.path.getsize(original_path)
            backup_size = os.path.getsize(backup_path)
            
            if original_size != backup_size:
                return False, f"文件大小不匹配: 原始 {original_size} vs 备份 {backup_size}"
            
            # 快速内容验证 - 比较文件开头和结尾
            with open(original_path, 'rb') as orig, open(backup_path, 'rb') as backup:
                # 比较前1000字节
                orig_start = orig.read(1000)
                backup_start = backup.read(1000)
                if orig_start != backup_start:
                    return False, "文件开头内容不匹配"
                
                # 比较最后1000字节
                orig.seek(-1000, 2)
                backup.seek(-1000, 2)
                orig_end = orig.read(1000)
                backup_end = backup.read(1000)
                if orig_end != backup_end:
                    return False, "文件结尾内容不匹配"
            
            return True, "备份验证成功"
            
        except Exception as e:
            return False, f"验证过程出错: {e}"
    
    def _safe_restore_from_backup(self, file_path: str, backup_path: str) -> bool:
        """安全地从备份恢复文件，包含详细的错误处理和验证"""
        try:
            if not os.path.exists(backup_path):
                print_error(f"备份文件不存在: {backup_path}")
                return False
            
            # 记录恢复前的状态
            original_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            backup_size = os.path.getsize(backup_path)
            
            print_info(f"开始恢复文件: {file_path}")
            print_info(f"当前文件大小: {original_size} 字节")
            print_info(f"备份文件大小: {backup_size} 字节")
            
            # 执行恢复
            shutil.copy2(backup_path, file_path)
            
            # 验证恢复结果
            restored_size = os.path.getsize(file_path)
            if restored_size == backup_size:
                print_success(f"文件恢复成功，大小验证通过: {restored_size} 字节")
                return True
            else:
                print_error(f"文件恢复后大小不匹配: 期望 {backup_size}，实际 {restored_size}")
                return False
                
        except PermissionError as e:
            print_error(f"恢复文件时权限不足: {e}")
            return False
        except OSError as e:
            print_error(f"恢复文件时系统错误: {e}")
            return False
        except Exception as e:
            print_error(f"恢复文件时发生未知错误 ({type(e).__name__}): {e}")
            return False
    
    def _find_callapi_function(self, content: str) -> Optional[re.Match]:
        """查找async callApi函数"""
        pattern = r'(async\s+callApi\s*\([^)]*\)\s*\{)'
        return re.search(pattern, content)
    
    def apply_patch(self, file_path: str, patch_mode: PatchMode) -> PatchResult:
        """应用补丁到指定文件"""
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return PatchResult(False, f"文件不存在: {file_path}")
            
            # 详细的操作日志
            self._log_file_state(file_path, "补丁前")
            print_info(f"开始补丁文件: {file_path}")
            print_info(f"补丁模式: {patch_mode.value} - {self.get_patch_description(patch_mode)}")
            
            # 检查并处理文件属性
            self._ensure_file_writable(file_path)
            
            # 读取文件内容
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print_info(f"文件读取成功，大小: {len(content)} 字符")
            except Exception as e:
                print_error(f"读取文件失败: {e}")
                return PatchResult(False, f"读取文件失败: {e}")
            
            # 检查是否已被补丁
            if self._is_already_patched(content):
                return PatchResult(False, "文件已被补丁，跳过操作")
            
            # 查找callApi函数
            match = self._find_callapi_function(content)
            if not match:
                return PatchResult(False, "未找到async callApi函数")
            
            # 创建备份
            backup_success, backup_path = self._create_backup(file_path)
            if not backup_success:
                return PatchResult(False, "创建备份失败")
            
            # 生成完整补丁代码
            patch_code = self.patches[patch_mode] + self._generate_session_randomizer()
            
            # 应用补丁
            func_start = match.end()
            patched_content = content[:func_start] + patch_code + content[func_start:]
            
            # 写入补丁后的内容
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(patched_content)
                
                # 记录补丁后的文件状态
                self._log_file_state(file_path, "补丁后")
                
                print_success(f"补丁应用成功: {file_path}")
                print_info(f"效果: {self.get_patch_description(patch_mode)}")
                print_info("隐私保护已启用!")
                print_info(f"补丁代码长度: {len(patch_code)} 字符")
                print_info(f"文件大小变化: {len(content)} → {len(patched_content)} 字符")
                
                return PatchResult(True, "补丁应用成功", file_path, backup_path)
                
            except PermissionError as e:
                error_msg = f"文件权限不足，请关闭 VS Code 或以管理员身份运行: {e}"
                print_error(error_msg)
                self._safe_restore_from_backup(file_path, backup_path)
                return PatchResult(False, error_msg)
            except OSError as e:
                error_msg = f"文件系统错误（可能文件被占用）: {e}"
                print_error(error_msg)
                self._safe_restore_from_backup(file_path, backup_path)
                return PatchResult(False, error_msg)
            except Exception as e:
                error_msg = f"写入补丁文件失败 ({type(e).__name__}): {e}"
                print_error(error_msg)
                self._safe_restore_from_backup(file_path, backup_path)
                return PatchResult(False, error_msg)
                
        except Exception as e:
            return PatchResult(False, f"补丁操作失败: {e}")
    
    def restore_from_backup(self, file_path: str) -> PatchResult:
        """从备份恢复原始文件"""
        try:
            file_path_obj = Path(file_path)
            backup_path = file_path_obj.with_name(f'{file_path_obj.stem}_ori{file_path_obj.suffix}')
            
            if not backup_path.exists():
                return PatchResult(False, f"备份文件不存在: {backup_path}")
            
            shutil.copy2(backup_path, file_path)
            print_success(f"已从备份恢复: {file_path}")
            
            return PatchResult(True, "恢复成功", file_path, str(backup_path))
            
        except Exception as e:
            return PatchResult(False, f"恢复失败: {e}")
    
    def get_patch_status(self, file_path: str) -> str:
        """获取文件的补丁状态"""
        try:
            if not os.path.exists(file_path):
                return "文件不存在"
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if self._is_already_patched(content):
                return "已补丁"
            else:
                return "未补丁"
                
        except Exception:
            return "状态未知"
