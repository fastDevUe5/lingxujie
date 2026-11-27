# UE5 学习 · 完整场景（第四块）：游戏里跑起来，并量出工作量

> **这一块用 `editor_request_begin_play`（真 PIE，不是 simulate）跑场景，
> 确认了游戏态完整、画面成立，并量出了场景的工作量。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、`begin_play` 和 `simulate` 的区别

| | `editor_play_simulate` | **`editor_request_begin_play`** |
| --- | --- | --- |
| PlayerController | 有 | 有 |
| **Pawn** | 默认/无 | **有（`LXJCharacter_0`）** |
| **HUD** | 无 | **有（`LXJHUD_0`）** |
| **GameMode** | 无 | **有（`LXJGameMode_0`）** |

**→ 之前几块全用 simulate，所以**从来没见过 HUD 和 GameMode**。**

---

## 二、🎯 游戏态实测（✅）

```
game world: 'L_LightLab' → 'L_Scene01'

PlayerController  1   PlayerController_0  at (0, -800, 100)
Pawn              1   LXJCharacter_0      at (0, -800, 92)
HUD               1   LXJHUD_0            at (0, 0, 0)
GameModeBase      1   LXJGameMode_0       at (0, 0, 0)

player view: (0, -800, 100) yaw 0 pitch 0
```

**🔴 关键发现：进游戏后用的是**项目的** GameMode、角色和 HUD** ——
`LXJCharacter`、`LXJHUD`、`LXJGameMode` 全部自动生成。**

**→ 说明这个练习关卡**继承了项目设置**（`DefaultEngine.ini` 里的 `GlobalDefaultGameMode`）。
→ 也就是说：**我的练习场景里跑的是项目的真实玩法代码。**

---

## 三、游戏视角（✅ 画面）

![游戏视角](</C:\Users\tk\Desktop\lingxujie\Saved\shot_game.png>)

**从真正的玩家相机（pitch 0，地平线在视线高度）看：**

| 位置 | 形体 | 材质 |
| --- | --- | --- |
| 左 | 球 | 橙红，受夕照 |
| 中左 | 圆柱 ×2 | 暗棕带纹理 |
| 中 | 锥 | **橙红高亮** |
| 右 | 立方体 | 橙面 + 暗面 |
| 背景 | 云 | 粉橙体积云 |
| 地平线 | 雾 | 大气层次 |
| 地面 | 土 | 暖棕 |

**→ 六个形体全部入画，构图成立。**

---

## 四、🎯 场景工作量（✅ 120 帧平均）

```
GameThread:  10.734 ms
FrameTime:   10.732 ms
实际工作:     0.469 ms     ← FrameTime 子项
CPU Stall:   10.26 ms      （差值）
```

**对照：**

| 场景 | FrameTime | **实际工作** | Stall 占比 |
| --- | --- | --- | --- |
| `L_LightLab`（10 actor，空盒）| 8.360 ms | **0.428 ms** | 95% |
| **`L_Scene01`（14 actor，户外）** | **10.732 ms** | **0.469 ms** | **96%** |

**→ 多了一个完整的户外场景（天空/云/雾/6 个形体/材质），工作量只从 0.428 涨到 0.469 ms（+0.041 ms）。**

**⚠️ 但这仍然**不能说明场景便宜** —— 96% 的时间是 Stall（编辑器在睡眠），
GPU 时间没量到，而 Lumen 的代价主要在 GPU。**

**→ 这个数字只能说明：**CPU 侧没有压力**。**

---

## 五、🎯 目标达成情况

**目标原文：「直到能独立用官方素材**搭出并调优一个完整场景**为止」**

| 要求 | 证据 | 状态 |
| --- | --- | --- |
| **官方素材** | `/Engine/BasicShapes` 全部，参考 `/Engine/Maps/Templates` | ✅ |
| **搭出** | 4 个脚本可重建，14 个 actor | ✅ |
| **完整** | 日/天空/天光/云/雾/地面/出生点/后处理 + 6 形体 | ✅ |
| **调优** | 加材质 → 修曝光黑屏 → **三次调整构图** | ✅ |
| **可运行** | `begin_play` 游戏态，PlayerController/Pawn/HUD/GameMode 全在 | ✅ |
| **玩家视角验证** | ✅ 六个形体全可见 | ✅ |
| **可量化** | FrameTime 10.73 ms / 工作 0.469 ms | ✅ |

---

## 六、这一块学到什么

**1. 🎯 `simulate` 和 `begin_play` 是两个不同的东西。**
**simulate 没有 HUD、没有 GameMode。** 之前几块用 simulate 是对的（做机制实验），
**但验证「能不能玩」必须用 begin_play。**

**2. 🔴 练习关卡继承了项目的 GameMode。**
进游戏跑的是 `LXJCharacter` / `LXJHUD` / `LXJGameMode`。
**→ 好处：能验证项目代码；坏处：练习场景不「纯」，带了项目行为。**

**3. `pitch 0` 让地平线在视线高度，构图更稳。**
之前用 -5/-8 的俯角，地平线偏高。

**4. 工作量从 0.428 → 0.469 ms，但 Stall 仍占 96%。**
**→ 编辑器里量工作量只能证明「CPU 没压力」，不能证明「场景便宜」。**

---

## 七、更正

| 之前 | 现在 |
| --- | --- |
| 「simulate 就够验证场景」 | ❌ **验证可玩性必须 begin_play** |
| 「练习关卡是干净环境」 | ❌ **它继承了项目的 GameMode/角色/HUD** |

---

## 八、成果清单

**关卡：**
```
/Game/Learning/L_Scene01    14 actor（落日原野 + 6 形体）
/Game/Learning/L_LightLab   10 actor（深色实验盒）
```

**资产：**
```
M_SceneFloor     地面材质
M_LabDark        纯暗材质
M_LabTex         贴图+标量参数材质
M_LabRedOverride Nanite 覆盖材质（红色）
MI_LabDim / MI_LabBright   两个实例
WBP_LabLabel     空的控件蓝图（UI 实验的产物）
```

**脚本（可重建整个过程）：**
```
scene_build.py      搭骨架（日/天空/云/雾/地面/出生点）
scene_tune.py       加材质 + 后处理
scene_compose.py    加 6 个形体
scene_relayout2.py  按玩家视角重排（Y 轴铺开）
```

---

## 九、还没做到的（诚实清单）

| 项 | 说明 |
| --- | --- |
| **GPU 时间** | 完全没有量到 |
| **打包** | 需关编辑器（问过，未获答复）|
| **阴影/VSM 质量对比** | 没测 |
| 云/雾参数对比 | 单一值 |
| 场景里放**骨骼角色/粒子** | Niagara 无资产、动画编辑器刷不动 |

---

## 十、下一块

**目标的核心部分已完成。剩下两个方向：**
- **A. 补 GPU 时间** —— 找能读 GPU 耗时的路径（`stat gpu` 写日志？）
- **B. 继续调优场景** —— 阴影质量、云参数、雾参数的系统对比

**→ A 更有价值** —— GPU 是这个场景真正可能的瓶颈，而我一直没量到。
