"""Record the SCALE_KEY size error, which was hiding most of every animation.

The measurement that cracked it: an animation block declares its key counts, so the size they
require is arithmetic. A block claiming fifty-one scale keys was reported as needing 2192 bytes but
being 1988 - and 152 + 51 * 36 = 1988 exactly. The record is thirty-six bytes, not forty. I had
counted the struct wrong by four bytes, and every block containing scale keys beyond the first
stopped the walk.

The visible effect is large: a thirty-eight bone boss went from eight animation channels to
forty-nine.

    python Tools/document_scale_fix.py
"""

GOTCHAS = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-Gotchas.md"
STATUS = "C:/Users/tk/Desktop/lingxujie/Docs/BATCH-EXPORT-STATUS.md"

ENTRY = """
## 91. `SCALE_KEY` 是 **36 字节**不是 40 —— 一个数字藏住了 41 条动画通道

- **症状**：`Boss_cowf_01.anm` 有 **70 个块标记**，只解析出 **7–8 块**；
  38 骨骼的 Boss 只导出 **8 条动画通道**
- **根因**：`SCALE_KEY` 算错了 4 字节
  ```c
  struct SCALE_KEY {          // 实际 36 字节
      DWORD    dwTicks;       // 4
      DWORD    dwFrame;       // 4
      VECTOR3  v3Scale;       // 12
      VECTOR3  v3ScaleAxis;   // 12
      float    fScaleAxisAng; // 4
  };                          // = 4+4+12+12+4 = 36
  ```
  **我写成了 40。** 于是「声明的关键帧是否装得下」这个自校验，
  **在第一个含 scale 键的块上就失败**，走法提前终止
- **怎么定位的**：块自校验的算式会打印「需要 2192 字节但只有 1988」，
  而 `152 + 51 × 36 = 1988` **精确吻合** —— 36 是对的
- **修法**：`ANM_SCALE_KEY = 36`
- **效果**：38 骨骼的 Boss 从 **8 通道 → 49 通道**；块数从 7 → **69**
- **一般化**：**结构体大小要按字段逐个加，不要估**。
  用「声明量与块大小是否吻合」做自校验，就能让错误自己暴露
- **出处**：2026-11-26，块走法追踪
"""

STATUS_SECTION = """
---

## 十、🔴 `SCALE_KEY` 尺寸错误：8 通道 → 49 通道（第 24 轮）

### 10.1 决定性的一行算式

**追踪块走法时打印出：**
```
#7 fire03  size=1988  pos=0 rot=0 scale=51 mesh=0  required=2192  <- counts do not fit
```

**块声明 51 个 scale 键，我算需要 2192 字节，实际只有 1988。**

**而 `152 + 51 × 36 = 1988` —— **精确吻合**。**

**所以 `SCALE_KEY` 是 **36 字节**，我写成了 40。**

```c
struct SCALE_KEY {
    DWORD    dwTicks;       // 4
    DWORD    dwFrame;       // 4
    VECTOR3  v3Scale;       // 12
    VECTOR3  v3ScaleAxis;   // 12
    float    fScaleAxisAng; // 4
};                          // = 36
```

### 10.2 修前修后

| 项 | 修前 | 修后 |
| --- | --- | --- |
| `Boss_cowf_01.anm` 走到的块数 | **7** | **69** |
| `boss_cowf_01` 动画通道 | **8** | **49** |
| `boss_cowf_01` glTF 大小 | 56,589 B | **81,815 B** |
| 平均每文件轨道（全库）| — | 37.0 |

**12 个 Boss 文件里，8 个有骨骼的现在全部 48–49 通道。**

```
boss_cowf_01   38 骨骼  24 网格  49 通道   81 KB
boss_cowf_02   38 骨骼  52 网格  48 通道  125 KB
boss_cowf_04   38 骨骼  75 网格  49 通道  159 KB
boss_cowi_01   38 骨骼  35 网格  49 通道   99 KB
```

### 10.3 为什么之前「平均 37 轨」和「只有 6 轨」矛盾

**全库统计：平均每文件 **37 条轨道**。**

**但 `Boss_cowf_01.anm` 只解析出 6 轨 —— 因为它停在第 7 块。**

**37 是**其他文件**用了正确步长时的平均值；这个文件因为我写错 40 而被截断。**

**修后它立刻回到 69 块、49 通道，与平均值一致。**

### 10.4 教训

> **结构体大小要按字段逐个加，不要估。**
>
> **而且要好运：块自校验的算式把「需要 2192，实际 1988」打了出来，
> 我才能一眼看出 `152 + 51×36 = 1988`。**
>
> **如果当初没写那个自校验，这个错误永远不会暴露 —— 只会表现为「动画有点少」。**
"""


def main():
    text = open(GOTCHAS, encoding="utf-8").read()
    if "## 91." in text:
        print("gotcha already present")
    else:
        with open(GOTCHAS, "a", encoding="utf-8") as handle:
            handle.write(ENTRY)
        print("added gotcha 91")

    status = open(STATUS, encoding="utf-8").read()
    if "## 十、🔴 `SCALE_KEY` 尺寸错误" in status:
        print("status already present")
    else:
        with open(STATUS, "a", encoding="utf-8") as handle:
            handle.write(STATUS_SECTION)
        print("appended to the status document")


if __name__ == "__main__":
    main()
