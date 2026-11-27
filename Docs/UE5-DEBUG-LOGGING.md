# UE5 调试 · 一：日志与断言体系

> **本系列目标：把「调试」从"看日志猜"变成"读源码知道机制，再按机制定位"。**
>
> **每一篇都必须：读本机 `Engine/Source` 核实 → 在本项目上实操 → 记录结论与更正。**
>
> **本篇日期：2026-11-26 · 依据 UE 5.8.4 源码 · 已在灵虚界项目实测**

---

## 一、日志级别：8 级 + 2 个「非级别」位

**源码：`Runtime/Core/Public/Logging/LogVerbosity.h`**

```c
namespace ELogVerbosity {
    enum Type : uint8 {
        NoLogging   = 0,   // 不用
        Fatal       = 1,   // 打到控制台 + 日志，并且崩溃
        Error       = 2,   // 控制台 + 日志；Commandlet 会因此失败
        Warning     = 3,   // 控制台 + 日志
        Display     = 4,   // 控制台 + 日志
        Log         = 5,   // 只写日志文件
        Verbose     = 6,   // 只在类别开启 Verbose 时才写
        VeryVerbose = 7,   // 只在开启 VeryVerbose 时才写

        All           = VeryVerbose,
        NumVerbosity,
        VerbosityMask = 0xf,   // 低 4 位是级别
        SetColor      = 0x40,  // ← 不是级别：设输出设备颜色
        BreakOnLog    = 0x80   // ← 不是级别：让这行日志断进调试器
    };
}
```

**⚠️ 第一件要记住的事：`SetColor` 和 `BreakOnLog` 是**标志位**，不是级别。**
**它们和级别共用一个 `uint8`，靠 `VerbosityMask = 0xf` 分离。**

---

## 二、日志到底会不会打印：两道闸门

**源码：`LogMacros.h` 第 240-255 行**

```cpp
template <int32 VerbosityToCheck, typename CategoryType>
bool IsLogActive(const CategoryType& Category) {
    if constexpr ((VerbosityToCheck & VerbosityMask) <= CategoryType::CompileTimeVerbosity &&
                  (VerbosityToCheck & VerbosityMask) <= ELogVerbosity::COMPILED_IN_MINIMUM_VERBOSITY)
    {
        return !Category.IsSuppressed((ELogVerbosity::Type)VerbosityToCheck);
    }
    else return false;
}
```

**三道条件，前两道是**编译期**，第三道是**运行期**：**

| # | 条件 | 时机 | 由谁决定 |
| --- | --- | --- | --- |
| 1 | `level <= Category::CompileTimeVerbosity` | **编译期** | `DECLARE_LOG_CATEGORY_EXTERN` 第 3 个参数 |
| 2 | `level <= COMPILED_IN_MINIMUM_VERBOSITY` | **编译期** | 全局宏，默认 `VeryVerbose` |
| 3 | `level <= Category.Verbosity` | **运行期** | `log <Cat> <Level>` / 配置 / 代码 |

**运行期那道，源码只有一行（`LogCategory.h` 第 45 行）：**
```cpp
bool IsSuppressed(ELogVerbosity::Type VerbosityLevel) const {
    return !((VerbosityLevel & VerbosityMask) <= Verbosity);
}
```

### 2.1 🔴 更正一个常见误解

**我之前以为「打包后 Verbose 日志会被编译掉」。**读源码后：

```cpp
// LogMacros.h 第 93-99 行
#ifndef COMPILED_IN_MINIMUM_VERBOSITY
    #define COMPILED_IN_MINIMUM_VERBOSITY VeryVerbose
#else
    #if !IS_MONOLITHIC
        #error COMPILED_IN_MINIMUM_VERBOSITY can only be defined in monolithic builds.
    #endif
#endif
```

**默认是 `VeryVerbose`（全保留）。**
**只有**项目显式**在 monolithic 构建里定义它，才会裁掉。**

**→ 「Verbose 不见了」在**编辑器**和**默认打包**里都只能是**运行期**原因，不是编译期。**

---

## 三、控制台命令：`log`

**源码：`Runtime/Core/Private/Logging/LogSuppressionInterface.cpp`，`Exec_Runtime` 第 589 行起**

| 命令 | 作用 | 源码依据 |
| --- | --- | --- |
| `log list [过滤词]` | 列出类别 + 当前级别 + `DebugBreak` 标记 | 第 593 行 |
| `log <Cat> <Level>` | 设级别 | `SetVerbosity` |
| `log <Cat> Break` | **切换**断点标志（`^=`，不是设为开）| 第 308-310 行 |
| `log reset` | 复位 | `NAME_Reset` |
| `log <Cat> toggle` | 在「上次非零级别」和关闭之间切换 | `ToggleAssociations` |

**`log list` 的输出格式（实测）：**
```
LogTemp                                   Warning
LogTemp                                   Log            - DebugBreak
```
**三列：`%-40s` 类别名 · `%-12s` 级别 · `DebugBreak` 标记。**

### 3.1 `log <Cat> Break` 是排查利器

**作用：让这个类别的**下一条**日志断进调试器。**

**什么时候用：**
- **「谁在什么时候打了这条日志？」** —— 设 Break，等它断，看调用栈
- **「这个函数被谁调的？」** —— 在函数入口打一条 `Log` 级别日志（保证可见），设 Break

**注意是**切换**：连按两次就关了。实测确认了这个行为。**

---

## 四、🔴 实测发现的三个陷阱

### 4.1 运行期改级别会**静默持续**整个会话

**实测序列：**
```
step 1: LogTemp   Warning      ← 源码说默认是 Log，这里是 Warning
step 2: log LogTemp Verbose → Verbose
step 3: log LogTemp Log     → Log
```

**那个 `Warning` 是我**更早的一个脚本**用 `log LogTemp Warning` 设的。
它在这个编辑器会话里一直有效。**

**⚠️ 而且配置里**没有** `[Core.Log]` 段 —— 所以这个改动重启就丢。**

### 4.2 引擎只「告发」调高，**不告发调低**

**源码第 345-349 行：**
```cpp
// Tattle on configs & other paths that raise the level after boot so we can quickly rule out
// code defaults for log spam
if ((OriginalVerbosityLevel < ELogVerbosity::Verbose) && (VerbosityLevel >= ELogVerbosity::Verbose))
    UE_LOGF(LogHAL, Log, "Log category %ls verbosity has been raised to %ls.", ...);
```

**→ 如果日志**调高**了，日志里会有一行 `verbosity has been raised to ...`，能直接定位。**
**→ 如果日志**莫名消失**（被调低），**没有任何记录**。**

**这就是「我的日志怎么不见了」最难查的原因：**
1. 之前某次会话/脚本把它调低了
2. 没有痕迹
3. 引擎不报错，也不提示

**排查办法：`log list <你的类别>` 先看当前级别，不要假设它是默认值。**

### 4.3 `Fatal` 会崩溃，`Error` 会让 Commandlet 失败

**源码注释写得很清楚：**
- `Fatal` = "Always prints a fatal error to console (and log file) and crashes"
- `Error` = "Commandlets and the editor collect and report errors. Error messages result in commandlet failure."

**→ 在跑 Commandlet（烘焙、批量导入）时，一条 `Error` 就能让它返回非零。**
**这解释了「明明跑完了却说失败」。**

---

## 五、本项目的真实缺陷（读源码 + 实测定位）

### 5.1 🔴 全部日志打在 `LogTemp` 上

**源码：`Source/LingXuJie/*.cpp` 里 100% 是 `UE_LOG(LogTemp, ...)`，没有一个专用类别。**

**`LogTemp` 的声明（`Runtime/Core/Public/CoreGlobals.h` 第 55 行）：**
```cpp
CORE_API DECLARE_LOG_CATEGORY_EXTERN(LogTemp, Log, All);
```
**→ 默认级别 `Log`(5)，编译期 `All`(7)。**

**后果：**
- 想调高本项目日志 → 必须调高整个引擎共用 `LogTemp` 的代码，噪声全开
- 想调低本项目日志 → 会把引擎的 `LogTemp` 一起压低
- `log list` 里根本区分不出「哪些是灵虚界的」

### 5.2 🔴 `LXJCharacter.cpp:182` 的 `Verbose` 日志**从来没打印过**

```cpp
UE_LOG(LogTemp, Verbose, TEXT("[LingXuJie] Used slot %d facing %.0f"), Index, CameraYaw);
```

**`Verbose`(6) > `LogTemp` 默认(5) → 运行期被抑制。**

**→ 这条日志写下来之后大概一直没生效过，而且不会有人发现。**

### 5.3 正确做法

```cpp
// LingXuJie.h
DECLARE_LOG_CATEGORY_EXTERN(LogLingXuJie, Log, All);

// LingXuJie.cpp
DEFINE_LOG_CATEGORY(LogLingXuJie);

// 用的时候
UE_LOG(LogLingXuJie, Log, TEXT("Player ready at %s"), *SpawnLocation.ToCString());
```

**然后：**
```
log list LingXuJie              → 只看到本项目的类别
log LogLingXuJie Verbose        → 只放开本项目的 Verbose
log LogLingXuJie Break          → 只在本项目打日志时断
```

**⚠️ 这是**待办**，我没有改 C++（用户要求先学习不开发）。已记入本篇作为证据。**

---

## 六、排查清单（可直接照着做）

### 6.1 「日志没出来」

| 步骤 | 命令 / 动作 | 排除什么 |
| --- | --- | --- |
| 1 | `log list <类别>` | **当前级别是不是被调低了**（最常见） |
| 2 | 看声明 | `CompileTimeVerbosity` 是否低于你要的级别 |
| 3 | 看级别数值 | `Verbose`(6) 在 `Log`(5) 默认下**必然不打印** |
| 4 | 看是不是 `Log` 而非 `Display` | `Log` 级**只写文件不写控制台** —— 控制台看不到但文件里有 |
| 5 | 查 `LogCmds=` 命令行 | 启动参数可能覆盖了 |

**⚠️ 第 4 条最容易误判：`Log` 级别**不进控制台**。在控制台看不到不等于没打。**

### 6.2 「日志太多/刷屏」

| 步骤 | 命令 | 说明 |
| --- | --- | --- |
| 1 | 搜日志里 `verbosity has been raised` | 引擎会告发**谁**把级别调高了 |
| 2 | `log list` 找 `Verbose` / `VeryVerbose` 的类别 | 逐个压低 |
| 3 | `log <Cat> toggle` | 在「上次非零」和关闭之间快速切 |

### 6.3 「谁在调这个函数」

```
log <Category> Break      ← 先确保该类别有 Log 级别日志，且当前级别 >= Log
```
**然后复现，断下来看调用栈。**

---

## 七、还没做但该做的

| 事项 | 为什么 |
| --- | --- |
| 给项目建 `LogLingXuJie` 类别 | 现在所有日志混在 `LogTemp` |
| 查 `LXJCharacter.cpp:182` 的 `Verbose` 是否真没生效过 | 需要在 PIE 里切技能并观察日志 |
| 摸清 `DefaultEngine.ini` 的 `[Core.Log]` 写法 | 现在项目完全没用它，等于放弃了持久化配置 |
| `ensure` / `check` / `verify` 的区别 | **下一篇** |

---

## 八、本篇的可复现脚本

| 脚本 | 作用 |
| --- | --- |
| `Tools/practice_log_commands.py` | 跑 `log list` / 改级别 / 切换 Break |
| `Tools/verify_verbosity_gate.py` | 四步读回级别，证明运行期闸门 |

**运行方式：**
```powershell
powershell -ExecutionPolicy Bypass -File Tools\RebuildInEditor.ps1 `
    -Script Tools\verify_verbosity_gate.py -TimeoutSeconds 180 -WaitPattern 'VERGATE: done'
```

---

**下一篇：`Docs/UE5-DEBUG-ASSERTS.md` —— `check` / `ensure` / `verify` / `checkf` 的区别与断点策略。**
