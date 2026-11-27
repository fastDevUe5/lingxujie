# UE5 学习 · Lumen（第二块）：官方文档自相矛盾的一条

> **上一轮我记了一个「待验证的真问题」：**
> **软件光追只支持静态网格/ISM/HISM/地形 → Boss 是骨骼网格 → 收不到反弹光。**
>
> **这一轮验证结果：**我错了，骨骼网格能收到反弹光。****
>
> **而且发现**官方文档自己前后矛盾**。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、文档的两处说法

**`Docs/UEManual/lumen-technical.md` 里有两段互相打架：**

### 说法 A（Surface Cache 一节，第 10 行）

> Surface cache support for skeletal meshes is enabled by default
> (`r.MeshCardRepresentation.SkeletalMesh`). Unlike static meshes, they don't have
> offline generated cards due to their dynamic nature. Instead, **six cards are placed
> around their pre-skinned bounding boxes** when they are added to scenes.

**→ 骨骼网格**有** Surface Cache，6 张 Card。**

### 说法 B（Software Ray Tracing 限制一节，第 31 行）

> Only Static Meshes, Instanced Static Meshes, Hierarchical Instanced Static Meshes,
> and Landscape terrain are represented in the Lumen Scene.

**→ 只说静态网格一类，**没提骨骼网格**。**

**⚠️ 两段在同一篇文档里，相隔 20 行。**

---

## 二、引擎源码怎么判

### 2.1 Cell 表示的入口

**`Runtime/Renderer/Private/Lumen/LumenScene.cpp:1433`：**
```cpp
const FCardRepresentationData* CardRepresentationData =
    PrimitiveSceneInfo->Proxy->GetMeshCardRepresentation();
```

**→ 每个 Lumen 图元都要过这一关。基类返回空就不进 Lumen Scene。**

### 2.2 谁实现了它（✅ 全局搜 `GetMeshCardRepresentation` 只 6 处）

| 文件 | 行 | 说明 |
| --- | --- | --- |
| `PrimitiveSceneProxy.h` | 506 | `{ return nullptr; }` ← **基类** |
| `StaticMeshSceneProxy.h` | 170 | override |
| **`SkeletalMeshSceneProxy.h`** | **45** | **override ← 关键** |
| `NaniteSceneProxy.h` | 553, 844 | override |
| `BaseDynamicMeshSceneProxy.h` | 326 | override |

**→ `FSkeletalMeshSceneProxy` **实现了** `GetMeshCardRepresentation()`。**

### 2.3 CVar 默认值

**`Runtime/Engine/Private/SkeletalMeshSceneProxy.cpp:73-86`：**
```cpp
static TAutoConsoleVariable<int32> CVarMeshCardRepresentationSkeletalMesh(
	TEXT("r.MeshCardRepresentation.SkeletalMesh"),
	1,                                              // ← 默认 1，启用
	TEXT("Whether to allow generating mesh cards for skeletal meshes."),
	FConsoleVariableDelegate::CreateLambda([](IConsoleVariable* InVariable)
		{ FSkinnedMeshComponentRecreateRenderStateContext Context(nullptr); }),
	ECVF_Scalability | ECVF_RenderThreadSafe);

bool AllowLumenCardGenerationForSkeletalMeshes(EShaderPlatform Platform)
{
	return CVarMeshCardRepresentationSkeletalMesh.GetValueOnAnyThread() != 0
		&& DoesPlatformSupportLumenGI(Platform);
}
```

**→ 默认值 **1**（启用），且有个专门的判定函数。**

**→ 说法 A 对，说法 B **不完整/过时**。**

---

## 三、本项目实测（✅）

```
r.MeshCardRepresentation.SkeletalMesh = "1"   LastSetBy: Scalability
r.MeshCardRepresentation              = "1"   LastSetBy: Constructor
```

**→ 本项目也是启用状态。**

**→ 上一轮我担心的「Boss 收不到反弹光」**不成立**。**

---

## 四、🔴 结论更正

| 上一轮的记录 | 现在 |
| --- | --- |
| 「Boss 是骨骼网格，软件光追下**不参与间接光**，会显得暗」 | **错**。`r.MeshCardRepresentation.SkeletalMesh=1`，骨骼网格有 6 张 Card，**参与 Lumen Scene** |
| 「这是本项目的真问题，下一轮验」 | **不是问题。文档的 limitations 列表漏了骨骼网格** |

**更正原因：我只读了文档的「限制」一节，没读到同篇「Surface Cache」一节，也没查源码。**

**→ 教训：**读文档不能只读「限制/不支持」这类负面清单，它们最容易过时。****
**→ 与源码冲突时，源码为准，然后把差异记下来。**

---

## 五、骨骼网格的 Card 有什么不同

**这是文档说法 A 里真正重要的细节：**

| 类型 | Card 怎么来 | 质量 |
| --- | --- | --- |
| 静态网格 | **离线生成**，捕获材质多角度 | 高 |
| **骨骼网格** | **运行时在 pre-skinned 包围盒周围放 6 张** | **有限** |
| 样条网格 | pre-deformed 的 Card 重适配到新包围盒 | 中间 |

**→ 官方原文：**
> "surface cache coverage and quality are fairly limited for skeletal meshes,
> especially during animations that deform the meshes a lot."

**→ 所以骨骼网格**有**反弹光，但**质量有限**，尤其是大幅变形时。**

**→ 这条对项目有实际意义：Boss 大幅挥砍动作时，它的间接光会更不准。**

---

## 六、顺带发现的异常

**量 4 个骨骼角色的包围盒时发现：**

```
MX_BIRD_TEST   SK_Bird       size  606 x  483 x  544    ← 正常
MX_BOBU_TEST   SK_Bobu       size  238 x  258 x  257    ← 正常
MX_BOSSCOWF    SK_BossCowf   size 1849 x 1025 x   11    ← 只有 11 cm 高
MX_BOSS001     SK_Boss001    size  300 x  388 x  265    ← 正常
```

**`MX_BOSSCOWF` 高只有 **11 cm**，另外两轴是 1849 和 1025 cm。**

**→ 这是一个**极度扁平**的形状。要么是网格本身坏了（骨骼塌陷），要么是它本来就躺平在地上。**

**⚠️ 这与之前记录的「`MX_BOSSCOWF` 9.2×5.1×5.5 m」不一致 —— 那次是**米**，这次是**厘米**：
9.2 m ≈ 920 cm，但这里长轴是 1849 cm ≈ 18.5 m。两个数对不上，需要单独查。**

**→ 记下来，后面单独验，不在这块里混。**

---

## 七、这一块学到什么

**1. 官方文档会自相矛盾，尤其是「限制」清单。**
同一篇里 Surface Cache 一节说骨骼网格支持，Limitations 一节说只支持静态网格。

**2. 判据在源码里很明确：`GetMeshCardRepresentation()` 返回非空就进 Lumen Scene。**
全引擎只有 5 个类实现它，`SkeletalMeshSceneProxy` 是其中之一。

**3. 「有」和「好」是两件事。**
骨骼网格有 6 张 Card（有反弹光），但运行时生成、质量有限（不好）。

**4. 我又犯了一次「只读一半」。**
上一轮只读了「限制」一节就下结论，没读同一篇的 Surface Cache 一节。

---

## 八、下一块

**继续 Lumen，验「墙不能薄于 10 cm」这条** —— 量兰州建筑的墙厚，看有没有薄的。

**这条能直接量，而且如果真有问题，会有漏光。**
