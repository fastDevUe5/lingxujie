# UE5 学习 · 补读（三十一）：Unreal MCP —— 三句话解释了我多次「挂住」

> **我用了 60+ 轮的 MCP，从没读过它的文档。**
> **读完发现：我多次「控制台没反应」「任务挂住」的原因，文档里都写着。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、文档结构（31.4 KB，47 节）

```
What Is the Model Context Protocol?
Set Up Unreal MCP / Enable the Plugins / Check Auto-Start
Run Your AI Agent from a Terminal / Generate a Client Config / Launch
Optional: Terminal Plugin / Unreal Assistant Panel / Add Server Instructions
**How Unreal MCP Works**
Toolsets and the Toolset Registry
**Tool Search**
Plugin Modules
**How the Server Runs**
Extend Unreal MCP
**Create Tools with the Toolset Registry**
Write a Toolset in Python / in C++
Tool Metadata / Refresh Tools / Register Tools Directly
Write Agent Skills / Add MCP Resources
Make Tools Available in Cooked Builds
Debug Unreal MCP
**Tips and Best Practices**
  Connect to More Than One Editor
  **Handle Long Tool Calls**
  Restart the Editor from an AI Agent
  Import Assets with Tools
Configuration Reference（Editor Preferences / Project Settings / Console Commands / CVars）
Limitations and Known Issues
```

---

## 二、🔴 三句话，每句都解释了我踩过的坑

### 2.1 「UI becomes blocked」的 MCP 版本

**`## How the Server Runs` 原文：**
> **「The MCP server runs tool calls **one at a time on the game thread**,
> so clients **shouldn't send overlapping tool calls**.」**

**→ 🔴 工具调用跑在**游戏线程**上，而且**一次只能一个**。**

**→ 这解释了：**
- 为什么 MCP 调用也会让编辑器卡顿
- 为什么我在 PIE 里跑 MCP 截图要等
- **为什么脚本超时后再发指令会「排队」而不是失败**

### 2.2 🔴 长脚本超时 —— 文档明确点名

**`## Handle Long Tool Calls` 原文：**
> **「Some clients stop waiting for a call after a timeout (**Claude Code after about 120 seconds**).
> To keep a long call alive, send a **`progressToken` in `_meta`** to get notifications/progress heartbeats.
> To cancel, send `notifications/cancelled`.
> **Split very long work, such as Live Coding builds, large scripts, asset scans, and automation runs,
> into shorter calls.**」**

**→ 🔴 文档点名的四类长任务里，我做过**三类**：**
- **大脚本**（场景搭建、材质构建）
- **资产扫描**（813 张贴图 / 610 个网格）
- **自动化运行**

**→ 而且它说「**split into shorter calls**」—— 正是我后来被迫采用的做法
（把落体实验拆成「放球」+「读高度」两次运行）。**

**→ 换句话说：**我靠试错发现了文档里写着的最佳实践。**

### 2.3 安全边界

**同一个 `## How the Server Runs` 里：**
> **「The plugin runs **inside the editor process**.
> By default, the server only accepts connections from the **same machine**,
> has **no authentication layer**, and isn't designed for remote use.
>
> The server checks each request's **Origin header** against an allow-list:
> **localhost, 127.0.0.1, and [::1]**, plus any origins you add in Editor Preferences.
> This prevents a web page from reaching the server through **DNS rebinding**.
> **Each origin you add widens that exposure.**
> Because there's no authentication, **any local process or any browser page served from an allowed
> origin can call the editor's tools**.」**

**→ 本项目 MCP 在 `127.0.0.1:8000`，符合默认允许列表。**
**→ 没有认证 —— 任何本机进程都能调编辑器工具。**

---

## 三、🎯 Tool Search 机制（解释了我为什么这样调工具）

**`## Tool Search` 原文：**
> **「By default, the plugin runs in tool-search mode (`bEnableToolSearch = true`).
> In this mode, `tools/list` returns **four discovery meta-tools** instead of every tool:」**

| 元工具 | 作用 |
| --- | --- |
| **`list_toolsets`** | 列出可用的工具集 |
| **`describe_toolsets`** | 列出某工具集的工具（带 schema 选项）|
| **`describe_tools`** | 给出特定工具的完整 schema（`Toolset.Tool` 格式）|
| **`call_tool`** | 调用工具集里的工具 |

**→ 这就是为什么我的 `Tools/mcp.ps1` 是这样调的：**
```
mcp.ps1 -Toolset "EditorToolset.EditorAppToolset" -Tool "CaptureViewport"
→ 内部走 call_tool，参数是 Toolset=... / Tool=...
```

**→ 工具集命名规则 `Toolset.Tool` 也来自这里。**

**→ 好处（文档说的）：「keeps `tools/list` responses small even with **hundreds of tools**」。
→ 本项目启用了 5 个工具集插件（ModelContextProtocol / ToolsetRegistry / EditorToolset /
   AutomationTestToolset / SlateInspectorToolset），工具总数上百。**

---

## 四、🎯 还有两条有用的

### 4.1 从 AI Agent 重启编辑器

> **「To restart the editor from an AI agent, call **`ExitEditor`** ...」**

**→ 有一条正规的重启路径，不用 PowerShell 杀进程。**
**⚠️ 但按项目 AGENTS.md 规则 1，关编辑器前必须问 —— 所以我不会主动用。**

### 4.2 多编辑器连接

**`## Connect to More Than One Editor`**
**→ 可以连多个编辑器实例。**
**⚠️ 但项目规则 1 明确「同一工程别开两个实例」（抢 `Saved/` 与资产锁）。**

---

## 五、这一篇学到什么

**1. 🔴 MCP 工具调用跑在**游戏线程**，一次一个 —— 和 Python 脚本一样会阻塞编辑器。**

**2. 🔴 客户端有**约 120 秒超时**，文档明确建议把长任务**拆成多次短调用**。**
**→ 我靠试错发现的「分次运行」做法，文档里写着。**

**3. 🎯 `bEnableToolSearch = true` 是默认，`tools/list` 只返回 4 个元工具。**
**→ 我的 `mcp.ps1 -Toolset ... -Tool ...` 走的正是 `call_tool`。**

**4. 🎯 MCP 无认证，只按 Origin 允许列表保护（localhost / 127.0.0.1 / [::1]）。**

**5. 🎯 有 `ExitEditor` 这个正规重启工具（但项目规则不许我擅自关）。**

---

## 六、更正

| 之前 | 现在 |
| --- | --- |
| 「MCP 调用挂了是网络问题」 | ❌ **超时 + 游戏线程排队** |
| 「分次运行是我发明的技巧」 | ❌ **文档明确写着 split into shorter calls** |
| 「MCP 是个独立服务」 | ❌ **它跑在编辑器进程内，共享游戏线程** |

---

## 七、还没做到

| 项 | 说明 |
| --- | --- |
| `progressToken` 心跳 | 我的调用脚本没实现（也超出可控范围）|
| **写自己的 Toolset（Python）** | **文档有完整章节，我没试过** |
| 写 Agent Skill | 没试 |
| MCP Resources | 没试 |
| 在打包版本里跑 MCP | 没试 |

**→ 「写自己的 Toolset」是值得做的一件事：
项目里已经有 `lingxujie_tools.level_ops.LingXuJieTools`（之前有人写过），
说明这条路可行，但我没自己写过。**

---

## 八、状态

```
Docs/UE5-LEARN-READ-MCP.md   1 篇（共 44 篇 learn 文档）
补读进度：32 / 57
主关卡 116 actor / 视口复位
```

---

## 九、下一篇

**继续补读（还剩 25 篇）。下一批：**
- `blueprints.md`（21.4 KB）
- `data-tables.md`（8.7 KB）+ `savegame.md`（12.2 KB）
- `sequencer-editor.md`（14.4 KB）
- `geometry-scripting.md`（10.4 KB）
- `fbx-static-mesh.md`（16.1 KB）+ `import-static-meshes.md`

**→ 选 `data-tables.md` + `savegame.md`（两篇都是实战向，且项目有 `LXJItems` 物品表）。**
