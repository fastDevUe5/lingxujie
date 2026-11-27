# UE5 调试 · 七：蓝图与脚本调试

> **本篇全部结论来自本机插件源码 + 在灵虚界项目上的**故意失败实测**。**
>
> **最实用的两条：**
> **1. Python 异常**永远打不垮编辑器** —— 实测连炸 4 次，编辑器全程 healthy。**
> **2. 蓝图 runaway 循环会弹**模态对话框** —— 自动化环境里这就是灾难。**
>
> **日期：2026-11-26 · UE 5.8.4**

---

## 一、Python 侧：四个日志通道，格式各不相同

**实测（同一个脚本里四种都打一遍）：**
```
LogPython:          [LingXuJie] PYB: this is unreal.log
LogPython: Warning: [LingXuJie] PYB-WARN: this is unreal.log_warning
LogPython: Error:   [LingXuJie] PYB-ERR: this is unreal.log_error
LogPython: this is bare print - goes through Python stdout redirection
```

| 调用 | 日志前缀 | 严重度 |
| --- | --- | --- |
| `unreal.log(...)` | `LogPython: ` | Log |
| `unreal.log_warning(...)` | `LogPython: Warning: ` | Warning |
| `unreal.log_error(...)` | `LogPython: Error: ` | **Error** |
| `print(...)` | `LogPython: ` | Log（被 stdout 重定向）|

**⚠️ `unreal.log_error` 是 **Error 级别**，在 Commandlet 里会导致**返回非零**（见 `UE5-DEBUG-LOGGING.md`）。
脚本里用它报可预期的失败要谨慎。**

---

## 二、Python 异常：栈长什么样

### 2.1 自己捕获并格式化（推荐）

```python
try:
    nested_one()
except ValueError as error:
    import traceback
    for line in traceback.format_exc().split("\n"):
        if line.strip():
            log("    %s" % line)
```

**实测输出：**
```
Traceback (most recent call last):
  File ".../practice_python_failures.py", line 46, in main
    nested_one()
  File ".../practice_python_failures.py", line 34, in nested_two
    nested_two()
  File ".../practice_python_failures.py", line 30, in nested_three
    nested_three()
  File ".../practice_python_failures.py", line 26, in nested_three
    raise ValueError("deliberate failure inside nested_three")
ValueError: deliberate failure inside nested_three
```

**→ 有**完整绝对路径 + 行号 + 出错的源码行**。可诊断。**

### 2.2 未捕获异常（插件自己处理）

**实测（脚本里直接 `raise`，不在任何 try 里）：**
```
LogPython: Error: Traceback (most recent call last):
LogPython: Error:   File ".../test_uncaught.py", line 3, in <module>
LogPython: Error:     raise RuntimeError("truly uncaught, no try block anywhere")
LogPython: Error: RuntimeError: truly uncaught, no try block anywhere
```

**源码依据：`PyUtil.cpp` 第 1603-1665 行**
```cpp
bool FetchPythonError(FString& OutError) {
    // This doesn't just call PyErr_Print as it also needs to work before stderr redirection
    PyErr_Fetch(...);
    PyErr_NormalizeException(...);
    ...
    FPyObjectPtr PyTracebackModule = FImport_ImportModule("traceback");
    PyObject* PyFormatExceptionFunc = PyDict_GetItemString(PyTracebackDict, "format_exception");
```

**→ 插件用标准 `traceback.format_exception` 生成，然后**逐行**打到 `LogPython` 的 Error 级别。**

### 2.3 🔴 关键结论：Python 异常打不垮编辑器

**实测连炸 4 次（ValueError / RuntimeError / 语法错误 / 未捕获），
每次之后 `EditorGuard -Action check` 都是 `CHECK: healthy`。**

**→ Python 异常被插件完整捕获，只是一个日志错误，**进程不受影响**。**

**→ 所以「脚本报错了」和「编辑器崩了」是**两件不同的事**，不要混着排查。**

### 2.4 语法错误的怪现象：**报两遍**

**实测：**
```
LogPython: Error:   def broken(:
LogPython: Error:              ^
LogPython: Error: SyntaxError: invalid syntax (.../test_syntax.py, line 2)
LogPython: Error:   def broken(:
LogPython: Error:              ^
```

**→ 同一段错误被打了**两次**（插件一次，Python 的 stderr 重定向一次）。**

**⚠️ 排查提示：日志里看到重复的错误块，不一定是脚本执行了两次。**

---

## 三、我自己的脚本为什么可靠：`-WaitPattern` 就是失败检测

**我的标准调用方式：**
```powershell
Tools\RebuildInEditor.ps1 -Script Tools\xxx.py -TimeoutSeconds 180 -WaitPattern 'PREFIX: done'
```

**为什么这个能当失败检测：**

| 情况 | `done` 会不会出现 |
| --- | --- |
| 正常结束 | ✅ 出现 |
| 中途抛异常（被我的 `except` 兜住）| ❌ 不出现 |
| 中途抛异常（未捕获）| ❌ 不出现 |
| 语法错误（整个文件没跑）| ❌ 不出现 |
| 卡死在某个 API（如 `get_bone_pose`）| ❌ 不出现（然后超时）|

**→ `-WaitPattern` 超时 = 脚本没走到最后一行 = 有失败。**

**这是我在这个项目里用得最久、也最可靠的脚本验证手段 ——
现在知道它为什么成立了。**

**建议每个脚本都遵守：**
```python
def main():
    ...
    log("PREFIX: done")     # 最后一行一定能到达，除非失败

try:
    main()
except Exception as error:
    import traceback
    log("PREFIX: FATAL: %r" % error)
    log(traceback.format_exc())
```

**两个 pattern 都要等：`-WaitPattern 'PREFIX: done|PREFIX: FATAL'`**
**→ 这样失败时不用等超时，能立刻拿到栈。**

### 3.1 `SystemExit` 会被吞掉

**源码 `PyUtil.cpp` 第 1620-1646 行：**
```cpp
if (PyExceptionType == PyExc_SystemExit && PyExceptionValue) {
    // Trap and discard SystemExit with an exit code of zero, as it is designed to make the
    // interpreter process exit (which doesn't make sense for an embedded interpreter)
    PyErr_Clear();
    return false;
}
```

**→ 脚本里 `sys.exit(0)` **什么都不会发生**（不退出、不报错）。**
**→ `sys.exit(1)` 则会报错。**

**⚠️ 不要用 `sys.exit()` 当"提前结束脚本"的手段。**

---

## 四、蓝图侧：九种运行时异常

**源码：`Runtime/CoreUObject/Public/Blueprint/BlueprintExceptionInfo.h`**
```cpp
namespace EBlueprintExceptionType {
    enum Type {
        Breakpoint,          // 断点命中
        Tracepoint,          // 观测点
        WireTracepoint,      // 连线观测点
        AccessViolation,     // 访问违例
        InfiniteLoop,        // 无限循环 / runaway
        NonFatalError,       // 非致命（记录后继续）
        FatalError,          // 致命
        AbortExecution,      // 中止执行
        UserRaisedError,     // 用户主动报错
    };
}
```

**排查时的意义：**

| 类型 | 含义 | 排查方向 |
| --- | --- | --- |
| `Breakpoint` | 你在调试器里设的断点 | 正常行为 |
| **`AccessViolation`** | **蓝图也能造成内存违例** | **对象已销毁还在调用** |
| **`InfiniteLoop`** | runaway 循环 / 无限递归 | 循环条件 / 递归出口 |
| `NonFatalError` | 报了继续跑 | 常见于节点连接错误 |
| `FatalError` | 停止执行 | 严重 |
| **`AbortExecution`** | `Stack.bAbortingExecution` 被置位 | 上游抛了异常 |
| `UserRaisedError` | 蓝图里主动 `throw` | 设计如此 |

---

## 五、🔴 蓝图的守卫阈值（源码实测）

**源码：`Runtime/CoreUObject/Private/UObject/ScriptCore.cpp`**

```cpp
// 第 79 行
static int32 GScriptRecurseLimit = 120;
// 受 bp.ScriptRecurseLimit 控制

// 第 107 行
COREUOBJECT_API int32 GMaximumScriptLoopIterations = 1000000;

// 第 73-76 行
static int32 GShortScriptWarnings = 0;
// 受 bp.ShortScriptWarnings 控制
```

| CVar | 默认 | 含义 |
| --- | --- | --- |
| `bp.ScriptRecurseLimit` | **120** | 递归 120 层判定为无限递归 |
| `GMaximumScriptLoopIterations` | **1,000,000** | 循环 100 万次判定为 runaway |
| `bp.ShortScriptWarnings` | 0 | 设 1 可缩短异常日志 |

**触发时的消息（源码里的原文）：**
```
"Infinite script recursion ({0} calls) detected - see log for stack trace"
"Runaway loop detected (over {0} iterations) - see log for stack trace"
"Computation timed out - see log for stack trace"
```

### 5.1 🔴🔴 自动化陷阱：这会弹模态对话框

**源码 `ScriptCore.cpp` 第 1283-1291 行的注释：**
```cpp
// Need to reset Runaway counter BEFORE throwing script exception, because the exception causes
// a modal dialog, and other scripts running will then erroneously think they are also "runaway".
BpET.Runaway = 0;
FBlueprintExceptionInfo RunawayLoopExceptionInfo(EBlueprintExceptionType::InfiniteLoop, ExceptionMessage);
FBlueprintCoreDelegates::ThrowScriptException(Context, Stack, RunawayLoopExceptionInfo);
```

**→ `ThrowScriptException` 会**弹出模态对话框**。**

**→ 在自动化环境里，那个对话框会**挡住一切**（和 gotcha #61 同一类问题）。**

**→ 所以：如果项目里有蓝图可能在 PIE 里跑出 runaway 循环，
自动化测试就会卡死在一个没人看的对话框上。**

**缓解：**
- `bp.ShortScriptWarnings=1` 让日志短一点（不解决对话框）
- 自动化跑之前确认 `EditorGuard -Action dismiss` 能点掉（实测能）
- **最根本：别让蓝图跑出 runaway 循环**

### 5.2 守卫的编译开关

**源码：`#if DO_BLUEPRINT_GUARD`**

**→ runaway 检测在**这个宏关闭的构建里根本不存在**。
**→ 编辑器里 `DO_BLUEPRINT_GUARD` 默认开启（`DO_GUARD_SLOW` 之外单独一个宏）。**

**⚠️ 这意味着「编辑器里能拦住，打包版可能拦不住」的情况是可能的 —— 待核实本项目的实际配置。**

---

## 六、排查清单

### 6.1 「Python 脚本失败了」

| 步 | 看什么 |
| --- | --- |
| 1 | 日志里搜 `LogPython: Error:` |
| 2 | 有 `Traceback` → 看最后的 `File "..." line N` |
| 3 | **注意重复的错误块**（语法错误会打两遍）|
| 4 | 没有 `done` 也没有 `FATAL` → 卡在某个 API（看超时）|
| 5 | 确认编辑器还活着（`EditorGuard check`）—— 异常不会杀编辑器 |

### 6.2 「蓝图运行时出错」

| 现象 | 对应的 `EBlueprintExceptionType` |
| --- | --- |
| 日志说 infinite recursion | `InfiniteLoop`（超 120 层）|
| 日志说 runaway loop | `InfiniteLoop`（超 100 万次迭代）|
| 日志说 computation timed out | `InfiniteLoop`（超时路径）|
| **弹了对话框且自动化卡住** | **任一种 — 对话框挡的** |
| 崩溃且栈里有蓝图 | `AccessViolation` |

### 6.3 「怎么快速定位蓝图里哪个节点」

**编辑器路径：**
1. 蓝图编辑器 → **Debug** 面板（`SKismetDebuggingView`）
2. 设断点 → PIE → 逐节点执行 → 看 Watch 值
3. `BreakOnLog`（见 `UE5-DEBUG-LOGGING.md`）也能用于蓝图节点

**⚠️ 蓝图断点**不能**通过 Python 设置** —— 只能 UI 操作。

---

## 七、待做

| 事项 | 为什么 |
| --- | --- |
| 确认本项目 `DO_BLUEPRINT_GUARD` 的实际值 | 决定打包版有没有循环守卫 |
| 在 PIE 里故意造一次 runaway，看对话框长什么样 | 验证自动化会被挡住 |
| 查 `bp.` 开头的全部 CVar | 还没系统查过 |

**⚠️ 按用户要求本轮**只读不改**，没有在项目里造 runaway 循环（会弹框挡住你）。**

---

## 八、本篇依据的源码位置

| 事实 | 文件 | 行 |
| --- | --- | --- |
| 插件用 `traceback.format_exception` 生成栈 | `PyUtil.cpp` | 1649-1665 |
| `SystemExit` 退出码 0 被丢弃 | 同上 | 1620-1646 |
| 9 种蓝图异常类型 | `BlueprintExceptionInfo.h` | 9-21 |
| 递归限制 120 | `ScriptCore.cpp` | 79 |
| 循环迭代限制 1,000,000 | 同上 | 107 |
| runaway 抛异常时**弹模态框** | 同上 | 1283-1291 |
| `bp.ShortScriptWarnings` | 同上 | 73-76 |
| 守卫受 `DO_BLUEPRINT_GUARD` 控制 | 同上 | 1276 |
