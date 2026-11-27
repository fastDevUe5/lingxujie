"""Link the packaging block and tidy this round's probe scripts.

    python Tools/link_learn_pkg01.py
"""

import os

INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

NET_ROW = ("| **网络第一块** | **`Docs/UE5-LEARN-NET-01.md`** | "
           "🔴 **更正**：复制层在跑（`net.ActorReport` 报 5 个复制 actor）；"
           "传输层无 NetDriver，源码解释 `net.SimulateConnections` 静默原因 |")

PKG_ROW = ("| **打包与优化第一块** | **`Docs/UE5-LEARN-PKG-01.md`** | "
           "✅ **帧时间终于量出来**（GameThread 8.863 ms）：发现 `stat dump*` 写日志；"
           "⚠️ 打包需关编辑器（Live Coding 互斥体），未做 |")

SCRATCH = [
    "Tools/opt_probe.py",
    "Tools/opt_stats.py",
    "Tools/opt_stats2.py",
    "Tools/opt_pie.py",
]

KEEP = ["Tools/opt_cleanup.py"]


def main():
    text = open(INDEX, encoding="utf-8").read()
    if "UE5-LEARN-PKG-01" not in text and NET_ROW in text:
        text = text.replace(NET_ROW, NET_ROW + "\n" + PKG_ROW, 1)
        open(INDEX, "w", encoding="utf-8").write(text)
        print("learning index: added the packaging block")
    else:
        print("learning index: nothing to add")

    root = "C:/Users/tk/Desktop/lingxujie/"
    for relative in SCRATCH:
        path = root + relative
        if os.path.exists(path):
            os.remove(path)
    print("kept: %s" % ", ".join(os.path.basename(p) for p in KEEP))


if __name__ == "__main__":
    main()
