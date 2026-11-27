"""Repair gotcha 93's code fence and add 94 and 95.

The fence lost two backticks somewhere in transcription, and the two entries from the last round
never landed. Writing them from a file rather than an inline command keeps the UTF-8 intact - an
inline command with Chinese text has been mangled more than once in this project.

    python Tools/fix_gotchas_93_to_95.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-Gotchas.md"

BROKEN_FENCE = "  `python\n"
FIXED_FENCE = "  ```python\n"
BROKEN_CLOSE = "  `\n\n  **②"
FIXED_CLOSE = "  ```\n\n  **②"

NEW_ENTRIES = """
## 94. 骨骼索引是稀疏的，不能直接当关节索引用

- **症状**：导出 `boss001.mod` 报
  `struct.error: 'H' format requires 0 <= number <= 65535`
- **根因**：`boss001` 有 **67 根骨骼，但索引是 11..83**（稀疏的）。
  我把**骨骼索引**直接写进 glTF 的 `JOINTS_0`，于是出现 83 > 67
- **为什么之前没暴露**：
  - `108_bird` 9 骨骼，索引 0..8 连续
  - `198_bobu` 31 骨骼，索引 0..30 连续
  - **`boss001` 67 骨骼稀疏 —— 第三个样本才暴露**
- **修法**：
  ```python
  ordered = sorted(bones, key=lambda b: b["index"])
  joint_of = {b["index"]: i for i, b in enumerate(ordered)}
  mapped = joint_of.get(bone_index)
  if mapped is not None:
      js.append(mapped)
  ```
- **教训**：**关节索引 = 该骨骼在 skin 关节列表里的位置，不是骨骼自己的编号**
- **出处**：2026-11-26，真 Boss 本体导入

## 95. 文件名告诉你它属于谁，不告诉你它是什么

- **症状**：`boss_cowf_01.mod` 有 38 骨骼、36/38 匹配动画、49 通道 ——
  一切都「对」，但导入后画面里全是大平面，看不出是 Boss
- **根因**：这个文件的 24 个网格块**全是火焰面片**：
  `fire03` / `BU_fire_boom_01` / `fire_U_b_08` —— 它是**Boss 身上的火**
- **判断方法：看网格块的名字**
  - 含 `fire` / `eff` / `smoke` / `boom` / `fog` → **特效**
  - 含 `head` / `arm` / `shoulder` / `eye` / `body` → **身体**
- **`boss001.mod` 才是本体**：`boss01_head` / `boss01_armL` / `boss01_eyeR` …
  17 个身体部件，0 个特效块，尺寸 0.05–1.11 米
- **教训**：**「有骨骼 + 有动画」不等于「是角色」。**
  判断一个文件是什么，只能看它里面有什么几何，不能看名字、不能看骨骼数
- **出处**：2026-11-26，找真身
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    changed = 0
    if BROKEN_FENCE in text:
        text = text.replace(BROKEN_FENCE, FIXED_FENCE)
        changed += 1
    if BROKEN_CLOSE in text:
        text = text.replace(BROKEN_CLOSE, FIXED_CLOSE)
        changed += 1
    print("fence repairs applied: %d" % changed)

    if "## 94." in text:
        print("entries already present")
    else:
        text = text.rstrip("\n") + "\n" + NEW_ENTRIES
        print("added entries 94 and 95")

    open(PATH, "w", encoding="utf-8").write(text)

    # Report what the file now contains.
    joined = open(PATH, encoding="utf-8").read()
    import re
    numbers = [int(m.group(1)) for m in re.finditer(r"^## (\d+)\.", joined, re.M)]
    print("gotcha entries: %d, highest: %d" % (len(numbers), max(numbers)))


if __name__ == "__main__":
    main()
