# AugmentCode-Free Extension.js 修改逻辑详解

## 概述

AugmentCode-Free 通过修改 VS Code AugmentCode 扩展的 `extension.js` 文件来实现隐私保护和功能增强。本文档详细说明了修改的完整逻辑、技术原理和实现细节。

## 修改目标文件

**文件路径：** `~/.vscode/extensions/augment.vscode-augment-[版本号]/out/extension.js`

**文件特征：**
- 大小：约 5.9MB 的压缩 JavaScript 代码
- 格式：经过混淆和压缩的单行代码
- 功能：AugmentCode 扩展的核心逻辑

## 修改原理

### 1. 目标函数定位

**查找模式：** `async callApi(参数列表){`

```javascript
// 原始函数签名（示例）
async callApi(r,n,s,i,a,o,l,c,d,u=!1){
    // 原始函数体
}
```

**定位逻辑：**
- 使用正则表达式：`r'(async\s+callApi\s*\([^)]*\)\s*\{)'`
- 找到函数开始的大括号 `{` 位置
- 在此位置插入补丁代码

### 2. 补丁插入策略

**插入位置：** 函数开始大括号 `{` 之后立即插入

```javascript
// 修改前
async callApi(r,n,s,i,a,o,l,c,d,u=!1){
    // 原始代码...
}

// 修改后
async callApi(r,n,s,i,a,o,l,c,d,u=!1){
    [补丁代码]
    // 原始代码...
}
```

## 补丁代码详解

### 核心补丁模式

#### 1. BLOCK 模式 - 完全阻止
```javascript
if (typeof s === "string" && (s.startsWith("report-") || s.startsWith("record-"))) { 
    return { success: true }; 
}
```
**功能：** 拦截所有遥测请求，直接返回成功状态，不发送任何数据

#### 2. EMPTY 模式 - 空数据
```javascript
if (typeof s === "string" && (s.startsWith("report-") || s.startsWith("record-"))) { 
    i = {}; 
}
```
**功能：** 将遥测数据替换为空对象，发送最小载荷

#### 3. RANDOM 模式 - 随机假数据
```javascript
if (typeof s === "string" && (s.startsWith("report-") || s.startsWith("record-"))) { 
    i = { timestamp: Date.now(), version: Math.random().toString(36).substring(2, 8) }; 
}
```
**功能：** 发送随机生成的假数据，让服务器收到无意义信息

#### 4. STEALTH 模式 - 隐身模式
```javascript
if (typeof s === "string" && (s.startsWith("report-") || s.startsWith("record-"))) { 
    i = { timestamp: Date.now(), session: Math.random().toString(36).substring(2, 10), events: [] }; 
}
```
**功能：** 发送看起来真实但实际为假的遥测数据

#### 5. DEBUG 模式 - 调试增强
```javascript
if (typeof s === "string" && (s.startsWith("report-") || s.startsWith("record-"))) { 
    i = { timestamp: Date.now(), version: Math.random().toString(36).substring(2, 8) }; 
} 
if (typeof s === "string" && s === "subscription-info") { 
    return { success: true, subscription: { Enterprise: {}, ActiveSubscription: { end_date: "2026-12-31", usage_balance_depleted: false } } }; 
} 
this.maxUploadSizeBytes = 999999999; 
this.maxTrackableFileCount = 999999; 
this.completionTimeoutMs = 999999; 
this.diffBudget = 999999; 
this.messageBudget = 999999; 
this.enableDebugFeatures = true;
```
**功能：** 
- 拦截遥测数据
- 伪造订阅信息（假装有企业版订阅）
- 移除各种限制（文件大小、数量、超时等）
- 启用调试功能

### 会话随机化代码

**目的：** 生成随机的会话ID和清空用户代理，进一步保护隐私

```javascript
const chars = "0123456789abcdef"; 
let randSessionId = ""; 
for (let i = 0; i < 36; i++) { 
    randSessionId += i === 8 || i === 13 || i === 18 || i === 23 ? "-" : 
                     i === 14 ? "4" : 
                     i === 19 ? chars[8 + Math.floor(4 * Math.random())] : 
                     chars[Math.floor(16 * Math.random())]; 
} 
this.sessionId = randSessionId; 
this._userAgent = "";
```

**功能：**
- 生成符合 UUID v4 格式的随机会话ID
- 清空用户代理字符串
- 每次启动都使用不同的会话标识

## 修改流程详解

### 1. 预检查阶段
```
1. 检查文件是否存在
2. 记录文件状态（大小、修改时间）
3. 检查文件权限，移除只读属性
4. 读取文件内容
5. 检查是否已被补丁（避免重复修改）
```

### 2. 定位和备份阶段
```
1. 使用正则表达式查找 callApi 函数
2. 确定插入位置（函数开始大括号后）
3. 创建原始文件备份（extension_ori.js）
4. 验证备份完整性
```

### 3. 补丁应用阶段
```
1. 根据选择的模式生成补丁代码
2. 添加会话随机化代码
3. 在指定位置插入完整补丁
4. 写入修改后的内容
5. 验证修改结果
```

### 4. 验证和日志阶段
```
1. 记录修改后的文件状态
2. 验证文件大小变化
3. 输出详细的操作日志
4. 确认补丁应用成功
```

## 技术细节

### 文件权限处理
```python
# 检查并移除只读属性
if not (current_mode & stat.S_IWRITE):
    os.chmod(file_path, current_mode | stat.S_IWRITE)
    
# Windows 特定处理
subprocess.run(['attrib', '-R', file_path])
```

### 补丁检测机制
```python
# 多重检测方法
1. 签名检测：查找特定的补丁标识符
2. 文件开头检测：检查是否以补丁代码开始
3. 大小检测：补丁后文件大小变化
4. 特征码检测：查找补丁特有的字符串
```

### 错误处理和恢复
```python
# 自动恢复机制
try:
    # 应用补丁
    apply_patch()
except Exception as e:
    # 从备份恢复原始文件
    restore_from_backup()
    # 记录详细错误信息
    log_error_details(e)
```

## 修改效果

### 隐私保护效果
- **遥测阻止：** 阻止或修改发送给服务器的使用数据
- **会话匿名：** 使用随机会话ID，无法追踪用户
- **用户代理清空：** 移除浏览器/系统识别信息

### 功能增强效果（DEBUG模式）
- **订阅伪造：** 获得企业版功能访问权限
- **限制移除：** 取消文件大小、数量等限制
- **调试启用：** 开启额外的调试和开发功能

### 文件变化
```
原始文件：5,948,081 字符
补丁后：  5,948,499 字符
增加：    418 字符（补丁代码）
```

## 安全考虑

### 备份机制
- 自动创建 `extension_ori.js` 备份文件
- 支持一键恢复到原始状态
- 备份完整性验证

### 可逆性
- 所有修改都是可逆的
- 提供恢复功能
- 不会永久损坏原始文件

### 检测规避
- 补丁代码混入原始代码中
- 不修改文件结构
- 保持扩展正常运行

## 使用建议

1. **备份重要性：** 始终保留原始备份文件
2. **版本兼容：** 扩展更新后需要重新应用补丁
3. **功能测试：** 应用补丁后测试扩展功能是否正常
4. **隐私意识：** 理解不同模式的隐私保护程度

## 技术原理总结

AugmentCode-Free 通过在 AugmentCode 扩展的核心 API 调用函数中插入拦截代码，实现了对遥测数据的控制和功能的增强。这种方法：

1. **精确定位：** 通过正则表达式准确找到关键函数
2. **最小侵入：** 只在必要位置插入代码，不破坏原有逻辑
3. **功能完整：** 提供多种保护模式满足不同需求
4. **安全可靠：** 完善的备份和恢复机制确保安全性

这种修改方式既保护了用户隐私，又增强了扩展功能，同时保持了良好的可维护性和安全性。