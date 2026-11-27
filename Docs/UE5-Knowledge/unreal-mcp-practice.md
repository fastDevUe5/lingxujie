# Unreal MCP 实操（引擎 5.8.4｜核对 2026-11-17｜本工程实测 ✅）

## 一句话结论

UE 的官方 MCP 是“**编辑器进程内的 MCP server + Toolset 注册表 + tool search 模式**”：
客户端只会看到 3 个元工具，真正的能力要靠 `call_tool` 按需调用。它足够让 agent 看视口、摆 Actor、跑 PIE，
但**每次编辑器重启都会让会话失效，必须重连**。

## 启用（本工程的实际配置）

1. `.uproject` 启用插件：`ModelContextProtocol`、`ToolsetRegistry`、`EditorToolset`、`AutomationTestToolset`、`SlateInspectorToolset`。
2. 让服务启动（二选一，本工程两个都做了）：
   - 命令行：`-ModelContextProtocolStartServer`
   - 配置：`Saved/Config/WindowsEditor/EditorPerProjectUserSettings.ini`
     `[/Script/ModelContextProtocolEngine.ModelContextProtocolSettings] bAutoStartServer=True`
3. 端口/路径：默认 `127.0.0.1:8000/mcp`，可用 `-ModelContextProtocolPort=N` 覆盖。
4. 验证：日志出现 `Starting MCP server on port 8000`；`Get-NetTCPConnection -LocalPort 8000` 显示监听。

## 调用模型（tool search 模式）

`tools/list` 只返回 3 个：

| 工具 | 作用 |
| --- | --- |
| `list_toolsets` | 列出所有工具集（本机实测 **21 个**） |
| `describe_toolset` | 取某个工具集里每个工具的名称、描述、inputSchema |
| `call_tool` | 实际执行：`{toolset_name, tool_name(短名), arguments}` |

示例（DSH 里的调用形态）：

```
mcp__unreal__call_tool(toolset_name="editor_toolset.toolsets.scene.SceneTools",
                       tool_name="get_current_level", arguments={})
→ {"returnValue": "/Game/Maps/CoinRush"}
```

**注意**：`describe_toolset` 返回的工具名带工具集前缀（`EditorToolset.EditorAppToolset.GetVisibleActors`），
但 `call_tool` 的 `tool_name` 要传**短名**（`GetVisibleActors`）。

## 实测可用的能力（本工程）

| 工具 | 实测结果 |
| --- | --- |
| `SceneTools.get_current_level` | `/Game/Maps/CoinRush` |
| `EditorAppToolset.GetVisibleActors` | 返回视锥内 actor 的 refPath 列表 |
| `EditorAppToolset.SetCameraTransform` | 改关卡视口机位 |
| `EditorAppToolset.CaptureViewport` | 返回 base64 PNG（300~500 KB），必须显式传 `captureTransform` |
| `SceneTools.add_to_scene_from_asset` | 生成 `/Engine/BasicShapes/Cube` 的 StaticMeshActor |
| `SceneTools.remove_from_scene` | 删除成功，返回 `true` |
| `EditorAppToolset.StartPIE` / `IsPIERunning` / `StopPIE` | 能在编辑器里起停 PIE，`IsPIERunning` 返回 `true` |

## 会话与坑

1. **编辑器重启 → 会话失效**：`Unknown session id '...' for 'tools/call'; client should reinitialize`。
   客户端配置里的 `reconnect` 只处理传输层断连，**不会**自动重做 MCP 握手；恢复办法是重挂客户端
   （DSH 里：禁用再启用 `@local/unreal-mcp` bundle）或重启 agent 会话。
2. **大结果会落盘**：`CaptureViewport` 的 base64 通常 300~500 KB，harness 会截断并写文件，
   用 `Tools/DecodeMcpCapture.ps1 -SpillPath <文件> -OutFile view.png` 解码后再看。
3. **同一时间只允许一个 agent**：MCP 会话、资产锁、Live Coding 会互相冲突。
4. **安全边界**：只监听 `127.0.0.1`，但它等于把“任意编辑器操作 + 脚本执行”交给代理，别开放到公网。
5. **打包不受影响**：插件虽标 `NoRedist`，但它是 EditorOnly，不参与 staging（实测打包成功）。

## 官方文档（当前是 5.9 版）与本机 5.8.4 的差异（重要）

Epic 的文档站默认展示**最新版本**，`unreal-mcp-in-unreal-editor` 这一页现在是 5.9 的内容。
和本机 5.8.4 逐项比对后，有几处**实质差异**，照文档配会在 5.8 上碰壁：

| 项 | 5.9 文档 | 本机 5.8.4（源码/实测） |
| --- | --- | --- |
| 服务器自动启动 | 默认 **开启** | **默认关闭**（`ModelContextProtocolSettings.h:42` `bAutoStartServer=false`），必须传 `-ModelContextProtocolStartServer` 或改配置 |
| tool search 元工具 | 4 个：`list_toolsets` / `describe_toolset` / `describe_tools` / `call_tool` | **3 个**：没有 `describe_tools`（`ModelContextProtocolSettings.h:44`、`ModelContextProtocolToolsetRegistryAdapter.h:31`） |
| 编辑器内助手面板（直接跑 Claude Code/Cursor 等） | 有（"虚幻助手面板"） | **没有**，只能外接客户端 |
| `Origin` 允许列表（防 DNS rebinding） | 有，可配置额外来源 | 源码里**没有搜到**该实现（未逐行确认，按"可能缺失"对待，别把端口暴露给浏览器） |
| 控制台命令 | `StartServer` / `RefreshTools` / `GenerateClientConfig` | 同样存在：`ModelContextProtocolModule.cpp:22-33`、`ModelContextProtocolEngineModule.cpp:40` |
| 烘焙版工具（`AIRuntimeCallable`） | 支持，需打标签 | 未验证 |
| 项目级 instructions（写进 DefaultGame.ini） | 有（Project Settings → Agentic Workflows） | 未验证 |

**结论**：查官方文档时必须先确认版本选择器；对 5.8 而言，`Engine/Source` 的源码才是唯一权威。

## 工程取舍

- 接法用“配置型 bundle”（`dsh-bundles/unreal-mcp/`），不改 DSH 核心，换机器只要装一次 bundle。
- 重连步骤写进 `AGENTS.md` 硬约束第 4 条，避免每个新 agent 重新踩。
- 需要“看画面”时优先用 `CaptureViewport`（能指定机位、能隐藏 UI），比截屏游戏窗口稳定。

## 待复核（升级 5.9 时）

- [ ] tool search 是否仍默认开启（5.9 增加了 MCP 的端口/来源/协议版本设置页）
- [ ] `CaptureViewport` 是否仍强制 `captureTransform`
- [ ] 会话失效后的重连是否已被官方修掉
- [ ] 工具集数量与名称是否变化（`AllToolsets` 在 5.9 增加了蓝图、编辑器操作、MVVM、性能等）
