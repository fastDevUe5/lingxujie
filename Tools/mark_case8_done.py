"""Add case 008 to the indexes.

    python Tools/mark_case8_done.py
"""

DEBUG_INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-DEBUG-INDEX.md"
LEARNING_INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

ANCHOR_D = (
    "| **历史警告 vs 当前状态** | **`UE5-DEBUG-CASE-MIP.md`** | "
    "**「贴图无 mip」是 DDS 导入失败的残留；实测 `NumMips=10` 完整，资产健康** |"
)

NEW_D = (
    "| **材质修复的视觉验证** | **`UE5-DEBUG-CASE-MATFIX.md`** | "
    "**赋 `M_Boss_Mob01` 后生物从灰变红棕；同一次改动全画面 0.99% / 猜错区域 8.8% / 正确区域 24%** |"
)

ANCHOR_L = "| 贴图无 mip | `UE5-DEBUG-CASE-MIP.md` | ✅ 历史残留（实测 10 级完整）|"
NEW_L = ("| 贴图无 mip | `UE5-DEBUG-CASE-MIP.md` | ✅ 历史残留（实测 10 级完整）|\n"
         "| 材质修复验证 | `UE5-DEBUG-CASE-MATFIX.md` | ✅ **视觉验证：24% 像素变化，画面可见** |")

LESSON = ("- **小物体的像素差要按物体区域算** —— 同一改动全画面 0.99% / 正确区域 24%；"
          "先看图定位变化，再框区域算数字\n")


def main():
    text = open(DEBUG_INDEX, encoding="utf-8").read()
    if "CASE-MATFIX" not in text:
        if ANCHOR_D in text:
            text = text.replace(ANCHOR_D, ANCHOR_D + "\n" + NEW_D, 1)
            open(DEBUG_INDEX, "w", encoding="utf-8").write(text)
            print("debug index: added the eighth case row")
        else:
            print("debug index: anchor not found")
    else:
        print("debug index: already present")

    text = open(LEARNING_INDEX, encoding="utf-8").read()
    if "CASE-MATFIX" not in text and ANCHOR_L in text:
        text = text.replace(ANCHOR_L, NEW_L, 1)
        open(LEARNING_INDEX, "w", encoding="utf-8").write(text)
        print("learning index: added the case row")

    text = open(LEARNING_INDEX, encoding="utf-8").read()
    if "小物体的像素差" not in text:
        anchor = "- **`listtextures <名字>` 有 `NumMips` 列**"
        if anchor in text:
            text = text.replace(anchor, LESSON + anchor, 1)
            open(LEARNING_INDEX, "w", encoding="utf-8").write(text)
            print("learning index: added the small-object lesson")


if __name__ == "__main__":
    main()
