# UE5 学习 · 补读（五）：天空大气 —— 散射参数实测

> **这一篇边读边调：把文档里 Rayleigh / Mie 的描述变成了**四组实测数据 + 两张图**。**
> **结果**反直觉但符合物理**：把 Rayleigh 调高，日落反而更红。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、文档结构（27.6 KB，27 节）

```
Sky Atmosphere Component / Enabling / Adjusting Atmospheric Directional Lights
Sky Atmosphere Model
  Rayleigh Scattering     ← 小粒子（空气分子），依赖波长
  Mie Scattering          ← 大粒子（尘埃/花粉/污染），产生雾霾 + 太阳光晕
  Mie Phase
  Atmospheric Absorption
  Altitude Distribution
Artistic Direction / Aerial Perspective Scale
Exponential Height Fog    ← 重要：Mie 本身就是高度雾模拟
Sky Rendering Options / Skydome Mesh / Customized Sky Material
Time of Day Example Level / Planetary Atmospheres
Moving the Atmosphere / Atmosphere Transmittance
Moving from Ground to Outer Space
Sunlight Shafts / Volumetric Cloud Shadow Quality
Visualization and Debugging
```

---

## 二、🎯 文档两条关键论断

### 2.1 Rayleigh（小粒子）

> **「Rayleigh scattering is highly dependent on the light wavelength.
> In the Earth's sky, blue scatters more...
> **However, at sunset, it appears red because light rays need to travel further in the atmosphere.
> After long distances, all blue light is scattered away before other colors**,
> resulting in colorful sunsets full of yellow, orange, and red colors.」**

**→ 日落时太阳低 → 光路长 → 蓝光先被散射掉 → 只剩黄橙红。**

### 2.2 Mie（大粒子）

> **「Incident light that follows the Mie scattering theory usually **absorbs** light,
> causing the clarity of the sky to appear **hazy by occluding light**.
> Light also usually scatters more forward, resulting in **bright halos around the light's source**」**
> **「Increasing or decreasing the aerosol density causes more or less clarity in the sky」**

**→ 尘埃越多 → 天空越朦胧 → 太阳周围有光晕。**

### 2.3 🔴 Mie 本身就是高度雾

> **「Mie scattering is a component of the atmosphere and is a height fog simulation in itself,
> meaning you can already use it to create height fog in your scene
> **without using the Exponential Height Fog component**」**

**→ 我的练习场景里**两套雾都在**（SkyAtmosphere + ExponentialHeightFog）—— 功能重叠。**

**文档说两者要联动需要：**
1. 项目设置开 **Support Sky Atmosphere Affecting Height Fog**
2. 把 **Fog Inscattering Color** 和 **Directional Inscattering Color** 设为**黑**

**→ 「Contribution from height fog is **additive**」**

---

## 三、✅ 本项目场景的活值

```
sky=1  fog=1

SkyAtmosphere:
  rayleigh_scattering_scale   0.0331      ← 地球默认
  mie_scattering_scale        0.003996    ← 地球默认
  mie_anisotropy              0.80        ← 地球默认

ExponentialHeightFog:
  fog_density                 0.02        ← 我自己设的

读不到的字段（get_editor_property 抛异常）：
  fog_inscattering_color / directional_inscattering_color
  absorption_scale / aerial_perspective_view_distance_scale
```

**→ 三个散射参数全是**地球默认值**，项目没调过。**

---

## 四、🎯 实测：四组散射配置

**用同一个相机（俯仰 +8°，能看到地平线以上），只改两个参数：**

| 模式 | Rayleigh | Mie | 意图 |
| --- | --- | --- | --- |
| **default** | 0.0331 | 0.003996 | 地球默认 |
| **hazy** | 0.0331 | **0.05**（×12.5）| 重度雾霾 |
| **blue** | **0.15**（×4.5）| 0.003996 | 加厚大气 |
| **clean** | 0.0331 | **0.0005**（×0.125）| 清透空气 |

### 4.1 天空区（画面上 35%）平均颜色（✅）

```
default   天空区平均 RGB: (170.6, 145.9, 153.8)
hazy      Mie ×12.5    : (164.9, 151.5, 164.7)
blue      Rayleigh ×4.5: (194.0, 154.4, 139.8)
clean     Mie ×0.125   : (179.1, 153.0, 159.6)
```

**解读：**

| 模式 | 变化 | 说明 |
| --- | --- | --- |
| **hazy** | R 170.6→**164.9**，B 153.8→**164.7** | **变灰蓝** —— 尘埃遮蔽了暖色 |
| **blue** | R 170.6→**194.0**，B 153.8→**139.8** | **更红** —— 见下 |
| **clean** | 整体略亮 | 空气清透，颜色更饱和 |

### 4.2 🔴 反直觉但正确：「blue」模式让日落更红

**把 Rayleigh 提高 4.5 倍，天空的 R 从 170.6 涨到 194.0，B 从 153.8 降到 139.8 —— **更红了**。**

**→ 这正是文档说的：**
> **「at sunset, it appears red because light rays need to travel further in the atmosphere.
> After long distances, **all blue light is scattered away before other colors**」**

**→ Rayleigh 是**波长相关**的散射：**蓝光被散射掉的速率远高于红光**。
→ 大气越厚（Rayleigh 越高）→ 蓝光被散掉得越多 → **剩下的光越红**。**

**→ 所以这个参数在**白天**调高会让天空更蓝，在**日落**调高会让天空更红。
→ **同一参数，两种效果，取决于太阳高度角。**

---

## 五、画面证据

![Rayleigh ×4.5（更红）](</C:\Users\tk\Desktop\lingxujie\Saved\shot_sky_blue.png>)

![Mie ×12.5（雾霾）](</C:\Users\tk\Desktop\lingxujie\Saved\shot_sky_hazy.png>)

**对比可见：**
- **Rayleigh 高**：暖色调更强，云层轮廓清晰，天空有层次
- **Mie 高**：天空发白发灰，**色彩被冲淡**，地平线亮，云层轮廓变模糊

**→ 「haze by occluding light」这句话在画面上是**可以直接看出来的**。**

---

## 六、这一篇学到什么

**1. 🎯 Rayleigh 和 Mie 的作用完全不同。**
- **Rayleigh**：波长相关，决定**天空颜色**（蓝/红取决于光路长度）
- **Mie**：波长无关，决定**清晰度/雾霾**，并有**前向散射光晕**

**2. 🔴 同一个参数在白天和日落效果相反。**
Rayleigh 调高：白天更蓝，日落更红。**→ 调参必须指定太阳高度角。**

**3. 🔴 Mie 本身就是高度雾。**
有 SkyAtmosphere 就**不一定需要** ExponentialHeightFog。
**→ 我的场景里两套都在，是功能重叠。**

**4. 两者联动需要项目设置 + 把雾的两个颜色设为黑。**

**5. 三个散射参数项目全用默认值**（0.0331 / 0.003996 / 0.8），没调过。

---

## 七、更正

| 之前 | 现在 |
| --- | --- |
| 「天空是引擎默认，没什么可调的」 | ❌ **三个散射参数都能调，且效果明确可测** |
| 「场景要有天空 + 高度雾」 | ⚠️ **SkyAtmosphere 自带高度雾，两套是重复的** |

---

## 八、还没做到

| 项 | 说明 |
| --- | --- |
| 验证「两者联动」的完整设置 | `Support Sky Atmosphere Affecting Height Fog` 在 `RendererSettings` 里，**Python 没有这个类** |
| 雾颜色设为黑的效果 | 字段读不到，没试 |
| `Aerial Perspective View Distance Scale` | 字段读不到 |
| 太阳高度角扫描（真正的 time-of-day） | 只试了 4 个固定太阳位置 |

**→ 下一步可以做**太阳高度角扫描**：把 DirectionalLight 从 -5° 扫到 -60°，拍一组，
看日落从红到蓝的全过程。那是真正理解 Rayleigh 的方式。**

---

## 九、状态

```
Docs/UE5-LEARN-READ-SKY.md   1 篇（共 28 篇 learn 文档）
补读进度：5 / 57
编辑器已还原：Rayleigh 0.0331 / Mie 0.003996 / 主关卡 116 actor / 视口复位
```
