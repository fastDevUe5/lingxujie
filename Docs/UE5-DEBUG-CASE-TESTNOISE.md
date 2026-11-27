# 实战诊断 006：把引擎的测试噪音当成项目的失败

> **起点：日志里 13 条 `LogAutomationTest: Error: Condition failed`。**
>
> **结论：这 13 条来自**引擎自己的实验性测试** `UnifiedErrorTests.cpp`，
> 与本项目毫无关系。项目自己的 15 个测试**全部通过**。**
>
> **日期：2026-11-26 · UE 5.8.4**

---

## 一、起点：13 条「测试失败」

**分类统计日志时，这是数量第三多的错误类：**
```
LogAutomationTest        Error   13   Condition failed
```

**→ 「13 个测试失败」听起来是个严重问题。**

---

## 二、上下文立刻给出了答案

**看日志原文（✅ 实测）：**
```
LogTemp: Error test: UE::UnifiedErrorTest::Empty: [空错误]
LogTemp: Error with param: UE::UnifiedErrorTest::WithInt: [整数-7出错]
LogTemp: Error with context: UE::UnifiedErrorTest::Empty: [空错误]
LogTemp: FError that has been invalidated: ::: []
LogTemp: FError that has been moved from: ::: []
LogAutomationTest: Error: Condition failed      ×13
```

**`UE::UnifiedErrorTest` —— 这是引擎在测**它自己的错误系统**。**

---

## 三、源码核实

**`Runtime/Core/Tests/Experimental/UnifiedError/UnifiedErrorTests.cpp`**

**那几个 `LogTemp` 行**逐字对应**文件末尾的冒烟代码：**
```cpp
FError Empty = UE::UnifiedErrorTest::Empty();
UE_LOGFMT(LogTemp, Log, "Error test: {Error}", Empty);

FError WithInt = UE::UnifiedErrorTest::WithInt(-7);
UE_LOGFMT(LogTemp, Log, "Error with param: {Error}", WithInt);

FError WithContext = UE::UnifiedErrorTest::Empty();
UE_LOGFMT(LogTemp, Log, "Error with context: {Error}", WithContext);

FError Invalidated = UE::UnifiedErrorTest::WithInt(99);
Invalidated.Invalidate();
UE_LOGFMT(LogTemp, Log, "FError that has been invalidated: {Error}", Invalidated);

FError MovedFrom = UE::UnifiedErrorTest::Empty();
FError MovedTo(MoveTemp(MovedFrom));
UE_LOGFMT(LogTemp, Log, "FError that has been moved from: {Error}", MovedFrom);
```

**→ **五行日志，两种语言（LogTemp 与中文错误文本），前缀完全吻合。**这是**同一个文件**产生的。**

**而 `Condition failed` 来自文件里那些 `CHECK(...)`：**
```cpp
CHECK(Empty.GetErrorCode() == (int32)ETestErrorCodes::Empty);
CHECK(Empty.GetModuleId() == UE::UnifiedErrorTest::GetStaticModuleId());
CHECK(WithInt.GetErrorCode() == (int32)UE::UnifiedErrorTest::WithInt.ErrorCode);
...
```

**⚠️ `CHECK` 就是 `LowLevelTestAdapter.h` 里那个**自动化测试专用断言宏**
（和 `check` / `verify` / `ensure` 完全不同的东西，见 `UE5-DEBUG-ASSERTS.md`）。
**它失败时打的正是 `LogAutomationTest: Error: Condition failed`。**

**→ 完整链条闭合：引擎测试 → `CHECK` 失败 → 13 条日志。**

---

## 四、🎯 真正的信号：项目自己的测试

**这 13 条与项目无关。那**项目的**测试是什么状态？—— 这才是该问的。**

**`Tools/RunTests.ps1` 用**独立的无头进程**跑（不打扰编辑器）：**
```powershell
& $Cmd "$Project" `
    "-ExecCmds=Automation RunTests LingXuJie" `
    "-TestExit=Automation Test Queue Empty" `
    -unattended -nosplash -nop4 ...
```

**✅ 实测结果：**
```
Test Completed. Result={Success} Name={AutoEquip}         Path={LingXuJie.Inventory.AutoEquip}
Test Completed. Result={Success} Name={Equip}             Path={LingXuJie.Inventory.Equip}
Test Completed. Result={Success} Name={Stacking}          Path={LingXuJie.Inventory.Stacking}
Test Completed. Result={Success} Name={Catalog}           Path={LingXuJie.Items.Catalog}
Test Completed. Result={Success} Name={DropTable}         Path={LingXuJie.Items.DropTable}
Test Completed. Result={Success} Name={AggroAndAttack}    Path={LingXuJie.MonsterBrain.AggroAndAttack}
Test Completed. Result={Success} Name={Leash}             Path={LingXuJie.MonsterBrain.Leash}
Test Completed. Result={Success} Name={PatrolAndReturn}   Path={LingXuJie.MonsterBrain.PatrolAndReturn}
Test Completed. Result={Success} Name={AddExperienceLevelsUp} ...
Test Completed. Result={Success} Name={ExperienceCurve}   ...
Test Completed. Result={Success} Name={KillReward}        ...
Test Completed. Result={Success} Name={LevelCap}          ...
Test Completed. Result={Success} Name={LevelUpFlash}      ...
Test Completed. Result={Success} Name={StatRewards}       ...
Test Completed. Result={Success} Name={ModuleLoaded}      Path={LingXuJie.Smoke.ModuleLoaded}
----
completed=15 failed=0
ALL TESTS PASSED
```

**→ **15 个全过。项目测试是健康的。**

---

## 五、🔴 教训：怎么区分引擎噪音和项目失败

**日志是**混合**的 —— 引擎、插件、项目都往里写。**
**同样的 `Error` 级别，可能是**引擎自测**，也可能是**真失败**。**

| 判据 | 引擎噪音 | 项目失败 |
| --- | --- | --- |
| **测试名/路径** | `UE::UnifiedErrorTest` / `Runtime/Core/Tests/` | `LingXuJie.*` / `Source/LingXuJie/Private/Tests/` |
| **时间戳** | 启动阶段、帧号 `[0]` | 运行 `RunTests` 时 |
| **周围的日志** | 与引擎源码逐字对应 | 只有测试框架输出 |
| **可复现** | 每次启动都有 | 改坏了才出现 |

**→ 最可靠的一招：**把日志行去源码里搜**。
那些 `LogTemp` 行和 `UnifiedErrorTests.cpp` **一字不差**，一搜就定位。**

**这正是本系列反复用的方法：**日志里的字符串，在源码里一定存在。****

---

## 六、顺带确认的一件事

**`RunTests.ps1` 用 `UnrealEditor-Cmd.exe`（commandlet 版）独立进程，
**不碰正在运行的编辑器**。**

**→ 这是安全验证项目的正确方式。**
**→ 和 `RunGame.ps1`（会 `Stop-Process` 编辑器）完全不同 —— 那条规则 2 禁的是后者。**

---

## 七、待办

| 事项 | 状态 |
| --- | --- |
| 把「引擎测试噪音」加进体检工具的输出说明 | 待做 |
| 把 `RunTests` 结果也纳入体检 | 待做（需独立进程，不适合放在编辑器内脚本里）|

**⚠️ 代码一字未改。**
