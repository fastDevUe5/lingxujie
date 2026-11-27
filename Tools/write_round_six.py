"""Append the sixth round to the handoff.

    python Tools/write_round_six.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 23. UE5 第六轮：物理仿真（2026-11-26 20:00）

### 一、新增文档

| 文档 | 大小 | 内容 |
| --- | --- | --- |
| **`UE5-PHYSICS.md`** | ~9 KB | 查询 vs 仿真两半分 + 13 个开关 + 物理材质 + 约束 + 布娃娃 |

### 二、🔴 核心认知：物理是两个独立的半边

| | 查询 | 仿真 |
| --- | --- | --- |
| 回答 | 能不能打中 | 会不会掉 |
| 机制 | 通道 + 响应 + 形状 | **刚体求解器（Chaos）** |
| 本项目 | **全开**（地形 CTF）| **全关** |

**两个独立：物体可以"能被射线打中但不掉"，也可以"掉但不参与查询"。**

### 三、实测：本项目零物理仿真

```
PHYS: actors 110
PHYS: primitive components: 26 MOVABLE + 98 STATIC = 124
PHYS: simulating physics:              0
PHYS: gravity enabled:                 0
PHYS: physical material override:      0
PHYS: physics constraints:             0
PHYS: skeletal meshes with physics asset: 0
```

**这是**对的**，不是缺陷。理由：**

**① 城市是静态几何**
**② 玩家用 `CharacterMovementComponent` —— 它是**运动学**的**

**关键认知：**
> **角色的移动不是"物理引擎推它"，而是"用碰撞查询扫掠着移动"。**
> **所以碰撞全开 + 仿真全关，玩家照样能站在地上走路。**

### 四、物理材质的两组容易忽略的参数

| 参数 | 意义 |
| --- | --- |
| `StaticFriction` vs `Friction` | **静摩擦**（推不推得动）vs **滑动摩擦** |
| `FrictionCombineMode` | **两个物体接触时摩擦怎么合**（平均/取大/取小/相乘）|

**所以"冰面 + 石头"的摩擦不是简单相加 —— 由 CombineMode 决定。**

### 五、踩到的坑

| # | 坑 |
| --- | --- |
| **76** | 遍历 `PrimitiveComponent` 时不能假设都有仿真属性（`ArrowComponent` 没有）|

### 六、掌握度

| 域 | 上一轮 | 本轮 |
| --- | --- | --- |
| **物理（碰撞部分）** | 70% | 70% |
| **物理（仿真部分）** | 0 | **50%** |
| **物理合计** | — | **60%** |

### 七、下一步

| 顺位 | 任务 | 备注 |
| --- | --- | --- |
| 1 | **Lumen** | 渲染 35% 里最大的空白 |
| 2 | 音频接入关卡 | 有 SoundClass 体系 |
| 3 | 动画实操 | 等 .mod 蒙皮 |
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 23." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 23; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
