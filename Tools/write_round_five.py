"""Append the fifth round to the handoff, including the correction.

    python Tools/write_round_five.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 22. UE5 第五轮：Gameplay 流程 + 输入系统 + 一个重要更正（2026-11-26 19:45）

### 一、新增两篇

| 文档 | 内容 |
| --- | --- |
| **`UE5-GAMEPLAY-FLOW.md`** | **从关卡加载到玩家能操作的 14 步**（全部源码逐一确认）|
| **`UE5-INPUT.md`** | 输入的三代方案 + **本项目用第一代** |

### 二、Gameplay 流程（14 步，源码确认）

```
GameInstance::Init → World::BeginPlay → SpawnActor → GameMode::InitGame
→ PostLogin → HandleStartingNewPlayer → RestartPlayer
→ [ChoosePlayerStart + SpawnDefaultPawnFor] → RestartPlayerAtPlayerStart
→ PlayerController::SetPawn → Pawn::PossessedBy → AcknowledgePossession
→ Actor::BeginPlay → 每帧 PlayerTick / Tick
```

**关键：`BeginPlay` 在**所有生成和占有之后**才跑，所以里面能拿到 Controller 和 Pawn。**

**我们的日志 `Player ready at V(...)` 就是 `BeginPlay` 打的 ——
它出现就说明 ①到⑫ 全走完了。**

### 三、🔴 发现本项目的输入矛盾

```
LXJCharacter.cpp:
  SetupPlayerInputComponent  0 处
  BindAction                 0 处
  IsInputKeyDown            18 处
  EKeys::                   20 处
```

**角色在 `Tick` 里轮询 `PC->IsInputKeyDown(EKeys::W)`，完全绕过输入系统。**

**但 `Config/DefaultInput.ini` 第 86-87 行写着：**
```ini
DefaultPlayerInputClass=/Script/EnhancedInput.EnhancedPlayerInput
DefaultInputComponentClass=/Script/EnhancedInput.EnhancedInputComponent
```

**引擎装的是第三代 Enhanced Input，我们在用第一代轮询。**

**判断：P0 不改。** 理由：键鼠够用、改要编译、现在改不会让游戏变好。
**该改的时机：做设置面板（改键）之前 —— 那时轮询做不出来。**

### 四、🔴 一个必须记下的更正

**我先前写「107 个遗留资产待清理」—— **这是错的**。**

**实测：**
```
jp_roof00            -> Texture2D   被 M_LZ_JP_ROOF00 引用
17_101_stonew01      -> Texture2D   被 M_LZ_17_101_STONEW01 引用
```

**它们是被材质实例引用的**贴图**，不是遗留资产。
按我的判断去删，**整座城的贴图会全部丢失。**（gotcha #75）**

**正确构成（实测）：**
| 类别 | 数量 |
| --- | --- |
| `SM_LZ_*` 网格 | 96 |
| `M_LZ_*` 材质实例 | 95 |
| `M_Moxiang_*` 母材质 | 4 |
| 贴图 | 104 |
| **合计** | **299** |

**教训：删之前必须查 `get_asset_class` + `get_referencers`，两个都查完才知道能不能删。**

### 五、掌握度更新

| 域 | 上一轮 | 本轮 |
| --- | --- | --- |
| **Gameplay 流程** | 60% | **65%**（14 步 + 钩子全清）|
| **输入系统** | 0 | **45%**（三代方案 + 本项目的选择）|

### 六、下一步

| 顺位 | 任务 | 备注 |
| --- | --- | --- |
| 1 | 音频接入关卡 | 有 SoundClass 体系了 |
| 2 | Lumen | 渲染 35% 里最大空白 |
| 3 | 动画实操 | 等 .mod 蒙皮 |
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 22." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 22; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
