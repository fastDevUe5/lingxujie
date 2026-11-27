"""Correct the local document status, which said twelve pages failed and never got updated.

The mirror now holds nineteen manual pages because the slugs were verified by title instead of guessed.
The status document still described three. This rewrites the relevant sections from the measured state
and records the two mistakes that delayed it.

    python Tools/update_local_docs_status.py
"""

import glob
import os

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/LOCAL-UE-DOCS.md"


def main():
    manual = sorted(glob.glob("C:/Users/tk/Desktop/lingxujie/Docs/UEManual/*.md"))
    manual = [f for f in manual if not f.endswith("README.md")]
    api = glob.glob("C:/Users/tk/Desktop/lingxujie/Docs/PythonAPI/*.txt")

    manual_kb = sum(os.path.getsize(f) for f in manual) / 1024.0
    api_kb = sum(os.path.getsize(f) for f in api) / 1024.0

    print("measured: manual %d pages (%.1f KB), python api %d files (%.1f KB)"
          % (len(manual), manual_kb, len(api), api_kb))

    text = open(PATH, encoding="utf-8").read()

    old_table = """| 目录 | 内容 | 来源 |
| --- | --- | --- |
| **`Docs/PythonAPI/`** | **UE 5.8 Python API 类参考**（156 篇，1.3 MB） | `dev.epicgames.com/.../python-api/class/` |
| **`Docs/UEManual/`** | **官方手册摘录**（3 篇，71 KB） | `dev.epicgames.com/documentation/.../unreal-engine/` |"""

    new_table = """| 目录 | 内容 | 来源 |
| --- | --- | --- |
| **`Docs/PythonAPI/`** | **UE Python API 类参考**（**%d 篇 `.txt`**，%.1f KB） | `dev.epicgames.com/.../python-api/class/` |
| **`Docs/UEManual/`** | **官方手册摘录**（**%d 篇 `.md`**，%.1f KB） | `dev.epicgames.com/documentation/.../unreal-engine/` |

> **⚠️ `PythonAPI` 是 `.txt` 不是 `.md`** —— 用 `glob("*.md")` 去找会以为它是空的。
> **2026-11-26 我自己就踩了这个，以为 190 篇都不见了。**""" % (
        len(api), api_kb, len(manual), manual_kb)

    if old_table in text:
        text = text.replace(old_table, new_table, 1)
    else:
        print("table anchor not found; skipping the table update")

    old_note = """**其余 12 篇的 slug 猜错了，抓回来是空页**（`nanite`、`material-editor`、`landscape-technical` 等）。
要补的话，去文档站确认准确 URL 再加进 `Tools/mirror_manual_pages.py` 的 `PAGES` 里。"""

    new_note = """**已收录 %d 篇。**2026-11-26 补齐，覆盖本轮学习计划的八个模块：

```
nanite / nanite-technical / lumen-technical / lumen-performance
niagara / skeletal-animation / materials / import-static-meshes
landscape-technical / world-partition / post-process-materials
asset-management / command-line-arguments / level-editor
instanced-materials / fbx-static-mesh
python-scripting / python-with-ai-agents / unreal-mcp
```

**还有 4 个主题没找到正确 slug**：`umg`（UI）、`physics`、`static-mesh-lod`、`lighting`。
下次用 `Tools/resolve_doc_slugs.py` 补，别猜。""" % len(manual)

    if old_note in text:
        text = text.replace(old_note, new_note, 1)
    else:
        print("note anchor not found; skipping the note update")

    addition = """

---

## 七、🔴 补齐这 16 篇时犯的两个错（2026-11-26）

**① 第一个探针是坏的。**
写了个脚本把 20 个 slug 全判「成功」，因为用了 `response.read(4000)` 然后拿
**4000 字节**当成功条件 —— 那是我自己的截断长度，不是页面大小。

**修法：加了负对照 `this-page-does-not-exist-at-all-xyz`。**
实测发现**站点对任何路径都返回 HTTP 200**，真伪只能看 `<title>`：
- 真页面 → 有 `<title>X | Unreal Engine 5.9 Documentation`
- 假页面 → **没有 `<title>`，body 也很短**

**② 我先去抓了网页，没查本地已有副本。**
`Docs/LOCAL-UE-DOCS.md` 早就写明了镜像范围和失败原因，我跳过它直接 fetch 了一遍，
重复了已经做过的工作。

**→ 两件事同一个形状：不先确认「现在是什么状态」就动手。**

**验证过的 slug 规律：**
- **多数要 `-in-unreal-engine` 后缀**（`nanite-virtualized-geometry-in-unreal-engine`）
- 少数不带（`nanite-technical-details`、`lumen-technical-details-in-unreal-engine` 后者带）
- **不能靠规律猜，只能逐条验标题**
"""

    if "补齐这 16 篇时犯的两个错" not in text:
        text = text.rstrip("\n") + addition
        print("appended the mistakes section")

    open(PATH, "w", encoding="utf-8").write(text)
    print("wrote LOCAL-UE-DOCS.md")


if __name__ == "__main__":
    main()
