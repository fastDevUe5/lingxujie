# UE5 知识库（项目内）

目的：把**官方文档 + 引擎源码 + 本工程实测**蒸馏成可检索、可复核的短笔记，
让任何 agent（包括几个月后的我）读一遍就达到同样的判断水平。

## 三条规则

1. **每条结论必须能追溯到出处**：官方文档 URL、引擎源码文件行号、或本工程的日志/退出码。三者冲突时**以源码和实测为准**。
2. **只写“能用的结论”**，不抄文档原文。笔记是决策依据，不是百科：`怎么用 + 什么时候别用 + 我们工程的取舍`。
3. **标注时效**：`引擎版本 + 核对日期 + 是否源码核对`。UE 每个小版本都会改 API，过期笔记比没有笔记更危险。
4. **官方文档默认展示最新版**（现在 5.9），查之前先确认版本选择器；和本机 5.8.4 有冲突时以源码为准，并把差异写进笔记（见 `unreal-mcp-practice.md` 的差异表）。

## 笔记模板

```markdown
# 主题（引擎 5.8.4｜核对 2026-11-17｜源码已核对 ✅）

## 一句话结论
（我们工程该怎么用）

## 关键事实
- 事实 1（出处：xxx.h:123 / 文档链接）
- 事实 2

## 我们工程的取舍
- 为什么不用官方推荐做法 / 为什么选这个方案

## 可复制片段
（C++ / Python / 命令行，能直接跑的那种）

## 反例与坑
- 别这样做……（会怎样）

## 待复核
- [ ] 升级 5.9 时确认 XXX 是否仍成立
```

## 分类与“何时读”

| 分类 | 内容 | 什么时候该读 |
| --- | --- | --- |
| A. 引擎机制 | Gameplay Framework 生命周期、UObject/GC、资源引用、模块与依赖、Config 层级 | 新写一个 Actor/Subsystem、遇到悬空指针、加新模块 |
| B. 编辑器自动化 | Python API 边界、MCP/Toolset 用法、资产导入与批处理、DataTable/DataAsset | 要批量改资产、要脚本生成内容、要 agent 操作编辑器 |
| C. 构建与发布 | UBT 参数、Live Coding、Cook/打包、DDC、CI | 构建失败、打包失败、启动慢、准备发版 |
| D. 渲染与性能 | Lumen/Nanite/VSM/TSR 取舍、Unreal Insights、性能预算 | 画面不对、帧率不够、要定画质档位 |

## 清单（✅ 已完成 / ⬜ 待写）

| 优先级 | 主题 | 主要问题 | 状态 |
| --- | --- | --- | --- |
| P0 | [Gameplay Framework 生命周期](gameplay-framework-lifecycle.md) | BeginPlay/StartPlay/PostLogin 顺序、Pawn 与 HUD 何时生成 | ✅ 5.8.4 源码核对 |
| P0 | [编辑器 Python 的能力边界](editor-python-boundaries.md) | 哪些能建、哪些必须走 C++、属性命名规律 | ✅ 本工程实测 |
| P0 | [Unreal MCP 实操](unreal-mcp-practice.md) | tool search 模式、call_tool 套用、会话失效、视口截图 | ✅ 本工程实测 |
| P0 | [用 MCP 写 Blueprint 图](blueprint-authoring-via-mcp.md) | 建图/连线/编译/PIE 验证，本地化 type_id 的坑 | ✅ 2026-11-19 实测 |
| P1 | 构建与打包 | UBT 参数、Live Coding 互斥、BuildCookRun 两步法、产物结构 | ⬜（素材已有：`Docs/UE5-Gotchas.md` 4/5 条 + `Tools/Package.ps1`） |
| P1 | 渲染开关决策表 | Lumen/Nanite/VSM/TSR 各自代价、什么时候关 | ⬜ |
| P2 | 资产管线 | 导入设置、LOD/Nanite、材质实例、命名与 LFS | ⬜ |
| P2 | 性能基线 | Insights 抓取、帧预算、常见瓶颈 | ⬜ |

> 已有素材：`Docs/UE5-Gotchas.md`（15 条实测）+ `AGENTS.md`（工程约定）。知识库不重复它们，只做**成体系的解释与决策**。

## 写入流程

1. 抓官方文档（优先 `dev.epicgames.com/documentation` 的 5.8 版本页）与 API 参考；
2. 到本机 `Engine/Source` 核对关键签名/默认值；
3. 在本工程跑一次最小验证（能编译、能出日志）；
4. 按模板写笔记，标注核对状态；
5. 在 `AGENTS.md` 的“何时读”里挂一行，确保下一个 agent 找得到。
