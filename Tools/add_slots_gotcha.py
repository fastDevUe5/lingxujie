"""Add gotcha 105 for the flattened face groups.

    python Tools/add_slots_gotcha.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-Gotchas.md"

ENTRY = """
## 105. 面组的材质索引被合并 —— 40 个材质变成 1 个槽

- **症状**：`boss001.mod` 有 **40 个 MATERIAL 块**，但导入 UE 后网格只有 **1 个材质槽**，
  全身用同一个表面
- **根因**：`read_mod_mesh` 把每个网格块的 **N 个面组**的所有三角面塞进一个列表，
  导出一个 primitive → 引擎给一个槽
- **事实**：面组本来就带材质索引
  ```
  MESH @83800: faceGroups=6
     group 0: mtl=39  index=5   group 3: mtl=36  index=2
     group 1: mtl=38  index=4   group 4: mtl=35  index=1
     group 2: mtl=37  index=3   group 5: mtl=34  index=0
  ```
- **修法**：**每个面组一个 primitive**，各自带 `"material": index`
  ```python
  groups.append({"material": g_mtl, "slot": g_index, "triangles": group_triangles})
  # 每个组生成独立索引缓冲，共享顶点属性
  ```
  **glTF 允许多 primitive 共享顶点属性、只换索引缓冲，所以成本几乎为零**
- **结果**：`primitives 17 → 40`、`materials 0 → 40`、UE 槽数 **1 → 40**
- **回归**：7 个模型包围盒**完全不变**，primitive 数各自增加（鸟 1→2、bobu 3→8、Boss 17→40）
- **教训**：**管道能导出几何，不等于导出了全部信息。**
  「哪些面用哪个材质」是一条独立的信息，丢了不会报错，只会让所有东西变一个颜色
- **出处**：2026-11-26，多材质槽
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 105." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(ENTRY)
    print("added gotcha 105")


if __name__ == "__main__":
    main()
