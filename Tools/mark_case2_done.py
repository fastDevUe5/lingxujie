"""Add the second case study to the indexes and record what it corrected.

    python Tools/mark_case2_done.py
"""

DEBUG_INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-DEBUG-INDEX.md"
LEARNING_INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

CASE_ROW = (
    "| **Boss 动画不播放** | **`UE5-DEBUG-CASE-ANIM.md`** | "
    "**`import_and_place.py` 从未设 `animation_mode`，也从未赋 `anim_to_play`** |"
)

CASE2_ROW = (
    "| **SM_Boss001 退化法线** | **`UE5-DEBUG-CASE-NORMALS.md`** | "
    "**`TRANSFORM_TYPE_NOT_SOLID (0x10)` 的几何本来就没有可用法线；导出器当正常数据导出了** |"
)

LESSONS = """- **`mesh_flag & 0xF0` 的四种 TRANSFORM_TYPE**：`0x00` SOLID / `0x10` NOT_SOLID / `0x30` ALIGN_VIEW / `0x50` ILLUSION —— **后三者的法线数据不可信**
- **「有没有法线」和「法线能不能用」是两件事** —— 客户端读了 NOT_SOLID 的法线但不用
- **StaticMesh 的 LOD 数是 `get_num_lods`**，且 **Python 读不到 StaticMesh 的法线** —— 要量就去源文件量
"""


def main():
    text = open(DEBUG_INDEX, encoding="utf-8").read()
    if "CASE-NORMALS" not in text:
        if CASE_ROW in text:
            text = text.replace(CASE_ROW, CASE_ROW + "\n" + CASE2_ROW, 1)
        else:
            text = text.replace("## 七、实战诊断记录（八域完成之后）",
                                "## 七、实战诊断记录（八域完成之后）", 1)
            anchor = "| **Boss 动画不播放** |"
            if anchor in text:
                text = text.replace(CASE_ROW, CASE_ROW + "\n" + CASE2_ROW, 1)
        open(DEBUG_INDEX, "w", encoding="utf-8").write(text)
        print("debug index: added the second case row")
    else:
        print("debug index: already present")

    text = open(LEARNING_INDEX, encoding="utf-8").read()
    if "TRANSFORM_TYPE_NOT_SOLID" not in text:
        anchor = "- **`/Game` 2194 个资产但 `/Game/Moxiang` 只有 370** —— 「项目有 N 个资产」的分母容易搞错"
        if anchor in text:
            text = text.replace(anchor, anchor + "\n" + LESSONS.rstrip(), 1)
            open(LEARNING_INDEX, "w", encoding="utf-8").write(text)
            print("learning index: added the three normal lessons")
        else:
            print("learning index: anchor not found")
    else:
        print("learning index: already present")


if __name__ == "__main__":
    main()
