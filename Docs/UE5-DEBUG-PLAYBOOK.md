# UE5 调试手册：症状 → 查什么

> **这份手册不是知识文档，是**决策索引**。**
> **左边是你看到的现象，右边是**该查什么、怎么验、最可能是什么**。**
>
> **每一条都来自本项目七次实战的实测，不是推测。**
>
> **日期：2026-11-26 · UE 5.8.4**

---

## 〇、先做两件事

**在任何判断之前：**

```powershell
powershell -ExecutionPolicy Bypass -File Tools\EditorGuard.ps1 -Action check   # 编辑器活着吗
py Tools/diagnose.py                                                          # 三十秒体检
```

**体检报 `COLLAPSED skeleton` / `missing` / 引用缺失，就先修那些。
没有报错再往下查。**

---

## 一、模型看起来不对

| 症状 | 先查 | 最可能 | 怎么确认 |
| --- | --- | --- | --- |
| **模型散开/部件分离** | **骨骼跨度** | **逆绑定矩阵错** | `diagnose.py` 报 `COLLAPSED skeleton`；用 `get_bone_transform` 读两根骨骼，跨度应为几百厘米 |
| **模型躺在地上** | **源数据三轴跨度** | **坐标轴转换错** | 量 `.mod`/glTF 源空间的 X/Y/Z 跨度，看哪个最长 |
| **模型太大/太小 100 倍** | **绑定矩阵平移量级** | **厘米/米混用** | 对比 glTF 节点平移（~1.3）和 IBM 平移（~130 就是错）|
| **表面有黑块/光照怪** | **法线质量** | **NOT_SOLID 几何的法线无意义** | 查 `.mod` 的 `mesh_flag & 0xF0`，`0x10` 的块法线不可信 |
| **表面是灰格** | **组件 override** | **没赋材质** | `component.get_material(0)` 返回 `WorldGridMaterial` 就是没赋 |
| **整体比例怪但包围盒对** | **别信包围盒** | **问题在矩阵不在顶点** | 包围盒只量顶点，不量绑定姿态 |

**⚠️ 第一行和第三行是同一个 bug 的两种表现（矩阵错）。**
**⚠️ 第二行是**假线索** —— 包围盒长轴说明不了朝向，**骨骼位置**才是结构证据。**

---

## 二、动画不动

| 症状 | 先查 | 最可能 | 怎么确认 |
| --- | --- | --- | --- |
| **完全看不见动** | **`animation_data.anim_to_play`** | **根本没赋动画** | 读结构体字段，不要读 `get_play_rate()`（无实例时误导性返回 0）|
| **赋了但还是不动** | **`animation_mode`** | **还是 `ANIMATION_BLUEPRINT`** | 应为 `ANIMATION_SINGLE_NODE` |
| **改了位置画面不变** | **先看有没有动画** | **没动画可求值** | 赋一个真动画再试 `saved_position` |
| **`get_bone_pose` 挂死** | **换 API** | **用错函数** | `component.get_bone_transform(name)` 单参数，能用 |

**验证方法（四时间点法）：**
```python
for position in (0.0, 0.25, 0.5, 0.75):
    data.set_editor_property("saved_position", position)
    component.set_editor_property("animation_data", data)
    print(component.get_bone_transform(bone_name).translation)
# 四个结果不同 = 动画在驱动；全同 = 没驱动
```

---

## 三、日志里有 Error / Warning

| 现象 | 先查 | 最可能 |
| --- | --- | --- |
| **`Condition failed` 很多条** | **测试名/路径** | **引擎自测噪音**（`UE::UnifiedErrorTest`、`Runtime/Core/Tests/`）|
| **`could not be found in the Asset Registry`** | **按名字搜资产** | **路径猜错了**（Interchange 会嵌套一层）|
| **`contains no miplevels`** | **`listtextures <名字>` 看 `NumMips`** | **可能是 DDS 导入失败的**历史残留**** |
| **`Invalid animation skeleton`** | **是不是刚清空了 `anim_to_play`** | **清空动画的合法提示** |
| **`缺失使用标记Nanite`** | **`used_with_nanite` 实测** | **是**保存状态**和内存状态不一致**，重存即可 |
| **`DXGIFormat not supported`** | — | **转 PNG**，别修 DDS |

**⚠️ 关键判据：拿日志行去源码里搜。日志里的字符串在源码里**一定存在**。**
**→ 一搜就知道是引擎的、插件的、还是我们的。**

---

## 四、性能

| 症状 | 先查 | 最可能 |
| --- | --- | --- |
| **`stat unit` 显示 30fps 是绿的** | **`t.TargetFrameTimeThreshold`** | **默认 33.9ms（30fps），不是 16.6** |
| **平均好看但有卡顿** | **`stat unitmax`** | **`stat unit` 是 EMA 平滑，单帧卡顿被稀释** |
| **改了 CVar 没效果** | **`LastSetBy`** | **`Constructor` = 代码默认值覆盖了 ini** |
| **截图里看不到 `stat` 面板** | — | **`CaptureViewport` 不含 Canvas 层，抓不到** |

---

## 五、内存

| 症状 | 先查 | 最可能 |
| --- | --- | --- |
| **`obj cycles` 报很多环** | **环里是 `/Game/` 还是 `/Engine/`** | **`/Engine/` 是 World↔Level 固有环，不是泄漏** |
| **想知道某对象为什么没销毁** | **`obj refs name=<完整路径>`** | 持有链一路到根 |
| **内存一直在涨** | **两份 `memreport -full` 对比** | **Count 涨=对象泄漏；Count 不变 NumKB 涨=同一对象累积** |
| **`memreport` 没反应** | **`Saved/Profiling/MemReports/`** | **延迟到帧末执行，输出在文件里不在控制台** |

---

## 六、渲染

| 症状 | 先查 | 最可能 |
| --- | --- | --- |
| **画面不对，想知道是哪一层** | **缓冲可视化菜单**（24 种，无控制台命令）| 只有 UI 能切 |
| **想看某个 RDG 资源的输出** | **`vis pool` 找名字 → `vis <名字>`** | **拼错名字不报错，只什么都不显示** |
| **验证「改了渲染有没有效果」** | **`Tools/diff_captures.py`** | **改渲染 16.7% 像素差；改覆盖层 0%** |
| **`vis pool` 和 `obj list` 对不上** | — | **池里是运行时 RT，`obj list` 是资产，不能相加** |

---

## 七、脚本

| 症状 | 先查 | 最可能 |
| --- | --- | --- |
| **脚本没输出** | **`-WaitPattern` 有没有匹配到 `done`** | **没匹配 = 有失败** |
| **想快速定位 Python 异常** | **搜 `LogPython: Error:`** | 栈带完整路径和行号 |
| **日志里同一段错误出现两次** | — | **语法错误会被打两遍**（插件 + stderr 重定向）|
| **`sys.exit(0)` 没退出** | — | **被插件吞掉了** |
| **自动化卡死在一个对话框上** | **`EditorGuard -Action dismiss`** | **蓝图 runaway 会弹模态框** |

---

## 八、崩溃

| 症状 | 先查 |
| --- | --- |
| **编辑器崩溃** | `Saved/Crashes/UECC-*/CrashContext.runtime-xml` |
| **想知道崩在哪** | **`PCallStack`**（带模块+偏移），不是 `CallStack`（只有模块名）|
| **想知道崩溃时人在干什么** | **`UserActivityHint`** |
| **异常地址里有可读 ASCII** | **数据被当指针用了** |
| **`IsAssert=true`** | 断言，查表达式和谁传了坏值 |
| **`IsAssert=false` + `EXCEPTION_ACCESS_VIOLATION`** | 指针生命周期问题 |

**⚠️ 本机没有 `cdb`/`windbg`/`UnrealEditor.pdb` —— 崩溃分析只能靠 XML。**

---

## 九、最容易犯的五种推理错误（本项目实测都犯过）

| # | 错误 | 例子 | 怎么防 |
| --- | --- | --- | --- |
| 1 | **数字真但含义错** | 「101 个网格缺材质」→ 98 个有 override | **结论与画面矛盾时先信画面** |
| 2 | **分母错** | 「Textures 只有 1 个」→ 实际 99 个，只是不在那个目录 | **说数字必须说清统计口径** |
| 3 | **把方法失败当事情做不到** | 「`set_position` 不求值」→ 其实没有动画可求值 | **失败时先问「我量的是不是那件事」** |
| 4 | **自证式验证** | 「IBM 往返误差 2e-16」→ 证明算术对，没碰到字节顺序 | **用独立读取者验** |
| 5 | **把报错当结果** | `Get-Process` 报错 → 误读为「进程没了」 | **先读报错本身** |

**共同点：都是**推理真、前提错**。**
**→ 防法只有一条：**任何结论落地前，找一个能推翻它的独立观察。****

---

## 十、工具的边界（别浪费时间）

| 想做的事 | 能做吗 | 替代 |
| --- | --- | --- |
| Python 读 StaticMesh 法线 | ❌ | 查 glTF 源文件 |
| Python 读贴图 mip | ❌ | `listtextures` |
| Python 切缓冲可视化 | ❌ | 只能 UI |
| 截图抓 `stat` 面板 | ❌ | `stat startfile` → Insights |
| 解析 minidump | ❌ 本机无工具无符号 | 靠 `CrashContext.runtime-xml` |
| 蓝图断点 | ❌ Python 设不了 | 只能 UI |
| 网络模拟 | ⚠️ 本项目无 NetDriver | 需先起 listen server |

---

## 十一、体检工具能自动查的

**`py Tools/diagnose.py`：**

| 检查 | 报什么 |
| --- | --- |
| 资产数（按类）| 各类计数 |
| 引用完整性 | `missing: N` |
| **骨骼跨度** | **`COLLAPSED skeleton`** |
| **动画赋值** | **`no animation assigned`** |
| 内存环 | `obj cycles` 输出 |
| 关键 CVar | 帧预算 / GI / 抗锯齿 |

**⚠️ 它查不出的：法线、材质是否正确、性能、崩溃、动画**是否在动**。**
**→ 那些按上面各节手动查。**
