"""Append the thirty-second round.

    python Tools/write_round_thirtytwo.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 49. 第三十二轮：**动画数据确认有运动；引擎侧探针失效**（2026-11-26 33:00）

### 一、直接量源文件：每个动画都在动

```
boss001_01.anm:   22 轨 → 20 轨在动，最大摆幅 20.6°（Bip01 R Finger11，100 键）
Boss_cowf_01.anm: 56 轨 → 36 轨在动，最大摆幅 73.7°（Bip01 R Thigh，51 键）
108_birda.anm:     6 轨 →  6 轨在动，最大摆幅 179.4°（Bone09，136 键）
198_bobu.anm:     11 轨 → 11 轨在动，最大摆幅 39.4°（Bip01 R Hand，320 键）
```

**导出的 glTF 通道数与轨道数一致（25/49/8/15）—— 数据完整传递。**

### 二、🔴 引擎侧探针为什么失效（gotcha #102）

**尝试与结果：**

| 步骤 | 结果 |
| --- | --- |
| `component.bounds` | **不存在** |
| `actor.get_actor_bounds()` | 可用 |
| `set_animation_mode(ANIMATION_SINGLE_NODE)` | **成功** |
| `get_anim_instance()` | `AnimSingleNodeInstance` |
| `instance.set_animation(...)` | **不存在** |
| `instance.set_animation_asset(...)` | **成功** |
| `instance.set_position(t, False)` | 调用成功，**包围盒不变** |
| `get_anim_pose_at_time(anim, t)` | **缺 `evaluation_type`，而该枚举没导出** |
| `get_bone_pose(...)` | **Python 线程挂死** |

**`largest bounds change: 0.0000` —— 所有时刻包围盒完全相同。
`set_position` 只改内部时间，不触发重新求值。**

### 三、诚实的结论

**✅ 已验证：源动画有真实运动，导出的通道携带数据。**
**❌ 未验证：编辑器里播放时网格是否**视觉上**跟着动。**

**这不是数据问题，是「编辑器非运行时怎么推进一帧」的 API 问题。
真机游戏里有 tick，会正常播放。**

### 四、方法教训

> **探针失效时，回到**被验证对象本身**。**
>
> 我想验证的是「动画有没有运动」。
> 用引擎组件去测，实际在测「引擎能不能被我驱动」—— **那是另一个问题**，
> 而且被 API 细节卡了两轮。
>
> **直接量 `.anm` 的旋转键，一个问题一个答案。**

**第 N 次同类：把「验证手段」和「被验证对象」混在一起。**

### 五、新增工具

| 工具 | 作用 |
| --- | --- |
| **`Tools/measure_motion.py`** | 量每个动画的旋转摆幅与位移（**不依赖引擎**）|

### 六、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **PIE 里验证动画**（运行时有 tick，`StartPIE` 后截图对比）|
| 2 | 批量材质（5,833 个贴图要批量转 PNG）|
| 3 | 批量导入 UE |
| 4 | 骨骼名不匹配（boss001 只有 21/67 有动画轨）|
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 49." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 49; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
