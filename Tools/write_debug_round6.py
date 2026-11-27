"""Append the sixth debugging round.

    python Tools/write_debug_round6.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 63. 调试系列第 6 轮：**脚本 — Python 炸不垮编辑器，蓝图会弹框**（2026-11-26 48:00）

### 一、Python 四个日志通道（实测格式）

```
LogPython:          [LingXuJie] PYB: this is unreal.log
LogPython: Warning: [LingXuJie] PYB-WARN: this is unreal.log_warning
LogPython: Error:   [LingXuJie] PYB-ERR: this is unreal.log_error
LogPython: this is bare print - goes through Python stdout redirection
```

**⚠️ `log_error` 是 Error 级别 —— Commandlet 里会导致返回非零。**

### 二、异常栈：带完整路径和行号

**自己捕获后格式化：**
```
Traceback (most recent call last):
  File ".../practice_python_failures.py", line 46, in main
    nested_one()
  File ".../practice_python_failures.py", line 34, in nested_two
  ...
ValueError: deliberate failure inside nested_three
```

**未捕获时插件自己打（源码 `PyUtil.cpp` 1649-1665 用 `traceback.format_exception`）：**
```
LogPython: Error: Traceback (most recent call last):
LogPython: Error:   File ".../test_uncaught.py", line 3, in <module>
LogPython: Error:     raise RuntimeError("...")
LogPython: Error: RuntimeError: truly uncaught, no try block anywhere
```

### 三、🔴 关键结论：Python 异常**打不垮编辑器**

**实测连炸 4 次（ValueError / RuntimeError / 语法错误 / 未捕获），
每次之后 `EditorGuard check` 都是 `CHECK: healthy`。**

**→ 「脚本报错了」和「编辑器崩了」是**两件不同的事**，不要混着排查。**

### 四、语法错误会**报两遍**

```
LogPython: Error:   def broken(:
LogPython: Error:              ^
LogPython: Error: SyntaxError: invalid syntax (..., line 2)
LogPython: Error:   def broken(:          ← 又来一遍
```

**→ 插件一次 + Python stderr 重定向一次。**
**→ 日志里重复的错误块 ≠ 脚本跑了两次。**

### 五、我的 `-WaitPattern` 为什么可靠

| 情况 | `done` 会不会出现 |
| --- | --- |
| 正常结束 | ✅ |
| 异常（被 except 兜住）| ❌ |
| 异常（未捕获）| ❌ |
| 语法错误 | ❌ |
| 卡死在 API | ❌（超时）|

**→ `-WaitPattern` 超时 = 没走到最后一行 = 有失败。**

**标准骨架（建议所有脚本都这样）：**
```python
def main():
    ...
    log("PREFIX: done")

try:
    main()
except Exception as error:
    import traceback
    log("PREFIX: FATAL: %r" % error)
    log(traceback.format_exc())
```
**等 `'PREFIX: done|PREFIX: FATAL'` —— 失败时不用等超时。**

### 六、`sys.exit(0)` 会被吞掉

**源码 `PyUtil.cpp` 1620-1646：**
```cpp
// Trap and discard SystemExit with an exit code of zero
PyErr_Clear();
```
**→ 脚本里 `sys.exit(0)` 什么都不会发生。不要用它做「提前结束」。**

### 七、蓝图侧：九种运行时异常

**源码 `BlueprintExceptionInfo.h` 9-21：**
`Breakpoint / Tracepoint / WireTracepoint / AccessViolation / InfiniteLoop /
NonFatalError / FatalError / AbortExecution / UserRaisedError`

**⚠️ `AccessViolation` 在蓝图里也存在 —— 蓝图也能造成内存违例。**

### 八、🔴🔴 蓝图守卫阈值与**模态框陷阱**

**源码 `ScriptCore.cpp`：**
```cpp
static int32 GScriptRecurseLimit = 120;                 // bp.ScriptRecurseLimit
COREUOBJECT_API int32 GMaximumScriptLoopIterations = 1000000;
```

**触发时的原文：**
```
"Infinite script recursion ({0} calls) detected - see log for stack trace"
"Runaway loop detected (over {0} iterations) - see log for stack trace"
"Computation timed out - see log for stack trace"
```

**🔴 第 1283-1291 行的注释是重点：**
```cpp
// Need to reset Runaway counter BEFORE throwing script exception, because the exception causes
// a modal dialog, and other scripts running will then erroneously think they are also "runaway".
```

**→ `ThrowScriptException` 会**弹模态对话框**。**
**→ 自动化环境里那个框会挡住一切（和 gotcha #61 同类）。**
**→ 如果 PIE 里有蓝图跑出 runaway，自动化会**卡死在一个没人看的对话框上**。**

### 九、新增

| 产出 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-SCRIPT.md`** | 四通道 + 异常格式 + 蓝图九种异常 + 守卫阈值 + 模态框陷阱 |
| `Tools/practice_python_failures.py` | 故意制造四种失败，对比输出 |

**清理了 4 个临时测试脚本（`test_uncaught.py` / `test_syntax.py` / `vis_on.py` / `vis_off.py`）。**

### 十、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **网络调试** —— replication、net.* CVar、lag simulation、`net.PackageMap` |
| 2 | 资产与加载问题 |
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 63." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 63; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
