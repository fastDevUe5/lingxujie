# UE5 学习索引 —— 唯一入口

> **这个文件的目的：让人（或下一个 agent）在 30 秒内找到"该读哪一篇"，而不是翻十个文档。**
>
> **新会话第一件事读这个，不要凭记忆。**

---

## 〇、先读总览

| 你要做什么 | 读哪个 | 关键结论 |
| --- | --- | --- |
| **只想看一次收口的总览** | **`Docs/UE5-KNOWLEDGE-SUMMARY.md`** | **31 篇文档地图 + 已掌握结论速查 + 已验证/未验证清单 + 104 条坑分类** |
| **要知道墨香管道做到哪了** | **`Docs/BATCH-EXPORT-STATUS.md`** | **2,407 个 PNG / 253 个 glTF / 98.5% 模型有贴图** |
| **🐛 要调试 / 定位问题** | **`Docs/UE5-DEBUG-INDEX.md`** | **调试系列入口；每篇都从 `Engine/Source` 核实机制** |
| **🎨 动手调渲染参数 / 判断开关有没有效果** | **`Docs/UE5-RENDER-HANDSON.md`** | **官方素材练手场 + A/B 方法 + 噪音地板 + 像素差实测表** |

**`UE5-KNOWLEDGE-SUMMARY.md` 是第 36 轮生成的**总览**：
它把 18 篇引擎知识 + 5 篇格式逆向 + 2 篇工程状态收成一份，
并明确列出**哪些结论已验证、哪些未验证** —— 不要跳过「未验证」那张表。**

## 〇之二、调试系列（进行中）

**当前重点：把「调试」从看日志猜，变成读源码知道机制再定位。**

| 主题 | 文档 | 状态 |
| --- | --- | --- |
| **日志体系** | **`Docs/UE5-DEBUG-LOGGING.md`** | ✅ 已完成 |
| **断言（check/verify/ensure）** | **`Docs/UE5-DEBUG-ASSERTS.md`** | ✅ 已完成 |
| **崩溃与调用栈** | **`Docs/UE5-DEBUG-CRASH.md`** | ✅ 已完成 |
| **性能剖析** | **`Docs/UE5-DEBUG-PERF.md`** | ✅ 已完成 |
| **内存与泄漏** | **`Docs/UE5-DEBUG-MEMORY.md`** | ✅ 已完成 |
| **渲染调试** | **`Docs/UE5-DEBUG-RENDER.md`** | ✅ 已完成 |
| **蓝图与脚本调试** | **`Docs/UE5-DEBUG-SCRIPT.md`** | ✅ 已完成 |
| **网络调试** ⚠️ | **`Docs/UE5-DEBUG-NET.md`** | ⚠️ 源码核实，**未实测**（本项目无网络）|
| **资产与加载** | **`Docs/UE5-DEBUG-ASSET.md`** | ✅ 已完成 |
| **🔧 体检工具** | **`Docs/UE5-DEBUG-TOOLKIT.md`** | ✅ 已完成 |
| **🩺 症状手册** | **`Docs/UE5-DEBUG-PLAYBOOK.md`** | ✅ **出问题先看这份** |
| **📋 调试总结** | **`Docs/UE5-DEBUG-SUMMARY.md`** | ✅ 17 轮到什么程度、还差什么 |

**七个实战案例：**

| 案例 | 文档 | 性质 |
| --- | --- | --- |
| Boss 动画不播放 | `UE5-DEBUG-CASE-ANIM.md` | ✅ 真缺陷（脚本没赋值）|
| SM_Boss001 退化法线 | `UE5-DEBUG-CASE-NORMALS.md` | ✅ 真缺陷（NOT_SOLID 无语义法线）|
| Boss 模型散开 | `UE5-DEBUG-CASE-IBM.md` | ✅ 真缺陷（IBM 转置两次 + 单位）|
| 材质缺失 | `UE5-DEBUG-CASE-MATERIAL.md` | ⚠️ 误报 + 1 个真 |
| Invalid animation skeleton | `UE5-DEBUG-CASE-WARNING.md` | ✅ 无害（我自己恢复动作触发）|
| 13 条测试失败 | `UE5-DEBUG-CASE-TESTNOISE.md` | ✅ 引擎噪音（项目 15/15 过）|
| 贴图无 mip | `UE5-DEBUG-CASE-MIP.md` | ✅ 历史残留（实测 10 级完整）|
| 材质修复验证 | `UE5-DEBUG-CASE-MATFIX.md` | ✅ **视觉验证：24% 像素变化，画面可见** |

**⚠️ 七个里只有三个真缺陷。这个比例本身是结论：日志里的「问题」大多数不是当前问题。**

**三条已确立的速查结论：**
- **`Log` 级别只写日志文件、不写控制台** —— 控制台看不到 ≠ 没打
- **`check(expr)` 在打包版里可能不求值表达式** —— 带副作用必须用 `verify`
- **`ensure` 同一行只报一次** —— 第一次没看到就永远消失
- **`stat unit` 是 0.9/0.1 的 EMA 平滑值** —— 单帧卡顿会被稀释，要用 `stat unitmax`
- **`CaptureViewport` 抓不到 `stat` 面板** —— 它不含 Canvas/HUD 层，`bShowUI` 两种都试过
- **引擎默认 `t.TargetFrameTimeThreshold = 33.9 ms`（30 fps）** —— 不是 16.6，项目目标 60 fps 时要改
- **`memreport` 延迟到帧末执行（先强制 GC）** —— 输出在 `Saved/Profiling/MemReports/`，不在控制台
- **`obj cycles` 报环数 ≠ 泄漏数** —— 必须看环里是谁；本项目 29 个环内对象全是引擎 World/Level
- **`obj refs name=<对象>` 是回答「为什么没被销毁」的唯一可靠办法**
- **`vis <RDG资源名>` 是控制台命令，能改场景渲染；缓冲可视化切换只有菜单** —— `vis help` 是权威语法
- **`vis pool` 列的是运行时渲染目标，不是资产** —— 和 `obj list`/`memreport` 量的不是同一样东西
- **改渲染能被截图抓到（16.7% 像素差），改 Canvas 覆盖层抓不到（0%）** —— 决定验证方式
- **Python 异常永远打不垮编辑器**（实测连炸 4 次全程 healthy）—— 「脚本报错」和「编辑器崩了」是两件事
- **蓝图 runaway 循环抛异常时会弹模态对话框** —— 自动化环境里会卡死（`bp.ScriptRecurseLimit=120`、循环上限 100 万）
- **语法错误在日志里打两遍**（插件一次 + stderr 重定向一次）—— 重复不代表跑了两次
- **`could not be found in the Asset Registry` 几乎总是路径猜错了** —— 用 `get_assets_by_path` 按名字搜，不要手写 `/Game/...`
- **`/Game` 2194 个资产但 `/Game/Moxiang` 只有 370** —— 「项目有 N 个资产」的分母容易搞错
- **`/Game/Moxiang` 有 99 个 Texture2D，不是 1 个** —— 之前只查了 `Textures` 子目录就下结论，分母搞错
- **`mesh_flag & 0xF0` 的四种 TRANSFORM_TYPE**：`0x00` SOLID / `0x10` NOT_SOLID / `0x30` ALIGN_VIEW / `0x50` ILLUSION —— **后三者的法线数据不可信**
- **「有没有法线」和「法线能不能用」是两件事** —— 客户端读了 NOT_SOLID 的法线但不用
- **IBM 要修两处**：槽位顺序（3/7/11 → 12/13/14）**加**平移乘 0.01（厘米转米） —— 只修第一处会得到放大 100 倍的模型
- **小物体的像素差要按物体区域算** —— 同一改动全画面 0.99% / 正确区域 24%；先看图定位变化，再框区域算数字
- **`listtextures <名字>` 有 `NumMips` 列** —— Python 读不到贴图 mip，只能靠这条控制台命令
- **日志告诉你发生过什么，不告诉你现在是什么** —— 旧警告必须用当前实测去否定
- **日志里的字符串在源码里一定存在** —— 拿日志行去源码搜，是区分引擎噪音和项目失败最快的办法
- **`RunTests.ps1` 用独立无头进程**，不碰运行中的编辑器；`RunGame.ps1` 才会 `Stop-Process`
- **清空 `anim_to_play` 会打 `Invalid animation skeleton`** —— 合法操作，引擎只是提示，不必追
- **读一段源码得出「必须这样」，可能忽略了同文件的另一条路径** —— 顺序假设就是这样被推翻的
- **结论与观察矛盾时，先信观察** —— 「101 个网格都用默认材质」但画面有贴图，一查发现 98 个靠组件 override；这是第四次同型误报被直觉拦住
- **验证必须用独立读取者** —— 「自己算 IBM 再逆回去」误差 2e-16 也证明不了字节顺序对；要用 glTF 规范位置读回来
- **包围盒正常 ≠ 模型正确** —— 它只量顶点，不量矩阵和绑定姿态
- **退化数据（全零/全同）比错误数据更危险** —— 它「看起来没坏」；67 根骨骼全在同一位置就是这样
- **StaticMesh 的 LOD 数是 `get_num_lods`**，且 **Python 读不到 StaticMesh 的法线** —— 要量就去源文件量
- **Cooker 靠引用图找资产，硬编码路径它看不见** —— 编辑器能跑、打包后静默失败的头号原因
- **敲一个 CVar 名字：有 `= value` 才存在，只有 `Cmd:` 就是不存在** —— 通用判据
- **`net PktLag` / `PktDup` / `PktOrder` 有互斥** —— `PktOrder` 优先，`PktDup` 不能和 `PktLag` 同用，设了会静默失效
- **网络模拟设置存全局、跨 PIE 重启残留** —— 排查「PIE 有延迟」先检查这个（本项目无 NetDriver，未实测）
- **渲染 A/B 的第一件事是量噪音地板** —— 控制组 23% 时，任何"改动效果"都没有意义（`UE5-RENDER-HANDSON.md`）
- **「改了没反应」有三层：旋钮不存在 / 没生效 / 生效但看不出** —— 三层要分开证（gotcha #113）
- **`r.LumenScene.Radiosity.Enable`、`r.LumenScene.Visualize` 不存在** —— 真名 `r.LumenScene.Radiosity`、`r.Lumen.Visualize`
- **编辑器 Python 的 `time.sleep` 阻塞游戏线程** —— 循环抓图只有最后一张会落盘（gotcha #114）
- **CVar 是全局的，换关卡不重置** —— "重载一下就好了"在这一层是错的（gotcha #112）
- **材质槽有两层：资产槽 + 组件 override，组件赢** —— 只改资产槽会得到"改了没反应"（gotcha #116）
- **一次 `execute_tool_script` 调用 = 查槽 + 赋材质 + 两张截图**（7 秒）—— 沙箱里 `try/except` 抓不住工具报错，参数必须先问清楚（#117/#118，`UE5-WORKFLOW-FIX.md` 第八节）

---


## 〇之三、实操学习系列（进行中）

**按本地官方文档逐块学，每块都必须在项目上实测。**

| 主题 | 文档 | 状态 |
| --- | --- | --- |
| **Lumen 第一块** | **`Docs/UE5-LEARN-LUMEN-01.md`** | ✅ 配置实测 + 图集数据 + 关 GI 量出 37.84% 像素变化 |
| **Lumen 第二块** | **`Docs/UE5-LEARN-LUMEN-02.md`** | ✅ 源码判定骨骼网格有 Card；发现官方文档限制清单不完整 |
| **Lumen 第三块** | **`Docs/UE5-LEARN-LUMEN-03.md`** | ✅ 量出 4 个网格薄于 10 cm（1 个 0.0）；漏光实验**失败**并写明原因 |
| **Lumen 第四块** | **`Docs/UE5-LEARN-LUMEN-04.md`** | ✅ **搭出可控练习关卡**；10 cm 天花板漏光、60 cm 不漏，实验成功 |
| **Lumen 第五块** | **`Docs/UE5-LEARN-LUMEN-05.md`** | 🔴 **更正**：练习关卡零距离场，测的是阴影穿透不是 GI 漏光 |
| **Lumen 第六块** | **`Docs/UE5-LEARN-LUMEN-06.md`** | ✅ 发现距离场是**流式**的；用有 DF 的 7.6 cm 网格证明薄面漏光（78.49% 像素变化）|
| **动画第一块** | **`Docs/UE5-LEARN-ANIM-01.md`** | ✅ 单节点 API 全摸清；🔴 编辑器里姿态刷不动（需 tick，属性不可改）；**发现 API 镜像 190 篇只有 110 可用** |
| **物理第一块** | **`Docs/UE5-LEARN-PHYS-01.md`** | ✅ **实测球落下 275 cm 并静止**；🔴 发现 `time.sleep()` 会冻住世界，这是之前所有失败的根因 |
| **物理第二块** | **`Docs/UE5-LEARN-PHYS-02.md`** | 🔴 **推翻**「球会滚」：立方体比球漂得远（83 vs 20 cm）；✅ **阻尼把漂移降到 0** |
| **Niagara 第一块** | **`Docs/UE5-LEARN-NIAGARA-01.md`** | 🔴 项目**零** Niagara 资产、Python**无**系统工厂；✅ 遗留 Cascade 粒子实测 40→39 存活；截图失败（白盒子）|
| **材质第一块** | **`Docs/UE5-LEARN-MAT-01.md`** | ✅ **从零建材质并贴到 6 个面，盒子从白变黑（画面证明）**；顺手修好白盒子问题 |
| **材质第二块** | **`Docs/UE5-LEARN-MAT-02.md`** | ✅ **参数化材质 + 两个实例，一张图看出参数差异**；🔴 `set_..._scalar_parameter_value` 返回 False 但值生效 |
| **材质第三块** | **`Docs/UE5-LEARN-MAT-03.md`** | ✅ **Nanite override 源码→实测→画面全链条**；搞清材质解析三层优先级；项目 0/60 材质用了 override |
| **UI/UMG 第一块** | **`Docs/UE5-LEARN-UI-01.md`** | 🔴 **负面结论**：只通第 1 环（建资产）；树不可访问、面板无构造方法、`construct` 后仍 0×0、`add_to_viewport` 无效（PIE 亦同）|
| **网络第一块** | **`Docs/UE5-LEARN-NET-01.md`** | 🔴 **更正**：复制层在跑（`net.ActorReport` 报 5 个复制 actor）；传输层无 NetDriver，源码解释 `net.SimulateConnections` 静默原因 |
| **打包与优化第一块** | **`Docs/UE5-LEARN-PKG-01.md`** | ✅ **帧时间终于量出来**（GameThread 8.863 ms）：发现 `stat dump*` 写日志；⚠️ 打包需关编辑器（Live Coding 互斥体），未做 |
| **打包与优化第二块** | **`Docs/UE5-LEARN-PKG-02.md`** | 🔴 **失败实验的结论**：编辑器 PIE 帧时间被**睡眠主导**（8.36ms 里 7.94ms 是 Stall），Lumen 开关差 0.024ms 被淹没；判据是看 Stall 占比 |
| **🎯 完整场景第一块** | **`Docs/UE5-LEARN-SCENE-01.md`** | ✅ **用官方素材搭出并调优完整场景**（8 actor：日/天空/天光/云/雾/地面/出生点/后处理）；🔴 `AEM_MANUAL` 不给值会黑屏（亮度 0.7 → 140.6）|
| **🎯 完整场景第二块** | **`Docs/UE5-LEARN-SCENE-02.md`** | ✅ 加 6 个形体构图；**户外关掉 Lumen 有 20.45% 像素变化** —— 和第 19 轮室内「测不出来」形成对照 |
| **🎯 完整场景第三块** | **`Docs/UE5-LEARN-SCENE-03.md`** | ✅ **从 PlayerStart 验证构图，三次迭代才成**；🔴 相机 yaw0 朝 +X 时画面**宽沿 Y 轴**（我搞错两次）|
| **🎯 完整场景第四块** | **`Docs/UE5-LEARN-SCENE-04.md`** | ✅ **begin_play 游戏态验证**（PlayerController/Pawn/HUD/GameMode 全在）；量出 14 actor 场景：FrameTime 10.73ms / 工作 0.469ms |
| **📋 阶段总结** | **`Docs/UE5-LEARN-SUMMARY.md`** | 22 篇 / 28 条更正；**目标终点已达成**，但 69 篇只覆盖约 17% |
| **补读-1 Nanite 技术** | **`Docs/UE5-LEARN-READ-NANITE.md`** | ✅ 文档给的 12B/16B 经源码核实；默认 16M/4M = **256 MB**；引擎溢出会自动告警，**本项目从未触发** |
| **补读-2 Nanite 概述 + 噪声排查** | **`Docs/UE5-LEARN-READ-NANITE2.md`** | 🔴 **推翻 SCENE-02**：噪声底 5.4-7.7%(云在动)；藏云后 **Lumen 实际只差 0.18%**，20.45% 是云 |
| **补读-3 A/B 标准流程** | **`Docs/UE5-LEARN-READ-AB.md`** | ✅ 关云后底噪 **0.62%**，Nanite 开关差异 **46.37%**（75×底噪）；引擎报 **VSM 非Nanite队列溢出** |
| **补读-4 虚拟阴影贴图** | **`Docs/UE5-LEARN-READ-VSM.md`** | ✅ VSM 有**五种**溢出（源码核实）；只有 MARKING_JOB_QUEUE 只影响性能；「尽量让几何是 Nanite」；页池 4096 页 |
| **补读-5 天空大气** | **`Docs/UE5-LEARN-READ-SKY.md`** | ✅ 四组散射配置实测：Rayleigh×4.5 让日落更红(194/154/140)；Mie×12.5 变灰(165/152/165)；Mie 本身就是高度雾 |
| **补读-6 太阳高度扫描** | **`Docs/UE5-LEARN-READ-SUN.md`** | ✅ 五个点单调：R−B 从 −18.4(-5°) 到 −74.4(-60°)；真正自变量是太阳高度，Rayleigh 只是放大器 |
| **补读-7 方向光** | **`Docs/UE5-LEARN-READ-LIGHT.md`** | ✅ 强度单位是 **lux**，我设的 8 lux 比室内还暗；曝光适应只有 **8.06 档(267倍)**，8→100000 是 13.61 档 → 过曝 |
| **补读-8 后处理材质** | **`Docs/UE5-LEARN-READ-PP.md`** | ✅ **全 Python 从零建后处理材质**（M_PPDesat）并生效：饱和度 52.68→0.05，97.57%像素变；`WeightedBlendable.material` 实际叫 **object** |
| **补读-9 TSR** | **`Docs/UE5-LEARN-READ-TSR.md`** | ✅ 25% 屏幕百分比（1/16 像素）重建画面接近原生；🔴 TSR 之后的 pass 跑**显示分辨率**（隐藏代价，量不到）；梯度指标对 TSR 无效 |
| **补读-10 反射与捕获** | **`Docs/UE5-LEARN-READ-REF.md`** | ✅ 源码枚举证实：**只有 `EReflectionMethod::None` 才用反射捕获**，Lumen 模式接管全部；本项目 0 个探针（干净） |
| **补读-11 贴图** | **`Docs/UE5-LEARN-READ-TEX.md`** | 🎯 审 813 张贴图查出 **1 张违规**：`T_GCM_Ceiling_BC` 3489×4096(奇数) → 压缩/mip/流式**全失效**，白占 ~55MB；**未修改**（导入素材，改会动画面）|
| **补读-13 植被与地形** | **`Docs/UE5-LEARN-READ-WORLD.md`** | ✅ 高度图公式 `A×Quads+1`（总为 2^n+1）+ 11 行推荐尺寸表 + **Z 轴常数 0.001953125**（验算通过）；🔴 项目**无 Landscape 无 Foliage**（用自建 LXJGround，放弃分块 LOD/流式）|
| **补读-15 LOD/HLOD** | **`Docs/UE5-LEARN-READ-LOD.md`** | 🔴 **差点误报**：610 资产中 143 个「单LOD+无Nanite」，但**关卡实际放置 99 个网格里 0 个违规** → 审计口径必须是「屏幕上有什么」不是「库房里有什么」|
| **补读-17 World Partition + 资产管理** | **`Docs/UE5-LEARN-READ-WP.md`** | ✅ WP 本质是**单关卡内切网格**（Cell 256m / Loading Range 768m），PlayerController 即流源，打包**必须 cook commandlet**；🔴 项目**两条都没走**（无 WP、无 PrimaryAsset），对 116 actor 规模合理但有天花板 |
| **补读-19 碰撞与物理** | **`Docs/UE5-LEARN-READ-PHYS2.md`** | ✅ 物理材质 18 个默认值全枚举：**restitution 默认 0.3**（不是 0）、`static_friction 0.0` vs `friction 0.7`（反直觉）；🔴 弹跳实验**失败**（`phys_material_override` 属性名不存在，第 8 次猜名字）|
| **补读-21 导航** | **`Docs/UE5-LEARN-READ-NAV.md`** | 🔴 **项目零导航**（无 RecastNavMesh / 无 BoundsVolume / 无配置）；源码确认怪物用 `AddMovementInput(Direction,1.f)` **直线走、不绕障**（全项目 0 处 AIController/MoveToLocation）|
| **补读-23 游戏框架** | **`Docs/UE5-LEARN-READ-GM.md`** | ✅ `AGameModeBase`（单机）vs `AGameMode`（多人 match state）的分界；玩家进入链路 `InitGame→PreLogin→PostLogin→HandleStartingNewPlayer→RestartPlayer→SpawnDefaultPawn`；**项目选对了 Base**，配置链 ini→GameMode→pawn/HUD |
| **补读-25 增强输入** | **`Docs/UE5-LEARN-READ-INPUT.md`** | 🔴 四概念（Action/Context/Modifier/Trigger）；**项目零 Input 资产**，源码用 `PC->IsInputKeyDown(EKeys::W)` **逐帧硬轮询**（比 BindAxis 还原始），按键全硬编码 → 无重绑定/无手柄/无触发器 |
| **补读-27 Enhanced Input 实操** | **`Docs/UE5-LEARN-READ-INPUT2.md`** | ✅ **从 0 打通**：`create_asset(...,None)` 无工厂也能建资产；`unreal.Key()` 不能传参只能设 `key_name=Name("SpaceBar")`；建成 `IA_LabJump` + `IMC_Lab` + 1 条按键映射并保存，**完整配方可复用** |
| **补读-29 Python 脚本** | **`Docs/UE5-LEARN-READ-PY.md`** | 🔴 **我漏了三个 API**：`ScopedEditorTransaction`（撤销分组，我 60+ 轮都没用过）、`ScopedSlowTask`（进度条，我跑过 6 分钟阻塞脚本）、`unreal.Vector` 运算符；文档那句「UI becomes blocked」解释了本系列多起「控制台没反应」|
| **补读-31 Unreal MCP** | **`Docs/UE5-LEARN-READ-MCP.md`** | 🔴 MCP 工具调用跑在**游戏线程**且一次一个；客户端**约 120 秒超时**，文档明写 split into shorter calls（我靠试错才发现）；Tool Search 默认开启，`tools/list` 只返回 4 个元工具 |
| **补读-33 数据表与存档** | **`Docs/UE5-LEARN-READ-DATA.md`** | ✅ DataTable 从 CSV 导入、价值在「策划能改」；`AsyncSaveGameToSlot` 是推荐方式；🔴 项目**刻意**不用 DataTable（LXJItems.h 注释：可单测 + 关卡生成不用建资产），且**完全没有存档系统** |
| **补读-35 蓝图** | **`Docs/UE5-LEARN-READ-BP.md`** | ✅ 五种类型（Class/Level/Interface/FunctionLibrary/MacroLibrary），Level Blueprint 每关卡都有；🔴 项目 7 个蓝图资产但**关卡里零个实例**，核心理由：蓝图逻辑无法用 Python 生成 |
| **补读-37 Geometry Scripting** | **`Docs/UE5-LEARN-READ-GS.md`** | ✅ 流程 DynamicMesh→Append→Boolean→Bake，文档明说也有 **Python 函数**（275 个属性可用）；🔴 补读-35 的缺口有答案：**关卡没有 LevelScriptActor**（无 Level Blueprint 逻辑）；关卡构成 98 静态网格 + 6 光源 + 4 骨骼 |骼 |
| **补读-39 Geometry Scripting 实操** | **`Docs/UE5-LEARN-READ-GS2.md`** | ✅ **函数在 DynamicMesh 上**，46 个图元全枚举；实测 append_box 得 **8 顶点 12 三角形**；🔴 **没有 bake 方法** → 几何在内存里出不成资产 |
| **补读-41 Sequencer 与 Control Rig** | **`Docs/UE5-LEARN-READ-SEQ.md`** | ✅ 两篇都是**界面导览**；Synchronous Scrubbing 逐帧对齐、Control Rig 有 Python Context；🔴 项目 **50 骨骼 : 7 动画**，零 LevelSequence / 零 ControlRig / 零 AnimMontage → 动画域弱的根因是没内容 |
| **补读-43 Chaos 碎裂** | **`Docs/UE5-LEARN-READ-CHAOS.md`** | ✅ 八种碎裂工具（Uniform/Voronoi、Cluster、Radial、Planar、Slice、Brick、Mesh、Custom），前提是 GeometryCollection；🔴 项目零资产且 FractureSettings 未暴露（切不了）；骨骼资产真相 **70 网格 / 50 骨骼 / 7 动画 / 28 物理** |
| **补读-45 音频** | **`Docs/UE5-LEARN-READ-AUDIO.md`** | ✅ 三个引擎（SoundCue=遗留 / **MetaSounds**=现代 / Quartz），20+ 节点清单；🔴 项目有 2 音波 + 5 SoundClass + 1 衰减，但**源码 0 处音频代码** → 资产从未被播放 |
| **补读-47 收口索引页 + 水体** | **`Docs/UE5-LEARN-READ-MISC.md`** | ✅ 五种水体(Ocean/Lake/River/Custom/Island)但 **Water 可选插件未启用**；材质实例必须先在父材质里**参数化**（我 MAT-02 已做对）；剩下 7 篇中 6 篇索引 + 1 篇 0.6KB 纯占位 |
| **补读-49 收尾 + 22工具集发现** | **`Docs/UE5-LEARN-READ-FINAL.md`** | 🔴🔴 **本系列最大发现**：MCP 有 **22 个工具集**，我只用了 3 个；有 ObjectTools 可查 API（我一直在猜）、ProgrammaticToolset 沙箱编排、LogsToolset 、AutomationTestToolset、BlueprintTools |
| **打包与优化第三块** | **`Docs/UE5-LEARN-PKG-03.md`** | 🔴 **GPU 耗时读不到**：`stat gpu` 不写日志，`r.GPUStats.Enabled`/`r.GPUCapture` 都不存在；CPU 和 GPU 走两套统计系统 |

## 一、按问题查（最常用）

| 你要做什么 | 读哪个 | 关键结论 |
| --- | --- | --- |
| **查某个 UE API 的签名** | `Docs/PythonAPI/<类名>.txt`（191 篇） | 官方 5.8 页，本地镜像 |
| **API 到底有多少、该学哪些** | **`Docs/UE5-API-INVENTORY.md`** | **实测 11,459 类 / 330,365 方法；本项目只需 ~870** |
| **搞清楚 Actor / Component / Pawn 是什么** | **`Docs/UE5-CORE-ARCHITECTURE.md`** | 继承链 + 生命周期 + Gameplay 五类 |
| **这段代码该放哪（子系统四层）** | **`Docs/UE5-SUBSYSTEMS.md`** | 按寿命选层 + 三个判断问题 |
| **物体没碰撞 / 射线打不中** | **`Docs/UE5-COLLISION.md`** | Enabled / 通道 / Response 三组正交 |
| **物体不会掉 / 没有物理仿真** | **`Docs/UE5-PHYSICS.md`** | 查询 vs 仿真两半分；**本项目零仿真** |
| **Nanite、后处理、材质设置** | **`Docs/UE5-RENDERING.md`** | 两套 Nanite 结构 + 351 个后处理字段 |
| **Lumen 全局光照 / 为什么光照好看** | **`Docs/UE5-LUMEN.md`** | **本项目已开 Lumen**；前提是距离场 |
| **这个工程到底开了哪些设置** | **`Docs/UE5-PROJECT-CONFIG.md`** | **92 个配置键一张表，先查这里** |
| **材质 / 引脚连不上 / 地面网格感** | **`Docs/UE5-MATERIALS.md`** | **先查引脚再连**；网格感真因是 64×64 贴图 |
| **动画怎么播 / 蒙太奇 / 状态机** | **`Docs/UE5-ANIMATION-RUNTIME.md`** | 槽位机制 + Notify 对应墨香特效脚本 |
| **想知道引擎有什么现成工具** | **`Docs/UE-TOOLSET-MAP.md`** | **217 个工具，先查再写** |
| **写自定义 MCP 工具** | `Docs/UE5-OFFICIAL-REFERENCE.md` 第三节 | 5.8 与 5.9 文档有**三处差异** |
| **移编辑器视口相机** | `Docs/UE5-OFFICIAL-REFERENCE.md` 第四节 | `set_level_viewport_camera_info`，**不是 CaptureViewport** |
| **跑 Python 脚本** | `Docs/UE5-OFFICIAL-REFERENCE.md` 第五节 | 控制台三模式都不解决抢焦点 |
| **导入动画** | **`Docs/ANM-TO-ENGINE-PLAN.md`** | **走 glTF 不走 FBX**；`import_asset(factory=None)` |
| **动画引擎内部怎么存/写** | **`Docs/UE5-ANIMATION-ENGINE.md`** | DataModel + Controller 各 42 方法；**完整写入配方** |
| **`.anm` 格式** | 研究区 `anm-rotation-solved.md` | 24 字节 = 单位四元数 |
| **批量导出 / 成功率 / 下一步** | **`Docs/BATCH-EXPORT-STATUS.md`** | **100/100 导出成功**；`.chx` 才是正确配对来源 |
| **人形角色导入进度 / 两个坑** | **`Docs/CHARACTER-IMPORT-STATUS.md`** | **多网格 + 顶点不在原点** |
| **墨香 → UE 完整管道** | **`Docs/MOXIANG-TO-UE-PIPELINE.md`** | **网格+动画四资产全通**；五种格式对照表 |
| **`.anm` 动画格式 / 帧率** | **`Docs/ANM-FORMAT-SOLVED.md`** | **帧率 30 fps（ticks/4800 推导）** |
| **`.mod` → UE 骨骼网格** | **`Docs/MOD-TO-UE-PIPELINE.md`** | **全链路跑通**；import_file 不认 glTF |
| **`.mod` 网格/蒙皮格式** | **`Docs/MOD-FORMAT-SOLVED.md`** | **已完全解开**；四文件逐字节验证（tail=0）|
| **逆向格式从哪开始** | **gotcha #81** | **先读研究区的客户端 C++ 源码** |
| **音频导入与播放** | **`Docs/UE5-AUDIO.md`** | **实测通过**：wav→SoundWave→播放；rotation 必需 |
| **UI / UMG / 为什么 Python 做不了** | **`Docs/UE5-UI.md`** | **实测边界**：类型有、连接没有 |
| **网络 / 复制 / 和墨香服务端的区别** | **`Docs/UE5-NETWORKING.md`** | 三行声明 + **UE 复制 ≠ 墨香协议** |
| **玩家从出生到能操作的 14 步** | **\Docs/UE5-GAMEPLAY-FLOW.md\** | 顺序 + 每类可重写的钩子 |
| **输入系统 / 为什么改键做不到** | **\Docs/UE5-INPUT.md\** | 三代方案 + **本项目用第一代** |
| **合并网格 / 减少 actor** | **`Docs/UE5-MESH-MERGE.md`** | **合并减 actor 不减 draw call** |
| **找不到 API 时怎么办** | **`Docs/UE5-MESH-MERGE.md` 第六节** | **读引擎自带工具的实现** |
| **资产引用 / 加载 / 遗留清理** | **`Docs/UE5-ASSET-PIPELINE.md`** | 硬引用 vs 软引用 + **实测引用链** |
| **踩过的坑** | `Docs/UE5-Gotchas.md`（70 条） | 遇到怪事先搜这里 |
| **🔄 要查官方文档** | **`Docs/LOCAL-UE-DOCS.md`** | **本地已有 52 篇手册 + 190 篇 API，先查这里** |

---

## 二、五份核心文档的分工

| 文档 | 回答什么 | 什么时候读 |
| --- | --- | --- |
| **`UE5-CORE-ARCHITECTURE.md`** | **对象模型、继承链、生命周期、Gameplay 五类** | 搞清楚"这是什么" |
| **`UE5-SUBSYSTEMS.md`** | **子系统四层、代码该放哪** | 写新系统之前 |
| **`UE5-RENDERING.md`** | **Nanite 两套结构、后处理、观感问题归因** | 画面不对时 |
| **`UE5-COLLISION.md`** | **碰撞三组正交概念、CTF 怎么选** | 碰撞不生效时 |
| **`UE-TOOLSET-MAP.md`** | **引擎已经有什么工具** | **动手写代码之前，永远先读** |
| `UE5-OFFICIAL-REFERENCE.md` | 能力地图 + API 出处 + 工具集写法 | 要调编辑器、要写工具 |
| `ANM-TO-ENGINE-PLAN.md` | **`.anm` 怎么进引擎（glTF 方案）** | 做动画导入 |
| `UE5-ANIMATION-ENGINE.md` | **引擎内部数据结构 + C++ 写入配方** | 写导入器 / 排查轨道丢失 |
| `MOD-SKIN-STATUS.md` | `.mod` 蒙皮进度（未解完） | 做网格导入 |
| `UE5-ANIMATION.md` | 动画系统可达边界 | 理解为什么不能直接写 |
| `UE5-Gotchas.md` | 哪里会炸、怎么炸（70 条） | 出问题时 |
| **`LOCAL-UE-DOCS.md`** | **本地官方文档：52 篇手册 / 730 KB** | **先查这里，别再抓网页** |

---

## 三、"不遗忘"靠什么保证

**光写文档不够 —— 文档写在没人读的地方等于没写。**

**三道机制：**

| 机制 | 位置 | 作用 |
| --- | --- | --- |
| **① `AGENTS.md` 开工流程** | 工程根 | **强制**新会话按顺序读 |
| **② 本索引** | 这里 | 30 秒定位到具体篇 |
| **③ 每篇开头写"结论先行"** | 各文档首段 | 只读一段也有用 |

**判断标准：如果新会话读完 `AGENTS.md` + 本索引，仍不知道该读哪篇 —— 是索引没写好，不是读者的问题。**

---

## 四、已掌握结论清单（可当速查表用）

### 4.1 编辑器与工具

| 结论 | 出处 |
| --- | --- |
| 5.8.4 有 **22 个工具集、217 个工具** | 实测 `list_toolsets` |
| **5.8.4 没有 `PythonScriptingTools`**（那是 5.9） | 实测 `ExecutePythonScript` = Unknown tool |
| 自建工具集可用，但 `tool_call` **不接受 `mode`** | 踩过，报 `no attribute ToolAccessMode` |
| 返回类型必须写 **`list[str]`**，不能只写 `list` | 踩过，报 `missing specification for contained type` |
| **`SetCameraTransform`** 移相机；**`CaptureViewport`** 只拍一张 | 踩过两次 |
| `SetCameraTransform` 参数是 **`{location, rotation:{pitch,yaw,roll}}`**，非四元数 | 踩过，传四元数相机跳到原点 |
| 控制台三种模式（Cmd/Python/REPL）**都不解决抢焦点** | 实测 |

### 4.2 动画

| 结论 | 出处 |
| --- | --- |
| **写动画轨道 Python 做不到** | `IAnimationDataController` 在 Developer 模块，BlueprintCallable = 0 |
| **读动画轨道可以** | `AnimationBlueprintLibrary.GetRawTrack*`，69 个 BlueprintCallable |
| **导入走 glTF 不走 FBX** | glTF 是 JSON 可直接写；FBX 需 Autodesk SDK |
| **glTF 的 `EPath` 正好对应三条轨道** | 引擎源码 `GLTFAnimation.h`：`Translation / Rotation / Scale` |
| **`import_asset(factory=None)` 走 Interchange** | `asset.py` 注释原文 |
| `.anm` 24 字节节 = **单位四元数 + 填充 0** | 656/656 验证 |

### 4.3 墨香数据（研究区）

| 结论 | 出处 |
| --- | --- |
| **兰州 = 地图 17** | `MapKindInfo.bin` 完整地图名表 |
| 建筑 OBJ 的 **Y 会被 UE 取反** | 踩过两次 |
| 兰州 1,563 个建筑网格 / 96 个材质组 | 已导入 |

---

## 五、坐标系与常量速查

```
墨香世界：51,200 cm 见方（512 m），1 格 = 100 cm
地形高度：513 × 513 浮点
建筑 OBJ：Y 为正 → UE 导入后 Y 为负
兰州密集区：X 0–10,000 / Y -20,000–0
兰州广场（默认视口）：(8950, -6200, 3900) yaw 0 pitch -2
人物参考高度：约 180 cm（角色类用圆柱+球，约 2 m）
```

---

## 六、怎么扩充这份索引

**学到新东西时，按这个顺序：**

```
1. 结论写进对应专题文档（UE5-ANIMATION / UE5-GOTCHAS / ...）
2. 在本文第四节点清单里加一行（结论 + 出处）
3. 如果是"新类别"，在第一节加一行"要做什么 → 读哪篇"
```

**不要只写在对话里 —— 上下文会被压缩，只有文件留下的东西不丢。**
