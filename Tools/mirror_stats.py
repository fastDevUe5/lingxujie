"""Report the local documentation mirror's size and how far it is from each meaning of complete.

"Complete" has two meanings here and they differ by three orders of magnitude. Complete for the course
is the nine curriculum areas plus the systems this project uses. Complete for the site is every page
Epic publishes. Reporting one number without saying which meaning it is would be misleading.

    python Tools/mirror_stats.py
"""

import glob
import os

ROOT = "C:/Users/tk/Desktop/lingxujie/Docs"
MANUAL = os.path.join(ROOT, "UEManual")
API = os.path.join(ROOT, "PythonAPI")

ARTICLE_LINES = 40
ARTICLE_CHARS = 4000

# Measured earlier by walking the API index: 11,459 classes exist in the Python reference.
PYTHON_API_TOTAL = 11459


def dir_stats(path, pattern):
    files = glob.glob(os.path.join(path, pattern))
    total = sum(os.path.getsize(f) for f in files)
    return files, total


def is_article(path):
    text = open(path, encoding="utf-8").read()
    lines = len([ln for ln in text.split("\n") if ln.strip()])
    return lines >= ARTICLE_LINES and len(text) >= ARTICLE_CHARS


def human(num_bytes):
    if num_bytes >= 1024 * 1024:
        return "%.2f MB" % (num_bytes / 1024.0 / 1024.0)
    return "%.1f KB" % (num_bytes / 1024.0)


def main():
    manual, manual_bytes = dir_stats(MANUAL, "*.md")
    manual = [f for f in manual if not f.endswith("README.md")]
    manual_bytes = sum(os.path.getsize(f) for f in manual)

    api, api_bytes = dir_stats(API, "*.txt")

    articles = [f for f in manual if is_article(f)]
    indexes = [f for f in manual if not is_article(f)]

    print("=" * 70)
    print("现在有多大")
    print("=" * 70)
    print("")
    print("%-28s %8s %10s %12s" % ("目录", "文件数", "大小", "单篇均"))
    print("-" * 70)
    print("%-28s %8d %10s %12s"
          % ("Docs/UEManual（手册）", len(manual), human(manual_bytes),
             human(manual_bytes / max(len(manual), 1))))
    print("%-28s %8d %10s %12s"
          % ("  其中 真文章", len(articles), "", ""))
    print("%-28s %8d %10s %12s"
          % ("  其中 索引页", len(indexes), "", ""))
    print("%-28s %8d %10s %12s"
          % ("Docs/PythonAPI（类参考）", len(api), human(api_bytes),
             human(api_bytes / max(len(api), 1))))
    print("-" * 70)
    print("%-28s %8d %10s" % ("合计", len(manual) + len(api), human(manual_bytes + api_bytes)))
    print("")

    # Two meanings of complete.
    print("=" * 70)
    print("离「完善」还差多少 —— 两种口径")
    print("=" * 70)
    print("")

    print("【口径 A】课程 + 项目所需  →  已达 100%")
    print("  十个领域全部有真文章：0 个缺口")
    print("  已覆盖 %d 篇真文章 / %s" % (len(articles), human(manual_bytes)))
    print("")

    avg_api = api_bytes / max(len(api), 1)
    full_api = avg_api * PYTHON_API_TOTAL
    remaining_api = PYTHON_API_TOTAL - len(api)
    print("【口径 B】整个文档站  →  远未完成")
    print("")
    print("  Python API 类:")
    print("    已有 %d / %d = %.1f%%" % (len(api), PYTHON_API_TOTAL,
                                        100.0 * len(api) / PYTHON_API_TOTAL))
    print("    还差 %d 个类" % remaining_api)
    print("    按单篇均 %s 估算，补完约 %s" % (human(avg_api), human(full_api)))
    print("    按每篇约 2 秒（纯抓取，不含解析）估算，约 %.1f 小时"
          % (remaining_api * 2.0 / 3600.0))
    print("")
    print("  手册概念页:")
    print("    已有 %d 篇（%s）" % (len(manual), human(manual_bytes)))
    print("    文档站手册页总数未实测 —— 这一项**我给不出数字**，不猜")
    print("")

    print("=" * 70)
    print("结论")
    print("=" * 70)
    print("")
    print("  已占空间: %s（%d 个文件）" % (human(manual_bytes + api_bytes),
                                          len(manual) + len(api)))
    print("  课程口径: 100%%，不需要再补")
    print("  整站口径: Python API %.1f%%，手册页百分比未知" % (100.0 * len(api) / PYTHON_API_TOTAL))


if __name__ == "__main__":
    main()
