"""Add gotchas 96 and 97 about the bone transform discoveries.

    python Tools/add_transform_gotchas.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-Gotchas.md"

ENTRY = """
## 96. 骨骼的 `mat4` 是**世界**变换，不是局部变换

- **症状**：把骨骼 `mat4` 沿父链累乘后，骨骼散到 **10 米外**
  （包围盒 395 × 1031 × 844 cm），对比网格只有 1.1 米
- **证据**：连续脊柱骨骼的 `mat4` 平移
  ```
  Bone28 (-32.44,  94.35, -11.19)
  Bone27 (-31.76, 112.12, -15.48)
  Bone26 (-28.83, 126.99, -19.19)
  Bone25 (-21.95, 143.83, -17.52)
  ```
  **Y 逐个递增，X/Z 很小 —— 这只能是世界坐标**
- **根因**：当成局部矩阵 `world * parent_world`，等于算了「世界²」
- **修法**：
  - `bind_world[bone] = bone["node_matrix"]`（**直接用，不累乘**）
  - glTF 节点局部变换 = `world * inverse(parent_world)`
- **出处**：2026-11-26，骨骼变换核对

## 97. 骨骼的 `fPos` / `fRotAng` 不能还原 `mat4`

- **症状**：用 `fRotAng`/`fRotAxis`/`fPos`/`fScale` 构造 glTF 节点变换，
  和用 `mat4` 算的逆绑定矩阵**描述的是两个不同的骨架**
- **实测差异**：
  ```
  Bone28  mat4 (-32.44, 94.35, -11.19)   字段 (13.92,  0.00,  0.00)   差 94.4
  Bone25  mat4 (-21.95, 143.83, -17.52)  字段 (0.23, -20.22, 16.59)   差 164.1
  ```
- **结论**：**`mat4` 是唯一权威**，其余字段不可用于重建变换
- **修法**：节点变换必须**分解 `mat4`**（translation + quaternion + scale），
  不能读散字段
- **一般化**：**一个结构里同时有「原料」和「成品」时，用成品**。
  原料可能没同步更新，或语义与成品不同
- **出处**：2026-11-26，骨骼变换核对
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 96." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(ENTRY)
    print("added gotchas 96 and 97")


if __name__ == "__main__":
    main()
