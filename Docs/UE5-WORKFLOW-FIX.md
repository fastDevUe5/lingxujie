# UE5 · 工作方式修正：用 ProgrammaticToolset 取代控制台打字

> **这是本系列最后、也是**最实用**的一份文档。**
> **它替换掉了我用了 80 轮的「激活编辑器 → 点控制台 → 粘贴 → 读日志文件」流程。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、为什么要换

**旧流程（我用了 80 轮）：**
```
写 .py 文件 → RebuildInEditor.ps1（激活编辑器 + 点控制台 + 粘贴 + 回车）
→ 读日志文件（Saved/Logs/LingXuJie.log）→ 解析 [LingXuJie] 行
```

**问题：**
- 每次都要**抢焦点**、**点控制台**
- 会被**模态框挡住**
- 结果要**从日志文件里捞**
- 编辑器 UI 在脚本运行期间**阻塞**
- 超过约 **120 秒**会超时（补读-31）

**新流程：**
```
一次 MCP 调用 execute_tool_script → 脚本里串多个工具 → run() 返回值直接出现在结果里
```

**→ 不抢焦点、不读日志文件、结果结构化。**

---

## 二、✅ 已验证的完整配方

### 2.1 两个必要的元工具

```powershell
# 1) 列所有工具集（22 个）
powershell -File Tools\mcp.ps1 -Top "list_toolsets"

# 2) 看某个工具集的工具名 + 输入 schema
'{"toolset_name":"lingxujie_tools.level_ops.LingXuJieTools"}' | Set-Content Saved\a.json
powershell -File Tools\mcp.ps1 -Top "describe_toolset" -ArgsFile Saved\a.json
```

**⚠️ 是 `describe_toolset`（单数），不是 `describe_toolsets`。**

### 2.2 ProgrammaticToolset 的两个工具

| 工具 | 参数 |
| --- | --- |
| **`get_execution_environment`** | 无（**每个会话必须先调一次**）|
| **`execute_tool_script`** | `script`（字符串）|

**`get_execution_environment` 返回的 `instructions` 里写着关键规则：**
```
execute_tool(tool_name, json_input)   ← 调任意已注册工具，返回 dict-like
脚本必须定义 run() 返回 Dict[str, Any]
可用模块: math / datetime / json / time / copy / re
```

### 2.3 实测通过的脚本

```python
import json

def list_actors(prefix):
    return execute_tool(
        "lingxujie_tools.level_ops.LingXuJieTools.list_actors",
        json.dumps({"prefix": prefix}))["returnValue"]

def read_log(pattern, n):
    return execute_tool(
        "lingxujie_tools.level_ops.LingXuJieTools.read_log",
        json.dumps({"pattern": pattern, "max_entries": n}))["returnValue"]

def run():
    all_actors = list_actors("")
    sounds = [a for a in all_actors if "AmbientSound" in a]
    lights = [a for a in all_actors if "Light" in a]
    return {
        "total": len(all_actors),
        "sound_actors": sounds,
        "light_count": len(lights),
    }
```

**调用方式：**
```powershell
$payload = @{ script = $script } | ConvertTo-Json -Compress
$payload | Set-Content Saved\script_args.json -Encoding ASCII
powershell -File Tools\mcp.ps1 `
    -Toolset "editor_toolset.toolsets.programmatic.ProgrammaticToolset" `
    -Tool "execute_tool_script" `
    -ArgsFile "Saved\script_args.json" -OutFile "Saved\out.txt"
```

**✅ 实测结果：**
```json
{"total": 116, "sound_actors": ["MX_AMBIENT_MUSIC (AmbientSound)"], "light_count": 7}
```

**→ 三个数据点，一次调用，**不需要读日志文件**。**

---

## 三、关键细节（踩过的）

| # | 细节 |
| --- | --- |
| 1 | **`describe_toolset` 是单数** —— `describe_toolsets` 会报 `Tool 'describe_toolsets' not found` |
| 2 | **必须先调 `get_execution_environment`** —— 否则不知道 `execute_tool` 的用法 |
| 3 | **`run()` 必须返回 dict** —— 不返回就没有结果 |
| 4 | **结果被双重 JSON 编码** —— 外层是 MCP 的 `{"returnValue": "..."}`，内层是 `run()` 的 dict |
| 5 | **`list_actors` 的 prefix 匹配的是 `标签`**，标签格式是 `MX_xxx (ClassName)` —— 用 `"SM_"` 匹配不到 |
| 6 | **工具名要写全** —— `lingxujie_tools.level_ops.LingXuJieTools.list_actors` |
| 7 | **空参数调用会打印完整 schema** —— 这是查参数名的正规途径（不需要猜） |

---

## 四、这件事的意义

**我 80 轮里至少 10 轮耗在「猜 API 名字」上：**
```
simulate_physics / get_bone_names / override_material_editor
level_script_blueprint / phys_material_override / GeometryScriptLibrary
num_lat_lines / StaticMeshFactory / WeightedBlendable.material / r.GPUStats.Enabled
```

**→ 而**空参数调用工具会打印完整 JSON schema** —— 参数名不用猜。**

**→ 这条规则**在 MCP 层**，比 Python 的 `dir()` 更直接。**

---

## 五、更正

| 之前 | 现在 |
| --- | --- |
| 「控制台打字是跑脚本的主要方式」 | ❌ **`execute_tool_script` 更快、不抢焦点、结果结构化** |
| 「结果要从日志文件里捞」 | ❌ **`run()` 的返回值直接回来** |
| 「**音频完全没播放**」 | ⚠️ **有一个 `AmbientSound`（`MX_AMBIENT_MUSIC`）会自动播放** |

---

## 六、状态

```
Docs/UE5-WORKFLOW-FIX.md   1 篇（工作方式文档）
主关卡 116 actor / 视口复位 / 提交已记录
```

---

## 七、下一步

**工具修好了（第 1 步完成）。按原计划：**

**第 2 步：补 4 个已诊断未实施的修复**
1. 动画接线
2. NOT_SOLID 法线
3. IBM 转置+缩放
4. 101 个 Nanite 网格的材质槽

**→ 现在可以用 `execute_tool_script` 一次跑完「改 + 验」，不用再走控制台。**

---

## 八、实测第二版：一次调用跑完「查材质槽 + 赋材质 + 两张截图」（2026-11-27）

**对象：`MX_BOSS001_STATIC`**（案例 004 里唯一真的没有材质的 actor）。
**结果：一次 `execute_tool_script` 调用，7.1 秒，返回 3.94 MB，里面是两张 1.4 MB 的 PNG + 全部槽位读数。**

### 8.1 这一次调用里串了 12 个工具

```
get_current_level → find_actors → get_label → get_components
→ list_properties(组件)              ← 先拿真实属性名，别猜
→ get_properties(overrideMaterials)  ← 组件这一层
→ get_material_slots / get_material  ← 资产这一层
→ CaptureViewport  (before)
→ set_properties(overrideMaterials)  ← 赋材质
→ get_properties(overrideMaterials)  ← 回读
→ save_assets(关卡)
→ CaptureViewport  (after)           ← 同一个机位
```

**脚本原文留在 `Saved/one_call_boss2.py`**（Saved 不入库，格式照抄即可）。

### 8.2 数据

| 项 | 值 |
| --- | --- |
| 一次调用耗时 | **7.1 s**（两次截图占大部分） |
| 返回体积 | **3.94 MB**（base64 PNG ×2） |
| 组件 override 前 | `WorldGridMaterial` ← **不是空的，是显式设成 WorldGrid** |
| 组件 override 后 | `M_Boss_Mob01` |
| 关卡保存 | `level_saved: true`，保存后 `is_dirty: false` |
| 两帧像素差 | **9.50%**（>8 阈值），**地面那一行 0.00%**，差异集中在角色身上 |

### 8.3 四条新踩的坑（已进 Gotchas #116–#119）

1. **资产槽赋了没用** —— 组件 `overrideMaterials` 里有一条显式 `WorldGridMaterial`，它优先。
   第一次调用把资产槽从 WorldGrid 改成 `M_Boss_Mob01`（回读确认改动生效），截图**两帧几乎一样**。
2. **沙箱里 `try/except` 抓不住工具报错** —— 任何一次工具调用失败都会终止整个脚本、只回错误文本，
   连已经拍好的图也一起丢。所以每一步的参数都必须合法：**属性名先 `list_properties` 问，不要猜。**
3. **`CaptureViewport` 必须显式传 `annotations`** —— 六个字段全填；`gridSpacing: 0` + `maxLabelDistance: 0`
   把网格线和标签关掉，`classFilter: null` 可以接受。不传会报
   `input param "annotations" needs a default value`。
4. **`SetCameraTransform` 真的会移动编辑器相机** —— 实测 (8950,-6200,4600)/pitch -25 → 还原到默认机位，
   两次 `GetCameraTransform` 都读得回来。**规则 3b 的复位现在可以直接走 MCP**，
   不必再 `RebuildInEditor` + `reset_view.py`（那条路仍是兜底）。

### 8.4 更正

| 之前 | 现在 |
| --- | --- |
| 「组件也没 override」（案例 004） | ⚠️ **组件有一条显式 `WorldGridMaterial` 的 override**，所以资产槽改不动画面 |
| 「查材质槽 = 查资产槽」 | ❌ **要查两层**：资产 `get_material_slots`/`get_material` + 组件 `overrideMaterials` |
| 「复位只能靠 `reset_view.py`」 | ⚠️ MCP `SetCameraTransform` 也行，且不抢焦点 |

### 8.5 产物

```
Saved/one_call_boss2.py       一次调用的完整脚本
Saved/boss2_before.png        改前（同一机位）
Saved/boss2_after.png         改后
Saved/boss2_compare.png       上下拼接的对照图
Saved/one_call_raw2.json      原始返回（3.9 MB，含两张图的 base64）
```

