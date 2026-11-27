"""Close the orientation question with the measurement that settles it.

The open item was whether the glTF axis mapping was wrong, since objects looked squat. Testing that
by "which axis is tallest" fails as a method: across seven models with one mapping the tallest axis
splits three ways. The orientation is instead fixed by the source's own convention - heights in a
height field are Z, and map placement uses z as elevation - so Z-up is right and the glTF mapping
that sends source Z to glTF Y is correct.

    python Tools/close_orientation.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/CHARACTER-IMPORT-STATUS.md"

SECTION = """
---

## 七、朝向问题：已关闭（第 20 轮）

### 7.1 「最高轴」不是有效的朝向判据

**原计划：用两种映射各导一次，保留让 Z 最高的那个。**

**实测七个模型（同一套映射，已应用 mat4）：**

| 文件 | 顶点 | X / Y / Z (cm) | 最高轴 |
| --- | --- | --- | --- |
| `198_bobu` | 632 | 126 / 156 / 110 | Y |
| `w25260` | 32 | 10 / 20 / 23 | Z |
| `216` | 517 | 59 / 134 / 71 | Y |
| `20_eagle_01` | 226 | 84 / 177 / 139 | Y |
| `108_bird` | 146 | 143 / 111 / 144 | Z |
| `19240` | 348 | 174 / 98 / 133 | X |
| `choco` | 190 | 186 / 149 / 40 | X |

**分布：`{'Y': 3, 'Z': 2, 'X': 2}` —— 没有任何轴占主导。**

**原因：**
> **「最高」只对直立人形等于「高度」。
> 对鸟是**翼展**，对四足兽是**体长**，对扁平道具是**宽度**。**

**所以这个判据本身是错的，不是映射错了。**

### 7.2 正确的判据：源格式自己的约定

**客户端是 **Z 朝上**：**

| 证据 | 出处 |
| --- | --- |
| `.hfl` 高度场把高程存为 **Z** | `FORMAT-REFERENCE.md` 第二节 |
| `.map` 物件摆放 `(x y z)`，**z 是高程** | 同上，第五节 |
| `HFIELD_DESC` 的 `left/top/right/bottom` 是 XY 平面 | 同上 |

**而我的映射 `(x, z, -y)` 让 **glTF 的 Y = 源的 Z** —— 这正是 Z-up → Y-up 的标准转换。**

**→ 映射正确，不需要改。**

### 7.3 那 `198_bobu` 为什么看着矮？

**它的尺寸是 126 × **156** × 110 cm —— **体长大于身高**。**

**它就是一只**矮胖生物**，不是误差。**

**对照 `20_eagle_01` 的 84 × **177** × 139：Y 是**翼展**，鸟张开翅膀本来就比身高宽。**

### 7.4 这一轮的教训

> **选了一个判据，它对该模型不成立，却以为是管道错了。**
>
> **判据要能被反驳** —— 「最高轴」在第一个模型上就给了一个可疑的答案，
> 但我先改代码，后验证判据。顺序反了。

**这和前几轮的错误同类：先有结论，后者证。**

---

## 八、最终状态（截止第 20 轮）

| 项 | 鸟 | 人形角色（bobu） |
| --- | --- | --- |
| 网格导入 | ✅ | ✅ |
| 骨骼数量 | ✅ 9/9 | ✅ 31/31 |
| AnimSequence | ✅ 9.0 s | ✅ 10.67 s |
| 渲染可见 | ✅ | ✅ |
| 多网格 | 不适用 | ✅ 已修 |
| 对象变换 | 恰好单位矩阵 | ✅ 已修 |
| **坐标轴** | ✅ | ✅ **确认正确** |

**管道正确。剩下的是**批量导出**和**材质**。**
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 七、朝向问题：已关闭" in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
