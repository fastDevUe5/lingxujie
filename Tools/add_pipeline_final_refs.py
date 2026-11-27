"""Add the buffer-length gotcha and wire the pipeline document into the index.

    python Tools/add_pipeline_final_refs.py
"""

GOTCHAS = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-Gotchas.md"
INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

ENTRY = """
## 83. glTF 的 `byteLength` 必须在所有 accessor 写完后才算

- **症状**：带动画的 glTF 导入产生 **0 个资产**，日志报
  ```
  LogInterchangeEngine: Error: 缓冲文件大小不匹配
  LogInterchangeEngine: Error: 提供的源数据中没有要导入的内容
  ```
  **看起来像文件损坏，实际是顺序问题。**
- **根因**：
  ```python
  gltf = { ..., "buffers": [{"byteLength": len(binary)}] }   # 算早了
  # 之后 add_view() 往 binary 追加动画数据
  # → 声明的 byteLength 比实际小
  ```
- **修法**：在 return 之前重新赋值
  ```python
  gltf["buffers"][0]["byteLength"] = len(binary)
  ```
- **怎么发现**：对比 `buffers[0].byteLength`（30532 才对）与声明值 —— 差的就是动画数据量
- **一般化**：**任何「先算总量、后追加内容」的结构都有这个风险**
- **出处**：2026-11-26，导入带动画的鸟
"""

OLD = "| **`.anm` 动画格式 / 帧率** |"
NEW = ("| **墨香 → UE 完整管道** | **`Docs/MOXIANG-TO-UE-PIPELINE.md`** | "
       "**网格+动画四资产全通**；五种格式对照表 |\n"
       "| **`.anm` 动画格式 / 帧率** |")


def main():
    text = open(GOTCHAS, encoding="utf-8").read()
    if "## 83." in text:
        print("gotcha already present")
    else:
        with open(GOTCHAS, "a", encoding="utf-8") as handle:
            handle.write(ENTRY)
        print("added gotcha 83")

    index = open(INDEX, encoding="utf-8").read()
    if OLD in index and "MOXIANG-TO-UE-PIPELINE" not in index:
        index = index.replace(OLD, NEW, 1)
        open(INDEX, "w", encoding="utf-8").write(index)
        print("index updated")
    else:
        print("index row already changed")


if __name__ == "__main__":
    main()
