"""Append the sixteenth debugging round.

    python Tools/write_debug_round16.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 73. 调试系列第 16 轮：**把引擎的测试噪音当成项目的失败**（2026-11-26 58:00）

### 一、起点：13 条「测试失败」

**分类统计日志时，`LogAutomationTest: Error: Condition failed` 有 13 条 ——
数量第三多的错误类。听起来像严重问题。**

### 二、上下文直接给出答案

**日志原文（✅ 实测）：**
```
LogTemp: Error test: UE::UnifiedErrorTest::Empty: [空错误]
LogTemp: Error with param: UE::UnifiedErrorTest::WithInt: [整数-7出错]
LogTemp: Error with context: UE::UnifiedErrorTest::Empty: [空错误]
LogTemp: FError that has been invalidated: ::: []
LogTemp: FError that has been moved from: ::: []
LogAutomationTest: Error: Condition failed      ×13
```

**`UE::UnifiedErrorTest` —— 引擎在测**它自己的错误系统**。**

### 三、源码核实：逐字对应

**`Runtime/Core/Tests/Experimental/UnifiedError/UnifiedErrorTests.cpp` 末尾：**
```cpp
UE_LOGFMT(LogTemp, Log, "Error test: {Error}", Empty);
UE_LOGFMT(LogTemp, Log, "Error with param: {Error}", WithInt);
UE_LOGFMT(LogTemp, Log, "Error with context: {Error}", WithContext);
UE_LOGFMT(LogTemp, Log, "FError that has been invalidated: {Error}", Invalidated);
UE_LOGFMT(LogTemp, Log, "FError that has been moved from: {Error}", MovedFrom);
```

**→ **五行日志和源码一字不差。**这是同一个文件。**

**而 `Condition failed` 来自文件里的 `CHECK(...)` 断言
（`CHECK` 是自动化测试专用宏，不是 `check`/`ensure`）。**

### 四、🎯 真正的信号：项目测试 15/15 全过

**`Tools/RunTests.ps1` 用**独立无头进程**跑（不打扰编辑器）：**
```
completed=15 failed=0
ALL TESTS PASSED
```

**15 个测试逐条 `Result={Success}`：**
AutoEquip / Equip / Stacking / Catalog / DropTable /
AggroAndAttack / Leash / PatrolAndReturn /
AddExperienceLevelsUp / ExperienceCurve / KillReward / LevelCap / LevelUpFlash / StatRewards /
ModuleLoaded

### 五、🔴 教训：怎么区分引擎噪音和项目失败

| 判据 | 引擎噪音 | 项目失败 |
| --- | --- | --- |
| **测试名/路径** | `UE::UnifiedErrorTest` / `Runtime/Core/Tests/` | `LingXuJie.*` / `Source/LingXuJie/Private/Tests/` |
| **时间戳** | 启动阶段、帧号 `[0]` | 跑 `RunTests` 时 |
| **周围日志** | 与引擎源码逐字对应 | 只有测试框架输出 |
| **可复现** | 每次启动都有 | 改坏了才出现 |

**→ 最可靠的一招：**拿日志行去源码搜。**
**那些 `LogTemp` 行和 `UnifiedErrorTests.cpp` 一字不差，一搜就定位。**

**→ 这正是本系列反复用的方法：日志里的字符串，在源码里一定存在。**

### 六、顺带确认

**`RunTests.ps1` 用 `UnrealEditor-Cmd.exe` 独立进程，**不碰运行中的编辑器**。**
**→ 这是安全验证项目的正确方式。**
**→ 与 `RunGame.ps1`（会 `Stop-Process` 编辑器）完全不同 —— 规则 2 禁的是后者。**

### 七、新增

| 产出 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-CASE-TESTNOISE.md`** | 噪音溯源 + 项目测试实测 + 区分判据 |

### 八、六个案例汇总

| 案例 | 症状 | 性质 |
| --- | --- | --- |
| 001 动画 | 看不见动 | **真缺陷**（脚本没赋值）|
| 002 法线 | 引擎警告 | **真缺陷**（NOT_SOLID 无语义法线）|
| 003 IBM | 模型散开 | **真缺陷**（转置两次 + 单位）|
| 004 材质 | 101 个缺材质 | **误报 + 1 个真缺陷** |
| 005 警告 | Invalid animation skeleton | **无害** |
| **006 测试** | **13 个测试失败** | **引擎噪音，项目 15/15 全过** |

**→ 六个里只有三个是真缺陷。另外三个是**误报、无害、噪音**。**
**→ 这个比例（50%）说明「识别不是什么」和「找到是什么」一样重要。**

### 九、下一轮

| 顺序 | 任务 |
| --- | --- |
| 1 | 查 `T_Boss_Mob01 contains no miplevels` |
| 2 | 开始应用已定位的修复 |

**⚠️ 代码仍未改。**
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 73." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 73; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
