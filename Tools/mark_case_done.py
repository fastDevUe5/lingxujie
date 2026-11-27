"""Add the case-study section to the debugging index.

    python Tools/mark_case_done.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-DEBUG-INDEX.md"

SECTION = """
## 七、实战诊断记录（八域完成之后）

| 案例 | 文档 | 结论 |
| --- | --- | --- |
| **Boss 动画不播放** | **`UE5-DEBUG-CASE-ANIM.md`** | **`import_and_place.py` 从未设 `animation_mode`，也从未赋 `anim_to_play`** |

**这次实战更正了两条既有结论（两条都是同一毛病）：**
- **`set_position` 会重新求值** —— 之前以为不会，是因为**根本没有动画被赋值**
- **`get_bone_transform` 能读骨骼** —— 之前用 `AnimPoseExtensions.get_bone_pose` 挂死，误判为「读不到」

> **共同点：把「我用这个方法失败了」当成「这件事做不到」。**
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "实战诊断记录" in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended the case-study section")


if __name__ == "__main__":
    main()
