"""Append the seventh round to the handoff.

    python Tools/write_round_seven.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 24. UE5 第七轮：Lumen —— 一个被我自己搞错的「零」（2026-11-26 20:15）

### 一、更正：Lumen 从第一天就在跑

**我之前说「Lumen 是零」。错的。**

**`Config/DefaultEngine.ini` 实测：**
```ini
r.DynamicGlobalIlluminationMethod=1     ; = Lumen GI
r.ReflectionMethod=1                    ; = Lumen 反射
r.Shadow.Virtual.Enable=1               ; 虚拟阴影贴图
r.GenerateMeshDistanceFields=True       ; Lumen 软件光追的前提
r.AllowStaticLighting=False             ; 全动态光照
r.AntiAliasingMethod=4                  ; = TSR
r.DefaultFeature.AutoExposure=False     ; 固定曝光（截图可复现）
```

**枚举（`EngineTypes.h` 源码核实）：**
```
EDynamicGlobalIlluminationMethod:  0=None  1=Lumen  2=ScreenSpace(废弃)  3=Plugin
EReflectionMethod:                 0=None  1=Lumen
```

**所以场景光照好看不是「默认天光凑合」，是 Lumen 在算间接光。**

### 二、Lumen 的硬前提（源码注释原文）

> *Requires 'Generate Mesh Distance Fields' enabled for Software Ray Tracing
> and 'Support Hardware Ray Tracing' enabled for Hardware Ray Tracing.*

**两条路：**
| 路径 | 前提 | 本项目 |
| --- | --- | --- |
| 软件光追（SDF） | `r.GenerateMeshDistanceFields=True` | ✅ 已开 |
| 硬件光追 | `r.Lumen.HardwareRayTracing=True` + 显卡支持 | ❌ 关着 |

**「网格距离场」= 把每个网格预处理成体素化的「离表面多远」，
光线在场里走比在三角形里走快几个数量级 —— 这是软件光追能实时的原因。**

**代价：勾了距离场的网格构建变慢、内存占用上升（地形 524,288 面尤其明显）。**

### 三、配置文件里还有一条重要注释

```ini
; Revisit for the MMO scale test (P0.5) - Lumen is expensive with many players on screen.
```

**这说明配置时就意识到了 MMO 规模问题。不是忘了，是**知道并推迟决定**。**

### 四、待办：Lumen 的 MMO 规模问题

| 方案 | 做法 |
| --- | --- |
| A. 只用 Lumen 做主角附近 | 远处切烘焙 |
| B. 全烘焙 + 少量动态 | 关 Lumen |
| C. 混合 | 室内 Lumen、室外烘焙 |

**P0.5 测试时必须重新决定。现在不做。**

### 五、踩到的坑

| # | 坑 |
| --- | --- |
| **77** | Lumen 软件光追依赖「生成网格距离场」，两者必须同时开 |

### 六、掌握度

| 域 | 上一轮 | 本轮 |
| --- | --- | --- |
| **渲染（含 Lumen）** | 35% | **55%** |

**涨的：Lumen 原理、两个独立开关、距离场前提、本项目配置、MMO 代价。
没涨的：没实际调过任何 Lumen 参数。**

### 七、下一步

| 顺位 | 任务 | 备注 |
| --- | --- | --- |
| 1 | 音频接入关卡（背景音 + 环境音）| 有 SoundClass 体系 |
| 2 | 动画实操 | 等 .mod 蒙皮 |
| 3 | 关闭 Lumen 做一次对比截图 | **需重启编辑器，要先问人** |
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 24." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 24; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
