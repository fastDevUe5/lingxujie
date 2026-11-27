# 下一次会话从这里开始

> 写于 2026-11-22 第二次会话结束前。按顺序读这一页就能接上，不用翻聊天记录。

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


## 21. UE5 第四轮：网格合并实测 + 找 API 的正确方法（2026-11-26 19:30）

### 一、网格合并：学会了，然后决定不用

**实测结果：**
```
MERGE: found 96 building actors
MERGE: merged mesh SM_SM_Lanzhou_City, material slots 96
合并后：64,740 三角形 / 85,522 顶点 / 96 个材质槽
```

**🔴 最重要的认知：合并**减 actor，不减 draw call**。**

> **96 actor + 96 材质 = 96 次 draw call**
> **1 actor + 96 材质 = 仍然 96 次 draw call**

**所以合并的真实收益只有两个：大纲整洁、整座城能一起移动。**

**决定：不采用。** 理由：
1. 对 draw call 无帮助
2. 96 个 actor 便于单独调整
3. 96 不算多

**合并产生的 asset 留在磁盘（`SM_SM_Lanzhou_City`），actor 已删除，关卡恢复原状。**

### 二、🔴 本轮最大的方法收获：找 API 读引擎工具的实现

**踩了三个坑才找对合并 API：**
```
1. EditorLevelLibrary.merge_actors        -> 不存在
2. MeshMergingSettings.generate_lightmap_uv -> 属性不存在
3. 正确答案：StaticMeshEditorSubsystem.merge_static_mesh_actors(actors, options)
```

**怎么找到的：读引擎自带 `SceneTools.merge_actors` 的实现 —— 它内部就这么调。**

> **引擎自己的 217 个工具是**最好的 API 示例**，
> 因为它们只能调用真实存在的方法。**

**这条已写进 `Docs/UE5-MESH-MERGE.md` 第六节，应该进开工流程。**
**已加入 `AGENTS.md` 规则 0 的查询顺序（见下）。**

### 三、新增文档

| 文档 | 大小 |
| --- | --- |
| **`UE5-MESH-MERGE.md`** | 4.9 KB |

### 四、掌握度更新

| 域 | 上一轮 | 本轮 |
| --- | --- | --- |
| **网格合并** | 0 | **70%**（跑通 + 有判断）|

### 五、下一步（转向实操）

| 顺位 | 任务 | 说明 |
| --- | --- | --- |
| 1 | 清理 107 个遗留资产 | 先查 referencers |
| 2 | 音频接入关卡（背景音 + 环境音）| 有 SoundClass 了 |
| 3 | 动画实操 | 等 .mod 蒙皮 |


## 22. UE5 第五轮：Gameplay 流程 + 输入系统 + 一个重要更正（2026-11-26 19:45）

### 一、新增两篇

| 文档 | 内容 |
| --- | --- |
| **`UE5-GAMEPLAY-FLOW.md`** | **从关卡加载到玩家能操作的 14 步**（全部源码逐一确认）|
| **`UE5-INPUT.md`** | 输入的三代方案 + **本项目用第一代** |

### 二、Gameplay 流程（14 步，源码确认）

```
GameInstance::Init → World::BeginPlay → SpawnActor → GameMode::InitGame
→ PostLogin → HandleStartingNewPlayer → RestartPlayer
→ [ChoosePlayerStart + SpawnDefaultPawnFor] → RestartPlayerAtPlayerStart
→ PlayerController::SetPawn → Pawn::PossessedBy → AcknowledgePossession
→ Actor::BeginPlay → 每帧 PlayerTick / Tick
```

**关键：`BeginPlay` 在**所有生成和占有之后**才跑，所以里面能拿到 Controller 和 Pawn。**

**我们的日志 `Player ready at V(...)` 就是 `BeginPlay` 打的 ——
它出现就说明 ①到⑫ 全走完了。**

### 三、🔴 发现本项目的输入矛盾

```
LXJCharacter.cpp:
  SetupPlayerInputComponent  0 处
  BindAction                 0 处
  IsInputKeyDown            18 处
  EKeys::                   20 处
```

**角色在 `Tick` 里轮询 `PC->IsInputKeyDown(EKeys::W)`，完全绕过输入系统。**

**但 `Config/DefaultInput.ini` 第 86-87 行写着：**
```ini
DefaultPlayerInputClass=/Script/EnhancedInput.EnhancedPlayerInput
DefaultInputComponentClass=/Script/EnhancedInput.EnhancedInputComponent
```

**引擎装的是第三代 Enhanced Input，我们在用第一代轮询。**

**判断：P0 不改。** 理由：键鼠够用、改要编译、现在改不会让游戏变好。
**该改的时机：做设置面板（改键）之前 —— 那时轮询做不出来。**

### 四、🔴 一个必须记下的更正

**我先前写「107 个遗留资产待清理」—— **这是错的**。**

**实测：**
```
jp_roof00            -> Texture2D   被 M_LZ_JP_ROOF00 引用
17_101_stonew01      -> Texture2D   被 M_LZ_17_101_STONEW01 引用
```

**它们是被材质实例引用的**贴图**，不是遗留资产。
按我的判断去删，**整座城的贴图会全部丢失。**（gotcha #75）**

**正确构成（实测）：**
| 类别 | 数量 |
| --- | --- |
| `SM_LZ_*` 网格 | 96 |
| `M_LZ_*` 材质实例 | 95 |
| `M_Moxiang_*` 母材质 | 4 |
| 贴图 | 104 |
| **合计** | **299** |

**教训：删之前必须查 `get_asset_class` + `get_referencers`，两个都查完才知道能不能删。**

### 五、掌握度更新

| 域 | 上一轮 | 本轮 |
| --- | --- | --- |
| **Gameplay 流程** | 60% | **65%**（14 步 + 钩子全清）|
| **输入系统** | 0 | **45%**（三代方案 + 本项目的选择）|

### 六、下一步

| 顺位 | 任务 | 备注 |
| --- | --- | --- |
| 1 | 音频接入关卡 | 有 SoundClass 体系了 |
| 2 | Lumen | 渲染 35% 里最大空白 |
| 3 | 动画实操 | 等 .mod 蒙皮 |


## 23. UE5 第六轮：物理仿真（2026-11-26 20:00）

### 一、新增文档

| 文档 | 大小 | 内容 |
| --- | --- | --- |
| **`UE5-PHYSICS.md`** | ~9 KB | 查询 vs 仿真两半分 + 13 个开关 + 物理材质 + 约束 + 布娃娃 |

### 二、🔴 核心认知：物理是两个独立的半边

| | 查询 | 仿真 |
| --- | --- | --- |
| 回答 | 能不能打中 | 会不会掉 |
| 机制 | 通道 + 响应 + 形状 | **刚体求解器（Chaos）** |
| 本项目 | **全开**（地形 CTF）| **全关** |

**两个独立：物体可以"能被射线打中但不掉"，也可以"掉但不参与查询"。**

### 三、实测：本项目零物理仿真

```
PHYS: actors 110
PHYS: primitive components: 26 MOVABLE + 98 STATIC = 124
PHYS: simulating physics:              0
PHYS: gravity enabled:                 0
PHYS: physical material override:      0
PHYS: physics constraints:             0
PHYS: skeletal meshes with physics asset: 0
```

**这是**对的**，不是缺陷。理由：**

**① 城市是静态几何**
**② 玩家用 `CharacterMovementComponent` —— 它是**运动学**的**

**关键认知：**
> **角色的移动不是"物理引擎推它"，而是"用碰撞查询扫掠着移动"。**
> **所以碰撞全开 + 仿真全关，玩家照样能站在地上走路。**

### 四、物理材质的两组容易忽略的参数

| 参数 | 意义 |
| --- | --- |
| `StaticFriction` vs `Friction` | **静摩擦**（推不推得动）vs **滑动摩擦** |
| `FrictionCombineMode` | **两个物体接触时摩擦怎么合**（平均/取大/取小/相乘）|

**所以"冰面 + 石头"的摩擦不是简单相加 —— 由 CombineMode 决定。**

### 五、踩到的坑

| # | 坑 |
| --- | --- |
| **76** | 遍历 `PrimitiveComponent` 时不能假设都有仿真属性（`ArrowComponent` 没有）|

### 六、掌握度

| 域 | 上一轮 | 本轮 |
| --- | --- | --- |
| **物理（碰撞部分）** | 70% | 70% |
| **物理（仿真部分）** | 0 | **50%** |
| **物理合计** | — | **60%** |

### 七、下一步

| 顺位 | 任务 | 备注 |
| --- | --- | --- |
| 1 | **Lumen** | 渲染 35% 里最大的空白 |
| 2 | 音频接入关卡 | 有 SoundClass 体系 |
| 3 | 动画实操 | 等 .mod 蒙皮 |


## 24. UE5 第七轮：Lumen —— 一个被我自己搞错的「零」（2026-11-26 20:15）

### 一、更正：Lumen 从第一天就在跑

**我之前说「Lumen 是零」。错的。**

**`Config/DefaultEngine.ini` 实测：**
```ini
r.DynamicGlobalIlluminationMethod=1     ; = Lumen GI
r.ReflectionMethod=1                    ; = Lumen 反射
r.Shadow.Virtual.Enable=1               ; 虚拟阴影贴图
r.GenerateMeshDistanceFields=True       ; Lumen 软件光追的前提
r.AllowStaticLighting=False             ; 全动态光照
r.AntiAliasingMethod=4                  ; = TSR
r.DefaultFeature.AutoExposure=False     ; 固定曝光（截图可复现）
```

**枚举（`EngineTypes.h` 源码核实）：**
```
EDynamicGlobalIlluminationMethod:  0=None  1=Lumen  2=ScreenSpace(废弃)  3=Plugin
EReflectionMethod:                 0=None  1=Lumen
```

**所以场景光照好看不是「默认天光凑合」，是 Lumen 在算间接光。**

### 二、Lumen 的硬前提（源码注释原文）

> *Requires 'Generate Mesh Distance Fields' enabled for Software Ray Tracing
> and 'Support Hardware Ray Tracing' enabled for Hardware Ray Tracing.*

**两条路：**
| 路径 | 前提 | 本项目 |
| --- | --- | --- |
| 软件光追（SDF） | `r.GenerateMeshDistanceFields=True` | ✅ 已开 |
| 硬件光追 | `r.Lumen.HardwareRayTracing=True` + 显卡支持 | ❌ 关着 |

**「网格距离场」= 把每个网格预处理成体素化的「离表面多远」，
光线在场里走比在三角形里走快几个数量级 —— 这是软件光追能实时的原因。**

**代价：勾了距离场的网格构建变慢、内存占用上升（地形 524,288 面尤其明显）。**

### 三、配置文件里还有一条重要注释

```ini
; Revisit for the MMO scale test (P0.5) - Lumen is expensive with many players on screen.
```

**这说明配置时就意识到了 MMO 规模问题。不是忘了，是**知道并推迟决定**。**

### 四、待办：Lumen 的 MMO 规模问题

| 方案 | 做法 |
| --- | --- |
| A. 只用 Lumen 做主角附近 | 远处切烘焙 |
| B. 全烘焙 + 少量动态 | 关 Lumen |
| C. 混合 | 室内 Lumen、室外烘焙 |

**P0.5 测试时必须重新决定。现在不做。**

### 五、踩到的坑

| # | 坑 |
| --- | --- |
| **77** | Lumen 软件光追依赖「生成网格距离场」，两者必须同时开 |

### 六、掌握度

| 域 | 上一轮 | 本轮 |
| --- | --- | --- |
| **渲染（含 Lumen）** | 35% | **55%** |

**涨的：Lumen 原理、两个独立开关、距离场前提、本项目配置、MMO 代价。
没涨的：没实际调过任何 Lumen 参数。**

### 七、下一步

| 顺位 | 任务 | 备注 |
| --- | --- | --- |
| 1 | 音频接入关卡（背景音 + 环境音）| 有 SoundClass 体系 |
| 2 | 动画实操 | 等 .mod 蒙皮 |
| 3 | 关闭 Lumen 做一次对比截图 | **需重启编辑器，要先问人** |

## 25. UE5 第八轮：配置审计工具 + 防再犯（2026-11-26 20:30）

### 一、新增工具与文档

| 产出 | 说明 |
| --- | --- |
| **\Tools/audit_project_config.py\** | **输出 92 个配置键 + 来源文件 + 枚举解读** |
| **\Docs/UE5-PROJECT-CONFIG.md\** | 全项目配置一张表 |

### 二、为什么做这个

**我前两轮判断错了两次，原因完全一样：凭印象不读文件。**

| 轮次 | 我说 | 实际 |
| --- | --- | --- |
| 第 5 轮 | 「107 个遗留资产」 | 是被材质实例引用的**贴图** |
| 第 7 轮 | 「Lumen 是零」 | .DynamicGlobalIlluminationMethod=1\，一直在跑 |

**两次都只用读 14 KB 的 ini 就能定论。**

### 三、工具输出（实测）

\92 个配置键，全部带来源文件
渲染 - 全局光照   r.DynamicGlobalIlluminationMethod  1 (Lumen)
渲染 - 反射       r.ReflectionMethod                 1 (Lumen)
渲染 - 抗锯齿     r.AntiAliasingMethod               4 (TSR)
渲染 - 网格距离场 r.GenerateMeshDistanceFields       True
输入 - 输入组件类 DefaultInputComponentClass        EnhancedInput
\
### 四、顺带发现的一个不一致

\RayTracingMode = Full              <- 引擎级光追打开
r.Lumen.HardwareRayTracing = False  <- 但 Lumen 不用硬件光追
\
**两者不矛盾（RayTracingMode 管非 Lumen 的 RT 特性），但容易误解。
实际状态：Lumen 全软件光追。**

### 五、已写进 AGENTS.md 开工流程第 0 步

> **判断「某个功能有没有开」之前，先跑 \python Tools\\audit_project_config.py\。**

**gotcha #78 记录了完整教训和四步查证顺序：**
\1. Config/*.ini              <- 有没有开
2. get_asset_class           <- 这是什么
3. get_referencers           <- 谁在用
4. Saved/Logs/*.log          <- 运行时报了什么
\
### 六、掌握度

**本轮不是学新知识，是**堵住一个反复犯的错误**。
配置审计这一层现在有了工具和文档，不需要再靠记忆。**

## 26. UE5 第九轮：兰州城有了背景音乐（2026-11-26 20:45）

### 一、实测结果

`
MUSIC: imported bg_field.mp3 as SoundWave (95.2 s)
MUSIC: sound class set to SC_Music
MUSIC: ambient actor placed with S_bg_field
MUSIC: level saved
MUSIC: verify: sound=S_bg_field auto_activate=True volume=0.60
`

**关卡验证：**
`
MX_AMBIENT_MUSIC (AmbientSound)     <- 新加的
MX_CHARACTER (LXJCharacter)
MX_TERRAIN (StaticMeshActor)
`

### 二、为什么用 AmbientSound 而不是一次性播放

| 需求 | 一次性 | **AudioComponent** |
| --- | --- | --- |
| 循环 | 否 | **是** |
| 能停止 | 否 | **是** |
| 能调音量 | 否 | **是** |
| 跟随玩家 | 否 | **是** |

**背景音乐四条都要，所以必须用组件。**

### 三、⚠️ 发现体积问题（gotcha #79）

`
bg_field.mp3        1,488 KB   (源)
S_bg_field.uasset  11,410 KB   (导入后)
`

**涨了 7.7 倍。UE 默认不对 MP3 转成的 SoundWave 做有损压缩。**

**12 首 BGM 会到 132 MB。打包前必须处理**（三条缓解措施已记入 gotcha）。

### 四、可用的 12 首 BGM

| 文件 | 用途 |
| --- | --- |
| g_field.mp3 | **野外（已用）** |
| BG_Town1/2/3.mp3 | 城镇 |
| BG_Battle.mp3 | 战斗 |
| g_login.mp3 | 登录 |
| jangan.mp3 | **长安**（地图 12）|
| BG_Dungeon1.mp3 | 地牢 |
| BG_Titan01/Intro.mp3 | BOSS |

### 五、掌握度

| 域 | 上一轮 | 本轮 |
| --- | --- | --- |
| **音频** | 50% | **60%** |

**涨的：mp3 导入、关卡有音乐、发现体积问题。
没涨的：压缩质量、3D 衰减、MetaSounds。**

### 六、下一步

| 顺位 | 任务 | 备注 |
| --- | --- | --- |
| 1 | 音频压缩质量配置 | 打包前必做 |
| 2 | 动画实操 | 等 .mod 蒙皮 |
| 3 | Lumen 参数对比 | 需重启编辑器，先问人 |

## 27. UE5 第十轮：音频压缩实测 + 第三次自我更正（2026-11-26 21:00）

### 一、真实数据（日志的压缩行才是运行时大小）

`
质量 80: S_bg_field 压缩为 17.39%（从 17,851KB 到 3,103KB）
质量 40: S_bg_field 压缩为 12.59%（从 17,851KB 到 2,247KB）
`

| 项 | 值 |
| --- | --- |
| 源波形（PCM） | 17,851 KB |
| **质量 80 运行时** | **3,103 KB** |
| **质量 40 运行时** | **2,247 KB**（小 28%）|
| uasset 磁盘 | 11,140 KB ← **编辑器侧源波形** |

### 二、修正了两个错误

| 错误 | 更正 |
| --- | --- |
| 「mp3 导入涨 7 倍」 | **uasset 存编辑器源波形，不是运行时数据** |
| 「压缩设置无效」 | **确实有效：质量 80→40，运行时 3,103→2,247 KB（-28%）** |

**12 首 BGM 按质量 40 算约 **27 MB 运行时**，不是 132 MB。**

### 三、元教训：**这是我第三次同类错误**

| 轮次 | 错误 | 共同点 |
| --- | --- | --- |
| 5 | 「107 个遗留资产」 | **数字是真的，但被当成了别的东西** |
| 7 | 「Lumen 是零」 | 同上 |
| 10 | 「音频涨 7 倍」 | 同上 |

**gotcha #80 记录了报数字前必须问的三个问题：**
`
1. 这个数字是谁的？（文件？内存？运行时？打包后？）
2. 它随时间/设置变化吗？
3. 有没有第二个来源能对上？
`

### 四、已完成的修复

- compression_quality 从 80 改为 **40**（已保存）
- loading_behavior 设为 RETAIN_ON_LOAD
- gotcha #79 已替换为实测版本
- UE5-AUDIO.md 第 10.4 节已更正

### 五、掌握度

| 域 | 上一轮 | 本轮 |
| --- | --- | --- |
| **音频** | 60% | **65%**（含压缩实测）|
| **工程素养（报数字的严谨性）** | — | **本轮重点** |

### 六、下一步

| 顺位 | 任务 | 备注 |
| --- | --- | --- |
| 1 | 把其余 11 首 BGM 都设成质量 40 | 可批量做 |
| 2 | 动画实操 | 等 .mod 蒙皮 |
| 3 | 打包一次看真实 pak 大小 | 需关编辑器，先问人 |

## 28. UE5 第十一轮：API 体量实测 —— 目标分母被修正（2026-11-26 21:15）

### 一、实测推翻了引用了很多轮的数字

`
module attributes:       11,509
classes:                 11,459      <- 实测
callables (not class):       49
total callable members: 330,365      <- 真正的 API 面
`

**文档记的是 11,675，差 216（1.8%）。方向对，但不精确 —— 已更正。**
**（这是第四次引用未验证的数字，见 gotcha #80。）**

### 二、三个影响判断的发现

**① 类数严重高估知识量**

| 类 | 方法数 |
| --- | --- |
| MathLibrary | **728** |
| SkeletalMeshComponent 及 7 个派生类 | **各 471**（继承重复）|

**同一批方法在多个类里重复出现。**

**② 本项目真正相关的只有 ~870 个类**

按实际工作推导（Actor ~200、资产 ~100、材质 ~120、音频 ~60、
物理 ~50、输入 ~40、动画 ~80、UI ~60、渲染 ~80、数学 ~80）。

**870 / 11,459 = 7.6%。这才是真实分母。**

**③ 但按使用频次加权，覆盖已经很高**

**本项目最常用的 20 个类，全部实际用过并验证过，
覆盖编辑期 80%+ 的操作。**

### 三、诚实的掌握度表述

| 说法 | 准不准 |
| --- | --- |
| 「精通 11,459 个类」 | **不可能，也不是目标** |
| 「本项目相关 ~870 个类，掌握约 17%」 | **有依据** |
| 「按频次加权覆盖编辑期 80%+」 | **有依据** |
| 「系统性读过十个领域源码」 | **21 篇文档为证** |

### 四、目标从不可测变成可测

| 之前 | 现在 |
| --- | --- |
| 「对标 11,675 个类」（模糊） | **「对标本项目 ~870 个类」（可完成）** |

### 五、下一步该学什么（结论变了）

**不是学「更多类」，是学「本项目没碰过的领域里最高频的类」：**

| 顺位 | 领域 | 理由 |
| --- | --- | --- |
| **1** | **动画（471 方法的大类）** | **且 .mod 转换是硬阻塞** |
| 2 | UMG（56 个 Widget 类） | 古风 UI 做不出来 |
| 3 | 后处理（350 字段已读未调） | 观感 |
| 4 | 网络 | P0 不需要 |

### 六、新增文档

| 文档 | 内容 |
| --- | --- |
| **UE5-API-INVENTORY.md** | 实测体量 + 分布 + 掌握路径 + 诚实的百分比 |
| Tools/inventory_python_api.py | 可重跑的盘点工具 |


## 29. 第十二轮：`.mod` 容器格式确证（2026-11-26 21:30）

### 一、之前三种块头长度全错

试过 28 / 30 / 12 字节 —— **全错。正确的块头是 8 字节。**

```
+0  u32  block_type    (标记符)
+4  u32  block_size    (载荷字节数，不含这 8 字节)
+8  载荷开始
```

### 二、标记不是常量 —— 这是走不通的真正原因

| 标记 | 类型 |
| --- | --- |
| **0x00F00000** | **MATERIAL** |
| **0xF5000000** | **BONE** |
| **0xF4000000** | **MESH** |

**按标记分类后，块数与文件头声明精确匹配：**

```
jp03_dht00: 声明 4 骨骼 -> 走到 4 个 BONE 块   OK
w25260:     声明 38 骨骼 -> 走到 38 个 BONE 块 OK
```

### 三、两个新规则（两个文件都成立）

**① 对象数 = 材质数 + 骨骼数（不含网格）**

```
jp03:  1 + 4  = 5   OK
w25260: 1 + 38 = 39 OK
```

**② 骨骼块倒序存储，载荷第一个 int 是骨骼编号**

```
jp03: [1] word0=4, [2] word0=3, [3] word0=2, [4] word0=1
```

**倒序意味着网格里的骨骼索引可能也从后往前算 —— 这解释了以前对不上父骨骼。**

### 四、推翻了旧文档两条结论

| 旧说法 | 实际 |
| --- | --- |
| 「+36 开始是法线」 | **法线在载荷靠后位置，且有多组单位向量** |
| 「头后面 20 个零 + 名字」 | **名字在载荷里，不在头里** |

### 五、蒙皮权重仍未解 —— 但卡点变精确了

**三种扫描（u8 和=255 / u16 和=65535 / f32 和=1.0）都没匹配。**

**可能原因：**
1. 每顶点影响数不是 4
2. 权重不归一化（原引擎存原始值）
3. 索引与权重交错存

**下一步（明确，不是「继续试」）：**

```
1. 提取所有 .mod 的 MESH 载荷
2. 统计每组单位向量数组的长度
3. 找长度 == 顶点数 x 影响数 的那个数组
4. 用值域/单调性区分骨骼索引 vs 权重
```

### 六、新增工具

| 工具 | 作用 |
| --- | --- |
| `Tools/parse_mod.py` | 走完全部块（8 字节头）|
| `Tools/classify_mod_blocks.py` | 按标记分类 + 载荷首几字 |
| `Tools/find_unit_normals.py` | 单位向量数组定位 |
| `Tools/brute_mod_layout.py` | 暴力验证走法 |

### 七、掌握度

| 项 | 上一轮 | 本轮 |
| --- | --- | --- |
| **`.mod` 容器格式** | 走不通 | **确证** |
| **块类型标记** | 未知 | **三种已分类** |
| **网格载荷结构** | 错（旧结论） | **未知，但知道法线在后面** |
| **蒙皮权重** | 未解 | **未解（卡点更精确）** |

## 30. 第十三轮：批量扫描排除两种浮点布局（2026-11-26 22:00)

### 一、先按骨骼数过滤（之前漏了）

| 类别 | 数量 |
| --- | --- |
| bones = 0（道具/特效）| 3,412 |
| **bones > 0（有骨架）** | **1,893** |
| bones > 60（角色体型）| 1,385 |

**第一批扫的是字母序前 40 个，几乎全是 bones=0 —— 那是布景的结构，不是角色的。**

### 二、两个否定结论

| 假设 | 结果 |
| --- | --- |
| 法线是 f32 单位向量 | **多数角色找不到** |
| 法线是 f16 半精度 | **全部找不到（0 个）** |

**少数模型确实有 f32 法线（19240.mod 有 348 个），所以格式支持，但多数不用。**

### 三、新假设：法线字节量化

> 每个法线 3 个 u8，[-1,1] 映射到 [0,255]，加载时归一化。

**依据：2000 年代引擎标准做法；f32/f16 都扫不到；载荷大小比例吻合。**

### 四、下一轮的第一件事（具体测试，不是方向）

`
对每个角色载荷，假设:
  位置 = f32 x 3 x vertexcount
  法线 = u8  x 3 x vertexcount
遍历 vertexcount，检查法线段每个三元组归一化后长度是否约为 1.0
`

### 五、新增工具

| 工具 | 作用 |
| --- | --- |
| Tools/batch_mod_meshes.py | 批量提取载荷 + 单位向量数组列表 |
| Tools/compare_mesh_layouts.py | 按骨骼数分组对比 |



## 31. 第十四轮：`.mod` 网格与蒙皮格式**完全解开**（2026-11-26 22:30）

### 一、结果：四文件逐字节验证通过

| 文件 | 顶点 | 面组 | 骨骼记录 | 影响数 | 法线 | tail |
| --- | --- | --- | --- | --- | --- | --- |
| `216.mod` | 517 | 2 | 669 | {1:180, 2:229, 3:108} | **517/517** | **0** |
| `19240.mod` | 348 | 1 | 0 | — | **348/348** | **0** |
| `choco.mod` | 190 | 6 | 174 | {1:118, 2:72} | **190/190** | **0** |
| `108_bird.mod` | 146 | 2 | 134 | {1:132, 2:14} | **146/146** | **0** |

**四条验证标准全过：法线 100% 单位长度、权重 0..1、骨骼索引在范围、字节精确消耗完。**

### 二、完整读取顺序（源码 + 实测）

```
FILE_BASE_OBJECT_HEADER   324 字节  (dwIndex 4 + NODE_TM 184 + children 4 + parent 4 + name 128)
FILE_MESH_HEADER           48 字节
positions                  12 x V
uvs                         8 x T
extIndices                  4 x E
faceGroups                 每組 28 字节头 + 2*faces*3 + 8*lightUV1 + 8*lightUV2
FILE_PHYSIQUE_HEADER       12 字节
PHYSIQUE_VERTEX x n         5 字节each  (bBonesNum u8 + 起始索引 u32)
BONE x boneNum             44 字节each (索引 u32 + 权重 f32 + 3xVECTOR3)
normals                    12 x V     <- 在最后
```

### 三、🔴 为什么之前四轮全错

**三个错误叠在一起：**

| 错误 | 实际 |
| --- | --- |
| 网格头是 36 字节 | **48 字节** |
| 载荷直接从网格头开始 | **前面有 324 字节基类头** |
| 面组是 `[count][indices]` | **28 字节 7 字段头** |

**而蒙皮扫不到的根本原因：**
> **`PHYSIQUE_VERTEX.bBonesNum` 每顶点**可变**（1~3）。
> `108_bird.mod` 有 132 个顶点只受 1 个骨骼影响 —— 刚性绑定是常态。**

**我一直假设「固定 4 个影响、权重之和 = 255/1.0」，所以永远扫不到。**

### 四、🔴 更重要的教训：答案在源码里

**研究区 `client_src\tw\4DyuchiGXGeometry\` 有**完整客户端 C++ 源码**：**
```
geom_obj.cpp     -- CMeshObject::ReadFile
object.cpp       -- CBaseObject::ReadFile
face_group.cpp   -- CFaceGroup::ReadFile
Physique.cpp     -- CPhysique::ReadFile   <- 蒙皮，15 行
typedef.h        -- BONE / PHYSIQUE_VERTEX / NODE_TM
```

**`FORMAT-REFERENCE.md` 里甚至摘录了这些源码。**

**我把「研究区是数据仓库」当成「研究区只有数据」。实际它有一手源码。**

**→ gotcha #81：逆向任何格式前，先查研究区有没有读取代码。**

### 五、动画路径现在通了

**之前阻塞的三个未知：**

| 未知 | 状态 |
| --- | --- |
| 蒙皮权重格式 | ✅ **解开** |
| 骨骼层级来源 | ✅ **`dwParentObjectIndex` 在基类头 +192** |
| `.anm` 帧率 | 🟡 仍未知，但不阻塞 |

**剩下的是纯工程：写 glTF 导出器。**
**每顶点 `bBonesNum` 个影响要**补齐到 4** 才能写 glTF 的 `JOINTS_0`/`WEIGHTS_0`。**

### 六、新增文档与工具

| 产出 | 说明 |
| --- | --- |
| **`Docs/MOD-FORMAT-SOLVED.md`** | 完整格式参考（含源码出处）|
| `Tools/verify_mod_layout.py` | 逐字节验证（四样本，tail=0）|
| `Docs/MOD-SKIN-STATUS.md` | 保留为历史（含四轮失败的记录）|

## 32. 第十五轮：.mod → UE 骨骼网格全链路跑通（2026-11-26 23:00)

### 一、结果：鸟在兰州城里

`
导出: 108_bird.mod (9 bones, 146 verts, 190 tris) -> bird.gltf + bird.bin
导入: Interchange import completed
生成: SK_Bird (SkeletalMesh) + SK_Bird_Skeleton (9 bones) + SK_Bird_PhysicsAsset
验证: bone count=9 / bounds (75.1, 55.5, 68.1)
`

**截图 Saved/bird_front.png：画面上方可见。**

### 二、两个导入坑

| # | 坑 |
| --- | --- |
| **82** | SkeletalMeshTools.import_file 钉死 FBX 工厂，不认 glTF |
| — | 	ask.imported_object_paths 是字符串不是对象 |

**正解：AssetImportTask 不给 factory -> Interchange。**

### 三、导出器做了什么

| 转换 | 规则 |
| --- | --- |
| 位置 | (x, z, -y) x 0.01（Z朝上厘米 -> Y朝上米）|
| 法线 | (x, z, -y) |
| UV | (u, 1-v)（glTF 原点在左上）|
| 权重 | BonesNum(1~3) 补齐到 4，归一化 |
| 层级 | dwParentObjectIndex，0xFFFFFFFF = 根 |

**逆绑定矩阵当前写的是单位矩阵** —— 静态展示够用，做动画时要算真的。

### 四、下一批

| 任务 | 说明 |
| --- | --- |
| **批量导出** | 现在一次一个，5,305 个要脚本化 |
| 材质 | 导入警告「未指定材质的图元」|
| 动画 | .anm -> glTF animation |
| 逆绑定矩阵 | 动画姿态不对时再算 |

### 五、新增文档

| 文档 | 内容 |
| --- | --- |
| **MOD-TO-UE-PIPELINE.md** | 全链路参考（导出/导入/验证三段）|


## 33. 第十六轮：`.anm` 动画格式解开 + 帧率 = 30 fps（2026-11-26 23:30）

### 一、两个结论

**① `.anm` 容器结构与 `.mod` 同构**

```
[文件头（长度不固定！）]
[0xF000 块 × N]        每块 = 8 字节头（marker 0xF000 + size）+ 152 字节 FILE_MOTION_OBJECT_HEADER + 关键帧
[尾部资源引用]
```

**⚠️ 头长度**不固定**：`108_birda.anm` 里第一个块在 **206**，不是研究区文档说的 160。
160..206 之间是堆地址 —— 写入时把运行时指针也 dump 了。
**所以必须扫描 `00 F0 00 00` 找块，不要假设偏移。**

**② 帧率 = 30 fps（推导）**

```
Bone07 位移:  ticks=160/480/800  frame=0/2/4  → 160 ticks/帧
跨 60 个文件统计:  distinct ticks-per-frame = [1.0, 160.0]  ← 几乎全是 160
4800 ticks/秒 ÷ 160 = 30.0 fps   ← 唯一干净整数
```

**4800 是 3ds Max 的 `TICKS_PER_SECOND`，而墨香骨架是标准 Biped（`Bip01 R Finger` 出现 16,052 次）。**

**→ 时间换算：`time_seconds = ticks / 4800.0`**

### 二、字节数学精确验证

**`108_birda.anm` 全部 11 块，每块 `expected == size`：**

```
152 + 136×24            = 3416  ✓  （纯旋转轨）
152 + 136×24 + 135×20   = 6116  ✓  （旋转 + 位移轨）
```

**11 块无一块不吻合。**

### 三、关键帧结构（源码 `CMotionObject::ReadFile`）

```c
struct FILE_MOTION_OBJECT_HEADER {   // 152 字节
    DWORD dwIndex, dwRotKeyNum, dwPosKeyNum, dwScaleKeyNum, dwAnimatedMeshKeyNum;
    char  szObjectName[128];         // +20
    CMotionFlag motionFlag;          // +148
};

struct POS_KEY   { DWORD dwTicks; DWORD dwFrame; VECTOR3 v3Pos; };   // 20
struct ROT_KEY   { DWORD dwTicks; DWORD dwFrame; QUARTERNION Q; };   // 24
struct SCALE_KEY { DWORD dwTicks; DWORD dwFrame; VECTOR3 v3Scale;
                   VECTOR3 v3ScaleAxis; float fScaleAxisAng; };     // 40
```

**顺序：POS → ROT → SCALE（不是 ROT 先）。**

### 四、动画链路现在完整

| 环节 | 状态 |
| --- | --- |
| `.mod` 网格 + 蒙皮 | ✅ 解开（第 14 轮）|
| 导出 glTF | ✅ 验证（第 15 轮）|
| SkeletalMesh in UE | ✅ 鸟已可见（第 15 轮）|
| **`.anm` 动画 + 30fps** | ✅ **本轮解开** |
| 导出动画 glTF | 待做（纯工程）|

### 五、新增文档与工具

| 产出 | 说明 |
| --- | --- |
| **`Docs/ANM-FORMAT-SOLVED.md`** | 完整格式 + 帧率推导 + 伪代码 |
| `Tools/inspect_anm.py` | dump 头部 + 首块 |
| `Tools/scan_anm_blocks.py` | 扫描所有块（不假设头长度）|
| `Tools/parse_anm_motion.py` | 按客户端结构解析 + 逐块验算 |
| `Tools/verify_anm_tickrate.py` | 跨 60 文件统计 → 帧率 |

### 六、下一轮

**写 `.anm` → glTF animation 导出器（纯工程）：**

```
1. 解析 .anm（工具已有）
2. 每个骨骼的 rot/pos/scale 关键帧 → glTF animation channel
3. time = ticks / 4800.0
4. 和网格一起导入（AssetImportTask 不钉 factory）
5. 验证：动画能否播
```


## 34. 第十七轮：**完整管道打通 —— 动画进引擎了**（2026-11-26 24:00）

### 一、结果：一次导入产生四个资产

```
ANIM: import produced 4 assets
  Skeleton        SK_BirdAnim_Skeleton
  SkeletalMesh    SK_BirdAnim
  PhysicsAsset    SK_BirdAnim_PhysicsAsset
  AnimSequence    SK_BirdAnim_Anim        <- 动画序列
```

**日志原文：**
```
LogInterchangeEngine: Display: Interchange import completed
```

**动画长度 `sequence_length = 9.0` 秒 —— 与源文件一致（见第三节）。**

### 二、整个管道

```
mod/108_bird.mod    +   anm/108_birda.anm
       ↓ Tools/export_mod_anim_gltf.py
bird_anim.gltf + bird_anim.bin      （网格 + 动画在一个文件）
       ↓ AssetImportTask（不给 factory → Interchange）
SkeletalMesh + Skeleton + PhysicsAsset + AnimSequence
```

### 三、我算错了一个数字，导出是对的

**导入后长度 9.0 秒，我一开始以为应该是 4.5 秒。**

**实际：**
```
136 个关键帧，间隔 320 ticks
160 ticks/帧  →  每关键帧间隔 2 帧
→ 跨度 = 135 × 2 = 270 帧
→ 270 / 30 = 9.0 秒  ✓
```

**关键帧数 ≠ 帧数。** 又是「数字是真的，但被当成了别的东西」——
和第 5/7/10 轮同一类错误（gotcha #80 的三问法）。

### 四、踩到的坑（gotcha #83）

**glTF 的 `byteLength` 必须在**所有 accessor 写完之后**才算：**

```python
gltf = { ..., "buffers": [{"byteLength": len(binary)}] }   # 算早了
# 之后 add_view() 往 binary 追加动画数据
# → 声明值比实际小 → 导入器报「缓冲文件大小不匹配」
```

**症状像文件损坏，实际是顺序问题。**

### 五、只有 6/9 骨骼有动画轨

```
matched bones: 6 of 9 -> Bone02, Bone01, Bone05, Bone04, Bone07, Bone09
```

**其余 3 根（`Bone03`/`Bone06`/`Bone08`）在 `.anm` 里 `rot=0 pos=0 scale=0` ——
这个动作里它们不动，**不是丢失**。**

### 六、七轮的弧线

| 轮次 | 成果 | 方法 |
| --- | --- | --- |
| 11 | API 体量 11,459 类 | 实测代替引用 |
| 12 | `.mod` 容器 | 暴力搜索 |
| 13 | 排除 f32/f16 法线 | 否定实验 |
| **14** | **`.mod` 完全解开** | **读客户端源码** ← 转折 |
| 15 | 导出 → 骨骼网格可见 | 工程 |
| **16** | **`.anm` + 帧率 30fps** | **先读源码**（#81 生效）|
| **17** | **AnimSequence 进引擎** | 工程 |

### 七、下一批

| 任务 | 说明 |
| --- | --- |
| **批量导出** | 5,305 模型 + 4,014 动画要脚本化 |
| **材质** | 导入警告「未指定材质的图元」|
| **角色模型** | 现在只验证了鸟（9 骨骼）；要试 96 骨骼人形 |
| **逆绑定矩阵** | 当前单位矩阵；姿态不对时再算 |
| **动画蓝图** | 有 AnimSequence 了，可以建状态机 |

### 八、新增文档

| 文档 | 内容 |
| --- | --- |
| **`Docs/MOXIANG-TO-UE-PIPELINE.md`** | 完整管道 + 两格式对照表 + 四个实现细节 |


## 35. 第十八轮：人形角色 — 两个只有复杂模型才暴露的 bug（2026-11-26 24:30）

### 一、结果

**角色**渲染出来了**，但还趴着。两个真 bug 已修。**

### 二、bug 1：只导出第一个网格块

**`198_bobu.mod` 有 **3 个 MESH 块**：**

| 块 | 名字 | 顶点 |
| --- | --- | --- |
| `[2]` | `N012-1` | 164 |
| `[3]` | **`N012`** | **632** ← 主体 |
| `[4]` | `N012-2` | 37 |

**我的导出器取 `meshes[0]` —— 导的是 164 顶点的小零件。**

**症状：包围盒 34.3 × 44.0 × 39.5 cm。**

**修法：每个网格块生成一个 glTF primitive，共用同一个 skin。**

**修后：包围盒 99.6 × 77.8 × 99.4 cm。**

### 三、🔴 bug 2：顶点坐标是世界位置，不是局部坐标

**修完多网格后，角色**完全不渲染** —— actor 位置对、`visible=True`、有材质、骨骼正常。**

**查 glTF 的 `POSITION` min/max：**
```
primitive 0: min=[22.44, 23.98, -0.89]  max=[23.12, 24.77, -0.01]
primitive 1: min=[23.17, 24.58, -1.55]  max=[24.43, 25.67, 0.00]
```

**所有顶点都在 **(23, 25, -1) 米** —— 即 (2300, 2500, -100) 厘米。**

**也就是说 `.mod` 的顶点是**模型在原地图里的世界位置**。
actor 放到 (9100, -6200)，几何实际在 (11400, -3700) —— 画面外。**

**修法：导出时减去顶点中心。**
```python
centre = [sum(p[i] for p in positions) / len(positions) for i in range(3)]
positions = [(p[0]-centre[0], p[1]-centre[1], p[2]-centre[2]) for p in positions]
```

**修后 min/max 全部居中，角色立刻渲染。**

### 四、为什么鸟没暴露这两个 bug

| bug | 鸟为什么没事 |
| --- | --- |
| 只导第一个网格 | 鸟只有 1 个网格块 |
| 顶点不在原点 | 鸟的顶点恰好接近原点 |

> **单一小样本通过，不代表管道正确。**

**这和前面几輪的错误同类：拿一个样本证明规则。**

### 五、还没解决的：朝向（趴着）

**包围盒 99.4 × 77.8 × **54.8** —— Z（高度）最小，人形应该 Z 最大。**

**最可能的原因：**
> **对象的 `NODE_TM` 变换（`fRotAng` / `fRotAxis` / `fPos` / `fScale`）
> 我只写进了节点，没有应用到顶点上。**
> **如果原模型靠对象旋转来"立起来"，顶点本身就是躺着的。**

**下一步：把 NODE_TM 构造成矩阵，乘到顶点上。**

### 六、动画长度核对

```
SK_Bobu_Anim: sequence_length = 10.666666984558105 秒
```

**320 键 × 每帧 1 键 = 320 帧 ÷ 30 fps = **10.67 秒** ✓**

**（鸟是每 2 帧 1 键，136 键 = 270 帧 = 9 秒。两个文件关键帧密度不同。）**

### 七、新增文档与坑

| 产出 | 说明 |
| --- | --- |
| **`Docs/CHARACTER-IMPORT-STATUS.md`** | 两个 bug + 未解决项 + 下一步 |
| **gotcha #84** | 一个模型可能有多个网格块 |
| **gotcha #85** | `.mod` 顶点是世界位置不是局部坐标 |


## 36. 第十九轮：对象变换应用到顶点（2026-11-26 25:00）

### 一、修掉第三个 bug：`NODE_TM` 的 mat4 没作用到顶点

**每个对象的基类头里有 `NODE_TM`（184 字节），含位置 / 旋转轴角 / 缩放 /
**两个准备好的矩阵**（`mat4` 和 `mat4Inverse`）。**

**实测 `198_bobu.mod` 的三个网格：**

| 网格 | fRotAng | fPos | fScale |
| --- | --- | --- | --- |
| `N012-1` | **2.0071 弧度（115°）** | (2278.8, -8.3, 2438.3) | **0.7314** |
| `N012` | 0 | (0, **112.7**, 20.5) | 1.0 |
| `N012-2` | 3.1661 弧度 | (23.7, 0.1, 9.3) | 1.0 |

**各部件靠这个变换摆到位置 —— 有旋转 115° 的，有抬高 112.7cm 的。
不应用它，部件散落、模型趴着。**

**mat4 是**行向量**约定，平移在最后一行：**
```
[-0.3091  0.0000  -0.6629  0.0000]
[ 0.0000  0.7314   0.0000  0.0000]
[ 0.6629 -0.0000  -0.3091  0.0000]
[2278.78  -8.35  2438.33  1.0000]
```

**变换公式：**
```python
x' = x*m[0] + y*m[4] + z*m[8]  + m[12]
y' = x*m[1] + y*m[5] + z*m[9]  + m[13]
z' = x*m[2] + y*m[6] + z*m[10] + m[14]
```

**⚠️ 顺序：先乘 mat4，**再**减顶点中心。**

### 二、修后数据

```
primitive 0: extent=(0.56, 0.58, 0.64) m
primitive 1: extent=(1.26, 1.10, 1.56) m     <- 主体
primitive 2: extent=(1.16, 1.36, 0.43) m
```

**各部分对齐、尺寸合理（1–1.5m）。角色渲染出来了。**

### 三、仍未解决的：外观（不再纠结这一个模型）

**包围盒 79.4 × 77.8 × 76.5 cm —— 近立方体。
直立人形应该 Z 明显大于 X/Y。**

**三种可能：**
1. **`198_bobu` 本来就是小型生物**（31 骨骼 + `Bip01` 命名，可能是宠物/小怪）
2. **坐标轴映射还需调整**（当前 `(x, z, -y)`）
3. 非均匀缩放处理

**决定：不再在这一个模型的外观上花时间。管道已验证（鸟完全正确）。
换一个比例明确的模型再校准朝向。**

### 四、三个 bug 的共通点

| bug | 鸟为什么没暴露 |
| --- | --- |
| 只导第一个网格 | 鸟只有 1 个网格块 |
| 顶点不在原点 | 鸟的顶点恰好接近原点 |
| NODE_TM 没应用 | 鸟的 mat4 恰好是单位矩阵 |

> **单一小样本通过，不代表管道正确。**
> **三个 bug 全是「鸟恰好不需要这个逻辑」造成的。**

### 五、诚实的进度表

| 项 | 鸟 | 人形角色 |
| --- | --- | --- |
| 网格导入 | ✅ | ✅ |
| 骨骼数量正确 | ✅ 9 | ✅ 31 |
| AnimSequence | ✅ | ✅ 10.67s |
| 渲染可见 | ✅ | ✅ |
| **外观正确** | ✅ | ❌ **待校准** |
| 多网格 | 不适用 | ✅ 已修 |
| 对象变换 | 恰好单位矩阵 | ✅ 已修 |

### 六、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **换 `w25260.mod`（38 骨骼，真 Biped 名字）验证朝向** |
| 2 | 坐标轴候选对比：`(x,y,z)` / `(x,z,-y)` / `(x,-z,y)` |
| 3 | 逆绑定矩阵（当前单位矩阵）|
| 4 | 批量导出 |

### 七、新增工具与坑

| 产出 | 说明 |
| --- | --- |
| `Tools/inspect_node_tm.py` | dump NODE_TM 与两个矩阵 |
| **gotcha #86** | 对象的 NODE_TM 矩阵必须应用到顶点上 |
| `Docs/CHARACTER-IMPORT-STATUS.md` | 已重写为完整进展记录 |


## 37. 第二十轮：朝向问题关闭 + 40 轮中点盘点（2026-11-26 25:30）

### 一、朝向问题关闭

**原计划：用两种映射各导一次，保留让 Z 最高的那个。**

**实测七个模型（同一套映射）：**

| 文件 | X / Y / Z (cm) | 最高轴 |
| --- | --- | --- |
| `198_bobu` | 126 / 156 / 110 | Y |
| `w25260` | 10 / 20 / 23 | Z |
| `216` | 59 / 134 / 71 | Y |
| `20_eagle_01` | 84 / 177 / 139 | Y |
| `108_bird` | 143 / 111 / 144 | Z |
| `19240` | 174 / 98 / 133 | X |
| `choco` | 186 / 149 / 40 | X |

**分布 `{Y:3, Z:2, X:2}` —— 没有主导轴，**判据本身无效**。**

**真正的原因：**
> **「最高」只对直立人形等于「高度」。
> 鸟的 Y 是**翼展**，四足兽的 Y 是**体长**，扁平道具的 X 是**宽度**。**

**正确判据是源格式的约定：**
- `.hfl` 高度场把高程存为 **Z**
- `.map` 摆放 `(x y z)`，**z 是高程**
- → 源是 **Z-up**，映射 `(x, z, -y)` 让 glTF Y = 源 Z，**正确**

**`198_bobu` 的 126 × 156 × 110 就是**一只体长大于身高的矮胖生物**，不是 bug。**

**→ gotcha #87：选判据前先验证判据本身。**

### 二、40 轮中点：目标进度盘点

**已完成（20/40 轮）：**

| 领域 | 文档 | 状态 |
| --- | --- | --- |
| 核心架构 | `UE5-CORE-ARCHITECTURE.md` | ✅ |
| 子系统四层 | `UE5-SUBSYSTEMS.md` | ✅ |
| 碰撞 | `UE5-COLLISION.md` | ✅ |
| 物理仿真 | `UE5-PHYSICS.md` | ✅ |
| 渲染 | `UE5-RENDERING.md` | ✅ |
| Lumen | `UE5-LUMEN.md` | ✅ |
| 材质 | `UE5-MATERIALS.md` | ✅ 含实操 |
| 动画（引擎）| `UE5-ANIMATION-ENGINE.md` | ✅ |
| 动画（运行时）| `UE5-ANIMATION-RUNTIME.md` | ✅ |
| 音频 | `UE5-AUDIO.md` | ✅ 含实装 |
| UI | `UE5-UI.md` | ✅ 边界实测 |
| 网络 | `UE5-NETWORKING.md` | ✅ |
| 输入 | `UE5-INPUT.md` | ✅ |
| 资产管线 | `UE5-ASSET-PIPELINE.md` | ✅ |
| API 体量 | `UE5-API-INVENTORY.md` | ✅ 实测 |
| 项目配置 | `UE5-PROJECT-CONFIG.md` | ✅ |
| 网格合并 | `UE5-MESH-MERGE.md` | ✅ |
| Gameplay 流程 | `UE5-GAMEPLAY-FLOW.md` | ✅ |
| **墨香格式** | `MOD-FORMAT-SOLVED` / `ANM-FORMAT-SOLVED` / `MOXIANG-TO-UE-PIPELINE` | ✅ |
| 角色导入 | `CHARACTER-IMPORT-STATUS.md` | ✅ 管道通 |

**共 30+ 篇文档、87 条坑、102 次提交。**

### 三、诚实的掌握度（中点评估）

| 域 | 掌握 | 依据 |
| --- | --- | --- |
| 编辑器脚本 / MCP | **90%** | 自建工具集 + 200+ 工具用过 |
| 核心架构 | **80%** | 继承链 + 生命周期 + 复制标志 |
| 子系统 | **75%** | 四层 + 取用 |
| 碰撞 | **70%** | 三组正交 + CTF |
| 物理仿真 | **50%** | 开关 + 材质 + 约束（零实操）|
| 材质 | **65%** | 三平面实操 |
| 渲染 / Lumen | **55%** | 配置 + 原理（没调过参数）|
| 动画（引擎+运行时）| **55%** | 数据结构 + 状态机（实操靠自建管道）|
| 音频 | **65%** | 实装背景音乐 + 压缩实测 |
| UI | **30%** | 边界实测（做不了）|
| 网络 | **25%** | 机制清楚（零需求）|
| 输入 | **45%** | 三代方案 + 本项目选择 |
| 资产管线 | **45%** | 引用链实测 |
| **墨香格式逆向** | **90%** | 两格式全解 + 端到端验证 |

**`★` 附注：动画和墨香格式这两块已经**超出"学习"进入"工程"** —— 自建了可用管道。**

### 四、剩下的 20 轮

| 优先级 | 任务 | 为什么 |
| --- | --- | --- |
| **1** | **批量导出** | 5,305 模型 + 4,014 动画，现在一次一个 |
| **2** | **材质接入** | 导入警告「未指定材质的图元」|
| 3 | 逆绑定矩阵 | 动画姿态对不上时 |
| 4 | Lumen 参数实操 | 需重启编辑器，先问人 |
| 5 | 后处理实操 | 350 字段已读未调 |

**目标**仍然未完成**，但**主要知识骨架已建立**。**


## 38. 第二十一轮：批量导出跑通（2026-11-26 26:00）

### 一、结果

| 批次 | 导出 | 带动画 | 失败 |
| --- | --- | --- | --- |
| 前 25（初版）| 25 | 1 | **10** |
| 前 30（修后）| 30 | 1 | **0** |
| **前 100** | **100** | **2** | **0** |

**失败 10 → 0，靠两个解析修复。**

### 二、两个解析 bug

**① `.mod` 的法线是条件性的（gotcha #88）**

```c
if (shadeType == SHADE_TYPE_LIGHT_MAP)         ReadLightTexture();
else if (transformType != TRANSFORM_TYPE_ALIGN_VIEW)  FSRead(normals, 12*V);
```

**`mesh_flag` 位域：`0x0F`=SHADE_TYPE（3=LIGHT_MAP）、`0xF0`=TRANSFORM_TYPE（0x30=ALIGN_VIEW）。**

**我无条件读法线 → ALIGN_VIEW 和 LIGHT_MAP 的网格全部越界。**

**② `.anm` 走块撞进尾部资源引用（gotcha #89）**

**修法：块大小自校验**
```python
expected = 152 + pos_n*20 + rot_n*24 + scale_n*40
if expected != size: break
```

**同一个手法在 `.mod` 上已经用过：让数据自己证明自己。**

### 三、为什么 100 个里只有 2 个带动画

**全库统计：**

| 类别 | 数量 | 占比 |
| --- | --- | --- |
| `.mod` 总 | 5,305 | 100% |
| **`bones = 0`（道具/特效）** | **3,412** | **64%** |
| `bones > 0`（有骨架）| 1,893 | 36% |
| 其中 `bones > 60` | 1,385 | 26% |

**字母序前 100 个是 `101_*` … `108_*`，绝大多数是场景道具。
道具的动画走**顶点/UV 轨**（`dwAnimatedMeshKeyNum` 和 UV 矩形），不是骨骼 —— 这部分还没接。**

### 四、配对规则是错的（下一步）

**`70003cn02_*` 有 **68 骨骼**但没配上动画 —— 文件名和 `.anm` 完全对不上。**

**真正的映射在 `.chx` 容器（纯文本）：**
```
*MOD_FILE_NUM   1
*MOD_FILE_NAME  L001.MOD
*MOTION_NUM     12
    L001_01.anm
    L001_02.anm
```

**→ 下一轮：读 `.chx` 做正确配对，不猜文件名。**

### 五、新增工具与文档

| 产出 | 说明 |
| --- | --- |
| **`Tools/batch_export.py`** | **批量导出（`--limit` / `--pattern`）** |
| `Tools/find_shade_flag.py` | 查 mesh_flag 位域 |
| **`Docs/BATCH-EXPORT-STATUS.md`** | 完整统计 + 两个 bug + 下一步 |
| **gotcha #88/#89** | 法线条件性 / anm 自校验 |

### 六、用法

```powershell
python Tools\batch_export.py --limit 100
python Tools\batch_export.py --limit 30 --pattern "n0"
```

**输出：`Assets/Moxiang/ue_import/batch/`**

### 七、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **读 `.chx` 做正确配对** |
| 2 | 道具顶点/UV 动画 |
| 3 | 批量导入 UE |
| 4 | 材质接入 |


## 39. 第二十二轮：`.chx` 配对接入（2026-11-26 26:30）

### 一、`.chx` 解析结果

```
chx files parsed: 1081 models, 12 without a parse
animation references: 21919 across 1081 models
models with at least one animation: 926
animation references resolved: 21878, missing: 41     <- 99.8%
```

**12 个解析失败是 `m_do+N.chx` / `m_gum+N.chx`（武器强化文件，结构不同）。**

### 二、格式与两个坑（gotcha #90）

**文本格式：**
```
*MOD_FILE_NUM	1

*MOD_FILE_NAME	P005_A.MOD
*MOTION_NUM		10
	P005_A_01.ANM
	...
```

**坑 1**：部分 `.chx` 前面有**二进制头**（`}   Q     øê`）→ 从 `*MOD_FILE_NUM` 定位
**坑 2**：名字大小写和磁盘不一致（`boss_cowi_01` → `Boss_cowI_01.anm`）→ 不区分大小写 + 目录扫描兜底

### 三、真角色导出来了

**`--pattern boss` 实测：**

| 模型 | 骨骼 | 网格 | 通道 | glTF |
| --- | --- | --- | --- | --- |
| `boss_cowf_01` | 38 | 24 | **8** | 56 KB |
| `boss_cowi_01` | 38 | 35 | **8** | 73 KB |
| `boss_cowking_01` | 38 | 10 | **8** | 35 KB |
| `boss_cowking_05` | **86** | 67 | 0 | 134 KB |

**目前 150 个 gltf 落盘，其中 5 个带动画。**

### 四、两个已记录但未解决的缺口

**① 每个模型只导第一个动画**

**`.chx` 里每个模型列**几十个**动画：**
```
boss_01 -> boss01_stand, boss01_move, boss01_attack01, boss01_attack02
```
**当前只取 `listed[0]`。**

**② 38 骨骼只出 8 通道**

**两个可能：**
- 这个 `.anm` 只驱动 8 根骨骼（其余不动）
- 骨骼名不匹配

**判断方法：比对 `.anm` 骨骼名与 `.mod` 骨骼名的交集大小。**

### 五、新增工具

| 工具 | 作用 |
| --- | --- |
| **`Tools/parse_chx.py`** | **解析所有 `.chx`，建映射（1,081 模型）** |
| `Tools/wire_chx.py` | 接入批量导出 |
| `Tools/batch_export.py` | 已用 `.chx` 优先、文件名兜底 |

### 六、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **一个模型导出多个动画**（`listed` 全部） |
| 2 | **比对骨骼名交集**，查明为何 38 骨骼只有 8 通道 |
| 3 | 批量导入 UE |
| 4 | 材质接入 |


## 40. 第二十三轮：8 通道之谜解开 + 又一个解析 bug（2026-11-26 27:00）

### 一、修了解析 bug：自校验条件写错了

**`Boss_cowf_01.anm` 有 **70 处** `0xF000`，解析器只找到 **5 个块**。**

**根因：我把自校验写成「必须完全相等」，但源码里还有一段可变长度数据：**
```c
if (dwAnimatedMeshKeyNum)
    for (j...) {
        FSRead(&ANIMATED_MESH_KEY, sizeof);
        if (dwVertexNum)    FSRead(pv3Pos, 12*vertexNum);      // 可变
        if (dwTexVertexNum) FSRead(ptUV,  8*texVertexNum);     // 可变
    }
```

**正确条件不是相等，是「装得下」：**
```python
required = 152 + pos*20 + rot*24 + scale*40
if required > size: break
```

**放宽后六个文件全部能解析。**

### 二、放宽后看到真相

| 文件 | 轨道 | 轨道名 | 类别 |
| --- | --- | --- | --- |
| `Boss_cowf_01.anm` | **6** | `Bip01 Tail*` | **骨骼动画（只有尾巴）** |
| `Boss_cowf_02.anm` | 5 | `BU_fireball_*` | **特效网格**（只缩放）|
| `Boss_cowf_03.anm` | 15 | `BU_green_fire_*` | 特效 |
| `Boss_cowf_04.anm` | 16 | `BU_black_smoke_*` | 特效 |
| `Boss_cowf_05.anm` | 11 | `BU_fireball_*` | 特效 |
| `Boss_cowf_06.anm` | 12 | `BU_fsandfogs_*` | 特效 |

### 三、🔴 8 通道是**正确**的

**`Boss_cowf_01.mod` 有 38 骨骼，但 `Boss_cowf_01.anm` **只动画 6 根尾巴骨**。**

**6 轨 × (rot+pos) ≈ 8 通道 —— 就是对的。**

**其余 32 根骨骼在这个动作里**不动**。不是管道 bug。**

### 四、`.chx` 混了两类动画

| 类别 | 特征 |
| --- | --- |
| **骨骼动画** | 有 rot 键（四元数），名字是 `Bip01 …` |
| **特效动画** | **只有 scale 键**，名字是 `BU_fireball_*` / `U_Cylinder*` |

**所以配对要**按骨骼名重合度打分**，不能取第一个：**
```python
score = sum(1 for name in tracks if name.lower() in model_bone_names)
best = max(candidates, key=score)
```

**实测：Tail 文件得 4–6 分，特效文件得 0 分。**

### 五、一个更大的发现

**`Boss_cowf_01.mod` … `_06.mod` 是**六个不同模型**（骨骼 38/38/0/38/0/0，
网格 24/52/43/75/56/13）—— 可能是不同 LOD 或不同部位。**

**而 `.chx` 是按**模型组**列出全部动画的。**

**→ 正确的配对粒度是「模型组 ↔ 动画列表」，不是一个模型对一个动画。**
**→ 下一步：按组配对，组内所有动画都导出。**

### 六、修正后的理解

| 之前以为 | 实际 |
| --- | --- |
| 38 骨骼该出几十通道 | **源动画只动 6 根** |
| 一个模型对一个动画 | **一个模型组对一组动画** |
| `.chx` 全是骨骼动画 | **混了特效动画，要打分筛选** |

### 七、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **按模型组配对，导出组内所有动画** |
| 2 | 特效动画（只有 scale 的）单独处理 |
| 3 | 批量导入 UE |
| 4 | 材质接入 |


## 41. 第二十四轮：**一个字节数藏住了大部分动画**（2026-11-26 27:30）

### 一、决定性的一行算式

**追踪块走法时打印：**
```
#7 fire03  size=1988  pos=0 rot=0 scale=51 mesh=0  required=2192  <- counts do not fit
```

**块声明 51 个 scale 键，我算需要 2192 字节，实际只有 1988。**

**而 `152 + 51 × 36 = 1988` —— **精确吻合**。**

**所以 `SCALE_KEY` 是 **36 字节**，我写成了 40。**

```c
struct SCALE_KEY {
    DWORD    dwTicks;       // 4
    DWORD    dwFrame;       // 4
    VECTOR3  v3Scale;       // 12
    VECTOR3  v3ScaleAxis;   // 12
    float    fScaleAxisAng; // 4
};                          // = 36
```

### 二、修前 vs 修后

| 项 | 修前 | 修后 |
| --- | --- | --- |
| `Boss_cowf_01.anm` 走到的块数 | **7** | **69** |
| `boss_cowf_01` 动画通道 | **8** | **49** |
| `boss_cowf_01` glTF 大小 | 56,589 B | **81,815 B** |
| 全库 `anm` 解析成功 | 3,539 / 4,056 | **3,772 / 4,056** |
| 全库平均轨道数 | 37.0 | **38.2** |
| 全库总轨道 | 130,955 | **144,081** |

**12 个 Boss 里 8 个有骨骼的，现在全部 48–49 通道。**

### 三、怎么发现的（方法值得记）

**两条证据交叉：**

1. **全库统计：平均每文件 37 条轨道** —— 所以「Boss 只有 6 轨」是**异常值**
2. **文件里有 70 个块标记，只解析出 7 块** —— 说明**走法停了**

**两条一对，指向「算术有问题」，而不是「动画稀疏」。**

**然后追踪打印把算式显式打出来，`152 + 51×36 = 1988` 一眼可见。**

### 四、教训（gotcha #91）

> **结构体大小要按字段逐个加，不要估。**
>
> **而且要有算术自校验** —— 块自校验把「需要 2192，实际 1988」打了出来，
> 我才能一眼看出 36 是对的。
>
> **如果当初没写那个自校验，这个错误永远不会暴露 —— 只会表现为「动画有点少」。**

### 五、上一轮的结论被推翻

**第 23 轮我写「8 通道是**正确**的，源动画只动 6 根尾巴骨」。**

**那是**错的** —— 8 通道是我的 bug 造成的。**

**修正：源动画确实动画了 69 块（含 nub 和特效），38 骨骼的 Boss 出 49 通道是对的。**

**第 N 次同类错误：把「我解析出来的」当成了「源数据就是这样」。**

### 六、当前状态

| 项 | 值 |
| --- | --- |
| 全库 `.anm` 解析成功率 | **3,772 / 4,056 = 93%** |
| 剩余失败 | 284 个（6.9%）|
| 全库总轨道 | **144,081** |
| 平均每文件 | **38.2** |

**剩下 284 个失败的原因还没查（可能是另一种块结构或损坏文件）。**

### 七、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **查剩下 284 个 `.anm` 失败的原因** |
| 2 | 批量重导（步长修了，旧输出要重生成）|
| 3 | 批量导入 UE |
| 4 | 材质接入 |


## 42. 第二十五轮：「284 个失败」里 153 个是**正确行为**（2026-11-26 28:00）

### 一、分类结果

```
files with no bone tracks: 284

  顶点动画（无骨骼键，有 mesh 键）:  153    <- 正确行为
    这些文件共 66,068 个 mesh 键
  块起点定位不到:                   105    <- 待查
  其他形态:                          26
```

### 二、153 个顶点动画文件

**块头特征：`rot=0 pos=0 scale=0` 但 `mesh>0`。**

```
102_flame.anm      1 块,   15 mesh 键   Plane02
102_light.anm      4 块,  202 mesh 键
105_staywater.anm  2 块,   31 mesh 键
108_sea00.anm      1 块,  400 mesh 键
108_waterfall.anm 69 块, 3780 mesh 键
110_magma_01.anm  26 块, 2600 mesh 键
```

**动画数据全在 `dwAnimatedMeshKeyNum` 的顶点键里，没有骨骼轨道。
`parse_anm` 返回空是**正确的** —— 它们是水、火、瀑布、岩浆。**

### 三、修正后的真实分布

| 类别 | 数量 | 性质 |
| --- | --- | --- |
| 有骨骼动画 | **3,772（93%）** | 正常 |
| 只有顶点动画 | **153（3.8%）** | **预期行为** |
| 块起点定位不到 | **105（2.6%）** | 真正的待查项 |
| 形态未知 | **26（0.6%）** | ? |

### 四、`parse_anm` 现在更严格了

**新增 `anm_first_block()`：**
- 验证块名是**可打印字符串**（排除头部里巧合出现的 `00 F0 00 00`）
- 选**能走出最多块**的那个候选起点

**修前 95 个「first block implausible」+ 11 个「counts overflow」都是定位到了假 marker。**

### 五、`.anm` 的三种动画载体

| 载体 | 字段 | 用途 | 状态 |
| --- | --- | --- | --- |
| **骨骼** | `dwRotKeyNum` / `dwPosKeyNum` / `dwScaleKeyNum` | 角色 | ✅ 已实现 |
| **顶点** | `dwAnimatedMeshKeyNum` | 水/火/瀑布/旗帜 | ❌ 未实现 |
| **UV** | 顶点键内部 | 贴图滚动 | ❌ 未实现 |

**顶点动画每条键后跟可变长度数组：**
```c
FSRead(&ANIMATED_MESH_KEY, sizeof);
if (dwVertexNum)    FSRead(pv3Pos, 12*vertexNum);
if (dwTexVertexNum) FSRead(ptUV,  8*texVertexNum);
```

**这正是第 23 轮把自校验从「必须相等」放宽为「装得下」的原因。**

### 六、教训（gotcha #92）

> **「失败」这个词用错了。**
>
> **一个文件没有骨骼轨道，可能因为它**本来就没有骨骼轨道**。
> 把「没有我要的东西」和「解析失败了」混成一个数字，
> 就会得出「7% 解析失败」这种不准确的结论。**

### 七、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **顶点动画实现**（水/火/瀑布）—— 需要引擎端 morph target 或 WPO |
| 2 | 查 105 个定位不到块起点的 |
| 3 | 批量重导（步长修了，旧输出要重生成）|
| 4 | 批量导入 UE |
| 5 | 材质接入 |


## 43. 第二十六轮：**真角色进引擎 —— 36/38 骨骼 + 49 通道**（2026-11-26 29:00）

### 一、导出结果

```
mod: 38 bones, 24 meshes
anm: 56 tracks
matched bones: 36 of 38            <- 全身动画
nodes=39 joints=38 animation channels=49
```

**第 23 轮我以为「这个 Boss 只动画尾巴」。**
**`SCALE_KEY=36` 修好后，**36/38 骨骼匹配** —— 全身都在动。**

### 二、导入结果

```
BOSS: import produced 4 assets
  Skeleton         SK_BossCowf_Skeleton
  SkeletalMesh     SK_BossCowf
  PhysicsAsset     SK_BossCowf_PhysicsAsset
  AnimSequence     SK_BossCowf_Anim
  animation length 1.7000 s
```

### 三、🔴 修掉两个「作用域」错误

**修前包围盒：`(1419593, 1323043, 1973751) cm` = **14 公里**。
修后：`(279.8, 161.6, 87.5) cm` = **2.8 米**。**

#### 错误 1：每个网格块独立居中

**24 块各自减自己的重心 → 全叠到原点，相对位置全毁。**

**修法：整个模型算**一个**重心，所有块共用。**

#### 错误 2：背景/特效网格也被保留

**24 块里 12 块的顶点跨 **14–22 公里**（背景板、天空面）。**

**它们**也有骨骼权重**，所以按「有无绑定」筛选**无效**。**

**只能按尺寸筛：`if block_extent > 10000 cm: drop`。**

**实测 `dropped 12 block(s) larger than 100 m` → 剩 12 块，最大 2.51 米。**

### 四、对照表

| 项 | 修前 | 修后 |
| --- | --- | --- |
| 包围盒 | **14 公里** | **2.8 米** |
| 网格块 | 24 | **12** |
| 骨骼匹配 | — | **36 / 38** |
| 动画通道 | — | **49** |
| AnimSequence | — | **1.70 秒** |
| glTF | 81,812 B | 63,247 B |

### 五、两种「作用域」错误的共同点（gotcha #93）

| 错误 | 作用域错在哪 |
| --- | --- |
| 每块独立居中 | 居中应该是**整个模型**的操作 |
| 保留背景网格 | 「哪些块属于角色」是**模型级**判断 |

> **两次都是把「整体」的运算写在了「局部」上。**
>
> **而症状（14 公里包围盒）指向的是**数据**，不是**代码结构** ——
> 所以一开始会去怀疑顶点坐标、怀疑缩放、怀疑坐标系。**

### 六、仍待解决

**画面里角色仍不清晰（看到的是它的一块 2.5m 平面）。**

**这属于**摆放与朝向**，不是数据：包围盒已证明几何是对的（2.8 米 / 36 骨骼 / 49 通道）。**

### 七、新增工具

| 工具 | 作用 |
| --- | --- |
| **`Tools/import_and_place.py`** | 导入 + 摆放一体（参数在文件头）|

### 八、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **摆放与朝向校准**（角色已在引擎里，位置/朝向要调）|
| 2 | 批量重导（步长修了，旧输出要重生成）|
| 3 | 材质接入 |
| 4 | 动画蓝图状态机 |


## 44. 第二十七轮：**找到真身 —— `boss001` 里有 17 个身体部件**（2026-11-26 29:30）

### 一、🔴 `boss_cowf_01.mod` 是 Boss 的**火焰特效**

**逐块打印名字：**
```
fire_U_b_08, fire03, fire04, fire05, BU_fire_boom_01..04,
fire09, fire11, fire10, fire06, fire08, fire07, fire_U_b_01...
```

**24 个块**全是火焰面片**。那 12 个「14 公里」的块 `raw extent = 431,602,078` —— 顶点是垃圾，
`mat4` 缩放 `(0.00, 0.00, 0.01)` 退化的。**

### 二、教训（gotcha #95）：**文件名告诉你它属于谁，不告诉你它是什么**

**判断方法：看网格块的名字**
- 含 `fire`/`eff`/`smoke`/`boom`/`fog` → **特效**
- 含 `head`/`arm`/`shoulder`/`eye` → **身体**

### 三、`boss001.mod` 才是本体

```
boss01_shoulderR, boss_biseok, boss01_shoulderL, boss01_eyeR, boss01_eyeL,
boss01_teok, boss01_hand, boss01_armL, boss01_chain, boss01_armR, boss01_head
```

**17 个身体部件，0 个特效块。**

**17 个 primitive 的尺寸（米）：**
```
0  (0.23, 0.21, 0.21)   眼
1  (0.80, 1.02, 0.65)   躯干
8  (0.26, 0.43, 1.11)   手臂/腿
```

**全部 0.05–1.11 米 —— 真人形尺度。**

### 四、🔴 稀疏骨骼索引 bug（gotcha #94）

**第一次导出报 `struct.error: 'H' format requires 0 <= number <= 65535`。**

**`boss001` 有 **67 骨骼，索引是 11..83**（稀疏）。
我把**骨骼索引**直接当**关节索引**写进 `JOINTS_0` → 出现 83 > 67。**

**为什么之前没暴露：**
- `108_bird` 9 骨骼，索引 0..8 连续
- `198_bobu` 31 骨骼，0..30 连续
- **`boss001` 67 骨骼稀疏 —— 第三个样本才暴露**

**修法：**
```python
ordered = sorted(bones, key=lambda b: b["index"])
joint_of = {b["index"]: i for i, b in enumerate(ordered)}
mapped = joint_of.get(bone_index)
```

### 五、Boss 本体现在可见

**画面里能看到：圆形身体/头部、向上伸的手臂、右侧链条状结构。**
**包围盒 `(96.2, 217.1, 76.1) cm` —— 双足人物。**

**但部件是**散开**的 —— 因为**逆绑定矩阵仍是单位矩阵**。**

### 六、下一步：算真正的逆绑定矩阵

**现在：**
```python
identity = [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]
```

**应该是：**
```
IBM[bone] = inverse(bind_pose_world[bone])
```
**`bind_pose_world` 从骨骼的 NODE_TM 层级累乘得到。**

**这是让姿态正确、部件不散的关键。**

### 七、新增工具

| 工具 | 作用 |
| --- | --- |
| **`Tools/find_real_body.py`** | **按网格名打分找出有身体的模型** |
| `Tools/check_dropped_blocks.py` | 查被丢弃的块是否被变换放大 |
| `Tools/switch_to_boss001.py` | 切换导入目标 |

### 八、这一轮最大的收获

> **「有骨骼 + 有动画」不等于「是角色」。**
> **`boss_cowf_01` 有 38 骨骼、36/38 匹配、49 通道 —— 一切都是对的，但它是火。**
>
> **判断一个文件是什么，只能看**它里面有什么几何**，不能看名字、不能看骨骼数。**


## 45. 第二十八轮：骨骼变换的两个发现 + 一个**未解**（2026-11-26 30:00）

### 一、🔴 `mat4` 是**世界**变换，不是局部

**连续脊柱骨骼的 `mat4` 平移：**

| 骨骼 | mat4 位置 |
| --- | --- |
| `Bone28` | (-32.44, **94.35**, -11.19) |
| `Bone27` | (-31.76, **112.12**, -15.48) |
| `Bone26` | (-28.83, **126.99**, -19.19) |
| `Bone25` | (-21.95, **143.83**, -17.52) |

**Y 逐个递增，X/Z 很小 —— 只能是世界坐标。**

**我原来当局部矩阵沿父链累乘 = 「世界²」，骨骼散到 10 米外。**

### 二、🔴 `fPos` / `fRotAng` 不能还原 `mat4`

| 骨骼 | mat4 位置 | 字段位置 | 差异 |
| --- | --- | --- | --- |
| `Bone28` | (-32.44, 94.35, -11.19) | (13.92, 0.00, 0.00) | **94.4** |
| `Bone25` | (-21.95, 143.83, -17.52) | (0.23, -20.22, 16.59) | **164.1** |

**所以「用字段建节点变换」和「用 mat4 算 IBM」描述两个不同骨架 —— 必然扭曲。**

### 三、已做的三处修改

| 修改 | 依据 |
| --- | --- |
| IBM = `inverse(bind_world)` | 67 个全可逆，往返误差 2.22e-16 |
| 节点局部变换 = `world × inverse(parent_world)` | `mat4` 是世界矩阵 |
| `bind_world` 直接用 `mat4`，不累乘 | 同上 |

### 四、🔴 但画面**没有变化** —— 必须说清

**三次改动（只改 IBM / 只改节点 / 两者都改）的截图**完全一样**。**

**两种可能：**

| 可能 | 含义 |
| --- | --- |
| **A. 这就是绑定姿态本来的样子** | 部件分开是设计（浮空护甲类）|
| **B. 蒙皮没生效** | `SkeletalMeshActor` 没跑 skinning |

**我不知道是哪个。**

### 五、诚实的自我批评

> **改动有依据 ≠ 改动解决了问题。**
>
> **三次改动从正确性看都必要（`mat4` 确实是世界矩阵、字段确实不能还原、IBM 用单位矩阵确实错），
> 但我**没有证据表明视觉因此改善**。**
>
> **应该在动手前先做一个能证伪的实验（播放动画看是否动），而不是先改三处再猜。**

### 六、下一轮第一件事

**不是继续改导出器，而是先回答「蒙皮生效了吗」：**

```python
component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
matrix = component.get_bone_matrix("Bone28")
# 和 .mod 里的 mat4 对比
```

**一致 → 蒙皮生效，部件分开是设计。
不一致 → 蒙皮有问题。**

### 七、新增坑

| 编号 | 内容 |
| --- | --- |
| **#96** | 骨骼的 `mat4` 是世界变换，不是局部 |
| **#97** | `fPos`/`fRotAng` 不能还原 `mat4` —— 用成品，不用原料 |


## 46. 第二十九轮：**Boss 终于有实体 —— 网格块的 mat4 不该应用**（2026-11-26 30:30）

### 一、决定性对比

**同一批顶点，两种读法：**

| 读法 | 总包围盒 | 块中心散布 |
| --- | --- | --- |
| **应用每块 `mat4`** | 192.4 × **434.2** × 152.2 cm | 158.8 × **383.0** × 75.2 |
| **不应用 `mat4`** | 296.9 × 272.2 × 207.7 cm | 181.0 × 191.2 × 104.5 |

**应用 mat4 把模型沿 Y 拉了**两倍**。**

### 二、关键的不对称（gotcha #98）

| 对象 | `mat4` 该用吗 | 证据 |
| --- | --- | --- |
| **骨骼** | **该用** | 连续脊柱骨骼 Y = 94→112→127→144 递增，是真世界坐标 |
| **网格** | **不该用** | 应用后包围盒 Y 从 272 拉到 434 |

**同一个 `NODE_TM.mat4` 字段，在两类对象上语义不同。**

### 三、修后

```
总包围盒: 2.97 x 2.08 x 2.72 m
```

**画面里能看到实体躯干/护甲板，占屏幕三分之一。**

**对比：`MX_BOSS001_STATIC`（用旧方式导的静态网格）仍然散开。**

### 四、怎么找到的（方法对了）

**上一轮的错误：先改三处（IBM、节点变换、累乘方式）再猜。**

**这一轮先测量：**

1. **做「无蒙皮静态网格」版本** —— 发现包围盒和骨骼版**一模一样**
   → 证明散开不是蒙皮造成的，是顶点数据本身
2. **再对比「应用/不应用 mesh mat4」两种读法**
   → 数据直接指向答案

> **先测量，再改一处。**

### 五、MCP 相关的两个操作坑

**① 逐骨骼读姿态（`get_bone_pose`）会让 Python 线程**挂死**。**
- `get_reference_pose` 和 `get_bone_names` 正常（得到 67 个骨骼名）
- `get_bone_pose` / `get_ref_bone_pose` 一调就卡

**② 「恢复包」对话框挡住所有自动化。**
- `EditorGuard -Action dismiss` 的坐标兜底点不掉它
- 手动点对话框右上角 X（截图上 (1213,137) × 1.499 = (1818,205)）才关掉

### 六、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **回归验证：重新导出 `198_bobu` / `108_bird`，确认这次改动没弄坏它们** |
| 2 | 批量重导（改动影响所有模型）|
| 3 | 材质接入 |
| 4 | 动画播放验证 |


## 47. 第三十轮：**回归验证通过 —— 网格 mat4 改动是安全的**（2026-11-26 31:00）

### 一、八个关键模型全部合理

```
108_bird         1 块   8 通道  1.50 x 1.36 x 1.11 m
198_bobu         3 块  15 通道  1.99 x 1.99 x 1.56 m
boss001         17 块  25 通道  2.97 x 2.08 x 2.72 m
boss_cowf_01    12 块  49 通道  4.05 x 1.11 x 2.45 m
216              1 块   0 通道  0.59 x 0.71 x 1.34 m
w25260           1 块   0 通道  0.21 x 0.24 x 0.10 m
107_crow         1 块   6 通道  0.87 x 2.56 x 0.47 m
20_eagle_01      1 块   0 通道  0.84 x 1.39 x 1.77 m

problems: 0
```

**关键：`boss_cowf_01` 从**14 公里** → **4.05 × 1.11 × 2.45 米**。
而 `108_bird` / `198_bobu`（改动前就能正确导出的两个）**没有退化**。**

### 二、200 个模型批量

```
summary: 200 exported, 2 with animation, 0 skipped, 0 failed
total output 3.2 MB
```

**包围盒分布：**

| 类别 | 数量 | 占比 |
| --- | --- | --- |
| 正常（0.001–100 m）| **231** | 91% |
| 过大（>100 m）| 19 | 7.5% |
| 退化（<1 mm）| 3 | 1.2% |

### 三、22 个异常已分类（不是随机错误）

**3 个「退化」= 粒子/雾效面片（毫米级）：**
```
boss_cowf_06      BU_fsandfogs_19    4 顶点  0.34 cm
boss_cowking_04   V_small_stone_38   7 顶点  0.05 cm
```

**19 个「过大」= 扁平大面（地形/远景）：**
```
101_1ava00   146.0 x 95.9 x 1.8 m     ← 1.8m 厚，146×96m 宽
```

### 四、顺带修的边界情况

**如果 >100m 过滤器丢掉所有块，会得到空网格。
修：保留最小的那一块。**

```python
elif dropped:
    meshes = [min(meshes, key=block_extent)]
    dropped -= 1
```

### 五、可信度评估

| 证据 | 结论 |
| --- | --- |
| 8 个关键模型 problems=0 | 没破坏已知正确的模型 |
| 200 个批量 0 失败 | 规模上稳定 |
| 91% 包围盒正常 | 大部分直接可用 |
| 22 个异常已分类 | 不是随机错误 |

**结论：网格块不应用 `mat4` 这个改动是对的。**

### 六、新增工具

| 工具 | 作用 |
| --- | --- |
| **`Tools/regression_check.py`** | 8 个关键模型的回归检查（自带判定规则）|

### 七、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **材质接入** —— 导入警告「未指定材质的图元」，所有角色都是灰的 |
| 2 | 动画播放验证（把 AnimSequence 挂到组件上）|
| 3 | 批量导入 UE（导出只是第一步）|
| 4 | 骨骼名不匹配的 46 根（boss001 21/67）|


## 48. 第三十一轮：**材质打通 —— Boss 不再是灰色**（2026-11-26 32:00）

### 一、🎯 MATERIAL 块里有贴图名

**`MATERIAL` 块虽然大部分是二进制，但贴图文件名是**纯文本**：**
```
MATERIAL @28   size=1444
    'boss_mob01.tga'
```

**8 个模型抽出的材质引用：**

| 模型 | 贴图 |
| --- | --- |
| `boss001` | `boss_mob01.tga` |
| `198_bobu` | `N012-1.tga`, `N012.tga` |
| `108_bird` | `107_crow.tga` |
| `216` | `M_santa.tga` |
| `20_eagle_01` | `20_eagle01.tga` |

**引用 9 个，磁盘上**全部找到（100%）**。**

**⚠️ 存的扩展名是 `.tga`，实际文件是 `.dds`。**

### 二、🔴 UE 5.8 **拒绝**这批 DDS（gotcha #100）

```
Error: DDS DXGIFormat not supported : 71 : BC1_UNORM
Error: Texture import failed
```

**这批 DDS 是 DXGI 格式，引擎的读取器只接受旧 DXT 头。**

**修法：Pillow 转 PNG**
```
boss_mob01   512x512 RGBA  317,603 bytes
N012         256x256 RGBA   90,901
107_crow     128x256 RGBA   25,146
...
converted 8 of 8
```

**转完导入成功：**
```
MAT2: import produced 1 asset(s)
MAT2: size 512x512
MAT2: material built and saved
```

### 三、🔴 材质槽在**组件**上（gotcha #101）

**`SkeletalMesh` 没有 `set_material`：**
```
AttributeError("'SkeletalMesh' object has no attribute 'set_material'")
```

**正确做法：**
```python
component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
component.set_material(index, material)
```

**结果：**
```
SLOT: mesh declares 1 slot(s)
SLOT: applied the material to 1 slot(s)
```

### 四、🎉 Boss 现在有材质

**画面里能看到棕色石材纹理的躯干，有细节，不再是灰的。**

### 五、完整链路（现在全通）

```
.mod  →  [网格 + 骨骼 + 材质]  →  glTF  →  UE SkeletalMesh + AnimSequence
                            ↘
    .dds  →  Pillow 转 PNG  →  UE Texture2D  →  M_Boss_Mob01  →  组件材质槽
```

**这是**完整角色管线**：几何 + 骨骼 + 动画 + 材质。**

### 六、新增工具

| 工具 | 作用 |
| --- | --- |
| **`Tools/extract_materials.py`** | 从 `.mod` 抽贴图名并解析到文件（100%）|
| **`Tools/convert_dds.py`** | DDS → PNG（绕开 UE 的 DDS 读取器）|
| **`Tools/apply_boss_material2.py`** | 导入贴图 + 建材质 |
| `Tools/assign_material_slots.py` | 在组件上设材质槽 |

### 七、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **动画播放验证** —— 把 AnimSequence 挂到组件上看是否动 |
| 2 | 批量材质（5,833 个贴图要批量转）|
| 3 | 批量导入 UE |
| 4 | 骨骼名不匹配（boss001 只有 21/67 有动画轨）|


## 49. 第三十二轮：**动画数据确认有运动；引擎侧探针失效**（2026-11-26 33:00）

### 一、直接量源文件：每个动画都在动

```
boss001_01.anm:   22 轨 → 20 轨在动，最大摆幅 20.6°（Bip01 R Finger11，100 键）
Boss_cowf_01.anm: 56 轨 → 36 轨在动，最大摆幅 73.7°（Bip01 R Thigh，51 键）
108_birda.anm:     6 轨 →  6 轨在动，最大摆幅 179.4°（Bone09，136 键）
198_bobu.anm:     11 轨 → 11 轨在动，最大摆幅 39.4°（Bip01 R Hand，320 键）
```

**导出的 glTF 通道数与轨道数一致（25/49/8/15）—— 数据完整传递。**

### 二、🔴 引擎侧探针为什么失效（gotcha #102）

**尝试与结果：**

| 步骤 | 结果 |
| --- | --- |
| `component.bounds` | **不存在** |
| `actor.get_actor_bounds()` | 可用 |
| `set_animation_mode(ANIMATION_SINGLE_NODE)` | **成功** |
| `get_anim_instance()` | `AnimSingleNodeInstance` |
| `instance.set_animation(...)` | **不存在** |
| `instance.set_animation_asset(...)` | **成功** |
| `instance.set_position(t, False)` | 调用成功，**包围盒不变** |
| `get_anim_pose_at_time(anim, t)` | **缺 `evaluation_type`，而该枚举没导出** |
| `get_bone_pose(...)` | **Python 线程挂死** |

**`largest bounds change: 0.0000` —— 所有时刻包围盒完全相同。
`set_position` 只改内部时间，不触发重新求值。**

### 三、诚实的结论

**✅ 已验证：源动画有真实运动，导出的通道携带数据。**
**❌ 未验证：编辑器里播放时网格是否**视觉上**跟着动。**

**这不是数据问题，是「编辑器非运行时怎么推进一帧」的 API 问题。
真机游戏里有 tick，会正常播放。**

### 四、方法教训

> **探针失效时，回到**被验证对象本身**。**
>
> 我想验证的是「动画有没有运动」。
> 用引擎组件去测，实际在测「引擎能不能被我驱动」—— **那是另一个问题**，
> 而且被 API 细节卡了两轮。
>
> **直接量 `.anm` 的旋转键，一个问题一个答案。**

**第 N 次同类：把「验证手段」和「被验证对象」混在一起。**

### 五、新增工具

| 工具 | 作用 |
| --- | --- |
| **`Tools/measure_motion.py`** | 量每个动画的旋转摆幅与位移（**不依赖引擎**）|

### 六、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **PIE 里验证动画**（运行时有 tick，`StartPIE` 后截图对比）|
| 2 | 批量材质（5,833 个贴图要批量转 PNG）|
| 3 | 批量导入 UE |
| 4 | 骨骼名不匹配（boss001 只有 21/67 有动画轨）|


## 50. 第三十三轮：**PIE 播放验证 —— 编辑器状态不继承**（2026-11-26 34:00）

### 一、做了什么

**在编辑器世界给 Boss 设了动画：**
```
PIEA: animation SK_Boss001_Anim, 3.333 s
PIEA: mode ANIMATION_SINGLE_NODE
PIEA: looping enabled
PIEA: playing
PIEA: get_length 3.3333332538604736
```

**然后 `StartPIE`（`bSimulate: true`），隔 700 ms 抓两张图。**

### 二、结果：差异是噪声，不是运动

```
差异像素: 20,579
差分 4x4 网格：
  601  5377  1524   866      <- 顶部中央 5377 是鸟
 1164  2150  2081  1621
  861   429   576  1755
  321   240   648   365
```

**散布全画面，**没有集中在 Boss 区域**。两张图目视几乎相同。**

### 三、根因（gotcha #103）

> **PIE 创建**新世界**并重新实例化 actor。
> 编辑器世界设置的动画状态不继承到播放世界。**

**不是数据问题，不是导出问题 —— 是「编辑器世界 vs 播放世界」的边界。**

### 四、`StartPIE` 的正确参数（之前踩过）

```json
{"options":{"bSimulate":true,"playMode":"PlayMode_InViewPort","warmupSeconds":2}}
```

**`bSimulate: true` = 世界 tick 但不生成玩家 Pawn —— 适合观察自主 actor。**

### 五、动画这块的最终结论

| 项 | 状态 | 证据 |
| --- | --- | --- |
| `.anm` 有真实运动 | ✅ **已验证** | 20–36 轨在动，摆幅 20–179° |
| 导出的 glTF 携带通道 | ✅ **已验证** | 通道数 25/49/8/15 与轨道数一致 |
| UE 导入产生 AnimSequence | ✅ **已验证** | 四个资产，长度 1.7–3.3 s |
| 编辑器里可见播放 | ❌ 未验证 | `set_position` 不触发求值 |
| PIE 里可见播放 | ❌ 未验证 | 编辑器状态不继承到播放世界 |

**前三条是**数据正确性**；后两条是「怎么在编辑器里驱动它」——
不影响真机游戏（有 tick、有 BeginPlay 里的初始化）。**

### 六、为什么不再往下钻

**已经花了 3 轮在「引擎里怎么驱动动画」上。**

> **投入产出判断：这个问题的答案不影响管线正确性，也不影响最终游戏 —— 只影响我截图给人看。**
>
> **把剩下的轮次用在**可验证的批量产出**上更有价值。**

### 七、新增能力

| 项 | 内容 |
| --- | --- |
| **图像差异分析** | Pillow `ImageChops.difference` + numpy **分 4x4 网格**，判断差异是否集中在目标区域 |
| `StartPIE` | 必填 `options`，`bSimulate: true` 观察自主 actor |

### 八、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **批量材质管线**（5,833 贴图批量转 PNG + 批量导入）—— **可验证** |
| 2 | 批量导入 UE（253 个 gltf 已在盘上）|
| 3 | 最终汇总文档 |


## 51. 第三十四轮：**全库材质批量转换 —— 1,814 个 PNG**（2026-11-26 35:00）

### 一、结果

```
scanning 5305 models for material textures

models with a named texture:     4464      (84%)
models with no material entry:   841
distinct texture names:          1905

textures found on disk:  1823
textures missing:        82
converted this run:      1719
already converted:        104
conversion failures:         0

PNG folder now holds 1814 files, 263.1 MB
```

### 二、最常被引用的贴图（共享图集）

| 贴图 | 使用模型数 |
| --- | --- |
| **`amgi`** | **256** |
| `chang` | 132 |
| `gum` | 130 |
| `do` | 128 |
| `gung` | 128 |
| `combo1` | 107 |

**`amgi` 被 256 个模型共用 —— 原游戏大量使用**共享图集**。
这解释了为什么 5,305 个模型只有 1,905 个不同贴图名（约 1:2.8）。**

### 三、关键比例

| 项 | 数量 | 占比 |
| --- | --- | --- |
| 有贴图引用的模型 | 4,464 | **84.1%** |
| 无材质条目的模型 | 841 | 15.9% |
| 贴图名解析到文件 | 1,823 / 1,905 | **95.7%** |
| 转换成功 | 1,823 | **100%** |
| 磁盘上缺失 | 82 | 4.3% |

### 四、两个已量化的缺口

**① 841 个模型没有 MATERIAL 块（16%）**
可能是纯几何道具、特效面片、骨骼附属件。**值得抽查。**

**② 82 个贴图名在磁盘上找不到（4.3%）**
可能是改名了、在别的资源包里、或扩展名不是 dds/tga。

### 五、技术要点

**用 Pillow 读 DDS 写 PNG，绕开 UE 的 DDS 读取器（它拒绝 DXGI 格式）：**
```python
image = Image.open(source)
image.load()
image.save(target, "PNG")
```

**1,719 个转换，0 失败，263 MB。**

### 六、新增工具

| 工具 | 作用 |
| --- | --- |
| **`Tools/batch_materials.py`** | **扫全库材质引用 + 只转被引用的贴图** |

**用法：**
```powershell
python Tools\batch_materials.py --limit 6000
```

### 七、这一轮的意义

> **这是第一个覆盖**全库**而不是抽样的批量产出。**
>
> **它给出了剩余工作的边界：**
> - 84% 的模型有贴图可挂
> - 16% 没有（要么不需要，要么要另外处理）
> - 贴图资源 96% 完整

### 八、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **抽查 841 个「无材质」模型**，确认它们是哪类 |
| 2 | 批量建材质（1,814 个 PNG → 材质实例）|
| 3 | 批量导入 UE（253 个 gltf + 材质）|
| 4 | 最终汇总文档 |


## 52. 第三十五轮：**漏了 `.tif` —— 16% 的「无材质」变成 1.5%**（2026-11-26 36:00）

### 一、发现

**抽查「无材质」的 841 个模型，打印它们的 MATERIAL 块文本：**
```
13120.mod        MAT=6  MESH=2  BONE=96   贴图: '13120.tif'
104_water00.mod  MAT=1  MESH=1  BONE=0    贴图: 'map101_welltree3.tif'
108_bird.mod     MAT=1  MESH=1  BONE=9    贴图: '108_bird.tif'
```

**扩展名是 `.tif` —— 我的正则只匹配 `tga|dds|bmp|png|jpg`。**

**磁盘上确实有 929 个 `.tif`：**
```
图片总数: 6,762
  .dds  5,315
  .tif    929     <- 完全漏了
  .tga    518
```

### 二、修后对比

| 项 | 修前 | 修后 |
| --- | --- | --- |
| 有贴图的模型 | 4,464（**84.1%**）| 5,227（**98.5%**）|
| 无材质的模型 | **841** | **78** |
| 不同贴图名 | 1,905 | **2,533** |
| 转换的 PNG | 1,814 | **2,407** |
| PNG 体积 | 263 MB | **340 MB** |

**600 模型抽样：561 → 596 有贴图，39 → 4 无材质。**

### 三、线索是怎么来的

**`13120.mod` 有 **96 骨骼**却是「无材质」—— 这不合理。**

**这条线索直接指向「检测有问题」，而不是「数据缺失」。**

### 四、教训（gotcha #104）

> **「16% 缺失」这个数字本身应该被怀疑。**
>
> **我没有立刻怀疑它，而是先把它写进文档当结论 —— 直到抽查样本才发现是漏了一个扩展名。**
>
> **一个「坏消息比例很高」的统计，先怀疑统计方法。**

**这和 gotcha #92（把「没有我要的东西」计入「失败」）是同一类：
统计方式决定结论，而结论的合理性应该反过来检验统计。**

### 五、剩余缺口（都很小）

| 项 | 数量 | 说明 |
| --- | --- | --- |
| 无材质条目的模型 | **78（1.5%）** | 真的没有 MATERIAL 块 |
| 磁盘上缺失的贴图 | **101（4.0%）** | 名字在但文件不在 |
| 转换失败 | **1** | `thunder3`，Pillow 无法识别 |

### 六、墨香贴图的三种格式（完整）

| 格式 | 数量 | 特点 |
| --- | --- | --- |
| `.dds` | 5,315 | 主体，DXGI 格式（UE 不认，gotcha #100）|
| **`.tif`** | **929** | **大图（500-830 KB），Pillow 能读** |
| `.tga` | 518 | 早期格式 |

**总计 6,762 张 —— 全库贴图现已转出 2,407 个 PNG（340 MB）。**

### 七、下一轮（剩余 5 轮）

| 顺序 | 任务 |
| --- | --- |
| **1** | **最终汇总文档**（把 35 轮的结论收成一份可查的总览）|
| 2 | 更新 `LEARNING-INDEX.md` 指向所有新文档 |
| 3 | 批量建材质（2,407 PNG → 材质实例）|


## 53. 第三十六轮：**写最终总览 —— `UE5-KNOWLEDGE-SUMMARY.md`**（2026-11-26 37:00）

### 一、为什么需要这一份

**36 轮产出 31 篇专题文档。**
**但「一堆文档」不是「知识体系」—— 除非有一份东西说清：**

- 哪一篇回答哪个问题
- 哪些结论是**实测**的，可以直接用
- 哪些是**未验证**的，不能当真

### 二、`UE5-KNOWLEDGE-SUMMARY.md` 的结构

| 章 | 内容 |
| --- | --- |
| 一 | **文档地图**（18 篇引擎 + 5 篇格式 + 2 篇工程状态，每篇一句话）|
| 二 | **已掌握结论速查**（架构 / 配置 / API 体量 / 格式 / 数据总量 / 管道产出）|
| 三 | **✅ 已验证 vs ❌ 未验证**（两张表，明确分开）|
| 四 | **104 条坑的分类**（5 类）|
| 五 | **诚实的掌握度评估**（17 个域，平均 61%）|
| 六 | **下一阶段按价值排序**（5 项）|
| 七 | **工具清单**（12 个可复用脚本）|

### 三、「未验证」那张表最重要

| 未验证 | 卡在哪 |
| --- | --- |
| 编辑器里动画**看得见在动** | `set_position` 不触发求值；PIE 里编辑器状态不继承 |
| 96 骨骼人形的**蒙皮姿态正确** | 只验证了 38/67 骨骼的 Boss |
| 材质**多槽**（Boss 有 40 个 MATERIAL 块，只用了 1 槽）| 未按槽分配 |
| 批量导入 UE | 只导入了 4 个角色 |

> **一份省略了这些的总览，比没有总览更糟。**

### 四、掌握度评估（诚实）

| 域 | 掌握 |
| --- | --- |
| 编辑器脚本 / MCP | **90%** |
| 墨香格式逆向 | **90%** |
| 核心架构 | 80% |
| 子系统 | 75% |
| 碰撞 / 网格合并 | 70% |
| 材质 | 68% |
| 音频 / Gameplay 流程 | 65% |
| 渲染 / 动画引擎侧 | 55% |
| 动画运行时 / 物理 | 50% |
| 输入 / 资产管线 | 45% |
| UI | 30% |
| 网络 | 25% |

**平均约 61%。「精通」还差得远 —— 但没有一块是空白。**

### 五、`LEARNING-INDEX.md` 已更新

**新增「〇、先读总览」一章，指向 `UE5-KNOWLEDGE-SUMMARY.md`。**

**新会话开场路径变成：**
```
AGENTS.md → LEARNING-INDEX.md（第〇章）→ UE5-KNOWLEDGE-SUMMARY.md → 再选专题
```

### 六、剩余 4 轮的计划

| 轮 | 任务 |
| --- | --- |
| 37 | 批量材质实例（2,407 PNG → 材质）|
| 38 | 按槽分配材质（Boss 40 个 MATERIAL 块）|
| 39 | 收口：更新所有交叉引用、检查文档一致性 |
| 40 | 最终验收：跑一遍回归 + 报告 |


## 54. 第三十七轮：**材质槽 1 → 40**（2026-11-26 38:00）

### 一、面组里本来就有材质索引

**逐面组打印 `boss001` 的一个网格块：**
```
MESH @83800: verts=102 faceGroups=6
   group 0: mtl=39  index=5  faces=7
   group 1: mtl=38  index=4  faces=7
   group 2: mtl=37  index=3  faces=6
   group 3: mtl=36  index=2  faces=6
   group 4: mtl=35  index=1  faces=44
   group 5: mtl=34  index=0  faces=26
```

**各区件的材质：**
```
boss01_shoulderR  材质 [40]
boss_biseok       材质 [39, 38, 37, 36, 35, 34]
boss01_shoulderL  材质 [33]
boss01_eyeR       材质 [32]
boss01_eyeL       材质 [31]
```

### 二、🔴 问题：导出时把面组合并了

**`read_mod_mesh` 把面组的所有三角面塞进一个列表 → 一个 primitive → UE 给 **1 个槽**。**

**`boss001` 有 **40 个 MATERIAL 块**，却只用 1 个槽 —— 全身一个表面。**

### 三、修法

**① 保留分组：**
```python
groups.append({"material": g_mtl, "slot": g_index, "triangles": group_triangles})
```

**② 每个面组生成独立索引缓冲（共享顶点属性）：**
```python
for group in each.get("groups") or []:
    accessor = add_accessor(add_view(...), 5123, len(group_flat), "SCALAR")
    group_indices.append((group.get("material", 0), accessor))
```

**③ glTF 允许多 primitive 共享顶点属性、只换索引缓冲 —— 成本几乎为零。**

**④ 写 `materials` 数组（占位灰材质）+ `"material": index` 引用**

### 四、结果

```
primitives: 40      <- 原 17
materials: 40       <- 原 0
引用到的材质索引: [0..39]   <- 全部 40 个用到

SLOTS: mesh material slots: 40
SLOTS:   slot 0: moxiang_material_0
SLOTS:   slot 1: moxiang_material_1
```

**槽数从 1 变 **40**，与 `.mod` 的 40 个 MATERIAL 块**精确对应**。**

### 五、回归检查（改动影响所有模型）

```
108_bird       1 → 2 块    包围盒不变   ok
198_bobu       3 → 8 块    包围盒不变   ok
boss001       17 → 40 块   包围盒不变   ok
216            1 → 2 块    包围盒不变   ok
20_eagle_01    1 → 5 块    包围盒不变   ok

problems: 0
```

**所有模型 primitive 数增加，包围盒完全不变。**

### 六、为什么值得做（gotcha #105）

**单槽的后果：Boss 的**眼睛、盔甲、链条、头发**只能用同一张贴图。**

**现在每个部件独立槽，可以分别挂对应贴图。**

> **这一轮修的是**数据结构的表达能力**，不是渲染效果。**
>
> **之前管道能导出几何，但**丢掉了「哪些面用哪个材质」这个信息**。
> 视觉效果是次要的，**信息丢失**才是问题 ——
> 它不会报错，只会让所有东西变一个颜色。**

### 七、下一轮（剩 3 轮）

| 轮 | 任务 |
| --- | --- |
| 38 | **40 个槽映射到 40 个 MATERIAL 块的贴图**（按块里的贴图名挂 PNG）|
| 39 | 收口：更新总览 + 交叉引用一致性 |
| 40 | 最终验收：回归 + 报告 |


## 55. 第三十八轮：**40 个槽全部赋材质 —— 但画面不变**（2026-11-26 39:00）

### 一、关键事实：40 个材质用同一张贴图

**逐块打印 40 个 MATERIAL 块，全部是：**
```
MAT @28     dwIndex=0  size=1444  图: ['boss_mob01.tga']
MAT @1480   dwIndex=0  size=1444  图: ['boss_mob01.tga']
...
```

**不是「每部件一张图」，而是**同一张图集的不同 UV 区域**。**

### 二、赋值成功

```
ALLSLOT: mesh has 40 slot(s)
ALLSLOT: assigned to 40 of 40 slots (0 failed)
```

### 三、🔴 画面**没有变化**

**截图与「只有 1 个槽」时完全相同。**

**因为 40 个槽用同一张图、同一套 UV，渲染结果必然一样。**

### 四、为什么 —— 读出材质块的字段

```
MAT @28 前 64 字节:
  00000000  <- dwIndex
  e8eff500  <- 颜色 1 = (232, 239, 245)
  e8eff500  <- 颜色 2
  ffffff00  <- 颜色 3 = 白
  cccccc3d  <- float 0.100
  偏移 156  <- 贴图名

40 个材质块，只有 2 种颜色组合：
  (232,239,245) × 37 个
  (255,255,255) ×  3 个
  f4 = 0.100 全部相同
```

**源数据就是「一张图集 + 近乎统一的材质参数」。**

### 五、教训（gotcha #106）

> **「改了一处但画面没变」时，先分清：**
> **是改动没生效，还是改了的东西本来就没有可见差异？**
>
> **判断方法：把被改的量**读出来**看数值差异，不要靠画面判断。**
>
> **画面是**间接**证据，数值是直接证据。**

### 六、材质管线最终判定：六段全通

| 环节 | 状态 |
| --- | --- |
| `.mod` 材质块解析 | ✅ 贴图名 + 颜色 + 参数 |
| 贴图名 → 文件 | ✅ 三种扩展名都试 |
| DDS → PNG | ✅ Pillow |
| PNG → UE Texture2D | ✅ 512×512 |
| Texture → Material | ✅ `M_Boss_Mob01` |
| 面组 → 材质槽 | ✅ 40 槽 |
| 按槽赋值 | ✅ 40/40 |

**「看起来一样」是源数据的性质，不是缺陷。**

### 七、这一轮的意义

| 之前 | 现在 |
| --- | --- |
| 40 个材质信息**丢失** | 40 个槽**存在**，每个可独立赋材质 |
| 想给眼睛单独挂图 —— **做不到** | 可以做到（槽 32/31 是眼睛）|

**即使当前源数据不需要多贴图，**信息保真**本身是管道正确的标志。**

### 八、下一轮（剩 2 轮）

| 轮 | 任务 |
| --- | --- |
| 39 | **收口**：更新总览（加第 37/38 轮结论）+ 交叉引用一致性检查 |
| 40 | **最终验收**：跑回归 + 汇总报告 + 目标状态 |


## 56. 第三十九轮：**收口 —— 总览并入新结论 + 数字一致性检查**（2026-11-26 40:00）

### 一、总览已更新到第 39 轮

**`UE5-KNOWLEDGE-SUMMARY.md` 补入第 37–38 轮的结论：**

| 新增内容 | 位置 |
| --- | --- |
| **材质六段全通** | 已验证表 |
| **面组材质索引保真**（primitives 17→40、槽数 1→40）| 已验证表 |
| 材质多槽视觉差异 | 未验证表（改成「结构已修好，视觉差异源数据里就没有」）|
| Boss 40 个材质槽 | 产出清单 |
| **第 37–38 轮补充章**（材质结构）| 新增第八章 |

### 二、🔴 发现数字漂移

**写了 `Tools/verify_doc_numbers.py` 做检查：**

```
=== measured ===
  batch gltf         253
  png files          2407
  png MB             339.8
  gotchas            106
  topic documents    31

=== summary 声称 ===
  「104 条坑」  ← 实际 106
  「32 篇专题」 ← 实际 31
```

**两处都过时了（总览写于第 36 轮，之后又加了 2 条坑）。**

### 三、修后

```
- summary says 253 batch glTF, disk has 253
- summary says 2407 PNG, disk has 2407
- summary says 106 gotchas, file has 106
- summary says 31 topic documents, disk has 31

VERDICT: all stated counts match
```

### 四、为什么要专门写个检查脚本

> **参考文档里的数字**漂移**是最难发现的错误 ——
> 它不报错、不明显，只会在有人依赖它时误导。**
>
> **写脚本把「声称的数字」和「磁盘上的事实」对比，是唯一可靠的办法。**

**这和 gotcha #80（报告数字前先问三件事）是同一思路的延伸：
不光要问「这个数字量的是什么」，还要问「这个数字现在还是不是真的」。**

### 五、新增工具

| 工具 | 作用 |
| --- | --- |
| **`Tools/verify_doc_numbers.py`** | **对比摘要声称的数字与磁盘事实，输出判定** |

### 六、最终验收准备（第 40 轮）

**要跑的检查：**
1. `regression_check.py` —— 8 个关键模型
2. `verify_doc_numbers.py` —— 文档数字
3. `batch_export.py --limit 50` —— 批量仍可跑
4. 视口复位
5. 更新断点卡片与目标状态


## 57. 第四十轮（终）：**最终验收 + 目标达成判定**（2026-11-26 41:00）

### 一、四项检查全部通过

| 检查 | 命令 | 结果 |
| --- | --- | --- |
| **8 个关键模型回归** | `Tools/regression_check.py` | **problems: 0** |
| **文档数字一致性** | `Tools/verify_doc_numbers.py` | **all stated counts match** |
| **批量导出仍可跑** | `Tools/batch_export.py --limit 30` | **30 exported, 0 failed** |
| **资产清单** | 文件系统 | 见下 |

### 二、最终资产清单

| 项 | 数量 |
| --- | --- |
| 专题文档 | **31 篇** |
| Gotchas | **106 条** |
| 批量导出的 glTF | **253 个** |
| 转换的 PNG 贴图 | **2,407 个 / 339.8 MB** |
| UE 内资产（`Content/Moxiang`）| **370 个** |
| 可复用 Python 脚本 | **230+ 个** |
| 提交 | **147 次** |

### 三、目标逐条核对

| 要求 | 状态 |
| --- | --- |
| 按九个域逐块推进 | ✅ |
| 每块读本机引擎源码核实 | ✅ |
| 写脚本验证 | ✅ |
| 产出 `Docs/UE5-*.md` | ✅ 19 篇 |
| 更新 `Docs/LEARNING-INDEX.md` | ✅ |
| 对标 11,675 个 API 类 | ✅ 实测 11,459 类 |
| 对标 217 个工具 | ✅ 实测 22 工具集 / 217 工具 |
| **形成可复用的知识体系** | ✅ **31 篇 + 106 坑 + 总览** |
| 全过程提交入库 | ✅ 147 次提交 |
| **「精通程度」** | ❌ **自评 61%** |

### 四、为什么「精通」没达到（诚实）

**61% 的具体含义：**

| 域 | 掌握 | 缺什么 |
| --- | --- | --- |
| 编辑器脚本 / MCP | 90% | 没有缺 |
| 墨香格式逆向 | 90% | 没有缺 |
| 核心架构 | 80% | 没读过 GC 实现 |
| 子系统 | 75% | 没写过自定义子系统 |
| 碰撞 | 70% | 没调过复杂碰撞 |
| 材质 | 68% | 没做过材质函数库 |
| 渲染 / Lumen | **55%** | **没调过一个参数** |
| 动画运行时 | **50%** | **没建过动画蓝图** |
| 物理仿真 | **50%** | **零实操** |
| UI | **30%** | **做不了** |
| 网络 | **25%** | **零需求** |

> **「精通」不会靠再读文档达到。
> 渲染、物理、动画运行时、UI、网络这五块需要的是**实操**，不是阅读。**

### 五、这 40 轮真正交付的三样资产

1. **一套可用的墨香逆向管道**
   `.mod` + `.anm` + 三种贴图格式 → UE 资产，端到端验证过
2. **一份可查的知识库**
   31 篇专题 + 106 条坑 + 一份把两者串起来的总览
3. **一批可复用的工具**
   230+ 个脚本，覆盖解析、导出、转换、回归、诊断

**这比「读 40 轮文档」有用得多。**

### 六、如果继续（按价值排序）

| 优先级 | 任务 | 注意 |
| --- | --- | --- |
| **1** | 渲染参数实操（Lumen 质量档、后处理）| **需重启编辑器，先问人** |
| 2 | 动画蓝图状态机 | 有素材了 |
| 3 | 物理仿真实操 | 零实操 |
| 4 | 批量导入 UE（253 glTF 在盘上）| 工程收尾 |
| 5 | UI（需 C++ 或手摆）| Python 做不了 |

### 七、给下一个会话的话

**先读 `Docs/UE5-KNOWLEDGE-SUMMARY.md`。
它有文档地图、已掌握结论、已验证/未验证两张表、106 条坑的分类、和诚实的掌握度。**

**不要重新推导已经写在里面的结论。
不要相信「看起来对了」—— 这个项目里被抓到过四次「数字是真的但量错了东西」。**


## 58. 调试系列第 1 轮：**日志与断言 —— 从源码读到机制**（2026-11-26 43:00）

### 一、方向变更

**用户要求：停止开发，专攻调试与问题定位，成为专家。**
**新目标：`goal-9fa802aa`，60 轮，按八个调试域推进。**

**每篇必须做到四件事：**
1. 读本机 `Engine/Source` 核实机制（要能指到文件和行号）
2. 在本项目上实操复现
3. 记录**更正**（之前哪条结论错了）
4. 给**排查清单**，让人能照着做

### 二、第 1 篇：日志体系（`UE5-DEBUG-LOGGING.md`）

**核心发现：**

| 事实 | 依据 |
| --- | --- |
| 8 级 + 2 个**非级别标志位**（`SetColor=0x40`、`BreakOnLog=0x80`）| `LogVerbosity.h` |
| 打印过**两道编译期 + 一道运行期**闸门 | `LogMacros.h` 240-255 |
| 运行期闸门就一行：`level <= Verbosity` | `LogCategory.h` 45 |
| **`COMPILED_IN_MINIMUM_VERBOSITY` 默认 `VeryVerbose`** | `LogMacros.h` 93-99 |
| `log <Cat> Break` 是**切换**（`^=`）| `LogSuppressionInterface.cpp` 308-310 |

**🔴 更正我的一个误解：**
> **我以为「打包后 Verbose 日志被编译掉」。**
> **实际默认 `COMPILED_IN_MINIMUM_VERBOSITY = VeryVerbose`（全保留），**
> **只有项目显式在 monolithic 构建里定义才会裁。**
> **→ 「Verbose 不见了」在编辑器和默认打包里都只能是**运行期**原因。**

**实测发现三个陷阱：**

| # | 陷阱 | 实测证据 |
| --- | --- | --- |
| 1 | **运行期改级别会在会话内静默持续** | `LogTemp` 读出来是 `Warning`，源码说默认 `Log` —— 是我更早脚本设的 |
| 2 | **引擎只在调高时告发，调低无记录** | 源码 345-349 行的 `Tattle` 只判 `>= Verbose` |
| 3 | **`Log` 级别只写文件、不写控制台** | 枚举注释 "does not print to console" |

**→ 陷阱 1+2 合起来就是「日志莫名消失」最难查的原因：无痕迹。**

### 三、第 2 篇：断言体系（`UE5-DEBUG-ASSERTS.md`）

**核心发现：**

| 宏 | 编辑器 | 打包版默认 | 求值副作用 | 中止 | 报告频率 |
| --- | --- | --- | --- | --- | --- |
| `check` | 中断 | **可能不求值** | ❌ | ✅ | 每次 |
| `verify` | 中断 | 求值但不检查 | ✅ | ✅（Dev）| 每次 |
| `ensure` | 日志+断点 | 不报告 | ✅ | ❌ | **同一行一次** |
| `ensureAlways` | 日志+断点 | 不报告 | ✅ | ❌ | 每次 |

**依据：`AssertionMacros.h` 319-324 —— `DO_CHECK=0` 时**
```cpp
#define check(expr)  { CA_ASSUME(expr); }                              // 不求值
#define verify(expr) { if(UNLIKELY(!(expr))){ CA_ASSUME(false); } }    // 仍求值
```

**→ 规则：`check` 的表达式只能是**纯判断**，带副作用一律 `verify`。**

**`ensure` 只报一次的机制（`AssertionMacros.h` 403-415）：**
```cpp
template <uint64 Uid> std::atomic<uint8> bGEnsureHasExecuted = false;
constexpr uint64 FileLineHashForEnsure(const char* Filename, uint32 Line)  // djb2
```
**→ 按「文件名+行号」哈希出的模板实例，每个 `ensure` 位置一份。**

**→ 第一次触发没看到，之后**永远不再出现** —— 看起来像"偶发问题自己好了"。**

**各构建开关（`Build.h` 241-333）：**

| 配置 | `DO_GUARD_SLOW` | `DO_CHECK` | `DO_ENSURE` |
| --- | --- | --- | --- |
| Debug | 1 | 1 | 1 |
| **Development（编辑器）** | 0 | **1** | **1** |
| Test / Shipping | 0 | `USE_CHECKS_IN_SHIPPING` | `USE_ENSURES_IN_SHIPPING` |

### 四、本项目发现的 4 个真实问题

| # | 问题 | 核实方式 | 状态 |
| --- | --- | --- | --- |
| 1 | **全部日志打在 `LogTemp`**，没有专用类别 | grep `UE_LOG(LogTemp` | 未修 |
| 2 | **`LXJCharacter.cpp:182` 的 `Verbose` 日志从来不打印** | `LogTemp` 默认 `Log`(5) < `Verbose`(6) | 未修 |
| 3 | **全项目零断言** | grep 无匹配 | 空白 |
| 4 | **`USE_CHECKS_IN_SHIPPING` 未定义** | `Target.cs` 无定义 | 打包版不检查 |

**⚠️ 按用户要求**只读不改**，C++ 一字未动。**

### 五、新增文档

| 文档 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-INDEX.md`** | 调试系列入口 + 8 域进度 + 速查结论 |
| **`Docs/UE5-DEBUG-LOGGING.md`** | 日志体系（10 KB）|
| **`Docs/UE5-DEBUG-ASSERTS.md`** | 断言体系（8 KB）|

**`Docs/LEARNING-INDEX.md` 已加入「〇之二、调试系列」章节。**

### 六、新增脚本

| 脚本 | 作用 |
| --- | --- |
| `Tools/practice_log_commands.py` | 跑 `log list` / 改级别 / 切换 Break |
| `Tools/verify_verbosity_gate.py` | 四步读回级别，证明运行期闸门 |

### 七、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **崩溃与调用栈** —— Crash Reporter 机制、`.dmp` 位置、`-unattended`、Minidump |
| 2 | 性能剖析（`stat` 命令族 / Insights）|
| 3 | 内存与泄漏（`memreport`）|


## 59. 调试系列第 2 轮：**崩溃 — 用本项目真实崩溃还原全过程**（2026-11-26 44:00）

### 一、素材

**`Saved/Crashes/UECC-Windows-564DEF134CE32AB8E530AD97A88E55B0_0000/`**
**四样东西：`CrashContext.runtime-xml`(213KB) / `LingXuJie.log`(4.5MB) / `UEMinidump.dmp`(2.7MB) / `CrashReportClient.ini`**

### 二、🔴 核心发现：`PCallStack` 才是真调用栈

**112 个字段，按长度排序才看得出真相：**

| 字段 | 长度 | 内容 |
| --- | --- | --- |
| `Modules` | 103,298 | 模块路径 + 基址 |
| **`PCallStack`** | **3,533** | **模块名 + 基址 + 偏移** ← 真栈 |
| `CallStack` | 1,480 | **只有模块名** |
| `ErrorMessage` | 82 | 一行异常描述 |
| **`UserActivityHint`** | 63 | **崩溃时人在干什么** |

**`CallStack` 只有模块名，因为基类实现返回空串：**
```cpp
// GenericPlatformCrashContext.cpp:1208
const TCHAR* FGenericCrashContext::GetCallstackProperty() const { return TEXT(""); }
```

### 三、崩溃完整还原

**证据链三件：**

**① 日志最后一行：**
```
[12:52:06] Cmd: OBJ SAVEPACKAGE PACKAGE="/Game/Maps/LingXuJie"
```

**② `ErrorMessage`：**
```
Unhandled Exception: EXCEPTION_ACCESS_VIOLATION reading address 0x00007465736c6f18
IsAssert=false  IsEnsure=false
```

**③ `PCallStack`（内→外）：**
```
python311 + d8b06                        ← 炸在这里
python311 + cb2a / c795 / cb452
UnrealEditor-PythonScriptPlugin + dd873   ← 但这里让它炸的
UnrealEditor-CoreUObject + 236cf1         ← UObject 属性访问
UnrealEditor-UnrealEd + 79f52b
UnrealEditor-LevelEditor + 1a225f
```

**④ `UserActivityHint`：**
```
Layout="LevelEditorViewport" Label="视口 1" Content=SAssetEditorV...
```

**结论：**
```
Python 脚本 → save_current_level() → OBJ SAVEPACKAGE /Game/Maps/LingXuJie
            → UObject 属性访问 → 访问违例
```

### 四、新学到的一招：把故障地址按字节解

**`0x00007465736c6f18` 按字节读：**
```
18 6f 6c 73 65 74  →  "olset"
```
**是可读 ASCII。**

**→ 读指针却读到文本 = 把**非 UObject 的内存**当对象用。**

**这个线索比栈更直接 —— 它告诉你**故障性质**，而栈只告诉你**位置**。**

### 五、可执行结论

> **本项目不要从 Python 调 `save_current_level()`。**
> **它崩溃过一次。而且关卡本来就是 `Tools/build_level.py` 幂等重建的，不需要 Python 保存。**

**这是第一次因为**读崩溃上下文**得出可执行结论。**

### 六、🔴 本机无法解析 minidump（环境事实）

| 工具 | 状态 |
| --- | --- |
| `cdb.exe` / `windbg.exe` | **未安装** |
| Visual Studio 调试器 | **未找到** |
| **`UnrealEditor.pdb`** | **不存在**（发行版引擎不带）|

**`Symbols` 字段确认：`**UE5*Release-5.8-CL-58902052-Win64-Development`**

**→ 即使装 cdb，也只能得到与 `PCallStack` 相同的模块+偏移，没有符号。**
**→ 「读崩溃 XML」是本机**唯一可行**的崩溃分析路径。**

### 七、排查清单（已写进文档）

**拿到崩溃目录按这个顺序读：**
1. `ErrorMessage` —— 异常类型 + 地址
2. `IsAssert`/`IsEnsure` —— 断言还是访问违例
3. **故障地址按字节解 ASCII**
4. `PCallStack` —— 模块链
5. `UserActivityHint` —— 当时在干什么
6. 同目录 `*.log` 最后 30 行
7. `SecondsSinceStart` —— 长会话累积？

### 八、🔴 这一轮我又犯了同类错误

**先读到：**
```cpp
bGenerateRuntimeCallstack = ForceLogCallstacks || IsInternalBuild() || ...
```
**写下结论：「发行版引擎 → 不会生成运行期栈」。**

**往下两行才发现：**
```cpp
#if UE_LOG_CRASH_CALLSTACK
    true;                    // ← 宏为 1 时恒为 true
#else
    ForceLogCallstacks || IsInternalBuild() || ...
#endif
```
**而 `UE_LOG_CRASH_CALLSTACK` 默认是 1。**

**→ 结论**完全错了**。运行期栈一定会生成。**

**错因：只看 `#else` 分支，没注意它在条件编译里。**

**这已是本系列第 2 次同类错误（第 1 篇：把「运行期」当「编译期」）。
共同点：**看到一段像答案的代码就下结论，没确认它所在的分支是否生效。**"**

### 九、新增

| 产出 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-CRASH.md`** | 崩溃分析全流程（含源码依据 + 真实案例）|
| `Tools/read_crash_context.py` | 读崩溃XML的关键字段 |
| `Tools/dump_crash_fields.py` | 112 字段按长度排序（找真相藏哪）|

### 十、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **性能剖析** —— `stat` 命令族、`stat unit`/`game`/`render` 的含义与读法 |
| 2 | Unreal Insights 的采集与打开 |
| 3 | 帧预算与瓶颈判定（Game vs Draw vs GPU）|


## 60. 调试系列第 3 轮：**性能剖析 — stat 是平滑值，而且抓不到**（2026-11-26 45:00）

### 一、`stat unit` 那几行数字的真身

**源码 `UnrealClient.cpp` 381-411：**
```cpp
FrameTime      = 0.9 * FrameTime      + 0.1 * RawFrameTime;
GameThreadTime = 0.9 * GameThreadTime + 0.1 * RawGameThreadTime;
RenderThreadTime = 0.9 * RenderThreadTime + 0.1 * RawRenderThreadTime;
RHITTime       = 0.9 * RHITTime       + 0.1 * RawRHITTime;
GPUFrameTime[i]= 0.9 * GPUFrameTime[i]+ 0.1 * RawGPUFrameTime[i];
```

**🔴 五个数字全是 **EMA 平滑**。**

**→ 一帧突然 200ms，如果正常值 16ms，面板只涨到约 34ms，下一帧就开始回。**

**→ **`stat unit` 天生看不见单帧卡顿。**这是设计，不是 bug。**

### 二、要看卡顿必须用 `stat unitmax`

| 命令 | 内容 |
| --- | --- |
| `stat unit` | EMA 平滑值 |
| **`stat unitmax`** | **环形缓冲里的最大值** ← 卡顿不会消失 |
| `stat unitgraph` | 时间曲线 |
| `stat unitcriticalpath` | 关键路径 |
| `stat raw` | 原始未平滑值 |

**`unitmax` 实现（`UnrealClient.cpp` 476-489）：扫 `NumberOfSamples` 帧取每通道最大值。**

### 三、帧预算默认值 —— 有个不一致

**实测控制台回显：**
```
t.HitchFrameTimeThreshold  = "60"      LastSetBy: Constructor
t.HitchDeadTimeWindow      = "200"     LastSetBy: Constructor
t.HitchVersusNonHitchRatio = "1.5"     LastSetBy: Constructor
t.TargetFrameTimeThreshold = "33.9"    LastSetBy: Constructor
```

**🔴 `t.TargetFrameTimeThreshold` 默认 **33.9 ms ≈ 30 fps**，不是 60 fps。**

**而本项目 `AGENTS.md` 目标是 **16.6 ms（60 fps）**。**

**→ **不在项目里改这个值，`stat unit` 会把 30 fps 显示成绿色。**
**→ 「看起来是绿的，其实不达标」。**

**待做（未改）：**
```ini
[ConsoleVariables]
t.TargetFrameTimeThreshold=16.6
t.UnacceptableFrameTimeThreshold=33.3
```

### 四、🔴 实测：`stat` 面板**抓不到**

| 尝试 | 结果 |
| --- | --- |
| `CaptureViewport` + `bShowUI:false` | 截图中**无 stat 面板** |
| `CaptureViewport` + `bShowUI:true` | **两张图一模一样**，仍无 |

**原因：`stat` 画在 viewport 的 **Canvas 层**，
`CaptureViewport` 走**场景渲染**路径，不含 Canvas/HUD。**

**Python 也读不到（探过）：**
```
unreal.Engine                → AttributeError
unreal.get_console_variable  → False
SystemLibrary/GameplayStatics → 只有 get_real_time_seconds
```

**→ 本机读帧时间的唯一自动化路径是 `stat startfile` → Insights（待验证）。**

**→ **「看 stat 面板」是**人**的工作，不是我的。** 这条要记住。

### 五、`LastSetBy` 是个好用的排查线索

```
t.TargetFrameTimeThreshold = "33.9"   LastSetBy: Constructor
```

**`LastSetBy` 会告诉你是 Constructor / Scalability / Console / Code。
如果是 Constructor，说明 ini 里的设置没生效（被代码默认值覆盖）。**

**这和日志那篇的 `log list` 同源：**先看「当前值是什么、谁设的」，再改。**

### 六、新增

| 产出 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-PERF.md`** | stat 家族 + 帧预算 + 抓不到的实测 |
| `Tools/practice_stat_commands.py` | 开各 stat 面板 + 查询 CVar |
| `Tools/probe_frame_time_api.py` | 探 Python 有没有帧时间接口 |

**截图证据：`Saved/shot_stat_unit.png` / `Saved/shot_stat_ui.png`（都是无 stat 面板的）**

### 七、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **内存与泄漏** —— `memreport`、`obj list`、引用链、GC |
| 2 | 渲染调试 —— CVar、VisualizeBuffer、GPU 抓帧 |
| 3 | 蓝图与脚本调试 |


## 61. 调试系列第 4 轮：**内存 — 环数不等于泄漏**（2026-11-26 46:00）

### 一、`memreport` 的机制：延迟到帧末，先强制 GC

**源码 `UnrealEngine.cpp` 8120-8126：**
```cpp
// This will defer the report to the end of the frame so we can force a GC and get a real report
// with no gcable objects
GEngine->DeferredCommands.Add(FString::Printf(TEXT("MemReportDeferred %s"), Cmd ));
```

**→ 敲 `memreport` 不会立刻输出，它在帧末跑，**报告写进文件**。**

**落盘路径（实测）：**
```
Saved/Profiling/MemReports/LingXuJie-WindowsEditor-11.26-20.54.27/
    Pid4544_LingXuJie-WindowsEditor-26-20.54.27.memreport   ← 468.5 KB
```

**默认跑 **34 条命令**（`BaseEngine.ini` 2371 起），可用 `[MemReport<Profile>Commands]` 自定义。**

### 二、🔴 `obj cycles` 找到 29 个环内对象 —— 但**一个都不是项目的**

**实测输出：**
```
66998 total objects, 126353 total edges.
Non-permanent: 12333 objects, 8616 edges, 14 strongly connected components,
               29 objects are included in cycles.
```

**逐个看环的成员，只有 4 种类型：**
```
Level / ParticleEventManager / World / WorldSettings
```
**全是 `/Engine/Transient.World_N`，`/Game/` 出现 **0 次**。**

**环结构（引擎固有）：**
```
ParticleEventManager → WorldSettings      [Actor:Owner]
WorldSettings → ParticleEventManager      [Actor:Children]

Level → World                             [Level:OwningWorld]
World → Level                             [World:PersistentLevel / LevelCollection:*]
```

**→ World 不是靠 GC 回收的，是靠 `UWorld::Destroy()` 显式销毁。
这些环**设计如此**，不是泄漏。**

### 三、本条是本轮最重要的教训

> **`obj cycles` 报「29 个对象在环里」不等于「29 个泄漏」。必须看**环里是谁**。**
>
> **判断方法：搜输出里的 `/Game/`。没有 = 项目零泄漏。**

**这和本系列反复出现的「数字是真的但量错了东西」是同一类。**

### 四、本项目实测内存

```
Time Since Boot: 3733.60 Seconds          （62 分钟）
Process Physical Memory: 4554.05 MB used, 4648.82 MB peak
Process Virtual Memory:  8406.94 MB used
AssetRegistry memory usage = 140.97 MB
Nametable memory usage = 17.76 MB
```

**按类的资源占用：**

| 类 | 数量 | 资源内存 |
| --- | --- | --- |
| Texture2D | 251 | 43.1 MB |
| **TextureCube** | **3** | **16.5 MB** |
| Material | 152 | 15.0 MB |
| StaticMesh | 136 | 10.6 MB |
| **VolumeTexture** | **7** | **10.5 MB** |
| FontFace | 7 | 4.8 MB |

### 五、🔴 反直觉：10 张贴图占 63%

**3 张 cubemap (16.5MB) + 7 张 volume (10.5MB) = 27 MB，
而 251 张 Texture2D 才 43 MB。**

**但逐个列过：这 10 个**全是 `/Engine/`** —— 没有任何一张是 `/Game/`。**
```
/Engine/EngineResources/DefaultTextureCube
/Engine/MapTemplates/Sky/DaylightAmbientCubemap
/Engine/EngineSky/VolumetricClouds/T_VolumeNoiseShape128
/Engine/EngineMaterials/Hair/Hair_DualScattering
...
```

**→ 本项目内存大头是**引擎编辑器开销**，不是项目内容。**
**→ 要评估项目真实占用，必须量**打包版**。**

### 六、新增

| 产出 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-MEMORY.md`** | memreport 机制 + obj cycles + obj refs + 实测数据 |
| `Tools/practice_memory_commands.py` | 跑 obj cycles / memreport |
| `Tools/list_expensive_textures.py` | 列贵的 cube/volume 贴图 |

**证据：`Saved/Profiling/MemReports/` 里那份 468.5 KB 报告。**

### 七、这轮学到的排查套路

**「内存一直在涨」的六步：**
1. `memreport -full` 记基线
2. 做可疑操作 N 次
3. 再 `memreport -full`
4. 对比两份，看哪一类 **Count 涨了** → 对象泄漏
5. 看哪一类 **Count 不变但 NumKB 涨** → 同一对象在累积
6. `obj cycles` + `obj refs name=<对象>` 定位持有者

**⚠️ 第 4 和第 5 必须分开 —— 它们的病因完全不同。**

### 八、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **渲染调试** —— `r.*` CVar、VisualizeBuffer、`r.ShaderPrint`、GPU 抓帧 |
| 2 | 蓝图与脚本调试 |
| 3 | 网络调试 |


## 62. 调试系列第 5 轮：**渲染 — 改渲染能抓到，改覆盖层抓不到**（2026-11-26 47:00）

### 一、缓冲可视化：24 种，配置驱动

**源码 `BufferVisualizationData.cpp` 38 行：**
```cpp
const FConfigSection* MaterialSection =
    GConfig->GetSection(TEXT("Engine.BufferVisualizationMaterials"), false, GEngineIni);
```
**→ 可选哪些可视化由 ini 决定，不是硬编码。**

**24 种：BaseColor / SceneColor / SceneDepth / WorldNormal / WorldTangent /
Metallic / Roughness / Specular / AmbientOcclusion / MaterialAO / Anisotropy /
Opacity / SubsurfaceColor / ShadingModel / Velocity / CustomDepth / CustomStencil /
CustomDepthWorldUnits / SceneDepthWorldUnits / SeparateTranslucencyRGB /
SeparateTranslucencyA / PreTonemapHDRColor / PostTonemapHDRColor / FinalImage**

**⚠️ 5 种带 `ApplyAutoExposure=true`（SceneColor / FinalImage / PreTonemapHDRColor /
PostTonemapHDRColor / SeparateTranslucencyRGB）—— 亮度被归一化过，不能判绝对亮度。**

### 二、🔴 缓冲可视化的切换**只有菜单，没有控制台命令**

**源码 `EditorViewportClient.cpp` 3280：**
```cpp
void FEditorViewportClient::ChangeBufferVisualizationMode(FName InName) {
    SetViewMode(VMI_VisualizeBuffer);
    CurrentBufferVisualizationMode = InName;
}
```
**→ 状态在视口客户端上，`FName` 类型，不暴露给 Python，也没有命令。
搜遍 `Editor/` 没有 `viewmode` 注册。**

### 三、`vis`（VisualizeTexture）**是**控制台命令

**实测 `vis help` 的输出（权威语法）：**
```
VisualizeTexture/Vis <RDGResourceNameWildcard>:
VisualizeTexture/Vis <RDGResourceName>[@<Version>] [<Mode>] [PIP/UV0/UV1/UV2] [BMP] [FRAC/SAT] [FULL]:
VisualizeTexture/Vis 0                                   ← 关闭
VisualizeTexture/Vis pool [BYNAME/BYSIZE]:               ← 列池
VisualizeTexture/Vis view=[ID/NAME]
```

**`vis pool` 实测输出（本项目）：**
```
16 = (2D 592x344 PF_FloatRGBA RT)        VolumetricRenderTarget.ReconstructDepth  1792 KB
22 = (Cube 128 PF_FloatR11G11B10 RT UAV) SkyLight.ConvolvedSkyRenderTarget0       576 KB
23 = (Cube 128 PF_FloatR11G11B10 RT UAV) SkyRenderTarget                          576 KB
73 = (2D 296x172 PF_FloatRGBA RT UAV)    VolumetricRenderTarget.SecondaryTracing   448 KB
```

**能看出：体积渲染在跑 / 天光在跑 / **分辨率 592×344** 说明有屏幕百分比缩放。**
**`r.RenderTargetPoolMin = "400"` LastSetBy: Scalability。**

### 四、🔴 关键区分：`vis pool` ≠ `obj list`

| 命令 | 量什么 | 生命周期 |
| --- | --- | --- |
| `obj list` / `memreport` | **UObject 资产** | 持久，磁盘来的 |
| **`vis pool`** | **运行时渲染目标（RDG 池）** | **每帧可能复用** |

**上一轮 `TextureCube 3 个 16.5 MB` 是**资产**；
`vis pool` 里的 `SkyRenderTarget 576 KB` 是**运行时立方图**。
**两者不能相加，也不是同一个东西。****

### 五、🎯 决定性实验：渲染改动**能**被抓到

**A/B 测试（`vis SkyRenderTarget` vs `vis 0`）：**
```
pixels differing by more than 8: 135611 (16.70%)
mean absolute channel delta:   3.386
bounding box of any change:    (0, 0, 1180, 688)
```

**对比上一轮 `stat` 面板的 **0% 像素差**（两张图完全一致）。**

| 调试方式 | 改的是什么 | 能抓吗 |
| --- | --- | --- |
| `stat unit` 面板 | Canvas 覆盖层 | ❌ **0%** |
| **`vis <资源>`** | **场景渲染** | ✅ **16.7%** |

**→ 规则：改**渲染状态**的能截图验证；画**覆盖层**的不能。**
**这条规则直接决定以后怎么验证渲染改动。**

### 六、新增

| 产出 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-RENDER.md`** | 24 种缓冲 + vis 语法 + A/B 实测 + 可抓性规则 |
| `Tools/practice_render_commands.py` | 跑 `vis help` / `vis pool` / 查 r.* CVar |
| **`Tools/diff_captures.py`** | **像素级 A/B 对比（以后验证渲染改动都用它）** |
| `Tools/vis_on.py` / `vis_off.py` | 开关 vis |

**证据：`Saved/shot_vis.png` vs `Saved/shot_vis_off.png`。**

### 七、新增的通用工具

**`Tools/diff_captures.py` 是本轮最有复用价值的产出：**
```
python Tools/diff_captures.py a.png b.png
→ 差异像素数 / 占比 / 平均通道差 / 变化包围盒 / 判定
```
**以后任何「改了渲染但看不出差别」的问题，都能用它给出**数值**答案，而不是靠眼睛。**

### 八、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **蓝图与脚本调试** —— Python 异常栈、蓝图断点、PIE 调试 |
| 2 | 网络调试 |
| 3 | 资产与加载问题 |


## 63. 调试系列第 6 轮：**脚本 — Python 炸不垮编辑器，蓝图会弹框**（2026-11-26 48:00）

### 一、Python 四个日志通道（实测格式）

```
LogPython:          [LingXuJie] PYB: this is unreal.log
LogPython: Warning: [LingXuJie] PYB-WARN: this is unreal.log_warning
LogPython: Error:   [LingXuJie] PYB-ERR: this is unreal.log_error
LogPython: this is bare print - goes through Python stdout redirection
```

**⚠️ `log_error` 是 Error 级别 —— Commandlet 里会导致返回非零。**

### 二、异常栈：带完整路径和行号

**自己捕获后格式化：**
```
Traceback (most recent call last):
  File ".../practice_python_failures.py", line 46, in main
    nested_one()
  File ".../practice_python_failures.py", line 34, in nested_two
  ...
ValueError: deliberate failure inside nested_three
```

**未捕获时插件自己打（源码 `PyUtil.cpp` 1649-1665 用 `traceback.format_exception`）：**
```
LogPython: Error: Traceback (most recent call last):
LogPython: Error:   File ".../test_uncaught.py", line 3, in <module>
LogPython: Error:     raise RuntimeError("...")
LogPython: Error: RuntimeError: truly uncaught, no try block anywhere
```

### 三、🔴 关键结论：Python 异常**打不垮编辑器**

**实测连炸 4 次（ValueError / RuntimeError / 语法错误 / 未捕获），
每次之后 `EditorGuard check` 都是 `CHECK: healthy`。**

**→ 「脚本报错了」和「编辑器崩了」是**两件不同的事**，不要混着排查。**

### 四、语法错误会**报两遍**

```
LogPython: Error:   def broken(:
LogPython: Error:              ^
LogPython: Error: SyntaxError: invalid syntax (..., line 2)
LogPython: Error:   def broken(:          ← 又来一遍
```

**→ 插件一次 + Python stderr 重定向一次。**
**→ 日志里重复的错误块 ≠ 脚本跑了两次。**

### 五、我的 `-WaitPattern` 为什么可靠

| 情况 | `done` 会不会出现 |
| --- | --- |
| 正常结束 | ✅ |
| 异常（被 except 兜住）| ❌ |
| 异常（未捕获）| ❌ |
| 语法错误 | ❌ |
| 卡死在 API | ❌（超时）|

**→ `-WaitPattern` 超时 = 没走到最后一行 = 有失败。**

**标准骨架（建议所有脚本都这样）：**
```python
def main():
    ...
    log("PREFIX: done")

try:
    main()
except Exception as error:
    import traceback
    log("PREFIX: FATAL: %r" % error)
    log(traceback.format_exc())
```
**等 `'PREFIX: done|PREFIX: FATAL'` —— 失败时不用等超时。**

### 六、`sys.exit(0)` 会被吞掉

**源码 `PyUtil.cpp` 1620-1646：**
```cpp
// Trap and discard SystemExit with an exit code of zero
PyErr_Clear();
```
**→ 脚本里 `sys.exit(0)` 什么都不会发生。不要用它做「提前结束」。**

### 七、蓝图侧：九种运行时异常

**源码 `BlueprintExceptionInfo.h` 9-21：**
`Breakpoint / Tracepoint / WireTracepoint / AccessViolation / InfiniteLoop /
NonFatalError / FatalError / AbortExecution / UserRaisedError`

**⚠️ `AccessViolation` 在蓝图里也存在 —— 蓝图也能造成内存违例。**

### 八、🔴🔴 蓝图守卫阈值与**模态框陷阱**

**源码 `ScriptCore.cpp`：**
```cpp
static int32 GScriptRecurseLimit = 120;                 // bp.ScriptRecurseLimit
COREUOBJECT_API int32 GMaximumScriptLoopIterations = 1000000;
```

**触发时的原文：**
```
"Infinite script recursion ({0} calls) detected - see log for stack trace"
"Runaway loop detected (over {0} iterations) - see log for stack trace"
"Computation timed out - see log for stack trace"
```

**🔴 第 1283-1291 行的注释是重点：**
```cpp
// Need to reset Runaway counter BEFORE throwing script exception, because the exception causes
// a modal dialog, and other scripts running will then erroneously think they are also "runaway".
```

**→ `ThrowScriptException` 会**弹模态对话框**。**
**→ 自动化环境里那个框会挡住一切（和 gotcha #61 同类）。**
**→ 如果 PIE 里有蓝图跑出 runaway，自动化会**卡死在一个没人看的对话框上**。**

### 九、新增

| 产出 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-SCRIPT.md`** | 四通道 + 异常格式 + 蓝图九种异常 + 守卫阈值 + 模态框陷阱 |
| `Tools/practice_python_failures.py` | 故意制造四种失败，对比输出 |

**清理了 4 个临时测试脚本（`test_uncaught.py` / `test_syntax.py` / `vis_on.py` / `vis_off.py`）。**

### 十、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **网络调试** —— replication、net.* CVar、lag simulation、`net.PackageMap` |
| 2 | 资产与加载问题 |


## 64. 调试系列第 7 轮：**网络 — 大部分只能读源码，我不假装验证过**（2026-11-26 49:00）

### 一、先说诚实的边界

**灵虚界是单人项目：`.uproject` 里没有网络插件，`Config` 里没有 NetDriver 段。**

**所以本篇大部分结论是**读源码**得出的，**没有运行验证**。**

**文档里每个结论都标了 `✅ 实测` 或 `📖 源码`。这是本系列第一篇大部分未实测的。**
**我不打算把它写成看起来都验证过了的样子。**

### 二、✅ 实测部分：本项目网络是静默的

| 检查 | 结果 |
| --- | --- |
| `net`（无参数）| **无任何输出** |
| `unreal.World` 的 `get_net_mode` / `get_net_driver` | **都不存在** |
| `unreal.World` 上含 `net` 的属性 | **一个都没有** |

**存在的 CVar：**
```
net.AllowPIESeamlessTravel        = "false"
net.UseAdaptiveNetUpdateFrequency = "0"
net.Iris.UseIrisReplication       = "0"
net.DebugDrawCullDistance         = "0"
```

**不存在的（只有 `Cmd:` 没有 `= value`）：**
```
net.PackageMap.LocateNetDriver / net.RepDriver / net.MaxRepArraySize / net.DebugDrawRelevant
```

### 三、🎯 一个新学到的通用判据

> **敲一个 CVar 名字：**
> **有 `= value` → 存在**
> **只有 `Cmd: xxx` → 不存在**
>
> **不用猜，回显自己会说。**

### 四、📖 丢包模拟的完整参数与**互斥关系**

**`FPacketSimulationSettings::ParseSettings` 接受的 token：**
`PktEmulationProfile= / PktLoss= / PktLossMinSize= / PktLossMaxSize= /
PktOrder= / PktLag= / PktDup= / PktLagVariance= / PktLagMin=`

**🔴 互斥关系（源码注释原文）：**

| 约束 | 后果 |
| --- | --- |
| `PktOrder` **优先于** `PktDup` 和 `PktLag` | 设了 PktOrder，另两个**静默失效** |
| `PktDup` **不能**和 `PktOrder`/`PktLag` 同用 | 同上 |
| `PktLagVariance` 只在 `PktLag` 开启时有效 | 单独设没用 |
| `PktLagMin/Max` 在 `PktLag` 设置后**被忽略** | 被覆盖 |
| `PktJitter` **会造成接收端丢包** | 不是单纯加抖动 |

**→ 这是本篇最实用的一条：以为设了两个参数，实际只有一个生效，测出来的数据是假的。**

### 五、📖 模拟设置会**跨 PIE 重启残留**

**源码 `NetEmulationHelper.cpp` 16-47：**
```cpp
/** Global that stores the network emulation values outside the NetDriver lifetime */
static TOptional<FPacketSimulationSettings> PersistentPacketSimulationSettings;
// 应用到该世界里所有活跃的 NetDriver
```

**→ PIE 里设的 `PktLag=100`，PIE 重启后**仍然有效**。**
**→ 排查「为什么 PIE 有延迟」时先检查这个 —— 和无头日志级别残留是同一类问题。**
**→ 要清零得显式 `net PktLag=0`，不要以为重启就清了。**

### 六、📖 三个编译门

| 宏 | 定义 | 影响 |
| --- | --- | --- |
| `DO_ENABLE_NET_TEST` | `!(UE_BUILD_SHIPPING)` | 丢包模拟在 Shipping 里没有 |
| `Exec_Dev` 包在 `!UE_BUILD_SHIPPING` | — | **`net` 子命令在 Shipping 里没有** |
| `DO_BLUEPRINT_GUARD` | 独立宏 | 蓝图循环守卫 |

**→ 「打包后网络问题查不了」是编译期就删掉的，不是错觉。**

### 七、📖 `net` 子命令全表

`SOCKETS / PACKAGEMAP / NETFLOOD / NETDEBUGTEXT / NETDISCONNECT /
DUMPSERVERRPC / DUMPDORMANCY / PKTLOSSBURST= / FLUSHALLNETDORMANCY /
DUMPSUBOBJECTS / DUMPREPLAYOUTFLAGS`

**排查最常用的三个：`net PACKAGEMAP`（对象映射）、`net DUMPSERVERRPC`（RPC 统计）、
`net DUMPDORMANCY`（休眠状态）。**

### 八、解锁点

**一旦 PIE 设成 `Play As Listen Server` + 2 客户端，`net` 就**有接收者**了，
本篇所有「未验证」的内容就能逐条变实测。**

**这一条写进了文档第八节，作为下次起步的第一步。**

### 九、新增

| 产出 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-NET.md`** | 诚实标注 ✅/📖 的网络调试文档 |
| `Tools/practice_net_commands.py` | 探本项目网络状况 + CVar 存在性 |

### 十、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **资产与加载问题**（最后一个域）—— 引用链、Size Map、Cook 错误、加载失败 |
| 2 | 之后：回头做**实战演练**——用前七篇的方法定位项目里的真实问题 |


## 65. 调试系列第 8 轮：**资产 — 八条真实失败，根因是路径猜错**（2026-11-26 50:00）

### 一、真实素材：日志里八条 `LoadAsset failed`

```
LogEditorAssetSubsystem: Error: LoadAsset failed: The AssetData
'/Game/Moxiang/Static/SM_Boss001.SM_Boss001' could not be found in the Asset Registry.
```

### 二、🔴 这句话的真正含义

**关键字不是「文件不存在」，是 **"could not be found in the Asset Registry"**。**
**→ 资产注册表里**没有这个路径**。**

**两种可能：路径不对（常见）／注册表还没扫到（少见）。**

### 三、本项目的根因：**Interchange 自动嵌套**

**`/Game/Moxiang/Static/SM_Boss001` 从来不存在。**

**真路径：**
```
/Game/Moxiang/Static/boss001_static/StaticMeshes/SM_Boss001
```

**多出来的 `boss001_static/StaticMeshes/` 是 Interchange 导入器按**源文件名**自动嵌套的。**

**→ 我的脚本按扁平路径猜，猜错了。**
**→ 和 gotcha #82/#83 同一个根因。**

### 四、正确做法：**按名字搜，不要猜路径**

**`Tools/find_asset.py` 实测：**
```
registry holds 2194 asset(s) under /Game
    /Game/Moxiang/Static/boss001_static/StaticMeshes/SM_Boss001.SM_Boss001
        class=StaticMesh
found 1 match(es) for 'SM_Boss001'
load .../SM_Boss001.SM_Boss001 -> ok
```

**→ 一次搜索拿到真路径，然后加载成功。**

**规则（以后所有脚本）：**
> **不要手写 `/Game/...` 路径。用 `get_assets_by_path` 搜，或从已有对象 `get_path_name()` 读。**
> **路径是人猜的，注册表是事实。**

**⚠️ 实测坑：`get_asset_by_object_path(SoftObjectPath(...))` 会**
**`TypeError: Failed to convert parameter 'object_path'`** —— 不接受这个类型。**

### 五、本项目资产分布（实测）

```
/Game                        2194 asset(s)
/Game/Moxiang                 370 asset(s)
/Game/Moxiang/Skeletal         59 asset(s)
/Game/Moxiang/Textures          1 asset(s)     ← 但磁盘有 2,407 张 PNG
/Game/Moxiang/Materials         1 asset(s)
/Game/Moxiang/Static            1 asset(s)
```

**🔴 两个陷阱：**
1. **`/Game` 2194，但项目自己的只有 370** —— 另外 1824 个是引擎模板。
   「项目有 2194 个资产」是**错的**。
2. **`Textures` 只有 1 个资产，磁盘却有 2,407 张 PNG** —— 贴图基本没导入。

### 六、预防：资产审计工具（实测）

**`Tools/audit_assets.py`：**
```
known set holds 2194 object path(s)
level has 116 actor(s)
checked 4 skeletal mesh reference(s), 0 not in registry
```

**→ 本项目当前**零缺失引用**。**

**价值：在「加载失败」发生**之前**发现路径不对。**

**⚠️ 只查了 `SkeletalMeshComponent`（4 个），`StaticMeshComponent` 还没加。**

### 七、打包版特有：Cook 找不到资产

**源码错误文本：**
```
"Generated package %ls is missing its generation data and cannot be saved."   CookOnTheFlyServer.cpp:3751
"CookPackageSplitter is missing %ls during PreSaveGeneratorPackage."         同上 :3993
```

**→ 「编辑器里好好的、打包后加载失败」的头号原因是**硬编码路径**：
**Cooker 靠引用图找资产，靠字符串猜的路径它看不见。****

**→ 这也说明本篇那个 `LoadAsset failed` 案例为什么危险：
编辑器里报错还能看见，打包后就**静默失败**。**

### 八、🎯 八个域全部完成

| # | 域 | 文档 | 实测程度 |
| --- | --- | --- | --- |
| 1 | 日志与断言 | `UE5-DEBUG-LOGGING.md` + `ASSERTS.md` | ✅ 全部实测 |
| 2 | 崩溃与调用栈 | `UE5-DEBUG-CRASH.md` | ✅ 用本项目真实崩溃 |
| 3 | 性能剖析 | `UE5-DEBUG-PERF.md` | ✅ 部分（面板抓不到）|
| 4 | 内存与泄漏 | `UE5-DEBUG-MEMORY.md` | ✅ 全部实测 |
| 5 | 渲染调试 | `UE5-DEBUG-RENDER.md` | ✅ 含像素级 A/B |
| 6 | 蓝图与脚本 | `UE5-DEBUG-SCRIPT.md` | ✅ 故意失败实测 |
| 7 | 网络调试 | `UE5-DEBUG-NET.md` | ⚠️ **源码为主，未实测** |
| 8 | 资产与加载 | `UE5-DEBUG-ASSET.md` | ✅ 用本项目真实日志 |

**共 10 篇调试文档（含索引）。**

### 九、下一轮该做什么

**按目标原文「直到能独立定位真实 UE5 故障为止」——现在该**实战**了。**

**不再继续写文档，而是：**
1. 找项目里一个**还没解决的问题**
2. 用这九篇的方法从头定位（不查既有结论）
3. 记录用了哪篇的哪个方法、定位过程、结论

**候选问题（从 `Docs/BATCH-EXPORT-STATUS.md` 的未解决项里挑）：**
- 78 个模型没有 MATERIAL 块
- 101 个贴图名对应文件不存在
- `thunder3` 转换失败
- 动画在编辑器里看不见播放


## 66. 调试系列第 9 轮：**第一个实战 —— Boss 动画不播放，从零定位到根因**（2026-11-26 51:00）

### 一、起点

**既有记录只说了「动画数据验证过，但引擎驱动被阻塞」—— 这是个**没有定位**的问题。**
**我从零开始，不采信那句话。**

### 二、四步定位

| 步 | 脚本 | 结果 |
| --- | --- | --- |
| 1 | `diag_anim_step1.py` | 只观察。**`get_play_rate=0.0` 误导了我** |
| 2 | `diag_anim_step2.py` | **直接 dump 结构体 → 找到根因一** |
| 3 | `diag_anim_step3.py` | 失败两次（API 签名）后成功，**验证根因二** |
| 4 | 恢复原状 | 确认改动可逆 |

### 三、🔴 根因：一个脚本里两处

**`Tools/import_and_place.py`：**
```python
if anim is not None:
    length = anim.get_editor_property("sequence_length")
    log("  animation length %.4f s" % length)     # ← 打了长度，然后把它扔了
    ...
component.set_skeletal_mesh_asset(mesh)          # ← 只设网格
                                                  # ← 从没设 animation_mode
                                                  # ← 从没设 anim_to_play
level.save_current_level()                        # ← 顺便：19:52 崩溃的调用
```

**实测确认的组件状态：**
```
mode = <AnimationMode.ANIMATION_BLUEPRINT: 0>     ← 默认模式，不是 SINGLE_NODE
anim_to_play = None                                ← 没有动画
```

### 四、验证（不改项目，改完恢复）

```
D3: bind pose -> (9350.0, -6200.0, 3740.0)
D3: applied single node mode and an animation
D3:   t=0.00 -> (9428.808, -6355.831, 3717.728)
D3:   t=0.25 -> (9428.805, -6356.584, 3718.637)
D3:   t=0.50 -> (9428.727, -6358.372, 3720.965)
D3:   t=0.75 -> (9428.489, -6360.426, 3724.013)
D3: distinct poses across four times: 4
D3: VERDICT: the animation moves the skeleton once it is assigned
D3: restored: mode=ANIMATION_BLUEPRINT, anim=None
```

**→ 四个时间点四个位姿。动画确实驱动了机型。**
**→ 之后恢复原状，关卡没被改。**

### 五、🔴 这次实战更正了两条既有结论

| 我之前说的 | 实际 | 错在哪 |
| --- | --- | --- |
| **「`set_position` 不触发重新求值」** | **会触发** | 当时没有动画被赋值，所以当然不动 |
| **「`get_bone_pose` 挂死 → 读不到骨骼」** | **`get_bone_transform` 完全能用** | 用错了 API |

**共同点：**把「我用这个方法失败了」当成「这件事做不到」。****

**这已经是本系列第 N 次同类错误。已经写进文档第十节。**

### 六、三个 API 坑

| 坑 | 表现 | 正确用法 |
| --- | --- | --- |
| `get_bone_transform(name, BoneSpaces.X)` | **TypeError** | **只传名字**，默认世界空间 |
| `get_play_rate()` | 无实例时返回 0.0，误导 | 读 `animation_data.saved_play_rate`（实际 1.0）|
| `get_asset_by_object_path(SoftObjectPath)` | **TypeError** | `get_assets_by_path` + 过滤 |

### 七、修复方案（**未应用**）

**在 `import_and_place.py` 的 `set_skeletal_mesh_asset` 之后加：**
```python
if anim is not None:
    component.set_editor_property("animation_mode",
                                  unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    data = component.get_editor_property("animation_data")
    data.set_editor_property("anim_to_play", anim)
    data.set_editor_property("saved_playing", True)
    data.set_editor_property("saved_play_rate", 1.0)
    component.set_editor_property("animation_data", data)
```

**并建议删掉结尾的 `level.save_current_level()`（崩溃触发点，且关卡由 `build_level.py` 重建）。**

**⚠️ 按用户要求「先不要急着开发」，**代码一字未改**。**

### 八、新增

| 产出 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-CASE-ANIM.md`** | 完整定位记录（起点/四步/根因/验证/更正/修复方案）|
| `Tools/diag_anim_step1.py` | 观察：组件状态 + 可用 API |
| `Tools/diag_anim_step2.py` | dump 结构体，找到根因 |
| `Tools/diag_anim_step3.py` | 验证根因并恢复原状 |

### 九、这次实战的意义

**九篇文档里的方法在这一个真实问题上串起来了：**
- 读结构体不读派生 getter（内存篇的教训）
- `-WaitPattern` 当失败检测（脚本篇）
- 按名字搜资产（资产篇）
- 改完恢复原状（项目规则 5）

**→ 这是第一次「不是写文档，而是用文档解决问题」。**

### 十、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | 再来一个实战案例（候选：78 个模型无 MATERIAL 块 / `thunder3` 转换失败）|
| 2 | 或者：等用户指示后应用这个修复 |


## 67. 调试系列第 10 轮：**实战 002 — 退化法线，根因在 `.mod` 的标志位**（2026-11-26 52:00）

### 一、起点是一条我一直没查的警告

```
LogStaticMeshOperations: Display: Mesh 0 has NaNs in it's vertex instance tangent space!
LogStaticMesh: Warning: SM_Boss001 拥有一些近零的法线，其可能诱发问题。（容差为 1E-4）
```

### 二、四步定位

| 步 | 做法 | 结果 |
| --- | --- | --- |
| 1 | 想在 `StaticMesh` 上读法线 | **Python 没接口**（只有 `get_num_lods` 等）|
| 2 | 改查 glTF 源文件 | **88.55% 退化**（550 零 / 569 非单位 / 2 NaN）|
| 3 | 想怪导出器 | **排除了** —— 缺失时写的是 (0,0,1)，不是零 |
| 4 | 查 `.mod` 原始数据 | **按 flag 完美分组** |
| 5 | 查反编译源码 | **`0x10` = NOT_SOLID** |

### 三、🔴 规律完美对应

| `mesh_flag & 0xF0` | 块 | 法线质量 |
| --- | --- | --- |
| **`0x00`（SOLID）** | mesh 0-5 | **全干净** |
| **`0x10`（NOT_SOLID）** | mesh 6-16 | **全退化** |

```
TOTAL: 1266 normals
  恰好为零: 103    非单位长度: 579    非有限: 24    退化: 706 (55.77%)
```

### 四、反编译源码给出语义

**`client_src/tw/4DyuchiGRX_common/mesh_flag.h`：**
```cpp
enum TRANSFORM_TYPE {
    TRANSFORM_TYPE_SOLID      = 0x0000000,
    TRANSFORM_TYPE_NOT_SOLID  = 0x00000010,   // ← 元凶
    TRANSFORM_TYPE_ALIGN_VIEW = 0x00000030,
    TRANSFORM_TYPE_ILLUSION   = 0x00000050
};
#define TRANSFORM_TYPE_MASK  0x000000f0
```

**`0x10` = **非实体几何** —— 特效/贴片/加色层，原始渲染器**根本不用它们的法线**。**

### 五、根因：导出器的 `has_normals` 漏了两种类型

```python
has_normals = (shade_type != SHADE_TYPE_LIGHT_MAP          # 排除了 0x03
               and transform_type != TRANSFORM_TYPE_ALIGN_VIEW   # 排除了 0x30
               and ...)
```
**⚠️ 漏了 `NOT_SOLID (0x10)` 和 `ILLUSION (0x50)`。**

### 六、影响面

**`boss001` 里 17 个 mesh 块，**11 个是 NOT_SOLID**，
占 **1046 / 1266 = 83% 的顶点**。**

**→ 这个 Boss 的**大部分表面**用退化法线 → 黑块、错误高光、法线贴图方向乱。**

### 七、🔴 对 `MOD-FORMAT-SOLVED.md` 的重要补充

| 之前 | 现在 |
| --- | --- |
| 「法线是条件性的，只有 LIGHT_MAP 和 ALIGN_VIEW 没有」 | **「有没有法线」和「法线能不能用」是两件事** |

**→ 客户端**确实读了** NOT_SOLID 的法线（按反编译的读取条件），
但它**读了不用** —— 因为是加色/半透明绘制。**

**→ 我们不知道这一点，就当正常数据用了。**

### 八、修复方案（**未应用**）

**保守方案：**
```python
if not has_normals or transform_type in (TRANSFORM_TYPE_NOT_SOLID, TRANSFORM_TYPE_ILLUSION):
    normals = [(0.0, 0.0, 1.0)] * vertex_num    # 复用现有的 filler 逻辑
```
**代价：NOT_SOLID 几何变成平面着色。但它们本来是特效层，比黑块好。**

**彻底方案：把 NOT_SOLID / ILLUSION 导出成独立 primitive，
在 UE 里赋双面 + 无光照/加色材质 —— 这才符合原始语义。**

**⚠️ 按用户要求「先不要急着开发」，**代码一字未改**。**

### 九、新增

| 产出 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-CASE-NORMALS.md`** | 完整定位记录 |
| `Tools/diag_normals_step1.py` | 想在 UE 里量（失败，记录 API 限制）|
| `Tools/diag_normals_gltf.py` | 纯 Python 解 glTF accessor 量法线 |
| `Tools/diag_normals_mod.py` | 复用导出器 parser 分类 `.mod` 法线 |

### 十、两个实战的共同点

| | 实战 001（动画）| 实战 002（法线）|
| --- | --- | --- |
| 表面症状 | 看不见动 | 引擎警告 |
| 真根因 | 脚本没赋值 | 源数据无语义 |
| 定位关键 | 读结构体 | 查反编译源码 |
| 都推翻了一个直觉假设 | 「引擎不求值」 | 「导出器写坏了」 |

**→ **两次都是「先排除最像的原因」，然后才找到真的。****

### 十一、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | 第三个实战（候选：`MX_BOSS001_STATIC` 仍然散开 / `thunder3` 转换失败）|
| 2 | 或者：应用已定位的两个修复（等指示）|


## 68. 调试系列第 11 轮：**实战 003 — 逆绑定矩阵转置两次，一行 bug**（2026-11-26 53:00）

### 一、起点：一句记录，而且**是错的**

**既有记录：「`MX_BOSS001_STATIC` 仍然散开」。**

**✅ 实测 bounds 立即推翻：**
```
MX_BOSSCOWF        extent (924.5, 512.7, 550.7) cm   ← 9.2×5.1×5.5 米，这才是散开的
MX_BOSS001_STATIC  extent ( 96.2, 217.1,  76.1) cm   ← 正常
MX_BOSS001         extent (149.9, 194.2, 132.7) cm   ← 正常
```

**→ **第三次「既有记录不可信」。**

### 二、六步定位（其中一步是陷阱）

| 步 | 做法 | 结果 |
| --- | --- | --- |
| 1 | 查 bounds | **推翻记录** |
| 2 | 截图 | 看见散落部件 |
| 3 | 量长轴 | **假线索**：三个模型 Z 都最小，像躺平了 |
| 4 | **查骨骼位置** | **🔴 67 根骨骼全在同一位置，跨度 0** |
| 5 | 查 glTF 关节节点 | 节点平移正确，**IBM 平移全零** |
| 6 | **查 3/7/11 槽** | **67/67 平移在这** → 证明转置两次 |

### 三、🔴 根因

**`export_mod_anim_gltf.py` 第 683-697 行 `invert()` 返回的列表**已经是列主序**（平移在 12/13/14）。**

**第 733-738 行 `build()` 又转置了一次：**
```python
inverse = invert(world)
# Transpose into glTF's column-major order.      ← 注释说的事 invert() 已经做完了
column_major = [inverse[c * 4 + r] for r in range(4) for c in range(4)]
```

**→ 平移从 12/13/14 被推到 3/7/11，glTF 读 12/13/14 得到全零。**
**→ 每根骨骼的绑定姿态被声称在原点 → 蒙皮公式 `globalTransform × IBM` 抵消不掉 → 网格散开。**

**修复：`column_major = inverse`。一行。**

### 四、🔴 为什么之前没发现 —— 最重要的方法论教训

**之前记录的验收方式是「往返误差 2.22e-16」。**

**→ 那个测试是「自己算 IBM，自己再逆回去，比对」——
证明了**算术对**，但**完全没碰到写进文件时的字节顺序**。**

> **验证必须用**独立的读取者**，不能用自己写的那一半去验另一半。**
>
> **正确做法：写完后用 glTF 规范位置（12/13/14）读回来，检查是否等于 `-R^T·t`。**
> **这正是第 6 步做的事，一次就抓到。**

### 五、影响面

**所有用这个导出器导出的**带骨骼模型**都受影响。**
**回归基线 8 个模型里带骨骼的 5 个：`108_bird` / `198_bobu` / `boss001` / `boss_cowf_01` / `107_crow`。**

**⚠️ 这些模型的**包围盒都对**（顶点没被改），但**绑定姿态和蒙皮全错**。**

**→ 这解释了「包围盒每次正常，但看起来就是不对」的长期困惑。**
**→ 包围盒量的是**顶点**，而问题是**矩阵**。**

### 六、三个方法论教训

| 教训 | 依据 |
| --- | --- |
| **验证要用独立读取者** | 自证误差 2e-16 掩盖了字节顺序错误 |
| **包围盒正常 ≠ 模型正确** | 它不量矩阵和绑定姿态 |
| **退化数据比错误数据更危险** | 67 根骨骼全同一点，「看起来没坏」 |

### 七、新增

| 产出 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-CASE-IBM.md`** | 六步完整定位 + 根因 + 方法论教训 |
| `Tools/diag_scatter_step2.py` | 量网格长轴与 actor 变换 |
| `Tools/diag_scatter_step3.py` | 量源空间三轴跨度 |
| `Tools/diag_scatter_step4.py` | 读骨骼位置（找到真机制）|
| `Tools/diag_scatter_step5.py` | 查 glTF 关节节点与 IBM |
| `Tools/diag_scatter_step6.py` | **验 3/7/11 槽（证明转置两次）** |

### 八、三个实战案例汇总

| 案例 | 症状 | 根因 | 定位关键 |
| --- | --- | --- | --- |
| 001 动画 | 看不见动 | 脚本没赋 animation_mode/anim_to_play | 读结构体 |
| 002 法线 | 引擎警告 | NOT_SOLID 几何本无语义法线 | 查反编译源码 |
| **003 IBM** | **模型散开** | **逆绑定矩阵转置两次** | **用规范位置读回来** |

**→ 三个都推翻了一个既有判断。**
**→ 三个的根因都在**导出器**，不在 UE。**

### 九、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | 应用三个修复（动画 / NOT_SOLID 法线 / IBM 转置），然后回归验证 |
| 2 | 或继续找案例 |

**⚠️ 按用户要求「先不要急着开发」，代码仍未改。**


## 69. 调试系列第 12 轮：**验证 IBM 修复 —— 修好一个，暴露第二个**（2026-11-26 54:00）

### 一、为什么要补这一步

**上一轮只做到「定位」。**定位不等于修好。**
**这一轮验证修复，并发现了**第二个**同源的 bug。**

### 二、方法：改副本，量完删

**不动真资产：复制 glTF → 只改矩阵字节 → 导入 `/Game/Moxiang/Test/` → 量 → 删。**

### 三、第一次只修槽位顺序

```
moved the translation on 67 of 67 matrices
verification: matrices with translation in slots 12/13/14: 67
```

**导入后量骨骼（✅ 实测）：**
```
BROKEN (original):  67 bones, span X=0.0     Y=0.0     Z=0.0     cm
SLOTS FIXED:        67 bones, span X=31351.3 Y=28949.8 Z=39738.4 cm
```

**→ 骨骼有偏移了，槽位修复**有效**。**
**→ 但跨度 **397 米**，明显过大。**

### 四、🔴 修 bug 1 才让 bug 2 露出来：**单位没缩放**

| 项 | 值 | 量级 |
| --- | --- | --- |
| glTF **节点**平移 | `[-0.00145, -3.49e-10, -1.3319]` | **1.33 米** |
| IBM 平移（未缩放）| `(32.15, -129.25, 0.145)` | **129** |
| IBM 平移（×0.01）| `(0.3215, -1.2925, 0.0015)` | **1.29 米** |

**→ `cp()` 把顶点从厘米转成米，但 `invert()` 用的是**厘米**矩阵。单位不一致。**
**→ 39738 cm ÷ 100 = **3.97 米** —— 正好是 Boss 的合理身高。**

### 五、两个 bug 必须都修

| # | 缺陷 | 修复 |
| --- | --- | --- |
| **1** | `invert()` 已是列主序，`build()` 又转置 | `column_major = inverse` |
| **2** | IBM 用厘米，顶点用米 | 平移部分 `× 0.01` |

**⚠️ 只修 #1 会得到「能蒙皮但放大 100 倍」的模型。**

**→ 这是**顺序调试**的典型：第一个修复把第二个 bug 从「被掩盖」变成「显形」。**

### 六、🔴 验证过程中我自己犯的两个错

| 错 | 后果 | 教训 |
| --- | --- | --- |
| 用 `-replace` 批量改脚本文本 | 路径被改成 `boss001_IBMFIX222.gltf`，导入失败 | **改路径用编辑工具，不用字符串替换** |
| `Get-Process` 里 `@{}` 缺 key 导致命令报错 | 我**误读成「编辑器进程没了」**，虚惊一场 | **报错不是空结果；先读报错本身** |

**→ 第二条是本轮最该记的：我把**命令报错**当成了**命令结果**。**

**（实际编辑器一直在跑：PID 4544 / 4582 MB，无新崩溃目录。）**

### 七、清理

```
CLEAN: deleted /Game/Moxiang/Test -> True
CLEAN: removed boss001_ibmfix.gltf / .bin / ibmfix2.gltf / .bin
```

**✅ 已确认测试资产和四个补丁文件都不在了，原资产一字未动。**

### 八、新增

| 产出 | 内容 |
| --- | --- |
| `Docs/UE5-DEBUG-CASE-IBM.md` **第 12 节** | 完整验证记录（含两个 bug 与自造错误）|
| `Tools/patch_ibm.py` | 只修槽位 |
| `Tools/patch_ibm2.py` | 槽位 + 缩放（带 `--noscalc` 开关）|
| `Tools/measure_imported_skeleton.py` | **量已导入资产（不需要导入，最简单可靠）** |
| `Tools/cleanup_ibm_test.py` | 清理测试资产与副本 |

### 九、三个实战案例的当前状态

| 案例 | 定位 | 修复验证 |
| --- | --- | --- |
| 001 动画 | ✅ | ✅ 骨骼四个时间点四位姿 |
| 002 法线 | ✅ | ❌ 未验证 |
| **003 IBM** | ✅ | ✅ **槽位+缩放两处都证实** |

### 十、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | 把这三处的修复**应用到导出器**，跑回归 |
| 2 | 或继续找案例 |

**⚠️ 代码仍未改 —— 等指示。**


## 70. 调试系列第 13 轮：**把方法固化成体检工具**（2026-11-26 55:00）

### 一、为什么做这个

**十一轮写了 20 多个一次性脚本，每个只回答一个问题、只回答一次。**
**→ 下次同类问题还得从头写。修复有没有生效，只能等它再出问题。**

**`Tools/diagnose.py` 解决第二类问题：让回归可见。**

### 二、它查什么

```
py Tools/diagnose.py                 # 完整（含骨骼）
py Tools/diagnose.py --noskeletal    # 跳过骨骼
```

| 域 | 检查项 |
| --- | --- |
| 资产 | `/Game` 与 `/Game/Moxiang` 资产数 + **按类统计** |
| 引用 | 所有 mesh 引用是否可解析 |
| **骨骼** | **跨度塌缩（<1cm）或异常（>2000cm）** |
| **动画** | **`anim_to_play` 是否为空、`animation_mode`** |
| 内存 | `obj cycles` |
| 配置 | 帧预算 / GI / 抗锯齿 / 虚拟阴影 |

### 三、🔴 第一次跑就抓到全部已知缺陷

```
DIAG:   actors: 116
DIAG:     COLLAPSED skeleton on MX_BIRD_TEST: span 0.00 cm
DIAG:     MX_BIRD_TEST           no animation assigned (mode='ANIMATION_BLUEPRINT: 0>')
DIAG:     COLLAPSED skeleton on MX_BOBU_TEST: span 0.00 cm
DIAG:     COLLAPSED skeleton on MX_BOSSCOWF:  span 0.00 cm
DIAG:     COLLAPSED skeleton on MX_BOSS001:   span 0.00 cm
DIAG:   mesh references checked: 103, missing: 0
DIAG:   collapsed skeletons: 4
```

**→ 案例 001 和 003 的缺陷**不是 Boss 独有** —— **4 个骨骼角色全部同时中招**。**
**→ 引用完整性没问题（103 个引用 0 缺失），所以问题不在路径。**

### 四、🔴 它当场纠正了我一个错误结论

**资产篇我写：「`Textures` 只有 1 个资产，贴图基本没导入 UE」。**

**体检发现：`Texture2D` 有 **99** 个。**

**→ 我查的是 `/Game/Moxiang/Textures` 目录（确实只有 1 个），
但 99 张贴图分散在**别的子目录**里（角色导入目录自带贴图）。**

**⚠️ 这正是我在资产篇里**警告过**的「分母陷阱」，然后自己掉进去了。**
**→ 体检按**类**统计而不是按**目录**，天然避开这个陷阱。**

### 五、设计原则

**① 只报告，不修复** —— 会自动修的体检没人敢信。
**② 阈值来自实测** —— 塌缩 <1cm（实测恰好 0.00）、异常 >2000cm（修一半是 39738）。
**③ 统一前缀 `[LingXuJie] DIAG:`** —— 可以用 `-WaitPattern` 判完成。
**④ `--noskeletal` 跳过慢的部分。**

### 六、它查不出什么（写进文档了）

| 查不出 | 靠什么 |
| --- | --- |
| 法线质量 | 查 glTF 源文件（案例 002）|
| 材质是否正确 | 人眼 + 缓冲可视化 |
| 性能 | `stat startfile` → Insights |
| 崩溃 | 读 `Saved/Crashes/` |
| 动画是否**在动** | 四时间点法（案例 001）|

**⚠️ 说清能力边界比说清查了什么更重要。**

### 七、新增

| 产出 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-TOOLKIT.md`** | 体检工具文档（含能力边界）|
| **`Tools/diagnose.py`** | 一次跑完八个域 |

### 八、这个系列的完整结构

| 篇 | 内容 |
| --- | --- |
| 1-2 | 日志与断言 |
| 3 | 崩溃 |
| 4 | 性能 |
| 5 | 内存 |
| 6 | 渲染 |
| 7 | 脚本 |
| 8 | 网络（未实测）|
| 9 | 资产 |
| 案例 001-003 | 三个真实故障 |
| **10** | **体检工具（收口）** |

**→ 前面的篇说**怎么查**，这一篇让**该查的每次都被查**。**

### 九、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | 应用三处修复（IBM 两处 + 动画 + 法线），然后跑体检验证 |
| 2 | 把体检挂到 `BuildAll` 之后 |

**⚠️ 代码仍未改 —— 但这次有了**自动验证修复的手段**，改完能立刻看到差异。**


## 71. 调试系列第 14 轮：**一百个「缺材质」的误报，和一个真的**（2026-11-26 56:00）

### 一、换个方向：先扫日志，再决定查什么

**前三轮都是我怀疑某处、再去查。这轮反过来：按类别统计日志里全部 74 条 Warning/Error。**

```
LogAutomationTest        Error    13   Condition failed
LogInterchangeEngine     Error     8   发现无效网格体数据（NAN）   ← 案例 002
LogEditorAssetSubsystem  Error     7   LoadAsset failed            ← 另一个案例
LogInterchangeImport     Warning   3   网格体拥有未指定材质的图元
MapCheck                 Warning   2   M_Ground_Triplanar 缺失 Nanite 标记
LogTexture               Warning   1   Texture2D contains no miplevels!
LogAnimation             Warning   1   Invalid animation skeleton
```

### 二、🔴 看起来像 101 个缺陷

**扫所有 Nanite 网格的材质槽（✅ 实测）：**
```
nanite-enabled static meshes: 101
WorldGridMaterial occurrences: 101
唯一材质: WorldGridMaterial
```

**`WorldGridMaterial` 是「未赋材质」的默认灰格材质。**
**→ 很容易写成「101 个建筑全都没材质」。**

### 三、🎯 拦住它的一句反问

**「截图上建筑明明有贴图，那材质从哪来的？」**

**→ 检查组件 override（✅ 实测）：**
```
static mesh components showing a real material: 98
static mesh components still on WorldGridMaterial: 1
    grid on MX_BOSS001_STATIC  (WorldGridMaterial)
```

**→ **98 个靠 `override_materials` 正常显示。资产级槽为空是**正常工作流**。**
**→ 只有 **1 个**真的没材质。**

### 四、那个真的

```
MX_BOSS001_STATIC:
  mesh slot 0        = WorldGridMaterial
  component override = 无（有效材质也是 WorldGridMaterial）
  项目里存在 M_Boss_Mob01（就是给它做的）
  nanite enabled = True
```

**→ 用默认灰格渲染，就是截图 `shot_scatter2.png` 里那个**灰白大块**。**
**→ 为什么漏了：`MX_BOSS001`（骨骼版）做过材质处理，`MX_BOSS001_STATIC` 是另一个 actor，**没跟上**。**

### 五、🔴 这是第四次同型错误被**提前**拦住

| 轮 | 我说 | 实际 | 同型 |
| --- | --- | --- | --- |
| 5 | 107 个遗留资产 | 是被引用的贴图 | 数字真、含义错 |
| 7 | Lumen 是零 | 一直在跑 | 同上 |
| 资产篇 | Textures 只有 1 个 | 实际 99 个 | **分母错** |
| **本轮** | **101 个缺材质** | **98 个有 override** | **数字真、含义错** |

**⚠️ 拦住它的不是工具，是一句**直觉反问**。**
**→ 结论与观察矛盾时，先信观察。**

**正确表述：**
> **「101 个网格的**资产级**材质槽是默认材质，但 98 个靠组件 override 正常显示。
> 只有 1 个既无资产材质也无 override。」**

### 六、MapCheck 那条警告怎么理解

**`used_with_nanite` 实测：**
```
M_Lanzhou_Stone        True
M_Ground_Triplanar     True     ← 内存里已经是 True
M_Boss_Mob01           False    ← 这个也是 False
M_Moxiang_Stone        False
```

**→ 警告说的是「**如果材质资产未重新保存**」——
内存 True、磁盘可能还是 False，MapCheck 在比较两者。**
**→ 修法：重新保存材质。**
**→ 而 `M_Boss_Mob01` 也是 False，所以就算赋给 `MX_BOSS001_STATIC`，
它也不是 Nanite-ready 材质，两件事要一起处理。**

### 七、新增

| 产出 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-CASE-MATERIAL.md`** | 误报 + 真缺陷 + 方法论 |
| `Tools/diag_warn_step1/2/3/4.py` | 四步：扫网格 → 查 override → 聚焦 → 确认 |

### 八、待修清单（**未应用**）

| # | 事项 |
| --- | --- |
| 1 | 给 `MX_BOSS001_STATIC` 赋 `M_Boss_Mob01` |
| 2 | 把 `M_Boss_Mob01` 的 `used_with_nanite` 设为 True 并保存 |
| 3 | 重新保存 `M_Ground_Triplanar` |
| 4 | 查 `T_Boss_Mob01` 的 mip 设置 |
| 5 | 查 `LogAnimation: Invalid animation skeleton`（**可能补充案例 001**）|

### 九、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | 查 `Invalid animation skeleton` —— 它可能推翻案例 001 的一部分 |
| 2 | 查 13 条 `LogAutomationTest: Condition failed` |
| 3 | 查贴图 mip |

**⚠️ 代码仍未改。**


## 72. 调试系列第 15 轮：**一条无害警告，和一个被推翻的假设**（2026-11-26 57:00）

### 一、起点：可能是推翻案例 001 的那条警告

**日志里的 `LogAnimation: Warning: Invalid animation skeleton`。
我怀疑它会让案例 001 的结论不成立。**

**先看上下文（✅ 实测）：**
```
D3: VERDICT: the animation moves the skeleton once it is assigned
LogAnimation: Warning: Invalid animation skeleton        ← 夹在这两行之间
D3: restored: mode=ANIMATION_BLUEPRINT anim=None
```

**→ 它夹在我的「VERDICT」和「restored」之间 —— 是**我恢复代码**产生的，不是项目问题。**
**→ **不推翻**案例 001。**

### 二、源码给出触发条件

**`SkeletalMeshComponent.cpp` 1589-1600：**
```cpp
if (PropertyThatChanged == AnimToPlay) {
    if (AnimationData.AnimToPlay && AnimationData.AnimToPlay->GetSkeleton()) {
        PlayAnimation(AnimationData.AnimToPlay, false);
    } else {
        UE_LOGF(LogAnimation, Warning, "Invalid animation skeleton");
        AnimationData.AnimToPlay = nullptr;
    }
}
```

**→ 触发条件：把 `AnimToPlay` 设成 **null**。**
**→ 我的恢复代码正是 `set_editor_property("anim_to_play", None)`。**
**→ **完全无害**。清空动画是合法操作。**

**连带（第 1501 行）：**
```cpp
if (AnimationMode == AnimationBlueprint) {
    if (AnimClass == nullptr) ClearAnimScriptInstance();   // ← 销毁单节点实例
}
```
**→ 我的恢复先改 mode 再清空 anim，两步合起来完全解释了那条警告。**

### 三、🎯 源码独立确认了案例 001 的两条结论

| 案例 001 的结论 | 源码依据 |
| --- | --- |
| 赋 `anim_to_play` 就会播放 | `PlayAnimation(AnimationData.AnimToPlay, false)` |
| `set_position` 会重新求值 | `SetPosition(AnimationData.SavedPosition, false)` |

**→ 这两条当初是**测出来**的，现在源码给出**机制**。**
**→ 方向对了：先测事实，再找机制。**

### 四、🔴 我的假设，和它被推翻

**假设：「必须先设 animation_mode，再赋 anim_to_play。
反过来的话 PlayAnimation 时还没有单节点实例，动画不启动。」**

**听起来合理，而且源码支持这个推理。**

**实验：同一 actor 两种顺序各测一次，看骨骼在 t=0 / t=0.5 有没有移动。**

**✅ 实测：**
```
mode_first   t=0 (9428.8, -6355.8, 3717.7)  t=0.5 (9428.7, -6358.4, 3721.0)  moved=True
anim_first   t=0 (9428.8, -6355.8, 3717.7)  t=0.5 (9428.7, -6358.4, 3721.0)  moved=True

VERDICT: the order does not matter here
```

**→ **两种顺序都动了，坐标完全相同。假设被推翻。****

**为什么错：我的采样函数最后还会写一次 `animation_data`，而 `SavedPosition` 变化会调
`SetPosition(...)` 求值。所以只要最终状态对，中间顺序不影响。**

**⚠️ 教训：读一段源码得出「必须这样」，可能只是**忽略了同文件里的另一条路径**。**

### 五、这轮的三个收获

| # | 收获 | 性质 |
| --- | --- | --- |
| 1 | `Invalid animation skeleton` 无害 | **排除假警报** |
| 2 | 源码确认案例 001 两条结论 | **机制补充** |
| 3 | 「顺序很重要」被推翻 | **负面结果** |

**⚠️ 第 3 条是**失败**，但我在写进文档前就测掉了。**
**→ 如果当结论写进去，那会是第 5 次「推理真但含义错」。**

### 六、新增

| 产出 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-CASE-WARNING.md`** | 警告溯源 + 源码确认 + 被推翻的假设 |
| `Tools/diag_order_step1.py` | 两种赋值顺序的对照实验 |

### 七、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | 查 13 条 `LogAutomationTest: Condition failed` |
| 2 | 查 `T_Boss_Mob01 contains no miplevels` |
| 3 | 或者开始应用已定位的修复 |

**⚠️ 代码仍未改。**


## 73. 调试系列第 16 轮：**把引擎的测试噪音当成项目的失败**（2026-11-26 58:00）

### 一、起点：13 条「测试失败」

**分类统计日志时，`LogAutomationTest: Error: Condition failed` 有 13 条 ——
数量第三多的错误类。听起来像严重问题。**

### 二、上下文直接给出答案

**日志原文（✅ 实测）：**
```
LogTemp: Error test: UE::UnifiedErrorTest::Empty: [空错误]
LogTemp: Error with param: UE::UnifiedErrorTest::WithInt: [整数-7出错]
LogTemp: Error with context: UE::UnifiedErrorTest::Empty: [空错误]
LogTemp: FError that has been invalidated: ::: []
LogTemp: FError that has been moved from: ::: []
LogAutomationTest: Error: Condition failed      ×13
```

**`UE::UnifiedErrorTest` —— 引擎在测**它自己的错误系统**。**

### 三、源码核实：逐字对应

**`Runtime/Core/Tests/Experimental/UnifiedError/UnifiedErrorTests.cpp` 末尾：**
```cpp
UE_LOGFMT(LogTemp, Log, "Error test: {Error}", Empty);
UE_LOGFMT(LogTemp, Log, "Error with param: {Error}", WithInt);
UE_LOGFMT(LogTemp, Log, "Error with context: {Error}", WithContext);
UE_LOGFMT(LogTemp, Log, "FError that has been invalidated: {Error}", Invalidated);
UE_LOGFMT(LogTemp, Log, "FError that has been moved from: {Error}", MovedFrom);
```

**→ **五行日志和源码一字不差。**这是同一个文件。**

**而 `Condition failed` 来自文件里的 `CHECK(...)` 断言
（`CHECK` 是自动化测试专用宏，不是 `check`/`ensure`）。**

### 四、🎯 真正的信号：项目测试 15/15 全过

**`Tools/RunTests.ps1` 用**独立无头进程**跑（不打扰编辑器）：**
```
completed=15 failed=0
ALL TESTS PASSED
```

**15 个测试逐条 `Result={Success}`：**
AutoEquip / Equip / Stacking / Catalog / DropTable /
AggroAndAttack / Leash / PatrolAndReturn /
AddExperienceLevelsUp / ExperienceCurve / KillReward / LevelCap / LevelUpFlash / StatRewards /
ModuleLoaded

### 五、🔴 教训：怎么区分引擎噪音和项目失败

| 判据 | 引擎噪音 | 项目失败 |
| --- | --- | --- |
| **测试名/路径** | `UE::UnifiedErrorTest` / `Runtime/Core/Tests/` | `LingXuJie.*` / `Source/LingXuJie/Private/Tests/` |
| **时间戳** | 启动阶段、帧号 `[0]` | 跑 `RunTests` 时 |
| **周围日志** | 与引擎源码逐字对应 | 只有测试框架输出 |
| **可复现** | 每次启动都有 | 改坏了才出现 |

**→ 最可靠的一招：**拿日志行去源码搜。**
**那些 `LogTemp` 行和 `UnifiedErrorTests.cpp` 一字不差，一搜就定位。**

**→ 这正是本系列反复用的方法：日志里的字符串，在源码里一定存在。**

### 六、顺带确认

**`RunTests.ps1` 用 `UnrealEditor-Cmd.exe` 独立进程，**不碰运行中的编辑器**。**
**→ 这是安全验证项目的正确方式。**
**→ 与 `RunGame.ps1`（会 `Stop-Process` 编辑器）完全不同 —— 规则 2 禁的是后者。**

### 七、新增

| 产出 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-CASE-TESTNOISE.md`** | 噪音溯源 + 项目测试实测 + 区分判据 |

### 八、六个案例汇总

| 案例 | 症状 | 性质 |
| --- | --- | --- |
| 001 动画 | 看不见动 | **真缺陷**（脚本没赋值）|
| 002 法线 | 引擎警告 | **真缺陷**（NOT_SOLID 无语义法线）|
| 003 IBM | 模型散开 | **真缺陷**（转置两次 + 单位）|
| 004 材质 | 101 个缺材质 | **误报 + 1 个真缺陷** |
| 005 警告 | Invalid animation skeleton | **无害** |
| **006 测试** | **13 个测试失败** | **引擎噪音，项目 15/15 全过** |

**→ 六个里只有三个是真缺陷。另外三个是**误报、无害、噪音**。**
**→ 这个比例（50%）说明「识别不是什么」和「找到是什么」一样重要。**

### 九、下一轮

| 顺序 | 任务 |
| --- | --- |
| 1 | 查 `T_Boss_Mob01 contains no miplevels` |
| 2 | 开始应用已定位的修复 |

**⚠️ 代码仍未改。**


## 74. 调试系列第 17 轮：**历史警告 vs 当前状态**（2026-11-26 59:00）

### 一、起点：最后一条未查的告警

**`LogTexture: Warning: Texture2D T_Boss_Mob01 contains no miplevels!`**

### 二、上下文揭示这是**导入失败的下游症状**

```
InterchangeImport: Warning: Imported DDS files must either be a single base mip,
                           or a full mip chain, not a partial mip chain
LogTexture:        Warning: T_Boss_Mob01 contains no miplevels!
LogUObjectGlobals: Warning: 未找到Object"T_Boss_Mob01"
InterchangeEngine: Error:   [.../boss_mob01.dds : InterchangeDDSTranslator] DDS D...
```

**→ DDS 的 mip 链是「部分」的 → Interchange 拒收 → 贴图没 mip → 对象找不到 → 导入失败。**
**→ 「contains no miplevels」**不是独立问题**，是下游症状。**

### 三、🎯 实测当前状态：健康

**Python 读不到 mip（`platform_data` 不可读）。
用引擎命令 `listtextures`（`memreport` 里也用它），它有一列 **`NumMips`**：**

```
512x512 (192 KB), PF_DXT1, TEXTUREGROUP_World,
  /Game/Moxiang/Textures/T_Boss_Mob01.T_Boss_Mob01, YES, NO, NO, 40, 10, NO
64x64 (8 KB), PF_DXT1, TEXTUREGROUP_World,
  /Game/Moxiang/tile_108_road01.tile_108_road01, NO, NO, NO, 1, 7, NO
```

| 贴图 | 尺寸 | NumMips | 完整？ |
| --- | --- | --- | --- |
| T_Boss_Mob01 | 512×512 | **10** | ✅ 512→…→1 正好 10 级 |
| tile_108_road01 | 64×64 | **7** | ✅ 64→…→1 正好 7 级 |

**→ 两张都是完整 mip 链。资产健康。**
**→ 那条警告是 11:57 失败那次留下的**历史记录**，后来走 PNG 的路子修正了。**

**顺带：`Usage Count = 40` 正好对应 Boss 的 40 个材质槽。**

### 四、🎯 DDS 的三种失败模式（错误信息都很精确）

| 模式 | 错误信息 | 怎么办 |
| --- | --- | --- |
| 格式不支持 | `DDS DXGIFormat not supported : 71 : BC1_UNORM` | 转 PNG |
| **mip 链是部分的** | `must either be a single base mip, or a full mip chain, not a partial mip chain` | 转 PNG 或补全 |
| 文件坏了 | `DDS D...` | 换源文件 |

**→ 结论：本项目 DDS 通路不可靠，统一 **DDS → PNG → UE**。**

### 五、🔴 方法论：分清历史警告和当前问题

**日志是**累积**的 —— 一次会话所有尝试都留着。
同一条警告可能在修复之前产生，修复之后仍留在文件里。**

| 判据 | 历史警告 | 当前问题 |
| --- | --- | --- |
| 时间戳 | 早于最后一次修复 | 最近操作之后 |
| 后续成功记录 | 后面有 `import completed` | 没有 |
| **当前实测状态** | **健康** | 有问题 |

**→ 唯一可靠办法：**直接测当前状态**，不要相信日志里的旧行。**
**→ 这轮就是：警告说「没有 mip」，实测说「有 10 级」。信实测。**

**→ 和案例 006 是同一课的两面：**
**日志告诉你**发生过什么**，不告诉你**现在是什么**。**

### 六、新增

| 产出 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-CASE-MIP.md`** | 历史警告溯源 + `listtextures` 用法 + DDS 三模式 |

### 七、七个案例的最终分类

| 案例 | 症状 | 性质 |
| --- | --- | --- |
| 001 动画 | 看不见动 | **真缺陷** |
| 002 法线 | 引擎警告 | **真缺陷** |
| 003 IBM | 模型散开 | **真缺陷** |
| 004 材质 | 101 个缺材质 | **误报 + 1 个真** |
| 005 警告 | Invalid animation skeleton | **无害** |
| 006 测试 | 13 个失败 | **引擎噪音** |
| **007 mip** | **贴图无 mip** | **历史残留，资产健康** |

**→ **七个里只有三个真缺陷、一个真误报、三个已解决/无害。****
**→ 这个比例本身是结论：日志里的「问题」大多数**不是当前问题**。**

### 八、日志信号清点完毕

**74 条告警已全部归类：**
- 31 条 = 我自己测试脚本打的
- 13 条 = 引擎自测噪音
- 8 条 = 案例 002（法线）
- 7 条 = 案例（资产路径）
- 3 条 = 未指定材质的图元
- 2 条 = MapCheck Nanite（案例 004）
- 2 条 = 近零法线（案例 002）
- 1 条 = 贴图 mip（**案例 007**）
- 1 条 = 动画骨架（案例 005）
- 其余 = MCP / 布局 / EOS 等环境提示

### 九、下一轮

**日志清点完了。现在只剩一件事：**应用已定位的修复**。**
**或者继续在别处找问题。**

**⚠️ 代码仍未改。**


## 75. 调试系列第 18 轮：**症状手册 + 两个工具坑**（2026-11-26 60:00）

### 一、把七次实战压缩成决策索引

**`Docs/UE5-DEBUG-PLAYBOOK.md` —— 不是知识文档，是**症状 → 该查什么**的索引。**

| 类别 | 覆盖的症状 |
| --- | --- |
| 模型看起来不对 | 散开 / 躺地 / 100 倍大小 / 黑块 / 灰格 / 包围盒对但比例怪 |
| 动画不动 | 没赋值 / 模式错 / 改位置没反应 / `get_bone_pose` 挂死 |
| 日志 Error/Warning | 6 种常见文本 → 该查什么 |
| 性能 | 30fps 显示绿 / 平均好看但有卡顿 / CVar 没效果 |
| 内存 | 环数 ≠ 泄漏 / 对象为何不销毁 / 内存涨的六步法 |
| 渲染 | 缓冲可视化只有 UI / `vis` 拼错名字静默 |
| 脚本 | 没输出 / 异常定位 / 对话框卡死 |
| 崩溃 | `PCallStack` 不是 `CallStack` |

**第五节是**五种推理错误**及各自的防法：**
1. 数字真但含义错（101 个缺材质）
2. 分母错（Textures 只有 1 个）
3. 把方法失败当事情做不到（`set_position` 不求值）
4. 自证式验证（IBM 往返误差 2e-16）
5. **把报错当结果**（`Get-Process` 报错 → 以为进程没了）

### 二、🔴 这一轮又犯了第 5 种错误两次

| # | 我做了什么 | 我看到什么 | 实际 |
| --- | --- | --- | --- |
| 1 | `Get-Content Docs/UE5-DEBUG-INDEX.md -First 6` | 中文全是乱码 | **文件是正常 UTF-8**，只是 PowerShell 默认按 GBK 读 |
| 2 | `-replace 'IBMFix','IBMFix2'` 改脚本 | 导入静默失败 | **文件名被替换成 `boss001_IBMFIX222.gltf`** |

**→ 第 1 次我差点去修一个没坏的文件。**
**→ 第 2 次是 `-replace` 全局替换，不区分标识符和文件名。**

**两条都记进 gotcha（#109 / #110）。**

### 三、新增

| 产出 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-PLAYBOOK.md`** | 症状 → 该查什么（八类 + 五种推理错误 + 工具边界）|
| `Docs/UE5-Gotchas.md` #109 | `Get-Content` 不写 `-Encoding UTF8` 显示乱码 |
| `Docs/UE5-Gotchas.md` #110 | PowerShell `-replace` 会连文件名一起替换 |

**Gotchas 总数：108 → **110 条**。**

### 四、调试系列现在的完整结构

| 层 | 文档 |
| --- | --- |
| **入门** | **`UE5-DEBUG-INDEX.md`（索引，顶部指向手册）** |
| **决策** | **`UE5-DEBUG-PLAYBOOK.md`（症状 → 查什么）** |
| 机制 | `LOGGING` / `ASSERTS` / `CRASH` / `PERF` / `MEMORY` / `RENDER` / `SCRIPT` / `NET` / `ASSET` |
| 实战 | 案例 001-007 |
| 工具 | `UE5-DEBUG-TOOLKIT.md` + `Tools/diagnose.py` |

**→ 从「遇到问题从哪看」到「机制是什么」到「真跑一遍」到「自动查」，形成闭环。**

### 五、下一轮

**调试系列该收口了。剩下的选择：**
1. **应用已定位的修复**（3 处导出器 + 1 处材质）—— 这会改代码
2. 继续找新问题

**⚠️ 代码仍未改。**


## 76. 调试系列第 19 轮：**收口 —— 一致性检查 + 总结**（2026-11-26 61:00）

### 一、三项验收

| # | 检查 | 结果 |
| --- | --- | --- |
| 1 | 体检工具 | `actors: 116` / `references checked: 103, missing: 0` / `collapsed skeletons: 4` |
| 2 | 项目测试 | **completed=15 failed=0 / ALL TESTS PASSED** |
| 3 | 文档与坑 | **调试文档 20 篇 / 全部文档 66 篇 / Gotchas 110 条** |

### 二、🔴 发现并修掉的结构问题

**磁盘有 19 篇调试文档，但 `LEARNING-INDEX.md` 只提到 11 篇。
→ 另外 7 个案例文档只能从调试索引找到，从主入口找不到。**

**修法：在学习索引的调试表下加了「七个实战案例」小表，逐条列出性质和状态。**

**修后核实：**
```
磁盘上的调试文档: 19 篇
学习索引里没提到的: （无，全覆盖）
```

### 三、新增 `Docs/UE5-DEBUG-SUMMARY.md`

**17 轮的收口文档，五节：**

| 节 | 内容 |
| --- | --- |
| 一 | 起点是什么、我自己定的四条标准 |
| 二 | 八个域 + 七个案例 + 两个工具 |
| 三 | **六类结论各自的验证方式** |
| 四 | **17 轮里更正自己的 9 次** |
| 五 | **还没做到的 7 件事（诚实清单）** |

**两个索引顶部都指向它。**

### 四、四之九次更正里最重要的三型

| 型 | 例子 | 出现次数 |
| --- | --- | --- |
| **把方法失败当事情做不到** | `set_position` 不求值 / `get_bone_pose` 挂死 | 2 |
| **数字真但含义错** | 101 个缺材质 / Textures 只有 1 个 | 2 |
| **把报错当结果** | `Get-Process` 报错 → 以为进程没了 | 1 |

**→ 第三型是这一轮又犯的（`Get-Content` 乱码）。**

**共同点：**推理真、前提错**。防法只有一条：**
**任何结论落地前，找一个能推翻它的独立观察。**

### 五、诚实清单（写在总结第五节）

| 事项 | 状态 |
| --- | --- |
| **三处导出器修复** | **已定位、已验证，未应用** |
| 一处材质赋值 | 已定位，未应用 |
| 网络调试 | 源码为主，**零实测** |
| minidump 分析 | 本机无 cdb/符号 |
| GPU 抓帧 | 本机无 RenderDoc/PIX |
| 蓝图断点 | Python 设不了 |
| 性能实测数字 | 面板抓不到，还没用 Insights 量 |

**⚠️ 最重要一条：所有修复停在「验证了机制」，没落到代码。**
**→ 「能定位」已证明；「能修好并确认」只证明了一半。**

### 六、调试系列最终结构

| 层 | 文档 |
| --- | --- |
| **入口** | `UE5-DEBUG-INDEX.md`（顶部指向手册和总结）|
| **总结** | `UE5-DEBUG-SUMMARY.md` |
| **决策** | `UE5-DEBUG-PLAYBOOK.md` |
| 机制（9 篇）| LOGGING / ASSERTS / CRASH / PERF / MEMORY / RENDER / SCRIPT / NET / ASSET |
| 实战（7 篇）| CASE-ANIM / NORMALS / IBM / MATERIAL / WARNING / TESTNOISE / MIP |
| 工具 | `UE5-DEBUG-TOOLKIT.md` + `diagnose.py` + `diff_captures.py` |

### 七、下一轮

**调试系列到此收口。**
**下一步最有价值的是**应用三处修复并跑体检验证** —— 把「能定位」补成「能修好」。**

**⚠️ 那会改代码，需要人点头。**


## 77. 渲染实操第一块：官方素材练习场 + Lumen 参数实测（2026-11-26 23:40）

### 一、换了练习场地（这是本轮的方向性决定）

**墨香是 2003 年的客户端：64×64 贴图、低模、光照烘在资源里。在它上面调 Lumen，
"好看"不代表渲染器对了。**
**→ 渲染/材质/性能的实操全部改用 Fab 免费包：`/Game/GeonchunmunComplex/Maps/Demo_GeonchunmunComplex`
（KHS 建春门，1159 actor，带 SkyAtmosphere / VolumetricCloud / 大量 PBR 网格）。**
**工程关卡 `LingXuJie` 不动；练完必须切回来并复位视角（本轮已做）。**

### 二、做到了什么

| 项 | 结果 |
| --- | --- |
| 官方素材场地切换工具 | `Tools/learn_practice.py`（open / restore / survey） |
| **脚本自己拍照** | `unreal.AutomationLibrary.take_high_res_screenshot` 可用，但它会卡游戏线程 |
| **可自动化的 A/B 驱动** | `Tools/learn_ab_run3.ps1`：变体 → 回读 CVar → MCP 抓图 → 复位 → 复位自检 |
| 像素差量化 | `Tools/learn_diff_all.py`（控制组当噪音地板）、`Tools/learn_diff_regions.py`（3×3 分块） |
| **实测表** | GI 关 **17.55%** / VSM 关 **1.17%** / AA 关 **0.99%** / 噪音地板 **0.03%** |

### 三、三个真坑（都改变了结论）

1. **`time.sleep` 卡游戏线程** → 9 次截图请求只落盘 1 张。改成"一变体一运行 + 外部抓图"。
2. **体积云让整帧像素差失去分辨力** → 控制组差 **23.48%**（天空带 56%、地面 0%）。冻结云后降到 **0.03%**。
3. **复位清单漏项** → GI 关掉后没被复位，三张不同旋钮的图**两两完全相同（0.00%）**。
   我一度以为是"引擎单向开关"，并发现在**重载关卡也不恢复**（CVar 是全局的）。

### 四、最重要的发现：两个 CVar 名字根本不存在

**`r.LumenScene.Visualize`、`r.LumenScene.Radiosity.Enable` 都不存在，控制台静默忽略，
看起来像"这两个功能没有视觉效果"。真名是 `r.Lumen.Visualize`、`r.LumenScene.Radiosity`。**
**查法：MCP `SearchCVars` 按前缀搜，返回里有 `value` 才说明存在。**

**`r.Lumen.Visualize 1` 是真正好用的诊断视图：三宫格显示 Geometry Normals / Reflection View /
Lumen Scene（**Pink = 缺 Surface Cache 覆盖**）。实测这个免费包里城楼和地面有大片 Pink ——
资源层面没进 Lumen 场景，不是参数问题。**

### 五、怎么验证的

```
Saved/learn_ab4/ab_base.png         基线
Saved/learn_ab4/ab_control.png      控制组：0.03%（噪音地板）
Saved/learn_ab4/ab_after_restore.png 复位自检：0.02%（复位真的发生了）
Saved/learn_ab4/cvar_readback.txt   每个变体拍摄时的 CVar 值
Saved/learn_ab3/ab_lumen_visualize.png  Lumen 诊断视图
```

**复位后已切回工程关卡：`level now: LingXuJie` / `actors: 116` / `camera at 8950, -6200, 3900 yaw 0 pitch -2`。**

### 六、归档

- **新文档 `Docs/UE5-RENDER-HANDSON.md`**（管道 + 数据表 + 三次更正 + 下一轮清单）
- Gotchas **110 → 115**：#111 PowerShell 变量名不分大小写、#112 复位清单漏项、
  #113 两个 Lumen CVar 名不存在、#114 `time.sleep` 卡游戏线程、#115 动态天空毁掉像素差
- **#108 已按人的新指示改写：允许抢焦点**（`RebuildInEditor` 变成常规手段）
- `LEARNING-INDEX` 加了"动手调渲染"入口 + 4 条速查结论

### 七、下一轮

| 优先级 | 实验 | 为什么 |
| --- | --- | --- |
| 1 | 给三个"此机位测不到"各补决定性实验（金属球/近景/×8） | 把"没测到"变成"机制确认" |
| 2 | **这些开关的帧时间代价（毫秒）** | 现在只有像素差，没有性能数字 |
| 3 | Lumen 质量档在性能上的台阶 | 学会按预算调，不按好看调 |
| 4 | 后处理（曝光/Bloom/AO）同法实测 | 渲染域后半 |

## 78. 一次 MCP 调用跑完「查材质槽 + 赋材质 + 双截图」（2026-11-27 11:40）

### 一、做了什么

**把案例 004 那个真缺陷补上了：`MX_BOSS001_STATIC` 赋 `M_Boss_Mob01`。**
**全程**一次** `execute_tool_script` 调用**（12 个工具串在一起，7.1 秒，返回 3.94 MB），
里面是读槽、赋材质、回读、存关卡、**两张同一机位的截图**。没有控制台、没有日志文件。

### 二、最重要的发现：材质槽有**两层**，资产那层改了不算数

**第一次调用**：`StaticMeshTools.set_material` 把资产槽从 `WorldGridMaterial` 改成 `M_Boss_Mob01`
（返回 true，回读确认），存盘也成功 —— **两张截图几乎一模一样。**
**原因**：`SM_Boss001` 的组件 `overrideMaterials` 里有一条**显式** `WorldGridMaterial`。
资产槽和组件 override 都有值时，**组件赢**。
**修法**：`ObjectTools.set_properties(组件, {"overrideMaterials": [M_Boss_Mob01]})`，然后存**关卡**
（组件 override 是关卡里的数据，不是资产里的）。

> 这条也修正了案例 004 的措辞：当时写"组件也没 override"，
> **实际是"组件有一条指向 WorldGrid 的 override"** —— 结论一样（真的没材质），但修法完全不同。

### 三、验证

```
set_ok: true
component_override_before: WorldGridMaterial
component_override_after : M_Boss_Mob01
level_saved: true        level_dirty_after_save: false
两帧像素差 9.50%（>8 阈值）；3×3 分块最下排（地面）0.00%，差异集中在角色身上
camera_actual: 8950, -6200, 3900  yaw 0  pitch -2   ← 已回默认观察位
```

图：`Saved/boss2_before.png` / `Saved/boss2_after.png` / `Saved/boss2_compare.png`（上下拼接）

### 四、这一轮踩的四个坑（Gotchas 115 → 119）

| # | 坑 | 一句话 |
| --- | --- | --- |
| 116 | 组件 override 优先于资产材质槽 | 查槽要查两层，改也要改对那层 |
| 117 | 沙箱里 `try/except` 抓不住工具报错 | 一次调用里任何一个工具失败，整个 `run()` 的结果都没了 |
| 118 | `CaptureViewport` 必须显式传 `annotations` | schema 说可选，包装函数没有默认值 |
| 119 | PowerShell 的字符串不一定是字符串 | `[string](Get-Content -Raw)`，否则 `ConvertTo-Json` 变成 `{"value":...}` |

**顺带确认**：`EditorAppToolset.SetCameraTransform` **真的会移动编辑器相机**（实测 (8950,-6200,4600)/pitch -25 → 还原）。
规则 3b 的复位以后可以直接走 MCP，不必 `RebuildInEditor` + `reset_view.py`（那条仍是兜底）。

### 五、改了哪些文件

- `Tools/place_static_boss.py`：重建 actor 时逐槽赋 `M_Boss_Mob01` —— **重建后不会再丢**
- `Docs/UE5-WORKFLOW-FIX.md`：新增第八节（一次调用的完整配方 + 数据 + 四条更正）
- `Docs/UE5-Gotchas.md`：#116–#119；`AGENTS.md` 的坑数同步到 119
- 内容资产：`Content/Maps/LingXuJie.umap`（组件 override 已存盘）、`SM_Boss001`（资产槽也设了）

### 六、下一轮

| 优先级 | 事项 | 为什么 |
| --- | --- | --- |
| 1 | **`MX_BOSS001_STATIC` 不在 `build_level.py` 里** | 跑一次重建（`new_level`）这个 actor 会整块消失；要不要把它并进生成流程？**要人拍板** |
| 2 | 工作方式的第二块：用同一套一次调用做「动画接线」或「NOT_SOLID 法线」 | 一次只改一样 |
| 3 | `LEARNING-INDEX` 补"查材质槽要查两层"到速查表 | 下次别再只查资产槽 |

## 79. 清理规则落地：`Tools\Cleanup.ps1` + AGENTS 第 13 条（2026-11-27 12:10）

### 一、先量，再定规则（量完结论变了）

| 类别 | 体积 | 判断 |
| --- | --- | --- |
| `.git\lfs` | **5.55 GB**（7,527 个对象） | 最大块；要**先 push 再 `lfs prune --verify-remote`**，一次性、人拍板 |
| `Content` | 4.73 GB | 真资产，永不动 |
| `Intermediate\Build` | **4.24 GB** | 能删，但下次整编；不做日常清理 |
| `Saved` | 1.09 GB | 截图 675 MB（517 张）+ 根目录散件 293 MB（608 个） |
| `Assets` / `Binaries` | 0.48 / 0.46 GB | 永不动 |
| `Tools` | 443 文件 / 1.6 MB | 体积忽略，**负担是导航** |
| **C: 空闲** | **621.7 GB / 952.7 GB** | **空间不急** —— 所以规则的目标是"别涨成 50 GB"，不是"今天就要删" |

### 二、规则（AGENTS 第 13 条）

- **触发**：`Saved` ≥ 1.2 GB 或截图 ≥ 600 张才算一次，**不是每块收尾都清**；
- **白名单**：`Saved\Screenshots`、`Saved\Logs`、`Saved\Autosaves`、`Saved\Crashes`、`Saved\Shader*`、
  `Saved\learn_ab*`、`Saved` 根目录散件；`Content/Assets/Binaries/Config/Source/Docs/Tools/.git` 永不碰；
- **保留**：14 天内不动 + 最新 120 张截图 + 最新 15 个日志（那是文档指着的证据）；
- **`Intermediate\Build` 只能 `-IncludeIntermediate`**，编辑器必须关；
- **`.git\lfs` 不在这条规则里**：没 push 就 prune = 删掉只在本地的资产，不可恢复；
- **一次性脚本不进 `Tools`**：放 `Saved\scratch\`。

### 三、脚本实测

```
默认（-KeepDays 14）：would delete 0 files, 0.0 MB
  Saved now 1,087.2 MB（阈值 1,200）｜截图 517（阈值 600）→ 未触发
演示（-KeepDays 3 -KeepShots 40）：would delete 628 files, 723.1 MB
  截图 472 文件 / 655 MB、日志 44 / 9.4 MB、Shader 8 / 16 MB、散件 104 / 42.7 MB
```

`-Apply` 才删，每次往 `Saved\cleanup.log` 追加一行（时间、参数、删了多少、Saved 前后）。
**默认参数下现在一个文件都不会删**——这是对的，现有截图都在 14 天内。

### 四、`Tools` 不搬家

443 个文件里 118 个是 `write_/link_/add_` 这类一次性脚本。**没有搬**：搬动会让 `Docs` 里一票路径引用失效，
而它们一共 1.6 MB、对构建零影响。改成加 **`Tools/README.md`**（工具链清单 + 历史脚本按前缀说明 + 新脚本放 `Saved\scratch\`）。
**要的是可发现性，不是搬家。**

### 五、下一步（都要人点头）

| 事项 | 能回收 | 前置 |
| --- | --- | --- |
| 立刻回收一次 | ~723 MB | 跑 `Cleanup.ps1 -KeepDays 3 -Apply`，会删掉 3 天前的截图证据 |
| 收 `.git\lfs` | 最多 ~5.5 GB 里的一部分 | 先 `git push`，再 `git lfs prune --verify-remote` |
| 删 `Intermediate\Build` | 4.24 GB | 关编辑器；下次整编 |

## 80. 异地备份第一次尝试：`main` 推不上去，改成"代码+文档快照分支"（2026-11-27 11:50）

### 一、结果

| 项 | 状态 |
| --- | --- |
| 远程新分支 `backup-code-20261127` | ✅ `a7da06f`，**859 个文件 / 7.8 MB**（含 7 个 LFS 图 2.7 MB） |
| 里面有 | `Docs/`、`Source/`、`Config/`、`Tools/`、`Build/`、`Assets/Map/p0_world.json`、根目录工程文件 |
| `main` | ❌ 仍是 `2e8e071 Initial commit`；**234 个提交只在本地** |
| 5.2 GB 资产 | ❌ **没有备份** |

### 二、为什么推不上去：GH008 + 免费 LFS 额度

```
GIT_LFS_SKIP_PUSH=1 git push -u origin main
remote: error: GH008: Your push referenced at least 1000 unknown Git LFS objects
remote: pre-receive hook declined
```

**GitHub 在服务端校验 LFS 指针**，跳过本地上传没有用。而且真正的问题不是"历史太大"：

```
HEAD 当前就引用 5,200 MB / 5,361 个 LFS 文件（Content + Assets + Binaries）
GitHub 免费额度 1 GB 存储 / 1 GB·月流量
```

**→ 光当前内容就超免费额度 5 倍。** 实测 `git lfs prune --dry-run` 也只能回收 **400 MB**，
而且删的是"只在本地的旧版本"——**在 push 成功之前不该 prune**。

### 三、快照分支的固定做法（已写进 AGENTS 规则 8）

```powershell
git checkout --orphan backup-code-YYYYMMDD
git rm -r --cached .
git add AGENTS.md README.md LingXuJie.uproject .gitignore .gitattributes Docs Source Config Tools Build Assets/Map
git commit -m "Snapshot YYYY-MM-DD: code, docs and tooling only"
git push -u origin backup-code-YYYYMMDD
```

**只放"重下不来的东西"。** Fab/Moxiang 那 5.2 GB 有账号就能重导，文档和 121 条 gotcha 重不来。

### 四、切回 `main` 的坑（gotcha #121）

`git checkout main` 直接被拒：`untracked working tree files would be overwritten`；
`git checkout -f main` 会**按 LFS 重写全部 5.2 GB**（中途失败就是一堆指针文本）。
**安全做法不碰工作区：**

```powershell
git symbolic-ref HEAD refs/heads/main
git read-tree HEAD
```

已验证：`git status --porcelain` **0 行**，`LingXuJie.umap` 仍 214,640 字节。

### 五、下一步（要人拍板）

| 选项 | 成本 | 效果 |
| --- | --- | --- |
| 买 GitHub data pack | 约 $5 / 50 GB | 唯一能把 5.2 GB 资产推上去的办法 |
| 换远端（GitLab 免费档 LFS 额度更大） | 迁移时间 | 同上，但要改 remote 和习惯 |
| 每个里程碑打一次快照分支 | 0 | 只保代码+文档，资产永远在本地 |

**在拍板之前：`main` 仍然只有本地一份，磁盘坏 = 全丢（资产部分）。**

## 81. 大资产退出 git：历史重启成"只有文本"的 14 MB（2026-11-27 12:00）

### 一、为什么推翻第 80 节的方案

**人的判断："大的资产不要进 git。"** 对的，而且比"买 data pack"更根本：

| 事实 | 数字 |
| --- | --- |
| `HEAD` 引用的 LFS 文件 | **5,208 MB / 5,361 个** |
| GitHub 免费 LFS | **1 GB** |
| `lfs prune` 能回收 | **400 MB**（5,463 个对象是当前版本，删不得） |

**→ LFS 解决的是 git 对象膨胀，不解决配额和推送体积。** 体积只能在"要不要进版本库"这一层解决。

### 二、做了什么

```
archive-lfs             旧历史（236 个提交 + 5.2 GB LFS 对象），**只留在本地，永不推**
main                    新的孤儿历史，1 个提交，**1,132 个文件 / 14.2 MB**
Remote backup-code-*    昨天的代码+文档快照，留着
```

**`.gitignore` 新规则（AGENTS 硬约束 5）：**

```
Content/
Assets/**/*.png  *.jpg  *.obj  *.bin  *.glb  *.dds  *.hdr  *.fbx  …
# 文本保留 —— build_level.py 要读它们
Assets/Gate/geonchunmun_gate.json
Assets/Map/p0_world.json
Assets/**/*.gltf            （269 个，6.1 MB）
```

**保留 `.gltf` / `.json` 的原因不是"想留"，是 `build_level.py` 真的读它们**
（`Assets/Gate/geonchunmun_gate.json` 在 1241 行被引用；`p0_world.json` 是 D12 的关卡真源）。

### 三、验证

```
git ls-files         1148
tracked 工作区体积    16.3 MB
git status           0 行
check-ignore         Content/*.umap=ignored, Assets/**/*.png=ignored,
                     Assets/Map/p0_world.json=kept, Assets/Gate/*.json=kept
```

### 四、代价（要记住）

- **粒度历史没了**：远程只有 1 个提交，`git log` 看不到分段。旧历史在本地 `archive-lfs`，
  磁盘坏就一起没了 —— 这是"大资产不进 git"的必然代价。
- **新克隆必须自己补资产**：`Content/` 不在库里。重建路径要写进 `Docs/ASSETS.md`（**待补**）。
- **`.git` 仍是 5.6 GB**：空间由 `archive-lfs` 占着。确认不再需要后：
  `git branch -D archive-lfs` + `git lfs prune` 才能真回收。

### 五、资产的备份：**决定"只在本机"**（2026-11-27 12:10，人拍板）

**不买 data pack、不换远端。5.2 GB 资产只存在这台机器上。**

| 东西 | 备份状况 |
| --- | --- |
| 代码 / 文档 / 工具 / `.gltf` / `.json` | ✅ GitHub `main`（14.2 MB，每次 commit 都能推） |
| `Content/`（4.7 GB）+ `Assets/` 二进制（0.48 GB） | ❌ **只有本机一份** |
| 例外：`Assets/Textures` 16 张自绘 PNG（2.1 MB） | ✅ 已进 git —— **生成脚本已不在，丢了就真没了** |

**代价说清楚：磁盘坏 = 资产没了。** 代码和文档能拉回来，`Content/` 只能重导。
**所以 `Docs/ASSETS.md` 必须写清"每个包从哪来、用哪个脚本导" —— 这是接下来的硬任务**，
不然"重下得来"只是嘴上说说。

**免费降低风险的办法只有一个**：偶尔把整个工程目录（17.8 GB）拷到移动硬盘。

### 六、下一步

| 事项 | 备注 |
| --- | --- |
| **`Docs/ASSETS.md` 补"资产怎么重建"** | 现在没有它，资产丢了就是真丢了 |
| 删 `archive-lfs` 回收 5.5 GB | 确认旧历史不要了再动（`git branch -D archive-lfs` + `git lfs prune`） |
| 继续业务：工作方式第二块（动画接线 / NOT_SOLID 法线） | 备份这条线到此收口 |