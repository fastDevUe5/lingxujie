# UE5 学习 · 补读（四十九）：补读完成 —— 以及本系列最大的一个发现

> **最后两篇读完了。但更重要的是：读 `python-with-ai-agents.md` 时，
> 我发现 MCP 有 **22 个工具集**，而我整个系列只用了 **3 个**。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、fbx-static-mesh.md（16.1 KB，18 节）

**FBX 导入管线的完整流程：**
```
General Setup / **Pivot Point** / **Triangulation** / **UV Texture Coordinates**
**Creating Normal Maps** / **Materials** / **Collision**
Caveats and Considerations / **Sockets** / **Vertex Colors**
Export Mesh / Import Mesh
**Static Mesh LODs / LOD Setup / Import LODs / Create LODs**
```

**两条可核实的：**

1. **`Combine Meshes` 选项**
> **「separate multiple Static Meshes into multiple assets within the destination package
> **unless specified to combine the meshes by enabling the Combine Meshes option**」**

**→ 默认一个 FBX 里的多个网格**拆成多个资产**，除非勾 Combine Meshes。**

2. **LOD 的本质**
> **「LODs are handled by creating models of varying complexity going from the full-detail
> base mesh to the lowest-detail LOD mesh」**

**→ LOD 是**独立模型**，不是自动简化的（这一点和 Nanite 的自动聚类**完全不同**）。**

---

## 二、python-with-ai-agents.md（8.0 KB，9 节）—— 直接讲 AI agent 怎么写脚本

### 2.1 🎯 最有用的建议（文档原文）

> **「When an AI agent needs to make many edits, such as building a widget tree or creating dozens of
> Material Instances, **prompt it to write and run one Python script instead of making many separate
> tool calls**. Use individual tool calls for **inspection, screenshots, and compile errors**.」**

**→ ✅ 这正是我在做的：多步操作用 Python 脚本，截图用 MCP。
→ 文档**确认这个模式是对的**。**

### 2.2 🔴 但这里提到了我**不知道的工具**

> **「The **`search_symbols`**, **`get_symbol`**, and **`grep_stubs`** tools look up the Python API.
> The toolset's **`read_me`** tool is intended to be called once per conversation.」**

**→ 有三个专门**查 Python API** 的工具！**

**→ 而我整个系列**一直在猜 API 名字**，至少赔了 10 轮：**
```
simulate_physics / get_bone_names / override_material_editor / level_script_blueprint
phys_material_override / GeometryScriptLibrary / num_lat_lines / StaticMeshFactory
WeightedBlendable.material / r.GPUStats.Enabled ...
```

### 2.3 `execute_python` 的三条硬规则

**文档明确列出：**
> **「All imports must be at the top level of the script, and star imports aren't allowed.
> `execute_python` checks the script before it runs and rejects it if it breaks either rule.
> The error names the line.」**
>
> **「The tool returns the value of the script's final expression, the same way an interactive
> Python session does.」**
>
> **「Output from `print` goes to the Output Log under the `LogPython` category,
> **not to the tool result**.」**

**→ 🔴 第三条解释了我这一整个系列的行为：**
**→ 我用 `unreal.log()` 写日志，然后**读日志文件** —— 那正是 `print` 的去处。**
**→ 而 `execute_python` 会**返回脚本最后一个表达式的值**，这个我一直没用。**

---

## 三、🔴🔴 最大的发现：22 个工具集，我用了 3 个

**用 `mcp.ps1 -Top "list_toolsets"` 列出实际可用的工具集：**

### 3.1 我一直在用的（3 个）

```
EditorToolset.EditorAppToolset       ← CaptureViewport
lingxujie_tools.level_ops.LingXuJieTools  ← reset_view
（加上 RebuildInEditor.ps1 的**控制台打字**）
```

### 3.2 我**完全没用过**的（19 个）

| 工具集 | 本来可以解决什么 |
| --- | --- |
| **`editor_toolset.toolsets.object.ObjectTools`** | **「discover available classes and subclasses」—— 这就是 API 发现工具！** |
| **`editor_toolset.toolsets.blueprint.BlueprintTools`** | **UMG 那块**（我卡在 WidgetTree 不可访问）|
| `editor_toolset.toolsets.material.MaterialTools` | 材质创建 |
| `editor_toolset.toolsets.material_instance.MaterialInstanceTools` | 材质实例 |
| `editor_toolset.toolsets.static_mesh.StaticMeshTools` | 静态网格 |
| `editor_toolset.toolsets.skeletal_mesh.SkeletalMeshTools` | 骨骼网格（含骨骼层级与 socket）|
| `editor_toolset.toolsets.texture.TextureTools` | 贴图 |
| `editor_toolset.toolsets.data_table.DataTableTools` | 数据表（补读-33 说「项目刻意不用」）|
| `editor_toolset.toolsets.curve_table.CurveTableTools` | 曲线表 |
| `editor_toolset.toolsets.data_asset.DataAssetTools` | 数据资产 |
| `editor_toolset.toolsets.string_table.StringTableTools` | 字符串表 |
| `editor_toolset.toolsets.actor.ActorTools` | **actor 父子关系与组件** |
| `editor_toolset.toolsets.scene.SceneTools` | **关卡加载/摆放/相机/大纲组织**（含 `merge_actors`！）|
| `editor_toolset.toolsets.primitive.PrimitiveTools` | 给 actor 加图元组件 |
| **`editor_toolset.toolsets.programmatic.ProgrammaticToolset`** | **沙箱 Python 编排多个工具** |
| **`EditorToolset.LogsToolset`** | **读日志**（我一直在读文件！）|
| **`AutomationTestToolset.AutomationTestToolset`** | **跑项目的 15 条自动化测试** |
| **`SlateInspectorToolset.SlateInspectorToolset`** | **UI 自动化**（能点编辑器按钮）|
| `ToolsetRegistry.AgentSkillToolset` | 技能管理 |

---

## 四、🔴 这意味着什么

**我这一整个系列的**工作方式**是：**
```
写 Python 文件 → RebuildInEditor.ps1（激活编辑器 + 点控制台 + 粘贴 + 回车）
→ 读日志文件 → MCP CaptureViewport 截图
```

**而项目**本来提供了**：**
```
programmatic.ProgrammaticToolset  → 沙箱 Python 编排，不需要控制台！
object.ObjectTools                → 查 API，不需要猜！
material.MaterialTools            → 材质专用工具
blueprint.BlueprintTools          → 蓝图专用工具
LogsToolset                       → 读日志，不需要读文件
AutomationTestToolset             → 跑测试
```

**→ 我用最原始的方式做了 78 轮，而手边有一套完整的工具集。**

**→ 这和补读-43 的判据升级是同一个形状：**
**「有没有这个能力」和「我有没有用对入口」是两件事。**

---

## 五、这一篇学到什么

**1. 🔴 MCP 有 **22 个工具集**，我只用了 **3 个**。**
**→ 用 `mcp.ps1 -Top "list_toolsets"` 才能列出来。**

**2. 🔴 有 **`ObjectTools`** 可以「discover available classes and subclasses」——
**这就是我一直在找的 API 发现工具。****

**3. 🔴 有 **`ProgrammaticToolset`**（沙箱 Python 编排）—— 不需要控制台打字。**

**4. 🔴 有 **`LogsToolset`** 读日志、**`AutomationTestToolset`** 跑测试、
**`BlueprintTools`** 处理蓝图 —— 我全都绕开了。**

**5. 🎯 `execute_python` 会返回**最后一个表达式的值**，而 `print` 走 Output Log。
**→ 我一直用 `unreal.log` + 读文件，**没用返回值**。**

**6. 🎯 FBX 的 LOD 是**独立模型**，Nanite 是**自动聚类** —— 两条完全不同的路。**

---

## 六、更正

| 之前 | 现在 |
| --- | --- |
| 「MCP 只有截图和能力有限的自定义工具」 | ❌ **22 个工具集，覆盖材质/蓝图/网格/贴图/数据/测试/日志/UI** |
| 「猜 API 名字是没办法的事」 | ❌ **有 `ObjectTools` 可以查** |
| 「控制台打字是唯一跑脚本的方式」 | ❌ **有 `ProgrammaticToolset`** |

---

## 七、状态

```
Docs/UE5-LEARN-READ-FINAL.md   1 篇（共 53 篇 learn 文档）
补读进度：57 / 57  ✅ 全部完成
主关卡 116 actor / 视口复位
```

---

## 八、补读完成的账

**69 篇本地文档，实际读了 57 篇相关页（其余是重复索引）。**
**产出：53 篇 learn 文档。**

**但最后这一页的发现**比前面 52 页加起来更重要**：
**→ 我用了 78 轮最原始的工作方式，而项目提供了 22 个工具集。**

**→ 这不是「学会了什么」，是「一直用错了入口」。**
