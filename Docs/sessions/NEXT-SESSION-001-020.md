# NEXT-SESSION 归档 · 第 1–20 节

> 从 `Docs/NEXT-SESSION.md` 分出来的历史（2026-11-27）。**当前状态看主文件。**

## 1. 当前状态（已验证）

| 项 | 状态 |
| --- | --- |
| 关卡 | `Done. 228 actors`（`Tools\BuildLevel.ps1`，命令行走通） |
| 天空 | 引擎体积云（`/Engine/EngineSky/VolumetricClouds/…`） |
| 植被 | Megaplants Bulrush 62 / Bracken Fern 12 / Giant Bamboo 8 + Megascans Tundra Grass 48（`BP_GrassField` 合并为 1 个 ISM） |
| 地面 | **已通过（2026-11-22）**：石板铺装（2K 苔石，`M_MS_Stone_Tiled` 平铺 6）+ 草地 + 起伏地形（`BP_Terrain` 程序化网格）；泥土路暂时关掉——平面上的异色矩形永远是色带，见 gotcha #56/#57 |
| 地面/台基 | Megascans Mossy Stone Walkway **2K**（`Content/Fab/…/Mossy_Stone_Walkway_ue4rcgxg/…`），4K 已彻底删除 |
| 屋顶 | Megascans Roof Tiles（2K） |
| 木构件/门窗 | Megascans Wood Planks（2K） |
| 墙面 | CC0 `clay_plaster`（Poly Haven 1K）—— **唯一剩下的非官方材质**（见待办 1） |
| 建筑 | `build_house()` 程序化 6 栋（石台基+夯土墙+木柱+木窗+门+双坡瓦顶+檐下木枋） |
| 非官方道具 | 全部停用（`USE_POLYFORK_PROPS = False`，表格保留） |
| 卡通渲染 | 已彻底删除，不再考虑 |
| 美术方向 | **古风 / 仙侠**，硬约束，见 `AGENTS.md` §0.55（不用再确认，也别做成和风/欧美/科幻） |
| 编辑器 | **现在是开着的**（人要看画面）。agent **不要自己关**，要关先问，见 `AGENTS.md` §1.9 |
| 窗口布局 | 人现在用的这套：左列编辑器 1494×864 + 内容浏览器在下，右列浏览器 1040×640 + 聊天 1040×740，间距 6 px；`Tools\SetupLayout.ps1` 已按这套写好（`-DryRun` 只打印） |

## 2. 本会话做完的两件事

### 2.1 4K 苔石 → 2K（原"待办 1"，已完成）

上个会话卡在"要在 Fab 面板里重装中质量版"上，其实**不用重装**：

- Fab 插件把下载的 zip 留在 `%LOCALAPPDATA%\Temp\FabLibrary\<uuid>\*.zip`，
  2K 版苔石 `mossy_stone_walkway_ue4rcgxg_2k_ue_mid.zip` 早就在本机缓存里（见 gotcha #53）。
- 已把三张 PNG 解到 `Assets/Megascans/mossy_stone_walkway_2k/`（LFS 入库），
  `Tools/build_level.py::megascans_stone_paths()` 首次构建时自动导入到
  `/Game/Fab/Megascans/Surfaces/Mossy_Stone_Walkway_ue4rcgxg/Medium/ue4rcgxg_tier_2/Textures/`。
  **重建不再需要联网**，换个新 clone 也能一次生成。
- 平铺系数 `tiling 6.0 → 3.0`：旧 4K 扫描覆盖 1x2 m，新 2K 覆盖 2x4 m，次数减半才保持石头的实际尺寸。
- 4K 的 `Content/Fab/Megascans/Surfaces/Mossy_Stone_Walkway_ue4rdbpg/`（5 个资产，51 MB）已删除；
  `Get-ChildItem Content -Recurse -Filter "*_4K_*"` 现在为 0。
- 贴图标志与 Fab 对齐：B `srgb=True/TC_Default`、N `srgb=False/TC_NormalMap`、ORM `srgb=False/TC_Masks`
  （用 `Tools/probe_texture.py` 复核，见 gotcha #52）。
- 截图：`Saved/Screenshots/stone2k_plaza.png`（村口广场，石板+苔藓正常，无粉红丢材质）。

### 2.2 删掉两个过时的工具脚本

`Tools/cleanup_4k.py`（原本用来删 4K）和 `Tools/downscale_textures.py`（mip bias 临时方案）已删除；
新增 `Tools/probe_texture.py`（打印贴图的 srgb / compression / 尺寸，排查贴图发白时先跑它）。

## 3. 待办 1：墙面材质换成官方（原"待办 2"，还没做）

**来源已定（2026-11-22 确认）：只用 Megascans（Fab 里选中质量 2K），不用 Poly Haven 等 CC0 替代。**
Fab 缓存的 7 个 zip 里**没有** plaster / rammed earth，所以这次必须真的下一次（要开编辑器、
用 Fab 面板搜 `clay plaster wall` / `mud plaster` / `rammed earth wall`）。下完先别急着关编辑器，
把 zip 从 `%LOCALAPPDATA%\Temp\FabLibrary` 复制出来解到 `Assets/Megascans/`，
再按 `megascans_stone_paths()` 那套写进 `build_level.py`——这样以后重建都不依赖 Fab。

- 落点：`Tools/build_level.py` 里 `"wall"` 那一项，现在是
  `make_textured_material("M_Wall_Plaster", "clay_plaster", tiling=6.0)`；
  换成 `tiled_megascans("wall", "M_MS_Wall_Tiled", <tiling>)` 之前，记得把新 surface 加进
  `MEGASCANS_TEXTURES` / `MEGASCANS_TEXTURE_IMPORTERS`（参考 `megascans_stone_paths()`）。
- 同一条链上 `"dirt"`（`M_Ground_Dirt`）和 `make_decal_material("M_Decal_Dirt", "clay_plaster")`
  也还在用 `clay_plaster`，换的时候一起考虑，别只换墙。

## 4. 环境与工具速查

```powershell
powershell -ExecutionPolicy Bypass -File Tools\BuildLevel.ps1        # 重建关卡（编辑器必须关着）
powershell -ExecutionPolicy Bypass -File Tools\BuildAll.ps1          # 编 C++（编辑器必须关着）
powershell -ExecutionPolicy Bypass -File Tools\RunTests.ps1          # 逻辑测试（15 条）
powershell -ExecutionPolicy Bypass -File Tools\RunGame.ps1 -Seconds 16 -Sequence "W:3" -OutFile Saved\Screenshots\x.png
powershell -ExecutionPolicy Bypass -File Tools\SetupLayout.ps1 -DryRun  # 先看当前窗口会挪到哪（不加 -DryRun 才真挪）
```

- **性能必须关编辑器测**（编辑器进程本身就吃掉 57–64 ms/帧，见 gotcha #47）
- 贴图看着发白/粗糙度不对：先跑 `Tools/probe_texture.py` 看 `srgb` 与 `compression`，别猜。
- **编辑器开着时**：它加载过的 `.uasset` 会锁住（`Remove-Item` 报"文件正由另一进程使用"），
  关卡也停在旧状态。要删/换资产就先关编辑器，别硬删。
- **关编辑器的正确姿势**：`PostMessage(主窗口, WM_CLOSE)` → 等「保存内容」出现 → 真实鼠标点**不保存**。
  **不要**用 MCP 的 `SlateInspectorToolset.Windows(action=close)`：它会把游戏线程卡在模态框上，
  对话框从此不响应任何输入，MCP 也一起挂掉（gotcha #51）。
- 沙盒是 `workspace-write` 时，注入到编辑器的鼠标/键盘会被 UIPI 丢掉（点不动、`PostMessage(WM_CLOSE)` 返回 False）；
  需要 GUI 自动化就切 `danger-full-access`，或者请人点一下。

## 5. 最近提交

```
(docs) 本次会话：4K→2K 换贴图 + gotcha #51–#53
2ebf5e4 Docs: window layout numbers match the non-overlapping layout actually in use
47228b9 Docs: handoff page for the next session (2K swap, official wall material, tool cheatsheet)
19ed549 Tools: keep the editor window inside the work area so its console stays clickable
```

## 6. 已入库的免费建筑资产（2026-11-22 晚，待导入）

四套 **Fab 免费**（已确认"Saved in My Library"，账号 `E`）：

| 资产 | 用途 | 链接 |
| --- | --- | --- |
| KHS – Korean Geonchunmun Gate | **山门广场**的主城门（石基拱门 + 城楼） | https://www.fab.com/listings/4c699223-a2b6-4dc5-9aa0-50cf3bc9aa75 |
| KHS – Gwolnaegaksa (In-Palace Offices) | **村落建筑**（模块化官署：房、院墙、门） | https://www.fab.com/listings/50ef2f6d-ea62-4174-a8bf-46bceec78cc8 |
| KCISA – Bogildo Island Seyeonjeong Pavilion | **后山道场**的亭子 | https://www.fab.com/listings/1b218798-b574-4353-82a7-0ae8bc253ff9 |
| KHS – Soswaewon Garden, Damyang | 村落庭院/水景素材（亭、门、院墙、溪谷、竹松、叠石） | https://www.fab.com/listings/b829ba85-0500-40e3-97eb-9850d94f9fbb |

**下一步（按顺序）**：
1. 编辑器 Fab 面板 → My Library 里下载这四套（体量可能很大，逐个确认 UE 版本兼容）；
2. 导入后**先把纹理按项目规矩压到 2K**（`Config/DefaultDeviceProfiles.ini` 已锁 2048），并检查碰撞/LOD；
3. 用 `build_level.py` 摆位：城门 → 山门广场，官署模块 → 村落，亭子 → 道场；
4. 出图给用户确认，再决定要不要**买**付费中式包（候选：Ancient Chinese City ¥50 / Modular Chinese Canal Town）。

**注意**：这四套是**韩国宫殿/园林**（KHS/KCISA），屋檐与斗拱比例偏朝鲜式；作为"远古/传奇感"的过渡资产可用，但要做到"一眼中国修仙"仍需纯中式素材替换。

## 7. 建春门已导入（2026-11-23 00:01）

- 来源：Fab `KHS - Korean Geonchunmun Gate`（免费），**选 5.7 版本导入**（5.8 不兼容提示 → 选"最接近的替代版本"），
  走的是 Fab 面板 →「添加到项目」，日志结尾 `LogFab: Fab workflow completed for asset 4c699223-...`。
- 落地：`Content/GeonchunmunComplex/`，**417 个资产 / 320 MB**，模块化：`SM_GCM_RoofA/B`、`SM_GCM_WallRoof02C`、
  `SM_GCM_Door01A/02A`、`SM_GCM_GongpoB`（斗拱）、`SM_GCM_YeonmokA`（椽）、`SM_SMJC_*` 门窗，另有 `Maps/Demo_GeonchunmunComplex`。
- ⚠️ **贴图超预算**：最大 `T_GCM_Ceiling_BC` 23.8 MB、`T_GCM_Roof03_BC` 12.6 MB（基本是 4K），
  按项目规矩要压到 2K —— 导入后先跑一遍 downscale（用 `TextureTools`/编辑器脚本，或直接在 Content Browser 里批量设 MaxTextureSize=2048）。
- ⚠️ **未提交到 git**：320 MB 进 LFS 代价太大，且可随时从 Fab 重下。要入库的话，**先压 2K 再提交**。

**下一步**：在 `build_level.py` 里按类路径 spawn 城门（拼装：石墙基座 + 拱门 + 城楼 + 斗拱 + 屋顶），
放在山门广场 `(0, -1500)` 处替代现在的三根方块柱；然后同样流程导入另外三套（官署 / 洗然亭 / 潇洒园）。

## 8. 免费村落素材已入库（2026-11-23，待导入）

Fab 库现在 14 个产品（3D 9 / 材质 5），新增四套，全部 **Personal ¥0**：

| 资产 | 角色 | 网格 | 链接 |
| --- | --- | --- | --- |
| KHS – Naganeupseong Walled Town | 民居（茅草院屋成组） | 206 | https://www.fab.com/listings/63f85871-436a-4c5b-a024-55f2a522c96d |
| KCISA – Korean Traditional Smart Materials Vol.1 | 地面（砖/石/草/土 智能材质） | 材质 | https://www.fab.com/listings/5b4d609d-d4ce-41f6-9d84-8409961939b6 |
| KCISA – Korean Traditional Heritage Props | 道具（罐/灯笼/条凳/农具） | 145 | https://www.fab.com/listings/c6193e7c-a21c-47d0-b19c-2f5f006fb2cc |
| tharlevfx – Water Materials | 水面材质（12+8 变体） | 材质 | https://www.fab.com/listings/063155ea-d9d2-4f29-b09f-33270b0bc861 |
| KHS – House Of Changwon | 院落住宅 | 228 | https://www.fab.com/listings/f663f513-e7ef-4bd3-b612-2f83ffb9cd9f |

**导入流程（已验证）**：Fab 面板 → 把编辑器拉宽到 >2000 px 才能看到右栏「添加到项目」→ 弹「与 5.8 不兼容」选 **5.7** →
下载分块写入 `%LOCALAPPDATA%\Temp\FabLibrary`（结束会清空）→ `LogFab: Fab workflow completed`。
导入后若要"整体摆进关卡"：`Tools/dump_level_layout.py` 采集演示图的变换 → 生成 JSON → `build_gate()` 同款代码重建。

**当前关卡状态**：只剩光照（12 actor），`main()` 在 `build_lighting()` 后 `return`，其余构建块都在下面注释着。

## 9. 交接（2026-11-23 晚，新会话从这里接）

### 当前状态
- 关卡 **95 个 actor**：`LXJGround` 地形 + 3 段路 + **桃源村 4 栋民居（68 件）** + 11 个灰盒（兰州 8 / 敦煌 1 / 秦皇陵 2）+ 光照。
  **城门、园林、水塘仍在生成流程之外**（代码还在 `build_level.py` 里，`build_gate()` / `build_garden()` 可随时调回来）。
- 地图**数据驱动**：`Assets/Map/p0_world.json` → `Tools/build_world.py` → `build_level.load_p0_world()`。
- 四张图：桃源村(60×60, 4 栋民居) / 兰州(90×90, 8 灰盒) / 敦煌(120×120, 野地) / 秦皇陵(80×80, Boss)，一条主路南北串联。
- 出生点 `PlayerStart` 在 **桃源村南口 (0,-10800) 朝北**（以前在兰州那边 (0,-5600)，等于出生在主城里）。
- 策划与参照已归档：`Docs/P0-DESIGN.md`、`Docs/P0-LAYOUT.md`；墨香参照与逆向资料全部在仓库外
  `C:/Users/tk/Desktop/moxiang-study/`（README 为总索引，含技术规格、贴图/UI/数值表/特效）。

### T1 已完成（2026-11-23，BACKLOG 已勾掉）
`build_world.py` 在 `zone["id"] == "taoyuan"` 时改走 `village_house.build_house()`，灰盒不再出现在桃源村；
`street_plot()` 给每块地皮算出「门朝街」的 yaw。每栋 **17 件**：石台基 1 + 墙 8（每面 2 开间）+ 角柱 4 + 门 1 + 门槛 1 + 屋顶 2 片。
日志：4 条 `house at <x>, <y>: 17 pieces` + `world: ... 68 house pieces` + `Done. 95 actors`。
图：`Saved/Screenshots/t1_village_gate.png` / `t1_village_street.png` / `t1_village_top.png`。

### 地基包已完成（2026-11-23 晚）：地面不再是「编辑器里才有」
- **根因**：`UProceduralMeshComponent` 的 section 不参与序列化，Python 建一次的地形存不进关卡，
  所以关掉编辑器再打开、或直接 `RunGame` 都是没地面的（gotcha #59）。
- **修法**：新 C++ 演员 `ALXJGround`（`Source/LingXuJie/LXJGround.*`）。高度场参数是 UPROPERTY（跟着关卡存），
  几何在 `PostRegisterAllComponents()` / `OnConstruction()` / `BeginPlay()` 里重建。`build_terrain()` 现在只负责
  spawn 它、写参数（尺寸/步长/平地矩形/草地材质）并调 `rebuild()`。**`BP_Terrain` 已经没人用了**（资产留着，可删）。
- **地形覆盖**：`Size 25000 cm`、中心 `(0,-500)` → x ±12500、y -13000..12000，四张图全在地面上
  （以前 17000/(0,-1500)：桃源村南 16 m、秦皇陵北 36 m 悬空）。
- **平地矩形改为读 JSON**：`load_p0_world()` 提到 `build_terrain()` 之前（旧顺序是「先建地形再读数据」，读到的平地永远是写死的那套）。
- **数据对齐**：主路改从村南口 `(0,-11600)` 起铺，穿过村子两排房子之间到兰州；
  兰州 8 栋灰盒收紧（`row_spacing` 1600→1100，最南一排 -6450，不再贴着桃源村北排 -7800）。
- **验证**：`BuildAll.ps1` 退出 0；冷加载探针 `Saved\probe_ground.py` → `sections=1 / 10201 verts / 20000 tris`；
  `RunGame.ps1` 从磁盘直接起游戏，出生点脚下就是石板路与草地。
  图：`Saved/Screenshots/g1_ingame_spawn.png`（游戏内出生点）/ `g2_village_street.png` / `g3_village_top.png` /
  `g4_world_overview.png`（全图）/ `g5_qinling_north.png`（秦皇陵北端地面）。

### 自检/自愈工具（2026-11-23 晚，崩溃之后补的）
`Tools/EditorGuard.ps1`：`-Action check` 一条命令看清「编辑器进程 / MCP 8000 端口 / Crash Reporter / 恢复包 /
最近崩溃目录」，健康时退出码 0；`-Action dismiss` 点掉挡住自动化的模态框（Crash Reporter 走「Close Without Sending」）；
`-Action restart` 崩了就以 MCP 模式重启并等端口；`-Action watch` **常驻**（每 20 s 自检，模态框立刻点掉，
只在检测到新崩溃目录时自动重启、最多 3 次；pid 写 `Saved\editor_guard.pid`），`-Action stop` 停掉。
`RebuildInEditor.ps1` 已内置：开跑前先 check（有模态框先 dismiss），
等待期间发现编辑器进程消失就自动 restart。**长操作前后各跑一次 check；"日志没输出"先查崩溃**（gotcha #61）。

### T2 桃源村定稿已完成（2026-11-23 晚，BACKLOG 已勾掉）
- **2 大 2 小**：房型按「开间」参数化（1 开间 = 2.46 m 墙板）。大房 `bays=(2,3)` → 4.9 × 7.4 m（19 件），
  小房 `bays=(2,2)` → 4.9 × 4.9 m（17 件），对角两块地皮放大房。屋顶半片的脊只有 6.88 m，
  3 开间的大房把屋顶沿脊向缩 7.3%（瓦纹拉伸看不出来；两对屋顶拼会更糟）。
- **院墙 + 柴门**：用包里原生的 `SM_SMJC_StoneWall01A`（2.46 × 0.17 × 2.05 m）围出 5 × 9 m 的前院，
  朝街那面留 1.5 m 门洞；柴门 = 两根 `SM_SMJC_Pillar` + 木过梁 + 木门板（引擎 Cube + 木材质）。
  每院 12 件，4 院共 48 件。
- **村口小门楼**：两柱（600 cm 跨）+ 一对屋顶（脊横跨路面），石砌柱础；为此把主路村口段收窄成 520 cm
  （`p0_world.json` 的路拆成两段），门柱才落在铺装外侧。
- **三件填充**：井（石圈 + 井口 + 木架，5 件）、栅栏（5 柱 + 2 道横杆，6 件）、柴堆（6 根柴，6 件）。
- **日志**：`4x house`（19/17/17/19 件）+ `4x courtyard`（各 12 件）+ `gatehouse 6` + 井/栏/柴堆 23 件 +
  `Done. 171 actors`。
- **图**：`Saved/Screenshots/t2_b3_entrance.png`（村口门楼）/ `t2_b3_street.png`（街上两排院墙）/
  `t2_b4_yard.png`（柴门近景）/ `t2_b4_top.png`（俯瞰）/ `t2_ingame.png`（游戏内街景）。

### T3 地面分层已完成（2026-11-23 晚，BACKLOG 已勾掉）
- 做法：**在材质里混合**，不铺色块。新材质 `M_Terrain_Blend`（`build_level.make_ground_blend_material`）：
  `|world X|` 作掩码 —— 路面以外 5.6 m 内是夯土（clay_plaster，乘 0.82/0.76/0.68 压成赭石色），
  5.6→12.5 m 平滑过渡到草地（grass_ground × 0.40/0.55/0.32），再叠一层 1/25 频率的纹理当作边界扰动，
  所以边界是**弯的、渐变的**，不是直边纸带（D8/否决清单要求的就是这个）。
- 挂载：`materials["terrain"]` 换成它，`build_terrain()` 照旧把它写进 `LXJGround.ground_material`。
- 验证：`Done. 171 actors`；游戏内/编辑器视口都正常（材质是存档资产，`RunGame` 从磁盘加载也生效）。
  图：`Saved/Screenshots/t3_blend.png`（街道俯瞰）/ `t3_eyelevel.png`（街面平视）/ `t3_edge.png`（横跨边界，
  泥土→草看不到硬边）/ `t3_ingame.png`（游戏内）。
- 坑：Python 里 `MaterialExpressionClamp` 的输入引脚连不上（编译失败、地面变棋盘格），改用 Max+Min 夹取；
  材质函数改代码后必须 `rebuild=True`（gotcha #64）。

### T4 兰州主城已完成（2026-11-23 晚，BACKLOG 已勾掉）
- **8 栋沿街**：复用 `village_house.build_house()`，全部 `bays=(2,3)`（4.9 × 7.4 m 临街店面，19 件/栋），
  不做院子（城市临街开门）。在 `build_world` 里由 `CITY_ZONE = "lanzhou"` 分支处理，计数单独打 `city buildings`。
- **4 个 NPC 位**：坐标来自 `p0_world.json` 的 `poi` 表（shop / quest / elder / healer，都在路两侧 x=±700），
  每个位置放一块 80×80×10 的青石标记（`build_npc_slot`）；T8 把标记换成会说话的人。
  注意 poi 表里还有 `pond`（水塘园林），它属于 D8 不进生成流程的那类，用 `NPC_POI_IDS` 白名单挡掉了。
- **1 个商店摊**：`build_stall`——四根木柱 + 柜台 + 平顶棚板，落在 shop POI 前方 2.5 m（6 件）。
- 日志：`stall at 950, -4800: 6 pieces` + 4 条 `npc slot` + `Done. 325 actors`。
  图：`Saved/Screenshots/t4_city_street.png`（兰州街）/ `t4_shop.png`（商店摊近景）/ `t4_ingame.png`（游戏内）。

### 下一个动作：BACKLOG T6（秦皇陵秘境）
Boss 石台 + 入口门道 + 1 只 Boss。`build_level.py` 里已有 `BOSS_PLATFORM`（`ground_patch("BOSS_Platform", ...)`，14×14 m），
入口门道可以用 `build_gatehouse` 改一版；Boss 本体是 T7/T8 的事，本轮先落标记。

### T5 敦煌野生已完成（2026-11-25）
- **改动**：`village_house.py` 新增 `build_monster_slot` / `build_pavilion`；`build_world.py` 加敦煌分支；
  `p0_world.json` 里敦煌 `buildings: 1 → 0`，新增 `mob1`–`mob7` 七个 poi。
- **怪位长什么样**：平底座 + 立桩（2 件），**故意做得和 NPC 的石板不同**——石板平躺，从路上看两者分不出来。
- **驿亭**：四柱 + 石础 + 双坡顶 + 一块基座板（11 件），**无墙**。跨度 420 cm（村口门楼是 600），
  所以檐口挑出于柱外——这是"休息亭"和"门"的区别。
- **数据驱动**：怪位和驿亭都从 `poi` 表读，靠 id 前缀（`mob`）区分；以后加怪只改 JSON。
- **沙地**：敦煌之前还是草地混合材质（NEXT-SESSION 早提醒过）。做法是**在地形材质里加一条世界 Y 方向的沙带**
  （−6600…6000，两端各 900 cm 渐隐，`clay_plaster` 乘沙色 0.86/0.74/0.52），
  **不是铺一块色块**——铺色块就是 D8 否掉的"纸带"。
- **日志**：`pavilion at 0, -300: 11 pieces, 420 cm span` + 7 条 `monster slot ... 2 pieces` +
  `world: ... 14 wilderness monster pieces` + `Done. 417 actors`，`BuildLevel.ps1` 退出 0。
- **图**：`Saved/Screenshots/t5_final.png`（驿亭 + 沙地 + 左侧一个怪位）/ `t5_camp.png`（换沙前的同一视角）。

### 新观测：敦煌沙地上有两团白/绿椭圆光斑（未修）
`t5_camp.png` 和 `t5_final.png` 在同一机位（0,−1400 朝北）都能看到路两侧各一团、对称、软边、中心过曝。
**不是这次沙地改出来的**（换沙前就有）。我查过 `build_ground_patches` 里的 puddle/water 片，
但那条链在 `main()` 里没被调，所以不是它。**待查**——下次单独开一块，别和布景混改。

### 下一个动作：BACKLOG T5（已完成），接下来 T6

### 观感问题（单独一条，别和布景混改）
1. 墙是城门包的粉红抹灰，**饱和度过高**（D7 低饱和）；可换 `M_Wall_Plaster` 夯土材质；
2. 屋顶檐口在 X 向比墙面线短 11 cm，近看有墙顶细边；
3. 门用浅蓝 `SM_SMJC_Door01A`，古风里太跳，`SM_GSB_DoorFrameA` 那套木门更稳；
4. 木构件（摊位/栅栏/柴堆）用的 `M_MS_Wood_Tiled` 偏灰白，不像赭石木料。

### 观感三件（单独一条，别和布景混改）
1. 墙是城门包的粉红抹灰，**饱和度过高**，与 D7「低饱和」冲突（可换成 `M_Wall_Plaster` 那套夯土材质）；
2. 屋顶檐口在 X 向比墙面线短 11 cm（`village_house` 里 slope 470 vs 墙 492），近看有墙顶细边；
3. 门用浅蓝 `SM_SMJC_Door01A`，古风里太跳，`SM_GSB_DoorFrameA` 那套木门更稳。

另注：院子里的**院墙/柴门**已按墨香新手村的读法做了；房子山墙开口是已知瑕疵（BACKLOG D-7）。

### 纪律（这次会话踩过的坑）
- **不要改编辑器窗口尺寸/位置**（`AGENTS.md` §0.5）。
- **改 `build_level.py` 一律用 edit 工具**，不要用 PowerShell 字符串替换（CRLF 失配已连续坑 5 次）。
- 一次只做一个块，先截图再继续；不要同时改材质+布景+光照。
- 参照《墨香》：**平地、一条街、两排房、低饱和、少装饰**，园林/城门这类"花哨"元素不要默认打开。
- 新会话**先读**：`AGENTS.md` → `Docs/DECISIONS.md`（已定的事，别重新论证）→ `Docs/ASSETS.md`（哪些资产已导入/在库里）→ `Docs/P0-DESIGN.md`（要做什么）→ 本文件第 9 节（停在哪）。
- **不要重复的分析**：Fab 免费资源筛选、村落包对比、墨香素材合法性、Lyra/完整工程的价值评估——结论都在 `DECISIONS.md` 第 4 节。
- 领任务看 `Docs/BACKLOG.md`（T1–T8，每条都有验收标准），一次只领一条。
- 每次收工：在 `Docs/NEXT-SESSION.md` 第 9 节更新"停在哪"，并 `git commit`。

---

## 10. 交接：墨香地图复刻（2026-11-26）

> **这一节取代第 9 节成为当前状态。** 项目方向已改为"用国服客户端的真实数据重建地图"，
> 之前手搓的 P0 四张图（桃源村/兰州/敦煌/秦皇陵）**已从生成流程里移除**，
> 代码仍在 `build_level.py` 里（`return` 之后），`p0_world.json` 也还在，可以随时恢复。

### 当前关卡状态（13 actors）

```
天空（SkyAtmosphere + SkyLight + 云 + 太阳，未动）
+ SM_Moxiang22_Terrain   墨香 22 号图真实地形，513×513，52 万面
+ M_Moxiang_Ground       tile_104_grass01 平铺 96 次
+ MX_PLAYERSTART         (47200, -22800, 3477)
```

**已验证：** 日志 `Player ready at V(X=47200.00, Y=-22800.00, Z=3477.00)` —— 角色站在地形上，没穿地。

### 关键数据来源

| 数据 | 位置 |
| --- | --- |
| 地形高度 | `C:/Users/tk/Desktop/moxiang-study/terrain/22.hfl.csv`（513×513，cm） |
| 建筑网格 | `moxiang-study/stm_exact/22_*.obj`（698 个，世界坐标） |
| 灯光 | `moxiang-study/tables/extra_lights.csv`（22.lfg 的 1016 盏） |
| 物件摆放 | `moxiang-study/tables/extra_objects.csv`（22.ofg 的 1145 个） |
| 地表贴图 | `moxiang-study/resources/dds/tile_*.dds` → 转 PNG |

### 生成链路

```
python Tools/build_map_obj.py --map 22      # hfl.csv + stm obj → ue_import/22_terrain.obj / 22_arch.obj
powershell -File Tools/RebuildInEditor.ps1  # 编辑器内重建（读 build_moxiang_map.py）
```

### 已踩平的坑（都记在 Docs/MAP-RECONSTRUCTION-SOP.md）

1. **OBJ 必须带 UV**，否则导入后三角面为 0
2. **绕序必须朝上**（`f a-b-c` / `f b-d-c`），否则碎成漂浮板块
3. **导入器把 Y 取反** → 网格在 `Y = -51200..0`，出生点必须在负 Y
4. **资产已存在时导入被跳过** → 先 `delete_asset`
5. **Nanite 网格不提供碰撞** → 必须 `set_nanite_settings(mesh, settings)`，只改属性无效
6. **多个 PlayerStart** → 建之前先销毁所有旧的
7. **DDS 头 UE 不认**（DXGI 71）→ 先转 PNG
8. **PIE 开着时建不了关卡** → 先 `StopPIE`

### 下一步（按优先级）

| # | 任务 | 备注 |
| --- | --- | --- |
| 1 | **修贴图观感** | 平铺太密（96 次看得出网格）+ 陡坡拉伸（需三向投影） |
| 2 | **加建筑** | 698 个 stm 网格合并成一个 OBJ，同一套流程 |
| 3 | **加灯光** | 1016 盏 lfg 灯光，先抽样 60 盏验证 |
| 4 | **加物件摆放** | 1145 个 ofg 物件，需要先把 .chr/.mod 模型导进来 |

### 纪律（这一节最重要）

- **编辑器常驻，不许关**；重建用 `RebuildInEditor.ps1`，验证用 MCP `StartPIE`
- **绝对不许用 `RunGame.ps1`** —— 它会 `Stop-Process` 掉编辑器
- **不许改窗口尺寸/位置**
- **一次只改一样**：改 → 重建 → 读日志 → **MCP 截图** → 结论 → 问下一步
- **改坏了先还原到上一个可用状态**，不要继续试
- **用证据定位**：看 `Saved/Logs/LingXuJie.log` 的 `[LingXuJie]` 和 `Player ready at V(...)`

**完整规则见 `Docs/MAP-RECONSTRUCTION-SOP.md`。**

---

## 11. 工作区拆分（2026-11-26 下午）

> **这是当前状态。第 10 节的地图复刻进度仍然有效，本节只讲"东西放哪了"。**

### 两个工作区

| 工作区 | 路径 | 职责 | 自己的 git |
| --- | --- | --- | --- |
| **研究区** | `C:\Users\tk\Desktop\moxiang-study` | 逆向、格式解码、数据提取、结论归档 | ✅ 本地仓库 |
| **工程区** | `C:\Users\tk\Desktop\lingxujie` | UE 关卡、模型/动画导入、玩法 | ✅ 原有 |

**单向：研究 → 工程。**

### 工具已按职责分家

| | 数量 | 内容 |
| --- | --- | --- |
| **工程 `Tools/`** | **32** | `build_level.py` / `build_moxiang_map.py` / `build_map_obj.py` / `build_world.py` / `chinese_house.py` / `village_house.py` / `draw_plan.py` / `breakpoint.py` / MCP 三个 / 22 个 `.ps1` |
| **研究 `Tools/`** | **573** | 全部 `decode_*` / `parse_*` / `extract_*` / `probe_*` / `audit_*` / `analyse_*` / 4 个反向 ps1 |

**分类标准：按"做什么"分。** 建 actor 的留工程，分析数据的去研究区。
**验证方式：** 解析每个剩余模块，确认没有 import 迁走的模块 → **0 断链**。

### 知识库已更新到今天

研区 `Docs/capability-report.md` 与 `technical-spec.md` §1 已重写，推翻 6 条旧结论：

| 旧结论 | 现在 |
| --- | --- |
| 骨骼层级未存储 | ❌ **就在 `dwParentObjectIndex`**（w_body01：192 根，190 根有父索引） |
| `.mod` 格式无规律 | ❌ 场景格式，5,267 零失败 |
| `.stm` 段间偏移未解 | ❌ 46,086 精确导出 |
| `.chx` 是碰撞体 | ❌ 文本动画集 |
| 布景 3,091 物件 | ⚠️ 实际 **4,245** |
| 布景 2,006 灯光 | ⚠️ 实际 **2,829** |

### 复刻能力结论

```
理解层  100%
素材层  ≈99.5%（唯一缺口 5 个音频，五版都没有）
实现层  ≈5%（引擎里只有地形 + 地表材质）
```

### 编辑器规则已更新

**允许 agent 自己启动编辑器**（`EditorGuard -Action restart`），**但不许擅自关闭**。
编辑器没开不是"待办"，是该启动的信号。

### 下一步

| # | 任务 | 在哪做 |
| --- | --- | --- |
| 1 | 修地表贴图观感（平铺太密 + 陡坡拉伸） | 工程区 |
| 2 | 加建筑（698 个 `.stm` 合并） | 工程区 |
| 3 | 加灯光（1,016 盏） | 工程区 |
| 4 | 清剩下约 35 处过时结论 + 合并 17 个 `skill-*` | 研究区 |
| 5 | 数据清理 ~2.3 GB（`anm_raw` / `stm_raw` / 重复 `model_obj`） | 研究区 |



## 12. 兰州城（地图 17）已进 UE（2026-11-26 15:50）

### 做到哪

**兰州城已经在地形上建起来了。** 这是第一座用**墨香原资源**复刻的城市。

### 关键突破：地图号→地名有表

`MapKindInfo.bin` 就是完整的地图目录，国服版在
`moxiang-study/tables/Resource_MapKindInfo.bin.csv`：

| 编号 | 名称 | | 编号 | 名称 |
| --- | --- | --- | --- | --- |
| 1 | 北京 | | 17 | **兰州** |
| 5 | 墨香城 | | 18 | 敦煌 |
| 6 | 洛阳 | | 35 | 黄河 |
| 12 | 长安 | | 70 | 少林寺 |

**以后不用再猜某张图是哪座城，查这张表。**

### 兰州（17）的数据

| 项 | 数量 |
| --- | --- |
| 建筑网格 | **1,563 个**（合并后 89,013 顶点 / 6.5 MB）|
| 地形 | 513×513 高度场，高差 0–9,269 cm |
| 布景 + 灯光 | 137 物件 + 17 盏 |
| 通行掩码 | 有 |

### 改动

- `Tools/build_map_obj.py --map 17` → 生成 `17_terrain.obj` + `17_arch.obj`
- `Tools/build_moxiang_map.py` 的 `build()` 改为：
  - 导入 `17_terrain.obj` → `SM_Lanzhou_Terrain`
  - 导入 `17_arch.obj` → `SM_Lanzhou_Arch`
  - 出生点 `(4000, -8800, 3684)`（该处地形高 3484，是兰州最平的区域之一）

### 验证

```
[LingXuJie] MX: terrain imported
[LingXuJie] MX: architecture imported = True
[LingXuJie] MX: player start at 4000, -8800, 3684
[LingXuJie] MX: Lanzhou placed, 2 surfaces
[LingXuJie] Done. 14 actors in /Game/Maps/LingXuJie
```

截图：`Saved\lanzhou_city.png`（城市全景）、`Saved\lanzhou_near.png`（街道尺度）

### 城市坐标分布（已量）

```
X:      0 .. 51,890 cm
Y(UE):  0 .. -46,364 cm      ← 注意 UE 导入会取反 Y
Z:      0 .. 11,269 cm
最密集: X 0–10,000 / Y -20,000–0
```

### 现在明显缺的三样

| 缺 | 表现 | 怎么补 |
| --- | --- | --- |
| **建筑贴图** | 全是灰白，只有一个平涂材质 | `.stm` 内嵌材质索引没拆开，需要**按材质分组导出** |
| **地面材质** | 草地（`tile_104_grass01`），原版是**土黄沙地/石铺广场** | 换 `tile` 里对应的地面图 |
| **灯光 / 天空** | 只有默认天光 | 17 盏灯的数据在 `tables/world_lights.csv` |

### 下一步（按优先级）

| # | 任务 | 说明 |
| --- | --- | --- |
| **1** | **按材质拆建筑贴图** | 最大观感提升。`build_map_obj.py` 现在把 1,563 个网格塞进一个 `usemtl`，要改成每个 `mtl` 一个组 |
| 2 | 换兰州地面材质 | 原版广场是沙土色，不是草 |
| 3 | 加 17 盏灯 + 天空 | 数据在 `world_lights.csv` |

### 已知问题（不是新坑，是旧代码）

```
collision setup failed: 'StaticMeshComponent' object has no attribute 'recreate_physics_state'
```
`place()` 里那三行是过时的 API 调用，**不影响** `complex-as-simple` 那条有效路径，
角色仍能站在地形上。下次顺手删掉。

### 12.1 建筑贴图已接上（2026-11-26 16:00）

**兰州城从"灰白块"变成"红瓦白墙的城"。**

### 做法

**关键发现：`stm_exact/17_*.obj` 里本来就有 `usemtl mtl_N` 分组，
`17.mtl` 里有材质序号→贴图的对应关系。** 之前的 `build_map_obj.py` 在合并时把 `usemtl` 丢了。

**改法只有一处：合并时按材质分组导出，不再全部塞进一组。**

**产物：**

| 产物 | 数量 |
| --- | --- |
| `Assets/Moxiang/ue_import/17_arch_*.obj` | **96 个**（按材质拆开，文件名带构件名）|
| `Assets/Moxiang/textures/*.png` | **95 张** |
| `17_arch.json` | 清单（组名 / obj / png / 是否 masked）|

**拆出来的构件名有实际意义：**
```
17_arch_jp_roof00/02/03/04.obj     屋顶
17_arch_jp_pillar00/01/02.obj      柱子
17_arch_jp_wall00..09.obj          墙
17_arch_jp_tent00/01.obj           帐篷
17_arch_store_01/02/03/11.obj      店铺
17_arch_fire_lamp_01.obj           灯笼
17_arch_54_nanju_wood00.obj        木构件
```

### 渲染流程（`build_moxiang_map.py`）

```
load_city_manifest(17_arch.json)
  → 每组 import_obj
  → 导入该组的 PNG
  → 建材质实例（opaque / masked 两个 master material）
  → 摆放
```

### 验证

```
[LingXuJie] Done. 109 actors in /Game/Maps/LingXuJie
[LingXuJie] Player ready at V(X=4000.00, Y=-8830.49, Z=3684.00) (level 1)
```

**actor 从 14 涨到 109**（96 个材质组各一个）。

截图：
- `Saved\lanzhou_textured.png` —— 城墙 + 红瓦群全景
- `Saved\lanzhou_gate.png` —— 飞檐、白墙、城墙细节

### 现在最明显的不足

| 不足 | 说明 |
| --- | --- |
| **地面还是草地** | 原版兰州是土黄沙地 / 石铺广场，不是绿草 |
| **屋檐偏粉紫** | 部分飞檐贴图颜色不对，可能要考虑 sRGB / 色彩空间 |
| **没有灯光** | 17 盏灯的数据在 `tables/world_lights.csv`，还没加 |
| **玩家角色不在画面里** | 出生点对，但可能被建筑挡住或在城外 |

### 一个必须记住的坑

**PIE 开着时 `build_level.py` 的 `new_level` 会返回 False**，
报 `RuntimeError: Could not create or load /Game/Maps/LingXuJie`。
**重建前先 `StopPIE`。**（gotcha #8 又踩了一次）

### 12.2 人眼视角 + 人物站位（2026-11-26 16:35）

**目标：能在编辑器里以人的尺度看城市，不用启动游戏。**

### 找到城里真正的开阔处

**写 `Tools/find_open_spot.py`：把 96 个材质组 OBJ 的顶点栅格化成占用图，
空地 + 周围建筑多 = 城中广场。**

**结果：UE (8950, -6200) 是最开阔的点（周围 67 个建筑，地面 3675 cm）。**

**注意坐标约定：** 建筑在 OBJ 里 Y 为正（0..46000），UE 导入后 **Y 取反** → UE Y -46000..0。

### 改动

`Tools/build_moxiang_map.py` 新增 `spawn_stand_in()`：
```python
角色类：LXJCharacter（C++ 类，圆柱身体 + 球头 + 立方剑的占位模型）
位置：  (8950, -6200, 3675)
标签：  MX_CHARACTER
```
**重建时自动放，不用手动摆。**

### 验证

```
[LingXuJie] MX: character from LXJCharacter at 8950, -6200, 3675
[LingXuJie] MX: stand-in character = True
[LingXuJie] Done. 110 actors in /Game/Maps/LingXuJie
```

截图：
- `Saved\plaza_yaw0.png` —— 街道 + **红牌坊**（最像原作的一张）
- `Saved\plaza_yaw90.png` —— 长屋 + 板车
- `Saved\char_v2_-7200.png` —— **人物站在广场，能judge尺度**
- `Saved\char_view_8950.png` —— 窗棂、门洞、货箱

### 观察结论

| 项 | 判断 |
| --- | --- |
| **街道尺度** | ✅ 合理，人物约 2m，城墙/长屋约 15-18m |
| **牌坊** | ✅ 红柱青瓦，形制对 |
| **窗棂 / 雕花壁板** | ✅ 细节在 |
| **地面平铺** | ⚠️ 96 次重复，近看有明显网格 |
| **材质光照** | ⚠️ 全平涂，没有 AO / 法线 |

### 下一步（只做一件）

**地面平铺太明显** —— 96 次重复在地面上形成可见网格。
把平铺次数降到 20-30，或加 UV 随机偏移。

## 13. 经验归档 + UE5 能力地图（2026-11-26 17:00）

### 一、本次新增的四条坑（`Docs/UE5-Gotchas.md` 共 68 条）

| # | 坑 | 一句话 |
| --- | --- | --- |
| **65** | `CaptureViewport` 不改编辑器视口相机 | **截图好看 ≠ 人的屏幕好看**。要改相机用 `set_level_viewport_camera_info` |
| **66** | PowerShell 把 `[Server]` 当通配符 | 报"0 个文件"但实际有 55 个。查这类目录用 `-LiteralPath` 或 Python |
| **67** | PIE 开着建不了关卡 | `new_level -> False`。重建前先 StopPIE，**脚本应自己检查** |
| **68** | 墨香 OBJ 的 Y 会被取反 | OBJ Y 为正 → UE Y 为负。定位错两次都是栽在这 |

### 二、新文档 `Docs/UE5-OFFICIAL-REFERENCE.md`

**内容：**

| 节 | 内容 |
| --- | --- |
| 一 | 环境事实（引擎源码核实：插件路径、模块位置） |
| 二 | **MCP 工具集现状**（实测我们的 5.8.4 有 5 个） |
| 三 | **自定义 MCP 工具集**（官方路径，5.8.4 可用） |
| 四 | **视口相机权威 API**（`UnrealEditorSubsystem.h` 原文签名） |
| 五 | Python 执行的三种路径对比 |
| 六 | 日志：用 MCP，别开窗口 |
| 七 | **`SlateInspectorToolset`** —— 被严重低估的能力 |
| 八 | Agent 技能：Markdown 形态即可 |
| 九 | **查 API 的正确顺序** |
| 十 | 官方文档索引 |
| 十一 | 和 Gotchas 的分工 |

### 三、最重要的发现

**我们这台 UE 5.8.4 已经具备写自定义 MCP 工具集的全部能力：**

```
Engine\Plugins\Experimental\ToolsetRegistry\Content\Python\toolset_registry   ← Python 模块在
Engine\Plugins\Experimental\ToolsetRegistry\Source\...\ToolsetDefinition.h    ← C++ 基类在
Engine\Plugins\Experimental\ModelContextProtocol                              ← MCP 服务器在
```

**官方文档（5.9）描述的 `PythonScriptingTools` 我们没有，但那条路我们不需要 ——
可以直接写自己的工具集，用 `@unreal.uclass()` + `unreal.ToolsetDefinition` + `@toolset_registry.tool_call`。**

**为什么重要：**

| 现在的做法 | 问题 |
| --- | --- |
| `RebuildInEditor.ps1` 往控制台**敲键盘** | 模态框 / 失焦 / 窗口被挡就失败 |
| 用 `CaptureViewport` 以为改了相机 | 它不改（坑 #65） |
| 重建前忘了 StopPIE | 失败（坑 #67） |

**改成工具集后这些结构性问题一次解决。**

### 四、下一个块的候选

| # | 任务 | 收益 |
| --- | --- | --- |
| **1** | **写 `Toolsets/LingXuJieTools.py`** —— 把 rebuild / reset_view / 读日志做成 MCP 工具 | ⭐⭐⭐ 消除"敲键盘"这一类脆弱 |
| 2 | 地面平铺次数 96 → 24 | ⭐⭐ 观感 |
| 3 | 用 `SlateInspectorToolset` 替代硬编码坐标点模态框 | ⭐⭐ 稳定性 |

### 五、验证

```
Docs/UE5-Gotchas.md          68 条（新增 65-68）
Docs/UE5-OFFICIAL-REFERENCE.md  10.4 KB / 259 行 / 11 节
AGENTS.md                    已引用新文档，规则 3b 写死在硬规则里
```

### 13.1 工具集已写 + 本地 API 镜像（2026-11-26 16:50）

#### 一、自定义 MCP 工具集（已写，待重启生效）

**位置：**
```
Content/Python/init_unreal.py            启动钩子（已存在，注册用）
Content/Python/lingxujie_tools/__init__.py
Content/Python/lingxujie_tools/level_ops.py
```

**提供的工具：**

| 工具 | 作用 |
| --- | --- |
| `LingXuJieTools.rebuild_level()` | 先 StopPIE → reload 构建器 → build → 存盘 → 复位相机 |
| `LingXuJieTools.reset_view(x,y,z,yaw,pitch)` | **真正移动编辑器视口相机** |
| `LingXuJieTools.get_view()` | 读当前相机 |
| `LingXuJieTools.list_actors(prefix)` | 列 actor |
| `LingXuJieTools.read_log(pattern, max_entries)` | 读日志 |

**⚠️ 需要重启编辑器才生效** —— `init_unreal.py` 只在启动时运行。
**规则 1 要求关编辑器前先问人，所以这一步挂着等确认。**

#### 二、控制台路径已彻底失效

**本次会话中途，`RebuildInEditor.ps1` 往控制台敲 `py` 完全不再执行**
（编辑器健康、无模态框、已知可用的 `reset_view.py` 也不跑）。
**这正是工具集要消灭的那类脆弱性。**

#### 三、两个关于相机的新事实

| 事实 | 说明 |
| --- | --- |
| **MCP 有 `SetCameraTransform` 工具** | **它能真正移视口**。之前我下结论说"只有 Python 能移"是错的 |
| **它的参数是普通 transform** | `{location:{x,y,z}, rotation:{pitch,yaw,roll}, scale:{...}}`，**不是四元数** |

**传四元数会把相机静默移到原点 (0,0,0)** —— 本次踩到，已恢复。

**验证过正确调用：**
```json
{"transform":{"location":{"x":8950,"y":-6200,"z":3900},
              "rotation":{"pitch":-2,"yaw":0,"roll":0},
              "scale":{"x":1,"y":1,"z":1}}}
```
读回确认：`{"location":{"x":8950,"y":-6200,"z":3900},"rotation":{"pitch":-2,"yaw":0}}`

#### 四、本地 Python API 镜像

**`Docs/PythonAPI/` —— 19 个文件 / 210 KB**

**只镜像本项目用到的类，不是整站。**理由：
- UE 整站数万页、随版本变、镜像下来又大又会悄悄过期
- **Python API 页是按版本生成的**，5.8 的页正好匹配本机引擎
- 它提供的是 **C++ 头文件给不了的东西：Python 名字与签名**

**已收录 18 个类**（`EditorAssetSubsystem` 超时、`MeshEditingLibrary` / `ToolAccessMode` 页面为空，已记录在 `Docs/PythonAPI/README.md`）。

**权威顺序（已写进 AGENTS.md 规则 1.0）：**
```
本机 Engine/Source 源码  >  Docs/PythonAPI（官方签名）  >  概念文档
```

### 13.2 本地官方文档已就位（2026-11-26 17:15）

#### 一、`Docs/PythonAPI/` —— 157 个文件 / 1.3 MB

**UE 5.8 Python API 类参考，按版本抓的，和本机引擎一致。**

**实测结果：108 个精选类全部处理完，0 失败。**
```
curated classes requested: 108
saved: 81    skipped: 27 (已存在)    failed: 0
耗时: 945 秒（约 16 分钟）
```

**抽查内容量：**
| 类 | 大小 | 方法数 |
| --- | --- | --- |
| `StaticMeshEditorSubsystem` | 26.7 KB | ~238 |
| `MaterialEditingLibrary` | 27.3 KB | ~262 |
| `LevelEditorSubsystem` | 8.8 KB | ~72 |
| `ToolsetDefinition` | 0.7 KB | 0（只定义基类） |

#### 二、`Docs/UEManual/` —— 4 个文件 / 72 KB

| 篇 | 大小 | 状态 |
| --- | --- | --- |
| `python-scripting.md` | 32 KB | ✅ |
| `unreal-mcp.md` | 31 KB | ✅ |
| `python-with-ai-agents.md` | 7.9 KB | ✅ |
| 其余 12 篇 | — | ❌ **slug 猜错，抓回空页** |

**这 3 篇正好是最相关的** —— 讲清了工具集与 skill 怎么写。
**剩下 12 篇（nanite / material-editor / landscape 等）要补的话，得先去文档站确认准确 URL。**

#### 三、为什么不全镜像（有实测数据支撑）

| 项 | 数字 |
| --- | --- |
| Python API 类总数 | **11,675** |
| 单页抓取耗时 | **约 9.5 秒** |
| **全量估算** | **约 31 小时** |
| **精选子集（108 类）** | **16 分钟** |

**全量里绝大部分是 AnimNode_*（动画图节点）和 CameraShake*（镜头抖动），
本项目一个都用不到。**

#### 四、索引文档

**`Docs/LOCAL-UE-DOCS.md`** —— 写清了：
- 两个目录各有什么
- 为什么不镜像整站（带实测数字）
- 权威顺序
- **引擎升级后怎么重跑**

#### 五、脚本

| 脚本 | 用途 |
| --- | --- |
| `Tools/python_api_classes.py` | 精选类清单（改这里就改抓什么） |
| `Tools/mirror_python_api_list.py` | 按清单抓，**可重复跑，已存在的跳过** |
| `Tools/mirror_python_api_bulk.py` | 全量抓（实测太慢，留作参考） |
| `Tools/mirror_manual_pages.py` | 手册摘录（`PAGES` 字典里改 slug） |

## 14. UE5 学习：控制台真相 + 动画系统调研（2026-11-26 17:35）

### 一、控制台三种模式的真相（已写进 `Docs/UE5-OFFICIAL-REFERENCE.md` 第五节）

编辑器底部输入框可切 `Cmd` / `Python` / `Python (REPL)`：

| 模式 | 适合 |
| --- | --- |
| Cmd | 跑脚本文件（`py "..."`） |
| Python | 一行操作 |
| **Python (REPL)** | **探 API 最好用**（`dir()`、试属性） |

**🔴 但换模式不解决抢焦点。**焦点问题来自"自动化要先点输入框"，
三个模式一样。**人在操作别的窗口时，`py` 命令完全不执行，日志里连 `Cmd:` 都没有 ——
2026-11-26 被这个误导过，以为控制台坏了。**

**可靠性排序：**
```
① MCP 内置工具（SetCameraTransform 等）  ← 不需要焦点，已跑通
② 自定义 MCP 工具集                      ← 不需要焦点，待重启
③ 控制台敲 py                            ← 需要焦点，最脆弱
```

### 二、动画系统调研结论（新文档 `Docs/UE5-ANIMATION.md`）

**核心发现：Python 能**读**动画轨道，不能**写**。**

| 能力 | Python 可达 | 依据 |
| --- | --- | --- |
| 读原始轨道 | ✅ | `AnimationBlueprintLibrary.GetRawTrackPositionData`（69 个 BlueprintCallable） |
| **写原始轨道** | ❌ | `IAnimationDataController` 在 `Developer/AnimationDataController`，**BlueprintCallable = 0** |

**核实的硬数据：**
```
AnimDataController.cpp            78,424 字节  BlueprintCallable = 0
AnimationBlueprintLibrary.h       48,818 字节  BlueprintCallable 69 处
  含 GetRawTrackPositionData: True
  含 SetRawTrackPositionData: False   ← 关键不对称
```

**→ `.anm` 导入器必须走 FBX 中转：**

```
墨香 .anm → 解析轨道 → 写 FBX → AssetImportTask + FbxImportUI 导入
                                    ↑ 这一步 Python 完全可达
```

**不需要改引擎、不需要 C++。**

### 三、下一轮的最小验证（不要一上来写完整导入器）

```
1. 挑最短的 .anm
2. 解析出 1 根骨骼的 3 个关键帧
3. 手写最小 FBX（ASCII，几十行）
4. Python AssetImportTask 导入
5. 编辑器里确认：时长对、骨骼名认得出、有动作
```

**过了再放大到 4,056 个。**

### 四、还没搞清的关键参数（在研究区查，不用重新逆向）

| 问题 | 影响 |
| --- | --- |
| `.anm` 帧率 | FBX 时间轴怎么填 |
| 旋转是四元数还是欧拉角 | FBX 怎么序列化 |
| 骨骼名是否与 `.mod` 一致 | 不一致会丢轨道 |
| `.chx` 怎么关联多个 `.anm` | 一套动作可能拆多文件 |

### 五、本轮新增文件

| 文件 | 内容 |
| --- | --- |
| `Docs/UE5-ANIMATION.md` | 动画调研结论（6.9 KB） |
| `Tools/read_animation_source.py` | 读引擎头文件，列 BlueprintCallable |
| `Tools/find_animation_write_path.py` | 定位动画写入接口 |
| `Tools/mirror_animation_api.py` | 抓 34 个动画类 API 页 |
| `Docs/PythonAPI/` | 现在共 **157 + 34 = 191 篇** |

### 14.1 工具集跑通了 + 22 个工具集（2026-11-26 17:50）

#### 一、自定义工具集**已注册并可用**

```
[LingXuJie] TOOLS: registration returned True
[LingXuJie] TOOLS: classes -> ['LingXuJieTools']
```

**实测四个工具：**
```
get_view    → "8950, -6200, 3900 yaw -4 pitch -8"
list_actors → ["MX_CHARACTER (LXJCharacter)", "MX_LZ_...", ...]
reset_view  → "camera at 8950, -6200, 3900 yaw 0 pitch -2"
（rebuild_level 未测，逻辑同上）
```

**窗口图验证：`Saved\tool_verified.png` —— 牌坊视角正确。**

#### 二、5.9 文档与 5.8.4 的**三处差异**（照抄会失败）

| 5.9 文档 | 5.8.4 实际 |
| --- | --- |
| `@tool_call(mode=unreal.ToolAccessMode.WRITE)` | ❌ **没有 `ToolAccessMode`**，`tool_call` 是裸装饰器 |
| `-> list` | ❌ 报 `missing specification for contained type`，**必须 `list[str]`** |
| `@staticmethod` | ✅ 一致 |

**报错原文：**
```
module 'unreal' has no attribute 'ToolAccessMode'
Type <class 'list'>: missing specification for contained type
```

#### 三、发现 16 个 Python 工具集（之前完全不知道）

**注册后 `list_toolsets` 从 5 个变成 22 个。**

| 类别 | 工具集 |
| --- | --- |
| **场景** | `SceneTools`（当前关卡操作） |
| **Actor** | `ActorTools` |
| **资产** | `AssetTools` |
| **材质** | `MaterialTools` / `MaterialInstanceTools` |
| **网格** | `StaticMeshTools` / **`SkeletalMeshTools`** ← 动画要用 |
| 其他 | `TextureTools` / `DataTableTools` / `DataAssetTools` / `CurveTableTools` / `StringTableTools` / `PrimitiveTools` / `ObjectTools` / `BlueprintTools` |
| 编排 | `ProgrammaticToolset`（串其他工具，**不是通用 Python 执行**） |

**所以我之前写「只有 5 个工具集」是错的 —— 那 5 个是 Python 侧还没加载时的状态。**

#### 四、`.anm` 旋转轨道解出（研究区）

**见 `moxiang-study/Docs/reverse-engineering/anm-rotation-solved.md`。**

**结论：24 字节记录 = `[索引][单位四元数 x,y,z,w][填充 0]`。**
**656/656 条记录长度为 1.0，第五浮点恒为 0。**

**这条解开之前只有位移+缩放，角色弯不了腿；现在是完整骨骼动画。**

#### 五、下一步（工具已经好用了）

| # | 任务 | 阻塞 |
| --- | --- | --- |
| **1** | 写 `.anm` → FBX 最小验证 | 需要确认帧率 |
| 2 | 地面平铺 96 → 24 | 无 |
| 3 | `rebuild_level` 实测 | 无 |

## 15. UE5 能力地图：217 个现成工具（2026-11-26 18:00）

### 一、本轮最重要的收获

**引擎自带 **217 个 MCP 工具**（16 个 Python 工具集），其中三个直接改变方案：**

| 发现 | 影响 |
| --- | --- |
| **`SkeletalMeshTools.import_file(import_animations=True)`** | **动画导入现成就有**，不用写自定义导入器 |
| **`SceneTools.merge_actors`** | 96 个材质组 actor 可以合并成一个 |
| **`MaterialTools.get_expression_input_names`** | 能查真实引脚名，解决 gotcha #64 |

**`import_file` 的 docstring 原文：**
> `import_animations`: When True, create AnimSequence assets for any animations contained in the file.

**所以 `.anm` 的完整路径变成：**
```
.anm → FBX → SkeletalMeshTools.import_file(import_animations=True)
          → Skeleton + SkeletalMesh + AnimSequence 全出来
```

**不需要写 C++、不需要写自定义导入器。**

### 二、新文档 `Docs/UE-TOOLSET-MAP.md`

**内容：**
- 217 个工具的分布
- 三个关键发现的完整签名
- 各工具集速查（场景 19 / 骨骼 22 / 材质 22 / 静态网格 15…）
- **"原来打算写、现在不用写"的对照表**
- 怎么查某个工具的确切签名

### 三、唯一还必须自己写的

```
.anm → FBX      ← 格式转换，没有现成工具
```

**其他全部有现成的。**

### 四、教训（已写进文档）

**我在这项目上花大量时间手写工具，而引擎里早有 217 个。**

**以后接手 UE 工作的第一步应该是：**
```
1. list_toolsets
2. 读对应工具集的 .py 源
3. 再决定要不要自己写
```

### 五、下一步

| # | 任务 | 依赖 |
| --- | --- | --- |
| **1** | **`.anm` → FBX 最小验证** | 确认帧率、旋转坐标系 |
| 2 | 用 `SkeletalMeshTools.import_file` 导入那个 FBX | 1 |
| 3 | 用 `get_bone_names` 比对 `.mod` 骨骼名 | 2 |
| 4 | 用 `merge_actors` 合并 96 个建筑 actor | 无 |
| 5 | 地面平铺 96 → 24 | 无 |


## 16. UE5 学习收官：glTF 方案 + 能力自评（2026-11-26 18:20）

### 一、"不遗忘"的机制

**新增 `Docs/LEARNING-INDEX.md`（5 KB）—— 唯一入口。**

**结构：**
- 第一节「按问题查」：**你要做什么 → 读哪一篇**（9 行速查）
- 第二节：五份核心文档的分工
- 第三节：三道防遗忘机制（AGENTS.md 开工流程 + 本索引 + 结论先行）
- 第四节：**已掌握结论清单**（可当速查表直接用，不用重新推导）
- 第五节：坐标系与常量速查

**已写进 `AGENTS.md` 开工流程第 0 步** —— 强制新会话先读它。

### 二、动画方案定了：**glTF，不是 FBX**

| | FBX | **glTF** |
| --- | --- | --- |
| Python 写 | ❌ 需 Autodesk SDK | ✅ **`json` 就够** |
| 结构对应 | 要转换 | ✅ **`Translation/Rotation/Scale` 正好三条轨道** |
| UE 导入 | `FbxImportUI` | ✅ `import_asset(factory=None)` 走 Interchange |

**决定性证据：`GLTFAnimation.h` 的 `EPath` 枚举就是 `Translation / Rotation / Scale`，
和我们解出的 `.anm` 三条轨道一一对应。**

**新文档 `Docs/ANM-TO-ENGINE-PLAN.md`。**

### 三、🔴 一个坏消息：不能只转动画

**`InterchangeGltfAnimation.cpp` 第 729 行：**
```cpp
UInterchangeSkeletalAnimationTrackNode* AcquireTrackNode(
    const FString& SkeletonNodeUid, FAnimationTimes& AnimTimes)
```

**动画轨道要绑 `SkeletonNodeUid`，而 skeleton node 来自**带蒙皮的网格**。**

**所以必须：`.mod`（网格+骨架+蒙皮）**和** `.anm`（轨道）一起转进同一个 glTF。**

### 四、新的关键未知：`.mod` 有没有蒙皮权重

**`mod-format.md` 提到「蒙皮/密集网格」段，但**没记权重结构**。**

**探查结果（`Tools/probe_mod_skin.py`）：**
```
样本 jp03_dht00.mod  5,203 字节
  5 对象 / 1 网格 / 4 骨骼
  4 个骨骼标记 + 1 个网格标记
  网格附近「小字节密度」21.5%   ← 可能有骨骼索引，但不确定
```

**这个要专门解，是下一步最关键的逆向任务。**

### 五、能力自评（本轮结束）

**见下方回复的完整评估。**

### 六、下一步

| # | 任务 | 类型 |
| --- | --- | --- |
| **1** | **研究区：解 `.mod` 的蒙皮权重** | 逆向 —— **最关键的阻塞** |
| 2 | 研究区：确定 `.anm` 帧率 | 查数据 |
| 3 | 工程区：`.mod` → glTF 最小验证（4 骨骼的 jp03_dht00）| 实现 |
| 4 | 工程区：加一条动画进同一 glTF | 实现 |

### 16.1 `.mod` 蒙皮调研：两条确定结论 + 一个假候选被排除（2026-11-26 18:35）

#### 一、确定的两条

**① 块长度字段**不包含**自己那 8 字节头**

```
验证: jp03_dht00.mod
  size 含头   → 识别出 0/5 个对象类型  ❌
  size 不含头 → 识别出 5/5             ✅
正确走法: offset += size + 8
```

**这条以前没写清，导致我第一遍走法完全错（对象类型全是 0x0）。**

**② 网格载荷前 36 字节是头，+36 起是法线（单位长度），之后是顶点**

**头部第 4 个字（+12）：道具 = 0，角色 = 4 —— 很可能是每顶点骨骼影响数。**

#### 二、一个假候选被**排除**（这是有效进展）

**`w25260.mod` 某段 u16 全 < 骨骼数（38），看起来像骨骼索引。**

**批量比对十几个模型：**

| 模型 | 骨骼 | 顶点数 | 段最大值 | 判定 |
| --- | --- | --- | --- | --- |
| **w25260** | 38 | **32** | **31** | **= 顶点数-1** ✅ |
| 其他 | — | 变化 | 62000+ | 落在浮点区 |

**→ 那是**顶点索引**，不是骨骼索引。**

**如果按它写导入器，会在第 2 个模型上崩，且很难查。**

#### 三、蒙皮权重**仍未解出**

**新文档 `Docs/MOD-SKIN-STATUS.md` —— 明确标注"未解完"，不编结论。**

**下一步该做（不是猜，是统计）：**
```
扫几百个模型，用「取值范围 vs 数量关系」判定
  · 骨骼索引：最大值 = 骨骼数-1，数量 = 顶点数 × 影响数
  · 三角形索引：最大值 = 顶点数-1，数量 = 三角形数 × 3
```

#### 四、重要：即使蒙皮解不出，动画方案也不会死

| 情况 | 应对 |
| --- | --- |
| 没有蒙皮权重 | 改用**刚体分段**（每骨骼段一个网格，按骨骼变换移动）|
| 观感 | **墨香是 2003 年低模，刚体分段可能反而更接近原作** |

**所以这是"做得像不像"的问题，不是"做不做得成"。**

#### 五、本轮新增

| 文件 | 内容 |
| --- | --- |
| `Docs/MOD-SKIN-STATUS.md` | 蒙皮进度（诚实标注未解完） |
| `Tools/dump_mod_mesh.py` | 走对象列表，验证长度语义 |
| `Tools/dump_mod_payload.py` | dump 网格载荷 |
| `Tools/scan_mod_index_ranges.py` | 批量统计索引范围 |
| 研究区 `mod-format.md` | 已补充块长度语义 + 蒙皮状态 |


## 17. UE5 系统学习：六块完成 + 掌握度自评（2026-11-26 18:50）

### 一、本轮完成的六块（全部引擎源码核实）

| 块 | 文档 | 核心结论 |
| --- | --- | --- |
| **1. 核心架构** | `UE5-CORE-ARCHITECTURE.md` (8.5 KB) | 继承链、生命周期、Gameplay 五类职责 |
| **2. 子系统** | `UE5-SUBSYSTEMS.md` (6.9 KB) | 四层按寿命选；`GameInstanceSubsystem` 直接继承 `USubsystem`，所以跨关卡存活 |
| **3. 渲染** | `UE5-RENDERING.md` (6.9 KB) | 两套 Nanite 结构；**Fallback 网格就是碰撞来源** |
| **4. 碰撞** | `UE5-COLLISION.md` (5.9 KB) | Enabled / 通道 / Response 三组正交 + CTF 怎么选 |
| **5. 四域调查** | `UE5-OTHER-DOMAINS.md` (7.8 KB) | 音频 186 KB / UI 294 KB / 网络 350 KB / 资产 196 KB |
| **6. 资产管线** | `UE5-ASSET-PIPELINE.md` (9.6 KB) | **引用链实测** + 软引用三态 + **Python 无异步加载** |

### 二、实测验证过的硬数据

```
SM_Lanzhou_Terrain:
  Nanite        = false
  三角形        = 524,288    (= 512×512×2)
  顶点          = 263,174
  依赖          = [NavigationSystem, InterchangeEngine, WorldGridMaterial]

Content/Moxiang 资产 298 个:
  SM_LZ_*  = 96   ← 与清单完全一致
  M_LZ_*   = 95
  jp_*     = 49   ← 旧构建遗留
  17_*     = 12   ← 旧构建遗留
```

### 三、新增的两条能力

| 能力 | 怎么做 |
| --- | --- |
| **查任意资产的引用链** | `AssetTools.get_dependencies` / `get_referencers` |
| **找出遗留资产** | 清单 vs 磁盘比对（不能凭名字对不上就删）|

### 四、发现的边界

**Python 侧没有异步加载** —— `AssetTools` 只有 `load_asset`（同步）。
**运行时资产管理必须 C++。** 编辑器自动化能用 Python，运行时不行。

### 五、掌握度自评（六块 + 已有）

| 域 | 掌握 | 证据 |
| --- | --- | --- |
| **编辑器脚本 / MCP / 工具集** | 🟢 **90%** | 自建工具集跑通，217 个工具逐条读过 |
| **核心架构** | 🟢 **80%** | 继承链、生命周期、复制标志都查过 |
| **子系统** | 🟢 **75%** | 四层结构 + 三个判断问题 |
| **碰撞** | 🟢 **70%** | 三组正交概念 + CTF 选择 |
| **资产管线** | 🟡 **45%** | 引用链实测过，异步加载确认做不到 |
| **渲染** | 🟡 **35%** | Nanite/后处理结构清楚，Lumen 零 |
| **动画** | 🟡 **30%** | 墨香侧格式 85%，引擎侧只到边界 |
| **音频** | 🟡 **25%** | 知道类，没播过声音 |
| **UI** | 🟡 **20%** | 知道三层，没做过控件 |
| **网络** | 🔴 **10%** | 知道 GameMode/GameState 复制差异 |

### 六、下一轮该学什么

**按"本项目最需要"排序：**

| 顺位 | 域 | 理由 |
| --- | --- | --- |
| 1 | **动画引擎侧** | 墨香 4,056 个动画要导入，这是唯一硬阻塞 |
| 2 | 音频 | 481 个音频已提取，迟早要播 |
| 3 | 材质图 | 观感最关键，且有 22 个现成工具 |
| 4 | UI（UMG） | 古风样式 Canvas 做不出来 |
| — | 网络 | **P0 单机不需要** |


## 18. UE5 学习第二轮：动画两侧 + 材质（2026-11-26 19:00）

### 一、本轮新增三篇

| 文档 | 大小 | 内容 |
| --- | --- | --- |
| **`UE5-ANIMATION-ENGINE.md`** | 8.4 KB | DataModel 42 读 + Controller 42 写 + **完整 C++ 写入配方** |
| **`UE5-ANIMATION-RUNTIME.md`** | 8.7 KB | 槽位机制 / 蒙太奇 / BlendSpace / Notify / 状态机 |
| **`UE5-MATERIALS.md`** | 7.4 KB | 22 个材质工具 + **地面网格感实测诊断** |

### 二、两条重要结论

**① 帧率从「阻塞」降为「调参」**

```
AnimationBlueprintLibrary.GetSequenceLength   <- Python 可用
AnimationBlueprintLibrary.GetNumFrames        <- Python 可用
所以 帧率 = GetNumFrames / GetSequenceLength
```

写入时 `Controller.SetFrameRate` 由我们决定。**所以原始帧率不影响能不能导入。**

**② 地面网格感的真正病因（实测）**

```
M_Moxiang_Ground: 3 个节点
  u_tiling = v_tiling = 96
  一张贴图覆盖 533 cm
  tile_108_road01 是 64x64 像素（已验证）
  所以 1 像素 = 8.3 cm，全图重复 9,216 次
```

**这不是参数问题，是素材分辨率问题。改平铺数治不了。**

### 三、一个诚实的发现

**引擎 `Engine/Content` 里没有自带骨骼网格（无 Mannequin / SKM_*）。**

**所以「练一次动画蓝图」做不了 —— 需要先有 SkeletalMesh，而那要等 .mod 转换。**

**动画这块：机制全懂，零实操，且被前置条件卡住。**

### 四、掌握度变化

| 域 | 上一轮 | 本轮 |
| --- | --- | --- |
| 动画（引擎侧）| 30% | **55%** |
| 动画（运行时）| — | **50%** |
| 材质 | 35% | **35%**（结构全懂，零实操）|

### 五、下一步（能真的动手的）

**材质三平面映射 —— 不需要前置条件**

```
create_material -> add_expression x15 -> get_expression_input_names
-> connect_expressions -> recompile -> 挂到地形 -> 截图对比
```

**目标：同时验证工具链可用 + 三平面有效 + 观感改善。**

## 19. 三平面材质建成 + 音频实测通过（2026-11-26 19:05）

### 一、本轮两件「真做成」的事

**① 三平面材质 M_Ground_Triplanar（24 节点）**

`
TRI: built 24 expressions
TRI: recompile ok
TRI: saved /Game/Moxiang/M_Ground_Triplanar
APPLY: replaced M_Moxiang_Ground with M_Ground_Triplanar
`

截图 Saved/tri_fixed.png：**网格消失、陡坡不拉伸、纹理细节回来了。**

**② 音频全链验证**

`
AUDIO: source M004_Attack_01.wav (55992 bytes)
LogAudioDerivedData: BINKA 压缩 29.15%（54KB → 15KB）
AUDIO: class=SoundWave duration=1.265 s
AUDIO: played at 8950, -6200, 3900
`

### 二、本轮踩的两个坑（都是「编译通过但画面不对」）

| # | 坑 | 教训 |
| --- | --- | --- |
| **71** | 三平面 UV 要**除**以米数，不是**乘**平铺次数 | 世界坐标是厘米，乘完变 21 万 → 退化成纯色 |
| **72** | 混合权重必须是**归一化比例** | 分量之和可能 >1，Lerp 钳制后混合失效 |
| **73** | play_sound_at_location 的 rotation 必需 | 反射签名没有默认值 |

### 三、掌握度更新

| 域 | 上一轮 | 本轮 |
| --- | --- | --- |
| **材质** | 35% | **65%**（做成 24 节点三平面）|
| **音频** | 25% | **40%**（实测导入+播放）|

### 四、下一步

| 顺位 | 任务 | 能现在做吗 |
| --- | --- | --- |
| 1 | SoundClass 分组 + AttenuationSettings | ✅ 能 |
| 2 | merge_actors 合并 96 个建筑 actor | ✅ 能 |
| 3 | 清理 107 个遗留资产 | ✅ 能（先查 referencers）|
| 4 | UI（UMG）框架 | ✅ 能 |
| 5 | 动画实操 | ❌ 等 .mod 蒙皮 |


## 20. UE5 第三轮：音频系统 + UI 边界 + 网络（2026-11-26 19:15）

### 一、三个新增

| 文档 | 大小 | 内容 |
| --- | --- | --- |
| **`UE5-AUDIO.md`** 扩写 | 6.2 KB | **5 个 SoundClass + 1 个衰减**（新增第九节）|
| **`UE5-UI.md`** | 5.5 KB | **实测边界**：Python 做不了 UMG 布局 |
| **`UE5-NETWORKING.md`** | 5.7 KB | 复制的三行声明 + **UE 复制 ≠ 墨香协议** |

### 二、三个「实测结论」

**① 音频系统建成**

```
sound classes: SC_Master, SC_Music, SC_SFX, SC_Voice, SC_Monster
attenuation saved: SA_Monster
磁盘确认：6 个 .uasset
```

**② UMG 的 Python 边界（决定性）**

```
WidgetTree / TextBlock / CanvasPanel 类型  -> 都暴露
WidgetBlueprint 的 widget/tree/root 属性  -> 一个都没有
WidgetBlueprintLibrary                     -> 不存在
UMGEditorSubsystem                         -> 未暴露
```

**结论：能造零件，造不出结构。UI 必须手点编辑器或写 C++。**

**③ UE 复制 ≠ 墨香服务端**

**两套完全不同的协议。即使架起墨香服务端，也不会走 UE 的复制。**
**墨香服务端的研究价值在「理解设计」，不在「和 UE 对接」。**

### 三、踩到的坑（74 条了）

| # | 坑 |
| --- | --- |
| **74** | 资产工厂类名**有的带 New 有的不带**（`SoundClassFactory` 无 New，`MaterialFactoryNew` 有）|

### 四、掌握度全表（本轮结束）

| 域 | 掌握 | 关键证据 |
| --- | --- | --- |
| 编辑器脚本 / MCP / 工具集 | **90%** | 自建工具集跑通，217 工具逐条读 |
| 核心架构 | **80%** | 继承链 + 生命周期 + 复制标志 |
| 子系统 | **75%** | 四层 + 三个判断问题 |
| 碰撞 | **70%** | 三组正交 + CTF |
| **材质** | **65%** | **做成 24 节点三平面** |
| 动画（引擎侧）| **55%** | DataModel 42+42 方法 + 写入配方 |
| **音频** | **50%** | **播过声音 + 建成 SoundClass 体系** |
| 动画（运行时）| **50%** | 槽位/蒙太奇/Notify/状态机 |
| 资产管线 | **45%** | 引用链实测 + 异步边界 |
| 渲染 | **35%** | Nanite 两套结构 + 350 后处理字段 |
| **UI** | **30%** | **实测边界（做不了）** |
| **网络** | **25%** | 三行声明 + RPC 方向 |

### 五、还没做的（诚实）

| 项 | 状态 |
| --- | --- |
| Lumen（全局光照）| 🔴 零 |
| MetaSounds | 🔴 零 |
| 动画蓝图实操 | 🔴 等 .mod 蒙皮 |
| UMG 实操 | 🔴 需人做 |
| 网络实操 | 🔴 P0 不需要 |

### 六、下一步

| 顺位 | 任务 | 能现在做吗 |
| --- | --- | --- |
| 1 | 清理 107 个遗留资产（先查 referencers）| ✅ |
| 2 | `merge_actors` 合并 96 个建筑 actor | ✅ |
| 3 | UMG 控件（需人配合）| ⚠️ 需人 |
| 4 | 动画实操 | ❌ 等 .mod |


