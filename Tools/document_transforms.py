"""Record the transform findings and be explicit that the visual check is inconclusive.

Three changes - real inverse bind matrices, node transforms derived from the matrix, and both
together - produced the same picture. That is itself information: either the bind pose simply looks
like this, or skinning is not taking effect and we are seeing raw vertices. Saying which requires a
test that was not run, so this records what is known and what is not.

    python Tools/document_transforms.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/BATCH-EXPORT-STATUS.md"

SECTION = """
---

## 十四、骨骼变换的两个发现 + 一个未解（第 28 轮）

### 14.1 🔴 `mat4` 是**世界**变换，不是局部变换

**连续的脊柱骨骼 `mat4` 平移：**

| 骨骼 | mat4 位置 |
| --- | --- |
| `Bone28` | (-32.44, **94.35**, -11.19) |
| `Bone27` | (-31.76, **112.12**, -15.48) |
| `Bone26` | (-28.83, **126.99**, -19.19) |
| `Bone25` | (-21.95, **143.83**, -17.52) |

**Y 从 94 → 112 → 127 → 144 逐个递增，X/Z 很小 —— 这是**脊柱的世界坐标**。**

**我原来把它当局部矩阵沿父链累乘，等于算了「世界²」，
骨骼散到 10 米外（包围盒 395 × 1031 × 844 cm）。**

### 14.2 🔴 `fPos` / `fRotAng` **不能还原 `mat4`**

**对比实测：**

| 骨骼 | mat4 位置 | 字段位置 | 差异 |
| --- | --- | --- | --- |
| `Bone28` | (-32.44, 94.35, -11.19) | (13.92, 0.00, 0.00) | **94.4** |
| `Bone25` | (-21.95, 143.83, -17.52) | (0.23, -20.22, 16.59) | **164.1** |

**最大差异 164 个单位。**

**所以：**
- 用 `fPos`/`fRotAng` 构造 glTF 节点变换 → **错的骨架**
- 用 `mat4` 算逆绑定矩阵 → **另一个骨架**
- 两边不一致，蒙皮必然扭曲

### 14.3 已做的修改

**① 逆绑定矩阵改为真算**
```python
IBM[bone] = inverse(bind_world[bone])
```
**验证：67 个矩阵全可逆，往返误差 2.22e-16。**

**② 节点变换改为从 `mat4` 反推局部矩阵**
```python
local = world * inverse(parent_world)
translation, rotation, scale = decompose(local)
```

**③ 逆绑定矩阵用 `mat4` 直接作世界矩阵（不再累乘）**

### 14.4 🔴 但画面**没有变化** —— 这一点必须说清

**三次改动（只改 IBM / 只改节点 / 两者都改）产生的截图**完全一样**。**

**两种可能：**

| 可能 | 含义 |
| --- | --- |
| **A. 这就是绑定姿态本来的样子** | 部件分开是模型设计（浮空护甲类），没有问题 |
| **B. 蒙皮没生效，看到的是原始顶点** | `SkeletalMeshActor` 没在跑 skinning |

**区分方法（还没做）：**
- 给 actor 指定 `SK_Boss001_Anim` 动画并播放，看是否动
- 或用 `SkeletalMeshComponent.get_bone_matrix()` 读实际骨骼位置

### 14.5 诚实结论

**我不知道部件散开是「模型本来如此」还是「蒙皮没生效」。**

**这三次改动从「正确性」角度看都是必要的：**
- `mat4` 确实是世界矩阵（证据：脊柱坐标递增）
- 字段确实不能还原 `mat4`（证据：差异 164）
- `IBM` 用单位矩阵确实错（证据：真实骨骼不在原点）

**但**没有证据表明视觉问题因此改善**。**

> **改动有依据 ≠ 改动解决了问题。**
> **我应该在动手前先做一个能证伪的实验（播放动画看是否动），
> 而不是先改三处再猜。**

### 14.6 下一轮该做的第一件事

**不是继续改导出器，而是先回答「蒙皮到底生效了吗」：**

```python
component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
# 读第 0 根骨骼的实际世界位置
matrix = component.get_bone_matrix("Bone28")
```

**如果骨骼位置和 `mat4` 一致 → 蒙皮生效，部件分开是设计。
如果不一致 → 蒙皮有问题。**
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 十四、骨骼变换的两个发现" in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
