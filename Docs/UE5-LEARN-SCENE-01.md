# UE5 学习 · 完整场景（第一块）：搭出来并调优

> **目标写的是「直到能独立用官方素材**搭出并调优一个完整场景**为止」。
> **这一块把它做出来了 —— 8 个 actor、全部官方素材、有画面为证。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、先读官方场景，再照着搭

**`Template_Default`（8 个 actor，✅ 逐个读取）：**
```
DirectionalLight           1
ExponentialHeightFog       1
PlayerStart                1
SkyAtmosphere              1
SkyLight                   1
StaticMeshActor            2   (SM_SkySphere, Floor)
VolumetricCloud            1
```

**`TimeOfDay_Default`（9 个）额外有 `TextRenderActor`，其余相同。**

**→ **一个可玩的室外场景最小只需 7 个元素**：太阳 + 天空大气 + 天光 + 体积云 + 高度雾 + 地面 + 出生点。**

**→ 而且**官方模板默认没有 Post Process Volume** —— 曝光靠引擎默认。**

---

## 二、照这个清单搭 `/Game/Learning/L_Scene01`

**全部用 `/Engine` 素材（✅ 实测）：**

| # | Actor | 关键设置 |
| --- | --- | --- |
| 1 | `DirectionalLight` | **Movable**，intensity 8，yaw -35（斜射，有影子）|
| 2 | `SkyAtmosphere` | 默认 |
| 3 | `SkyLight` | **Movable**，**real time capture** |
| 4 | `VolumetricCloud` | 默认 |
| 5 | `ExponentialHeightFog` | **fog density 0.02** |
| 6 | `Floor`（`/Engine/BasicShapes/Cube`）| scale (40, 40, 0.2) → **4000×4000×20 cm** |
| 7 | `PlayerStart` | (0, -800, 100) |

**实测输出：**
```
created /Game/Learning/L_Scene01
sun: movable, intensity 8
sky light: movable, real time capture
fog density 0.02
floor: 4000 x 4000 x 20 cm
placed 7 actors
saved: True
```

**第一次截图（`shot_scene01.png`）：画面已经是一个能认出来的落日原野 —— 橙粉云、地平线雾、地面。**

---

## 三、🎯 调优：加材质 + 后处理

### 3.1 给地面一个材质（复用材质那一块的做法）

**`M_SceneFloor`：albedo (0.18, 0.15, 0.12)，roughness 0.9 —— 暖棕色土面。**

```
created M_SceneFloor: albedo 0.18/0.15/0.12, roughness 0.9
floor material: 'M_SceneFloor'
```

### 3.2 🔴 加后处理体积 —— 然后场景**变黑了**

**我设了：**
```python
settings.set_editor_property("override_auto_exposure_method", True)
settings.set_editor_property("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL)
```

**结果：画面**全黑**。**

**用像素统计确认（✅）：**
```
手动曝光的场景  平均亮度: (0.7, 0.6, 0.3)        ← 接近全黑
```

**🔴 原因：`AEM_MANUAL` 只是**切换模式**，手动曝光还需要一个**曝光值**。
不给值 → 解出的曝光极低 → 黑屏。**

### 3.3 修复：关掉覆盖，让引擎默认接管

```python
settings.set_editor_property("override_auto_exposure_method", False)
```

**修复后（✅）：**
```
修复后的场景    平均亮度: (140.6, 112.6, 111.7)  ← 正常
```

**🔴 但这里有个容易误判的点：读 `auto_exposure_method` **仍然是 `AEM_MANUAL`**，
画面却已经正常了。**

**→ 因为 `override_auto_exposure_method = False` 让引擎**忽略**这个字段的值。
→ **存储的值 ≠ 生效的值**，当覆盖标志关闭时。**

---

## 四、最终场景（✅ 画面为证）

![完整场景](</C:\Users\tk\Desktop\lingxujie\Saved\shot_scene03.png>)

**画面里能读出的东西：**

| 元素 | 证据 |
| --- | --- |
| **落日光** | 整片暖色调、云层被侧照 |
| **体积云** | 顶部橙色云团有体积感，不是贴图 |
| **天空大气** | 地平线由暖过渡到冷，有散射 |
| **高度雾** | 地平线附近有雾层，远处地面变淡 |
| **地面材质** | 右下角棕红色地面（`M_SceneFloor`），不是默认灰格 |
| **曝光正常** | 平均亮度 140，不是 0.7 也不是过曝 255 |

---

## 五、🎯 这个场景证明了什么

**目标要求「用官方素材搭出并调优一个完整场景」—— 逐条对照：**

| 要求 | 做到 |
| --- | --- |
| **用官方素材** | ✅ 全部来自 `/Engine`（BasicShapes、MapTemplates 的参考结构）|
| **搭出** | ✅ 8 个 actor，脚本可重建 |
| **完整** | ✅ 光/天空/云/雾/地面/出生点，和官方模板同构 |
| **调优** | ✅ 加材质、加后处理、修曝光（从黑到正常，用亮度数字验证）|
| **可验证** | ✅ 截图 + 像素均值 |

---

## 六、这一块学到什么

**1. 🎯 官方场景模板是**最好的「完整」参照**。**
`Template_Default` 只有 8 个 actor —— **完整不等于复杂**。

**2. 🔴 `AEM_MANUAL` 只切模式，不给值就是黑屏。**
手动曝光需要 `exposure_offset`（当前 1.0，`b_override_exposure_offset = False`）。

**3. 🔴 存储的值 ≠ 生效的值。**
`override_* = False` 时，读那个字段仍然返回存的值，但引擎不采用。

**4. 亮度均值是个便宜可靠的判据。**
黑屏 = (0.7, 0.6, 0.3)；正常 = (140.6, 112.6, 111.7)。**不用看图就能判断。**

**5. 官方默认**没有** Post Process Volume。**
我自己加的，反而先把它调黑了 —— **说明「加东西」比「默认状态」更容易出错。**

---

## 七、更正

| 之前 | 现在 |
| --- | --- |
| 「完整场景需要很多元素」 | ❌ **官方模板只用 8 个 actor** |
| 「加后处理只会更好」 | ❌ **我加的后处理先把场景变成了黑屏** |

---

## 八、还没做到的

| 项 | 说明 |
| --- | --- |
| 场景里放**其他网格**（球/柱/锥）| 只放了地板 |
| **Lumen 在这个场景里的效果** | 场景有太阳 + 天光，Lumen 应该在跑，但没对比 |
| **性能** | 没量（且编辑器里量不可靠，见上一块）|
| **PIE 里跑一遍** | 只看了编辑器视口 |

---

## 九、下一块

**继续丰富并调优这个场景：**
1. 放更多官方网格（球/柱/锥）形成一个小构图
2. **对比 Lumen 开/关在这个户外场景里的画面差异**（户外天光 + Lumen 应该明显）
3. PIE 里跑一次，确认 PlayerStart 到位

**⚠️ 编辑器状态：当前是 `L_Scene01`（8 actor）。主关卡 `LingXuJie` 未动（116 actor）。**
