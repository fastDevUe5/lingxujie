"""Append the thirty-third round.

    python Tools/write_round_thirtythree.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 50. 第三十三轮：**PIE 播放验证 —— 编辑器状态不继承**（2026-11-26 34:00）

### 一、做了什么

**在编辑器世界给 Boss 设了动画：**
```
PIEA: animation SK_Boss001_Anim, 3.333 s
PIEA: mode ANIMATION_SINGLE_NODE
PIEA: looping enabled
PIEA: playing
PIEA: get_length 3.3333332538604736
```

**然后 `StartPIE`（`bSimulate: true`），隔 700 ms 抓两张图。**

### 二、结果：差异是噪声，不是运动

```
差异像素: 20,579
差分 4x4 网格：
  601  5377  1524   866      <- 顶部中央 5377 是鸟
 1164  2150  2081  1621
  861   429   576  1755
  321   240   648   365
```

**散布全画面，**没有集中在 Boss 区域**。两张图目视几乎相同。**

### 三、根因（gotcha #103）

> **PIE 创建**新世界**并重新实例化 actor。
> 编辑器世界设置的动画状态不继承到播放世界。**

**不是数据问题，不是导出问题 —— 是「编辑器世界 vs 播放世界」的边界。**

### 四、`StartPIE` 的正确参数（之前踩过）

```json
{"options":{"bSimulate":true,"playMode":"PlayMode_InViewPort","warmupSeconds":2}}
```

**`bSimulate: true` = 世界 tick 但不生成玩家 Pawn —— 适合观察自主 actor。**

### 五、动画这块的最终结论

| 项 | 状态 | 证据 |
| --- | --- | --- |
| `.anm` 有真实运动 | ✅ **已验证** | 20–36 轨在动，摆幅 20–179° |
| 导出的 glTF 携带通道 | ✅ **已验证** | 通道数 25/49/8/15 与轨道数一致 |
| UE 导入产生 AnimSequence | ✅ **已验证** | 四个资产，长度 1.7–3.3 s |
| 编辑器里可见播放 | ❌ 未验证 | `set_position` 不触发求值 |
| PIE 里可见播放 | ❌ 未验证 | 编辑器状态不继承到播放世界 |

**前三条是**数据正确性**；后两条是「怎么在编辑器里驱动它」——
不影响真机游戏（有 tick、有 BeginPlay 里的初始化）。**

### 六、为什么不再往下钻

**已经花了 3 轮在「引擎里怎么驱动动画」上。**

> **投入产出判断：这个问题的答案不影响管线正确性，也不影响最终游戏 —— 只影响我截图给人看。**
>
> **把剩下的轮次用在**可验证的批量产出**上更有价值。**

### 七、新增能力

| 项 | 内容 |
| --- | --- |
| **图像差异分析** | Pillow `ImageChops.difference` + numpy **分 4x4 网格**，判断差异是否集中在目标区域 |
| `StartPIE` | 必填 `options`，`bSimulate: true` 观察自主 actor |

### 八、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **批量材质管线**（5,833 贴图批量转 PNG + 批量导入）—— **可验证** |
| 2 | 批量导入 UE（253 个 gltf 已在盘上）|
| 3 | 最终汇总文档 |
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 50." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 50; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
