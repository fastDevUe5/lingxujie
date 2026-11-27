# UE5 学习 · 补读（三十七）：Geometry Scripting —— 和上一轮 Level Blueprint 缺口的答案

> **这篇讲用**蓝图**做程序化建模。**
> **实测：Geometry Scripting 的类**在项目里可用**（275 个相关属性）；
> 而上一轮我发现的 Level Blueprint 缺口，答案是**关卡里根本没有 LevelScriptActor**。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、geometry-scripting.md（10.4 KB，12 节）

**全部是**蓝图分步教程**：**
```
Prerequisite Knowledge
Enabling Plugin
Creating a Blueprint Class
Event Setup
Building Geometry
Adding Transformation Widget
Editing with Booleans
Adding Widgets
Bake to Static Mesh Function
Reviewing End Results
On Your Own
```

**核心机制（文档原文提取）：**

| 步骤 | 做什么 |
| --- | --- |
| 1 | 建一个 Blueprint 类 |
| 2 | **设置事件来填充 Dynamic Mesh** |
| 3 | **`Append Box`** 往 DynamicMesh 里加图元 |
| 4 | **`Apply Mesh Boolean`** 做布尔运算 |
| 5 | **`Bake to Static Mesh`** 把 DynamicMesh 烘成静态网格资产 |

**→ 一句话：**Geometry Scripting 是「在蓝图里拼动态网格，再烘成静态资产」。**

**文档开头一句值得记：**
> **「Geometry Scripting provides **Blueprint and Python functions** for creating custom modeling
> tools and workflows.」**

**→ 明确说**有 Python 函数**。**

---

## 二、✅ 实测：Geometry Scripting 在项目里可用

```
DynamicMesh 类可用:              True
GeometryScriptLibrary 可用:      False      ← 这个名字不对
GeometryScript 相关属性:          275        ← 但有一大批
DynamicMesh 相关属性:             23
```

**前几个类名：**
```
FGeometryScriptFitOrientedBoxMethod
GeometryScript3DGridParameters
GeometryScriptAdapt...
```

**→ 类都在，只是不叫 `GeometryScriptLibrary`。**
**→ 275 个相关属性说明这是一个**完整暴露**的子系统。**

**⚠️ 我没继续深挖具体函数名 —— 那是下一轮可以做的事。**
**→ 但「可用」这个结论已经成立。**

---

## 三、🎯 上一轮缺口的答案：**关卡没有 Level Blueprint**

### 3.1 上一轮的疑问

**补读-35 里我写道：**
> **「Level Blueprint 是「每个关卡都有」的，
> 我**没有查过项目关卡的 Level Blueprint 里有什么**。那可能是隐藏逻辑的位置。」**

### 3.2 这一轮的答案

```
World 上 bluePrint/script 相关属性: []
level_script_blueprint 读失败（不是这个属性名）
LevelScriptActor = None          ← 关键
```

**→ 用 `GameplayStatics.get_actor_of_class(world, LevelScriptActor)` 查：**
**→ 返回 `None`。**

**→ **这个关卡没有 LevelScriptActor —— 也就是没有 Level Blueprint 逻辑。****

**→ 结论：**之前担心的「隐藏逻辑藏在 Level Blueprint 里」不成立。**
**→ 关卡的 116 个 actor 就是全部，没有额外的关卡级脚本。**

---

## 四、🎯 顺便拿到关卡的**真实构成**

```
StaticMeshActor      98
PointLight            4
SkeletalMeshActor     4
DirectionalLight      2
SkyLight              ...
```

**→ 116 个 actor 里：**
- **98 个静态网格**（84%）
- **4 个点光源 + 2 个方向光 + 天光**（照明）
- **4 个骨骼网格**（角色/怪物）

**→ 这是一张**静态场景为主**的地图 —— 98/116 是静态网格，没有复杂 actor。**

**→ 这也解释了为什么关卡的「实际工作」只有 0.469 ms（补读-SCENE-04）：图元少。**
**→ 也解释了为什么 5 个蓝图都没被放置：这关不需要蓝图。**

---

## 五、这一篇学到什么

**1. 🎯 Geometry Scripting 的流程是「建 DynamicMesh → Append 图元 → Boolean → Bake to Static Mesh」。**
**→ 它不是运行时建模，是**编辑器建模工具**。**

**2. 🎯 文档明确说它有**Python 函数**，而不只是蓝图节点。**
**✅ 实测：275 个 `GeometryScript*` 属性可用。**

**3. 🔴 上一轮担心的 Level Blueprint **不存在** —— `LevelScriptActor = None`。**
**→ 关卡没有隐藏的关卡级逻辑。**

**4. 🎯 关卡的构成是 98 个静态网格 + 6 个光源 + 4 个骨骼网格。**
**→ 静态为主，没有复杂 actor —— 这解释了它的低 CPU 工作量。**

**5. 🔴 又一次验证：**猜属性名会失败**。**
`level_script_blueprint` 和 `GeometryScriptLibrary` 都不存在。
**→ 正确做法是 `dir()` 枚举，或换一个入口（`get_actor_of_class`）。**

---

## 六、更正

| 之前 | 现在 |
| --- | --- |
| 「Level Blueprint 可能有隐藏逻辑」 | ❌ **没有 LevelScriptActor，不存在** |
| 「Geometry Scripting 是蓝图专属」 | ❌ **文档明说也有 Python 函数** |
| 「`level_script_blueprint` 是属性名」 | ❌ **不存在，要查 LevelScriptActor** |

---

## 七、还没做到

| 项 | 说明 |
| --- | --- |
| **用 Geometry Scripting 建一个 DynamicMesh 实操** | **可以做**（275 个属性可用），值得下一轮做 |
| 找出具体函数名（Append Box / Apply Boolean / Bake）| 没枚举 |
| Geometry Scripting 能否运行时用 | 文档没说，没测 |
| `Bake to Static Mesh` 的产物验证 | 没做 |

**→ 下一轮值得做：**用 Python 建一个 DynamicMesh，加一个 box，烘成静态网格资产。**
**→ 那是**真正的程序化建模实操**，而且项目里类可用。**

---

## 八、状态

```
Docs/UE5-LEARN-READ-GS.md   1 篇（共 47 篇 learn 文档）
补读进度：38 / 57
主关卡 116 actor / 视口复位
```

---

## 九、下一篇 / 下一轮

**两个方向：**
- **继续补读**（还剩 19 篇）：`sequencer-editor.md` / `fbx-static-mesh.md` /
  `collision` 已读 / `landscape` 已读 / `hlod` 已读
- **或做 Geometry Scripting 实操**：建 DynamicMesh → Append Box → Bake

**→ 我倾向做 Geometry Scripting 实操。**
**理由和 Enhanced Input 那次一样：读到了「有这个能力」，
但没实操就等于不懂。而且这次类明确可用。**
