"""Record the two triplanar mistakes as gotchas, since both are common and both compile fine.

A triplanar graph that is wrong in either of these ways still compiles. The first produces a flat
colour, the second a broken blend, and neither raises an error - which is exactly the kind of
failure worth writing down.

    python Tools/add_triplanar_gotchas.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-Gotchas.md"

ENTRIES = """
## 71. 三平面材质的 UV 要**除**以米数，不是**乘**平铺次数

- **症状**：三平面材质建好、编译通过、挂上去 —— **地面变成纯色，完全没有纹理**
- **根因**：`WorldPosition` 返回的是**厘米**（比如 x=8950）。
  乘以平铺次数 24 得到 UV = 214,800 —— 贴图被采到极限密度，
  **引擎退化成平均值，看起来就是纯色**
- **修法**：除以「每贴图覆盖多少厘米」：
  ```
  UV = WorldPosition / 600      <- 每 6 米一张贴图
  ```
  **概念转换：不是"重复多少次"，是"每张覆盖多长"。**
- **怎么发现**：接了世界坐标后如果变纯色，**先查除法方向**
- **出处**：2026-11-26，三平面第一次尝试

## 72. 三平面混合权重必须是**归一化比例**，不能是分量之和

- **症状**：三平面看起来"某两个面特别亮、另一个面不见了"，或者混合边界有硬断层
- **根因**：法线分量绝对值相加可能 **> 1**。
  `Lerp` 的 Alpha 超过 1 会被钳制到 1，等于"永远选 B"，混合就失效了
- **修法**：用比例而不是和：
  ```
  错: alpha = |n.x| + |n.y|
  对: alpha = |n.y| / (|n.x| + |n.y|)      <- 恒在 [0,1]
  ```
  **并且分母要加一个很小的 epsilon 防止除零**
  （法线朝正上时 |x|+|y| = 0）
- **出处**：2026-11-26，三平面第一次尝试的第二个错误
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 71." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(ENTRIES)
    import re
    numbers = re.findall(r"^## (\d+)\.", text + ENTRIES, re.M)
    print("appended; total gotchas %d, last %s" % (len(numbers), numbers[-2:]))


if __name__ == "__main__":
    main()
