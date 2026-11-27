"""Append the twenty-eighth round.

    python Tools/write_round_twentyeight.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 45. 第二十八轮：骨骼变换的两个发现 + 一个**未解**（2026-11-26 30:00）

### 一、🔴 `mat4` 是**世界**变换，不是局部

**连续脊柱骨骼的 `mat4` 平移：**

| 骨骼 | mat4 位置 |
| --- | --- |
| `Bone28` | (-32.44, **94.35**, -11.19) |
| `Bone27` | (-31.76, **112.12**, -15.48) |
| `Bone26` | (-28.83, **126.99**, -19.19) |
| `Bone25` | (-21.95, **143.83**, -17.52) |

**Y 逐个递增，X/Z 很小 —— 只能是世界坐标。**

**我原来当局部矩阵沿父链累乘 = 「世界²」，骨骼散到 10 米外。**

### 二、🔴 `fPos` / `fRotAng` 不能还原 `mat4`

| 骨骼 | mat4 位置 | 字段位置 | 差异 |
| --- | --- | --- | --- |
| `Bone28` | (-32.44, 94.35, -11.19) | (13.92, 0.00, 0.00) | **94.4** |
| `Bone25` | (-21.95, 143.83, -17.52) | (0.23, -20.22, 16.59) | **164.1** |

**所以「用字段建节点变换」和「用 mat4 算 IBM」描述两个不同骨架 —— 必然扭曲。**

### 三、已做的三处修改

| 修改 | 依据 |
| --- | --- |
| IBM = `inverse(bind_world)` | 67 个全可逆，往返误差 2.22e-16 |
| 节点局部变换 = `world × inverse(parent_world)` | `mat4` 是世界矩阵 |
| `bind_world` 直接用 `mat4`，不累乘 | 同上 |

### 四、🔴 但画面**没有变化** —— 必须说清

**三次改动（只改 IBM / 只改节点 / 两者都改）的截图**完全一样**。**

**两种可能：**

| 可能 | 含义 |
| --- | --- |
| **A. 这就是绑定姿态本来的样子** | 部件分开是设计（浮空护甲类）|
| **B. 蒙皮没生效** | `SkeletalMeshActor` 没跑 skinning |

**我不知道是哪个。**

### 五、诚实的自我批评

> **改动有依据 ≠ 改动解决了问题。**
>
> **三次改动从正确性看都必要（`mat4` 确实是世界矩阵、字段确实不能还原、IBM 用单位矩阵确实错），
> 但我**没有证据表明视觉因此改善**。**
>
> **应该在动手前先做一个能证伪的实验（播放动画看是否动），而不是先改三处再猜。**

### 六、下一轮第一件事

**不是继续改导出器，而是先回答「蒙皮生效了吗」：**

```python
component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
matrix = component.get_bone_matrix("Bone28")
# 和 .mod 里的 mat4 对比
```

**一致 → 蒙皮生效，部件分开是设计。
不一致 → 蒙皮有问题。**

### 七、新增坑

| 编号 | 内容 |
| --- | --- |
| **#96** | 骨骼的 `mat4` 是世界变换，不是局部 |
| **#97** | `fPos`/`fRotAng` 不能还原 `mat4` —— 用成品，不用原料 |
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 45." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 45; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
