"""Append the thirteenth debugging round.

    python Tools/write_debug_round13.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

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
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 70." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 70; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
