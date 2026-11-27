# UE5 学习 · Niagara（第一块）：系统能跑，但看不见

> **这一块的结果是「一半成功」：粒子**确实在模拟（40 个存活），但**截不到画面**。
> 而且这条路上撞到了一个硬限制：**这个项目里一个 Niagara 资产都没有。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、官方文档说了什么

**`Docs/UEManual/niagara-overview.md`（14.6 KB，24 节，**是真文章不是索引页**）：**

| 概念 | 要点 |
| --- | --- |
| **四个核心组件** | **Systems**（容器）/ **Emitters**（产生粒子）/ **Modules**（构建块）/ **Parameters**（数据抽象）|
| **工作流** | 先建 System → 加 Emitter → 在 Emitter 里加 Module |
| **Asset Browser** | 建系统时弹出，按类别/标签筛选，可自定义分类 |
| **Paradigms** | **Inheritance**（继承）/ **Dynamic Inputs**（动态输入）/ **Micro Expressions**（微表达式）/ **Events**（事件）/ **Data Interfaces** / **Houdini** |
| **可选阶段** | CPU 还是 GPU 模拟（Emitter 属性）|

**⚠️ 这些全部围绕**Niagara 编辑器**（UI）—— 而下面会看到，Python 侧建不了 Niagara 系统。**

---

## 二、🔴 硬限制：项目里**没有任何 Niagara 资产**

**实测（扫描 `/Engine` 和 `/Game` 全库，✅）：**

```
/Engine niagara assets: {}
/Game   niagara assets: {}
```

**→ **引擎自带内容和项目里都没有一个 Niagara 系统或发射器。****

**→ 想练 Niagara，必须**新建**一个 —— 而这就撞上第二条限制。**

---

## 三、🔴 第二条限制：Python **没有** Niagara 系统工厂

**运行时 Niagara API 是存在的（498 个 `unreal` 属性带 niagara/effect）：**

```
has NiagaraFunctionLibrary: True
has NiagaraSystem:          True
has NiagaraComponent:       True
has NiagaraActor:           True
```

**但工厂只有这 4 个：**
```
NiagaraDynamicInputScriptFactory
NiagaraFunctionScriptFactory
NiagaraModuleScriptFactory
NiagaraParameterDefinitionsFactory
```

**→ **没有 `NiagaraSystemFactory`，也没有 `NiagaraEmitterFactory`。****
**→ **无法从 Python 新建 Niagara 系统或发射器。****
**→ 也没有 `NiagaraEditorSubsystem` / `NiagaraSystemEditorSubsystem`。**

---

## 四、退而求其次：用遗留的 Cascade

**扫描发现 **2 个** 遗留 Cascade 粒子系统：**

```
/Engine/Functions/Engine_MaterialFunctions02/ExampleContent/3dParticleOpacity_Particle
/Engine/Tutorial/SubEditors/TutorialAssets/TutorialParticleSystem   ← 用这个
```

**放置成功（✅）：**

```python
actor = spawn_actor_from_class(unreal.Emitter, (0, 0, 150), rot)
component = actor.get_component_by_class(unreal.ParticleSystemComponent)
component.set_editor_property("template", tutorialSystem)
```

```
particle component template: 'TutorialParticleSystem'
```

---

## 五、🎯 粒子**确实在模拟** —— 这是本块的实质成果

**在 game world 里读粒子组件（✅）：**

```
template: 'TutorialParticleSystem'
is_active: True
get_num_active_particles: 40
--- activate 之后 ---
is_active now: True
active particles now: 39      ← 数量变了，说明真的在跑
```

**→ **40 个粒子存活，且两次读数不同（40 → 39）—— 模拟是活的。****

**→ 这一条**结论是硬的**：Cascade 粒子系统在 PIE 里正常模拟。**

---

## 六、🔴 但**截不到画面**

**试了 6 次不同机位/设置，全部失败：**

| 尝试 | 结果 | 猜测原因 |
| --- | --- | --- |
| 1 | 全黑 | 相机在密闭房间**外面** |
| 2 | 全白 | **朝向错**（yaw 90 = +Y，但粒子在 +X）|
| 3 | 全白 | 朝向修正后仍是白 —— 灯太亮（5000）|
| 4 | 全黑 | 关灯了 —— **受光材质在黑暗里看不见** |
| 5 | 过曝白 | 灯 300，房间白墙 + 相机贴墙 70 cm |
| 6 | 过曝白 | 关掉自动曝光（`r.EyeAdaptationQuality 0`）**仍然白** |

**→ 最终判断：**问题是练习关卡本身是个"白盒子"** ——**
**白色 `BasicShapeMaterial` + 密闭小房间 + 相机贴墙，任何东西都会被白墙淹没。**

**→ 40 个小粒子在 4.2 米外、白底上 —— 对比度不够。**

---

## 七、这一块学到什么

**1. 🔴 Niagara **不能**用 Python 建。** 没有系统工厂。要建只能 UI。

**2. 🔴 项目里**零** Niagara 资产。** `/Engine` 和 `/Game` 都是空的。
**→ 「用官方素材练 Niagara」这条在本机**做不到** —— 官方内容没带 Niagara。**

**3. 遗留 Cascade 还能用。** 2 个引擎自带粒子系统可放置、可模拟。

**4. 🎯 判据：`get_num_active_particles()` 能证明粒子在跑。**
不需要看见画面 —— **两次读数不同就说明模拟活着**（40 → 39）。

**5. 🔴 练习关卡的设计有缺陷：白盒子不适合做视觉实验。**
**应该用深色材质做房间**，或者至少一面墙不用白色。

**6. 相机朝向反复搞错（第 3 次）。**
**方位规则要背下来：`yaw 0 = +X` / `90 = +Y` / `180 = -X` / `270 = -Y`。**

---

## 八、更正

| 之前 | 现在 |
| --- | --- |
| 「用官方素材可以练任何域」 | ❌ **Niagara 不行** —— 官方内容没有 Niagara 资产 |
| 「练习关卡够用了」 | ❌ **白盒子不适合视觉实验**，要深色 |

---

## 九、要做真正 Niagara 实操，需要什么

| 条件 | 现状 |
| --- | --- |
| 一个 Niagara 系统资产 | ❌ 没有，且 Python 建不了 |
| 或者下载官方 Niagara 示例 | ❌ 没做（Fab 上可能有免费 VFX 包）|
| 深色练习房间 | ❌ 现在是白的 |

**→ 下次可以考虑：从 Fab 下载免费 Niagara 特效包（官方免费素材），再放到深色房间里。**

---

## 十、下一块

**材质**（目标里的下一项）—— **这一块 Python 可控性最好**
（`MaterialEditingLibrary` 能建材质、连节点），而且不依赖白盒子问题。

**⚠️ 练习关卡已恢复（粒子已删、灯回 5000、10 个 actor），主关卡已重开。**
