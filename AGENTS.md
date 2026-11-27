# AGENTS.md — 灵虚界（LingXuJie）

任何 agent 进入本工程先读这一份。它是 CoinRush 项目验证过的约定，按本工程改写了名字。

## ⛔ 最高优先级硬规则（2026-11-26 定，违反过多次，不再容忍）

**做地图/关卡相关的活，先读 [Docs/MAP-RECONSTRUCTION-SOP.md](Docs/MAP-RECONSTRUCTION-SOP.md)。**

**逆向/格式/素材的问题，去研究区查，不要在工程里重新分析：**
`C:\Users\tk\Desktop\moxiang-study\AGENTS.md` + `Docs\capability-report.md`。
研究区有自己的 git 和自己的规则（不碰 UE、不碰 MCP）。**两个工作区单向：研究 → 工程。**

1. **编辑器：可以自己启动，不许擅自关闭。**
   启动/重启用 `Tools\EditorGuard.ps1 -Action restart`（会等到 MCP 8000 端口就绪）；
   自检用 `-Action check`；重建用 `Tools\RebuildInEditor.ps1`（编辑器内重建）；
   验证用 MCP `StartPIE`。**关掉前必须问一句**——人可能正开着看画面。
   编辑器没开不是"待办"，是**该启动的信号**：要跑重建/验证就直接拉起来，不用请示。
2. **绝对不许用 `Tools\RunGame.ps1` 做日常验证**——它第 144 行会 `Stop-Process` 掉编辑器
   再起游戏，这就是"编辑器老被莫名关掉"的真凶。只有人明确说要整屏截图时才用。
3. **绝对不许改编辑器和内容浏览器的尺寸/位置。**
   - **每次 `EditorGuard -Action restart` 之后必须跑 `Tools\SetupLayout.ps1`** ——
     重启拉起来的编辑器默认是**最大化**的，不跑就等于改了尺寸（2026-11-26 又犯过一次）。
   - 布局：编辑器 `0,0 1494×864`、内容浏览器 `0,870 1494×516`、聊天 `1500,646 1040×740`。
   - 任何时候发现窗口不对，**只跑 SetupLayout，不要手动拖拽、不要最大化、不要双击标题栏**。
   - 截图前也跑一次，确保画面比例和平时一致。
3b. **每次操作结束，必须把编辑器视口恢复到默认观察位 —— 不许留在我自己的临时视角。**
   **人是一直盯着编辑器视口看的。我为了截图把相机挪到墙里、贴地、或地下，
   干完活就拍屁股走人，人打开就是一屏黑 —— 这是反复被批评的事。**

   **固定默认视角（兰州广场，正对红牌坊）：**
   ```
   位置 (8950, -6200, 3900)   yaw 0   pitch -2
   ```

   **⚠️ 必须用这个命令还原，不能用 CaptureViewport：**
   ```powershell
   powershell -ExecutionPolicy Bypass -File Tools\RebuildInEditor.ps1 `
       -Script Tools\reset_view.py -TimeoutSeconds 60 -WaitPattern 'VIEW: camera now'
   ```
   **`EditorAppToolset.CaptureViewport` 的 `captureTransform` 只对那一张截图生效，
   不改编辑器相机 —— 2026-11-26 犯过：截图好看，人的编辑器里还是黑的。
   真正改相机的是 `UnrealEditorSubsystem.set_level_viewport_camera_info()`，
   已封装在 `Tools/reset_view.py`。**

   **规则：**
   - **每批截图做完、或每次重建之后，最后一步必须跑 `Tools/reset_view.py`。**
   - 临时视角（墙内、地下、俯视 90°、极近距离）**只能用于这一次截图**，用完立刻还原。
   - **判断标准：如果人现在切到编辑器，看到的应该是一张能认出来的兰州街景。**
     看不清、发黑、全是墙 —— 就是没还原。


4. **一次只改一样**：改完 → `RebuildInEditor` → 读日志 → **MCP 截图** → 一句话结论 → 问下一步。
   **不许一口气改材质+布景+光照。**
5. **改坏了先还原到上一个可用状态**，不要在上一步的基础上继续试。
6. **用证据定位，不要猜**：先看 `Saved\Logs\LingXuJie.log` 的 `[LingXuJie]` 行和
   `Player ready at V(...)`，再读 `Source/LingXuJie/*.cpp`。同一个问题连试两次没成就停下重推。
   **读引擎日志用 MCP，不要打开「消息日志 / Message Log」窗口：**
   ```powershell
   '{"category":"","pattern":"LingXuJie","maxEntries":20}' | Set-Content Saved\mcp_args.json -Encoding ASCII
   powershell -ExecutionPolicy Bypass -File Tools\mcp.ps1 `
       -Toolset "EditorToolset.LogsToolset" -Tool "GetLogEntries" `
       -ArgsFile "Saved\mcp_args.json" -OutFile "Saved\mcp_log.txt"
   ```
   参数：`category` 留空=全部类别；`pattern` 正则（必填）；`maxEntries` 从末尾取几条。
   **开那个窗口会挡住视口、打断自动化点击，没有任何好处。**
7. **每一步都要给图片**，不要只描述。截图用 MCP `CaptureViewport` + `Tools\mcp_capture.py`。
8. **PIE 开着时建不了关卡**（`new_level -> False`），重建前先 `StopPIE`。
9. **每个块收尾必须更新 `Docs/NEXT-SESSION.md`**（写"做到哪、怎么验证的、下一步"），
   然后 `git commit`。**这是每个块的固定一步，不是"收工时"的判断**——
   判断会漏，清单不会。**上下文会被自动压缩，只有写进文件的东西才不丢。**
   别等人的提醒：一个块做完、验证完、截图完，就顺手写。
10. **写完状态后，回复末尾必须附「断点卡片」**，固定五行，不要自由发挥：

    ```
    —— 断点卡片 ——
    做到哪：<一行>
    验证：<日志行 / 截图路径 / 提交号>
    干净断点：是 / 否（原因）
    新会话开场：先读 AGENTS.md + Docs/MAP-RECONSTRUCTION-SOP.md，再读 NEXT-SESSION 第 N 节
    ```

    **为什么是五行固定格式**：人不需要临场问我"能不能新开"，卡片自己会说。
    完整版随时可重新生成：`python Tools/breakpoint.py`。
11. **人手动创建的文件，一律不许动 —— 包括桌面上看着像杂物的。**
   - 清理只清**我自己生成的**东西（日志、缓存、临时脚本、构建产物）。
   - 人的文件哪怕只有一行、哪怕名字叫「新建 文本文档.txt」，**也是他的东西**。
     看到有内容，**先说一句"这个我能收进工程吗"，等回答**，不要自己搬、不要自己删。
   - 2026-11-26 犯过：把人桌面上的 `新建 文本文档.txt`（9 个符箓名 + 一条边界规则）
     移进工程并删了原件，被明确批评。**已原样还原（233 字节校验一致）。**

12. **自动化的焦点规则（2026-11-26 23:00 人已放宽）：**
   **人明确说过："你在进行操作的时候可以优先抢占焦点。"**
   **所以 `RebuildInEditor.ps1`（激活编辑器 + 点控制台 + 粘贴 + 回车）从现在起是常规手段，
   可以放心用；不需要再为了"不抢焦点"绕路。**
   **但下面三条不变：**
   - **不许改编辑器和内容浏览器的尺寸/位置**（规则 3）；
   - **操作完必须把视口还原到默认观察位**（规则 3b）；
   - 能走 MCP 就不走键盘——不是怕抢焦点，而是 **MCP 更快、更不容易被对话框挡住**。

   **优先顺序（从上到下，能停在前一层就不要往下）：**

   | 优先 | 手段 | 为什么 |
   | --- | --- | --- |
   | **1** | **MCP 工具调用** | 跑在编辑器进程内，最快，不受对话框影响 |
   | **2** | **UI Automation 按名字点按钮** | 不依赖坐标 |
   | 3 | 控制台键入（`RebuildInEditor.ps1` / SlateInspector） | **已允许抢焦点**，但慢、会被模态框挡住 |
   | 4 | 坐标点击 | 仅当上面都不行，且日志里要明说 |

   **已修好的（2026-11-26）：**
   - `SetupLayout.ps1`：删掉 `SetForegroundWindow`，改用 `SWP_NOACTIVATE`；
     清理遮挡窗口从 `SW_MINIMIZE` 改为 `SW_HIDE`（后者不激活任何窗口）
   - `EditorGuard.ps1`：关崩溃报告器/恢复包，改成先 `PostMessage(WM_CLOSE)`，
     坐标点击只在 WM_CLOSE 无效时兜底

   **自查命令：**
   ```powershell
   python Tools/audit_focus.py
   ```
   **它会列出所有 `SetForegroundWindow` / `mouse_event` / `SendKeys` 的**调用**（自动排除 DllImport 声明）。
   新增脚本后跑一次。**

13. **清理是"到点算一次"，不是每块收尾都清。**（2026-11-27 定，工具 `Tools\Cleanup.ps1`）
   **默认只算不删，`-Apply` 才动手；每次 `-Apply` 会往 `Saved\cleanup.log` 追加一行。**

   - **触发**：`Saved` ≥ **1.2 GB** 或截图 ≥ **600 张** 时才算一次（脚本自己会报这两条）。
     **平时不用管**，更不要在每块收尾时顺手删——那会变成仪式，还会把证据删掉。
   - **白名单**：只动 `Saved\Screenshots`、`Saved\Logs`、`Saved\Autosaves`、`Saved\Crashes`、
     `Saved\Shader*`、`Saved\learn_ab*`、`Saved` 根目录的散件（txt/json/png/jpg/bmp/log）。
     **`Content / Assets / Binaries / Config / Source / Docs / Tools / .git` 一律不碰**；
     `Saved\Config`、`Saved\SaveGames`、`Saved\Collections` 也排除。
   - **保留**：14 天内的东西永远不动；截图另外保最新 120 张、日志保最新 15 个
     —— 那是文档里指着的证据。想立刻回收就调小 `-KeepDays`（脚本会先算给你看）。
   - **`Intermediate\Build`（约 4.2 GB）只能显式 `-IncludeIntermediate`**，且编辑器必须关；
     删一次 = 下次整编，**不要为了省几个 GB 日常清**。
   - **`.git\lfs`（约 5.5 GB）不在这条规则里**：要先 push 再 `git lfs prune --verify-remote`，
     是一次性、人拍板的动作。**没 push 就 prune = 删掉只在本地的资产，不可恢复。**
   - **一次性脚本不进 `Tools`**：新写的临时脚本放 `Saved\scratch\`（`Saved/` 不入库），
     `Tools` 只放会反复用的工具 —— 见 `Tools/README.md`。

## 开工流程（新会话第一件事，读文件前不要动任何东西）

0. **`Docs/LEARNING-INDEX.md` —— 唯一入口。** 按"你要做什么"查到该读哪一篇。
   **不要凭记忆，不要重新推导已经写下来的结论。** 那份索引里还有一份"已掌握结论清单"，可以直接当速查表。
   **判断"某个功能有没有开"之前，先跑 `python Tools\audit_project_config.py`** ——
   它输出 92 个配置键 + 来源文件。两次判断错误（"Lumen 是零""107 个遗留资产"）
   都是**凭印象不读文件**造成的，见 gotcha #78。
1. 读 `Docs/DECISIONS.md` —— **已定的 17 条 + 已否决的 7 条**。不要重新论证，不要"我觉得更好的方案"。
2. 读 `Docs/ASSETS.md` —— 哪些资产已导入、哪些在 Fab 库、署名要求。**不要再去 Fab 找包。**
3. 读 `Docs/P0-DESIGN.md` —— 要做什么（四张图、系统、数值、DoD）。
4. 读 `Docs/BACKLOG.md` —— 领**一条**任务（T1–T8），它自带验收标准。
5. 读 `Docs/NEXT-SESSION.md` —— **取编号最大的那一节**（目前是第 81 节：大资产退出 git —— 历史重启成"只有文本"的 14 MB），
   那里是"上次停在哪"。第 14 节及之前是历史。

**动手写任何工具/脚本之前，先读 `Docs/UE-TOOLSET-MAP.md` ——
引擎自带 217 个工具，很可能已经有了，别重复造。**

**然后按这一条做，做完再领下一条**。禁止一次改三样东西（材质 + 布景 + 光照）；
每步都要 `Tools/RebuildInEditor.ps1` 重建 + 截图 + `git commit`。

**最常见的两种"幻觉"，先自查**：

- 想摆园林/城门/池塘/贴花 → 见 `DECISIONS.md` D8，这些**默认不进生成流程**；
- 想重开一套新架构、新目录、新脚本 → 见 `DECISIONS.md` D12，关卡真源是
  `Tools/build_level.py` + `Assets/Map/p0_world.json`，**不要另起炉灶**。

## 协作风格（和人配合的方式，不是可选项）

人（项目所有者）已经明确要求过下面这些，照做：

1. **先说要做什么，再动手**。一句话说清"这一步改什么、预期看到什么"，不要闷头改完再解释。
2. **一次只做一个块**：改完 → 重建 → **截图** → 一句话结论 → 再问下一步。不要一口气改材质+布景+光照。
3. **每一步都给出可验证的证据**：日志行（如 `Done. N actors`）、截图路径、提交号。**没验证就不许说"做好了"。**
4. **图片放在回复里**，让人直接看到画面，不要只描述。
5. **做错了直接认**，说明原因 + 怎么修。不要悄悄重做、也不要找借口。
6. **不要反复试错刷屏**：同一个问题连续两次没成，停下来分析原因，而不是继续换参数硬试。
7. **不要为了自己方便改人的环境**（窗口尺寸/位置、编辑器开关、关卡之外的设置）。
8. **不确定就问一句**，尤其是"要不要花时间/花钱/改方向"这类决策。
9. **回答用中文、简短、先说结论**；技术细节放在结论之后。
10. 人说过"太慢""太乱""太花哨"时，**先减东西**，不要加东西。
11. **长操作前后各跑一次 `Tools\EditorGuard.ps1 -Action check`**（编译/重建/游戏/批量 py）；
    "日志没有输出 / 没有 Done" 时**先查崩溃**（Crash Reporter 会静默挡住一切自动化，见 gotcha #61），不要闷头重试。

## 0. 环境事实

| 项 | 值 |
| --- | --- |
| 引擎 | Unreal Engine **5.8.4**，`C:\Program Files\Epic Games\UE_5.8`（未在启动器登记） |
| 工程 | `C:\Users\tk\Desktop\lingxujie\LingXuJie.uproject`（仓库根 = 工程根） |
| 工具链 | VS2026 Community（MSVC 14.52），引擎自带 dotnet 10 |
| 阶段 | P0 单机垂直切片（先跑通闭环，再上联机） |

## 0.5 窗口布局（2560×1440）

**这就是人现在实际在用的布局**（2026-11-22 确认："以后窗口大小位置就差不多这样"），
随时可重跑 `Tools\SetupLayout.ps1`（`-DryRun` 只打印不移动）：

| 窗口 | 位置 | 尺寸 |
| --- | --- | --- |
| 编辑器（视口 / 主工作区） | 0, 0 | 1494×864 |
| 内容浏览器（浮动，就在编辑器下面） | 0, 870 | 1494×516 |
| Fab / 浏览器（Edge） | 1500, 0 | 1040×640 |
| DeepSeek Harness（聊天窗） | 1500, 646 | 1040×740 |

- 结构：**左列 = 编辑器 + 内容浏览器上下叠**，右列 = 浏览器在上、聊天在下；
  间距统一 6 px，底部都停在 1386（工作区 1392 减去 6），**没有任何窗口压到任务栏**。
- 屏幕是 2560×1440，工作区高 1392（任务栏约 48）。窗口不能超过工作区，否则底部状态栏/控制台被切掉、自动化点不到。
- 截图前先跑一次布局脚本；某个窗口没找到就跳过，不报错。
- 编辑器视口截图优先用 MCP 的 `EditorAppToolset.CaptureViewport`（干净、无 UI 遮挡），而不是整屏截图。
- 模态框（Fab 的 `Select a version`、`保存内容`、`恢复包`）会挡住一切自动化点击，见 gotcha #42/#43。
- 别把窗口位置改小了"顺手"挪回去：人是按这个布局看画面的，挪之前先问。
- **绝对不要为了自己的方便改窗口尺寸**（2026-11-23 又犯了一次：为了让 Fab 面板拉出右栏，把编辑器撑到 2200×1380，
  人看着很不舒服）。Fab 面板右栏被裁掉时，正确做法是 **把 Fab 标签页拖出来浮动/铺满、或按 Ctrl+滚轮缩放页面**，
  实在不行就问一句；**永远不要动编辑器的尺寸和位置**。

## 0.55 美术风格：古风（硬性，不用再提醒）

**一切视觉产出必须是东方古风 / 仙侠**，这是项目前提，不是每轮再确认的选项。

- 建筑与环境：飞檐、木构（柱/枋/窗棂）、夯土墙、青瓦/黛瓦、石台基、竹木、苔石、灯笼。
  参考分寸：唐/宋建筑比例 + 修仙氛围，不要日式鸟居/和风庭院，不要欧美中世纪/哥特。
- 配色：黛青、赭石、朱砂、月白、青金；金色只做点缀（灵光、器物边饰），不要大面积金属感。
- 材质：写实 PBR（官方 Megascans 优先），拒绝卡通/toon（已否掉，见 gotcha #50）、拒绝低模平涂。
- 道具与植被：中国/东亚题材优先；Fab 里优先挑 `region: Asia` / 中式园林 / 稻田竹篱这类。
  拿不准先问一句，别先做完再改。
- UI/HUD：毛笔感字体、暗底 + 细金边、竖排或仿篆刻标题；不要现代扁平卡片式按钮。
- 特效：灵气=青白流光、法术=符箓/剑气，不要科幻激光、霓虹。

## 0.6 画质与体积预算

- **贴图上限 2K**：`Config/DefaultDeviceProfiles.ini` 里把 World / NormalMap / Character 组锁到 2048，
  Specular / Effects 锁到 1024。1080p/60 的目标下 4K 只是浪费下载时间和显存。
- **Fab 下载一律选「中质量」**（=2K）。4K 版单套材质 50 MB 上下，2K 只要十几 MB，
  下载/导入时间差好几倍（`Mossy_Stone_Walkway` 就是误选了高质量，50.1 MB）。
- 帧预算目标：1080p / 60 fps / Frame ≤ 16.6 ms。**性能数字必须在编辑器完全关闭时测**（见 gotcha #47）。
> **接手新会话先读** [Docs/NEXT-SESSION.md](Docs/NEXT-SESSION.md)：当前状态、待办、环境速查。

## 1. 硬约束

0. **先查官方文档再动手**，顺序是：**本机 `Engine/Source` 源码 → 官方文档 → 实测**。
   能力地图与 API 出处见 `Docs/UE5-OFFICIAL-REFERENCE.md`。
   **🔴 找不到 API 时最快的办法：读引擎自带工具的实现** ——
   那 217 个工具只能调用**真实存在**的方法，所以它们本身就是最好的 API 示例
   （例：`SceneTools.merge_actors` 内部调 `StaticMeshEditorSubsystem.merge_static_mesh_actors`）。
1. 不要双击 `.uproject`，用命令行/`UnrealEditor.exe <upath>` 启动。
2. **编译前关闭编辑器**（Live Coding 持有互斥体，UBT 会报错）。打包必须走 `Tools\Package.ps1`。
3. 同一时间只允许一个 agent 操作编辑器；MCP 会话在编辑器重启后需重连。
4. **`.ps1` 一律 ASCII**（PowerShell 5.1 会把无 BOM UTF-8 当 ANSI）。
5. **大资产不进 git**（2026-11-27 起，见 NEXT-SESSION 第 81 节）：
   **`Content/` 整目录、`Assets/` 下所有二进制（png/jpg/obj/bin/glb/dds/hdr/fbx…）一律不入库**，
   由 `.gitignore` 挡住。**只提交文本**：源码、文档、工具、`.gltf`/`.json`（`build_level.py` 要读的参数与引用）。
   **理由**：Fab 有账号就能重下、墨香源文件在研究区、`Content/` 由 `build_level.py` 重建 ——
   而 5.2 GB 走 LFS 也照样超 GitHub 免费额度、照样推不上去（gotcha #120/#122）。
6. 不提交 `Binaries/ Intermediate/ Saved/ DerivedDataCache/ .vs/`。
7. 改完 C++ 必须跑 `Tools\BuildAll.ps1`，确认关卡仍能生成。
8. **提交在本地，推送按里程碑**：每个可验证的小步都 `git commit`（提交信息写清改了什么 + 怎么验证）；
   **不要每步都 `git push`**——完成一个大的迭代/里程碑（例如 M0.3 全部收口）再推一次远程。
   **大资产已不在 git 里（硬约束 5），所以 `main` 是正常可推的。**
   2026-11-27 把远程 `main` 重建成"只有文本"的新历史：
   **旧的 236 个提交（含 5.2 GB LFS）留在本地分支 `archive-lfs`，永不推、也不要 push 它**
   （推会被 `GH008` 拒，gotcha #120）。**想回收那 5.5 GB 空间，删掉 `archive-lfs` 再 `git lfs prune`。**
9. **编辑器默认不开，但由人决定关不关**：日常闭环是 `BuildAll`（编译 + Python 生成关卡）→ `RunTests` → `RunGame` 截图，
   全程不需要编辑器 GUI。只有要用 MCP / 手摆资产 / 调蓝图时才开编辑器，
   开之前确认没有构建任务（Live Coding 互斥体会让 `BuildAll` 失败）。
   同一工程别开两个实例（抢 `Saved/` 与资产锁）。
   **agent 不要自己关编辑器**：人可能正开着看画面/调东西，关掉就看不见了。
   需要关（例如要跑 `BuildAll`、要删被锁的资产）时**先问一句**；人不在、又非关不可时才自己动手，
   并在回复里说明为什么关、怎么重开。
   （编辑器开着时，它加载过的 `.uasset` 会被锁住，`Remove-Item` 报"文件正由另一进程使用"；
   关编辑器的正确姿势见 gotcha #51。）

## 2. 命令

```powershell
powershell -ExecutionPolicy Bypass -File Tools\BuildAll.ps1     # 编译 + 生成关卡
powershell -ExecutionPolicy Bypass -File Tools\BuildLevel.ps1   # 只生成关卡（需关编辑器）
powershell -ExecutionPolicy Bypass -File Tools\RebuildInEditor.ps1  # 编辑器常开时在内部重建
powershell -ExecutionPolicy Bypass -File Tools\SetupLayout.ps1      # 摆好编辑器/Fab/聊天窗的位置
powershell -ExecutionPolicy Bypass -File Tools\Cleanup.ps1          # 清理 Saved（默认只算不删，-Apply 才删）
powershell -ExecutionPolicy Bypass -File Tools\EditorGuard.ps1 -Action check    # 编辑器/MCP/模态框/崩溃自检
powershell -ExecutionPolicy Bypass -File Tools\EditorGuard.ps1 -Action dismiss  # 点掉 Crash Reporter / 恢复包
powershell -ExecutionPolicy Bypass -File Tools\EditorGuard.ps1 -Action restart  # 崩了就重启并等 MCP 端口
powershell -ExecutionPolicy Bypass -File Tools\EditorGuard.ps1 -Action watch    # 常驻：每 20s 自检，点掉模态框，新崩溃才重启
powershell -ExecutionPolicy Bypass -File Tools\EditorGuard.ps1 -Action stop     # 停掉常驻自检
powershell -ExecutionPolicy Bypass -File Tools\RunGame.ps1 -Seconds 20
powershell -ExecutionPolicy Bypass -File Tools\RunTests.ps1
powershell -ExecutionPolicy Bypass -File Tools\Package.ps1 -Config Shipping
powershell -ExecutionPolicy Bypass -File Tools\VerifyPackage.ps1
powershell -ExecutionPolicy Bypass -File Tools\MakeRelease.ps1 -Version v0.0.1
```

## 3. 代码地图

| 文件 | 职责 |
| --- | --- |
| `Source/LingXuJie/LXJGameMode.*` | GameMode（默认 Pawn = `ALXJCharacter`，HUD = `ALXJHUD`） |
| `Source/LingXuJie/LXJCharacter.*` | 玩家角色：越肩相机、冲刺/闪避/滑翔、技能输入、死亡回城 |
| `Source/LingXuJie/LXJCombatComponent.*` | 三个技能、灵力、冷却、伤害倍率（等级/装备加成落在这里） |
| `Source/LingXuJie/LXJHealthComponent.*` | 生命值、受伤数字、死亡事件（玩家/怪/木桩共用） |
| `Source/LingXuJie/LXJProgressComponent.*` | 经验与等级、升级加点、击杀结算 `GrantKillReward` |
| `Source/LingXuJie/LXJMonster*.{h,cpp}` + `LXJMonsterBrain.h` | 怪物基类、灵兽/邪修子类、纯函数状态机 |
| `Source/LingXuJie/LXJProjectile.*` | 邪修的远程法术弹 |
| `Source/LingXuJie/LXJItems.*` / `LXJPickup.*` | 物品表/掉落表；掉落物与自动拾取 |
| `Source/LingXuJie/LXJInventoryComponent.*` | 背包（堆叠）+ 武器/护甲槽 + 属性汇总 |
| `Source/LingXuJie/LXJHUD.*` | Canvas HUD：血/灵/技能栏/等级经验/掉落提示 |
| `Source/LingXuJie/LXJGround.*` | 程序化地面（高度场参数存关卡，几何在加载时自建；见 gotcha #59） |
| `Source/LingXuJie/Private/Tests/*.cpp` | 自动化测试（15 条，`Tools\RunTests.ps1`） |
| `Tools/build_level.py` | 关卡 + 材质 + 怪物生成（幂等重建） |
| `Tools/RunGame.ps1` | 起游戏、按 `-Sequence` 打输入、截图、读日志 |
| `Tools/PublishRepo.ps1` | 首次发布/换远程仓库（带 LFS 与体积预检） |

## 4. 完成定义

1. `BuildAll.ps1` 退出码 0，日志出现 `[LingXuJie] Done. N actors`；
2. `RunGame.ps1` 能截到非黑画面；
3. 玩法改动用 `-Sequence` 验证；
4. 改到逻辑必须跑 `RunTests.ps1` 且全绿；
5. 提交信息写清“改了什么 + 怎么验证的”；
6. **`Docs/NEXT-SESSION.md` 的最新一节已更新**（做到哪 / 怎么验证的 / 下一步），并已 `git commit`。
   **这一条和 1–5 平级，不是一个可以跳过的收尾动作。**

## 5. 已知坑

全部在 [`Docs/UE5-Gotchas.md`](Docs/UE5-Gotchas.md)（**122 条**）：继承 CoinRush 的 27 条（Live Coding 互斥、
LFS、MCP 会话失效、Smart App Control 拦 UBT、打包版 ProjectSavedDir 等），
加上 P0 阶段新增的 #28–#122（Canvas HUD 伤害数字、相机 yaw、UE5.8 编译两则、actor 清单排查、
agent 沙箱弄坏 UBT、SpawnActor 朝向、状态机"巡逻≠回家"、近战判定三连坑、自动曝光洗白画面、
多平行光竞争、程序化地面不进存档、Python 烘 StaticMesh 撞断言、崩溃报告窗口挡自动化、
编辑器内重建复用旧模块、重建后截图只有影子、Python 建材质的 Clamp 引脚、
**#65 CaptureViewport 不改视口相机、#66 PowerShell 把 `[Server]` 当通配符、
#67 PIE 开着建不了关卡、#68 墨香 OBJ 的 Y 会被取反、
#116 组件 override 优先于资产材质槽、#117 沙箱里 try/except 抓不住工具报错、
#118 CaptureViewport 必须传 annotations、#119 PowerShell 字符串不是字符串、
#120 GitHub 用 GH008 拒绝缺 LFS 对象的推送、#121 从快照分支切回 main 不能用 checkout -f、#122 LFS 不是"大资产进 git"的解药**）。**新坑继续追加**。

**能力地图与 API 出处在 [`Docs/UE5-OFFICIAL-REFERENCE.md`](Docs/UE5-OFFICIAL-REFERENCE.md)：**
我们这台 5.8.4 有哪些 MCP 工具集、视口相机的权威 API（引擎源码核实）、
**怎么用 Python 写自己的 MCP 工具集**（官方路径，比往控制台敲键盘可靠得多）、
以及查 API 的正确顺序（**先查本机引擎源码，再查官方文档，最后才实测**）。

系统知识在 [`Docs/UE5-Knowledge/`](Docs/UE5-Knowledge/README.md)。

## 6. 不要做

- 不把玩法逻辑写进蓝图（设计前提是 C++ + Python；蓝图只做胶水）；
- 不在构建产物目录手改文件；
- 不在没跑测试的情况下提交回合/数值逻辑。
