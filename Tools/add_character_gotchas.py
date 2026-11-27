"""Record the two character-specific bugs as gotchas and wire the status doc into the index.

    python Tools/add_character_gotchas.py
"""

GOTCHAS = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-Gotchas.md"
INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

ENTRIES = """
## 84. 一个模型可能有多个网格块，只导第一个会得到残缺的模型

- **症状**：`198_bobu.mod` 导入后包围盒 **34.3 × 44.0 × 39.5 cm** —— 没有这么小的人形
- **根因**：该文件有 **3 个 MESH 块**（164 / 632 / 37 顶点），导出器只取 `meshes[0]`，
  导的是 164 顶点的小零件，不是 632 顶点的主体
- **为什么鸟没暴露**：鸟只有 1 个网格块
- **修法**：每个网格块生成一个 glTF primitive，**共用同一个 skin**
  ```python
  primitives = []
  for each in meshes:
      attributes, indices = emit_mesh(each)      # 各自有自己的 PHYSIQUE
      primitives.append({"attributes": attributes, "indices": indices})
  gltf["meshes"][0]["primitives"] = primitives
  ```
  **glTF 允许多 primitive 共享一个 skin，每个 primitive 有自己的 attributes。**
- **出处**：2026-11-26，测试 31 骨骼人形角色

## 85. `.mod` 的顶点坐标是世界位置，不是相对原点的局部坐标

- **症状**：多网格修好后包围盒合理（99.6 × 77.8 × 99.4），但角色**在关卡里完全不渲染**。
  actor 位置正确、`visible=True`、有材质、骨骼正常。
- **根因**：查 glTF 的 `POSITION` min/max 发现所有顶点都在 **(23, 25, -1) 米**：
  ```
  primitive 0: min=[22.44, 23.98, -0.89]  max=[23.12, 24.77, -0.01]
  ```
  **也就是说顶点是**模型在原地图里的世界坐标**，不是局部坐标。**
  actor 放到 (9100, -6200)，几何实际在 (11400, -3700) —— 画面外。
- **为什么鸟没暴露**：鸟的顶点恰好接近原点
- **修法**：导出时减去顶点中心
  ```python
  centre = [sum(p[i] for p in positions) / len(positions) for i in range(3)]
  positions = [(p[0]-centre[0], p[1]-centre[1], p[2]-centre[2]) for p in positions]
  ```
  修后 min/max 全部居中于原点，角色立刻渲染出来。
- **⚠️ 更彻底的修法**：应用对象的 `NODE_TM` 变换（`fRotAng`/`fRotAxis`/`fPos`/`fScale`），
  而不是只减中心 —— 当前模型仍"趴着"，很可能就缺这一步
- **出处**：2026-11-26，人形角色不渲染的诊断
"""

OLD_INDEX = "| **墨香 → UE 完整管道** |"
NEW_INDEX = ("| **人形角色导入进度 / 两个坑** | **`Docs/CHARACTER-IMPORT-STATUS.md`** | "
             "**多网格 + 顶点不在原点** |\n"
             "| **墨香 → UE 完整管道** |")


def main():
    text = open(GOTCHAS, encoding="utf-8").read()
    if "## 84." in text:
        print("gotchas already present")
    else:
        with open(GOTCHAS, "a", encoding="utf-8") as handle:
            handle.write(ENTRIES)
        print("added gotchas 84 and 85")

    index = open(INDEX, encoding="utf-8").read()
    if OLD_INDEX in index and "CHARACTER-IMPORT-STATUS" not in index:
        index = index.replace(OLD_INDEX, NEW_INDEX, 1)
        open(INDEX, "w", encoding="utf-8").write(index)
        print("index updated")
    else:
        print("index row already changed")


if __name__ == "__main__":
    main()
