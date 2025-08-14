# Design Document

## Overview

This design document outlines the solution for fixing misleading error messages and improving the patch application process in the AugmentCode-Free application. The main issues are inaccurate error reporting, insufficient logging, and poor exception handling in the patch management system.

## Architecture

The fix involves enhancing the `PatchManager` class with better error handling, more detailed logging, improved patch detection, and clearer success/failure reporting.

### Current Issues Analysis

1. **Misleading Error Messages**: "恢复原始文件失败!" appears even when restore operations succeed
2. **Poor Exception Handling**: Generic exception catching without specific error details
3. **Insufficient Logging**: Limited visibility into what actually happens during patch operations
4. **Patch Detection Issues**: May not correctly identify already-patched files in all cases

### Root Causes

1. **Exception Swallowing**: The `except:` block catches all exceptions without logging details
2. **Success Verification**: No verification that restore operations actually succeeded
3. **Generic Error Messages**: Same error message for different failure scenarios
4. **Limited Patch Signatures**: Current detection method may miss some patch variations

## Components and Interfaces

### Enhanced PatchManager Class

```python
class PatchManager:
    def apply_patch(self, file_path: str, patch_mode: PatchMode) -> PatchResult:
        # Enhanced with detailed logging and better error handling
        
    def _verify_backup_integrity(self, original_path: str, backup_path: str) -> bool:
        # New method to verify backup was created correctly
        
    def _verify_restore_success(self, file_path: str, backup_path: str) -> bool:
        # New method to verify restore operation succeeded
        
    def _enhanced_patch_detection(self, content: str) -> tuple[bool, str]:
        # Improved patch detection with multiple methods
        
    def _log_file_state(self, file_path: str, operation: str) -> None:
        # New method for detailed file state logging
```

### Enhanced Error Handling Strategy

```python
# Before (problematic)
except:
    print_error("恢复原始文件失败!")

# After (improved)
except Exception as e:
    print_error(f"恢复原始文件失败: {type(e).__name__}: {e}")
    # Additional verification and specific error handling
```

### Improved Logging Framework

```python
class PatchLogger:
    def log_operation_start(self, operation: str, file_path: str)
    def log_file_state(self, file_path: str, description: str)
    def log_exception(self, operation: str, exception: Exception)
    def log_operation_result(self, operation: str, success: bool, details: str)
```

## Data Models

### Enhanced PatchResult

```python
class PatchResult:
    def __init__(self, success: bool, message: str, file_path: str = "", 
                 backup_path: str = "", operation_log: list = None):
        self.success = success
        self.message = message
        self.file_path = file_path
        self.backup_path = backup_path
        self.operation_log = operation_log or []
        self.timestamp = datetime.now()
```

### File Operation State

```python
@dataclass
class FileState:
    path: str
    size: int
    modified_time: float
    is_patched: bool
    patch_signatures_found: list
```

## Error Handling

### Exception Classification

1. **File Access Errors**: Permission denied, file locked, file not found
2. **Patch Application Errors**: Function not found, patch code invalid, write failures
3. **Backup/Restore Errors**: Backup creation failed, restore verification failed
4. **Validation Errors**: Patch detection failed, file integrity issues

### Improved Error Messages

```python
ERROR_MESSAGES = {
    "file_locked": "文件被占用，请关闭 VS Code 后重试",
    "permission_denied": "权限不足，请以管理员身份运行",
    "backup_failed": "备份创建失败: {reason}",
    "restore_failed": "恢复失败: {reason}",
    "patch_invalid": "补丁代码无效: {reason}",
    "function_not_found": "未找到目标函数，可能是扩展版本不兼容"
}
```

### Verification Methods

```python
def _verify_restore_success(self, file_path: str, backup_path: str) -> tuple[bool, str]:
    """验证恢复操作是否成功"""
    try:
        # Compare file sizes
        original_size = os.path.getsize(file_path)
        backup_size = os.path.getsize(backup_path)
        
        if original_size != backup_size:
            return False, f"文件大小不匹配: {original_size} vs {backup_size}"
        
        # Compare modification times
        # Compare first 1000 bytes for quick verification
        
        return True, "恢复验证成功"
    except Exception as e:
        return False, f"验证过程失败: {e}"
```

## Testing Strategy

### Unit Tests

1. **Error Handling Tests**: Verify specific exceptions are caught and reported correctly
2. **Patch Detection Tests**: Test various patch states and detection accuracy
3. **File Operation Tests**: Test backup, restore, and verification operations
4. **Logging Tests**: Verify all operations are logged appropriately

### Integration Tests

1. **Full Patch Cycle**: Apply patch, verify success, restore, verify restore
2. **Error Scenarios**: Test various failure conditions and error reporting
3. **Already Patched Files**: Test behavior with pre-patched files
4. **File Lock Scenarios**: Test behavior when files are in use

### Manual Testing

1. **VS Code Running**: Test patch application while VS Code is running
2. **Permission Issues**: Test with limited file permissions
3. **Multiple Versions**: Test with multiple extension versions
4. **Network Drives**: Test with files on network locations

## Implementation Approach

### Phase 1: Enhanced Logging and Error Reporting

```python
def apply_patch(self, file_path: str, patch_mode: PatchMode) -> PatchResult:
    operation_log = []
    
    try:
        self._log_operation_start("patch_application", file_path)
        
        # Existing logic with enhanced logging
        
    except PermissionError as e:
        error_msg = f"权限不足: {e}"
        self._log_exception("patch_application", e)
        return PatchResult(False, error_msg, operation_log=operation_log)
    
    except FileNotFoundError as e:
        error_msg = f"文件未找到: {e}"
        self._log_exception("patch_application", e)
        return PatchResult(False, error_msg, operation_log=operation_log)
    
    except Exception as e:
        error_msg = f"补丁应用失败: {type(e).__name__}: {e}"
        self._log_exception("patch_application", e)
        return PatchResult(False, error_msg, operation_log=operation_log)
```

### Phase 2: Improved Patch Detection

```python
def _enhanced_patch_detection(self, content: str) -> tuple[bool, str]:
    """增强的补丁检测"""
    detection_methods = [
        self._check_signature_based_detection,
        self._check_size_based_detection,
        self._check_content_pattern_detection
    ]
    
    for method in detection_methods:
        is_patched, confidence = method(content)
        if is_patched:
            return True, f"检测方法: {method.__name__}, 置信度: {confidence}"
    
    return False, "未检测到补丁"
```

### Phase 3: Verification and Recovery

```python
def _safe_restore_with_verification(self, file_path: str, backup_path: str) -> tuple[bool, str]:
    """安全恢复并验证"""
    try:
        # Create temporary backup of current state
        temp_backup = f"{file_path}.temp_backup"
        shutil.copy2(file_path, temp_backup)
        
        # Perform restore
        shutil.copy2(backup_path, file_path)
        
        # Verify restore success
        success, message = self._verify_restore_success(file_path, backup_path)
        
        if success:
            os.remove(temp_backup)
            return True, "恢复成功并已验证"
        else:
            # Restore failed, revert to temp backup
            shutil.copy2(temp_backup, file_path)
            os.remove(temp_backup)
            return False, f"恢复验证失败: {message}"
            
    except Exception as e:
        return False, f"恢复操作异常: {type(e).__name__}: {e}"
```

## Performance Considerations

- File verification operations should be lightweight (compare sizes first, then samples)
- Logging should be asynchronous to avoid blocking patch operations
- Backup operations should use efficient file copying methods
- Large file handling should use streaming operations where possible

## Security Considerations

- Backup files should have appropriate permissions
- Temporary files should be cleaned up properly
- File path validation to prevent directory traversal
- Verification of file integrity before and after operations