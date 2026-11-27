"""Append the ninth debugging round: the first real case study.

    python Tools/write_debug_round9.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 66. 调试系列第 9 轮：**第一个实战 —— Boss 动画不播放，从零定位到根因**（2026-11-26 51:00）

### 一、起点

**既有记录只说了「动画数据验证过，但引擎驱动被阻塞」—— 这是个**没有定位**的问题。**
**我从零开始，不采信那句话。**

### 二、四步定位

| 步 | 脚本 | 结果 |
| --- | --- | --- |
| 1 | `diag_anim_step1.py` | 只观察。**`get_play_rate=0.0` 误导了我** |
| 2 | `diag_anim_step2.py` | **直接 dump 结构体 → 找到根因一** |
| 3 | `diag_anim_step3.py` | 失败两次（API 签名）后成功，**验证根因二** |
| 4 | 恢复原状 | 确认改动可逆 |

### 三、🔴 根因：一个脚本里两处

**`Tools/import_and_place.py`：**
```python
if anim is not None:
    length = anim.get_editor_property("sequence_length")
    log("  animation length %.4f s" % length)     # ← 打了长度，然后把它扔了
    ...
component.set_skeletal_mesh_asset(mesh)          # ← 只设网格
                                                  # ← 从没设 animation_mode
                                                  # ← 从没设 anim_to_play
level.save_current_level()                        # ← 顺便：19:52 崩溃的调用
```

**实测确认的组件状态：**
```
mode = <AnimationMode.ANIMATION_BLUEPRINT: 0>     ← 默认模式，不是 SINGLE_NODE
anim_to_play = None                                ← 没有动画
```

### 四、验证（不改项目，改完恢复）

```
D3: bind pose -> (9350.0, -6200.0, 3740.0)
D3: applied single node mode and an animation
D3:   t=0.00 -> (9428.808, -6355.831, 3717.728)
D3:   t=0.25 -> (9428.805, -6356.584, 3718.637)
D3:   t=0.50 -> (9428.727, -6358.372, 3720.965)
D3:   t=0.75 -> (9428.489, -6360.426, 3724.013)
D3: distinct poses across four times: 4
D3: VERDICT: the animation moves the skeleton once it is assigned
D3: restored: mode=ANIMATION_BLUEPRINT, anim=None
```

**→ 四个时间点四个位姿。动画确实驱动了机型。**
**→ 之后恢复原状，关卡没被改。**

### 五、🔴 这次实战更正了两条既有结论

| 我之前说的 | 实际 | 错在哪 |
| --- | --- | --- |
| **「`set_position` 不触发重新求值」** | **会触发** | 当时没有动画被赋值，所以当然不动 |
| **「`get_bone_pose` 挂死 → 读不到骨骼」** | **`get_bone_transform` 完全能用** | 用错了 API |

**共同点：**把「我用这个方法失败了」当成「这件事做不到」。****

**这已经是本系列第 N 次同类错误。已经写进文档第十节。**

### 六、三个 API 坑

| 坑 | 表现 | 正确用法 |
| --- | --- | --- |
| `get_bone_transform(name, BoneSpaces.X)` | **TypeError** | **只传名字**，默认世界空间 |
| `get_play_rate()` | 无实例时返回 0.0，误导 | 读 `animation_data.saved_play_rate`（实际 1.0）|
| `get_asset_by_object_path(SoftObjectPath)` | **TypeError** | `get_assets_by_path` + 过滤 |

### 七、修复方案（**未应用**）

**在 `import_and_place.py` 的 `set_skeletal_mesh_asset` 之后加：**
```python
if anim is not None:
    component.set_editor_property("animation_mode",
                                  unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    data = component.get_editor_property("animation_data")
    data.set_editor_property("anim_to_play", anim)
    data.set_editor_property("saved_playing", True)
    data.set_editor_property("saved_play_rate", 1.0)
    component.set_editor_property("animation_data", data)
```

**并建议删掉结尾的 `level.save_current_level()`（崩溃触发点，且关卡由 `build_level.py` 重建）。**

**⚠️ 按用户要求「先不要急着开发」，**代码一字未改**。**

### 八、新增

| 产出 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-CASE-ANIM.md`** | 完整定位记录（起点/四步/根因/验证/更正/修复方案）|
| `Tools/diag_anim_step1.py` | 观察：组件状态 + 可用 API |
| `Tools/diag_anim_step2.py` | dump 结构体，找到根因 |
| `Tools/diag_anim_step3.py` | 验证根因并恢复原状 |

### 九、这次实战的意义

**九篇文档里的方法在这一个真实问题上串起来了：**
- 读结构体不读派生 getter（内存篇的教训）
- `-WaitPattern` 当失败检测（脚本篇）
- 按名字搜资产（资产篇）
- 改完恢复原状（项目规则 5）

**→ 这是第一次「不是写文档，而是用文档解决问题」。**

### 十、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | 再来一个实战案例（候选：78 个模型无 MATERIAL 块 / `thunder3` 转换失败）|
| 2 | 或者：等用户指示后应用这个修复 |
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 66." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 66; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
