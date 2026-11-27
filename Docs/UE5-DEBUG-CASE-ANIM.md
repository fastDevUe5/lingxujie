# 实战诊断 001：Boss 动画不播放

> **本篇不是「知识文档」，是一次**真实故障的完整定位记录**。**
>
> **问题：`MX_BOSS001` 有 25 条动画通道、67 根骨骼、动画资产也在，
> 但在编辑器里**看不见它在动**。**
>
> **结论：`import_and_place.py` 设了网格却**从未设过动画模式，也从未赋值动画**。**
> **根因两处，都在同一个脚本里。**
>
> **日期：2026-11-26 · UE 5.8.4 · 用调试系列第 1/6/9 篇的方法**

---

## 一、起点：只有一句模糊的描述

**既有记录说：「动画数据验证过，但引擎驱动被阻塞」。
再往下就没有了 —— 这是个**没有定位**的问题。**

**我从零开始，不采信这个描述。**

---

## 二、第一步：观察，不假设

**脚本 `Tools/diag_anim_step1.py` 只做观察：找 actor、看组件状态、列出可用的骨骼读取 API。**

**输出（关键部分）：**
```
D1: level holds 116 actor(s)
D1: candidate actor: 'MX_BOSSCOWF' (SkeletalMeshActor)
D1: candidate actor: 'MX_BOSS001' (SkeletalMeshActor)
D1: mesh asset: '/Game/Moxiang/Skeletal/Characters/boss_cowf/SkeletalMeshes/S...'
D1: component.animation_data = <Struct 'SingleAnimationPlayData' ...>
D1: component.anim_class = None
D1:     is_playing -> False
D1:     get_play_rate -> 0.0
```

### 2.1 第一印象是错的

**`get_play_rate() -> 0.0` 看起来像「播放速率被设成 0」。
如果就此下结论，会去查谁设了 `play_rate`，方向就错了。**

**⚠️ 这是本系列反复出现的陷阱：派生 getter 返回的值可能量的是另一件事。**

### 2.2 同时解决了「读不到骨骼」这个老问题

**第 1 步顺带列出了组件上所有骨骼相关 API，发现：**
```
get_bone_transform      ← 🔴 这个一直都在
get_socket_location
get_num_bones / get_bone_name / get_bone_index
```

**→ 之前我用的 `AnimPoseExtensions.get_bone_pose` 会挂死，
但**普通的 `get_bone_transform` 完全能读骨骼世界坐标**。**

**→ 「读不到骨骼」这个判断本身就是错的 —— 是**用错了 API**。**

---

## 三、第二步：读结构体，不读派生 getter

**脚本 `Tools/diag_anim_step2.py` 直接 dump `animation_data` 的每个字段。**

**输出：**
```
D2: animation_data type = SingleAnimationPlayData
D2:     animation_data.anim_to_play = None          ← 🔴 根因一
D2:     animation_data.saved_looping = True
D2:     animation_data.saved_play_rate = 1.0        ← 速率其实是 1.0！
D2:     animation_data.saved_playing = True
D2:     animation_data.saved_position = 0.0
D2: component.get_play_rate() = 0.0                  ← 派生 getter 骗了我
D2: component.is_playing() = False
D2: component.get_num_bones() = 67
D2:     bone 0 = Bip01 / bone 66 = Bone28
```

### 3.1 🔴 两个结论同时确立

**① `saved_play_rate` 其实是 **1.0** —— 第一步看到的 `0.0` 是派生 getter 在**没有动画实例**时返回的默认值。**

**② `anim_to_play = None` —— **根本没有动画被赋值**。**

**→ 「动画不播放」的真相是**没有可播放的东西**。**

---

## 四、第三步：找谁该负责

**`MX_BOSS001` 不在 `build_level.py` 里。全工程搜索找到 `Tools/import_and_place.py`。**

**读它的代码（第 60 行之后）：**
```python
if anim is not None:
    length = anim.get_editor_property("sequence_length")
    log("  animation length %.4f s" % length)     # ← 只打了长度
    ...
component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
if component is not None:
    component.set_skeletal_mesh_asset(mesh)        # ← 只设了网格
actor.set_actor_scale3d(...)
                                                   # ← 🔴 根因二：从没设 animation_mode
                                                   # ← 🔴 根因一：从没设 anim_to_play
level.save_current_level()                         # ← ⚠️ 顺便：这正是崩溃的那次调用
```

**→ 脚本**找到了**动画资产，**打了它的长度**，然后就**把它扔了**。**

---

## 五、第四步：验证根因（不改项目）

**脚本 `Tools/diag_anim_step3.py`：**
1. 记下当前状态
2. 设 `animation_mode = ANIMATION_SINGLE_NODE`
3. 赋值 `anim_to_play`
4. 在四个时间点读同一根骨骼的世界坐标
5. **恢复原状**

**输出：**
```
D3: bone count: 67, sampling bone 10 = Name("Bip01-L-Clavicle")
D3: bind pose -> (9350.0, -6200.0, 3740.0)
D3: state before: mode=<AnimationMode.ANIMATION_BLUEPRINT: 0> anim=None
D3: applied single node mode and an animation
D3:   t=0.00 -> (9428.808, -6355.831, 3717.728)
D3:   t=0.25 -> (9428.805, -6356.584, 3718.637)
D3:   t=0.50 -> (9428.727, -6358.372, 3720.965)
D3:   t=0.75 -> (9428.489, -6360.426, 3724.013)
D3: distinct poses across four times: 4
D3: VERDICT: the animation moves the skeleton once it is assigned
D3: restored: mode=ANIMATION_BLUEPRINT, anim=None
```

### 5.1 🎯 根因二得到确认

```
state before: mode=<AnimationMode.ANIMATION_BLUEPRINT: 0>
```

**→ 组件的动画模式是 **`ANIMATION_BLUEPRINT`（默认值 0）**，不是 `ANIMATION_SINGLE_NODE`。**

**→ 在 `ANIMATION_BLUEPRINT` 模式下，即使赋了 `anim_to_play`，也不会播放。**

**→ `import_and_place.py` 两个都没设，所以**双重失效**。**

### 5.2 骨骼真的在动

**四个时间点给出 **4 个不同的坐标**。动画确实在驱动机型。**

---

## 六、🔴 这次诊断更正了我两条既有结论

| 我之前说的 | 实际 | 错在哪 |
| --- | --- | --- |
| **「`set_position` 不触发重新求值」** | **会触发** —— 实测四个时间点四个位姿 | 当时没有动画被赋值，所以当然不动 |
| **「`get_bone_pose` 挂死 → 读不到骨骼」** | **`get_bone_transform` 完全能用** | 用错了 API，把「这个 API 不行」当成「读不到」 |

**⚠️ 这两条都是同一个毛病的变体：
**把「我用这个方法失败了」当成「这件事做不到」。**

**第一次是说「引擎不重新求值」，其实是「没有东西可求值」。
第二次是说「读不到骨骼」，其实是「没用对函数」。**

---

## 七、修复方案（**尚未应用**）

**`Tools/import_and_place.py` 需要在 `set_skeletal_mesh_asset` 之后加：**

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

**⚠️ 另外建议删掉结尾的 `level.save_current_level()`：**
**它是 19:52 那次崩溃的触发点（见 `UE5-DEBUG-CRASH.md`），
而关卡本来就由 `build_level.py` 幂等重建，不需要从这里保存。**

**⚠️ 按用户要求「先不要急着开发」，我**没有改代码**。
这只是验证过的修复方案，等指令。**

---

## 八、顺带发现的三个 API 坑

| 坑 | 表现 | 正确用法 |
| --- | --- | --- |
| `get_bone_transform(name, BoneSpaces.X)` | **TypeError** | **只传名字**，默认就是世界空间 |
| `get_play_rate()` | 无实例时返回 **0.0**，误导 | 读 `animation_data.saved_play_rate` |
| `get_asset_by_object_path(SoftObjectPath)` | **TypeError** | 用 `get_assets_by_path` + 过滤（见 `UE5-DEBUG-ASSET.md`）|

---

## 九、这次实战用了哪些调试方法

| 方法 | 出处 | 用在哪 |
| --- | --- | --- |
| **读结构体而不读派生 getter** | `UE5-DEBUG-MEMORY.md`（`obj cycles` 要看内容）| 第 2 步 |
| **`-WaitPattern` 已作为失败检测** | `UE5-DEBUG-SCRIPT.md` | 每一步 |
| **按名字搜资产而不是猜路径** | `UE5-DEBUG-ASSET.md` | 找 `AnimSequence` |
| **改完恢复原状** | 项目规则 5「改坏了先还原」| 第 5 步 |
| **控制台 CVar 存在性判据** | `UE5-DEBUG-NET.md` | 未用上 |

**→ 九篇文档里的方法确实在这一个真实问题上串起来了。**

---

## 十、定位过程的耗时与弯路

| 阶段 | 脚本 | 结果 |
| --- | --- | --- |
| 1 | `diag_anim_step1.py` | 一次成功，但 `get_play_rate=0` **误导** |
| 2 | `diag_anim_step2.py` | 一次成功，**找到根因一** |
| 3 | `diag_anim_step3.py` | **失败两次**（bone_name 缺、BoneSpaces 报错）才成功 |
| 4 | 验证 | 一次成功 |

**→ 弯路的形态和以前一样：**API 签名不熟，试错**。
但这次每次失败都**只改一处**，没有乱试。**
