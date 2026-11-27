# UE5 / CoinRush 踩坑清单

每条都来自本机实测，写明**症状 → 原因 → 正确做法 → 出处**。新增条目请保持同样格式，出处写源码路径、日志片段或退出码。

引擎：UE 5.8.4（`C:\Program Files\Epic Games\UE_5.8`）｜工具链：VS2026 / MSVC 14.52

---

## 1. `GetInputMouseDelta` 不在 `UPlayerInput` 上

- **症状**：`error C2039: "GetInputMouseDelta": 不是 "UPlayerInput" 的成员`
- **原因**：该函数属于 `APlayerController`，不是输入对象。
- **正确**：`PC->GetInputMouseDelta(dx, dy);`
- **出处**：`Source/CoinRush/CRCharacter.cpp` 编译日志；声明在 `Engine/Source/Runtime/Engine/Classes/GameFramework/PlayerController.h`

## 2. Python 不能给材质表达式输入赋值

- **症状**：`MaterialExpressionMultiply: Property 'A' for attribute 'a' ... is protected and cannot be set`
- **原因**：`FExpressionInput` 成员是 protected，`set_editor_property` 只对公开属性有效。
- **正确**：
  ```python
  unreal.MaterialEditingLibrary.connect_material_expressions(base, "", multiply, "A")
  unreal.MaterialEditingLibrary.connect_material_expressions(strength, "", multiply, "B")
  unreal.MaterialEditingLibrary.connect_material_property(multiply, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
  ```
  常量表达式本身仍可用 `set_editor_property("constant", unreal.LinearColor(r,g,b,1))`。
- **出处**：`Tools/build_level.py` 的 `make_material()`；异常发生在 PythonScriptCommandlet

## 3. 雾的组件属性叫 `enable_volumetric_fog`

- **症状**：`ExponentialHeightFogComponent: Failed to find property 'volumetric_fog'`
- **正确**：`set_editor_property("enable_volumetric_fog", False)`；同类还有 `fog_density`、`fog_height_falloff`。
- **教训**：Python 属性名是 UPROPERTY 去前缀后的名字，别按 C++ 变量名猜。
- **出处**：`Tools/build_level.py` 的 `build_lighting()`；属性声明在 `Engine/Source/Runtime/Engine/Classes/Components/ExponentialHeightFogComponent.h`

## 4. 编辑器开着时 UBT 拒绝编译

- **症状**：`Unable to build while Live Coding is active. Exit the editor and game...`（`Result: Failed (OtherCompilationError)`，退出码 6）
- **原因**：UBT 检测到目标可执行文件的 Live Coding 互斥体；由 `BuildConfiguration.bAllowHotReloadFromIDE` 控制。
- **正确**：构建命令加 `-NoHotReloadFromIDE`。**注意 `-NoHotReload` 无效**（它设的是 `HotReloadMode`，不解除该检查）。
- **出处**：`System/HotReload.cs:270-278`、`Configuration/BuildConfiguration.cs:160`；`Tools/BuildAll.ps1` 已带该参数

## 5. 打包必须先编译、再 `-skipbuild`

- **症状**：`RunUAT BuildCookRun ... -build` 直接失败（退出码 6），日志停在 Live Coding 那句。
- **原因**：`BuildCookRun` 不接收 `-NoHotReloadFromIDE`，它自己调 UBT 时又撞上同一个互斥。
- **正确**：两步走（`Tools/Package.ps1` 已封装）
  1. `Build.bat CoinRushEditor Win64 Development ... -NoHotReloadFromIDE`
  2. `Build.bat CoinRush Win64 Development ... -NoHotReloadFromIDE`
  3. `RunUAT BuildCookRun ... -skipbuild -cook -stage -pak -archive`
- **验证**：实测成功——497 个包、整包约 900 MB、`CoinRush.exe` 317 MB，启动日志到 `Engine is initialized`。
- **顺带结论**：MCP 插件虽标 `NoRedist`，但它是 EditorOnly，不参与 staging，不影响打包。

## 6. PowerShell 5.1 会把无 BOM 的 UTF-8 当 ANSI 读

- **症状**：`.ps1` 里的中文让解析器报 `The string is missing the terminator`，明明引号是成对的。
- **原因**：PS 5.1 默认按系统代码页（GBK）读无 BOM 文件，多字节字符被截断。
- **正确**：**所有 `.ps1` 保持纯 ASCII**（注释也写英文）。需要中文输出时用 `[System.IO.File]::ReadAllText($p, [Text.Encoding]::UTF8)` 读文件，或改用 `pwsh` 7。
- **出处**：`Tools/CheckAssets.ps1` 第一版；`Tools/*.ps1` 现已全部 ASCII（可用脚本检查非 ASCII 字符数）

## 7. `PrintWindow` 抓 DX12 窗口会挂起

- **症状**：对打包版游戏窗口调用 `PrintWindow(hwnd, hdc, 2)` 长时间不返回，脚本卡死。
- **正确**：别用它抓实时 3D 窗口；用 `Tools/RunGame.ps1` 那条路（启动游戏 → `CopyFromScreen` 抓客户区 → 关闭）。
- **出处**：`Tools/CaptureWindow.ps1`（保留作参考，但对 DX12 不可靠）

## 8. 编辑器重启后 MCP 会话失效

- **症状**：`Unknown session id 'xxxx' for 'tools/call'; client should reinitialize`
- **原因**：UE 的 MCP 服务每个编辑器进程一套会话；客户端保存的 session id 在新进程里无效，且不会自动重握手。
- **正确**：禁用再启用 DSH 的 `@local/unreal-mcp` bundle（强制重连），或重启 agent 会话。客户端配置里的 `reconnect` 只处理传输层断连，解决不了这个。
- **出处**：`ModelContextProtocolServer.cpp` 的会话校验；实测两次

## 9. MCP 服务默认不随编辑器启动

- **症状**：插件启用了，但 8000 端口不监听，日志没有 `Starting MCP server`。
- **原因**：`UModelContextProtocolSettings::bAutoStartServer` 默认 `false`（`config=EditorPerProjectUserSettings`）。
- **正确**：`-ModelContextProtocolStartServer` 启动，或在 `Saved/Config/WindowsEditor/EditorPerProjectUserSettings.ini` 写
  `[/Script/ModelContextProtocolEngine.ModelContextProtocolSettings] bAutoStartServer=True`（本工程两者都做了）。
- **出处**：`ModelContextProtocolSettings.h:42`、`ModelContextProtocolSettings.cpp:32-61`

## 10. `CaptureViewport` 必须显式传 `captureTransform`

- **症状**：`Function "CaptureViewport", input param "captureTransform" needs a default value.`
- **正确**：显式传相机位姿（`location` + `rotation`），即使你刚用 `SetCameraTransform` 设过。
- **补充**：返回的 base64 PNG 通常 300~500 KB，会被 harness 落盘；用 `Tools/DecodeMcpCapture.ps1` 解码。

## 11. `new_level` 对已存在地图会失败

- **症状**：`LevelEditorSubsystem: Error: NewLevel. Failed to validate the destination. An asset already exists at this location.`
- **正确**：改成幂等重建——`load_level()` → 遍历 `get_all_level_actors()` 并 `destroy_actor()` → 重新生成 → `save_current_level()`。只有地图不存在时才 `new_level`。
- **出处**：`Tools/build_level.py` 的 `ensure_empty_level()`

## 12. 双击 `.uproject` 提示找不到引擎

- **原因**：`C:\ProgramData\Epic\UnrealEngineLauncher\LauncherInstalled.dat` 的 `InstallationList` 为空，引擎未登记。
- **正确**：用 `Open_Editor.bat` / `Run_Game.bat`（直接调 `UnrealEditor.exe`），或在注册表 `HKCU\Software\Epic Games\Unreal Engine\Builds` 登记。

## 13. PowerShell 的 `$PID` 是只读自动变量

- **症状**：枚举窗口时 `无法覆盖变量 PID，因为该变量为只读`。
- **正确**：用别的名字，例如 `$procId`。
- **出处**：`Tools/RunGame.ps1` 的 C# 互操作调用

## 14. VS Code IntelliSense 需要 UBT 生成的编译数据库

- **症状**：新克隆的工程在 VS Code 里 C++ 全红。
- **正确**：跑 `UnrealBuildTool -projectfiles -project=<uproject> -game -VSCode`（VS Code 任务“UE: 刷新 VS Code IntelliSense”已封装），生成 `.vscode/compileCommands_CoinRush.json`。
- **注意**：`compileCommands_*/` 目录里的 `.rsp` 和 `*.code-workspace` 含绝对路径，已 gitignore，别提交。

## 15. 单机编译器版本偏新

- **症状**：编译日志告警 `Visual Studio compiler version 14.52.37029 is newer than latest preferred version 14.50.35717`。
- **处理**：目前只影响告警，产物正常；如遇到无从解释的编译/链接错误，优先怀疑工具链版本，换 VS 2022 17.x 的 MSVC 14.38~14.44 复核。

## 16. 官方文档默认展示最新版本（5.9），不是本机的 5.8

- **症状**：照着 `dev.epicgames.com` 的页面配 MCP，结果 5.8 上服务不自启、工具里找不到 `describe_tools`。
- **原因**：文档页顶部/侧栏有版本选择器，默认给最新版；5.8 与 5.9 在 MCP 上有实质差异（自动启动默认值、元工具数量、助手面板、Origin 校验）。
- **正确**：查文档先确认版本；对 API 细节以 `Engine/Source` 为准。差异清单见
  [`Docs/UE5-Knowledge/unreal-mcp-practice.md`](UE5-Knowledge/unreal-mcp-practice.md) 的"官方文档（当前是 5.9 版）与本机 5.8.4 的差异"。
- **出处**：<https://dev.epicgames.com/documentation/unreal-engine/unreal-mcp-in-unreal-editor?lang=zh-CN>（页面标题为 5.9 文档）vs 本机 `ModelContextProtocolSettings.h:42-44`

## 17. `-game` 启动时 Python/ToolsetRegistry 报 AttributeError

- **症状**：游戏日志开头出现
  `module 'unreal' has no attribute 'PythonTestRunner'`、`has no attribute 'AgentSkill'`，来自
  `Engine/Plugins/Experimental/ToolsetRegistry/Content/Python/init_unreal.py`。
- **原因**：这些是编辑器插件的 Python 初始化脚本，在 `-game` 模式下运行时缺少编辑器 Python 绑定；属于噪音。
- **处理**：忽略即可，不影响游戏；如果嫌吵，可以在打包版里不启用这些插件（编辑器专用，不进包）。
- **出处**：`Saved\Logs\CoinRush.log` 启动段，2026-11-17 实测

## 18. `[SystemSettings]` 里的 `t.MaxFPS` 在工程 DefaultEngine.ini 不生效

- **症状**：在 `Config/DefaultEngine.ini` 写了
  ```
  [SystemSettings]
  t.MaxFPS=120
  ```
  启动后 `stat unit` 仍是 `Frame: 2.02 ms`（约 485fps，完全没被限制）；而同一文件 `[/Script/Engine.Engine] bSmoothFrameRate=False` 是生效的。
- **对照**：命令行 `-ExecCmds="t.MaxFPS 120, stat unit"` 立刻变成 `Frame: 8.33 ms`，说明 cvar 本身没问题。
- **做法**：帧率上限写到代码里（`ACRGameMode::StartPlay` 用 `IConsoleManager` 设），或用命令行；不要指望工程 ini 的 `[SystemSettings]`。
- **出处**：`Config/DefaultEngine.ini`、`Source/CoinRush/CRGameMode.cpp`、2026-11-17 三次对比实测

## 19. 运行时合成音频在 5.8 上不可靠，改用“生成 WAV + 导入”

- **症状**：想用 `USoundWaveProcedural` + `QueueAudio` 做零资产音效，但 5.8 里 `USoundWave` 的 `Duration`、`NumChannels`、`SampleRate` 已经私有化/改名，`GetDuration()` 是虚函数，一次性音效的时长语义不确定——不播、或播完不收尾都可能，且本地无法用耳朵验证。
- **正确**：用脚本生成标准 16-bit PCM WAV（`Tools/GenerateAudio.ps1`），再用 `AssetImportTask` 导入成真正的 `USoundWave` 资产（`Tools/import_audio.py`），C++ 里 `LoadObject` + `PlaySoundAtLocation`。这条路只用到稳定 API，音色可听、可调、可版本控制。
- **出处**：本工程 2026-11-17 实测；`Content/Audio/SFX_Coin.uasset`、`SFX_Land.uasset`

## 20. 运行时 `LoadObject` 的资产不会自动进包（打包后材质变灰、音效没声）

- **症状**：打包版能跑，但日志出现 `[CoinRush] SFX loaded: coin=0 land=0`；同类问题表现为金币/角色材质变成默认灰。
- **原因**：cooker 只收集**静态可见的引用**（关卡里的 Actor、CDO 上的 ConstructorHelpers/硬引用、软引用清单）。代码里
  `LoadObject<USoundBase>(nullptr, TEXT("/Game/Audio/SFX_Coin.SFX_Coin"))` 用的是纯字符串路径，cooker 看不见，于是这些资产根本没被打进包。
- **正确**：在打包设置里显式声明目录，等价 ini：
  ```
  [/Script/UnrealEd.ProjectPackagingSettings]
  +DirectoriesToAlwaysCook=(Path="/Game/Audio")
  +DirectoriesToAlwaysCook=(Path="/Game/Materials")
  ```
  或者改用 `TSoftObjectPtr` / 资产注册表查询，让引用在 cook 时可见。
- **验证**：打包后检查 `%APPDATA%\Unreal Engine\AutomationTool\Logs\<Engine>\FinalCopyWin64_UFSFiles.txt` 里有没有对应 `.uasset`；
  再跑一次打包版，日志应为 `SFX loaded: coin=1 land=1`。
- **出处**：2026-11-17 实测——修复前 `coin=0 land=0`，加 `DirectoriesToAlwaysCook` 后 `coin=1 land=1`，cooked manifest 里出现
  `M_Coin/M_Character/M_Accent/SFX_Coin/SFX_Land`。

## 21. `IncludeDebugFiles` 管不到命令行打包，要去掉 pdb 得用 `-nodebuginfo`

- **症状**：在 `DefaultGame.ini` 写了 `[/Script/UnrealEd.ProjectPackagingSettings] IncludeDebugFiles=False`，
  `BuildCookRun` 打出来的 Shipping 包里仍然有 211 MB 的 `.pdb`。
- **原因**：该属性只在编辑器 **Turnkey**（平台菜单打包）里被读取（`TurnkeySupportModule.cpp:574`）；
  UAT 的 `BuildCookRun` 用的是 `ProjectParams.NoDebugInfo`（命令行 `-nodebuginfo`），两者互不相通。
- **正确**：给 `BuildCookRun` 加 `-nodebuginfo`。属性名也注意：是 `IncludeDebugFiles`，**没有 `b` 前缀**，写错会被静默忽略
  （以 `ProjectPackagingSettings.h:242` 的 UPROPERTY 名为准）。
- **验证**：Shipping 包里 `Get-ChildItem -Recurse -Filter *.pdb` 计数为 0，整包从 826 MB 降到 319 MB。
- **出处**：2026-11-17 实测；`AutomationUtils/ProjectParams.cs:2176-2185`、`DeveloperToolSettings/.../ProjectPackagingSettings.h:242`

## 22. Editor 目标没有 Shipping 配置

- **症状**：`Build.bat CoinRushEditor Win64 Shipping` 直接失败（退出码 6），打包脚本第一步就挂。
- **原因**：`CoinRushEditor` 只有 Debug/DebugGame/Development 等配置；Shipping 只对**游戏**目标有意义。
- **正确**：打 Shipping 包时，编辑器目标仍然编译 Development（cooker 只需要一个能跑的编辑器），游戏目标才用 Shipping。
  `Tools/Package.ps1` 已经按这个规则写死。
- **出处**：2026-11-17 实测；`Source/CoinRushEditor.Target.cs`

## 23. 只发 `CoinRush\` 子目录的包，双击 `-Win64-Shipping.exe` 会静默退出（退出码 1）

- **症状**：把归档里的 `CoinRush\Binaries\Win64\CoinRush-Win64-Shipping.exe` 单独拷走（或只打包 `CoinRush\` 目录）后运行，
  进程立刻结束、退出码 1，**不写日志、不弹窗、事件日志里只有一条无害的 `RADAR_PRE_LEAK_64`**；而在原归档目录里跑同一个 exe 却正常。
- **原因**：`BuildCookRun -archive` 产出的根目录是 `...\Windows\`，里面有
  `CoinRush.exe`（`BootstrapPackagedGame` 引导程序）、共享的 `Engine\`、以及 `CoinRush\` 内容目录。
  游戏二进制按 `../../../Engine` 找引擎模块——只拷 `CoinRush\` 就找不到 `Engine\`，于是在初始化日志之前退出。
  原始位置能跑，是因为上一层正好有 `Engine\`。
- **正确**：发布时必须带上 `CoinRush.exe` + `Engine\` + `CoinRush\` 三者，入口用 `CoinRush.exe`。
  `Tools/MakeRelease.ps1` 已改为从 `Saved\Package\Shipping\Windows` 整目录打包。
- **验证**：解压到全新目录 → 运行 `CoinRush.exe` → 进程存活、窗口标题 `CoinRush`。
- **出处**：2026-11-17 实测；`Saved\Package\Shipping\Windows\` 布局

## 24. Blueprint 工具的 `type_id` 是本地化的（中文编辑器）

- **症状**：照文档用 `Math|Rotator|MakeRotator`、`Development|PrintString` 写图，报
  `The node could not be created` / `AddEvent|EventBeginPlay does not exist`。
- **原因**：MCP 的节点类型 ID 取自编辑器本地化后的分类与标题。中文编辑器下实际是
  `数学|旋转|MakeRotator`、`开发|PrintString`、`变换|AddActorLocalRotation`、`添加事件|事件BeginPlay`。
- **正确**：先用 `BlueprintTools.find_node_types(graph, type_id_filter="BeginPlay", context_pins=[])` 拿真实 ID；
  事件节点用 `create_node` 建，不要用 `write_graph_dsl` 的 `(event ...)`（5.8.4 + 中文环境实测解析失败）。
- **补充**：`get_node_type_pins` 会创建临时节点；孤立节点会导致编译失败且错误列表为空。
- **出处**：2026-11-19 实测；`Docs/UE5-Knowledge/blueprint-authoring-via-mcp.md`

## 25. StaticMeshActor 蓝图的 Tick 逻辑被静默忽略（组件移动性 = Static）

- **症状**：蓝图里 Tick 调 `AddActorLocalRotation` / `SetActorRotation`，运行时只有日志
  `Mobility of ... StaticMeshComponent0 has to be 'Movable' if you'd like to move.`，物体纹丝不动。
- **原因**：`StaticMeshActor` 及其子类的网格组件默认 `Static` 移动性。用 `set_properties({"Mobility": "Movable"})`
  改 CDO 组件**不生效**（返回 true，但被组件模板覆盖）。
- **正确**：在生成器里对实例组件调用 `component.set_mobility(unreal.ComponentMobility.MOVABLE)`；
  拾取物还要 `set_collision_profile_name("OverlapAllDynamic")` + `set_editor_property("generate_overlap_events", True)`
  （没有 `set_generate_overlap_events`）。属性 JSON 改 `BodyInstance.CollisionProfileName` 也不生效。
- **验证**：改完后游戏日志不再出现该警告，倒计时 44→49、加时球消失。
- **出处**：2026-11-19 实测；`Tools/build_level.py::configure_blueprint_prop`

## 26. Smart App Control 拦截 UBT 动态编译的规则程序集（构建 exit 6）

- **症状**：`Build.bat CoinRushEditor/CoinRush ...` 退出码 6，日志里：
  `Could not load file or assembly '...\Intermediate\Build\BuildRules\CoinRushModuleRules.dll'. 应用程序控制策略已阻止此文件。 (0x800711C7)`
  随后 `IOException: The process cannot access the file ... because it is being used by another process`。
- **原因**：Windows 11 **Smart App Control 处于强制模式**（`HKLM\SYSTEM\CurrentControlSet\Control\CI\Policy\VerifiedAndReputablePolicyState = 1`），
  阻止 `dotnet.exe` 加载未签名/无信誉的托管程序集。事件日志 `Microsoft-Windows-CodeIntegrity/Operational` 事件 3077 指向同一文件。
  这是**机器策略**，不是工程问题：Nov 19 还能构建（策略当时未生效/未拉取新判定），Nov 22 起被拦。
- **影响**：任何 `dotnet` 驱动的 UBT 构建（Editor / Game 目标）都会失败；`-skipbuild` 的 cook/archive 仍然可用。
- **可行解**：
  1. 关闭 Smart App Control（Windows 安全中心 → 应用和浏览器控制 → 智能应用控制 → 关闭；**关闭后除非重装系统否则无法再打开**，属于用户决策）；
  2. 在无 SAC 的机器或 CI 上构建，产物拷回；
  3. 用受信任证书给程序集签名（需要企业环境，个人环境没有意义）。
  另：管理员加 Defender 排除项**不能**绕过 SAC（实测普通权限直接拒绝）。
- **应急**：只做 cook/archive 时可用 `Tools\Package.ps1` 的第二步命令手动执行（`RunUAT.bat BuildCookRun ... -skipbuild`），
  但那会沿用**旧的** Shipping 二进制——本次验证就是这么发现的：包能跑，但结算页缺 `BEST` 行（exe 时间戳是 11/17）。
- **出处**：2026-11-22 实测；CodeIntegrity 事件 3077 / `VerifiedAndReputablePolicyState=1`

## 27. 打包版存档写不进去（Shipping 的 ProjectSavedDir 指向 %LOCALAPPDATA%）

- **症状**：Shipping 包跑完一局，结算页显示 `SAVE FAILED`，包目录和 `%LOCALAPPDATA%` 下都没有 `.sav`；
  同样的代码用 Development 包跑却能正常存档（存到包目录）。
- **定位过程**：在 HUD 上临时打出 `ProjectSavedDir` 与写文件结果，得到
  `mem=1 bytes=2009 write=0 err=5 C:/Users/tk/AppData/Local/CoinRush/Saved/SaveGames/CoinRushProfile.sav`，
  `err=5 = ERROR_ACCESS_DENIED`；同时写包目录的探针返回 `project=1 err=0`。
- **原因**：打包版 `FPaths::ProjectSavedDir()` = `%LOCALAPPDATA%\<Project>\Saved\`（走 `FPlatformMisc::UserDir()`），
  这台机器上未签名的 Shipping 进程对该目录写文件被拒绝；Development 包解析到项目目录，所以没有暴露。
- **正确**：存档先写 `ProjectSavedDir()`，失败则回退到 `FPaths::ProjectDir()/Saved/SaveGames/`（便携存档）；
  读档时若标准槽不存在，就从这个便携路径 `LoadGameFromMemory`。HUD 只在“尝试过保存且失败”时提示。
- **验证**：打包版跑两局——第一局 `COINS 1/8` 后包内出现 `Saved/SaveGames/CoinRushProfile.sav`，
  第二局 0 分结算页显示 `BEST 1/8 COINS`，说明跨进程读档成功。
- **出处**：2026-11-22 实测；`Tools/VerifyPackage.ps1` + `Saved/Screenshots/Pkg_LoadRun.png`

## 28. 伤害数字用 TextRender 在 Game 模式不渲染（LingXuJie）

- **症状**：3D 文字 Actor（`UTextRenderComponent`）spawn 成功（日志 `valid=1`、位置正确），
  但 `-game` 窗口里完全看不到数字。
- **正确**：即时 UI 元素走 **Canvas HUD + `Canvas->Project(World)` 世界坐标投影**，
  在 `AHUD::DrawHUD` 里画（本工程 `LXJHUD::AddDamageNumber`），立刻可见。
- **出处**：2026-11-22 实测；`Source/LingXuJie/LXJHUD.*`

## 29. 自定义第三人称相机未初始化 yaw，W 永远走向世界 +X

- **症状**：角色出生在后面朝南的 PlayerStart，但按 W 却往东走，场景里的门和怪都不在视野中，
  技能扫掠也打不到（日志 `hits=0`）。
- **原因**：相机 boom 用 `SetUsingAbsoluteRotation(true)` 并硬编码 `CameraYaw = 0`，
  不跟随 PlayerStart / Controller 朝向；移动方向由相机 yaw 推导。
- **正确**：`BeginPlay` 里 `CameraYaw = GetController()->GetControlRotation().Yaw`。
- **出处**：2026-11-22 实测；`Source/LingXuJie/LXJCharacter.cpp`

## 30. UE 5.8 编译小坑两则（LingXuJie）

- `EKeys::Type` 不存在：键位数组应写 `const FKey Slots[] = { EKeys::LeftMouseButton, ... };`，
  并 `#include "InputCoreTypes.h"`。
- `FOverlapResult` 需要显式 `#include "Engine/OverlapResult.h"`（`Engine/World.h` 不再传递包含）。
- **出处**：2026-11-22 编译报错原文（error C2039 / C2027）

## 31. 排查“道具/怪物到底在不在关卡里”：打印 actor 清单

- **做法**：`Tools/inspect_level.py` 把 `get_all_level_actors()` 的 label / class / location 写成
  `Saved/level_actors.txt`（直接写文件比 `unreal.log` 可靠，commandlet 的日志有时不进 stdout）。
- 本次靠它确认 3 个 `LXJTrainingDummy` 确实在 `/Game/Maps/LingXuJie`、坐标正确，
  从而把问题定位到“相机朝向”而不是“生成失败”。
- **出处**：2026-11-22 实测；`Tools/inspect_level.py`

## 32. agent 沙箱限制 UBT 日志目录 → dotnet 抛未捕获异常，构建“假失败”（0xE0434352）

- **症状**：`Tools\BuildAll.ps1` 报 `Build failed` / exit `-532462766`，但 UBT 日志里是
  `Result: Succeeded`、DLL 时间戳也更新了；连输出都只有 `Using bundled DotNet SDK version` 两行，
  之后再跑连 `%LOCALAPPDATA%\UnrealBuildTool\Log.txt` 都不再刷新。
- **定位**：别用 `Build.bat`（它吞掉托管异常），直接跑
  `dotnet.exe <Engine>\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.dll -Mode=QueryTargets -Project=<uproject>`
  并重定向到文件，得到真身：
  `Unhandled exception. System.UnauthorizedAccessException: Access to the path
  'C:\Users\<user>\AppData\Local\UnrealBuildTool\Trace-backup-...uba' is denied.
  at EpicGames.Core.Log.BackupLogFile(...) at UnrealBuildTool.UnrealBuildTool.Main(...)`。
- **原因**：UBT 启动时把上一条 trace/log **改名备份并删掉旧备份**，目录在 `%LOCALAPPDATA%`（工程外）。
  受限沙箱（只允许写工作区）拒绝该删除 → 未处理异常 → 进程以 `0xE0434352` 退出。
  **代码没编译错，是沙箱/权限问题**。
- **正确**：
  1. 让 agent 以可写 `%LOCALAPPDATA%\UnrealBuildTool` 的权限跑构建（本会话已改成 full-access）；
  2. 或在 `BuildConfiguration.xml` 里关掉日志备份：`<Log bBackupLogFiles="false"/>`
     （`GlobalOptions.BackupLogFiles`，关了就不再删除旧备份）；
  3. 判断构建成败以 UBT 日志的 `Result: Succeeded` + 产物时间戳为准，不要只看退出码。
- **出处**：2026-11-22 实测；`UnrealBuildTool/System/GlobalOptions.cs:115`、`UnrealBuildTool.cs:223`

## 33. `SpawnActor(…, Rotation, …)` 的朝向在 `BeginPlay` 里还读不到（法术弹永远飞 +X）

- **症状**：邪修日志里 `dir V(X=-0.55, Y=-0.83, Z=0.06)`（瞄准是对的），但弹丸每次都是
  `rot=R(0)`、`vel=V(X=1900.00)`，笔直飞世界 +X、从不命中任何人。
- **原因**：`BeginPlay` 是在 `UWorld::SpawnActor` 内部、`InitProjectile` **之前**派发的；
  此时传入的 SpawnRotation 还没落到根组件上，`GetActorForwardVector()` 仍是 `(1,0,0)`。
  `UProjectileMovementComponent::InitializeComponent` 又用 `InitialSpeed * forward` 先算了一遍速度，
  于是 `InitProjectile` 里再取 forward 也是错的。
- **正确**：不要把朝向托付给 SpawnTransform——把方向显式传进去：
  `InitProjectile(Source, Direction, Damage)` 内部 `SetActorRotation(Direction.Rotation())`
  + `Movement->Velocity = Direction.GetSafeNormal() * Speed`。
- **附带验证**：弹丸碰撞用 **Block + `OnComponentHit`**（引擎 projectile 模板的做法）才可靠；
  一开始用 `QueryOnly` + 只对 Pawn `Overlap` 的球体，扫掠移动**完全不产生** overlap 事件（实测 0 次）。
- **出处**：2026-11-22 实测；`Source/LingXuJie/LXJProjectile.cpp`、`LXJEvilCultivator.cpp`

## 34. 纯函数状态机别把“巡逻走远”当成“该回家”

- **症状**：怪物出生后日志疯狂刷 `Patrol -> Return`、`Return -> Patrol`，每帧一次，怪只在原地抖。
- **原因**：brain 规则写成“没目标且离出生点 > 阈值 → Return”，而巡逻本身就会走出 180 单位阈值，
  于是巡逻→返回→到家→巡逻无限循环。
- **正确**：Return 只由**失去目标**触发（当前状态是 Chase/Attack），巡逻可以合法离开出生点；
  leash 仍然优先于一切。纯函数测试里专门留了 “a wandering patrol keeps patrolling” 这条用例防回归。
- **出处**：2026-11-22 实测；`Source/LingXuJie/LXJMonsterBrain.h`、`Private/Tests/LXJMonsterBrainTests.cpp`

## 35. 近战判定三连坑：单次扫掠被布景挡住 / 朝向是旧的 / 怪物绕到背后

- **症状**：`Sword art hits=0`，或者贴脸打怪一直 `hits=0`，而怪物照样在揍玩家。
- **三个真凶（都实测踩过）**：
  1. `SweepSingleByChannel` 撞到第一个**布景**就停（本次是灵气环的发光石柱），怪在石头后面永远打不到。
     → 改 `SweepMultiByChannel` 遍历所有命中，只对**带 HealthComponent 的 actor**结算伤害，布景直接跳过。
  2. `Owner->GetActorForwardVector()` 是**最后一次移动方向**；站桩时它不变，玩家回头看哪都打不到。
     → 玩家把**相机 yaw** 通过 `Combat->SetAimDirection()` 传进去，扫掠沿相机方向；出招瞬间也把角色转向相机。
  3. 怪物在 `Chase` 里贴着玩家**横移绕圈**，经常转到背后；只用 `dot > 0` 判定就永远打不到。
     → 攻击距离内**停止移动**（`UpdateChase` 里 `Distance <= AttackRange*0.95` 直接 StopMovement），
     并给近战加“贴脸豁免”：`DistanceToOwner <= Radius + 150` 时无视朝向。
- **附带**：怪物攻击时的 `LaunchCharacter(forward*420)` 冲锋会把自己顶到玩家身后，已删除。
- **出处**：2026-11-22 实测；`LXJCombatComponent.cpp`、`LXJMonster.cpp`

## 36. 自动曝光会把你加的灯“追”成一片白（headless 截图尤其明显）

- **症状**：给关卡加暖阳 / 门灯 / 灵气点光之后，`RunGame` 截图整体发白、草地变黄绿、石台变奶油色；
  越调灯越白，把灯全删掉又恢复正常。
- **原因**：`r.DefaultFeature.AutoExposure=True` 时相机一直在收敛曝光，而 `RunGame` 是进关后 1 秒左右抓图，
  画面还没稳定；新增的亮光又会触发相机重新压曝光，于是整帧发白（不是某一盏灯过曝）。
- **正确**：
  1. 先锁曝光：`Config/DefaultEngine.ini` 里 `r.DefaultFeature.AutoExposure=False`（截图可复现，调美术时也好判断亮度）。
  2. 不要靠无头截图盲调亮度：一次只改一个变量、重跑一次对比；真正的 look-dev 应该在编辑器视口里做。
  3. 后处理里同时覆盖 `auto_exposure_min/max_brightness` 又改场景灯光，两个变量一起动就永远查不出是谁白的。
- **实测**：同一场景同一相机，加 4×6000 cd 点光时全白；关掉自动曝光后同样的灯只形成柔和光池。
- **出处**：2026-11-22 实测；`Config/DefaultEngine.ini`、`Tools/build_level.py`

## 37. 加第二盏平行光会报“多盏平行光竞争”，并可能让雾/半透明用错光源

- **症状**：屏幕上横着一条警告：`Multiple directional lights are competing to be the single one used for
  forward shading, translucent, water or volumetric fog. Please adjust their ForwardShadingPriority.`
- **原因**：forward 渲染只接受一盏“主”平行光，靠 `ForwardShadingPriority` 决定谁赢；不设时引擎按整体亮度猜。
- **正确**：给辅助光（补光/轮廓光）显式设低优先级，比如
  `safe_set(rim_component, "forward_shading_priority", -1)`，主光保持默认 0。
- **附带**：`ExponentialHeightFogComponent` **没有** `volumetric_fog_density` 属性（设了会被 skip），
  体素雾浓度由 `fog_density` 配合 `volumetric_fog_extinction_scale` 决定。
- **出处**：2026-11-22 实测；`Tools/build_level.py::build_lighting`

## 38. 贴图发白：`Texture2D` 的 sRGB 只能在导入时定；后处理属性名也不是想当然

- **症状**：PBR 贴图上墙后整片发白（草地变沙地、石台变奶油色），材质图里贴图、UV、法线都连对了。
- **定位**：用一段 probe 脚本打印 `texture.get_editor_property("srgb")` → 一直是 `False`。
- **原因**：`set_editor_property("srgb", True)` 会被接受但**不重建纹理资源**（不报错、`skip property` 也没有），
  采样仍按线性读，自然发白。
- **正确**：在**导入时**用工厂决定：`unreal.TextureFactory()` → `srgb = not is_linear`，
  法线再设 `compression_settings = TC_NORMALMAP`，然后 `task.factory = factory`。
  已经导入错的贴图必须删掉重导，改属性救不回来。
- **顺带的属性名坑**（都是实测撞出来的）：
  - 色温是 `white_temp`，**不是** `temperature`（`PostProcessSettings` 上没这个属性）；
  - `ExponentialHeightFogComponent` 没有 `volumetric_fog_density`（见 #37）；
  - `FPostProcessSettings` 这类**结构体没有 `get_name()`**，写通用 `safe_set()` 的报错分支时要
    `hasattr(obj, "get_name")` 兜底，否则日志本身会抛 `AttributeError` 把整个建关流程带崩。
- **出处**：2026-11-22 实测；`Tools/build_level.py::ensure_texture / apply_texture_flags / safe_set`

## 39. 自己搭 HDRI 天空球行不通：`Is Sky` 是编译期 usage 标记，Python 改不了

- **症状**：用"巨大反转球 + 无光照材质采样等距柱状图"当天空，结果**整个关卡被一个灰白球罩住**，
  同时引擎红字警告：`A sky light with real-time capture enabled is in the scene. It requires at least
  a SkyAtmosphere component, A volumetricCloud component or a mesh with a material tagged as IsSky.`
- **原因**：天空不是普通不透明几何——渲染器要靠材质的 **Is Sky** 标记把它画在远平面、并让 SkyLight 采集。
  这个标记是材质的 **usage flag**（编译期由 `SetMaterialUsage` 设定），
  Python 的 `set_editor_property("is_sky", True)` 会被静默忽略（不报错、也不生效）。
- **官方替代**：引擎自带 **HDRIBackdrop** 插件（`Engine/Plugins/Runtime/HDRIBackdrop`），
  里面是 `Content/Blueprints/HDRIBackdrop` + `EnviroDome` + `MI_HDRI_Sky`。
  但它的模块类型是 **Editor**（`"Type": "Editor"`，且 `EnabledByDefault: false`），
  更适合编辑器里 look-dev，不适合当运行时/打包依赖。
- **另一条路（可行但没走）**：把等距柱状图转成 `TextureCube`，给 SkyLight 设
  `source_type = SLS_SpecifiedCubemap` + `cubemap`。本机 Python 暴露了
  `TextureCubeArrayFactory` / Interchange 的 cube 工厂节点，但**没有**直接"equirect → cubemap"的工厂，
  要在编辑器里手动转或用 Interchange 管线，成本不划算。
- **结论**：P0 继续用 `SkyAtmosphere`（效果已经够用），HDRI 天空留到"决定上写实资产"时一起处理。
- **出处**：2026-11-22 实测；`Tools/build_level.py::build_sky / make_sky_material`、`HDRIBackdrop.uplugin`

## 40. 体积云要用对路径：`/Engine/EngineSky/VolumetricClouds/…`（我在这上面误判过一次）

- **正确做法（当前采用）**：spawn `unreal.VolumetricCloud`，把组件材质设成
  **`/Engine/EngineSky/VolumetricClouds/m_SimpleVolumetricCloud_Inst`**（注意 **`VolumetricClouds/` 子目录**），
  配合 `SkyAtmosphere` 就是"蓝天 + 白云"。
  ```python
  instance = unreal.load_asset("/Engine/EngineSky/VolumetricClouds/m_SimpleVolumetricCloud_Inst"
                               ".m_SimpleVolumetricCloud_Inst")
  safe_set(component, "material", instance)
  ```
  代价实测：GPU 3.26 → 4.04 ms（≈+0.8 ms），1080p/60 预算内。
- **我踩的坑（记录一下，别再犯）**：一开始写成 `/Engine/EngineSky/m_SimpleVolumetricCloud_Inst`（漏了
  `VolumetricClouds/`），`load_asset` 返回空，日志只有一句 `engine cloud material instance not found`，
  于是**误判成"引擎没带体积云材质"**，转去试 `BP_Sky_Sphere`（得到永久黄昏色）和云板（得到灰天花板），
  最后退回纯 `SkyAtmosphere`。
  **正确排查姿势**：资产路径不确定时，先走资产注册表把目录列出来，别拿 `load_asset` 的 null 当结论：
  ```python
  registry = unreal.AssetRegistryHelpers.get_asset_registry()
  registry.scan_paths_synchronous(["/Engine/EngineSky"])
  for data in registry.get_assets_by_path("/Engine/EngineSky", recursive=True):
      unreal.log("%s (%s)" % (data.package_name, data.asset_class_path.asset_name))
  ```
- **另外两条被否掉的路线**（都实测过，确实更差）：
  - `BP_Sky_Sphere`：不跟随平行光（蓝图的 Directional Light 变量没暴露给 Python），永远渲染成黄昏色；
  - 用 `M_Sky_Panning_Clouds2_Inst` 铺一块 9 km 云板：材质是给天穹用的，渲染成不透明灰板，把天空和阳光都挡掉。
- **出处**：2026-11-22 实测；`Tools/build_level.py::build_clouds / build_sky_sphere / build_cloud_plane`

## 41. UE 5.8 编辑器自带 MCP 服务端：加 `-ModelContextProtocolStartServer` 就能用 HTTP 驱动

- **背景**：`@local/unreal-mcp` 这个 DSH bundle 指向 `http://127.0.0.1:8000/mcp`，但默认启动的编辑器**不监听 8000**，
  于是这个会话里根本没有 UE 工具（`failOnStartupError` 只是不报错，不会自动拉起引擎侧服务）。
- **正确启动方式**（二选一）：
  - 启动参数：`UnrealEditor.exe <uproject> -ModelContextProtocolStartServer -ModelContextProtocolPort=8000`
  - 或者 项目设置 → 插件 → Model Context Protocol → **Auto Start Server**
- **不需要 DSH 的 MCP 客户端也能用**：服务端是标准 MCP Streamable HTTP，直接用 PowerShell 发 JSON-RPC 即可
  （`Tools\mcp.ps1`）：`initialize` → 拿 `Mcp-Session-Id` 响应头 → 带这个头发 `tools/call`。
- **调用约定（容易踩）**：
  - 元工具是 `list_toolsets` / `describe_toolset` / `call_tool`；
  - `call_tool` 的 `arguments` 要写成
    `{"toolset_name":"SlateInspectorToolset.SlateInspectorToolset","tool_name":"Snapshot","arguments":{...}}`，
    `tool_name` 用**短名**（`Snapshot`）；写全名会报 `Unknown tool`；
  - PowerShell 传 JSON 时引号会被吞，最稳的是**把 JSON 写进文件再 POST**（`Tools\mcp.ps1 -ArgsFile`）。
- **SlateInspectorToolset 用法**：`Snapshot` 只给顶层窗口（depth 0），要看面板内部必须先
  `Observe(ref=<窗口ref>, maxDepth=30)`，再 `Snapshot(ref=<同一ref>)`；点击用 `Click(ref=...)`，
  比坐标点击可靠得多。坐标是**逻辑像素**，本机 100% 缩放时与物理像素一致（可用 `GetWindowRect` 校验）。
- **已知限制**：Fab 面板是 CEF 网页（Slate 里只有一个不透明 webview 控件），`Snapshot` 看不到页面内部控件，
  页面内的按钮只能用坐标点击；Fab 插件也没有任何 Python 接口（`FabSubsystem`/`FabBrowser` 都不存在）。
- **Fab 插件的登录**：浏览器里登录过 Fab 网站**不会**同步给编辑器插件（插件走 EOS）。未登录时日志会出现
  ```text
  LogFab: Error: Login failed - error code: EOS_InvalidAuth
  LogFab: Error: User auth token is invalid - unable to get auth token
  ```
  但**实测免费资产不需要登录也能「添加到项目」**：面板里点它就会下载并落到 `Content/<资源名>/`，
  日志结尾是 `LogFab: Display: Fab workflow completed for asset <guid>`。
  需要登录的是"购买/加入库"那类动作；登录入口是面板右上角头像 → 登录 → Epic 授权页（会显示当前浏览器已登录的账号）→ 确认。
- **Megaplants 落地形态**：Megaplants 不是普通静态网格，而是 `SKM_*`（骨骼网格）+ `PVE_*`（Procedural Vegetation
  Editor 实例）+ `MI_*_Foliage` 材质 + `T_*_CA/NT` 贴图，落在 `Content/Megaplant_Library/<Plant>/`；
  要摆进关卡得用 `SkeletalMeshActor`（或 PVE 插件），不能当 StaticMesh 用。
- **出处**：2026-11-22 实测；`Tools/mcp.ps1`、`Tools/ui.ps1`、`Engine/Plugins/Fab`、`Engine/Plugins/Experimental/ModelContextProtocol`

## 42. Fab 插件装 Megascans 表面的三种结局（成功 / 报错 / 静默无操作）

同一天、同一套操作，装了三个表面材质，结果不一样：

| 资产 | 日志 | 结果 |
| --- | --- | --- |
| Mossy Stone Walkway | `Fab workflow completed` + 弹出**保存内容**对话框 | ✅ 成功，磁盘出现 `MI_*` + 4K 贴图（50 MB） |
| Roof Tiles | `Error: Failed to import Megascan asset: tk4gcgldy` + `workflow cancelled` | ❌ 插件导入失败 |
| Red Roof Tiles | `Fab workflow completed`，`Content/Fab/Materials already exists` | ❌ 什么都没写 |

- **成功的那次关键动作**：资产先在「添加到我的库」，再点「添加到项目」；导入完成后编辑器弹
  「保存内容」对话框，**必须点「保存选中」**资产才落到磁盘（否则只在内存里，`Get-ChildItem` 看不到）。
- **静默无操作那次**：日志照样打 `completed`，但 `Content` 文件数不变——不要只看日志，要核对磁盘。
- 结论：**Fab 插件的 Megascans 导入不稳定**。稳妥路线是网页下载 `纹理集`（texture set）zip，
  再用 Python 导入（能完全绕开插件的导入器），代价是要自己建材质。
- **出处**：2026-11-22 实测；`Content/Fab/Megascans/Surfaces/…`、`Saved/Logs/LingXuJie.log` 的 `LogFab` 行
- **补充（同日实测，这条最实用）**：Fab 详情页的「添加到项目」按钮 **Y 坐标会变**——带「质量」下拉的页面
  按钮在窗口内 y≈421（屏幕 y≈789），不带下拉的页面在 y≈354（屏幕 y≈747）。按固定坐标点会**打空且无任何报错**，
  表现就是"点了没反应、日志也没有 Add listing"。判断方法：先截图看详情页右侧有没有「中质量/高质量」那行。
  按这个规律修好坐标后，Megaplants Bracken Fern 一次成功（`Content/Megaplant_Library/Plant_Bracken_Fern`，72 个文件）。
- **再补充（同日晚）**：即使坐标正确，**同一个按钮也可能偶发不响应**（点「添加到项目」后日志里既没有
  `Add listing to project` 也没有报错）。同一天的成功/失败统计：Megaplants 类 **2 次全成**
  （Bulrush 40 文件、Bracken Fern 72 文件），Megascans 表面/经典 3D 植物 **5 次里只成 1 次**
  （Mossy Stone Walkway），其余全是"报错"或"静默无操作"。
  结论：**别把 Fab 插件当可靠下载器**，要批量拿资产就走网页 + Python 导入。

### 42.1 更正：所谓"静默无操作"是**检查太早**，资产其实稍后才落盘

- 先前记的"Roof Tiles / Red Roof Tiles 什么都没写"**是错的**。半小时后再看，两个表面都在：
  `Content/Fab/Megascans/Surfaces/Roof_Tiles_tk4gcgldy`（48.3 MB）与 `Red_Roof_Tiles_tfqnfggs`（24.3 MB），
  各含 `MI_*` + 2K 的 B/N/ORM。
- **教训**：Fab 下载/解包是异步的，日志的 `workflow completed` **不等于**磁盘就绪；
  不要在 30 秒内用文件数判断成败，至少等几分钟或看 `Content/Fab/Megascans/Surfaces/` 下是否出现新目录。
- 目前手上的官方表面：`Mossy_Stone_Walkway`（4K）、`Roof_Tiles`（2K）、`Red_Roof_Tiles`（2K）。

### 42.2 真正的元凶：Select a version 模态框 + 聊天窗口遮挡

- 点「添加到项目」后，**部分资产会再弹一个 `Select a version` 模态框**（下拉默认 5.8，按钮 `取消` / `添加到项目`）。
  模态框一开，后续所有点击都被它吃掉——表现就是"点了没反应、日志里连 `Add listing` 都没有"。
- 更坑的是：这个模态框的主按钮在面板右侧，**如果窗口被别的窗口（比如 DSH 聊天窗）盖住，
  点击会打到上层窗口上**，同样毫无反馈。
- **排查口诀**：点了没反应时，**先截图看有没有模态框、模态框按钮是否被别的窗口挡住**。
  `GetWindowRect` 列出所有可见大窗口的坐标，就能判断重叠。
- 处理这两点后，`Megasplants: Giant Bamboo` 一次成功（`Content/Megaplant_Library/Tree_Giant_Bamboo`，37 个资产）。

## 43. 编辑器非正常关闭后弹「恢复包」对话框：卡住的 MCP 也是它

- **症状**：编辑器崩溃/被强杀后重启，会弹「恢复包」模态框（列出 `MI_/SM_/T_` 自动保存包，
  按钮 `恢复选中项` / `跳过恢复`）。**这是模态框，会把 MCP 的 Slate/编辑器调用一起堵住**——
  表现是脚本"卡住无输出"，而不是报错。
- **处理**：截图确认对话框 → 点表头复选框全选 → 点 `恢复选中项`。实测恢复出了整套
  Megascans `Tundra Grass`（`FT_*` 9 个 + `MI_*` + `SM_*` + 2K 贴图），文件数从 475 → 501。
- **教训**：agent 驱动编辑器时，**任何模态框都会阻塞后续所有自动化调用**。脚本超时/无响应时，
  第一件事是截图看有没有对话框（Fab 的 `Select a version`、恢复包、保存内容都是这一类）。
- **出处**：2026-11-22 实测；`Content/Fab/Megascans/Plants/Tundra_Grass_wk2oaeyqx`

## 44. 想用 Instanced Foliage 做草皮？Python 这条路是堵的

- `unreal.InstancedFoliageActor` 在 Python 里存在，但 **`spawn` 返回 None**（不能这样创建）；
- `unreal.Actor` **没有 `add_instance_component`**（`AActor::AddInstanceComponent` 没暴露给 Python），
  所以也没法新建一个 `InstancedStaticMeshComponent` 挂到 Actor 上；
- `unreal.EditorFoliageSubsystem` **不存在**（`hasattr` 为 False）。
- **可行替代**：用 `fts_*`（FoliageType）+ 在**编辑器里手动画**，或者用 MCP 的 BlueprintTools
  生成一个"根组件是 ISM/HISM"的蓝图 Actor，再在世界里摆那个蓝图。
- 当前状态：草地仍按"每个草丛一个 StaticMeshActor"摆（48 个），非官方植被已全部拆除，
  场景 draws 262 → 233。等做出 ISM 蓝图后再合并。
- **出处**：2026-11-22 实测；`Tools/build_level.py::build_grass`

## 45. Instanced Foliage 的替代方案：用 SubobjectDataSubsystem 造一个带 ISM 的蓝图

- 上一节说 Python 走不通，但**有一条路是通的**：先做一个"根组件是 `InstancedStaticMeshComponent`"的
  蓝图资产，再在世界里 spawn 这个蓝图、拿组件加实例（`InstancedStaticMeshComponent.add_instance(t, True)`
  是暴露的）。
- 造蓝图的关键 API（`Tools/make_grass_bp.py`，幂等，跑一次即可）：
  ```python
  factory = unreal.BlueprintFactory(); factory.set_editor_property("parent_class", unreal.Actor)
  bp = asset_tools.create_asset("BP_GrassField", "/Game/Props", unreal.Blueprint, factory)
  sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
  handles = sds.k2_gather_subobject_data_for_blueprint(bp)
  params = unreal.AddNewSubobjectParams()
  params.set_editor_property("parent_handle", handles[0])
  params.set_editor_property("new_class", unreal.InstancedStaticMeshComponent)
  params.set_editor_property("blueprint_context", bp)
  handle, fail = sds.add_new_subobject(params)
  unreal.BlueprintEditorLibrary.compile_blueprint(bp)
  unreal.EditorAssetLibrary.save_asset("/Game/Props/BP_GrassField", False)
  ```
- **坑**：`add_new_subobject` 的 `fail_reason` 返回的是**空对象**（`str()` 为空但真值为真），
  用 `if fail_reason:` 会误判成失败；要用 `if str(fail_reason).strip():`。
- **效果**：48 丛草合并成 1 个 actor / 1 个 draw call；关卡 actors 358 → 144，draws 233 → 145。
- **出处**：2026-11-22 实测；`Tools/make_grass_bp.py`、`Tools/build_level.py::build_grass`
- **补充（Wood Planks，同日）**：同一个插件对某些表面**稳定失败**——连续两次 `Error: Failed to import Megascan asset:
  throbglfw` + `workflow cancelled`，等 150 秒也没有内容。而 Roof Tiles 报同样的错却最终落盘。
  所以这两类要分开看：**"报错后取消了"不会自愈，"报错但最终完成"才有救**。
  可靠做法：走网页下载 `纹理集`（texture set）→ `Tools/import_fab.py` 已支持纯贴图包（import_texture_set）。

## 46. 编辑器不用关了：在编辑器内部跑生成器（控制台 `py`）

- 日常闭环以前是"关编辑器 → `BuildLevel.ps1`（另起 commandlet）→ 再开"，很折腾。其实编辑器**自己**就能跑：
  底部状态栏的 **Cmd 控制台**输入 `py "C:/<path>/Tools/build_level.py"` 回车即可，生成的关卡会直接刷新。
- 已封装：`Tools\RebuildInEditor.ps1`（自动定位编辑器窗口 → 点控制台 → 粘贴 `py "<script>"` → 回车 →
  轮询日志里的 `Done. N actors`）。实测在编辑器常开状态下重建成功（144 actors，`save_current_level -> True`）。
- **注意**：控制台输入框在窗口内相对位置约 (宽×0.334, 底-13)；窗口一旦被别的窗口挡住或被模态框阻塞，
  这个脚本也会点不到——先确保编辑器在最前、没有对话框。
- **C++ 编译仍然需要关编辑器**（Live Coding 互斥体），但 **Python 生成关卡不需要**。
- **出处**：2026-11-22 实测；`Tools/RebuildInEditor.ps1`

## 47. 编辑器开着时游戏会掉到 15 fps —— 不是材质问题，是 GPU 争抢

同场景、同 720p，三组实测（`stat unit`）：

| 状态 | Frame | GPU | Draw | 显存 |
| --- | --- | --- | --- | --- |
| 编辑器可见 | 64.03 ms | 62.50 ms | 61.7 ms | 3.90/6.96 GB |
| 编辑器最小化 | 57.55 ms | 56.02 ms | 57.5 ms | 3.90/6.96 GB |
| 编辑器完全关闭 | **7.44 ms** | 6.55 ms | 7.43 ms | 3.90/6.96 GB |

- **4K Megascans 贴图不是瓶颈**：显存只用 3.9 GB；降成 2K 也救不了 8 倍差距。
- 原因：编辑器进程即使最小化也持有 D3D12 设备、Lumen/Nanite 场景与着色器编译队列，
  游戏一启动就在抢 GPU。
- **策略**：`Tools\RunGame.ps1` 现在会自动最小化编辑器并在结束后恢复（能省一点，但**不够**）；
  **要测真性能就必须完全关掉编辑器**，日常改资产/看效果时开着无妨。
- **出处**：2026-11-22 实测；`Tools/RunGame.ps1`

## 48. 用方块拼中式坡屋顶：坡长/落差/roll 符号必须按几何算

- 用 `Cube` 拼双坡顶时，三处容易错（都实测踩过）：
  1. **坡长**：`slab_len = (depth/2 + eave) / cos(pitch)`；用 `depth * 0.62` 会短，脊部出现裂缝；
     用 `depth * 0.78` 又太长，两片交叉成"蝶形"。
  2. **位置**：坡板中心放在 `y = ±half_depth/2`、`z = ridge_z - drop/2`，其中 `drop = half_depth * tan(pitch)`。
  3. **roll 符号**：`roll = +sign * pitch` 才是"外侧低、中间高"的正确双坡；写反会得到两翼上翘。
- 山墙两端目前是**开口**的（没有三角形填充墙），从侧面看会看到屋面内侧——下一步补"山墙"或用
  `Plane`/自定义网格做三角面。
- **出处**：2026-11-22 实测；`Tools/build_level.py::build_house`

## 49. 程序化曲面屋顶（ProceduralMeshComponent）第一次尝试是坏的

- 方案：造 `BP_CurvedRoof`（根组件 `ProceduralMeshComponent`，用 SubobjectDataSubsystem 建，和
  `BP_GrassField` 同法），再在 Python 里 `create_mesh_section(0, verts, tris, normals, uvs, [], [], False)`
  喂一个"凹曲线 + 四角上翘 + 檐口外张"的网格。
- **实测结果：生成的拓扑是坏的**——视口里出现大块乱飞的平面，房屋被遮住。
  初步判断是顶点/索引顺序或 `Vector2D` 数组类型在蓝图函数调用里被转换出错，
  但没继续深挖（收益不确定，且每次验证要走一遍编辑器重建）。
- **已回退**：`USE_CURVED_ROOF = False`，函数保留备用；当前用方块坡顶（薄板）保证可用。
- **下一步如果还要曲面**：改用 `MeshDescription` 生成真正的 StaticMesh 资产（而不是运行期 PMC），
  这样能离线检查、可复用、也便于做成模块化构件；或者直接买现成中式构件包。
- **出处**：2026-11-22 实测；`Tools/make_roof_bp.py`、`Tools/build_level.py::build_curved_roof`

## 50. 卡通渲染（Toon/Cel Shading）：做过、否掉了、已彻底删除

- 试过一次后处理材质方案（`MD_POST_PROCESS` + `BL_SCENE_COLOR_AFTER_TONEMAPPING`，采样
  `PPI_POST_PROCESS_INPUT0`，只量化亮度并保色相，远处用 `PPI_SCENE_DEPTH` 还原）。
  **技术可行**，但会作废 Megascans 写实质材的价值，与"官方素材优先、写实路线"直接冲突。
- **决定：不再考虑**。代码（`make_cel_material` / `build_cel_shading` / `CEL_SHADING`）与
  `M_CelShading*` 资产已从工程删除（用编辑器 API `EditorAssetLibrary.delete_asset` 删，
  运行中直接 `Remove-Item` 会被文件锁挡住）。
- 两条仍然有用的工程经验：
  1. `unreal.BlendableLocation` 没有 `BL_AFTER_TONEMAPPING`，正确名是 `BL_SCENE_COLOR_AFTER_TONEMAPPING`；
     枚举取不到时用候选名逐个 `hasattr` 兜底最省事。
  2. **材质已存在时 `does_asset_exist` 为真，改代码不会重建**——改材质名强制重建，否则你以为改了其实没生效。
- **出处**：2026-11-22 实测并删除；`Tools/cleanup_cel.py`

## 51. 低完整性沙盒里"点不动编辑器"：UIPI 拦输入；MCP 的 `Windows close` 会把编辑器卡死在模态框上

- **症状**：`Tools\ui.ps1 -Action click` 返回 `clicked x,y` 但编辑器毫无反应；`PostMessage(WM_CLOSE)`
  返回 `False`（`WM_NULL` 却是 `True`）。同一台机器上人手动点同一个按钮就有效。
- **原因**：DSH 在 `workspace-write` 沙盒下，命令进程的完整性级别低于编辑器进程，**UIPI 只放行
  白名单消息**（`WM_NULL` 等），鼠标/键盘注入（`mouse_event`/`SendInput`）和 `PostMessage(WM_CLOSE)`
  一律被丢弃。切到 `danger-full-access` 后同一份脚本立刻生效——这就是上个会话"控制台 py 命令
  一直点不进去"的真因，不是窗口坐标算错。
- **判断办法**：`PostMessage(WM_NULL)` 成功 + `PostMessage(WM_CLOSE)` 失败 = UIPI 拦截，别再调坐标了，
  要么让沙盒放开、要么请人点。
- **更糟的一半**：**别用 MCP 的 `SlateInspectorToolset.Windows(action=close)` 关编辑器**。它会在游戏线程里
  同步等窗口销毁，弹出的「保存内容」模态框因此**完全不处理输入**（人点和注入都无效），同时 MCP 服务器
  也被挂住（后续 `tools/call` 全部超时）。恢复办法：Task Manager 结束 `UnrealEditor.exe`，或用
  `PostMessage(主窗口, WM_CLOSE)` 让模态框重新可交互后再点「不保存」。
- **正确关闭姿势（有输入权限时）**：
  1. `PostMessage(FindWindow("LingXuJie - 虚幻编辑器"), WM_CLOSE)`；
  2. 等「保存内容」窗口出现，用真实鼠标点**不保存**（那批材质下次 `BuildLevel` 会重新生成）；
  3. 轮询 `Test-NetConnection 127.0.0.1 -Port 8000` 变 False / 资产文件可独占打开，再开始构建。
  编辑器持有时 `Content` 里被它加载过的 `.uasset`（关卡引用的材质/贴图）会**删不掉、改不了**，
  报"文件正由另一进程使用"。
- **出处**：2026-11-22 实测（Mossy Stone 4K→2K 换贴图时连续踩到）。

## 52. UE 5.8 的导入期色彩空间：`TextureFactory.srgb` 没了，`ColorSpaceMode` 又不暴露给 Python

- **症状**：`safe_set(factory, "srgb", True/False)` 报
  `Failed to find property 'srgb' for attribute 'srgb' on 'TextureFactory'`（#38 的老办法在 5.8 失效）。
- **源码**：`Engine/Source/Editor/UnrealEd/Classes/Factories/TextureFactory.h`
  → `UPROPERTY(Transient) ETextureSourceColorSpace ColorSpaceMode;`，旧 bool 已删除。
- **但**：`unreal.TextureSourceColorSpace` 在 Python 里**不存在**，`color_space_mode` 属性也读不到
  （`UPROPERTY(Transient)` 不在 Python 暴露的属性表里），`0/1/2/"Linear"` 全部 `Failed to find property`。
- **可行做法**：导入后 `texture.set_editor_property("srgb", False)` + `EditorAssetLibrary.save_asset()`。
  标志位会**持久化**，下次加载按正确的色彩空间建 SRV（`probe_texture.py` 里重新加载验证过：
  ORM/N 都是 `srgb=False`）。代价是同一会话内的内存实例仍是旧格式。
- **压缩设置相反**：`factory.compression_settings = TC_NORMALMAP / TC_MASKS` **是生效的**
  （法线贴图直接进成 `TC_NORMALMAP`）；但 Python 没有 `update_resource`/`post_edit_change`，
  想把 ORM 换成 `TC_MASKS` 只能改属性 + 保存，**数据不会立刻重压**（uasset 大小不变），
  打包/重导时才按新设置走。Fab 自己装的 ORM 就是 `Masks`，跟它对齐即可。
- **出处**：2026-11-22 实测；`Tools/build_level.py::ensure_megascans_texture`、`Tools/probe_texture.py`

## 53. Fab 的贴图集缓存可以直接复用：绕开 Fab 面板装 2K 版

- **发现**：Fab 插件把下载的 zip 留在 `%LOCALAPPDATA%\Temp\FabLibrary\<uuid>\<asset>_<id>_<res>_<quality>.zip`，
  里面有 `Textures/T_<id>_2K_{B,N,ORM}.png` + `.gltf` + `.json`（`json` 里带 `physicalSize`）。
  上个会话辛苦找的「中质量 2K 苔石」其实**早就在本机**：`mossy_stone_walkway_ue4rcgxg_2k_ue_mid.zip`。
- **用法**：解出 PNG 放进 `Assets/Megascans/<name>/`（LFS），`build_level.py` 首次构建时
  用 `AssetImportTask` 导到 `Content/Fab/Megascans/...` 同一层级结构里；**以后重建不再需要网**。
- **注意**：同一素材在 Fab 改版后会换 id（4K 是 `ue4rdbpg`，2K 是 `ue4rcgxg`），
  `json.maps[].physicalSize` 也可能不同（1x2 m vs 2x4 m）→ 平铺系数要按物理尺寸换算。
  这次 4K 是 1x2 m、2K 是 2x4 m，所以 `tiling 6.0 → 3.0`（一半的次数覆盖同样物理尺寸）。
- **出处**：2026-11-22 实测；`Assets/Megascans/mossy_stone_walkway_2k/`、`Tools/build_level.py::megascans_stone_paths`

## 54. 想让画面变暖，别去改平行光的颜色：SkyAtmosphere 按太阳颜色整体缩放天空

- **症状**：把主光从白改成暖橙 `Color(255,198,148)`，强度只降了 8%，画面却整体暗掉约 2 档，
  天空从蓝变成橄榄绿，连实时捕获的 SkyLight 环境光一起变暗。
- **原因**：`SkyAtmosphere` + `atmosphere_sun_light` 是**物理模型**：天空的亮度和色相都按太阳光的
  颜色/强度算。把太阳调成橙色等于把蓝光从光源里拿掉，天空的瑞利散射没有蓝可散 → 天变脏变暗；
  而 SkyLight 开了 `real_time_capture`，它会把这个变暗的天空当成环境光再喂回整个场景，双重变暗。
- **正确做法**（现在采用）：太阳保持**近白**（`(255,243,230)`，只是略微偏暖），把太阳压低到
  仰角 20° 左右让大气自己产生暖色，暖调交给**后处理调色**（white temp / color gain）和雾色。
  `tune_white.png`（白太阳）与 `tune_v3.png`（近白 + 低角度）都是亮的，只有真橙色的那版是暗的。
- **出处**：2026-11-22 实测；`Tools/build_level.py::build_lighting`

## 55. `PostProcessSettings` 的值必须配 `bOverride_` 标志，否则整个 PPV 静默无效

- **症状**：PPV 里设了 bloom 0.8 / vignette 0.25 / AO 0.8 / white temp，截图里**一点变化都没有**，
  但日志里没有任何报错。视觉 pass v1 的"后处理"调整其实从来没生效过。
- **定位**：用 MCP 的 `ObjectTools.get_properties` 读 `PostProcessVolume.Settings`，看到
  `bOverride_WhiteTemp` / `bOverride_ColorSaturation` / `bOverride_ColorContrast` /
  `bOverride_ColorGain` / `bOverride_BloomIntensity` / `bOverride_VignetteIntensity` /
  `bOverride_AmbientOcclusionIntensity` **全是 false**，而对应的值是设好的。
- **原因**：`FPostProcessSettings` 是"每项一个 override 开关"的结构；渲染器只看带 override 的项，
  而 Python 的 `set_editor_property("white_temp", ...)` 只写值、不打开开关，也不报错。
- **修法**：值 + 开关一起设。Python 里开关名就是 `override_` + 蛇形属性名
  （`override_white_temp` / `override_bloom_intensity` / `override_color_gain`，实测全部对得上）：
  ```python
  if safe_set(settings, name, value):
      safe_set(settings, "override_" + name, True)
  ```
  见 `build_level.py::set_grade()`；设完再 `volume.settings = settings`。
- **出处**：2026-11-22 实测；`Tools/build_level.py::set_grade / build_lighting`

## 56. 平面上"不同颜色的矩形"永远是一条色带 —— 地面细节不要靠叠板子

- **症状**：草地上一块泥土矩形、石板上一条泥土带，无论怎么调颜色/厚度，看着都像"贴了一条纸带"。
  用户连提了三次，我前两次都在改**铺装的边**（抬高台、压边石、边缘碎石），越改越丑。
- **原因**：人眼对**直的色界**极其敏感。只要两块面是"不同材质 + 矩形 + 直边"，边界就一定跳出来；
  而"边缘加东西"（压边石、撒碎石）只是又加了一条窄的异色带，问题没消失、还多了一条。
- **无效尝试**（都实测过）：12 cm 抬高台 → 侧面是一圈拉伸的石头竖条；30 cm 压边石 → 一条细石带；
  边缘碎石 → 一排黑箱子；`u*(1-u)+v*(1-v)` 羽化材质 → 编译可用，但 8 m 见方的块在这个尺度下仍是带子。
- **正确方向**：让边界**不存在**，而不是给它加装饰：
  1. 能减少就减少——把"泥土路"整块关掉，只留「石板 / 草地」两种面，画面立刻干净；
  2. 真要混合，只能用**能混材质的载体**：Landscape 图层混合、逐顶点混合材质、或软边遮罩的贴花
     （前提是遮罩来自程序化渐变，**不能**拿无 alpha 的 JPG 当遮罩，见 #57）；
  3. 若必须保留两块不同面，就让轮廓**参差**（多块斜着拼）而不是一个大矩形。
- **出处**：2026-11-22 实测；`Tools/build_level.py`（VILLAGE_EARTH / kerb_ring / build_edge_gravel /
  make_feathered_material）

## 57. JPG 贴图没有 alpha：拿它当贴花遮罩 = 实心色块

- **症状**：地面上一大片硬边色块/色带，像贴纸。
- **原因**：`M_Decal_Moss/M_Decal_Dirt` 用贴图的 alpha 当不透明度，而 Poly Haven 的 diffuse 是 **JPG**，
  没有 alpha 通道 → 不透明度恒为 1 → 每个 decal 都是一整块实心矩形（而且尺寸修对之后更明显）。
- **修法**：贴花的不透明度必须来自**程序化遮罩**（`MaterialExpressionRadialGradientExponential`、
  距离场、或噪声纹理），不能用无 alpha 的彩色贴图；在换成软边之前，`SPAWN_DECALS=False`。
- **附带**：`DecalComponent.DecalSize` 单位是**厘米**，表里写"米"不换算会得到 6 cm 的小点，
  看起来像"decal 没生效"。
- **出处**：2026-11-22 实测；`Tools/build_level.py::make_decal_material / build_decals`

## 58. 切到别的关卡再切回来，程序化地面会变成一片白（材质还在，但渲染成 WorldGrid）

- **症状**：为了看导入包的 Demo 图，用 MCP `SceneTools.load_level` 加载了
  `/Game/GeonchunmunComplex/Maps/Demo_GeonchunmunComplex`，再切回 `LingXuJie` 后，
  **整片草地变成白色带网格**（典型的 WorldGridMaterial），铺装/建筑/植被都正常。
- **排查**：`find_actors "TERRAIN"` → 读 PMC 的 `OverrideMaterials` → 材质引用**仍然正确**
  （`/Game/Materials/M_Terrain_Grass`），uasset 也在磁盘上；日志里材质编译已完成（不是编译中）。
  说明几何与引用都在，是**材质资产本身在被重新载入后丢了贴图/图形状态**。
- **修法**：直接重建关卡（`Tools\RebuildInEditor.ps1`）。`build_terrain` 每次都会用
  `rebuild=True` 重新生成 `M_Terrain_Grass`，重建后立刻恢复绿色。
- **规矩**：**别为了看素材 Demo 图切走当前关卡**。要看就把 Demo 图在**另一个编辑器实例/打包版**里看，
  或者看完立刻重建一次；本工程的关卡本来就是脚本生成的，切回来不一定等于原样。
- **附带**：`py` 控制台粘贴偶尔会把杂字符带进命令（实测出现过 `Cmd: kcgpy "..."`），
  粘贴前先 `^a` + `Del` 清空，再粘。
- **出处**：2026-11-23 实测；`Tools/build_level.py::build_terrain`、MCP `SceneTools.load_level`
## 59. 程序化地面不进存档：关掉编辑器 / 直接 RunGame 就没地（黑地或白格）

- **症状**：RebuildInEditor.ps1 之后编辑器里草地正常；关掉编辑器重新打开，或者直接
  `Tools\RunGame.ps1` 从磁盘起游戏，**地面消失**（编辑器视口是白格 WorldGrid，游戏里是黑地）。
- **根因**：`UProceduralMeshComponent` 的 section（顶点/三角/法线）不是 UPROPERTY，**不参与序列化**。
  `create_mesh_section()` 建出来的几何只活在当前进程内存里，`save_current_level()` 存不下去，
  重新加载就是 `get_num_sections() == 0`。材质引用、actor 位置、日志都正常，所以很容易误判成"材质丢了/编译中"。
- **修法**：地面改成 `ALXJGround`（`Source/LingXuJie/LXJGround.*`）：高度场参数（centre/size/step/flat_areas）
  是 UPROPERTY（跟着关卡存），几何在 `PostRegisterAllComponents()`（冷加载与生成都走这条路）+
  `OnConstruction()` + `BeginPlay()` 里重建。关卡里只存几 KB 参数，编辑器/游戏都有地。
- **验证**：`UnrealEditor-Cmd ... -run=pythonscript -script=Saved\probe_ground.py` 冷加载后
  `sections=1 / 10201 verts / 20000 tris`；`RunGame.ps1` 出生点脚下就是石板路。
- **出处**：2026-11-23；`Tools/build_level.py::build_terrain`、`Source/LingXuJie/LXJGround.cpp`

## 60. Python 里把 ProceduralMesh 烘成 StaticMesh 资产会把编辑器打崩

- **症状**：为了绕开 #59，试着用 `StaticMeshDescription` 手搓一个地形 uasset：
  `create_polygon()` 一调就 **Assertion failed: (Index >= 0) & (Index < ArrayNum)**（`MeshDescriptionBase::CreatePolygon`），
  编辑器 Critical error 直接退出（进程没了，不是弹窗）。
- **根因**：5.8 的 Python 绑定里，`UStaticMesh::create_static_mesh_description()` 造出来的描述**没有 polygon group 容器**
  （`create_polygon_group()` 的返回值用不了），而且**法线根本没有 setter**（`set_vertex_instance_normal` 不存在），
  就算不崩也做不出能看的地形。
- **规矩**：不要在 Python 里手搓 MeshDescription。要持久化网格走 C++（`FMeshDescription` /
  `UStaticMesh::BuildFromMeshDescriptions`），或者像 #59 那样运行时重建。
- **附带**：崩过的编辑器下次启动会弹「恢复包」模态框挡住 MCP；处理办法见 #42/#43——把模态框窗口拉高露出
  「跳过恢复」再点（直接发 ESC 无效）。
- **出处**：2026-11-23 实测
## 61. 崩溃之后「Crash Reporter」窗口会悄悄挡住一切自动化（看着像"脚本没反应"）

- **症状**：`py` 脚本打进控制台后日志一行都没有；`RebuildInEditor.ps1` 一直等到超时；MCP 调用挂住；
  点控制台没反应。日志里最后一条是我们自己发出去的命令，所以特别容易误判成"脚本卡了/参数不对"。
- **真相**：编辑器进程已经崩了（`Saved\Crashes\UECC-Windows-<hash>_0000\` 有崩溃目录），
  屏幕上留着一个 `LingXuJie Crash Reporter` 窗口（Close Without Sending / Send and Close / Send and Restart）。
  它**不写 LingXuJie.log**，所以从日志完全看不出来。
- **处置**：用 `Tools\EditorGuard.ps1`：
  - `-Action check`：打印 editor 进程 / MCP 8000 端口 / Crash Reporter / 恢复包 / 最近崩溃目录，健康时退出码 0；
  - `-Action dismiss`：点掉 Crash Reporter（**Close Without Sending**，不上传）和「恢复包」（跳过恢复）；
  - `-Action restart`：先 dismiss，再以 `-ModelContextProtocolStartServer` 重启编辑器并等端口（`-ApplyLayout` 才会重摆窗口）。
- **实现坑**：Crash Reporter 是 Qt 窗口，**UIAutomation 找不到按钮**（`FindFirst` 返回 null），只能走坐标兜底：
  左下角 `(left+100, top+height-26)`。恢复包同理：先把窗口撑到 1180x1010，再点右下角
  `(left+width-72, top+height-33)`。
- **已内置**：`RebuildInEditor.ps1` 开跑前先 `check`（有模态框就先 `dismiss`），等待期间发现 `UnrealEditor`
  进程消失就自动 `restart` 并以退出码 1 结束。
- **常驻模式**：`-Action watch` 每 20 s 自检（`-IntervalSeconds` 可调），出现模态框**立刻点掉**；
  **只在检测到新崩溃目录时**才自动重启（人手关闭的编辑器不会被抢回来），最多重启 3 次；
  pid 写进 `Saved\editor_guard.pid`，`-Action stop` 停掉。会话里用后台任务起：
  `powershell -ExecutionPolicy Bypass -File Tools\EditorGuard.ps1 -Action watch`。
- **启动方式**：必须走 `powershell -ExecutionPolicy Bypass -File ...`；直接 `& Tools\EditorGuard.ps1` 会因执行策略被拒
  （"在此系统上禁止运行脚本"）。

## 62. 编辑器内重建会复用旧的 Python 模块（改了代码，日志却还是老行为）

- **症状**：改完 `village_house.py` / `build_world.py`，用 `Tools\RebuildInEditor.ps1` 重建，日志却还是
  旧格式（例如改了「2 大 2 小」仍然打出 4 条 `17 pieces`，没有 `(2 x 3 bays ...)`）。
- **根因**：`RebuildInEditor.ps1` 是在**同一个编辑器进程**里反复 `py "Tools/build_level.py"`，
  而 `build_level.py` 里 `from build_world import ...` 命中 `sys.modules` 缓存 —— 上一次 import 的模块对象
  一直活着，磁盘上的新代码根本没被执行。换 headless（`BuildAll.ps1`）或重启编辑器才会生效。
- **修法**：`load_p0_world()` 在 import 前把自家模块从缓存里踢掉：
  ```python
  for name in ("build_world", "village_house"):
      sys.modules.pop(name, None)
  ```
- **验证**：改完立刻 `RebuildInEditor.ps1`，日志出现新格式
  `house at -1400, -9400: 19 pieces (2 x 3 bays, 492 x 737 cm)`。
- **出处**：2026-11-23；`Tools/build_level.py::load_p0_world`、T2 尺寸分层那一轮

## 63. 重建后立刻截图，新 actor 可能只有影子没有网格

- **症状**：`RebuildInEditor.ps1` 返回成功后马上 `CaptureViewport`，画面里房子**不见了**，
  地上却留着房子的影子；再等几秒重截就正常。
- **根因**：重建是「清空 + 重新 spawn」，新 actor 的渲染资源（Nanite/Lumen 的代理、网格流送）要过一下才就绪，
  而阴影代理先建好了 —— 所以出现"有影无物"。
- **规矩**：重建/重开关卡之后**等 5 秒以上再截图**；截出来缺东西先重截一次，别急着断定是生成逻辑坏了。
- **出处**：2026-11-23，T2 院墙那一轮

## 64. Python 建材质：Clamp 节点输入引脚连不上 → 材质编译失败（地面变棋盘格）

- **症状**：新建的 `M_Terrain_Blend` 一挂上地形，地面立刻变成白格 WorldGrid（默认材质）；
  日志里是 `Failed to compile Material for platform PCD3D_SM6, Default Material will be used in game`
  加一行 `(Node Clamp) Missing Clamp input`。
- **根因**：5.8 的 Python 绑定里 `connect_material_expressions(..., "Input")` 对 `MaterialExpressionClamp`
  不生效（引脚名对不上）。同样的写法对 `LinearInterpolate` 的 `A/B/Alpha`、`Multiply/Add/Subtract/Divide`
  的 `A/B`、`ComponentMask` 的空引脚名都没问题。
- **修法**：用 `MaterialExpressionMax(x, 0)` + `MaterialExpressionMin(x, 1)` 两步夹取，A/B 引脚稳定可用。
- **附带（坑中坑）**：
  1. 材质已存在时工厂函数默认直接复用旧资产 —— 改了材质代码必须传 `rebuild=True`（内部先 `delete_asset`），
     否则你看到的永远是最早那版。
  2. 日志里的 `Failed to compile` 会保留历史行，**判断当前是否失败要看时间戳最后一条**，
     不要被十几分钟前的旧失败误导（这一轮就被误导过一次）。
- **出处**：2026-11-23，T3 地面分层；`Tools/build_level.py::make_ground_blend_material`
- **规矩**：长操作（编译/重建/游戏/批量 py）**前后各跑一次 `EditorGuard -Action check`**；
  "日志没有输出 / 没有 Done" 时**先查崩溃**，不要闷头重试。
- **出处**：2026-11-23（agent 自己在 Python 里烘 StaticMesh 撞断言，崩溃窗口开着没人处理，后面 18 分钟都在"等一个死进程"）

## 65. `CaptureViewport` 的 `captureTransform` 不改编辑器视口相机 —— 截图好看，人的屏幕还是黑的

- **症状**：用 MCP `EditorAppToolset.CaptureViewport` 带 `captureTransform` 截图，
  出来的图是漂亮的兰州街景；但人切到编辑器，视口里还是建筑内部一片黑。
- **根因**：`captureTransform` 只对**那一次渲染**生效，它创建一个临时相机拍一张图，
  **完全不移动编辑器视口相机**。两次犯同一个错，都是拿截图当"视口已恢复"的证据。
- **修法**：真正移动相机的是编辑器子系统：
  ```python
  subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
  subsystem.set_level_viewport_camera_info(location, rotation)
  # 读回来确认
  loc, rot = subsystem.get_level_viewport_camera_info()
  ```
  已封装 `Tools/reset_view.py`，用 `RebuildInEditor.ps1 -Script Tools/reset_view.py` 调用。
- **验证也要换**：`Tools/grab_editor_window.py` 走 Windows API 直接抓编辑器窗口，
  **看到的就是人看到的**。MCP 渲染的图不能用来证明"视口是什么样"。
- **出处**：2026-11-26，兰州城做图；`AGENTS.md` 规则 3b

## 66. PowerShell 把目录名里的 `[Server]` 当成通配符字符集 —— 明明有文件却报"0 个"

- **症状**：`Get-ChildItem '源码\[Server]Agent'` 报 0 个文件，但源码里明明有 55 个。
- **根因**：PowerShell 路径里的方括号是**字符集通配符**，`[Server]Agent` 表示
  「S/e/r/v/e/r 中任一字符 + Agent」，所以它去找 `SAgent`、`eAgent`… 而真实目录叫 `[Server]Agent`。
- **修法**：查这类目录一律用 `-LiteralPath`：
  ```powershell
  Get-ChildItem -LiteralPath '源码\[Server]Agent'
  ```
  或者干脆用 Python 的 `os.walk` / `os.listdir`（没有通配符语义）。
- **教训**：任何带 `[ ] * ?` 的路径都要当心。这个坑让我误判"服务端源码是空的"，
  差点得出完全错误的结论。
- **出处**：2026-11-26，查台服源码的服务端目录

## 67. PIE 开着时 `new_level` 返回 False，重建报 `Could not create or load`

- **症状**：`build_level.py` 执行到 `new_level` 返回 `False`，
  `RuntimeError: Could not create or load /Game/Maps/LingXuJie`。
- **根因**：PIE（Play In Editor）运行时关卡处于被占用状态，不能新建/替换。
- **修法**：重建前先 MCP `StopPIE`（`EditorAppToolset.StopPIE`，参数传 `{}`）。
- **注意**：这个错在 `AGENTS.md` 规则 8 里写过，但实际执行时还是会忘 ——
  **重建脚本应该在开头自己检查并 StopPIE**，不要指望调用者记得。
- **出处**：2026-11-26，兰州城重建；`AGENTS.md` 规则 8

## 68. 墨香 OBJ 的坐标：导出写 `(x, z, height)`，UE 导入会**取反 Y**

- **症状**：按 OBJ 文件里的坐标去摆相机，永远对不上城市的位置；按顶点范围算出来的"城中心"
  在引擎里是空地，算出来的"空地"是建筑内部。
- **根因**：`Tools/build_map_obj.py` 把墨香坐标 `(wx, wy, height)` 写成 OBJ 的
  `v wx wy height`，但**墨香是 Z 向上、UE 是 Z 向上但 Y 取反** ——
  UE 的 OBJ 导入器会把 OBJ 的 Y 变成 `-Y`。
  所以：**OBJ 里 Y 为正的区域 → 引擎里 Y 为负。**
- **修法**：读 OBJ 算位置时，最后输出 UE 坐标要 `y_ue = -y_obj`。
  `Tools/find_open_spot.py` 就是栽在这里，第二轮才修正。
- **记忆点**：墨香地图 51,200 cm 见方；地形 Y 在 UE 是 `-51200..0`；
  兰州建筑 OBJ Y 是 `0..46000` → UE `-46000..0`。
- **出处**：2026-11-26，兰州城定位

## 69. MCP 工具的资产参数要完整对象路径，不是资产路径

- **症状**：`StaticMeshTools.is_nanite_enabled(mesh="/Game/Moxiang/SM_Lanzhou_Terrain")` 报
  `Parameter error: ... is not a valid object path for property 'mesh'`
- **根因**：这些工具的参数类型是 `unreal.Object` 引用，需要 `/Game/文件夹/资产名.对象名` 格式
- **修法**：
  ```
  错误: /Game/Moxiang/SM_Lanzhou_Terrain
  正确: /Game/Moxiang/SM_Lanzhou_Terrain.SM_Lanzhou_Terrain
  ```
  两者通常同名，但路径里必须出现**两次**
- **出处**：2026-11-26，查地形 Nanite 状态

## 70. 碰撞的正确工具是 generate_convex_collisions，不是关掉 Nanite

- **症状**：之前为了「Nanite 不提供复杂碰撞」，把地形的 Nanite 关掉了
- **根因**：关 Nanite 是治症状。Nanite 的碰撞来自 Fallback 网格
  （`FMeshNaniteSettings.GenerateFallback` / `FallbackPercentTriangles`），
  而引擎另外提供了碰撞生成工具
- **修法**：
  ```
  StaticMeshTools.generate_convex_collisions(mesh)   -> 生成凸包
  StaticMeshTools.remove_collisions(mesh)            -> 清除
  StaticMeshTools.set_nanite_enabled(mesh, True)     -> 保留 Nanite
  ```
  **注意：凸包不适合地形** —— 地形会变成一块大平板。
  地形仍应用 `CTF_USE_COMPLEX_AS_SIMPLE`（本项目已在用）
- **出处**：2026-11-26，读 static_mesh.py 源码

## 71. 三平面材质的 UV 要**除**以米数，不是**乘**平铺次数

- **症状**：三平面材质建好、编译通过、挂上去 —— **地面变成纯色，完全没有纹理**
- **根因**：`WorldPosition` 返回的是**厘米**（比如 x=8950）。
  乘以平铺次数 24 得到 UV = 214,800 —— 贴图被采到极限密度，
  **引擎退化成平均值，看起来就是纯色**
- **修法**：除以「每贴图覆盖多少厘米」：
  ```
  UV = WorldPosition / 600      <- 每 6 米一张贴图
  ```
  **概念转换：不是"重复多少次"，是"每张覆盖多长"。**
- **怎么发现**：接了世界坐标后如果变纯色，**先查除法方向**
- **出处**：2026-11-26，三平面第一次尝试

## 72. 三平面混合权重必须是**归一化比例**，不能是分量之和

- **症状**：三平面看起来"某两个面特别亮、另一个面不见了"，或者混合边界有硬断层
- **根因**：法线分量绝对值相加可能 **> 1**。
  `Lerp` 的 Alpha 超过 1 会被钳制到 1，等于"永远选 B"，混合就失效了
- **修法**：用比例而不是和：
  ```
  错: alpha = |n.x| + |n.y|
  对: alpha = |n.y| / (|n.x| + |n.y|)      <- 恒在 [0,1]
  ```
  **并且分母要加一个很小的 epsilon 防止除零**
  （法线朝正上时 |x|+|y| = 0）
- **出处**：2026-11-26，三平面第一次尝试的第二个错误

## 73. `play_sound_at_location` 的 rotation 是必需参数

- **症状**：`unreal.GameplayStatics.play_sound_at_location(world, sound, location)` 报
  `TypeError: play_sound_at_location() required argument 'rotation' (pos 4) not found`
- **根因**：反射签名里 `rotation` 没有默认值，没有省略它的重载
- **修法**：显式传 `unreal.Rotator(0, 0, 0)`
- **出处**：2026-11-26，音频实测

## 74. 资产工厂类名**有的带 New 有的不带** —— 猜必错

- **症状**：`tools.create_asset(name, path, unreal.SoundClass, unreal.SoundClassFactoryNew())` 报
  `AttributeError: module 'unreal' has no attribute 'SoundClassFactoryNew'`
- **根因**：引擎的工厂类命名不统一，同一个模块里两种风格并存：
  ```
  USoundClassFactory        <- 没有 New
  USoundAttenuationFactory  <- 没有 New
  USoundMixFactory          <- 没有 New
  USoundConcurrencyFactory  <- 没有 New
  USoundCueFactoryNew       <- 有 New
  UMaterialFactoryNew       <- 有 New
  UStaticMeshFactoryNew     <- 有 New
  ```
- **怎么查**：扫引擎源码找真实类名，不要猜：
  ```python
  # 找所有继承 UFactory 的音频相关类
  re.finditer(r'class\s+(?:\w+_API\s+)?(U\w*Factory\w*)\s*:\s*public\s+UFactory', text)
  ```
- **修法**：先 `Tools/list_python_toolset_tools.py` 看有没有现成工具，
  再扫源码确认工厂名，**最后才写代码**
- **出处**：2026-11-26，建音频系统时踩到

## 75. 「名字对不上清单」不是「没人用」的证据

- **症状**：`Content/Moxiang` 里 104 个资产不在导入清单里，看着像旧构建遗留，
  我据此写了「107 个遗留资产待清理」
- **实测推翻**：
  ```
  jp_roof00            -> Texture2D   <- 被 M_LZ_JP_ROOF00 引用
  17_101_stonew01      -> Texture2D   <- 被 M_LZ_17_101_STONEW01 引用
  ```
  **它们是**贴图**，正是材质实例所引用的那些贴图。清单只列网格和材质，不列贴图。**
- **后果**：按原判断删掉 = **整座城的贴图全部丢失**
- **正确做法**：删任何资产前查**两件事**
  ```
  AssetTools.get_asset_class(asset)      <- 它是什么
  AssetTools.get_referencers(asset)      <- 谁引用它
  ```
  两个都查完才知道能不能删
- **出处**：2026-11-26，本轮最重要的更正

## 76. 遍历 PrimitiveComponent 时不能假设都有仿真属性

- **症状**：用 `get_components_by_class(unreal.PrimitiveComponent)` 拿到组件后逐个读
  `simulate_physics`，撞到 `ArrowComponent` 抛异常：
  `ArrowComponent: Failed to find property 'simulate_physics'`
- **根因**：`ArrowComponent` 确实继承 `PrimitiveComponent`，但不带任何仿真设置。
  同类还有 `BillboardComponent`、`DrawFrustumComponent` 等辅助组件
- **修法**：写一个安全取值函数，读不到就返回默认值
  ```python
  def safe(component, name, default=None):
      try:
          return component.get_editor_property(name)
      except Exception:
          return default
  ```
- **出处**：2026-11-26，物理状态审计

## 77. Lumen 的软件光追依赖「生成网格距离场」，两者必须同时开

- **症状**：开了 `r.DynamicGlobalIlluminationMethod=1`（Lumen），但间接光看起来不对或很弱
- **根因**：源码注释写明 Lumen 的前提：
  > *Requires 'Generate Mesh Distance Fields' enabled for Software Ray Tracing
  > and 'Support Hardware Ray Tracing' enabled for Hardware Ray Tracing.*
- **修法**：软件光追路径必须同时有 `r.GenerateMeshDistanceFields=True`；
  硬件光追路径还需要 `r.Lumen.HardwareRayTracing=True` 且显卡支持
- **代价**：开了距离场，网格构建时间变长、内存占用上升（大网格尤其明显）
- **出处**：2026-11-26，读 Lumen 枚举注释

## 78. 「我没读过」不等于「没开」——判断有没有之前先读配置

- **症状**：两次判断错误，都是凭印象而不是读文件
  - 第 5 轮：「107 个遗留资产待清理」→ 实际是被引用的**贴图**
  - 第 7 轮：「Lumen 是零」→ 实际 `r.DynamicGlobalIlluminationMethod=1`，**从第一天就在跑**
- **根因**：把「我没研究过这个」当成了「项目没有这个」
- **修法**：判断「有没有」之前，按这个顺序查
  ```
  1. Config/*.ini              <- 项目设置（有没有开）
  2. AssetTools.get_asset_class <- 这是什么东西
  3. AssetTools.get_referencers <- 谁在用
  4. Saved/Logs/*.log          <- 运行时报了什么
  ```
  **四个都查完，再下结论。**
- **工具**：`python Tools\audit_project_config.py` 输出 92 个配置键 + 来源文件
- **出处**：2026-11-26，两次判断错误的合并教训

## 79. uasset 体积不是运行时体积 —— 判断音频开销要看日志的压缩行

- **我先写错的版本**：说「mp3 导入后涨 7 倍」，用 `S_bg_field.uasset` 11.14 MB 当运行时开销。
  **这是错的。**
- **实测数据**（`LogAudioDerivedData` 的压缩行，才是运行时数据）：
  ```
  质量 80: S_bg_field 压缩为 17.39%（从 17,851KB 到 3,103KB）
  质量 40: S_bg_field 压缩为 12.59%（从 17,851KB 到 2,247KB）
  ```
  | 项 | 值 |
  | --- | --- |
  | 源波形（PCM） | 17,851 KB |
  | **质量 80 运行时** | **3,103 KB** |
  | **质量 40 运行时** | **2,247 KB**（小 28%）|
  | `uasset` 磁盘 | 11,140 KB ← **编辑器侧源波形** |
- **根因**：`uasset` 里存的是**编辑器用的源波形**，运行时压缩数据在
  `DerivedDataCache` / 打包后的 pak 里。**改运行时压缩质量不会改 uasset 大小。**
- **怎么量运行时大小**：读日志的 `LogAudioDerivedData` 行，或打包后看 pak
- **修法**：`sound.set_editor_property("compression_quality", 40)` **确实生效**
  （质量 80 → 40 让运行时从 3,103 KB 降到 2,247 KB）
- **出处**：2026-11-26，第一次判断错误后的二次更正

## 80. 量错了对象，等于没量 —— 先问「这个数字代表什么」

- **症状**：把 S_bg_field.uasset 的 11.14 MB 当成「音频运行时开销」，
  据此写了错误的结论（gotcha #79 的第一版）
- **实际**：uasset 存的是**编辑器侧源波形**，运行时数据是日志里那句
  压缩为 17.39%（从 17,851KB 到 3,103KB）
- **这是我的**第三次**同类错误**（前两次：#75 遗留资产、#78 Lumen 是零）
  共同点：**数字本身是真的，但被当成了别的东西**
- **修法**：报出任何数字前，先回答三个问题
  `
  1. 这个数字是谁的？（文件？内存？运行时？打包后？）
  2. 它随时间/设置变化吗？（改了设置它动了吗？）
  3. 有没有第二个来源能对上？（日志？DDC？打包产物？）
  `
  三个问题有一个答不上来，就先别写结论
- **出处**：2026-11-26，音频体积判断的二次更正

## 81. 逆向格式先读源码 —— 研究区有客户端 C++ 源码，别从二进制猜

- **症状**：花了**四轮**（第 11–14 轮）从二进制反推 `.mod` 的网格与蒙皮布局，
  试过三种块头长度、三种法线格式（f32/f16/u8）、固定 4 影响的权重扫描 —— **全部失败**
- **实际**：研究区 `client_src\tw\4DyuchiGXGeometry\` 有**完整的客户端 C++ 源码**：
  ```
  geom_obj.cpp     -- CMeshObject::ReadFile     读网格的完整顺序
  object.cpp       -- CBaseObject::ReadFile     324 字节基类头
  face_group.cpp   -- CFaceGroup::ReadFile      28 字节面组头
  Physique.cpp     -- CPhysique::ReadFile       ★ 蒙皮（15 行代码）
  typedef.h        -- BONE / PHYSIQUE_VERTEX / NODE_TM 结构体
  ```
  **`FORMAT-REFERENCE.md` 里甚至摘录了这些源码。**
- **根因**：我把「研究区是数据仓库」当成了「研究区只有数据」。
  实际它有**反编译出来的源码**，那是比二进制更权威的一手资料。
- **修法**：逆向任何格式前，先做这一件事
  ```powershell
  # 研究区有没有这个格式的读取代码？
  Select-String -Path 'C:\Users\tk\Desktop\moxiang-study\client_src\tw\**\*.cpp' `
      -Pattern 'ReadFile|LoadFile' -List
  # 研究区有没有格式文档？
  Get-ChildItem 'C:\Users\tk\Desktop\moxiang-study\Docs' -Recurse -Filter '*format*'
  ```
- **代价**：四轮 VS 一分钟
- **出处**：2026-11-26，`.mod` 格式解开后的复盘

## 82. `SkeletalMeshTools.import_file` 钉死 FBX 工厂，不支持 glTF

- **症状**：`SkeletalMeshTools.import_file(... source_file='x.gltf')` 报
  `FbxFactory does not support ".gltf" files. Allowed: ['fbx', 'obj'].`
- **根因**：那个工具内部钉死了 FBX 工厂，只认 `.fbx` / `.obj`
- **修法**：用 `AssetImportTask` 不指定 factory，让引擎走 Interchange
  ```python
  task = unreal.AssetImportTask()
  task.filename = '.../x.gltf'
  task.destination_path = '/Game/...'
  task.destination_name = 'SK_X'
  # 不给 factory
  unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
  ```
- **附带坑**：`task.imported_object_paths` 是字符串列表不是对象，
  要 `EditorAssetLibrary.load_asset(path)` 再取
- **成功的标志**：生成三个资产（SkeletalMesh + Skeleton + PhysicsAsset）
- **出处**：2026-11-26，导入墨香的鸟模型

## 83. glTF 的 `byteLength` 必须在所有 accessor 写完后才算

- **症状**：带动画的 glTF 导入产生 **0 个资产**，日志报
  ```
  LogInterchangeEngine: Error: 缓冲文件大小不匹配
  LogInterchangeEngine: Error: 提供的源数据中没有要导入的内容
  ```
  **看起来像文件损坏，实际是顺序问题。**
- **根因**：
  ```python
  gltf = { ..., "buffers": [{"byteLength": len(binary)}] }   # 算早了
  # 之后 add_view() 往 binary 追加动画数据
  # → 声明的 byteLength 比实际小
  ```
- **修法**：在 return 之前重新赋值
  ```python
  gltf["buffers"][0]["byteLength"] = len(binary)
  ```
- **怎么发现**：对比 `buffers[0].byteLength`（30532 才对）与声明值 —— 差的就是动画数据量
- **一般化**：**任何「先算总量、后追加内容」的结构都有这个风险**
- **出处**：2026-11-26，导入带动画的鸟

## 84. 一个模型可能有多个网格块，只导第一个会得到残缺的模型

- **症状**：`198_bobu.mod` 导入后包围盒 **34.3 × 44.0 × 39.5 cm** —— 没有这么小的人形
- **根因**：该文件有 **3 个 MESH 块**（164 / 632 / 37 顶点），导出器只取 `meshes[0]`，
  导的是 164 顶点的小零件，不是 632 顶点的主体
- **为什么鸟没暴露**：鸟只有 1 个网格块
- **修法**：每个网格块生成一个 glTF primitive，**共用同一个 skin**
  ```python
  primitives = []
  for each in meshes:
      attributes, indices = emit_mesh(each)      # 各自有自己的 PHYSIQUE
      primitives.append({"attributes": attributes, "indices": indices})
  gltf["meshes"][0]["primitives"] = primitives
  ```
  **glTF 允许多 primitive 共享一个 skin，每个 primitive 有自己的 attributes。**
- **出处**：2026-11-26，测试 31 骨骼人形角色

## 85. `.mod` 的顶点坐标是世界位置，不是相对原点的局部坐标

- **症状**：多网格修好后包围盒合理（99.6 × 77.8 × 99.4），但角色**在关卡里完全不渲染**。
  actor 位置正确、`visible=True`、有材质、骨骼正常。
- **根因**：查 glTF 的 `POSITION` min/max 发现所有顶点都在 **(23, 25, -1) 米**：
  ```
  primitive 0: min=[22.44, 23.98, -0.89]  max=[23.12, 24.77, -0.01]
  ```
  **也就是说顶点是**模型在原地图里的世界坐标**，不是局部坐标。**
  actor 放到 (9100, -6200)，几何实际在 (11400, -3700) —— 画面外。
- **为什么鸟没暴露**：鸟的顶点恰好接近原点
- **修法**：导出时减去顶点中心
  ```python
  centre = [sum(p[i] for p in positions) / len(positions) for i in range(3)]
  positions = [(p[0]-centre[0], p[1]-centre[1], p[2]-centre[2]) for p in positions]
  ```
  修后 min/max 全部居中于原点，角色立刻渲染出来。
- **⚠️ 更彻底的修法**：应用对象的 `NODE_TM` 变换（`fRotAng`/`fRotAxis`/`fPos`/`fScale`），
  而不是只减中心 —— 当前模型仍"趴着"，很可能就缺这一步
- **出处**：2026-11-26，人形角色不渲染的诊断

## 86. 对象的 NODE_TM 矩阵必须应用到顶点上

- **症状**：角色导入后几何在，但「趴着」、各部件位置错乱
- **根因**：每个对象的基类头里有 NODE_TM（184 字节），含位置/旋转轴角/缩放，
  以及**两个准备好的矩阵**（mat4 和 mat4Inverse）。
  各部件的摆放靠它 —— 实测某网格 RotAng=2.0071（115°）、Scale=0.7314、
  Pos=(2278.8, -8.3, 2438.3)。
  **导出时若只把它写进 GLTF 节点而不作用于顶点，几何就散落/趴着。**
- **mat4 的约定**：**行向量**，平移在最后一行
  `
  x' = x*m[0] + y*m[4] + z*m[8]  + m[12]
  y' = x*m[1] + y*m[5] + z*m[9]  + m[13]
  z' = x*m[2] + y*m[6] + z*m[10] + m[14]
  `
- **顺序**：先乘 mat4，**再**减顶点中心（否则居中会算错）
- **出处**：2026-11-26，角色「趴着」的诊断

## 87. 「最高轴」不是有效的模型朝向判据

- **症状**：角色导入后看着「趴着」，我据此怀疑坐标轴映射错了
- **实际**：用七个模型测「哪个轴最高」，分布是 {Y:3, Z:2, X:2} —— **没有主导轴**
- **根因**：**「最高」只对直立人形等于「高度」**
  - 鸟的 Y 是**翼展**
  - 四足兽的 Y 是**体长**
  - 扁平道具的 X 是**宽度**
- **正确判据**：看源格式自己的约定
  - 墨香 .hfl 把高程存为 **Z**
  - .map 摆放 (x y z)，**z 是高程**
  - → 源是 Z-up，glTF 映射 (x, z, -y) 让 glTF Y = 源 Z，**正确**
- **教训**：**选判据前先验证判据本身**。我在第一个模型上就得到了可疑答案，
  却先去改代码、后去验判据 —— 顺序反了
- **出处**：2026-11-26，朝向问题关闭

## 88. `.mod` 的法线是**条件性**的（LIGHT_MAP 和 ALIGN_VIEW 都没有）

- **症状**：批量导出时部分模型报
  `unpack_from requires a buffer of at least N bytes ... (actual buffer size is N-20)`
  —— **跑到文件末尾之外十几到二十字节**
- **根因**：客户端源码里法线读取有两个前置条件
  ```c
  if (meshFlag.GetShadeType() == SHADE_TYPE_LIGHT_MAP)
      m_pLightTexture->ReadFile(pFP);          // 光图代替法线
  else if (meshFlag.GetTransformType() != TRANSFORM_TYPE_ALIGN_VIEW)
      FSRead(normals, 12 * dwVertexNum);        // 两个条件都要过
  ```
  **`mesh_flag` 位域（`mesh_flag.h`）：**
  | 掩码 | 含义 |
  | --- | --- |
  | `0x0F` SHADE_TYPE | 0=VERTEX_LIGHT_IM / 1=VERTEX_LIGHT_RT / **3=LIGHT_MAP** |
  | `0xF0` TRANSFORM_TYPE | 0=SOLID / 0x10=NOT_SOLID / **0x30=ALIGN_VIEW** / 0x50=ILLUSION |
  | `0x100` RIGID_TYPE | 刚体 |
  | `0x200` PICK_ENABLE | 可拾取 |
  | `0x7F000000` RENDER_ZPRIORITY | 渲染优先级 |
  | **`0x80000000` WRITE_ZBUFFER** | **写 Z 缓冲（与解析无关）** |
- **修法**：先判两个条件，再决定读不读法线；没有法线时给 glTF 一个常量 `(0,0,1)`
  —— 平涂正是源文件不写法线的意思
- **出处**：2026-11-26，批量导出

## 89. `.anm` 走块要自校验，否则会撞进尾部资源引用

- **症状**：`.anm` 解析报 `unpack_from requires 20 bytes`，20 正是 `<5I` 头的大小
- **根因**：`.anm` 最后一块后面有**资源引用文本**（`.dds` / `.chx` 文件名）。
  走法只看 `0xF000` 标记和 size，撞进尾部后把随机字节当成了块头
- **修法**：块大小自校验
  ```python
  expected = 152 + pos_n*20 + rot_n*24 + scale_n*40
  if expected != size:
      break        # 走到尾部了
  ```
  **和 `.mod` 的验证同一手法：让数据自己证明自己**
- **出处**：2026-11-26，批量导出

## 90. `.chx` 有的带二进制头尾，且名字大小写和磁盘不一致

- **症状**：直接按文本读 `.chx` 拿到乱码开头
  （`m_do+10.chx` 开头是 `}   Q     øê`）
- **根因**：部分 `.chx` 在文本列表前后各有一段**二进制头/尾**
- **修法**：
  ```python
  start = text.find("*MOD_FILE_NUM")   # 不假设从字节 0 开始
  # 收集动画名时，遇到不以 .ANM 结尾的行就停（后面是二进制尾）
  ```
- **第二个坑**：`.chx` 里的名字大小写可能和磁盘不一致
  （`boss_cowi_01` 列出的是 `Boss_cowI_01.anm`）
  → 查找要**不区分大小写**，并对目录做一次扫描兜底
- **成果**：1,081 个模型 / 21,919 条动画引用 / **21,878 条解析成功（99.8%）**
- **出处**：2026-11-26，批量导出配对

## 91. `SCALE_KEY` 是 **36 字节**不是 40 —— 一个数字藏住了 41 条动画通道

- **症状**：`Boss_cowf_01.anm` 有 **70 个块标记**，只解析出 **7–8 块**；
  38 骨骼的 Boss 只导出 **8 条动画通道**
- **根因**：`SCALE_KEY` 算错了 4 字节
  ```c
  struct SCALE_KEY {          // 实际 36 字节
      DWORD    dwTicks;       // 4
      DWORD    dwFrame;       // 4
      VECTOR3  v3Scale;       // 12
      VECTOR3  v3ScaleAxis;   // 12
      float    fScaleAxisAng; // 4
  };                          // = 4+4+12+12+4 = 36
  ```
  **我写成了 40。** 于是「声明的关键帧是否装得下」这个自校验，
  **在第一个含 scale 键的块上就失败**，走法提前终止
- **怎么定位的**：块自校验的算式会打印「需要 2192 字节但只有 1988」，
  而 `152 + 51 × 36 = 1988` **精确吻合** —— 36 是对的
- **修法**：`ANM_SCALE_KEY = 36`
- **效果**：38 骨骼的 Boss 从 **8 通道 → 49 通道**；块数从 7 → **69**
- **一般化**：**结构体大小要按字段逐个加，不要估**。
  用「声明量与块大小是否吻合」做自校验，就能让错误自己暴露
- **出处**：2026-11-26，块走法追踪

## 92. 「解析失败」和「没有我要的东西」是两回事

- **症状**：统计 `.anm` 时得出「284 个失败（7%）」
- **实际**：这 284 个里 **153 个是顶点动画文件**
  （块头 `rot=0 pos=0 scale=0` 但 `mesh>0`）—— 水、火、瀑布、岩浆。
  **它们本来就没有骨骼轨道，`parse_anm` 返回空是正确行为**
- **真实分布**：

  | 类别 | 数量 | 性质 |
  | --- | --- | --- |
  | 有骨骼动画 | 3,772（93%）| 正常 |
  | 只有顶点动画 | 153（3.8%）| **预期行为** |
  | 块起点定位不到 | 105（2.6%）| 真正的待查项 |
  | 形态未知 | 26（0.6%）| ? |

- **`.anm` 的三种动画载体**

  | 载体 | 字段 | 用途 |
  | --- | --- | --- |
  | 骨骼 | `dwRotKeyNum` / `dwPosKeyNum` / `dwScaleKeyNum` | 角色 |
  | 顶点 | `dwAnimatedMeshKeyNum` | 水/火/瀑布/旗帜 |
  | UV | 顶点键内部 | 贴图滚动 |

- **教训**：**把「没有我要的东西」计入「失败」，会夸大问题规模**。
  统计时要区分**预期为空**和**意外失败**
- **出处**：2026-11-26，批量导出统计

## 93. 把「整体」的运算写在「局部」上：包围盒 14 公里

- **症状**：38 骨骼的 Boss 导入 UE 后包围盒 **(1419593, 1323043, 1973751) cm = 14 公里**
- **两个原因，都是作用域错误**：

  **① 每个网格块独立居中**
  ```python
  # 错：每块减自己的重心 → 24 块全叠到原点
  centre = centroid(block.positions)
  # 对：整个模型一个重心
  centre = centroid(all_blocks_all_positions)
  ```

  **② 背景/特效网格也被保留**
  - 24 块里有 **12 块**顶点跨 **14–22 公里**（背景板、天空面）
  - 它们**也有骨骼权重**，所以按「有无绑定」筛选**无效**
  - 只能按**尺寸**筛：if block_extent > 10000 cm: drop

- **修后**：包围盒 **279.8 × 161.6 × 87.5 cm**，网格块 24 → 12
- **教训**：**最响的症状（14 公里）指向的是数据，而错误在代码结构上**。
  先去查顶点坐标、缩放、坐标系，白花了时间 —— 应该先问「这个运算的作用域对不对」
- **出处**：2026-11-26，真角色导入

## 94. 骨骼索引是稀疏的，不能直接当关节索引用

- **症状**：导出 `boss001.mod` 报
  `struct.error: 'H' format requires 0 <= number <= 65535`
- **根因**：`boss001` 有 **67 根骨骼，但索引是 11..83**（稀疏的）。
  我把**骨骼索引**直接写进 glTF 的 `JOINTS_0`，于是出现 83 > 67
- **为什么之前没暴露**：
  - `108_bird` 9 骨骼，索引 0..8 连续
  - `198_bobu` 31 骨骼，索引 0..30 连续
  - **`boss001` 67 骨骼稀疏 —— 第三个样本才暴露**
- **修法**：
  ```python
  ordered = sorted(bones, key=lambda b: b["index"])
  joint_of = {b["index"]: i for i, b in enumerate(ordered)}
  mapped = joint_of.get(bone_index)
  if mapped is not None:
      js.append(mapped)
  ```
- **教训**：**关节索引 = 该骨骼在 skin 关节列表里的位置，不是骨骼自己的编号**
- **出处**：2026-11-26，真 Boss 本体导入

## 95. 文件名告诉你它属于谁，不告诉你它是什么

- **症状**：`boss_cowf_01.mod` 有 38 骨骼、36/38 匹配动画、49 通道 ——
  一切都「对」，但导入后画面里全是大平面，看不出是 Boss
- **根因**：这个文件的 24 个网格块**全是火焰面片**：
  `fire03` / `BU_fire_boom_01` / `fire_U_b_08` —— 它是**Boss 身上的火**
- **判断方法：看网格块的名字**
  - 含 `fire` / `eff` / `smoke` / `boom` / `fog` → **特效**
  - 含 `head` / `arm` / `shoulder` / `eye` / `body` → **身体**
- **`boss001.mod` 才是本体**：`boss01_head` / `boss01_armL` / `boss01_eyeR` …
  17 个身体部件，0 个特效块，尺寸 0.05–1.11 米
- **教训**：**「有骨骼 + 有动画」不等于「是角色」。**
  判断一个文件是什么，只能看它里面有什么几何，不能看名字、不能看骨骼数
- **出处**：2026-11-26，找真身

## 96. 骨骼的 `mat4` 是**世界**变换，不是局部变换

- **症状**：把骨骼 `mat4` 沿父链累乘后，骨骼散到 **10 米外**
  （包围盒 395 × 1031 × 844 cm），对比网格只有 1.1 米
- **证据**：连续脊柱骨骼的 `mat4` 平移
  ```
  Bone28 (-32.44,  94.35, -11.19)
  Bone27 (-31.76, 112.12, -15.48)
  Bone26 (-28.83, 126.99, -19.19)
  Bone25 (-21.95, 143.83, -17.52)
  ```
  **Y 逐个递增，X/Z 很小 —— 这只能是世界坐标**
- **根因**：当成局部矩阵 `world * parent_world`，等于算了「世界²」
- **修法**：
  - `bind_world[bone] = bone["node_matrix"]`（**直接用，不累乘**）
  - glTF 节点局部变换 = `world * inverse(parent_world)`
- **出处**：2026-11-26，骨骼变换核对

## 97. 骨骼的 `fPos` / `fRotAng` 不能还原 `mat4`

- **症状**：用 `fRotAng`/`fRotAxis`/`fPos`/`fScale` 构造 glTF 节点变换，
  和用 `mat4` 算的逆绑定矩阵**描述的是两个不同的骨架**
- **实测差异**：
  ```
  Bone28  mat4 (-32.44, 94.35, -11.19)   字段 (13.92,  0.00,  0.00)   差 94.4
  Bone25  mat4 (-21.95, 143.83, -17.52)  字段 (0.23, -20.22, 16.59)   差 164.1
  ```
- **结论**：**`mat4` 是唯一权威**，其余字段不可用于重建变换
- **修法**：节点变换必须**分解 `mat4`**（translation + quaternion + scale），
  不能读散字段
- **一般化**：**一个结构里同时有「原料」和「成品」时，用成品**。
  原料可能没同步更新，或语义与成品不同
- **出处**：2026-11-26，骨骼变换核对

## 98. 网格块的 mat4 不该应用（骨骼的该用）

- **症状**：oss001 导入后部件散开，像一堆分离的碎片
- **实测对比**（同一批顶点，两种读法）：

  | 读法 | 总包围盒 | 块中心散布 |
  | --- | --- | --- |
  | 应用每块 mat4 | 192.4 x **434.2** x 152.2 cm | 158.8 x **383.0** x 75.2 |
  | 不应用 mat4 | 296.9 x 272.2 x 207.7 cm | 181.0 x 191.2 x 104.5 |

  **应用 mat4 把模型沿 Y 拉了两倍。**
- **关键的不对称**：同一个 NODE_TM.mat4 字段，两类对象语义不同
  - **骨骼**：该用 —— 连续脊柱 Y = 94→112→127→144 递增，是真世界坐标
  - **网格**：不该用 —— 顶点已经是世界坐标，mat4 会二次拉开
- **修后**：包围盒 **2.97 × 2.08 × 2.72 m**，Boss 有实体
- **怎么找到的**：先做无蒙皮静态网格，发现包围盒和骨骼版一模一样
  → 证明散开不是蒙皮造成的；再对比两种读法 → 数据直接给答案
- **教训**：**同一个结构体字段在不同对象上可能有不同语义**；
  不要因为「字段名叫矩阵」就假设它在所有地方都是变换
- **出处**：2026-11-26，Boss 实体化

## 99. 墨香材质块的贴图名存 `.tga`，磁盘上是 `.dds`

- **现象**：MATERIAL 块里的纯文本是 `boss_mob01.tga`，
  但真正的文件是 `resources/dds/boss_mob01.dds`
- **修法**：查找时**换扩展名**，不要信任存的扩展名
  ```python
  stem = os.path.splitext(name)[0]
  for folder, extension in ((DDS, ".dds"), (TGA, ".tga")):
      candidate = os.path.join(folder, stem + extension)
      if os.path.exists(candidate):
          return candidate
  ```
- **实测**：8 个模型共 9 个贴图引用，**100% 解析成功**
- **出处**：2026-11-26，材质管线

## 100. 墨香 DDS 是 DXGI 格式，UE 5.8 不认

- **症状**：
  ```
  LogFactory: FactoryCreateFile: Texture with TextureFactory (...boss_mob01.dds)
  Error: DDS DXGIFormat not supported : 71 : BC1_UNORM
  Error: Image Import failed.
  Error: Texture import failed
  ```
- **根因**：这批 DDS 用 DXGI 格式头（`BC1_UNORM` = DXGI 71），
  引擎的 DDS 读取器只接受旧的 DXT 头，`import_asset_tasks` 走 Interchange 或
  显式 `TextureFactory` 都失败
- **修法**：**用 Pillow 转 PNG 再导入**
  ```python
  image = Image.open(source + ".dds")
  image.load()
  image.save(target + ".png", "PNG")
  ```
  **8 个全部转换成功，原始尺寸保留（512x512 / 256x256 / 128x256）**
- **一般化**：**格式不认时不要换工具，先换格式**
- **出处**：2026-11-26，材质管线

## 101. 材质槽覆盖在**组件**上，`SkeletalMesh` 没有 `set_material`

- **症状**：
  ```
  AttributeError("'SkeletalMesh' object has no attribute 'set_material'")
  TypeError("SkeletalMesh: Failed to convert type 'list' to property")
  ```
- **根因**：`SkeletalMesh` 资产只有导入时带的那份材质列表，
  **放置时的覆盖属于组件** —— 这是 UE 的常规分工，不是 API 缺失
- **正确做法**：
  ```python
  component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
  component.set_material(index, material)     # 按槽号覆盖
  ```
- **槽数从网格读**：`len(mesh.get_editor_property("materials"))`
- **出处**：2026-11-26，材质管线

## 102. 验证动画运动，别用引擎组件去测

- **症状**：想验证「导出的动画有没有运动」，去驱动 SkeletalMeshComponent
  - component.bounds 不存在，要用 ctor.get_actor_bounds()
  - instance.set_animation 不存在，是 **set_animation_asset**
  - get_anim_pose_at_time 缺必填的 evaluation_type 参数，而该枚举**没导出到 Python**
  - get_bone_pose 会让 Python 线程**挂死**
  - set_position(t) 调用成功，但**不触发重新求值**，包围盒在所有时刻完全相同
- **根因**：**在验证「对象」时，实际在测「手段」**
  - 我想知道的是「动画数据里有没有运动」
  - 却在测「引擎能不能被我驱动」—— 被 API 细节卡了两轮
- **正确做法**：直接量源文件
  `python
  # 每条轨道的旋转键与首键的最大夹角
  worst = max(quat_angle(first, r[1]) for r in rotations[1:])
  `
  实测：boss001 20 轨在动（最大 20.6°），boss_cowf 36 轨（73.7°），
  鸟 6 轨（179.4°），bobu 11 轨（39.4°）—— **数据是对的**
- **教训**：**探针失效时，回到被验证对象本身**
- **出处**：2026-11-26，动画验证

## 103. PIE 会建新世界，编辑器里设的动画状态不继承

- **症状**：在编辑器世界给 `SkeletalMeshComponent` 设了动画并 `set_playing(True)`，
  启动 PIE（`bSimulate: true`，世界会 tick），隔 700 ms 抓两张图 ——
  **差异散布全画面，Boss 没动**
- **根因**：**PIE 创建新世界并重新实例化 actor**，
  编辑器世界的动画状态**不继承到播放世界**
- **诊断方法**：用 Pillow 做图像差异并**分 4x4 网格统计**，
  看差异是否集中在目标区域。散布全画面 = 噪声；集中一处 = 真的动了
  ```python
  arr = np.asarray(ImageChops.difference(a, b)).astype(int)
  mask = arr.sum(axis=2) > 10
  # 按 4x4 分块打印像素数
  ```
- **`StartPIE` 参数**（必填）：
  ```json
  {"options":{"bSimulate":true,"playMode":"PlayMode_InViewPort","warmupSeconds":2}}
  ```
  **`bSimulate: true` = 世界 tick 但不生成玩家 Pawn，适合观察自主 actor**
- **要设 PIE 里的状态**：需要拿播放世界的句柄（`get_game_world()` 之类），
  那是另一个问题，与管线正确性无关
- **出处**：2026-11-26，PIE 播放验证

## 104. 墨香贴图有三种格式，.tif 的 929 个最容易被漏掉

- **症状**：批量扫描材质时报告「841 个模型（16%）无贴图」
- **根因**：我的正则只匹配 	ga|dds|bmp|png|jpg，
  但墨香还用 **.tif** —— 磁盘上 929 个
  `
  图片总数: 6,762
    .dds  5,315
    .tif    929     <- 漏掉的
    .tga    518
  `
- **修后**：有贴图的模型 **4,464（84.1%）→ 5,227（98.5%）**，
  无材质的 **841 → 78**
- **线索**：13120.mod 有 **96 骨骼**却没有贴图 —— 这不合理，
  说明检测有问题而不是数据缺失
- **教训**：**「坏消息比例很高」的统计，先怀疑统计方法。**
  我把 16% 当结论写进了文档，直到抽查样本才发现是漏了一个扩展名
- **出处**：2026-11-26，材质批量

## 105. 面组的材质索引被合并 —— 40 个材质变成 1 个槽

- **症状**：`boss001.mod` 有 **40 个 MATERIAL 块**，但导入 UE 后网格只有 **1 个材质槽**，
  全身用同一个表面
- **根因**：`read_mod_mesh` 把每个网格块的 **N 个面组**的所有三角面塞进一个列表，
  导出一个 primitive → 引擎给一个槽
- **事实**：面组本来就带材质索引
  ```
  MESH @83800: faceGroups=6
     group 0: mtl=39  index=5   group 3: mtl=36  index=2
     group 1: mtl=38  index=4   group 4: mtl=35  index=1
     group 2: mtl=37  index=3   group 5: mtl=34  index=0
  ```
- **修法**：**每个面组一个 primitive**，各自带 `"material": index`
  ```python
  groups.append({"material": g_mtl, "slot": g_index, "triangles": group_triangles})
  # 每个组生成独立索引缓冲，共享顶点属性
  ```
  **glTF 允许多 primitive 共享顶点属性、只换索引缓冲，所以成本几乎为零**
- **结果**：`primitives 17 → 40`、`materials 0 → 40`、UE 槽数 **1 → 40**
- **回归**：7 个模型包围盒**完全不变**，primitive 数各自增加（鸟 1→2、bobu 3→8、Boss 17→40）
- **教训**：**管道能导出几何，不等于导出了全部信息。**
  「哪些面用哪个材质」是一条独立的信息，丢了不会报错，只会让所有东西变一个颜色
- **出处**：2026-11-26，多材质槽

## 106. 「改了但画面没变」：先分清是没生效还是没有可见差异

- **症状**：给 Boss 的 40 个材质槽全赋同一材质后，**画面与只有 1 个槽时完全一样**
- **两个可能**：
  1. 赋值**没生效**
  2. 赋的东西**本来就没有可见差异**
- **这次是第 2 个**：读材质块字段发现
  `
  40 个材质块，只有 2 种颜色组合：
    (232,239,245) × 37 个
    (255,255,255) ×  3 个
    f4 = 0.100 全部相同
  
  贴图全部是同一张 boss_mob01.tga
  `
  **源数据就是「一张图集 + 近乎统一的材质参数」，视觉差异全在 UV 区域**
- **判断方法**：**把被改的量读出来看数值差异**，不要靠画面判断
- **教训**：画面是**间接**证据。数值是直接证据
- **出处**：2026-11-26，材质字段解析

## 107. 「消息日志」窗口会遮挡视口 —— `SetupLayout.ps1` 现在自动最小化它

- **要求**：人明确说过，消息日志窗口要最小化/关闭，不要遮挡，**并且不要反复提醒他**
- **做法**：不是靠每次记住，而是写进 `Tools/SetupLayout.ps1` ——
  它本来就在摆窗口，顺手把遮挡视口的窗口最小化
- **判定方式：按**矩形重叠**，不按标题**
  ```powershell
  # 属于本编辑器进程、未最小化、矩形与编辑器重叠、且不在编辑器下方（内容浏览器在下方）
  bool overlaps = r.L < keep.Rt && r.Rt > keep.L && r.T < keep.B && r.B > keep.T;
  ```
  **因为 `SetupLayout.ps1` 必须保持纯 ASCII**（PowerShell 5.1 把无 BOM UTF-8 当 ANSI），
  不能直接匹配中文标题 `消息日志`
- **验证**：先手动恢复消息日志 → 跑 `SetupLayout.ps1` → 输出
  ```
  overlay      -> 1 overlapping window(s) minimised
  ```
- **写这段时犯的两个错（都是老毛病）**：
  1. **在 .ps1 里写了中文** —— 违反该文件自己第一条注释
     「keep this file ASCII-only」，`Find('消息日志')` 匹配不到，那行静默没执行
  2. **检查写成了 `if "GetWindowThreadProcessId" in text`** ——
     匹配到了**使用处**而不是**声明**，于是误判「已声明」，
     `Add-Type` 因为缺 `DllImport` 而编译失败
- **教训**：
  - **「已经存在」的检查要匹配**特征的完整形态**，不能只匹配子串**
  - **文件头部写着约束时，先读约束再动手**
- **出处**：2026-11-26，消息日志遮挡

## 108. 自动化抢焦点会打断人 —— 优先 MCP，不用鼠标

- **要求**：人会在左侧编辑器/右侧对话之外还切去别的窗口做事。
  **agent 的自动化一旦抢焦点，人的操作就被打断。**
- **我自己犯过的**：
  - 用 `mouse_event` 点「恢复包」对话框 —— **真的移动了人的鼠标**
  - `SetupLayout.ps1` 里 `SetForegroundWindow($editor)` —— **每次跑都抢焦点**
  - 清理遮挡窗口用 `SW_MINIMIZE` —— 把焦点交给了下一个窗口
- **正确顺序**：

  | 优先 | 手段 | 为什么安全 |
  | --- | --- | --- |
  | 1 | **MCP 工具调用** | 跑在编辑器进程内，不碰焦点 |
  | 2 | UI Automation 按名字点 | 不动光标 |
  | 3 | `PostMessage(WM_CLOSE)` | 关对话框不必点击 |
  | 4 | `SetWindowPos` + `SWP_NOACTIVATE` | 移动不抢焦点 |
  | 5 | 坐标点击 | 仅最后手段 |

- **已修**：
  - `SetupLayout.ps1` 删掉 `SetForegroundWindow`，`Place()` 改 `SWP_NOACTIVATE`，
    遮挡窗口清理改 `SW_HIDE`
  - `EditorGuard.ps1` 加 `PostClose()`（`PostMessage` + `WM_CLOSE`），
    两个对话框关闭都先走它
- **验证**：跑 `SetupLayout` / `EditorGuard check` / `EditorGuard dismiss` 后，
  **前台窗口仍是原来那个**（实测三次都是聊天窗口）
- **自查**：`python Tools/audit_focus.py`
- **写审计脚本时又犯了同一个错**：`name + "("` 也匹配到
  `DllImport ... extern bool name(` **声明**，于是把已修好的文件报成有问题。
  **修：跳过含 `DllImport` / `extern` 的行**
- **教训**：**「匹配到名字」不等于「匹配到调用」。**
  和 #107 里那两次是同一类：**检查的是子串，不是语义**
- **出处**：2026-11-26，焦点问题
- **🔴 规则已变更（2026-11-26 23:00，人明确指示）**：
  **"你在进行操作的时候可以优先抢占焦点"** —— 所以 `RebuildInEditor.ps1`
  （激活窗口 + 点击控制台 + 粘贴 + 回车）现在是**允许的常规手段**，
  不再是"最后手段"。
  **仍然不变的两条**：不许改编辑器和内容浏览器的**尺寸/位置**；
  操作完必须把视口还原到默认观察位（AGENTS.md 规则 3b）。
  上面那张优先级表继续有效，只是第 5 档从"仅最后手段"升为"可用"。

## 109. `Get-Content` 不写 `-Encoding UTF8` 会把中文显示成乱码

- **症状**：`Get-Content Docs/UE5-DEBUG-INDEX.md -First 6` 输出
  `# UE5 璋冭瘯涓庨棶棰樺畾浣?路 绯诲垪绱㈠紩`
- **我当时以为**文件编码被我的脚本写坏了
- **实际**：文件是**正常 UTF-8**，解码验证：
  ```
  前 120 字节 hex: 2320554535 20e8b083e8af95e4b88e…
  UTF-8 解码: 成功
  第一行: # UE5 调试与问题定位 · 系列索引
  ```
- **原因**：PowerShell 5.1 的 `Get-Content` 默认按系统 ANSI（本机 GBK）读，不按 UTF-8
- **修法**：
  ```powershell
  Get-Content file.md -Encoding UTF8 -First 6
  ```
  或者用 `read` 工具（它按 UTF-8 读）
- **⚠️ 这是我**第二次**把「工具输出异常」当成「数据有问题」**
  （第一次见 #108 的 `Get-Process` 报错被误读为进程消失）
- **教训**：**显示乱码先查读取端的编码，别先怀疑文件。**
- **出处**：2026-11-26，症状手册索引

## 110. PowerShell 的 `-replace` 会连文件名一起替换

- **症状**：`(Get-Content x.py) -replace 'IBMFix', 'IBMFix2'` 之后，
  脚本里的路径变成 `boss001_IBMFIX222.gltf`，导入静默失败
- **原因**：`-replace` 是**全局正则替换**，不区分「代码里的标识符」和「字符串里的文件名」
- **后果**：Interchange 报 `使用所选的管线` 无法导入，`imported_object_paths` 为空
- **修法**：
  - **改脚本用 `edit` / `write` 工具，不用字符串替换**
  - 真要替换时，锚定上下文（如替换整行而不是子串）
- **⚠️ 和 #109 同一类：工具的行为和我以为的不同**
- **出处**：2026-11-26，验证 IBM 修复

## 111. PowerShell 变量名不区分大小写 —— `$Readback` 和 `$readback` 是同一个变量

- **症状**：脚本报 `Exception calling "AppendAllText": Illegal characters in path`，
  报错点在写文件那一行，路径看起来完全正常
- **原因**：同一个作用域里先写了 `$Readback = Join-Path ...`（路径），
  循环里又写了 `$readback = (Get-Content ...)`（JSON 文本）——
  **PowerShell 变量不区分大小写，第二次赋值把路径覆盖成了 JSON**
- **为什么难发现**：报错在写文件处，谁都会去检查路径拼写，不会想到被覆盖
- **修法**：**同一脚本里不要用只差大小写的变量名**；写盘用 `Set-Content` 一次写，
  不用循环 append
- **同类**：几乎同时 `Add-Content -Encoding` 报"参数不存在"，也是这一片代码在误导排查方向
- **教训**：**报错位置不是原因位置。** 和 #110 一样：先怀疑"变量/字符串被别的代码改了"
- **出处**：2026-11-26，渲染 A/B 第二轮

## 112. A/B 复位清单必须写全每个变体碰过的旋钮

- **症状**：三个不同旋钮的对照图**两两完全相同（0.00–0.03%）**，
  和基线都差 17.56%
- **我当时的判断**："Lumen GI 关掉后引擎不会恢复，得重载场景"
- **实际**：复位清单里没写 `r.Lumen.DiffuseIndirect.Allow`。
  第一个变体把它关掉之后，**后面每个变体的"复位"都没把它打开**，
  于是三张图都是"GI 关着"的样子
- **连带发现**：**重载关卡也不会恢复** —— CVar 是全局的，换世界不重置它。
  所以"重载一下就好了"这个直觉在这一层是错的
- **修法**：
  1. 复位清单**逐条列出所有变体碰过的 CVar**（开和关两个方向都写）
  2. 跑完再拍一张"复位后"截图，和控制组比 —— 现在这张是
     `Saved/learn_ab4/ab_after_restore.png`，0.02%
- **教训**：**"这台机器/引擎有怪行为"之前，先证明自己的脚手架没有漏项。**
  和调试系列 #3/#4/#9 是同一型：把工具给出的结果当成事实
- **出处**：2026-11-26，渲染 A/B

## 113. `r.LumenScene.Visualize` / `r.LumenScene.Radiosity.Enable` 这两个名字不存在

- **症状**：设了 `r.LumenScene.Visualize 1`、`r.LumenScene.Radiosity.Enable 0`，
  像素差 0.02–0.04%（等于噪音），看起来像"这两个功能没有视觉效果"
- **实际**：**两个 CVar 都不存在**，控制台静默忽略。真名是：
  - `r.Lumen.Visualize`（0 关 / 1 Overview / 3 Lumen Scene …）
  - `r.LumenScene.Radiosity`（没有 `.Enable` 后缀）
- **怎么查出来**：MCP `EditorToolset.EditorAppToolset.SearchCVars` 按前缀搜，
  返回里**有 `value` 字段才说明存在**
- **教训**：**"改了没反应"的第一问是"这个旋钮存在吗"，第二问才是"生效了吗"。**
  和已有结论「有 `= value` 才存在，只有 `Cmd:` 就是不存在」是同一条，
  但这次是**用错名字**而不是**猜名字**，更容易蒙混过去
- **出处**：2026-11-26，Lumen 实操

## 114. 编辑器 Python 里 `time.sleep` 会卡住游戏线程 —— 循环抓图只出最后一张

- **症状**：一个循环里请求 9 张 `take_high_res_screenshot`，日志 9 行"shot"都在，
  磁盘上只有 **1 个** PNG（最后那个）
- **原因**：编辑器 Python 跑在游戏线程；`time.sleep` 睡的就是要出图、要推进帧的那条线程。
  每次新请求取消上一个未完成的请求，脚本返回后只剩最后一个能渲染
- **修法**：
  - **一个变体一次运行**，抓图放到脚本返回之后（MCP `CaptureViewport` 从外部抓）
  - 或者把 `take_high_res_screenshot` 的返回值当任务，交给引擎排程，不在 Python 里等
- **教训**：**在引擎里写脚本，"异步的东西用同步等待"几乎总是错的**
- **出处**：2026-11-26，渲染 A/B 第一版

## 115. 动态天空会让整帧像素差失去分辨力

- **症状**：控制组（设置完全不变）和基线差 **23.48%** 像素
- **定位**：3×3 分块 —— 天空带 **56.0%**、城楼+地面带 7.2%、最下排 **0.0%**
- **原因**：Demo 场景里有 VolumetricCloud 在逐帧飘动
- **修法**：A/B 前先冻结逐帧动画源（`r.VolumetricCloud 0`），
  控制组降到 **0.03%**；或者只比"稳定区域"，并在文档里写清楚排除了哪些区域
- **教训**：**先量噪音地板，再解释差异。** 没有地板的百分比只是数字
- **出处**：2026-11-26，KHS 建春门 Demo 关卡

## 116. 资产级材质槽赋了，画面没变 —— 组件 override 优先，而且它可能已经有值

- **症状**：`StaticMeshTools.set_material` 返回 `true`，`get_material` 回读已是 `M_Boss_Mob01`，
  `save_assets` 也成功；**前后两张截图几乎一模一样**
- **原因**：`SM_Boss001` 的组件 `overrideMaterials` 里有一条**显式** `WorldGridMaterial`
  —— 不是"空数组"，是"明确设成了 WorldGrid"。组件 override 优先于资产槽，所以资产槽改了白改
- **查法**（MCP，两条调用）：
  ```
  ObjectTools.list_properties(组件)              ← 拿到真实属性名 overrideMaterials
  ObjectTools.get_properties(组件, [属性名])     ← 读到那条 WorldGridMaterial
  ```
  **`get_properties` 传错名字会直接报 "could not be read" 并终止整个脚本**（见 #117）
- **修法**：改组件那一层
  ```
  ObjectTools.set_properties(组件, json.dumps(
      {"overrideMaterials": [{"refPath": "/Game/.../M_Boss_Mob01.M_Boss_Mob01"}]}))
  save_assets(["/Game/Maps/LingXuJie"])     # 组件 override 是关卡里的数据，要存关卡
  ```
  与 `build_level.py` 的既有约定一致（那里也是 `component.set_material(slot, mat)`）
- **教训**：**"查材质槽"要查两层 —— 资产槽 + 组件 override。**
  只查资产槽会得出"这里没材质"的错结论；只改资产槽会得出"改了没反应"的错结论
- **出处**：2026-11-27，`MX_BOSS001_STATIC`（案例 004 的那个真缺陷）

## 117. `execute_tool_script` 里工具报错会终止整个脚本，`try/except` 抓不住

- **症状**：脚本里用 `try: execute_tool(...) except Exception: ...` 包住一次调用，
  结果整个 `run()` 的结果**没有返回**，只回来那一条错误文本；已经算出来的东西全丢
- **原因**：工具失败抛的是沙箱层的错误，不是 Python 异常 —— `except` 没机会执行，
  脚本直接被判定失败
- **修法**：
  - **不要用"多试几个名字看哪个对"的写法**；先用 `list_properties` / `describe_toolset` 问清楚
  - **先读后写**：所有可能失败的调用放在写操作之前，失败时至少没改坏东西
  - 一次调用里**只放一个"可能失败"的新参数**，出问题能立刻定位
- **教训**：**在沙箱里，异常处理不是安全网；参数正确才是。**
- **出处**：2026-11-27，一次调用里连试 4 个 `slot_name`，把整个结果试没了

## 118. `CaptureViewport` 必须显式传 `annotations`，六个字段全填

- **症状**：只传 `captureTransform` + `bShowUI`，报
  `Function "CaptureViewport", input param "annotations" needs a default value.`
  但它的 input schema 里 `annotations` **不在 required 里**
- **原因**：生成的 Python 包装函数里该参数没有默认值；schema 的 required 与包装函数不一致
- **修法**：显式传，不想看网格和标签就这样：
  ```json
  {"gridSpacing": 0, "gridExtent": 0, "gridHeight": 0,
   "maxLabelDistance": 0, "classFilter": null, "maxLabels": 0}
  ```
  `gridSpacing: 0` 关网格、`maxLabelDistance: 0` 关标签，`classFilter: null` 可以接受
- **教训**：**schema 说"可选"不等于包装函数给默认值** —— 报"needs a default value"时照着 schema 全填
- **更正（2026-11-27 PIE 抓图）**：反过来也一样 —— 只传 `annotations` 不传 `captureTransform`，报
  `input param "captureTransform" needs a default value`。**两个参数都没有默认值，必须同时传**，
  否则你会在两个错误之间来回跳
- **出处**：2026-11-27，一次调用里两次截图

## 119. PowerShell 里 `$script` 装 `Get-Content -Raw` 的结果，`ConvertTo-Json` 会变成 `{"value": ...}`

- **症状**：`@{ script = $script } | ConvertTo-Json -Compress` 生成的载荷是
  `{"script":{"value":"\"\"\"One execute..."}}`，MCP 回 `Script must define a callable run() function.`
- **原因**：`Get-Content -Raw` 返回的字符串带着 `PSPath / PSDrive / Length` 等备注属性，
  `ConvertTo-Json` 把整个对象序列化，而不是当成字符串
- **修法**：**先转成纯字符串再拼载荷**
  ```powershell
  $script = [string](Get-Content Saved\one_call_boss2.py -Raw)
  @{ script = $script } | ConvertTo-Json -Compress | Set-Content Saved\script_args.json -Encoding ASCII
  ```
  （`@'...'@` here-string 直接赋值没有这个问题，所以第一版脚本没踩到）
- **教训**：**PowerShell 的"字符串"不一定真是字符串** —— 交给 `ConvertTo-Json` 之前先 `[string]`
- **出处**：2026-11-27，第一次从文件读脚本

## 120. GitHub 会拒绝缺 LFS 对象的推送（GH008）—— `GIT_LFS_SKIP_PUSH` 在它这里无效

- **症状**：`GIT_LFS_SKIP_PUSH=1 git push -u origin main` 报
  `remote: error: GH008: Your push referenced at least 1000 unknown Git LFS objects` /
  `pre-receive hook declined`，远程保持不动
- **原因**：GitHub 的 pre-receive 钩子**在服务端**校验：提交里只要引用 LFS 指针，对应对象就必须已经在远端。
  跳过本地 LFS 上传只能骗过本地 pre-push 钩子，骗不过 GitHub
- **数字（2026-11-27 实测）**：
  - 本地 `.git\lfs\objects` **5.55 GB**（7,527 个对象）
  - **`HEAD` 当前就引用了 5,200 MB** 的 LFS 文件（`Content/` + `Assets/` + `Binaries/` 共 5,361 个）
  - GitHub 免费额度 **1 GB 存储 / 1 GB·月流量** → 不只是"历史太大"，**光是当前内容就超 5 倍**
- **能走通的三条路**：
  1. **买 data pack**（约 $5 / 50 GB）后 `git lfs push --all origin` —— 唯一能完整推上去的办法
  2. **换远端**（GitLab 免费档的 LFS 额度更大）
  3. **推一个只含代码+文档的快照分支**（本工程用这条，见下一条）
- **教训**：**"跳过 LFS 推代码" 在 GitHub 上不成立。** 要判断能不能推，先算 `HEAD` 里 LFS 文件的**当前体积**，
  不是历史体积
- **出处**：2026-11-27，第一次尝试异地备份

## 121. 从"只含代码的快照分支"切回 `main`，`git checkout` 会拒绝或重写 5.2 GB

- **症状**：在 orphan 分支（`backup-code-*`）上，`git checkout main` 报
  `The following untracked working tree files would be overwritten by checkout: Assets/ ... Aborting`
  —— 因为快照分支里 `Content/`、`Assets/` 全是未跟踪文件
- **危险修法**：`git checkout -f main` 会**按 LFS 重新写一遍全部 5.2 GB 资产**；
  中途失败就留下一堆指针文本，等于把资源弄坏
- **安全修法（不碰工作区）**：
  ```powershell
  git symbolic-ref HEAD refs/heads/main   # HEAD 指回 main
  git read-tree HEAD                      # 只重建索引，不动工作区
  ```
  然后 `git status --porcelain` 应为 0 行
- **教训**：**切分支前先问"这次 checkout 会重写多少字节"** —— 大 LFS 仓库里 `-f` 不是"强制"，
  是"重下一遍"
- **出处**：2026-11-27，推完快照分支之后

## 122. LFS 不是"大资产进 git"的解药 —— 5.2 GB 照样超配额、照样推不动

- **症状**：`.gitattributes` 把 `*.uasset / *.umap / *.png / *.png…` 全挂上 LFS，看起来"处理过了"；
  结果仓库 **5.6 GB**、`main` 一个提交都推不上去、`lfs prune` 实测只回收 **400 MB**
- **数字**：`HEAD` 当前引用 **5,208 MB** LFS（5,361 个文件）；GitHub 免费 **1 GB**；
  7,527 个本地 LFS 对象里 **5,463 个是当前版本**（所以 prune 动不了它们）
- **根因**：LFS 解决的是 **git 对象膨胀**，不解决 **配额、上传体积、克隆成本**。
  "能不能用 LFS 存"和"该不该进 git"是两个问题，前者永远是"能"
- **修法（本工程已做）**：**不跟踪**，而不是"优雅地跟踪"
  - `.gitignore` 排除 `Content/` 和 `Assets/` 下所有二进制
  - 只提交文本：源码 / 文档 / 工具 / `.gltf` / `.json`
  - **重建路径写进 `Docs/ASSETS.md`**（Fab 包名、导入脚本、墨香源文件位置）——
    不然"重下得来"只是嘴上说说
- **教训**：**体积问题只能在"要不要进版本库"这一层解决。**
  判断标准不是"能不能压缩/LFS"，是"**丢了能不能重建**"：能重建的不进 git，不能重建的（源码、文档、参数）才进
- **出处**：2026-11-27，`main` 历史重建（NEXT-SESSION 第 81 节）

## 123. `StopPIE` 之后编辑器相机跑到 z = -25328，必须手动复位

- **症状**：一次调用里 `StartPIE → CaptureViewport → StopPIE`，返回的 `camera_after` 是
  `(3536, -8740, **-25328**)` —— 远在地底。人切回编辑器就是一屏黑（规则 3b 正是防这个）
- **原因**：PIE 在视口里运行会把视口相机交给游戏视角；停止时恢复的姿势不一定是 PIE 之前的那个
- **修法**：**PIE 的调用里，`StopPIE` 之后立刻 `SetCameraTransform` 回默认位，并回读确认**：
  ```
  SetCameraTransform({location: 8950,-6200,3900, rotation: 0,-2,0})
  GetCameraTransform  → 期望 8950,-6200,3900 yaw 0 pitch -2
  ```
  `Tools\Status.ps1` 会直接告诉你 `default view: yes/no`
- **教训**：**"截图好看"和"人的编辑器好看"是两件事**，PIE 之后尤其如此 —— 相机复位要写进调用里，不能靠记性
- **出处**：2026-11-27，C++ 闭环自证（NEXT-SESSION 第 83 节）

## 124. 「消息日志」窗口会被布局恢复回来 —— 强杀编辑器 = "已关闭"没被记住

- **症状**：`Docs` 里写着"绝不打开消息日志"（规则 6），它还是每次都在，浮在视口上挡画面，
  人被反复提醒到发火
- **原因**：UE 把**上次退出时的窗口布局**存进 `Saved/Config/...`，下次启动照原样恢复。
  我上次是 `Stop-Process` 强杀的 —— 编辑器没走正常退出流程，**"这个窗口已经关了"没被写回去**，
  所以每次都回来。而 `ui.ps1 -Action click` 在本机注入无效，按钮点不掉（只有 `PostMessage(WM_CLOSE)` 有效）
- **判断**：`Tools\Status.ps1` 现在有一行
  ```
  windows    : none
  ```
  出现 `message log` 就是它又回来了（检查是机器做的，不靠记性）
- **修法**：
  1. `PostMessage(WM_CLOSE)` 关掉（标题按 Unicode 码点匹配，`Status.ps1` 里有现成写法）
  2. `Tools\SetupLayout.ps1` 重新排版
  3. **关编辑器要走正常退出**（WM_CLOSE + 没有脏资产），否则下次照样恢复
- **教训**：**"绝不做 X"的规则，要配一个"X 现在存在吗"的检查**，否则规则只是希望
- **证实（2026-11-27 12:45）**：关掉窗口 → **正常退出**（WM_CLOSE、无脏资产）→ 重启后 `windows: none`，
  而 MapCheck 的警告照旧存在 —— 所以**不是 MapCheck 弹出它，就是布局恢复**。
  现在 `EditorGuard -Action restart` 也加了保险：重启后 +4s / +12s 各探一次，发现就 `WM_CLOSE` 并记日志
- **出处**：2026-11-27，被用户当场指出（第三次）