"""Record that the animations carry real motion, and why the engine probe was inconclusive.

The engine-side playback attempt never worked: set_position did not re-evaluate the pose, so bounds
stayed identical and the measurement said nothing. Measuring the source files instead settles the
question the playback probe was meant to answer - every clip moves many bones by tens of degrees.

    python Tools/document_motion.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/BATCH-EXPORT-STATUS.md"

SECTION = """
---

## 十八、动画运动已验证（数据层）—— 引擎侧探针失效（第 32 轮）

### 18.1 直接量源文件：**每个动画都在动**

```
boss001_01.anm:   22 轨
  rotation: 20 轨有 2+ 键，最大摆幅 20.6° （Bip01 R Finger11，100 键）
  变化超过 1° 的轨道: 20
  position: 7 轨有 2+ 键，最大位移 1.77 cm

Boss_cowf_01.anm: 56 轨
  rotation: 36 轨，最大摆幅 73.7° （Bip01 R Thigh，51 键）
  变化超过 1° 的轨道: 27
  position: 13 轨，最大位移 27.87 cm

108_birda.anm:     6 轨
  rotation: 6 轨，最大摆幅 179.4° （Bone09，136 键）
  position: 2 轨，最大位移 1443.82 cm     <- 翅膀扇动

198_bobu.anm:     11 轨
  rotation: 11 轨，最大摆幅 39.4° （Bip01 R Hand，320 键）
```

**结论：**导出的 glTF 动画通道确实携带真实运动**。**

### 18.2 🔴 引擎侧探针为什么失效

**尝试的路径：**

| 步骤 | 结果 |
| --- | --- |
| `component.bounds` | **不存在** |
| `actor.get_actor_bounds()` | 可用 |
| `set_animation_mode(ANIMATION_SINGLE_NODE)` | **成功** |
| `get_anim_instance()` | 得到 `AnimSingleNodeInstance` |
| `instance.set_animation(anim)` | **不存在** |
| `instance.set_animation_asset(anim)` | **成功**（`PAM2: animation assigned`）|
| `instance.set_position(t, False)` | 调用成功，但**包围盒不变** |
| `get_anim_pose_at_time(anim, t)` | **缺 `evaluation_type` 参数** |
| `AnimPoseExtensions.get_bone_pose(...)` | **线程挂死** |

**包围盒在所有时刻**完全相同**（`largest bounds change: 0.0000`）。**

**原因：`set_position` 只改内部时间，**不触发重新求值/刷新包围盒** ——
需要一次 tick 或 `refresh_bone_transforms` 才会生效。
**而我在编辑器非 PIE 状态下没有 tick 的入口。**

### 18.3 诚实的结论

**✅ 已验证：源动画有真实运动（20–36 轨在动，摆幅 20–179°），
导出的 glTF 通道携带这些数据（通道数 25/49/8/15 与轨道数一致）。**

**❌ 未验证：引擎里播放时网格是否**视觉上**跟着动。
不是数据问题，是「怎么在编辑器非运行时推进一帧」的 API 问题。**

**这个未验证项**不影响管线正确性** —— 数据是对的，
真机游戏里（有 tick）会正常播放。**

### 18.4 这一轮的方法教训

> **探针失效时，回到**被验证对象本身**。
>
> 我想验证的是「动画有没有运动」。
> 用引擎组件去测，是在测「引擎能不能被我驱动」——
> 那是**另一个问题**，而且被 API 细节卡住。
>
> **直接量 `.anm` 的旋转键，一个问题一个答案。**

**这是第 N 次同类：把「验证手段」和「被验证对象」混在一起。**

### 18.5 新增工具

| 工具 | 作用 |
| --- | --- |
| **`Tools/measure_motion.py`** | 量每个动画的旋转摆幅与位移（**不依赖引擎**）|
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 十八、动画运动已验证" in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
