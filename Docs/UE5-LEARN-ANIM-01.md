# UE5 学习 · 动画系统（第一块）：API 摸清了，但姿态在编辑器里刷不动

> **这一块把动画系统能用 Python 碰到的部分全部摸了一遍，结论有一半是「不行」。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、官方文档说了什么

**`Docs/UEManual/state-machines.md`（12 KB，11 节）：**

| 概念 | 要点 |
| --- | --- |
| **State Machine** | 建在动画蓝图的 Anim Graph 里，接 Output Pose |
| **Entry Point** | 每个状态机都有入口，决定默认状态 |
| **States** | 状态内部有自己的 Anim Graph 层，产出该状态的最终姿态 |
| **Transitions** | 状态间的转移，带规则 |
| **Conduit** | **一对多 / 多对一 / 多对多的共享转移逻辑**；要当入口状态需开 `Allow Conduit Entry States` |
| **State Alias** | 把多个状态当一组来转移 |
| **`Always Reset on Entry`** | 状态属性：进入时把状态内所有动画**重新初始化**。不勾的话重入状态会接着上次的播放位置 |

**→ 这条 `Always Reset on Entry` 是经典坑：不勾，重入状态动画不会从头播。**

**⚠️ 但这些都属于**动画蓝图**，需要 UI 建图。Python 侧没有 `AnimBlueprintFactory`（只有 `BlueprintFactory` / `MaterialFactoryNew`）。**

---

## 二、Python 侧能碰到什么（✅ 实测）

**`AnimSingleNodeInstance` 的完整接口：**
```
play_anim(is_looping, play_rate, start_position)
set_animation_asset(asset, is_looping, play_rate)
set_playing(is_playing)
set_position(position, fire_notifies=True)
set_position_with_previous_time(position, previous_time, fire_notifies=True)
set_play_rate / set_looping / set_reverse / stop_anim
get_length() / get_animation_asset()
```

**`SkeletalMeshComponent` 的动画接口：**
```
set_animation(new_anim_to_play)
play_animation(new_anim_to_play, looping)
set_animation_mode(mode, force_init_anim_script_instance=True)
set_play_rate / set_position
get_anim_instance() / get_animation_mode()
set_anim_instance_class(new_class)
```

**→ 单节点动画完全可控。**

---

## 三、🔴 但姿态刷不动 —— 三层原因

### 3.1 骨架和动画是匹配的

```
mesh skeleton: 'sash-tails-mesh_Skeleton'
anim skeleton: 'sash-tails-mesh_Skeleton'
same skeleton: True
```

**→ 不是配错骨架的问题。**

### 3.2 动画也真的绑上了

```
instance asset after set_animation: 'stone-guardian-beast-663ee9_Anim'
instance length: 4.00 s
```

**→ 不是没绑上的问题。**

### 3.3 但四个时间点骨骼位置完全一样

```
leaf 'sash-tails-mesh': t=0    -> (675.99, -50.66, 226.58)
leaf 'sash-tails-mesh': t=half -> (675.99, -50.66, 226.58)
moved: False
```

**→ `set_position` 只写了值，**没有触发一次动画求值**。**

---

## 四、缺的那一环：编辑器不 tick 动画

**`SkeletalMeshComponent` 有个属性：**
```
update_animation_in_editor (bool): [Read-Write]
  If true, this will Tick until disabled
```

**默认 **False**。→ 编辑器里生成的骨骼角色**不 tick 动画**。**

**→ 没有 tick，写进去的 position 永远不会被求值成姿态。**

### 但改不了

```
Exception: SkeletalMeshComponent: Property 'bUpdateAnimationInEditor'
for attribute 'update_animation_in_editor' on 'SkeletalMeshComponent'
cannot be edited on templates
```

**→ 这个属性是给 **Details 面板**上用的，**Python 改不了**。**

---

## 五、🔴 所以正确的做法是什么

| 方法 | 能刷新姿态吗 | 依据 |
| --- | --- | --- |
| `AnimSingleNodeInstance.set_position()` | ❌ 编辑器里不行 | 本轮实测 |
| `component.set_editor_property("update_animation_in_editor", True)` | ❌ Python 改不了 | 本轮实测（模板限制）|
| **编辑器属性路径**（`animation_data.saved_position`）| ✅ **可以** | 项目之前验证过（案例 001）|
| **PIE 里跑** | ✅ | 有 tick |

**→ 编辑器里要验证动画，用**编辑器属性路径**（`animation_data` 结构体），不要用实例 API。**

**→ 实例 API 只在 **PIE / 运行时**有效。**

**⚠️ 这和我之前记录的一条结论吻合：**
> 「`set_position` 不触发求值」—— 但当时我以为原因是「没赋动画」。

**现在的完整解释是：**两个原因都有** —— 既要有动画，也要有 tick。**

---

## 六、顺带学到的一个 API（项目里早就有）

**我花了几轮找「怎么列出骨骼名」，试了：**
```
mesh.get_bone_names()        ❌ 不存在
skeleton.get_bone_names()    ❌ 不存在
skeleton.reference_skeleton  ❌ 不存在
mesh.get_num_bones()         ❌ 不存在
```

**正确的：**
```
component.get_num_bones()        → 33
component.get_bone_name(index)   → 'AuxScene' / 'jujube-tree' / ...
```

**→ **`Tools/diagnose.py` 第 89-90 行一直在用这个。**
→ 我没有先读项目自己的工具，白花了几轮。**

**🔴 这是又一次「不先查已有的东西就自己造」。**

---

## 七、🔴 另一个重大发现：Python API 镜像只有 110/190 可用

**查 `AnimationBlueprintLibrary.txt` 时发现它是 **404 页面**：**
```
404Page not foundThe page you were looking for was not found.
```

**审计全部 190 篇（✅ 实测）：**

```
文件 190
  可用    110  （58%）
  404      25
  可疑     55（多为「太小」）
```

**404 的例子：`AnimationBlueprintLibrary`、`AnimationEditorSubsystem`、`AssetManager`、
`EditorEngine`、`ReferenceSkeleton`、`MeshDescription`、`KismetMathLibrary`、`ToolAccessMode`…**

**→ 我之前说「Python API 190 篇都在」是**错的**。**
**→ 一条 `grep "404"` 就能查出来，我一直没查。**

**⚠️ 这批 404 的原因可能是：这些名字在文档站用 `struct/` 或 `enum/` 路径而不是 `class/`。
需要单独查，本轮没做。**

---

## 八、这一块学到什么

**1. 单节点动画的 API 完整可用，但**在编辑器里刷不出姿态**。**
需要 tick，而 tick 开关 Python 改不了。

**2. 编辑器里验证动画要用**编辑器属性**（`animation_data.saved_position`），不是实例 API。**

**3. 官方文档的动画部分（状态机、Conduit、`Always Reset on Entry`）全部需要**动画蓝图**，
而 Python 建不了动画蓝图 → 这部分**只能 UI 学**，本轮只做了阅读归档。**

**4. 🔴 又犯了「不先查已有工具」：`get_bone_name(index)` 项目里一直在用。**

**5. 🔴 镜像质量没验过：190 篇里 80 篇不可用。**

---

## 九、下一块

**动画这块再深挖需要 UI（动画蓝图），Python 到顶了。**

**两个选择：**
- **A. 补镜像的 80 篇**（能修，但要查清 404 的正确路径）
- **B. 转**物理**（目标里的下一项）—— Python 对物理的可控性更好（加约束、施力、读速度）**

**→ 我倾向 B，因为 A 是工具维护不是学 UE。但 A 影响后面每一次查 API，可以考虑先修。**
