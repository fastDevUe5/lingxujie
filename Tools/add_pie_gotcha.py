"""Add gotcha 103 about PIE worlds, written from a file to keep the UTF-8 intact.

    python Tools/add_pie_gotcha.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-Gotchas.md"

ENTRY = """
## 103. PIE 会建新世界，编辑器里设的动画状态不继承

- **症状**：在编辑器世界给 `SkeletalMeshComponent` 设了动画并 `set_playing(True)`，
  启动 PIE（`bSimulate: true`，世界会 tick），隔 700 ms 抓两张图 ——
  **差异散布全画面，Boss 没动**
- **根因**：**PIE 创建新世界并重新实例化 actor**，
  编辑器世界的动画状态**不继承到播放世界**
- **诊断方法**：用 Pillow 做图像差异并**分 4x4 网格统计**，
  看差异是否集中在目标区域。散布全画面 = 噪声；集中一处 = 真的动了
  ```python
  arr = np.asarray(ImageChops.difference(a, b)).astype(int)
  mask = arr.sum(axis=2) > 10
  # 按 4x4 分块打印像素数
  ```
- **`StartPIE` 参数**（必填）：
  ```json
  {"options":{"bSimulate":true,"playMode":"PlayMode_InViewPort","warmupSeconds":2}}
  ```
  **`bSimulate: true` = 世界 tick 但不生成玩家 Pawn，适合观察自主 actor**
- **要设 PIE 里的状态**：需要拿播放世界的句柄（`get_game_world()` 之类），
  那是另一个问题，与管线正确性无关
- **出处**：2026-11-26，PIE 播放验证
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 103." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(ENTRY)
    print("added gotcha 103")


if __name__ == "__main__":
    main()
