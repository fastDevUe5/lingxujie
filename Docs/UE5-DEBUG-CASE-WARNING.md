# 实战诊断 005：一条无害的警告，和一个被推翻的假设

> **起点：日志里一条 `LogAnimation: Warning: Invalid animation skeleton`。
> 我怀疑它会推翻案例 001 的结论。**
>
> **结果：**
> **① 它是**无害的**，由我自己恢复动画时的清空动作触发。**
> **② 源码**独立确认**了案例 001 的两条结论。**
> **③ 我据此提出的「赋值顺序很重要」假设，**被实测推翻**。**
>
> **日期：2026-11-26 · UE 5.8.4 · 源码 `SkeletalMeshComponent.cpp`**

---

## 一、起点：那行警告出现在哪

**日志原文（含上下文）：**
```
D3: distinct poses across four times: 4
D3: VERDICT: the animation moves the skeleton once it is assigned
LogAnimation: Warning: Invalid animation skeleton        ← 这里
D3: restored: mode=<AnimationMode.ANIMATION_BLUEPRINT: 0> anim=None
D3: done
```

**⚠️ 它夹在我的「VERDICT」和「restored」之间。**

**→ 也就是说：它是我**恢复原状**那几行代码产生的，不是项目本身的问题。**

**→ **不推翻**案例 001。**

---

## 二、源码给出触发条件

**`Runtime/Engine/Private/Components/SkeletalMeshComponent.cpp` 第 1589-1600 行：**

```cpp
if (PropertyThatChanged->GetFName() == GET_MEMBER_NAME_CHECKED(FSingleAnimationPlayData, AnimToPlay))
{
    // make sure the animation skeleton is valid
    if (AnimationData.AnimToPlay && AnimationData.AnimToPlay->GetSkeleton())
    {
        PlayAnimation(AnimationData.AnimToPlay, false);
    }
    else
    {
        UE_LOGF(LogAnimation, Warning, "Invalid animation skeleton");
        AnimationData.AnimToPlay = nullptr;
    }
}
```

**→ 触发条件：把 `AnimToPlay` 设成 **null**（或设成没有 skeleton 的动画）。**

**→ 我的恢复代码：**
```python
restored.set_editor_property("anim_to_play", saved_anim)   # saved_anim 是 None
```
**→ 设成 None → 命中 else 分支 → 打警告并置空（本来就是空）。**

**→ **完全无害**。清空一个动画是合法操作，引擎只是顺手警告一句。**

### 2.1 连带的第二个发现

**同一段代码之前（第 1501 行）：**
```cpp
if (PropertyThatChanged->GetFName() == GET_MEMBER_NAME_CHECKED(USkeletalMeshComponent, AnimationMode))
{
    if (AnimationMode == EAnimationMode::AnimationBlueprint)
    {
        if (AnimClass == nullptr)
        {
            ClearAnimScriptInstance();     // ← 销毁单节点实例
        }
        ...
    }
}
```

**→ 我的恢复第一步把 mode 改成 `ANIMATION_BLUEPRINT`，而 `AnimClass` 是 None
→ **销毁了单节点实例**。
→ 第二步再清空 `anim_to_play` → 警告。**

**→ 两步合起来完全解释了那行警告。**

---

## 三、🎯 源码**独立确认**了案例 001 的两条结论

**这段源码是我在这次诊断里第一次读到的，而它恰好印证了我之前**实测**得出的两条：**

| 案例 001 的结论 | 源码依据 |
| --- | --- |
| **「赋了 `anim_to_play` 就会播放」** | `PlayAnimation(AnimationData.AnimToPlay, false)` —— 属性变化时自动播 |
| **「`set_position` 会重新求值」** | `SetPosition(AnimationData.SavedPosition, false)` —— `SavedPosition` 变化时调用 |

**→ 这两条当初是我**测出来**的（四个时间点四个位姿）。
→ 现在源码给出了**机制**。

**⚠️ 这正是本系列想要的方向：先测出事实，再找到机制。反过来的顺序容易变成「读代码想象行为」。**

---

## 四、🔴 我的假设，和它被推翻

**看到 `PlayAnimation` 在**属性变化**时触发，我提出一个假设：**

> **「必须先设 `animation_mode`，再赋 `anim_to_play`。
> 反过来的话，`PlayAnimation` 时还没有单节点实例，动画不会启动。」**

**它听起来很合理，而且源码支持这个推理。**

### 4.1 实验设计

**同一个 actor，两种顺序，各测一次：**
```python
# 顺序 A
component.set_editor_property("animation_mode", ANIMATION_SINGLE_NODE)
data.set_editor_property("anim_to_play", anim)

# 顺序 B（反过来）
data.set_editor_property("anim_to_play", anim)
component.set_editor_property("animation_mode", ANIMATION_SINGLE_NODE)
```
**然后在 t=0 和 t=0.5 各读一次骨骼位置，看有没有移动。**

### 4.2 实测结果（✅）

```
ORDER: mode_first   t=0 (9428.8, -6355.8, 3717.7)  t=0.5 (9428.7, -6358.4, 3721.0)  moved=True
ORDER: anim_first   t=0 (9428.8, -6355.8, 3717.7)  t=0.5 (9428.7, -6358.4, 3721.0)  moved=True

ORDER: mode first: animation moved the bone = True
ORDER: anim first: animation moved the bone = True
ORDER: VERDICT: the order does not matter here
```

**→ **两种顺序都动了，坐标完全相同。假设被推翻。**

### 4.3 为什么假设错了

**我的采样函数在**最后**还会写一次 `animation_data`：**
```python
def sample(component, data, position):
    data.set_editor_property("saved_position", position)
    component.set_editor_property("animation_data", data)    # ← 这次写触发 SetPosition
```

**→ 而 `SavedPosition` 变化会调用 `SetPosition(...)` 求值。
→ 所以**只要最终状态对，中间顺序不影响结果**。**

**→ 推理的漏洞：我只考虑了 `PlayAnimation` 这一条触发路径，
没想到 **`SetPosition` 也是一条独立的求值路径**，而它在两种顺序下都会跑。**

**⚠️ 教训：读一段源码得出「必须这样」，可能只是**忽略了同文件里的另一条路径**。**

---

## 五、这一轮的实际收获

| # | 收获 | 性质 |
| --- | --- | --- |
| 1 | **`Invalid animation skeleton` 无害**，清空动画即触发 | **排除一个假警报** |
| 2 | 源码确认案例 001 的两条结论 | **机制补充** |
| 3 | 「顺序很重要」的假设**被推翻** | **负面结果** |

**→ 第 2 条让我对案例 001 更有信心（实测 + 源码双重支持）。
→ 第 1 条让日志里少一条误报。
→ 第 3 条是**失败**，但也是有价值的失败。**

**⚠️ 我没有把「顺序很重要」写进任何文档的结论区，因为它在写之前就被测掉了。**

**如果把假设当结论写进去，那会是第 5 次「数字/推理真但含义错」。**

---

## 六、待办

| 事项 | 状态 |
| --- | --- |
| 把「清空 animation 会打这条警告」写进 gotcha | 待做 |
| 继续查 13 条 `LogAutomationTest: Condition failed` | 待做 |
| 查 `T_Boss_Mob01 contains no miplevels` | 待做 |

**⚠️ 代码一字未改。**
