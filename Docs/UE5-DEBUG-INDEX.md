# UE5 调试与问题定位 · 系列索引

> **🔴 出问题时先看 `UE5-DEBUG-PLAYBOOK.md` —— 症状 → 该查什么。**
>
> **📋 要看整段学下来做到了什么、还差什么：`UE5-DEBUG-SUMMARY.md`。**

> **目标：把「调试」从"看日志猜"变成"读源码知道机制，再按机制定位"。**
>
> **每一篇都必须：读本机 `Engine/Source` 核实 → 在本项目实操 → 记录结论与**更正**。**
>
> **依据：UE 5.8.4 本机源码 · 项目：灵虚界**

---

## 一、进度

| # | 主题 | 文档 | 状态 |
| --- | --- | --- | --- |
| **1** | **日志与断言体系** | `UE5-DEBUG-LOGGING.md` | ✅ **已完成** |
| **2** | **断言（check/verify/ensure）** | `UE5-DEBUG-ASSERTS.md` | ✅ **已完成** |
| **3** | **崩溃 / 调用栈 / 崩溃上下文** | **`UE5-DEBUG-CRASH.md`** | ✅ **已完成** |
| **4** | **性能剖析（stat / 帧预算）** | **`UE5-DEBUG-PERF.md`** | ✅ **已完成** |
| **5** | **内存与泄漏（memreport / obj cycles）** | **`UE5-DEBUG-MEMORY.md`** | ✅ **已完成** |
| **6** | **渲染调试（缓冲可视化 / vis）** | **`UE5-DEBUG-RENDER.md`** | ✅ **已完成** |
| **7** | **蓝图与脚本调试** | **`UE5-DEBUG-SCRIPT.md`** | ✅ **已完成** |
| **8** | **网络调试**（**源码为主，本项目无网络未实测**）| **`UE5-DEBUG-NET.md`** | ⚠️ **已完成（未实测）** |
| **9** | **资产与加载问题** | **`UE5-DEBUG-ASSET.md`** | ✅ **已完成** |

---

## 二、已经确立的核心结论（速查）

### 2.1 日志

| 结论 | 依据 |
| --- | --- |
| 8 个级别 + 2 个**非级别标志位**（`SetColor=0x40`、`BreakOnLog=0x80`）| `LogVerbosity.h` |
| 打印需过**两道编译期 + 一道运行期**闸门 | `LogMacros.h` 240-255 |
| `COMPILED_IN_MINIMUM_VERBOSITY` 默认 `VeryVerbose`（全保留）| `LogMacros.h` 93-99 |
| **→ 「Verbose 不见了」多半是**运行期**，不是编译期** | 同上 |
| `log <Cat> Break` 是**切换**，不是设为开 | `LogSuppressionInterface.cpp` 308-310 |
| **运行期改级别会在会话内静默持续** | 本项目实测 |
| **引擎只在级别**调高**时告发，调低**无记录** | `LogSuppressionInterface.cpp` 345-349 |
| **崩溃上下文的 `PCallStack` 才带偏移，`CallStack` 只有模块名** | `GenericPlatformCrashContext.cpp` 1208 |

**排查「日志没出来」的顺序：**
1. `log list <类别>` —— 看当前级别（最常见原因）
2. 看 `DECLARE_LOG_CATEGORY_EXTERN` 的 `CompileTimeVerbosity`
3. `Verbose`(6) 在 `Log`(5) 默认下**必然不打印**
4. **`Log` 级别只写文件不写控制台** —— 控制台看不到 ≠ 没打

### 2.2 断言

| 宏 | 编辑器 | 打包版默认 | 求值副作用 | 中止 | 报告频率 |
| --- | --- | --- | --- | --- | --- |
| `check` | 中断 | **可能不求值** | ❌ | ✅ | 每次 |
| `verify` | 中断 | 求值但不检查 | ✅ | ✅（Dev）| 每次 |
| `ensure` | 日志+断点 | 不报告 | ✅ | ❌ | **同一行一次** |
| `ensureAlways` | 日志+断点 | 不报告 | ✅ | ❌ | 每次 |

**规则：`check` 的表达式只能是**纯判断**；带副作用一律 `verify`。**
**依据：打包版 `check(expr)` 展开成 `CA_ASSUME(expr)`，不求值。**

**⚠️ `ensure` 同一行只报一次 —— 第一次没看到就永远不会再出现。**

---

## 三、本项目已发现的真实问题

| # | 问题 | 依据 | 状态 |
| --- | --- | --- | --- |
| 1 | **全部日志打在 `LogTemp`**，没有专用类别 | grep `UE_LOG(LogTemp` | 未修（用户要求先学习）|
| 2 | **`LXJCharacter.cpp:182` 的 `Verbose` 日志从来不会打印** | `LogTemp` 默认 `Log`(5) < `Verbose`(6) | 未修 |
| 3 | **全项目零断言**（0 处 `check`/`verify`/`ensure`）| grep | 空白 |
| 4 | **没定义 `USE_CHECKS_IN_SHIPPING`** | `Target.cs` 无定义 | 打包版不检查 |

---

## 四、可复现脚本

| 脚本 | 作用 |
| --- | --- |
| `Tools/practice_log_commands.py` | 跑 `log list` / 改级别 / 切换 Break |
| `Tools/verify_verbosity_gate.py` | 四步读回级别，证明运行期闸门 |

---

## 五、学习方式（自我要求）

**每一篇都必须做到四件事：**

1. **读源码** —— 结论要能指到具体文件和行号
2. **实操** —— 在本项目上复现，不只看文档
3. **记录更正** —— 之前哪条结论错了，写清楚错在哪
4. **给排查清单** —— 让人能照着做，而不是只描述原理

**⚠️ 已经抓到的自我错误（本系列第 1-2 篇）：**
- 以为「打包后 Verbose 被编译掉」→ 实际默认 `COMPILED_IN_MINIMUM_VERBOSITY = VeryVerbose`，是运行期问题

## 六、八个域全部完成（第 6 轮收口）

| # | 域 | 文档 | 实测程度 |
| --- | --- | --- | --- |
| 1 | 日志与断言 | `UE5-DEBUG-LOGGING.md` + `UE5-DEBUG-ASSERTS.md` | ✅ 全部实测 |
| 2 | 崩溃与调用栈 | `UE5-DEBUG-CRASH.md` | ✅ 用本项目真实崩溃 |
| 3 | 性能剖析 | `UE5-DEBUG-PERF.md` | ✅ 部分（stat 面板抓不到）|
| 4 | 内存与泄漏 | `UE5-DEBUG-MEMORY.md` | ✅ 全部实测 |
| 5 | 渲染调试 | `UE5-DEBUG-RENDER.md` | ✅ 含像素级 A/B |
| 6 | 蓝图与脚本 | `UE5-DEBUG-SCRIPT.md` | ✅ 故意失败实测 |
| 7 | 网络调试 | `UE5-DEBUG-NET.md` | ⚠️ **源码为主，未实测** |
| 8 | 资产与加载 | `UE5-DEBUG-ASSET.md` | ✅ 用本项目真实日志 |

**八个域覆盖完毕。下一步该做的是**实战演练** ——
找一个项目里的真实问题，用这九篇的方法从头定位，而不是继续写文档。**

## 七、实战诊断记录（八域完成之后）

| 案例 | 文档 | 结论 |
| --- | --- | --- |
| **Boss 动画不播放** | **`UE5-DEBUG-CASE-ANIM.md`** | **`import_and_place.py` 从未设 `animation_mode`，也从未赋 `anim_to_play`** |
| **SM_Boss001 退化法线** | **`UE5-DEBUG-CASE-NORMALS.md`** | **`TRANSFORM_TYPE_NOT_SOLID (0x10)` 的几何本来就没有可用法线；导出器当正常数据导出了** |
| **Boss 模型散开** | **`UE5-DEBUG-CASE-IBM.md`** | **逆绑定矩阵转置了两次：平移从 12/13/14 槽跑到 3/7/11，glTF 读到全零 → 骨骼塌缩到原点** |
| **材质缺失（真假各一）** | **`UE5-DEBUG-CASE-MATERIAL.md`** | **「101 个 Nanite 网格缺材质」是误报（98 个有组件 override）；真缺陷是 `MX_BOSS001_STATIC` 一个** |
| **无害警告 + 被推翻的假设** | **`UE5-DEBUG-CASE-WARNING.md`** | **`Invalid animation skeleton` 是清空动画时的正常提示；「赋值顺序很重要」的假设经实测否决** |
| **引擎测试噪音** | **`UE5-DEBUG-CASE-TESTNOISE.md`** | **13 条 `Condition failed` 来自引擎 `UnifiedErrorTests.cpp`；项目自己的 15 个测试全过** |
| **历史警告 vs 当前状态** | **`UE5-DEBUG-CASE-MIP.md`** | **「贴图无 mip」是 DDS 导入失败的残留；实测 `NumMips=10` 完整，资产健康** |
| **材质修复的视觉验证** | **`UE5-DEBUG-CASE-MATFIX.md`** | **赋 `M_Boss_Mob01` 后生物从灰变红棕；同一次改动全画面 0.99% / 猜错区域 8.8% / 正确区域 24%** |

**这次实战更正了两条既有结论（两条都是同一毛病）：**
- **`set_position` 会重新求值** —— 之前以为不会，是因为**根本没有动画被赋值**
- **`get_bone_transform` 能读骨骼** —— 之前用 `AnimPoseExtensions.get_bone_pose` 挂死，误判为「读不到」

> **共同点：把「我用这个方法失败了」当成「这件事做不到」。**

## 八、可复用的体检工具

| 工具 | 覆盖 | 用法 |
| --- | --- | --- |
| **`Tools/diagnose.py`** | 资产/引用/骨骼/动画/内存/配置 | **`py Tools/diagnose.py`** |

**第一次跑就抓到全部已知缺陷：4 个骨骼角色**同时**中了「骨骼塌缩」和「没有动画」两个 bug。**

**文档：`UE5-DEBUG-TOOLKIT.md`（含它能查什么、查不出什么）。**

## 九、症状手册（七次实战提炼）

**`UE5-DEBUG-PLAYBOOK.md` 是**决策索引**，不是知识文档：左边是现象，右边是该查什么。**

| 类别 | 覆盖 |
| --- | --- |
| 模型看起来不对 | 散开 / 躺地 / 100 倍大小 / 黑块 / 灰格 |
| 动画不动 | 没赋值 / 模式错 / 改位置没反应 |
| 日志 Error/Warning | 6 种常见文本 → 该查什么 |
| 性能 | 30fps 显示绿 / 平均好看但有卡顿 / CVar 没效果 |
| 内存 | 环数 ≠ 泄漏 / 对象为何不销毁 |
| 渲染 | 缓冲可视化只有 UI / `vis` 拼错名字静默 |
| 脚本 | 没输出 / 异常定位 / 对话框卡死 |
| 崩溃 | `PCallStack` 不是 `CallStack` |

**第五节是七次实战里犯过的**五种推理错误**及各自的防法。**
