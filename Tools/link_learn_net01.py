"""Link the network block and tidy this round's scripts.

    python Tools/link_learn_net01.py
"""

import os

INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

UI_ROW = ("| **UI/UMG 第一块** | **`Docs/UE5-LEARN-UI-01.md`** | "
          "🔴 **负面结论**：只通第 1 环（建资产）；树不可访问、面板无构造方法、"
          "`construct` 后仍 0×0、`add_to_viewport` 无效（PIE 亦同）|")

NET_ROW = ("| **网络第一块** | **`Docs/UE5-LEARN-NET-01.md`** | "
           "🔴 **更正**：复制层在跑（`net.ActorReport` 报 5 个复制 actor）；"
           "传输层无 NetDriver，源码解释 `net.SimulateConnections` 静默原因 |")

SCRATCH = ["Tools/net_a_probe.py", "Tools/net_b_simulate.py"]
KEEP = ["Tools/net_cleanup.py"]


def main():
    text = open(INDEX, encoding="utf-8").read()
    if "UE5-LEARN-NET-01" not in text and UI_ROW in text:
        text = text.replace(UI_ROW, UI_ROW + "\n" + NET_ROW, 1)
        open(INDEX, "w", encoding="utf-8").write(text)
        print("learning index: added the network block")
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
