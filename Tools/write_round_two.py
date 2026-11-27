"""Append the second learning round to the handoff.

A file rather than an inline command, because the text mixes quotes, pipes and Chinese punctuation
that PowerShell corrupts when passing a heredoc through python -c.

    python Tools/write_round_two.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 18. UE5 学习第二轮：动画两侧 + 材质（2026-11-26 19:00）

### 一、本轮新增三篇

| 文档 | 大小 | 内容 |
| --- | --- | --- |
| **`UE5-ANIMATION-ENGINE.md`** | 8.4 KB | DataModel 42 读 + Controller 42 写 + **完整 C++ 写入配方** |
| **`UE5-ANIMATION-RUNTIME.md`** | 8.7 KB | 槽位机制 / 蒙太奇 / BlendSpace / Notify / 状态机 |
| **`UE5-MATERIALS.md`** | 7.4 KB | 22 个材质工具 + **地面网格感实测诊断** |

### 二、两条重要结论

**① 帧率从「阻塞」降为「调参」**

```
AnimationBlueprintLibrary.GetSequenceLength   <- Python 可用
AnimationBlueprintLibrary.GetNumFrames        <- Python 可用
所以 帧率 = GetNumFrames / GetSequenceLength
```

写入时 `Controller.SetFrameRate` 由我们决定。**所以原始帧率不影响能不能导入。**

**② 地面网格感的真正病因（实测）**

```
M_Moxiang_Ground: 3 个节点
  u_tiling = v_tiling = 96
  一张贴图覆盖 533 cm
  tile_108_road01 是 64x64 像素（已验证）
  所以 1 像素 = 8.3 cm，全图重复 9,216 次
```

**这不是参数问题，是素材分辨率问题。改平铺数治不了。**

### 三、一个诚实的发现

**引擎 `Engine/Content` 里没有自带骨骼网格（无 Mannequin / SKM_*）。**

**所以「练一次动画蓝图」做不了 —— 需要先有 SkeletalMesh，而那要等 .mod 转换。**

**动画这块：机制全懂，零实操，且被前置条件卡住。**

### 四、掌握度变化

| 域 | 上一轮 | 本轮 |
| --- | --- | --- |
| 动画（引擎侧）| 30% | **55%** |
| 动画（运行时）| — | **50%** |
| 材质 | 35% | **35%**（结构全懂，零实操）|

### 五、下一步（能真的动手的）

**材质三平面映射 —— 不需要前置条件**

```
create_material -> add_expression x15 -> get_expression_input_names
-> connect_expressions -> recompile -> 挂到地形 -> 截图对比
```

**目标：同时验证工具链可用 + 三平面有效 + 观感改善。**
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 18." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 18; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
