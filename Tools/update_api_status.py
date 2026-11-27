"""Correct the status document: the API mirror is 164 pages, all verified, not 190 of unknown quality.

Two audits were wrong before this. The first counted 190 files and claimed completeness without checking.
The second used a 1500 byte floor and called fifty-five valid short pages suspicious. The correct test is
whether a file begins with the API page header, which short memberless types do.

    python Tools/rewrite_local_docs.py
"""

import glob
import os
import re

DOC = "C:/Users/tk/Desktop/lingxujie/Docs/LOCAL-UE-DOCS.md"
MANUAL = "C:/Users/tk/Desktop/lingxujie/Docs/UEManual"
API = "C:/Users/tk/Desktop/lingxujie/Docs/PythonAPI"

ARTICLE_LINES = 40
ARTICLE_CHARS = 4000
HEADER = re.compile(r"^# unreal\.")


def api_stats():
    files = [f for f in glob.glob(os.path.join(API, "*.txt"))
             if os.path.basename(f) not in ("MANIFEST.txt", "README.txt")]
    good = 0
    for path in files:
        with open(path, encoding="utf-8", errors="replace") as handle:
            if HEADER.match(handle.read(200)):
                good += 1
    total_bytes = sum(os.path.getsize(f) for f in files)
    return len(files), good, total_bytes


def main():
    text = open(DOC, encoding="utf-8").read()

    count, good, total_bytes = api_stats()
    files = [f for f in glob.glob(os.path.join(MANUAL, "*.md"))
             if not os.path.basename(f).endswith("README.md")]
    manual_bytes = sum(os.path.getsize(f) for f in files)

    articles = 0
    for path in files:
        body = open(path, encoding="utf-8").read()
        lines = len([ln for ln in body.split("\n") if ln.strip()])
        if lines >= ARTICLE_LINES and len(body) >= ARTICLE_CHARS:
            articles += 1

    print("manual: %d pages (%d articles), %.1f KB"
          % (len(files), articles, manual_bytes / 1024.0))
    print("api   : %d pages, %d verified, %.1f KB"
          % (count, good, total_bytes / 1024.0))

    # Replace the two counts in the summary table.
    old_manual = re.search(r"\| \*\*`Docs/UEManual/`\*\* \|[^\n]*\|", text)
    if old_manual:
        new_manual = ("| **`Docs/UEManual/`** | **%d 篇**（%d 真文章 + %d 索引页）| %.1f KB |"
                      % (len(files), articles, len(files) - articles, manual_bytes / 1024.0))
        text = text.replace(old_manual.group(0), new_manual, 1)

    old_api = re.search(r"\| \*\*`Docs/PythonAPI/`\*\* \|[^\n]*\|", text)
    if old_api:
        new_api = "| **`Docs/PythonAPI/`** | **%d 篇 `.txt`，全部验证有页面头** | %.1f KB |" % (
            good, total_bytes / 1024.0)
        text = text.replace(old_api.group(0), new_api, 1)

    # Refresh the header line.
    text = re.sub(
        r"> \*\*最后更新：[^\n]*\*\*",
        "> **最后更新：2026-11-27 · 实测 %d 篇手册（%d 真文章）+ %d 篇已验证 API**"
        % (len(files), articles, good),
        text, count=1)

    addition = """

---

## 九、🔴 API 镜像的两次误判（2026-11-27）

**第一次：** 我说「190 篇 Python API 都在」，**从没验过内容**。
打开 `AnimationBlueprintLibrary.txt` 才发现是 404 页面。

**第二次：** 审计时用了 `MIN_BYTES = 1500` 的下限，把 55 篇判为「可疑」。
**抽查发现它们全是有效的** —— 一个没有方法的结构体只有 285 字节，那就是全部内容。

**正确判据：看文件是否以 `# unreal.<名字>  (UE 5.8 Python API)` 开头。**

```
审计结果
  189 篇
  有效 164（87%）
  404   25
```

**处理：删掉 25 个 404 文件** —— 它们比缺失更糟，因为**看起来有覆盖**。
**现在 164 篇，100% 有页面头。**

**⚠️ 那 25 个名字在文档站确实找不到**（`class/` `struct/` `enum/` `type/` 四种路径全试过），
API 索引页也是 JS 渲染抓不到。**可能本来就不作为 Python API 页存在。**

**规律：**
| 判据 | 对不对 |
| --- | --- |
| 文件数 | ❌ 只说明文件存在 |
| 字节数下限 | ❌ 简单类型天生就短 |
| **页面头** | ✅ |
"""

    if "API 镜像的两次误判" not in text:
        text = text.rstrip("\n") + addition
        print("appended the audit note")

    open(DOC, "w", encoding="utf-8").write(text)
    print("wrote %s" % os.path.basename(DOC))


if __name__ == "__main__":
    main()
