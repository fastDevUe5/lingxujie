"""Add gotcha 92 about counting expected emptiness as failure.

    python Tools/add_vertex_gotcha.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-Gotchas.md"

ENTRY = """
## 92. 「解析失败」和「没有我要的东西」是两回事

- **症状**：统计 `.anm` 时得出「284 个失败（7%）」
- **实际**：这 284 个里 **153 个是顶点动画文件**
  （块头 `rot=0 pos=0 scale=0` 但 `mesh>0`）—— 水、火、瀑布、岩浆。
  **它们本来就没有骨骼轨道，`parse_anm` 返回空是正确行为**
- **真实分布**：

  | 类别 | 数量 | 性质 |
  | --- | --- | --- |
  | 有骨骼动画 | 3,772（93%）| 正常 |
  | 只有顶点动画 | 153（3.8%）| **预期行为** |
  | 块起点定位不到 | 105（2.6%）| 真正的待查项 |
  | 形态未知 | 26（0.6%）| ? |

- **`.anm` 的三种动画载体**

  | 载体 | 字段 | 用途 |
  | --- | --- | --- |
  | 骨骼 | `dwRotKeyNum` / `dwPosKeyNum` / `dwScaleKeyNum` | 角色 |
  | 顶点 | `dwAnimatedMeshKeyNum` | 水/火/瀑布/旗帜 |
  | UV | 顶点键内部 | 贴图滚动 |

- **教训**：**把「没有我要的东西」计入「失败」，会夸大问题规模**。
  统计时要区分**预期为空**和**意外失败**
- **出处**：2026-11-26，批量导出统计
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 92." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(ENTRY)
    print("added gotcha 92")


if __name__ == "__main__":
    main()
