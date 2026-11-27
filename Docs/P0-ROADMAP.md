# 《灵虚界》P0 路线图与交接说明

> 本文件用于跨会话交接：新会话（工作目录 `C:\Users\tk\Desktop\lingxujie`）读这一份即可继续。
> 最后更新：2026-11-22

## 项目定位

东方修仙题材 **3D MMO** 原型，UE 5.8.4 + C++ + 编辑器 Python。
P0 目标：**验证核心循环（打怪 → 掉落 → 升级 → 换装）+ 修仙视觉氛围 + 多人同屏可行性**，
不是做完整 MMO。

## 里程碑状态

| 里程碑 | 内容 | 状态 |
| --- | --- | --- |
| **M0.0 骨架** | C++ 模块、GameMode、Python 生成关卡（石台/灵门/石柱/灵气环）、工具链（构建/测试/打包/验证/发布） | ✅ 完成 |
| **M0.1 移动与相机** | 第三人称越肩、冲刺、闪避（Ctrl/C）、御剑滑翔（空中按空格）、Lumen+VSM | ✅ 完成 |
| **M0.2 战斗基础** | 普攻 J/LMB、剑诀 1、Qi Burst 2、灵力与冷却、HP/伤害、HUD 伤害数字、训练木桩（重生）、死亡回城 | ✅ 完成 |
| **M0.3 AI + 掉落 + 装备** | 2 种小怪（灵兽近战 / 邪修远程）、巡逻-索敌-仇恨-攻击、掉落、背包格子、穿装加属性、经验升级 | ✅ 完成（5/5） |
| **M0.4 任务 + UI** | 一条任务链（对话→杀怪→交任务→升级→学技能）、血条/灵力/技能栏/任务追踪 | ⬜ |
| **M0.5 网络压力测试** | Dedicated Server、2 客户端 + 20 假人同屏、帧率与同步数据 | ⬜ **建议在 M0.3 后先做一次粗测** |

## M0.3 建议顺序（下一步从这里开始）

1. ✅ **经验与等级**：击杀给经验，升级 +攻击/生命，HUD 显示 `Lv.N EXP x/y`
   - `ULXJProgressComponent`（等级/经验/升级奖励，纯逻辑可单测）：`ExpToNext = 50 + 50*Level`，上限 Lv.60
   - 升级：每级 +18 最大生命（并按同量回血）、+4% 伤害倍率；`ULXJCombatComponent` 三招都乘 `GetDamageMultiplier()`
   - 击杀结算：`ULXJProgressComponent::GrantKillReward(Killer, Exp)`，木桩/怪物死亡时调用
   - HUD：左上 `Lv.N` + `EXP x/y` + 紫色经验条，升级时中央 `LEVEL UP Lv.N` 横幅（1.6s 淡出）
   - 训练木桩经验调成 100（一次击杀刚好升到 Lv.2，方便验证）；真怪之后给 45~60
   - 测试：`LingXuJie.Progress.*` 6 条（曲线/升级/上限/横幅/击杀奖励/属性叠加）
2. ✅ **怪物 AI**：`ALXJMonster`（Character + 状态机）+ 两种子类
   - brain 抽成纯函数 `LXJMonsterBrain::NextState()`（巡逻/追击/攻击/脱战），无世界依赖、可单测
   - 灵兽 `ALXJSpiritBeast`：追击半径 1200，攻击距离 200，冲锋速度 620，22 伤 / 1.4s
   - 邪修 `ALXJEvilCultivator`：保持 800 距离，1000 内放 `ALXJProjectile` 法术弹（16 伤 / 2.4s）
   - 仇恨：看见（≤1200）或被打都触发，脱战距离 2400~3000（leash），回家后转巡逻
   - 死亡：给击杀者经验、隐藏 14~16s 后原地重生；怪物之间不互相伤害
   - 测试：`LingXuJie.MonsterBrain.*` 3 条
3. ✅ **掉落**：怪物死亡按掉落表生成 `ALXJPickup`，玩家靠近 220 自动吸取
   - 物品表在代码里（`LXJItems`，不是 DataTable）：灵石 / 玄铁剑 / 玉灵甲 / 灵虚剑 / 流云袍
   - 掉落表纯函数 `LXJItems::RollDrops()`：灵石必掉（近战 4~8，邪修 6~12），装备 25%/35% 概率
   - 拾取物形状+材质区分类型（球=灵石、剑=武器、柱=护甲），待机上下浮动，飞向玩家
   - 拾取后 HUD 右侧滚动 `+4 LING SHI` 提示；90 秒不捡会消失
4. ✅ **背包与装备**：`ULXJInventoryComponent`（12 格、99 堆叠）+ 武器/护甲槽 + 属性汇总
   - 装备/卸下按“差值”推给 `ULXJHealthComponent::AddMaxHealth` 与 `ULXJCombatComponent::AddAttackPercent`
     （与升级加成叠加，不互相覆盖）
   - P0 无背包 UI：拾取时**自动穿戴更强的**同部位装备，旧的塞回背包（`TryAutoEquip`）
   - HUD 显示 `LING SHI n` / `BAG n/12` / `W:` `A:` 当前装备
   - 测试：`LingXuJie.Items.*`、`LingXuJie.Inventory.*` 共 6 条
5. ✅ **收尾**：木桩已下线（`build_level.py` 里 `TRAINING_DUMMIES=False`，留着开关方便调试），
   关卡只剩 4 只真怪；`Tools\Package.ps1 -Config Shipping` 打包通过（158 MB），
   `Tools\VerifyPackage.ps1` 启动打包版 → 跑位/攻击 → 截图，HUD 与战斗都正常
   - 已知：Shipping 版不产生 `Saved/Logs`（%LOCALAPPDATA% 那次目录根本没被创建），
     验证只能看截图；`VerifyPackage.ps1` 已改为找不到日志只警告

## 已知坑（必读，别重复踩）

全部在 `Docs/UE5-Gotchas.md`，P0 阶段新增的 4 条：

- **#28** 伤害数字用 `UTextRenderComponent` 在 Game 模式不渲染 → 用 Canvas HUD + `Canvas->Project`
- **#29** 自定义相机要在 `BeginPlay` 里从 Controller 取 yaw，否则 W 永远走世界 +X
- **#30** `EKeys::Type` 不存在（用 `FKey`）；`FOverlapResult` 要 include `Engine/OverlapResult.h`
- **#31** 排查关卡内容用 `Tools/inspect_level.py` 写 `Saved/level_actors.txt`

继承自 CoinRush 的 27 条同样适用（Live Coding 互斥、LFS、MCP 会话、SAC 拦 UBT、打包版存档路径等）。

## 常用命令

```powershell
powershell -ExecutionPolicy Bypass -File Tools\BuildAll.ps1          # 编译 + 生成关卡
powershell -ExecutionPolicy Bypass -File Tools\BuildLevel.ps1        # 只生成关卡
powershell -ExecutionPolicy Bypass -File Tools\RunGame.ps1 -Seconds 20 -Sequence "W:1.5|2:0.05"
powershell -ExecutionPolicy Bypass -File Tools\RunTests.ps1
powershell -ExecutionPolicy Bypass -File Tools\Package.ps1 -Config Shipping
powershell -ExecutionPolicy Bypass -File Tools\VerifyPackage.ps1
powershell -ExecutionPolicy Bypass -File Tools\MakeRelease.ps1 -Version v0.0.1
```

## 操作键位（P0）

| 键 | 功能 |
| --- | --- |
| WASD / 方向键 | 移动（相机相对） |
| 鼠标 / Q E | 转视角 |
| Space | 跳跃；**空中按住 = 御剑滑翔** |
| Shift | 冲刺 |
| Ctrl / C | 闪避冲刺（0.75s 冷却） |
| J / 鼠标左键 | 普攻（剑击） |
| 1 | 剑诀（单体高伤，耗灵 30） |
| 2 | Qi Burst（群体，耗灵 60） |
| Esc | 退出 |

## 当前仓库状态

- 远程：**`git@github.com:fastDevUe5/lingxujie.git`**（2026-11-22 建好并推送，main 已跟踪，37 个 LFS 对象 3.1 MB 已上传）
  - **注意：仓库当前是 public**（匿名调 `api.github.com/repos/fastDevUe5/lingxujie` 返回 200）。
    要改私有：仓库 Settings → General → 最下面 Danger Zone → Change repository visibility。
  - 仓库名在 GitHub 上的规范形式是**小写 `lingxujie`**；用 `LingXuJie` 会被 301 重定向（push 仍能成功，但会刷 warning）。
- 本地提交 15+，工作区干净；远程**只在里程碑收口时推**（本地可能领先远程，这是有意的）
- 仓库清理（2026-11-22）：早期提交误把 `Binaries/ Intermediate/ Saved/` 入库（含 2.3 GB 的 shared PCH），
  `.git` 一度 610 MB、GitHub 会因单文件 >100 MB 直接拒收。已用 `git filter-branch` 重写历史去掉这些路径、
  `.git` 降到 7 MB；备份在 `C:\Users\tk\Desktop\lingxujie-history-backup.bundle`（547 MB，确认无误后可删）。
  `.gitignore` 已补上 Unreal 构建产物。
- 推送验证（2026-11-22）：远端 `refs/heads/main` 与本地 HEAD 一致；**全新 clone 回来** `LingXuJie.umap`
  是 71 KB 真实资产（不是 LFS 指针），13 个 LFS 文件全部可取 → LFS 端到端打通。
- 关卡 actor 数：35（4 只怪：2 灵兽 + 2 邪修）
- 测试：15 条（Progress 6 / MonsterBrain 3 / Items 2 / Inventory 3 / 冒烟 1）
- 打包：`Saved\Package\Shipping\Windows`（158 MB exe），打包版实测可玩（截图 `Saved\Screenshots\Pkg_Run.png`）
- 编辑器 MCP：需先 `UnrealEditor.exe <uproject> -ModelContextProtocolStartServer`，
  重启编辑器后要在 DSH 里禁用/启用 `@local/unreal-mcp` bundle 重连

## 美术 / 资产：Polyfork 试验结论（2026-11-22）

试过 [Polyfork](https://polyfork.dev/)（3,505 个免费低模 + 2,113 个付费 HD，资产是"带旋钮的程序"，
可导出 GLB/FBX/USDZ/OBJ，商用免署名）。试验脚本：[`Tools/polyfork_trial.py`](Tools/polyfork_trial.py)
（导入 6 个中国风道具 → 摆成山门 → 截图 → 可一键重放）。

**能用的**：几何、尺度、风格都合适。石狮、石灯笼、青铜三足鼎、院落户型、多层塔、枣树/国槐这批
正好补上"石台 + 灵门"缺的东方环境层，低模平面着色跟我们现有的 primitive 风格不打架。
实拍证据：`Saved/Screenshots/polyfork_trial.png`（两尊石狮夹着台阶、石灯笼立在两侧、左右各一座檐顶建筑）。

**卡点（都是实测）**：
1. **GLB 进 UE 会丢颜色**：Interchange 把顶点色塌成单个 `<id>_material_0`，道具全是白的。
2. **多部件拆分**：一个 GLB 变成 `/Game/<id>/StaticMeshes/` 下多个网格（塔 3 段、院子 3 件），要整体 spawn。
3. **骨骼件丢失**：树冠等带骨骼的部件进成 SkeletalMesh，静态 spawn 只剩树干。
4. **FBX 才带命名材质，但匿名拿不到**：`/cdn/<id>.fbx` 一律 404，FBX 打包下载要免费账号（邮箱）。
5. 有 `params.json`：每个颜色区的 hex 默认值 + 预设 + 夜间自发光参数，**补材质可以脚本化**。

**结论**：2026-11-22 已按 CC BY 4.0（带署名）**正式引入 6 个道具**，用于视觉 pass v1：

- GLB 源文件入库在 `Assets/Polyfork/`（走 LFS），署名行在 [`Docs/Polyfork-CREDITS.md`](Polyfork-CREDITS.md)；
- `Tools/build_level.py` 里有一张 `PROPS` 表（id / 主色 / 粗糙度 / 金属度 / 摆放变换），
  **首次建关卡时自动导入**到 `/Game/Props/<id>/`，并按 `params.json` 的主色生成平涂材质 `M_Prop_<id>`
  （GLB 的顶点色 Interchange 读不到，必须自己补）；
- 导入后删掉 Interchange 顺带导进来的 `SkeletalMeshes`（树冠等骨骼件），否则一棵树多占 5 MB；
- 摆放：石狮夹山门台阶、四盏石灯笼（路口 + 台面）、多层塔在左、院落在右、青铜鼎在台面北侧、三棵枯枣树框住入口。
- 换资产只需改 `PROPS` 表 + 往 `Assets/Polyfork/` 放一个 GLB，`BuildLevel` 会自动导入并上材质。

## 视觉 pass v1（2026-11-22）

目标是"肉眼能看出变化"，做法全部在 `Tools/build_level.py` 里，可幂等重建。

**改了什么**：
- **锁定曝光**：`Config/DefaultEngine.ini` 的 `r.DefaultFeature.AutoExposure=False`。原来的自动曝光会让每次截图
  亮度都不一样，而且我一加灯它就把整帧追成白色（见 gotcha #36）。
- **两色照明**：暖白主光 + 冷蓝轮廓光（`forward_shading_priority=-1`，避免多平行光竞争，见 #37），
  山门两侧加暖色门灯、灵气环上加 4 盏青光点光。
- **后处理体积**（unbound）：bloom 0.8 / threshold 1.0、暗角 0.25、AO 0.8。**不覆盖曝光**。

**效果**：`Saved/Screenshots/visual_final.png`（改后）对比 `visual_before.png`（改前）——
门洞暖光池、灵气环冷光、立柱侧边有蓝色轮廓，天空与草地不再被洗白。

**过程教训（重要）**：纯靠无头截图盲调灯光会把画面越调越白，正确顺序是
①先锁曝光 → ②一次只改一个变量 → ③每步截图对比；真正的 look-dev 应该在编辑器视口里做。

**下一步（按收益排序）**：
1. ✅ **资产**（2026-11-22 完成）：6 个 Polyfork 中国风道具已进关卡，见上一节的管线说明；
2. **材质**：石台/玉石/灵气环的粗糙度与自发光再调，给地面加一点 color variation；
3. **色彩分级**：PPV 里加 saturation/contrast/temperature；
4. 天空换成黄昏或月夜（试过月夜，因为点光过曝退回；等资产与曝光经验更足再试）；
5. 树冠是骨骼件被丢掉了，现在是枯树——想要绿叶得换成 foliage 是静态网格的树种，或单独处理 SkinnedMesh。

## 地图分区与进度（2026-11-22）

世界结构：世界 → 大区（青云山）→ 场景（山门外景）→ 区域（zone）。P0 只做一张图、三个区域。

| 区域 | 范围 | 玩法动词 | 内容 | 状态 |
|---|---|---|---|---|
| **灵田村落** | x −2500..2500，y −5300..−3300 | 采 + 打 | 夯土街（7 块 4 m 砖）、12 块稻田、3 间夯土民居、酒肆、水井、10 段竹篱、2 只灵兽 | ✅ 2026-11-22 |
| **山门广场** | ±1500（30×30 m 台面） | 打 | 灵气环竞技场、石狮、石灯笼、玉柱门、2 灵兽 + 2 邪修 | ✅ 既有 |
| **后山道场** | x −1300..1300，y 3400..5400 | 探 + 打精英 | 2 m 石径 16 块、两侧石砌挡墙 10 段、三座石坛、钟楼、4 棵造型松、4 座坟冢、2 名邪修 | ✅ 2026-11-22 |

**村落细节（`Tools/build_level.py`）**：
- 街区用 `STREET_TILES`（7 块，间距 4 m）串起出生点与广场；`PADDY_TILES` 由坐标列表生成 12 块；
  `FENCE_RUNS` 沿街两侧各两段。
- 出生点移到村口 `(0, −5600)`，朝向广场；地面从 80 m 扩到 170 m 并把草地贴图 tiling 提到 75。
- 村里放 2 只灵兽（`SpiritBeast_Village_0/1`），离出生点约 2000 cm，走过去就会遭遇。

**道场细节（2026-11-22 完成）**：
- 石径 `SHRINE_PATH` 16 块（2 m/块）从广场北缘通到石坛；`SHRINE_WALLS` 只在两侧各 5 段矮挡墙——
  **别在路中间横着砌墙**，实测那样会把石径堵死、视野全被墙占满（试过 11 段横墙，画面很难看）。
- 三座石坛 `stone-altar` 呈品字形，钟楼 `tiered-bell-tower` 放在左后方 2300/5250 做远景剪影。
- 邪修从广场挪到道场（`EvilCultivator_0/1` 在 700/4600 与 −700/4850）：开阔广场不利于远程怪，
  道场有石坛、松树和坟冢做掩体。
- 三个区域全部站得住：村口一眼能看到村落、灵门与远处钟楼，`Frame 3.08 ms / GPU 3.24 ms / 266 draws / 262k tris`，171 actors。

## 画质目标与性能预算（2026-11-22 实测）

**机器**：RTX 5060 / i5-14600KF（14C20T）/ 48 GB。
**当前关卡实测**（1280×720，Lumen + VSM + TSR 100%）：`Frame 3.31 ms`、`Game 2.04 ms`、`GPU 2.72 ms`、
`Draws 165`、`Prims 110.4k`、`VRAM 588 MB`。**离 60 帧（16.6 ms）还有 5 倍余量**。

**目标档位：1080p / 60 fps / Lumen High**（不追 4K、不开硬件光追、不上 Nanite）：

| 指标 | 现在 | 上限 | 说明 |
|---|---|---|---|
| 分辨率 | 720p（截图） | 1920×1080 | 演示档基准 |
| 帧时间 | 3.31 ms | **≤ 16.6 ms** | 留 2.5× 给联机压力测试 |
| GPU | 2.72 ms @720p | **≤ 10 ms @1080p** | 1080p 像素 2.25×，约 6 ms |
| 游戏线程 | 2.04 ms | **≤ 8 ms**（20 假人） | M0.5 的瓶颈在 CPU/网络 |
| Draw calls | 165 | **≤ 1500** | 单个 draw ≈ 0.01–0.02 ms |
| 三角面 | 110k | **≤ 1.5M** | 低模场景可以很宽 |
| 显存 | 588 MB | **≤ 4 GB** | 8 GB 卡留一半 |
| 纹理 | 1k | 主城/主角 2k，普通 1k | 再高是浪费 |

**三档切换**：A 开发档（720p 窗口，≥200 fps）→ B 演示档（1080p，Lumen High，体素雾，2k 主纹理，60 fps）
→ C 压力档（M0.5：1080p + Lumen **Medium** + TSR 100%，客户端 ≥45 fps 即可）。

**怎么测**（每次加内容都跑一遍，30 秒）：

```powershell
powershell -ExecutionPolicy Bypass -File Tools\RunGame.ps1 -Seconds 18 -Sequence "T:1" -ExecCmds "stat unit" `
  -OutFile "Saved\Screenshots\perf.png"
# 打开 perf.png，右上角读 Frame / Game / GPU / Draws / Prims
```

**贴图现状（2026-11-22 晚）**：Megascans 表面已全部是 2K（Roof Tiles / Red Roof Tiles / Wood Planks /
Mossy Stone Walkway），`Get-ChildItem Content -Recurse -Filter "*_4K_*"` 为 0；苔石的源 PNG 放在
`Assets/Megascans/mossy_stone_walkway_2k/`，`build_level.py` 首次构建时导入，**重建不需要联网**
（Fab 插件下载的 zip 也还留在 `%LOCALAPPDATA%\Temp\FabLibrary`，见 gotcha #53）。
**仍未官方化**：墙面/夯土地面/泥土贴花用的是 CC0 `clay_plaster`（1K），是最后一个非 Megascans 表面。

**护栏**：
- Draws 破 1500 或 Frame 破 16 ms，先查"重复物件有没有用 HISM 实例化"（稻田砖、竹林、灯笼这类成片的）；
- 不做：Nanite（低模无收益）、硬件光追（直接砍半帧）、4K、8k 纹理、每道具独立材质；
- 内容增长按"每关 ≈ 5 倍当前密度"估算仍是安全的。

## 提交与推送策略

- **每步都 commit，按里程碑才 push**：小步（一个功能、一个 bug、一次文档整理）只提交本地；
  完成一个大迭代/里程碑（M0.3 收口、M0.4 收口…）再 `git push origin main`。
- 好处：远程历史每个点都是能跑的状态，不会被"改一半""跑挂了"的中间提交污染；
  本地可以随便试、随便改，回滚成本低。
- 想现在同步：`git push origin main`（LFS 对象自动跟随，本工程约 3 MB）。

## 编辑器会话（要不要一直开着？）

**默认不开。** 日常闭环完全不需要 GUI：`BuildAll.ps1` 编译 + 用 `build_level.py` 以 commandlet 生成关卡，
`RunTests.ps1` 跑逻辑测试，`RunGame.ps1` 截图验玩法。

需要开编辑器的场景只有三种：要用 MCP 工具（视口/资产/蓝图）、要手摆资产、要肉眼看光照氛围。这时的做法：

```powershell
# 开（带 MCP 服务端），做完就关；MCP 会话在重启后要在 DSH 里禁/启用 @local/unreal-mcp 重连
& 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe' `
  'C:\Users\tk\Desktop\lingxujie\LingXuJie.uproject' -ModelContextProtocolStartServer
```

为什么不让它常开：编辑器持有 Live Coding 互斥体，**只要它开着 `BuildAll` 就会失败**；
而本工程 95% 的活是 C++ + 数值/关卡脚本，等于让一个挡编译的进程占着资源。
另外同一工程开两个实例容易互相抢 `Saved/` 与资产锁。

`Tools\BuildAll.ps1` 现在会在检测到编辑器运行时先给出提示（构建失败时再补一句原因）；
`Tools\RunGame.ps1` 默认**不再杀**已存在的 UnrealEditor 进程（以前会误杀你开着的编辑器），
要清理残留实例请显式加 `-KillExisting`。

## 发布 / 推送

远程已接好。要换新仓库或第一次发布：

```powershell
powershell -ExecutionPolicy Bypass -File Tools\PublishRepo.ps1 -Url git@github.com:<user>/<repo>.git
powershell -ExecutionPolicy Bypass -File Tools\PublishRepo.ps1 -Token <pat> -Private   # 让脚本自己建仓库
powershell -ExecutionPolicy Bypass -File Tools\PublishRepo.ps1 -DryRun                 # 不联网预演
```

`PublishRepo.ps1` 会先检查：工作区必须干净、历史里不能有 >95 MB 的 blob、必须装了 git-lfs；
然后 `git remote add origin` + `git push -u origin main` + `git lfs push --all`。
