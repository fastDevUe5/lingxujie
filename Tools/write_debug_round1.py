"""Append the first round of the debugging series to the session log.

    python Tools/write_debug_round1.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 58. 调试系列第 1 轮：**日志与断言 —— 从源码读到机制**（2026-11-26 43:00）

### 一、方向变更

**用户要求：停止开发，专攻调试与问题定位，成为专家。**
**新目标：`goal-9fa802aa`，60 轮，按八个调试域推进。**

**每篇必须做到四件事：**
1. 读本机 `Engine/Source` 核实机制（要能指到文件和行号）
2. 在本项目上实操复现
3. 记录**更正**（之前哪条结论错了）
4. 给**排查清单**，让人能照着做

### 二、第 1 篇：日志体系（`UE5-DEBUG-LOGGING.md`）

**核心发现：**

| 事实 | 依据 |
| --- | --- |
| 8 级 + 2 个**非级别标志位**（`SetColor=0x40`、`BreakOnLog=0x80`）| `LogVerbosity.h` |
| 打印过**两道编译期 + 一道运行期**闸门 | `LogMacros.h` 240-255 |
| 运行期闸门就一行：`level <= Verbosity` | `LogCategory.h` 45 |
| **`COMPILED_IN_MINIMUM_VERBOSITY` 默认 `VeryVerbose`** | `LogMacros.h` 93-99 |
| `log <Cat> Break` 是**切换**（`^=`）| `LogSuppressionInterface.cpp` 308-310 |

**🔴 更正我的一个误解：**
> **我以为「打包后 Verbose 日志被编译掉」。**
> **实际默认 `COMPILED_IN_MINIMUM_VERBOSITY = VeryVerbose`（全保留），**
> **只有项目显式在 monolithic 构建里定义才会裁。**
> **→ 「Verbose 不见了」在编辑器和默认打包里都只能是**运行期**原因。**

**实测发现三个陷阱：**

| # | 陷阱 | 实测证据 |
| --- | --- | --- |
| 1 | **运行期改级别会在会话内静默持续** | `LogTemp` 读出来是 `Warning`，源码说默认 `Log` —— 是我更早脚本设的 |
| 2 | **引擎只在调高时告发，调低无记录** | 源码 345-349 行的 `Tattle` 只判 `>= Verbose` |
| 3 | **`Log` 级别只写文件、不写控制台** | 枚举注释 "does not print to console" |

**→ 陷阱 1+2 合起来就是「日志莫名消失」最难查的原因：无痕迹。**

### 三、第 2 篇：断言体系（`UE5-DEBUG-ASSERTS.md`）

**核心发现：**

| 宏 | 编辑器 | 打包版默认 | 求值副作用 | 中止 | 报告频率 |
| --- | --- | --- | --- | --- | --- |
| `check` | 中断 | **可能不求值** | ❌ | ✅ | 每次 |
| `verify` | 中断 | 求值但不检查 | ✅ | ✅（Dev）| 每次 |
| `ensure` | 日志+断点 | 不报告 | ✅ | ❌ | **同一行一次** |
| `ensureAlways` | 日志+断点 | 不报告 | ✅ | ❌ | 每次 |

**依据：`AssertionMacros.h` 319-324 —— `DO_CHECK=0` 时**
```cpp
#define check(expr)  { CA_ASSUME(expr); }                              // 不求值
#define verify(expr) { if(UNLIKELY(!(expr))){ CA_ASSUME(false); } }    // 仍求值
```

**→ 规则：`check` 的表达式只能是**纯判断**，带副作用一律 `verify`。**

**`ensure` 只报一次的机制（`AssertionMacros.h` 403-415）：**
```cpp
template <uint64 Uid> std::atomic<uint8> bGEnsureHasExecuted = false;
constexpr uint64 FileLineHashForEnsure(const char* Filename, uint32 Line)  // djb2
```
**→ 按「文件名+行号」哈希出的模板实例，每个 `ensure` 位置一份。**

**→ 第一次触发没看到，之后**永远不再出现** —— 看起来像"偶发问题自己好了"。**

**各构建开关（`Build.h` 241-333）：**

| 配置 | `DO_GUARD_SLOW` | `DO_CHECK` | `DO_ENSURE` |
| --- | --- | --- | --- |
| Debug | 1 | 1 | 1 |
| **Development（编辑器）** | 0 | **1** | **1** |
| Test / Shipping | 0 | `USE_CHECKS_IN_SHIPPING` | `USE_ENSURES_IN_SHIPPING` |

### 四、本项目发现的 4 个真实问题

| # | 问题 | 核实方式 | 状态 |
| --- | --- | --- | --- |
| 1 | **全部日志打在 `LogTemp`**，没有专用类别 | grep `UE_LOG(LogTemp` | 未修 |
| 2 | **`LXJCharacter.cpp:182` 的 `Verbose` 日志从来不打印** | `LogTemp` 默认 `Log`(5) < `Verbose`(6) | 未修 |
| 3 | **全项目零断言** | grep 无匹配 | 空白 |
| 4 | **`USE_CHECKS_IN_SHIPPING` 未定义** | `Target.cs` 无定义 | 打包版不检查 |

**⚠️ 按用户要求**只读不改**，C++ 一字未动。**

### 五、新增文档

| 文档 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-INDEX.md`** | 调试系列入口 + 8 域进度 + 速查结论 |
| **`Docs/UE5-DEBUG-LOGGING.md`** | 日志体系（10 KB）|
| **`Docs/UE5-DEBUG-ASSERTS.md`** | 断言体系（8 KB）|

**`Docs/LEARNING-INDEX.md` 已加入「〇之二、调试系列」章节。**

### 六、新增脚本

| 脚本 | 作用 |
| --- | --- |
| `Tools/practice_log_commands.py` | 跑 `log list` / 改级别 / 切换 Break |
| `Tools/verify_verbosity_gate.py` | 四步读回级别，证明运行期闸门 |

### 七、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **崩溃与调用栈** —— Crash Reporter 机制、`.dmp` 位置、`-unattended`、Minidump |
| 2 | 性能剖析（`stat` 命令族 / Insights）|
| 3 | 内存与泄漏（`memreport`）|
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 58." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 58; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
