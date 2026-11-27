# 下一次会话从这里开始

> 写于 2026-11-22 第二次会话结束前。按顺序读这一页就能接上，不用翻聊天记录。


## 会话历史分卷

> 2026-11-27 起主文件只保留最近 15 节（第 67 节往前都在这几卷里）。
> 找旧决策先查这里，不要翻主文件。

| 卷 | 节 |
| --- | --- |
| [`NEXT-SESSION-001-020.md`](sessions/NEXT-SESSION-001-020.md) | 第 001–020 节 |
| [`NEXT-SESSION-021-040.md`](sessions/NEXT-SESSION-021-040.md) | 第 021–040 节 |
| [`NEXT-SESSION-041-060.md`](sessions/NEXT-SESSION-041-060.md) | 第 041–060 节 |
| [`NEXT-SESSION-061-066.md`](sessions/NEXT-SESSION-061-066.md) | 第 061–066 节 |

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
| ✅ `Docs/ASSETS.md` 已改成可执行的重建清单 | 兰州城那条链路已核实（`build_map_obj.py` → `build_moxiang_map.py`），见 `Docs/ASSETS.md` 第 2 节 |
| 剩余缺口：角色 glTF 批量导入 / Fab 包库名核实 / 每个包被谁用 | 都写在 `Docs/ASSETS.md` 第 7 节 |
| 删 `archive-lfs` 回收 5.5 GB | 确认旧历史不要了再动（`git branch -D archive-lfs` + `git lfs prune`） |
| 继续业务：工作方式第二块（动画接线 / NOT_SOLID 法线） | 备份这条线到此收口 |

## 82. 协作准备：会话记录分卷 + 一屏自检 + 验证纪律（2026-11-27 12:15）

### 一、三个问题（都是这轮实际遇到的）

| 问题 | 证据 |
| --- | --- |
| 会话记录太厚 | `NEXT-SESSION.md` **81 节 / 250 KB**，"读最大编号那节"要先 grep |
| 开工自检靠临时拼 | 这轮开场我自己写脚本查关卡/相机/actor 数/git 状态 |
| 步骤没有验证就不能算数 | 我以为 `main` 能推，被 `GH008` 打脸；`ASSETS` 清单里一度有"待核"当结论 |

### 二、做了什么

**1. 分卷（`Docs/sessions/`）**

```
主文件     67–81     15 节   1,341 行   （只留最近 15 节）
卷 001–020 20 节
卷 021–040 20 节
卷 041–060 20 节
卷 061–066  6 节
```

分卷脚本是临时件（`Saved/scratch/split_next_session.py`，不入库）；主文件顶部有分卷索引。

**2. `Tools/Status.ps1`（一屏自检，ASCII）**

```
== LingXuJie status ==
editor     : running (pid 4544)
mcp  :8000 : listening
guard      : CHECK: healthy
level      : /Game/Maps/LingXuJie  |  actors 116
camera     : 8950, -6200, 3900  yaw 0  pitch -2.0
             default view: yes
git        : main -> origin/main  ahead 0  behind 0  dirty 3
disk       : Saved 1,087.2 MB  |  screenshots 499  (cleanup trigger 1200 MB / 600)
```

**它自己判断相机是不是默认位** —— 规则 3b 从"我记得复位"变成"屏幕上写着 yes/no"。

**3. AGENTS 第 9 条加"验证纪律"**

> 写进文档 / 清单 / SOP 的操作步骤，后面必须跟一条**可复制的验证命令 + 期望输出**；
> 当时没验证的标 `⚠️ 未验证`。**没有验证的步骤等于没写。**

### 三、验证

- 分卷：`81 = 15 + 20 + 20 + 20 + 6`，章节号去重后仍是 1..81（脚本打印 "accounted sections: 81"）
- `Status.ps1`：实跑 exit 0，四行信息都对；`camera default view: yes`
- 分卷后 `Select-String '^## \d+\.'` 在五个文件里共 81 条，最小 1、最大 81

### 四、下一步

| 事项 | 说明 |
| --- | --- |
| 编辑器**租约文件**（多 agent 串行化） | 等真有两个 agent 同时干活再做；现在硬约束 3 够用 |
| `Docs/ASSETS.md` 三个缺口 | 角色 glTF 批量导入 / Fab 库名核实 / 每个包被谁用 |
| 回业务：动画接线 或 NOT_SOLID 法线 | 流程这条线可以收了 |

## 83. C++ 闭环自证：编译 → 测试 → PIE → 截图（2026-11-27 12:35）

### 一、结果（全部实测）

| 步 | 结果 |
| --- | --- |
| `BuildAll.ps1` 编译 | `Result: Succeeded`，退出码 **0** |
| 关卡生成 | `Done. 110 actors in /Game/Maps/LingXuJie` |
| `RunTests.ps1` | **completed=15 failed=0**，`ALL TESTS PASSED` |
| 重启编辑器 | `EditorGuard -Action restart -ApplyLayout` → MCP 2 秒内就绪、布局已应用 |
| PIE | `StartPIE` → `running=True`；日志 `Player ready at V(8950,-6200,3675)`；截到画面；`StopPIE` → `False` |

**证据**：`Saved\Logs\build.log`、`Saved\Logs\tests.log`、`Saved\proof_pie_player.png`（1180×688，
看得见替身角色站在广场上）。

### 二、两个发现（都比"编译通过"重要）

**① 重建会抹掉手动摆的 actor：116 → 110。**
`build_level.py` 是 `new_level` 全量重建，以下 6 个不属于生成流程的 actor 全没了：

```
MX_BOSS001_STATIC（刚修好材质的那个）  MX_BOSS001  MX_BOSSCOWF
MX_BIRD_TEST  MX_BOBU_TEST  MX_AMBIENT_MUSIC（背景音乐）
```

**→ 上一轮（第 78 节）的材质修复从**关卡**里消失**（脚本 `place_static_boss.py` 里还在，材质在资产上）。
**→ 这是硬缺口：手动摆的东西没有归属，每次重建都要人肉重跑 5 个脚本。**
（`place_static_boss.py` / `place_bird.py` / `place_bobu.py` / `place_character.py` / `add_level_music.py` 都在，
只是没人把它们串进 `BuildAll`。）

**② 输入注入仍不可用：按钮点不动，但 `WM_CLOSE` 有效。**
关编辑器时弹出「保存内容」对话框（脏的全是上一轮的实验室实验：`/Engine/BasicShapes/Cube` +
`/Game/Learning/` 的 4 个），`ui.ps1 -Action click` **点了没反应**；`PostMessage(WM_CLOSE)` 却有效
（对话框能关、编辑器能退出）。所以"先消息、后点击"的顺序是对的，**不要再指望点按钮**。
强杀进程后编辑器再启动会弹「恢复包」，`EditorGuard -Action dismiss` 一次就清掉。

### 三、相机的坑（gotcha #123）

`StopPIE` 之后编辑器相机被打到 `(3536, -8740, -25328)` —— 地底。已按规则 3b 复位，
`GetCameraTransform` 回读 `8950,-6200,3900 yaw 0 pitch -2`。**PIE 的调用里必须把复位写进去。**

### 四、下一步

| 事项 | 为什么排第一 |
| --- | --- |
| **写 `Tools/place_extras.py`，并挂到 `BuildAll` 末尾** | 补上"手动 actor 没有归属"这个缺口；一次调用放回 6 个，重建后不再丢 Boss 和背景音乐 |
| 然后领 T6（秦皇陵：Boss 石台 + 入口 + 1 只 Boss） | 纯内容，且正好用上刚补的摆位脚本 |
