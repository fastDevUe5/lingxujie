"""Write the closing summary of the debugging series.

Seventeen rounds, eight domains, seven case studies. This records what was built, what it cost, and an
honest account of what remains unproven - the fixes are diagnosed and demonstrated but not applied.

    python Tools/write_debug_summary.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-DEBUG-SUMMARY.md"

CONTENT = """# UE5 调试与问题定位 · 总结

> **17 轮 · 八个域 · 七个实战案例 · 19 篇文档 · 110 条坑**
>
> **这一篇是收口：做到了什么、怎么验证的、哪些还没做到。**
>
> **日期：2026-11-26 · UE 5.8.4**

---

## 一、从哪开始，往哪去

**起点是一句要求：「优先学调试、排查定位问题这方面，一边学一边实操，一边归档」。**

**没给的：先学什么、怎么算学会、什么时候算够。**

**我自己定的标准（写在 `UE5-DEBUG-INDEX.md` 里）：**

> 每一篇必须做到四件事：
> 1. **读源码** —— 结论要能指到具体文件和行号
> 2. **实操** —— 在本项目上复现，不只看文档
> 3. **记录更正** —— 之前哪条结论错了，写清楚错在哪
> 4. **给排查清单** —— 让人能照着做

**第 3 条是最难也是最有价值的一条。**

---

## 二、做了什么

### 2.1 八个域（机制文档）

| 域 | 文档 | 核心结论 |
| --- | --- | --- |
| **日志** | `UE5-DEBUG-LOGGING.md` | 打印过两道编译期 + 一道运行期闸门；`Log` 级别不写控制台 |
| **断言** | `UE5-DEBUG-ASSERTS.md` | 打包版 `check` 可能**不求值**；`ensure` 同一行只报一次 |
| **崩溃** | `UE5-DEBUG-CRASH.md` | `PCallStack` 带偏移，`CallStack` 只有模块名 |
| **性能** | `UE5-DEBUG-PERF.md` | `stat unit` 是 EMA 平滑；面板**抓不到** |
| **内存** | `UE5-DEBUG-MEMORY.md` | `memreport` 延迟到帧末先 GC；环数 ≠ 泄漏数 |
| **渲染** | `UE5-DEBUG-RENDER.md` | 24 种缓冲可视化只有 UI 能切；`vis` 是命令 |
| **脚本** | `UE5-DEBUG-SCRIPT.md` | Python 异常**打不垮编辑器**；蓝图 runaway 会弹模态框 |
| **网络** | `UE5-DEBUG-NET.md` | ⚠️ **本项目无网络，源码为主未实测** |
| **资产** | `UE5-DEBUG-ASSET.md` | 「注册表找不到」几乎总是**路径猜错** |

### 2.2 七个实战案例

| 案例 | 根因 | 验证方式 |
| --- | --- | --- |
| **动画不播放** | 脚本没赋 `animation_mode`/`anim_to_play` | 四个时间点四个位姿 |
| **退化法线** | `NOT_SOLID (0x10)` 几何本无语义法线 | `.mod` 按 flag 完美分组 |
| **模型散开** | **IBM 转置两次 + 单位没缩放** | 67/67 平移在错槽；跨度 0 → 397m → 3.97m |
| 材质缺失 | 1 个 actor 没赋材质（98 个有 override）| 组件有效材质检查 |
| 无害警告 | 清空 `anim_to_play` 的合法提示 | 上下文 + 源码 |
| 13 条测试失败 | 引擎自测噪音 | 源码逐字对应 + 项目测试全过 |
| 贴图无 mip | DDS 导入失败的历史残留 | `listtextures` 实测 10 级完整 |

**⚠️ 七个里只有三个真缺陷。另外四个是误报、无害、引擎噪音、历史残留。**

### 2.3 工具

| 工具 | 作用 |
| --- | --- |
| **`Tools/diagnose.py`** | **一次跑完八个域，首跑就抓到 4 个角色同时中两个 bug** |
| `Tools/diff_captures.py` | 像素级 A/B，判断渲染改动有没有效果 |

---

## 三、怎么验证的

**每一类结论都有自己的验证方式，不是笼统「跑了一下」：**

| 结论类型 | 验证方式 | 例子 |
| --- | --- | --- |
| **机制** | 指到源码行号 | `LogMacros.h:240-255` 三道闸门 |
| **运行时行为** | 控制台命令 + 读回 | `log list` / `t.*` 的 `LastSetBy` |
| **数据问题** | 直接解析二进制 | glTF accessor / `.mod` 块 |
| **视觉改动** | 像素级 A/B | 16.7% vs 0% |
| **结构** | 读对象属性 | 骨骼跨度 / 材质槽 |
| **测试** | 独立进程跑 | `RunTests.ps1` 15/15 |

**⚠️ 最有价值的一条验证教训：**
> **「自己算、自己验」等于没验。**
> `IBM = inverse(bindWorld)` 的往返误差 2e-16 证明了算术，但**完全没碰到字节顺序**。
> **验证必须用独立读取者。**

---

## 四、更正了哪些结论

**17 轮里我更正了自己 9 次，每一次都写进了文档：**

| # | 原结论 | 实际 | 类型 |
| --- | --- | --- | --- |
| 1 | 打包后 Verbose 日志被编译掉 | 默认 `VeryVerbose` 全保留 | 机制 |
| 2 | `bGenerateRuntimeCallstack` 只在内部构建 | `UE_LOG_CRASH_CALLSTACK` 默认 1，恒真 | 读错分支 |
| 3 | `set_position` 不触发求值 | 会触发，只是当时没动画 | 把方法失败当事做不到 |
| 4 | `get_bone_pose` 挂死 → 读不到骨骼 | `get_bone_transform` 能用 | 同上 |
| 5 | Textures 只有 1 个资产 | 实际 99 个，只是不在那个目录 | 分母错 |
| 6 | 101 个 Nanite 网格缺材质 | 98 个有 override | 数字真、含义错 |
| 7 | 赋值顺序很重要 | 实测无关 | 读漏了同文件另一条路径 |
| 8 | 贴图没有 mip | 实测 10 级完整 | 历史残留 |
| 9 | 编辑器进程没了 | 一直活着，是我的命令报错 | **把报错当结果** |

**⚠️ 第 3、4、9 是同一型：把「我的工具/方法给出的结果」当成了「事实」。**

---

## 五、还没做到什么（诚实清单）

| 事项 | 状态 |
| --- | --- |
| **三处导出器修复** | **已定位、已验证**，但**没应用** |
| **一处材质赋值** | 已定位，未应用 |
| **网络调试** | 源码为主，**零实测**（本项目无 NetDriver）|
| **最小化 dump 分析** | 本机无 `cdb`/符号，只能靠 crash XML |
| **GPU 抓帧** | 本机无 RenderDoc/PIX |
| **蓝图断点** | Python 设不了 |
| **性能实测数字** | `stat` 面板抓不到，还没用 Insights 量过 |

**⚠️ 最重要的一条：所有修复都停在「验证了机制」这一步，没有落到代码里。**
**→ 所以「能定位」已经证明，「能修好并确认」只证明了一半。**

---

## 六、这套能力实际长什么样

**面对一个陌生症状时的流程：**

```
1. EditorGuard -Action check          → 编辑器活着吗
2. diagnose.py                        → 三十秒体检，常见问题直接报
3. 看 UE5-DEBUG-PLAYBOOK.md           → 症状 → 该查什么
4. 查不上？按域翻机制文档             → 知道该看哪段源码
5. 拿日志行去源码搜                   → 知道是引擎/插件/我们的
6. 量出数字                           → 不要靠画面判断
7. 找一个能推翻结论的独立观察         → 这一步是整个流程的核心
```

**第 7 步是 17 轮里代价最高、也最有收获的一步。**

---

## 七、如果继续，最有价值的三件事

| 优先级 | 事项 | 为什么 |
| --- | --- | --- |
| **1** | **应用三处修复并跑体检验证** | 把「能定位」补成「能修好」 |
| 2 | 用 Insights 量一次真实帧时间 | 性能域目前只有机制没有数字 |
| 3 | 起一个 listen server 做网络实测 | 唯一零实测的域 |

**⚠️ 第 1 项会改代码，需要人点头。**
"""


def main():
    import os
    if os.path.exists(PATH):
        text = open(PATH, encoding="utf-8").read()
        if "17 轮 · 八个域" in text:
            print("already present")
            return
    with open(PATH, "w", encoding="utf-8") as handle:
        handle.write(CONTENT)
    print("wrote %s (%d bytes)" % (PATH.rsplit("/", 1)[-1], len(CONTENT)))


if __name__ == "__main__":
    main()
