# UE5 调试 · 十：可复用的体检工具

> **前九篇讲机制，三个实战案例讲方法。这一篇是**把方法固化下来**。**
>
> **`Tools/diagnose.py` 一次跑完八个域的常规检查，
> 把「要出问题时才发现」变成「跑一次就知道」。**
>
> **日期：2026-11-26 · UE 5.8.4**

---

## 一、为什么需要它

**十一轮调试写了 20 多个一次性脚本：
`diag_anim_step1..3`、`diag_normals_*`、`diag_scatter_step2..6` ……**

**每个只回答一个问题，只回答一次。**

**→ 下次同类问题再来，还得从头写。
→ 修复有没有生效，只能等它再出问题才知道。**

**这个工具解决的是**第二类**问题：让回归可见。**

---

## 二、它查什么

```
py "Tools/diagnose.py"                 # 完整检查（含骨骼）
py "Tools/diagnose.py --noskeletal"    # 跳过骨骼（大关卡用）
```

| 域 | 检查项 | 对应文档 |
| --- | --- | --- |
| **资产** | `/Game` 与 `/Game/Moxiang` 的资产数、按类统计 | `UE5-DEBUG-ASSET.md` |
| **引用** | 所有 StaticMesh / SkeletalMesh 引用是否可解析 | 同上 |
| **骨骼** | **骨骼跨度是否塌缩（< 1 cm）或异常（> 2000 cm）** | `UE5-DEBUG-CASE-IBM.md` |
| **动画** | **`anim_to_play` 是否为空、`animation_mode` 是什么** | `UE5-DEBUG-CASE-ANIM.md` |
| **内存** | `obj cycles` 的引用环 | `UE5-DEBUG-MEMORY.md` |
| **配置** | 帧预算、GI 方式、抗锯齿、虚拟阴影等关键 CVar | `UE5-DEBUG-PERF.md` |

---

## 三、第一次跑就抓到全部已知缺陷（✅ 实测）

```
DIAG: --- sweep start (skeletal=True) ---
DIAG: === assets ===
DIAG:   /Game                2194 asset(s)
DIAG:   /Game/Moxiang         370 asset(s)
DIAG:     MaterialInstanceConstant      135
DIAG:     StaticMesh                    101
DIAG:     Texture2D                      99
DIAG:     Material                        7
DIAG:     PhysicsAsset                    5
DIAG:     Skeleton                        5
DIAG:     SkeletalMesh                    5
DIAG:     SoundClass                      5
DIAG:     AnimSequence                    4
DIAG:     SoundWave                       2
DIAG: === level ===
DIAG:   actors: 116
DIAG:     COLLAPSED skeleton on MX_BIRD_TEST: span 0.00 cm
DIAG:     MX_BIRD_TEST           no animation assigned (mode='ANIMATION_BLUEPRINT: 0>')
DIAG:     COLLAPSED skeleton on MX_BOBU_TEST: span 0.00 cm
DIAG:     MX_BOBU_TEST           no animation assigned (mode='ANIMATION_BLUEPRINT: 0>')
DIAG:     COLLAPSED skeleton on MX_BOSSCOWF:  span 0.00 cm
DIAG:     MX_BOSSCOWF            no animation assigned (mode='ANIMATION_BLUEPRINT: 0>')
DIAG:     COLLAPSED skeleton on MX_BOSS001:   span 0.00 cm
DIAG:     MX_BOSS001             no animation assigned (mode='ANIMATION_BLUEPRINT: 0>')
DIAG:   mesh references checked: 103, missing: 0
DIAG:   collapsed skeletons: 4
DIAG: --- sweep done ---
```

### 3.1 它当场证明了什么

**① 案例 001 和案例 003 的缺陷**不是 Boss 独有** —— 4 个骨骼角色**全部**同时中招。**

**② 「骨骼塌缩」和「没有动画」是两个**独立**的缺陷，但**总是同时出现**，
因为都源于同一个脚本的遗漏。**

**③ 引用完整性没问题**（103 个 mesh 引用，0 缺失）—— 所以问题不在资产路径。**

---

## 四、🔴 它同时纠正了我一个错误结论

**上一轮（资产篇）我写：**
> **「`Textures` 只有 1 个资产，贴图基本没导入 UE」**

**体检发现：`Texture2D` 有 **99** 个。**

**→ 我当时查的是 `/Game/Moxiang/Textures` 目录（那里面确实只有 1 个），
但 99 张贴图分散在**其他子目录**里（角色导入目录自带贴图）。**

**⚠️ 这正是我自己在资产篇里警告过的「分母陷阱」：

> **「项目有 N 个资产」这个说法的分母必须说清是哪个路径。**

**而我警告完就自己掉进去了。**

**→ 体检工具的价值之一，就是它按**类**统计而不是按**目录**，天然避开这个陷阱。**

---

## 五、设计原则

**① 只报告，不修复。**

**→ 会自动修的体检工具没人敢信。它改了什么你不知道。**

**② 阈值来自实测，不是拍的。**

| 判据 | 阈值 | 依据 |
| --- | --- | --- |
| 骨骼塌缩 | **跨度 < 1 cm** | 案例 003 实测跨度恰好 0.00 |
| 骨骼异常 | **跨度 > 2000 cm** | 案例 003 修一半是 39738 cm，正常约 400 cm |
| 缺失引用 | 资产路径不可解析 | 103 个引用全过 |

**③ 输出用统一前缀 `[LingXuJie] DIAG:`。**

**→ 可以用 `-WaitPattern 'DIAG: --- sweep done'` 判断它跑完了。**
**→ 这本身就是 `UE5-DEBUG-SCRIPT.md` 里的方法。**

**④ `--noskeletal` 能跳过慢的部分。**

**→ 大关卡先跑快的，确认没大问题再跑全的。**

---

## 六、它查不出什么（**必须说清**）

| 查不出 | 为什么 | 要靠什么 |
| --- | --- | --- |
| **法线质量** | Python 读不到 StaticMesh 法线 | 查 glTF 源文件（案例 002）|
| **材质是否正确** | 只能看槽位赋了没有 | 人眼看 + 缓冲可视化 |
| **性能** | `stat` 面板抓不到 | `stat startfile` → Insights |
| **网络** | 本项目没有 NetDriver | — |
| **崩溃** | 崩溃后脚本跑不了 | 读 `Saved/Crashes/`（崩溃篇）|
| **动画是否**在动** | 只检查赋值，不检查求值 | 案例 001 的四时间点法 |

**⚠️ 一张表把工具的能力边界说清楚，比它查了什么更重要。**

---

## 七、什么时候跑

| 时机 | 为什么 |
| --- | --- |
| **改完导入器/导出器之后** | 立刻看骨骼和引用有没有回归 |
| **重建关卡之后** | 确认 actor 数和引用没变 |
| **接手项目第一步** | 三十秒知道现状 |
| **怀疑「有东西不对」时** | 先跑体检，再决定查哪块 |

**建议加进一个包装脚本，和 `BuildAll` 一起跑 —— 待做。**

---

## 八、本篇的定位

**它是这个系列的**收口**：**

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
| **10（本篇）** | **把方法变成能反复跑的东西** |

**→ 前面的篇告诉你**怎么查**，这一篇让**该查的每次都被查**。**

---

## 九、待做

| 事项 | 为什么 |
| --- | --- |
| 把体检加进 `BuildAll` 之后 | 让回归自动可见 |
| 补上法线检查（走 glTF 而非 UE） | 案例 002 目前没有自动检查 |
| 把 20 多个 `diag_*.py` 归档或删除 | 已被体检覆盖的可以清掉 |
| 加一个 `--json` 输出 | 便于和上次结果做 diff |
