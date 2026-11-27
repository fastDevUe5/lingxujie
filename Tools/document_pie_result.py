"""Record the PIE result and close the animation-playback question honestly.

The animation was assigned and playing in the editor world, PIE launched in simulate mode so the world
ticks, and two captures 700 ms apart differ across the whole frame with nothing concentrated on the
boss. The differences are noise, not motion.

The cause is understood and worth writing down rather than working around: PIE builds a new world and
reinstantiates its actors, so animation state set in the editor world does not carry over. Setting it
from Python inside PIE would need a handle on the play world, which is a separate problem from whether
the pipeline works.

    python Tools/document_pie_result.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/BATCH-EXPORT-STATUS.md"

SECTION = """
---

## 十九、PIE 播放验证：编辑器状态不继承（第 33 轮）

### 19.1 做了什么

**在编辑器世界：**
```
PIEA: animation SK_Boss001_Anim, 3.333 s
PIEA: mode ANIMATION_SINGLE_NODE
PIEA: looping enabled
PIEA: playing
PIEA: get_length 3.3333332538604736
```

**然后 `StartPIE`（`bSimulate: true`，世界会 tick 但不生成玩家），
隔 700 ms 抓两张。**

### 19.2 结果：差异是噪声，不是运动

```
差异像素: 20,579
x 范围: 0..1179    y 范围: 0..683
```

**差异分布（4×4 网格，像素数）：**
```
  601  5377  1524   866      <- 顶部中央 5377 是鸟，不是 Boss
 1164  2150  2081  1621
  861   429   576  1755
  321   240   648   365
```

**散布全画面，**没有集中在 Boss 区域**。两张图目视几乎相同。**

### 19.3 根因

> **PIE 会创建**新世界**并重新实例化 actor。
> 在**编辑器世界**设置的动画状态（`set_animation_asset` + `set_playing`）**不继承到 PIE 世界**。**

**这不是数据问题，也不是导出问题 —— 是「编辑器世界 vs 播放世界」的边界。**

**要在 PIE 里设置，需要拿到播放世界的句柄，
那是另一个问题（`UnrealEditorSubsystem.get_game_world()` 之类），
与「管线是否正确」无关。**

### 19.4 动画这块的最终结论

| 项 | 状态 | 证据 |
| --- | --- | --- |
| `.anm` 有真实运动 | ✅ **已验证** | 20–36 轨在动，摆幅 20–179° |
| 导出的 glTF 携带通道 | ✅ **已验证** | 通道数 25/49/8/15 与轨道数一致 |
| UE 导入产生 AnimSequence | ✅ **已验证** | 四个资产，长度 1.7–3.3 s |
| 编辑器里可见播放 | ❌ **未验证** | `set_position` 不触发求值 |
| PIE 里可见播放 | ❌ **未验证** | 编辑器状态不继承到播放世界 |

**前三条是数据正确性；后两条是「怎么在编辑器里驱动它」——
后者不影响真机游戏（有 tick、有 BeginPlay 里的初始化）。**

### 19.5 为什么不再往下钻

**已经花了 3 轮在「引擎里怎么驱动动画」上。**
**这个问题的答案不影响管线正确性，也不影响最终游戏 —— 只影响我截图给人看。**

> **投入产出判断：**
> **把剩下的轮次用在**可验证的批量产出**上（材质批量、导入批量），
> 比继续解 PIE 世界访问更有价值。**

### 19.6 新增知识

| 项 | 内容 |
| --- | --- |
| `StartPIE` 参数 | 必须给 `{"options":{"bSimulate":bool,"playMode":"PlayMode_InViewPort","warmupSeconds":N}}` |
| `bSimulate: true` | 世界 tick 但不生成玩家 Pawn，适合观察自主 actor |
| 图像差异分析 | Pillow `ImageChops.difference` + numpy 分网格，能判断「差异是否集中在目标区域」 |
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 十九、PIE 播放验证" in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
