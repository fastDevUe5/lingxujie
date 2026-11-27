# UE5 调试 · 二：断言体系（check / verify / ensure）

> **本篇全部结论来自本机 `Engine/Source/Runtime/Core/Public/Misc/AssertionMacros.h` 与 `Build.h`。**
>
> **核心结论有一条是反直觉的：`check` 在打包版里**不一定会求值它的表达式**。**
>
> **日期：2026-11-26 · UE 5.8.4**

---

## 一、先看清 `DO_CHECK` 在各构建里的值

**源码：`Misc/Build.h` 第 241-333 行**

| 配置 | `DO_GUARD_SLOW` | `DO_CHECK` | `DO_ENSURE` |
| --- | --- | --- | --- |
| `UE_BUILD_DEBUG` | **1** | **1** | **1** |
| `UE_BUILD_DEVELOPMENT`（**编辑器就是这个**）| 0 | **1** | **1** |
| `UE_BUILD_TEST` | 0 | `USE_CHECKS_IN_SHIPPING` | `USE_ENSURES_IN_SHIPPING` |
| `UE_BUILD_SHIPPING` | 0 | `USE_CHECKS_IN_SHIPPING` | `USE_ENSURES_IN_SHIPPING` |

**`USE_CHECKS_IN_SHIPPING` / `USE_ENSURES_IN_SHIPPING` 项目可以自己定义，默认是 0。**

> **所以在编辑器里，`check` / `verify` / `ensure` 全部生效 —— 在编辑器测试通过，**
> **不代表打包版里这些代码还在。**

---

## 二、`check` 与 `verify`：**同一个东西，直到打包**

### 2.1 `DO_CHECK = 1` 时（Debug / Development）

**源码第 221-230 行：**
```cpp
#if DO_CHECK
    #define verify(expr)  UE_CHECK_IMPL(expr)
    #define check(expr)   UE_CHECK_IMPL(expr)
```

**完全一样。**`UE_CHECK_IMPL`（第 235-249 行）：
```cpp
#define UE_CHECK_IMPL(expr) \
    { if(UNLIKELY(!(expr))) { \
          if (FDebug::CheckVerifyFailedImpl2(#expr, __FILE__, __LINE__, TEXT(""))) { PLATFORM_BREAK(); } \
          CA_ASSUME(false); } \
      else { CA_ASSUME(true); } }
```

**行为：**
1. 求值 `expr`
2. 为假 → `CheckVerifyFailedImpl2` → 打日志 + **触发断言对话框/中断**
3. 返回 true（表示「要不要断进调试器」）→ `PLATFORM_BREAK()`

**→ `check` 失败会**中断执行**（不是返回 false 继续跑）。**

### 2.2 🔴 `DO_CHECK = 0` 时（默认打包版）

**源码第 319-324 行：**
```cpp
#define check(expr)               { CA_ASSUME(expr); }
#define checkf(expr, format, ...) { CA_ASSUME(expr); }
#define verify(expr)              { if(UNLIKELY(!(expr))){ CA_ASSUME(false); } }
```

**关键差异：**

| 宏 | 打包版里表达式**会被求值吗** | 后果 |
| --- | --- | --- |
| `check(expr)` | **不保证** —— `CA_ASSUME(expr)` 只是给编译器的假设 | **带副作用的表达式会静默消失** |
| `verify(expr)` | **会** —— 显式 `if(!(expr))` | 副作用保留 |

**`CA_ASSUME` 是编译器的「我保证这是真的」，不会生成求值代码。**

### 2.3 什么时候必须用 `verify`

```cpp
// ❌ 危险：打包版里 DoWork() 可能根本不执行
check(DoWork());

// ✅ 正确：DoWork() 一定执行
verify(DoWork());

// ✅ 也正确：断言和副作用分开
bool bOk = DoWork();
check(bOk);
```

**规则：**
> **`check` 的表达式只能是**纯判断**。
> 任何带副作用（函数调用、赋值、自增、指针推进）的，一律用 `verify`。**

**这条规则的依据不是风格，是 `CA_ASSUME` 的语义。**

---

## 三、`ensure` 家族：**不中断**，只报告

**源码第 430-464 行：**
```cpp
#define ensure(           InExpression                ) UE_ENSURE_IMPL (false, InExpression)
#define ensureMsgf(       InExpression, InFormat, ... ) UE_ENSURE_IMPL2(false, InExpression, InFormat, ##__VA_ARGS__)
#define ensureAlways(     InExpression                ) UE_ENSURE_IMPL (true,  InExpression)
#define ensureAlwaysMsgf( InExpression, InFormat, ... ) UE_ENSURE_IMPL2(true,  InExpression, InFormat, ##__VA_ARGS__)
```

**展开（第 430-443 行）：**
```cpp
#define UE_ENSURE_IMPL(Always, InExpression) \
    ( LIKELY(!!(InExpression)) || \
      ( CheckEnsureFailed(Always, bGEnsureHasExecuted<FileLineHashForEnsure(__FILE__, __LINE__)>, \
                          __FILE__, __LINE__, #InExpression) && \
        UE_BREAK_AND_RETURN_FALSE() ) )
```

### 3.1 `ensure` vs `ensureAlways` 的唯一区别

**源码第 403-415 行：**
```cpp
template <uint64 Uid>
std::atomic<uint8> bGEnsureHasExecuted = false;

constexpr uint64 FileLineHashForEnsure(const char* Filename, uint32 Line) { /* djb2 hash */ }
```

**→ `bGEnsureHasExecuted` 是按「文件名 + 行号」哈希出的**模板实例**，每个 `ensure` 位置一份。**

| 宏 | `Always` | 同一位置触发几次 |
| --- | --- | --- |
| `ensure` | `false` | **只有第一次**（之后 `bGEnsureHasExecuted` 已置位，静默）|
| `ensureAlways` | `true` | **每次都触发** |

> **⚠️ 这条极其重要：`ensure` 在同一行只报一次。
> 如果它第一次触发时你没在看日志，之后**永远不会再出现** —— 看起来像"偶发问题自己好了"。**

**排查建议：怀疑某个 `ensure` 时，把它周围的日志级别调高，或者临时改成 `ensureAlways`。**

### 3.2 `ensure` **不中断**执行

**展开里 `UE_BREAK_AND_RETURN_FALSE()` 只是个表达式，返回 `false`。**
**它不会中止函数，只会在**附加了调试器**时 `PLATFORM_BREAK()`。**

**→ 没有调试器时，`ensure` 失败只是一条日志，代码继续跑。**

**这就是「ensure 报了一堆但游戏照常运行」的原因。**

### 3.3 `DO_ENSURE = 0` 时

**源码第 469 行：**
```cpp
#define ensure( InExpression ) (LIKELY(!!(InExpression)))
```
**→ 仍然求值，但**不报告**。副作用保留。**

---

## 四、四种断言的完整对照

| 宏 | 编辑器（Dev）| 打包版默认 | 求值副作用 | 中止执行 | 报告频率 |
| --- | --- | --- | --- | --- | --- |
| `check` / `checkf` | 中断 + 日志 | **可能不求值** | ❌ 不可靠 | ✅ 是 | 每次 |
| `verify` | 中断 + 日志 | **会求值**，不检查 | ✅ 保留 | ✅ 是（Dev）| 每次 |
| `ensure` / `ensureMsgf` | 日志 + 可能断点 | 不报告 | ✅ 保留 | ❌ 否 | **同一行一次** |
| `ensureAlways` / `ensureAlwaysMsgf` | 日志 + 可能断点 | 不报告 | ✅ 保留 | ❌ 否 | **每次** |

---

## 五、排查时的实用判断

### 5.1 「编辑器里好好的，打包后行为不一样」

**第一嫌疑：`check()` 里的副作用在打包版消失了。**

**排查方法：**
```powershell
# 搜所有 check( 调用，看表达式里有没有函数调用/赋值
Select-String -Path Source\**\*.cpp -Pattern '\bcheck\w*\s*\(' |
  Where-Object { $_.Line -match '\w+\s*\(' }
```

**本项目的搜索结果：**
```
Source/LingXuJie 下没有任何 check / verify / ensure 调用
```
**→ 灵虚界目前完全不用断言。这既是好事（没有这个陷阱），也是空白（缺少契约检查）。**

### 5.2 「ensure 只报了一次就消失了」

**这是 `ensure` 的定义行为，不是 bug。**

**要每次都看到，改成 `ensureAlways`。**

### 5.3 「崩溃了但没有有效调用栈」

**`check` 失败会走 `FDebug::CheckVerifyFailedImpl2` —— 它会先弹对话框。
自动化环境里那个对话框会**挡住一切**（见 gotcha #61）。**

**→ CI / 批量脚本里跑，应该关掉对话框或用 `-unattended`。**

---

## 六、待办（本项目）

| 事项 | 状态 |
| --- | --- |
| 全项目**零断言** | 已核实（grep 无匹配）|
| 给关键前置条件加 `check` | 待做（用户要求先学习不开发）|
| 给可恢复的异常加 `ensureAlways` | 待做 |
| 核实 `USE_CHECKS_IN_SHIPPING` 在本项目 | 待查 `Target.cs` |

**⚠️ 按用户要求本章**只读不改**，C++ 一字未动。**

---

## 七、本篇依据的源码位置

| 事实 | 文件 | 行 |
| --- | --- | --- |
| `check` / `verify` 在 `DO_CHECK=1` 时相同 | `Misc/AssertionMacros.h` | 221-230 |
| `UE_CHECK_IMPL` 展开 | 同上 | 235-249 |
| `DO_CHECK=0` 时 `check` 变 `CA_ASSUME` | 同上 | 319-324 |
| `ensure` 只报一次靠 `bGEnsureHasExecuted` | 同上 | 403-415, 430-443 |
| `ensure` 不中断靠 `UE_BREAK_AND_RETURN_FALSE` | 同上 | 417-428 |
| `DO_ENSURE=0` 时 `ensure` 变弱 | 同上 | 467-469 |
| 各构建的 `DO_CHECK` / `DO_ENSURE` | `Misc/Build.h` | 241-333 |

---

**下一篇：`Docs/UE5-DEBUG-CRASH.md` —— 崩溃、调用栈、.dmp 与 Crash Reporter 的自动化处理。**
