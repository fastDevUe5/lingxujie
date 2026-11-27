# 本地 UE 官方文档

> **目的：把课程要查的官方文档搬到本地，减少来回翻网页。**
> **只搬运，不改编** —— 原文照录，出处写在每篇开头。
>
> **最后更新：2026-11-27 · 实测 69 篇手册（47 真文章）+ 164 篇已验证 API**

---

## 一、总数

| 目录 | 内容 | 大小 |
| --- | --- | --- |
| **`Docs/UEManual/`** | **69 篇**（47 真文章 + 22 索引页）| 950.4 KB |
| **`Docs/PythonAPI/`** | **164 篇 `.txt`，全部验证有页面头** | 1486.4 KB |

> **⚠️ `PythonAPI` 是 `.txt` 不是 `.md`。** 用 `glob("*.md")` 找会以为它是空的。

**判定标准：**
- **真文章** = 至少 40 行非空 + 4000 字符
- **索引页** = 只列子主题链接，单看学不到东西

---

## 二、按模块

### 渲染 / 几何 —— 7 篇（6 真文章）/ 198.2 KB

| 文件 | 内容 | 大小 | 类型 |
| --- | --- | --- | --- |
| `temporal-super-resolution.md` | TSR 时序超分 | 84.4 KB | 文章 |
| `virtual-shadow-maps.md` | 虚拟阴影贴图 | 43.2 KB | 文章 |
| `nanite-technical.md` | Nanite 技术细节 | 26.1 KB | 文章 |
| `fbx-static-mesh.md` | FBX 静态网格管线 | 16.0 KB | 文章 |
| `nanite.md` | Nanite 概述 | 14.9 KB | 文章 |
| `static-mesh-lod.md` | LOD 自动生成 | 8.7 KB | 文章 |
| `import-static-meshes.md` | 导入静态网格 | 4.9 KB | **索引页** |

### 渲染 / 光照 —— 9 篇（6 真文章）/ 142.2 KB

| 文件 | 内容 | 大小 | 类型 |
| --- | --- | --- | --- |
| `sky-atmosphere.md` | 天空大气 | 27.2 KB | 文章 |
| `lumen-technical.md` | Lumen 技术细节 | 25.1 KB | 文章 |
| `reflections-captures.md` | 反射捕获 | 19.7 KB | 文章 |
| `post-process-materials.md` | 后处理材质 | 18.3 KB | 文章 |
| `directional-lights.md` | 定向光 | 18.0 KB | 文章 |
| `lumen-performance.md` | Lumen 性能指南 | 17.7 KB | 文章 |
| `reflections.md` | 反射概述 | 6.6 KB | **索引页** |
| `light-types.md` | 光源类型 | 5.4 KB | **索引页** |
| `lighting-environment.md` | 环境光照 | 4.2 KB | **索引页** |

### 材质 —— 6 篇（3 真文章）/ 64.0 KB

| 文件 | 内容 | 大小 | 类型 |
| --- | --- | --- | --- |
| `texture-asset-editor.md` | 贴图资产编辑器 | 29.8 KB | 文章 |
| `instanced-materials.md` | 实例化材质 | 9.5 KB | **索引页** |
| `material-editor-guide.md` | 材质编辑器指南 | 7.6 KB | 文章 |
| `material-expressions.md` | 材质表达式参考 | 7.6 KB | 文章 |
| `materials.md` | 材质概述 | 5.9 KB | **索引页** |
| `textures.md` | 贴图概述 | 3.5 KB | **索引页** |

### 世界 —— 10 篇（7 真文章）/ 97.7 KB

| 文件 | 内容 | 大小 | 类型 |
| --- | --- | --- | --- |
| `water-bodies.md` | 水体 Actor | 27.6 KB | 文章 |
| `world-partition.md` | World Partition | 19.2 KB | 文章 |
| `foliage.md` | 植被模式 | 12.8 KB | 文章 |
| `landscape-technical.md` | Landscape 技术指南 | 10.5 KB | 文章 |
| `navigation-mesh.md` | 导航网格 | 7.6 KB | 文章 |
| `collision.md` | 碰撞概述 | 7.0 KB | 文章 |
| `navigation-basic.md` | 基础寻路 | 6.9 KB | 文章 |
| `navigation.md` | 导航概述 | 2.9 KB | **索引页** |
| `water.md` | 水体概述 | 2.6 KB | **索引页** |
| `landscape.md` | Landscape 概述 | 0.6 KB | **索引页** |

### 动画 —— 8 篇（4 真文章）/ 56.3 KB

| 文件 | 内容 | 大小 | 类型 |
| --- | --- | --- | --- |
| `sequencer-editor.md` | Sequencer 编辑器 | 14.1 KB | 文章 |
| `state-machines.md` | 动画状态机 | 11.9 KB | 文章 |
| `control-rig-editor.md` | Control Rig 编辑器 | 11.2 KB | 文章 |
| `animation-editors.md` | 动画编辑器 | 9.1 KB | 文章 |
| `control-rig.md` | Control Rig 概述 | 3.4 KB | **索引页** |
| `animation-blueprints.md` | 动画蓝图 | 2.6 KB | **索引页** |
| `skeletal-animation.md` | 骨骼动画系统 | 2.1 KB | **索引页** |
| `sequencer.md` | Sequencer 概述 | 1.9 KB | **索引页** |

### 模拟 —— 5 篇（3 真文章）/ 53.0 KB

| 文件 | 内容 | 大小 | 类型 |
| --- | --- | --- | --- |
| `chaos-fracture.md` | Chaos 破裂 | 19.3 KB | 文章 |
| `physics.md` | 物理 | 15.6 KB | 文章 |
| `niagara-overview.md` | Niagara 概述 | 14.4 KB | 文章 |
| `niagara.md` | Niagara 概述页 | 3.2 KB | **索引页** |
| `chaos-destruction.md` | Chaos 破坏 | 0.6 KB | **索引页** |

### 玩法与系统 —— 5 篇（4 真文章）/ 81.4 KB

| 文件 | 内容 | 大小 | 类型 |
| --- | --- | --- | --- |
| `enhanced-input.md` | 增强输入 | 24.6 KB | 文章 |
| `blueprints.md` | 蓝图 | 21.1 KB | 文章 |
| `umg-quick-start.md` | UMG 快速入门 | 14.4 KB | 文章 |
| `game-mode.md` | Game Mode 与 Game State | 11.9 KB | 文章 |
| `gameplay-framework.md` | Gameplay 框架 | 9.4 KB | **索引页** |

### 音频 / 网络 / 性能 —— 6 篇（3 真文章）/ 89.5 KB

| 文件 | 内容 | 大小 | 类型 |
| --- | --- | --- | --- |
| `sound-cue-reference.md` | Sound Cue 参考 | 40.1 KB | 文章 |
| `networking.md` | 网络 | 23.4 KB | 文章 |
| `performance.md` | 性能分析 | 16.0 KB | 文章 |
| `audio.md` | 音频概述 | 5.7 KB | **索引页** |
| `sound-cue-editor.md` | Sound Cue 编辑器 | 3.7 KB | **索引页** |
| `attenuation.md` | 声音衰减 | 0.6 KB | **索引页** |

### 编辑器与脚本 —— 6 篇（6 真文章）/ 106.6 KB

| 文件 | 内容 | 大小 | 类型 |
| --- | --- | --- | --- |
| `python-scripting.md` | Python 脚本 | 32.0 KB | 文章 |
| `unreal-mcp.md` | Unreal MCP | 30.9 KB | 文章 |
| `command-line-arguments.md` | 命令行参数 | 14.2 KB | 文章 |
| `asset-management.md` | 资产管理 | 14.0 KB | 文章 |
| `python-with-ai-agents.md` | Python + AI Agent | 7.9 KB | 文章 |
| `level-editor.md` | 关卡编辑器 | 7.6 KB | 文章 |

### 本项目专用（跨领域但项目直接用） —— 6 篇（5 真文章）/ 59.0 KB

| 文件 | 内容 | 大小 | 类型 |
| --- | --- | --- | --- |
| `hlod.md` | HLOD 层级 LOD | 13.6 KB | 文章 |
| `savegame.md` | 存档 | 12.0 KB | 文章 |
| `insights.md` | Unreal Insights | 11.1 KB | 文章 |
| `geometry-scripting.md` | 几何脚本（程序化网格） | 10.3 KB | 文章 |
| `data-tables.md` | 数据表 | 8.6 KB | 文章 |
| `user-interfaces-huds.md` | UI 与 HUD（Canvas） | 3.3 KB | **索引页** |

### 未归类

- `niagara-modules.md` 2.5 KB

---

## 三、🔴 判断「有没有抓到」的正确方法

**文档站对**任何路径**都返回 HTTP 200**，包括不存在的：

```
this-page-does-not-exist-at-all-xyz  ->  200  没有 <title>  body 很短
lumen-technical-details-...         ->  200  有 <title>Lumen Technical Details</title>
```

**→ 判据只能是**有没有 `<title>`**，不能看状态码。**
`Tools/verify_curriculum_slugs.py` 内置负对照。

---

## 四、🔴 三个用错过的判据

| # | 错的判据 | 为什么错 | 改成什么 |
| --- | --- | --- | --- |
| 1 | `read(4000)` 后按状态码判成功 | 4000 是**截断长度**，不是页面大小 | 看 `<title>` + 负对照 |
| 2 | 「`-`/`|` 开头行占比高 = 索引页」 | 抓取时 `<li>` 全被转成 `\n- `，任何列表页面都像索引 | **只看行数与字符数** |
| 3 | 审计脚本的分组清单写死 | 加了新文章它还在看旧的索引页，一直报 uncovered | 分组清单**同时列出索引页和文章页** |

**共同点：判据没跟上数据。每次改完数据都要重跑 `audit_manual_gaps.py` 核实。**

---

## 五、还没做到的

| 项 | 现状 |
| --- | --- |
| **Python API 覆盖** | **190 / 约 11,459 类 = 1.7%**（**按需子集**，不是缺口）|
| **音频** | 2 篇且都偏薄（`audio` 5736 字符 / `sound-cue-editor` 3749）|
| **索引页** | 22 篇只有子主题链接，需要时按需补子页面 |
| **整站** | 未镜像，估数十小时且随版本漂移 |

---

## 六、为什么不全站镜像

| 项 | 数字 |
| --- | --- |
| 单页抓取 | 约 1–10 秒 |
| 全量估算 | 数十小时 |
| **本目录** | **69 篇 / 950 KB** |

**→ 覆盖课程要查的九个领域，不是整站。**

---

## 七、权威顺序

```
① 本机 Engine/Source 源码          ← 最权威
② Docs/PythonAPI/（官方签名）      ← C++ 给不了的 Python 名字
③ Docs/UEManual/（官方手册）        ← 概念与用法
④ 实测                            ← 前三者都没有时
```

---

## 八、怎么更新

```powershell
python Tools/verify_curriculum_slugs.py   # 1. 验证 slug，打印 PAGES
# 2. 加进 Tools/mirror_manual_pages.py
python Tools/mirror_manual_pages.py       # 3. 抓取（幂等）
python Tools/audit_manual_gaps.py         # 4. 覆盖率与缺口
python Tools/rewrite_local_docs.py        # 5. 重生本文档
```

**⚠️ 不要再猜 slug。** 猜的结果是 12 篇空页，花了两轮才修好。

---

## 九、🔴 API 镜像的两次误判（2026-11-27）

**第一次：** 我说「190 篇 Python API 都在」，**从没验过内容**。
打开 `AnimationBlueprintLibrary.txt` 才发现是 404 页面。

**第二次：** 审计时用了 `MIN_BYTES = 1500` 的下限，把 55 篇判为「可疑」。
**抽查发现它们全是有效的** —— 一个没有方法的结构体只有 285 字节，那就是全部内容。

**正确判据：看文件是否以 `# unreal.<名字>  (UE 5.8 Python API)` 开头。**

```
审计结果
  189 篇
  有效 164（87%）
  404   25
```

**处理：删掉 25 个 404 文件** —— 它们比缺失更糟，因为**看起来有覆盖**。
**现在 164 篇，100% 有页面头。**

**⚠️ 那 25 个名字在文档站确实找不到**（`class/` `struct/` `enum/` `type/` 四种路径全试过），
API 索引页也是 JS 渲染抓不到。**可能本来就不作为 Python API 页存在。**

**规律：**
| 判据 | 对不对 |
| --- | --- |
| 文件数 | ❌ 只说明文件存在 |
| 字节数下限 | ❌ 简单类型天生就短 |
| **页面头** | ✅ |
