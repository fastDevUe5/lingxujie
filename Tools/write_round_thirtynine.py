"""Append the thirty-ninth round.

    python Tools/write_round_thirtynine.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 56. 第三十九轮：**收口 —— 总览并入新结论 + 数字一致性检查**（2026-11-26 40:00）

### 一、总览已更新到第 39 轮

**`UE5-KNOWLEDGE-SUMMARY.md` 补入第 37–38 轮的结论：**

| 新增内容 | 位置 |
| --- | --- |
| **材质六段全通** | 已验证表 |
| **面组材质索引保真**（primitives 17→40、槽数 1→40）| 已验证表 |
| 材质多槽视觉差异 | 未验证表（改成「结构已修好，视觉差异源数据里就没有」）|
| Boss 40 个材质槽 | 产出清单 |
| **第 37–38 轮补充章**（材质结构）| 新增第八章 |

### 二、🔴 发现数字漂移

**写了 `Tools/verify_doc_numbers.py` 做检查：**

```
=== measured ===
  batch gltf         253
  png files          2407
  png MB             339.8
  gotchas            106
  topic documents    31

=== summary 声称 ===
  「104 条坑」  ← 实际 106
  「32 篇专题」 ← 实际 31
```

**两处都过时了（总览写于第 36 轮，之后又加了 2 条坑）。**

### 三、修后

```
- summary says 253 batch glTF, disk has 253
- summary says 2407 PNG, disk has 2407
- summary says 106 gotchas, file has 106
- summary says 31 topic documents, disk has 31

VERDICT: all stated counts match
```

### 四、为什么要专门写个检查脚本

> **参考文档里的数字**漂移**是最难发现的错误 ——
> 它不报错、不明显，只会在有人依赖它时误导。**
>
> **写脚本把「声称的数字」和「磁盘上的事实」对比，是唯一可靠的办法。**

**这和 gotcha #80（报告数字前先问三件事）是同一思路的延伸：
不光要问「这个数字量的是什么」，还要问「这个数字现在还是不是真的」。**

### 五、新增工具

| 工具 | 作用 |
| --- | --- |
| **`Tools/verify_doc_numbers.py`** | **对比摘要声称的数字与磁盘事实，输出判定** |

### 六、最终验收准备（第 40 轮）

**要跑的检查：**
1. `regression_check.py` —— 8 个关键模型
2. `verify_doc_numbers.py` —— 文档数字
3. `batch_export.py --limit 50` —— 批量仍可跑
4. 视口复位
5. 更新断点卡片与目标状态
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 56." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 56; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
