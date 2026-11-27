# UE5 学习 · 补读（四十七）：收口剩下的索引页 + 水体

> **这一篇把剩下的 9 篇一次读完。**
> **其中 8 篇是**索引页**（列主题、链到别处），只有 `water-bodies` 和
> `import-static-meshes` 有实质内容。**
> **→ 水体系统**没启用**；材质实例那部分我**已经实操过**。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、water-bodies.md（27.6 KB，23 节）—— 唯一的实质水体文档

**五种水体 actor：**

| 类型 | 说明 |
| --- | --- |
| **Ocean** | 无限海洋 |
| **Lake** | 湖泊（封闭水域）|
| **River** | 河流（沿 spline）|
| **Custom** | 自定义形状 |
| **Island** | 岛屿（排除水域）|

**设置分组：**
```
Water Body Properties / Selected Points
River Spline Visualization and Manipulation
Water / Terrain / Curve Settings / Water Heightmap Settings
Blend Mode / Falloff Settings
Effects / Blurring / Curl Noise / Wave
Rendering / Underwater Post Process Settings
Water Body Exclusion Volume
```

**→ 这是一个**完整的水体系统**：形状（5 种）+ 水面（波/卷曲噪声）+ 水下后处理。**

### 1.1 🔴 但水系统是**可选插件**

**`water.md` 原文：**
> **「The Water system is a selection...」**（Water 插件是选择性启用的）

**✅ 实测：**
```
uproject 插件: ['PythonScriptPlugin', 'EditorScriptingUtilities', 'ModelContextProtocol',
                'ToolsetRegistry', 'EditorToolset', 'AutomationTestToolset',
                'SlateInspectorToolset', 'ProceduralVegetationEditor']
含 Water: []                     ← 没有
引擎里存在: Water.uplugin         ← 引擎里有，但项目没启用
```

**→ **项目没启用 Water 插件 → 水体系统完全不可用 → 这一篇对项目是纯理论的。****

---

## 二、instanced-materials.md（9.7 KB，12 节）—— 我已经实操过

**这不是纯索引，有两条实质内容：**

### 2.1 命名约定（文档明确推荐）

> **「The prefix `M_` denotes a parent Material, as in `M_Chair`.
> The prefix `MI_` denotes a Material instance, as in the two examples pictured right.」**

**→ ✅ 我这一系列**完全遵守了**：`M_LabDark` / `M_LabTex` / `M_SceneFloor`（父）、
`MI_LabDim` / `MI_LabBright`（实例）。**

### 2.2 🎯 参数化的必要性（文档原话）

> **「It is important to know that you **cannot edit every single characteristic of a Material instance
> by default**. To make Material attributes editable within an instance,
> **you must designate them as parameters in the parent Material**. This is called **parameterizing**
> your Material.」**

**→ 这正是我在 MAT-02 做的事：**
```
M_LabTex（父）里放了 ScalarParameter "Brightness"
MI_LabDim  → Brightness = 0.02
MI_LabBright → Brightness = 0.9
```

**→ 两个实例共用一张贴图，只改一个参数值 —— 这就是 parameterizing 的完整用法。**

**→ 而且这解释了补读-MAT-03 里那个「改了参数返回 False 但值生效了」的坑：
参数只有在**父材质里声明过**才能实例化改。**

### 2.3 文档还给了层级概念的依据

> **「A Material instance inherits all of its attributes from the parent (or master) Material.」**

**→ 「Hierarchical Material relationships help you alter the appearance of a Material
without recompiling the Material」**（文档首句大意）
**→ 这解释了为什么改 MI 参数**不需要重编译**，而改父材质**需要**。**

---

## 三、其余 7 篇：确认是索引页

| 文档 | 大小 | 节数 | 性质 |
| --- | --- | --- | --- |
| `light-types.md` | 5.5 KB | 5 | **索引**（光照类型与 mobility 的总览）|
| `lighting-environment.md` | 4.2 KB | 7 | **索引**（光照特性/要点分组）|
| `niagara.md` | 3.2 KB | 5 | **索引**（入门/教程/特性分组）|
| `niagara-modules.md` | 2.5 KB | 4 | **索引**（模块参考的入口，含 Selection Stack / 执行状态管理）|
| `water.md` | 2.6 KB | 6 | **索引**（Water 插件说明）|
| `chaos-destruction.md` | **0.6 KB** | **1** | **纯占位**（只有一句「去哪找学习资源」）|
| `sound-cue-editor.md` | 3.7 KB | 6 | **索引**（Sound Wave / Sound Cue 简介）|

**→ 7 篇里 6 篇是索引，1 篇（`chaos-destruction`）是**纯占位**（0.6 KB，只有一句话）。**

**→ 这些页的价值是**导航**，不是内容。读它们等于确认「这个主题有独立文档，但这里只有目录」。**

---

## 四、import-static-meshes.md（5.0 KB，6 节）—— 一篇实用流程

```
Set Up / Exporting
Importing
...
```

**→ 讲**从建模软件导出再导入**的流程（FBX 相关）。
**→ 项目已经导入了 610 个静态网格，所以这个流程**已经被跑过很多次**了
（虽然是别人跑的，不是我）。**

---

## 五、🎯 这一篇最值得记的两件事

### 5.1 索引页的辨识

**→ 本系列多次因为「数链接行数」把索引页误判成正文（补读早期）。**
**→ 现在有了更简单的判据：**看章节数 + 看是否有 `## Overview` 这种「总览」标题 + 看字数。**
**→ 0.6 KB 的 `chaos-destruction` 是纯占位；2.5 KB 的 `niagara-modules` 是纯索引；
27.6 KB 的 `water-bodies` 是真正文。**

### 5.2 材质实例这件事我做对了

**→ `instanced-materials.md` 讲的「parameterizing」，我在 MAT-02 完整做过：
父材质里声明 ScalarParameter，两个实例只改那个值。**
**→ 而且这解释了 MAT-03 那个坑（parameter 必须先在父材质里声明）。**

---

## 六、这一篇学到什么

**1. 🎯 五种水体：Ocean / Lake / River / Custom / Island。**
**但**Water 是可选插件，项目没启用** → 完全不可用。**

**2. 🎯 `M_` = 父材质，`MI_` = 实例**（文档推荐的命名约定，我一直在用）。

**3. 🎯 「不能改实例的每个属性，必须先在父材质里**参数化**」**
**→ 这正是我 MAT-02 做的，也解释了 MAT-03 的坑。**

**4. 🎯 剩下 7 篇里 6 篇是索引、1 篇是 0.6 KB 纯占位。**

**5. 🎯 判断「索引页 vs 正文」的实用判据：字数 + 章节数 + 有无总览标题。**

---

## 七、更正

| 之前 | 现在 |
| --- | --- |
| 「水体是引擎自带功能」 | ❌ **是可选插件，项目没启用** |
| 「实例材质就是改参数」 | ✅ **准确说：父材质必须先声明参数，否则改不了** |

---

## 八、状态

```
Docs/UE5-LEARN-READ-MISC.md   1 篇（共 52 篇 learn 文档）
补读进度：55 / 57（一次收口 9 篇）
主关卡 116 actor / 视口复位
```

---

## 九、补读还剩 2 篇

```
fbx-static-mesh.md (16.1 KB)      ← 实质内容
python-with-ai-agents.md (8.0 KB) ← 实质内容
```

**→ 下一轮读完最后两篇，补读就全部完成。**
