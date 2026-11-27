"""Append the fifteenth debugging round.

    python Tools/write_debug_round15.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 72. 调试系列第 15 轮：**一条无害警告，和一个被推翻的假设**（2026-11-26 57:00）

### 一、起点：可能是推翻案例 001 的那条警告

**日志里的 `LogAnimation: Warning: Invalid animation skeleton`。
我怀疑它会让案例 001 的结论不成立。**

**先看上下文（✅ 实测）：**
```
D3: VERDICT: the animation moves the skeleton once it is assigned
LogAnimation: Warning: Invalid animation skeleton        ← 夹在这两行之间
D3: restored: mode=ANIMATION_BLUEPRINT anim=None
```

**→ 它夹在我的「VERDICT」和「restored」之间 —— 是**我恢复代码**产生的，不是项目问题。**
**→ **不推翻**案例 001。**

### 二、源码给出触发条件

**`SkeletalMeshComponent.cpp` 1589-1600：**
```cpp
if (PropertyThatChanged == AnimToPlay) {
    if (AnimationData.AnimToPlay && AnimationData.AnimToPlay->GetSkeleton()) {
        PlayAnimation(AnimationData.AnimToPlay, false);
    } else {
        UE_LOGF(LogAnimation, Warning, "Invalid animation skeleton");
        AnimationData.AnimToPlay = nullptr;
    }
}
```

**→ 触发条件：把 `AnimToPlay` 设成 **null**。**
**→ 我的恢复代码正是 `set_editor_property("anim_to_play", None)`。**
**→ **完全无害**。清空动画是合法操作。**

**连带（第 1501 行）：**
```cpp
if (AnimationMode == AnimationBlueprint) {
    if (AnimClass == nullptr) ClearAnimScriptInstance();   // ← 销毁单节点实例
}
```
**→ 我的恢复先改 mode 再清空 anim，两步合起来完全解释了那条警告。**

### 三、🎯 源码独立确认了案例 001 的两条结论

| 案例 001 的结论 | 源码依据 |
| --- | --- |
| 赋 `anim_to_play` 就会播放 | `PlayAnimation(AnimationData.AnimToPlay, false)` |
| `set_position` 会重新求值 | `SetPosition(AnimationData.SavedPosition, false)` |

**→ 这两条当初是**测出来**的，现在源码给出**机制**。**
**→ 方向对了：先测事实，再找机制。**

### 四、🔴 我的假设，和它被推翻

**假设：「必须先设 animation_mode，再赋 anim_to_play。
反过来的话 PlayAnimation 时还没有单节点实例，动画不启动。」**

**听起来合理，而且源码支持这个推理。**

**实验：同一 actor 两种顺序各测一次，看骨骼在 t=0 / t=0.5 有没有移动。**

**✅ 实测：**
```
mode_first   t=0 (9428.8, -6355.8, 3717.7)  t=0.5 (9428.7, -6358.4, 3721.0)  moved=True
anim_first   t=0 (9428.8, -6355.8, 3717.7)  t=0.5 (9428.7, -6358.4, 3721.0)  moved=True

VERDICT: the order does not matter here
```

**→ **两种顺序都动了，坐标完全相同。假设被推翻。****

**为什么错：我的采样函数最后还会写一次 `animation_data`，而 `SavedPosition` 变化会调
`SetPosition(...)` 求值。所以只要最终状态对，中间顺序不影响。**

**⚠️ 教训：读一段源码得出「必须这样」，可能只是**忽略了同文件里的另一条路径**。**

### 五、这轮的三个收获

| # | 收获 | 性质 |
| --- | --- | --- |
| 1 | `Invalid animation skeleton` 无害 | **排除假警报** |
| 2 | 源码确认案例 001 两条结论 | **机制补充** |
| 3 | 「顺序很重要」被推翻 | **负面结果** |

**⚠️ 第 3 条是**失败**，但我在写进文档前就测掉了。**
**→ 如果当结论写进去，那会是第 5 次「推理真但含义错」。**

### 六、新增

| 产出 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-CASE-WARNING.md`** | 警告溯源 + 源码确认 + 被推翻的假设 |
| `Tools/diag_order_step1.py` | 两种赋值顺序的对照实验 |

### 七、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | 查 13 条 `LogAutomationTest: Condition failed` |
| 2 | 查 `T_Boss_Mob01 contains no miplevels` |
| 3 | 或者开始应用已定位的修复 |

**⚠️ 代码仍未改。**
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 72." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 72; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
