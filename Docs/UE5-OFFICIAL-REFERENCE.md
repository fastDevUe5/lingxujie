# UE5 官方能力与本地实测对照（2026-11-26）

> **这份文档的目的：把"官方怎么说"和"我们这台机器上实际是什么"对齐。**
> 只收录本项目真正依赖的东西，每条都注明出处（引擎源码路径 / 官方文档链接 / 实测日志）。
>
> **不写泛泛而谈的 UE5 教程** —— 查得到的不抄，抄了也会过期。
> 这里写的是：**我们能用什么、怎么用、哪里踩过坑。**

---

## 一、环境事实（引擎源码核实）

| 项 | 值 | 出处 |
| --- | --- | --- |
| 引擎 | UE **5.8.4**，`C:\Program Files\Epic Games\UE_5.8` | 工程 `.uproject` |
| MCP 插件 | `Engine\Plugins\Experimental\ModelContextProtocol` | 目录存在 |
| 工具集注册模块 | `Engine\Plugins\Experimental\ToolsetRegistry\Content\Python\toolset_registry` | 目录存在 |
| 工具集基类 | `ToolsetRegistry\Source\ToolsetRegistry\Public\...\ToolsetDefinition.h` | 头文件存在 |
| Python 插件 | 已启用（`unreal` 模块可用） | 实测可用 |

**结论：5.8.4 具备**自定义 MCP 工具集**的全部能力，不需要升级到 5.9。**

---

## 二、MCP 工具集现状（2026-11-26 实测，**22 个**）

**⚠️ 早前写"只有 5 个"是错的。** 那 5 个是**还没触发 Python 工具集加载前**的列表。
注册了自己的工具集之后，`list_toolsets` 变成 **22 个**。

### 2.1 C++ 内置（5 个）

| 工具集 | 用途 |
| --- | --- |
| `EditorToolset.EditorAppToolset` | 控制台变量、资产成像、Actor/资产选择、**视口相机**、内容浏览器、PIE |
| `EditorToolset.LogsToolset` | 读引擎日志、控制日志详细度 |
| `SlateInspectorToolset.SlateInspectorToolset` | Playwright 风格的 Slate UI 自动化 |
| `AutomationTestToolset.AutomationTestToolset` | 自动化测试发现与执行 |
| `ToolsetRegistry.AgentSkillToolset` | 列出 / 读取 / 创建 agent 技能 |

### 2.2 Python 工具集（16 个，**之前完全不知道**）

| 工具集 | 用途 |
| --- | --- |
| `editor_toolset.toolsets.actor.ActorTools` | 查看与修改 actor |
| `editor_toolset.toolsets.asset.AssetTools` | 资产与磁盘文件 |
| `editor_toolset.toolsets.blueprint.BlueprintTools` | 蓝图 |
| `editor_toolset.toolsets.scene.SceneTools` | **当前关卡的场景操作** |
| `editor_toolset.toolsets.object.ObjectTools` | 对象属性读写 |
| `editor_toolset.toolsets.material.MaterialTools` | **材质与材质函数** |
| `editor_toolset.toolsets.material_instance.MaterialInstanceTools` | 材质实例 |
| `editor_toolset.toolsets.static_mesh.StaticMeshTools` | 静态网格 |
| **`editor_toolset.toolsets.skeletal_mesh.SkeletalMeshTools`** | **骨骼网格** ← 动画要用 |
| `editor_toolset.toolsets.texture.TextureTools` | 贴图 |
| `editor_toolset.toolsets.data_table.DataTableTools` | 数据表 |
| `editor_toolset.toolsets.data_asset.DataAssetTools` | 数据资产 |
| `editor_toolset.toolsets.curve_table.CurveTableTools` | 曲线表 |
| `editor_toolset.toolsets.string_table.StringTableTools` | 字符串表 |
| `editor_toolset.toolsets.primitive.PrimitiveTools` | 加基础几何组件 |
| `editor_toolset.toolsets.programmatic.ProgrammaticToolset` | **编排其他工具**（见下） |

**`ProgrammaticToolset` 不是通用 Python 执行**，官方描述原文：
> "Batches calls to other registered tools through a small sandboxed Python script that glues
> them together with custom logic. The script's purpose is tool orchestration, not general
> Python execution."

**但它仍有用**：能把多个工具串成一次调用，减少往返。

### 2.3 我们自己的（1 个）

| 工具集 | 工具 |
| --- | --- |
| **`lingxujie_tools.level_ops.LingXuJieTools`** | `rebuild_level` / `reset_view` / `get_view` / `list_actors` / `read_log` |

**实测通过：**
```
get_view    → "8950, -6200, 3900 yaw -4 pitch -8"
list_actors → ["MX_CHARACTER (LXJCharacter)", "MX_LZ_101_10_SOONGSAN_DOOR (StaticMeshActor)", ...]
reset_view  → "camera at 8950, -6200, 3900 yaw 0 pitch -2"
```

### ⚠️ 5.8.4 仍然没有 `PythonScriptingTools`

**官方 5.9 文档描述的 `execute_python` / `search_symbols` / `get_symbol` / `grep_stubs` / `read_me`
这套工具，5.8.4 没有。** 实测 `ExecutePythonScript` 返回 `Unknown tool`。

**替代方案见第三节 —— 自己写工具集，这条路已验证可行。**

---

## 三、自定义 MCP 工具集（**已验证可用**，5.8.4）

> **2026-11-26 实测：`lingxujie_tools` 注册成功，四个工具都能调用。**
> **下面所有约定都是踩过坑之后的实际写法，不是照抄文档。**

### 3.1 与 5.9 文档的**三处差异**（照抄会失败）

| 5.9 文档写的 | 5.8.4 实际 |
| --- | --- |
| `@toolset_registry.tool_call(mode=unreal.ToolAccessMode.WRITE)` | ❌ **没有 `ToolAccessMode`**，`tool_call` 是**裸装饰器**，不接受 `mode` |
| `-> list` | ❌ 报 `Type <class 'list'>: missing specification for contained type`，**必须写 `list[str]`** |
| `@staticmethod` + docstring | ✅ 一致 |

**报错原文（留着对照）：**
```
module 'unreal' has no attribute 'ToolAccessMode'
Type <class 'list'>: missing specification for contained type
```

### 3.2 最小可用骨架（已跑通）

```python
import unreal
import toolset_registry


@unreal.uclass()
class LingXuJieTools(unreal.ToolsetDefinition):
    """LingXuJie 工程的编辑器操作工具集。

    用于重建关卡、复位视口相机、抓取编辑器窗口。
    涉及地图/关卡的操作都应该走这里，不要靠敲控制台。
    """

    @toolset_registry.tool_call
    @staticmethod
    def rebuild_level() -> str:
        """重建兰州城关卡。

        Returns:
            完成信息，含 actor 数量。
        """
        # 真实实现应当：StopPIE -> 调 build_moxiang_map.build() -> reset_view
        subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        count = len(subsystem.get_all_level_actors())
        return "actors=%d" % count
```

### 关键约定（官方文档原文要点）

| 项 | 要求 |
| --- | --- |
| **类** | `@unreal.uclass()` + 继承 `unreal.ToolsetDefinition` |
| **类 docstring** | 会变成工具集描述，写成"AI 什么时候该用这个工具集" |
| **工具方法** | `@toolset_registry.tool_call(mode=...)` + `@staticmethod`，两者缺一不可 |
| **访问模式** | `ToolAccessMode.READ` / `WRITE` / `EXECUTE` |
| **类型标注** | 决定 JSON schema：`list[T]`→`Array(T)`，`dict[str,V]`→`Map(str,V)`，`T \| None`→可选参数 |
| **docstring** | Google 风格（`Args:` / `Returns:`），会进 schema |
| **错误** | **抛异常**，不要返回错误字符串 |
| **长任务** | 可以是 `async def` |

### 注册方式

```python
# <插件>/Content/Python/<包>/__init__.py
from toolset_registry.registration import Registration
from my_toolset import ops

_registration = Registration([ops.LingXuJieTools])
```

```python
# <插件>/init_unreal.py
from my_toolset import _registration
_registration.register()
```

**改完之后：重新加载模块 + 执行控制台命令 `ModelContextProtocol.RefreshTools`，
已连接的客户端可能要重连。**

### 对本项目的价值（为什么值得做）

| 现在的做法 | 问题 | 改成工具集后 |
| --- | --- | --- |
| `RebuildInEditor.ps1` 往控制台**敲键盘** | 窗口被挡 / 模态框 / 焦点丢失就失败 | 直接调用，无 UI 依赖 |
| 用 MCP `CaptureViewport` 以为改了相机 | **它不改相机**（gotcha #65） | 工具里调 `SetLevelViewportCameraInfo` |
| 重建前忘了 `StopPIE` | `new_level -> False`（gotcha #67） | 工具内部自己检查 |
| 每一步都要 powershell 拼 JSON | 易错、难读 | 一次调用 |

---

## 四、视口相机：权威 API（引擎源码核实）

**出处：**
`Engine\Source\Editor\UnrealEd\Public\Subsystems\UnrealEditorSubsystem.h`
（`UUnrealEditorSubsystem`，`UNREALED_API`）

```cpp
bool GetLevelViewportCameraInfo(FVector& CameraLocation, FRotator& CameraRotation);
void SetLevelViewportCameraInfo(FVector CameraLocation, FRotator CameraRotation);
UWorld* GetEditorWorld();
UWorld* GetGameWorld();
bool ScreenToWorld(const FVector2D& ScreenPosition, FVector& WorldPosition, FVector& WorldDirection);
bool WorldToScreen(const FVector& WorldPosition, FVector2D& ScreenPosition);
bool GetLevelViewportSize(FIntPoint& Size);
```

**Python 侧（实测可用）：**

```python
subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
subsystem.set_level_viewport_camera_info(location, rotation)
current_location, current_rotation = subsystem.get_level_viewport_camera_info()
```

**🔴 核心区别（踩过两次）：**

| 调用 | 改不改编辑器视口 | 用途 |
| --- | --- | --- |
| `EditorAppToolset.CaptureViewport(captureTransform=...)` | **❌ 不改** | 只拍一张指定视角的图 |
| `UnrealEditorSubsystem.set_level_viewport_camera_info(...)` | **✅ 改** | 真的把相机移过去 |

**要给人看就得用后者。验证用 `Tools/grab_editor_window.py`（抓真窗口）。**

---

## 五、Python 脚本执行：三条路

### 5.1 编辑器底部的控制台有三种模式，但它们都不解决抢焦点

**编辑器状态栏那个输入框可以切：`Cmd` / `Python` / `Python (REPL)`。**

| 模式 | 能干什么 | 适合什么 |
| --- | --- | --- |
| **Cmd** | `py "脚本.py"`、引擎控制台命令 | 跑脚本文件 |
| **Python** | 直接跑一行 Python | 一行小操作 |
| **Python (REPL)** | 交互式，能 `dir()`、试 `get_editor_property` | **探 API 最方便** |

**🔴 关键结论：换模式**不解决抢焦点问题**。**
焦点问题来自"自动化脚本要先点击那个输入框才能敲字"，
**跟选哪个模式无关** —— 三个都一样。

**而且这会假死**：人在操作别的窗口时，`RebuildInEditor.ps1` 的 `py` 命令
**完全不执行，日志里连 `Cmd:` 行都没有**，看起来像"脚本坏了"，其实是焦点被抢。
**2026-11-26 被这个误导过一次，以为是控制台失效。**

### 5.2 按可靠性排序的四条路

| 路 | 需要焦点 | 可靠性 | 状态 |
| --- | --- | --- | --- |
| **① MCP 内置工具** | ❌ 不需要 | ✅ **高** | **已跑通**（`SetCameraTransform` / `GetCameraTransform` / `StartPIE` / `CaptureViewport`） |
| **② 自定义 MCP 工具集** | ❌ 不需要 | ✅ **高** | 代码已写（`Content/Python/lingxujie_tools/`），**待重启注册** |
| ③ 控制台敲 `py` | ✅ 需要 | ⚠️ 中 | 现在是这条，最脆弱 |
| ④ 5.9 的 `execute_python` | — | — | 本机没有 |

**日常操作应尽量走 ① 和 ②。控制台只作"人在场时"的探路工具。**

**`Python (REPL)` 的不可替代之处：** 想知道某个对象有什么方法、某个属性怎么设，
在那里敲一句 `dir(obj)` 比查文档快得多。**用完记得清空，别留半截状态。**

---

## 六、日志：别开窗口，用 MCP

```powershell
'{"category":"","pattern":"LingXuJie","maxEntries":20}' | Set-Content Saved\mcp_args.json -Encoding ASCII
powershell -ExecutionPolicy Bypass -File Tools\mcp.ps1 `
    -Toolset "EditorToolset.LogsToolset" -Tool "GetLogEntries" `
    -ArgsFile "Saved\mcp_args.json" -OutFile "Saved\mcp_log.txt"
```

**读回来用 `Tools/show_log.py`（避开 PowerShell 的引号/编码问题）。**

**开「输出日志」窗口没好处**：会挡视口、打断自动化点击。

---

## 七、`SlateInspectorToolset` —— 被严重低估的一个

**这是 5.8.4 自带的能力，我们几乎没用过。**

官方描述：Playwright 风格的 Slate UI 自动化，**公开快照、屏幕截图和交互工具，
用于以编程方式驱动虚幻编辑器 UI**。浅根观察者（深度 0）持续追踪顶层窗口；
用某个面板前先 `Observe()` 拿深度控件树，用完 `Unobserve()`。

**对本项目的用途：**

| 场景 | 现在 | 用 Slate Inspector |
| --- | --- | --- |
| 点掉模态框 | `EditorGuard -Action dismiss`（坐标硬编码） | 按控件名点，不怕窗口位移 |
| 切换视口模式 | 无 | 可以 |
| 读面板文字 | 无 | 可以 |

**下一轮如果模态框又捣乱，优先考虑用这个，而不是加坐标。**

---

## 八、Agent 技能（官方机制，我们用的是 Markdown）

**官方文档说两种写法都支持：**
- **C++ 或 Markdown 文件** → 走 `AgentSkillToolset`
- **Python 类** → `@agent_skill` + `unreal.AgentSkill` + `instructions` 属性

**我们现在的 `AGENTS.md` / `Docs/*.md` 就是 Markdown 形态，是对路的。**
不需要改成 Python 类，除非要让技能**带参数执行动作**。

---

## 九、查 API 的正确顺序

**遇到"这个函数到底签名是什么"，按这个顺序查，别猜：**

| 顺序 | 查哪 | 为什么 |
| --- | --- | --- |
| **1** | **本机引擎源码 `Engine\Source` / `Engine\Plugins`** | **最权威**，就是编译这份二进制的那份代码 |
| 2 | 官方 Python API 文档 `dev.epicgames.com/documentation/.../python-api/` | 有 Python 名字与签名 |
| 3 | 官方手册页 | 讲概念与用法 |
| 4 | 实测（打日志把 `dir(obj)` 打出来） | 前三个都没有时 |

**Python 侧确认某个子系统有什么方法：**
```python
import unreal
sub = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
unreal.log("\n".join(sorted(dir(sub))))
```

---

## 十、官方文档索引（本项目相关）

| 主题 | 链接 |
| --- | --- |
| Python 脚本总览 | https://dev.epicgames.com/documentation/unreal-engine/scripting-the-unreal-editor-using-python |
| Python 与 AI agent（工具集/skill） | https://dev.epicgames.com/documentation/unreal-engine/using-python-with-ai-agents-in-unreal-engine |
| Unreal MCP | https://dev.epicgames.com/documentation/unreal-engine/unreal-mcp-in-unreal-editor |
| Python API：UnrealEditorSubsystem | https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/UnrealEditorSubsystem |
| Python API 总目录 | https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/ |

---

## 十一、和 `UE5-Gotchas.md` 的关系

- **本文档**：能力地图 + API 出处 + 架构选择（"有什么、该用什么"）
- **`UE5-Gotchas.md`（68 条）**：具体坑的症状/根因/修法（"哪里会炸、怎么炸"）

**两个都读。这份告诉你有什么，那份告诉你哪里不能踩。**
