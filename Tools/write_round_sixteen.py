"""Append the sixteenth round and update the index.

    python Tools/write_round_sixteen.py
"""

NEXT = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"
INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

SECTION = """

## 33. 第十六轮：`.anm` 动画格式解开 + 帧率 = 30 fps（2026-11-26 23:30）

### 一、两个结论

**① `.anm` 容器结构与 `.mod` 同构**

```
[文件头（长度不固定！）]
[0xF000 块 × N]        每块 = 8 字节头（marker 0xF000 + size）+ 152 字节 FILE_MOTION_OBJECT_HEADER + 关键帧
[尾部资源引用]
```

**⚠️ 头长度**不固定**：`108_birda.anm` 里第一个块在 **206**，不是研究区文档说的 160。
160..206 之间是堆地址 —— 写入时把运行时指针也 dump 了。
**所以必须扫描 `00 F0 00 00` 找块，不要假设偏移。**

**② 帧率 = 30 fps（推导）**

```
Bone07 位移:  ticks=160/480/800  frame=0/2/4  → 160 ticks/帧
跨 60 个文件统计:  distinct ticks-per-frame = [1.0, 160.0]  ← 几乎全是 160
4800 ticks/秒 ÷ 160 = 30.0 fps   ← 唯一干净整数
```

**4800 是 3ds Max 的 `TICKS_PER_SECOND`，而墨香骨架是标准 Biped（`Bip01 R Finger` 出现 16,052 次）。**

**→ 时间换算：`time_seconds = ticks / 4800.0`**

### 二、字节数学精确验证

**`108_birda.anm` 全部 11 块，每块 `expected == size`：**

```
152 + 136×24            = 3416  ✓  （纯旋转轨）
152 + 136×24 + 135×20   = 6116  ✓  （旋转 + 位移轨）
```

**11 块无一块不吻合。**

### 三、关键帧结构（源码 `CMotionObject::ReadFile`）

```c
struct FILE_MOTION_OBJECT_HEADER {   // 152 字节
    DWORD dwIndex, dwRotKeyNum, dwPosKeyNum, dwScaleKeyNum, dwAnimatedMeshKeyNum;
    char  szObjectName[128];         // +20
    CMotionFlag motionFlag;          // +148
};

struct POS_KEY   { DWORD dwTicks; DWORD dwFrame; VECTOR3 v3Pos; };   // 20
struct ROT_KEY   { DWORD dwTicks; DWORD dwFrame; QUARTERNION Q; };   // 24
struct SCALE_KEY { DWORD dwTicks; DWORD dwFrame; VECTOR3 v3Scale;
                   VECTOR3 v3ScaleAxis; float fScaleAxisAng; };     // 40
```

**顺序：POS → ROT → SCALE（不是 ROT 先）。**

### 四、动画链路现在完整

| 环节 | 状态 |
| --- | --- |
| `.mod` 网格 + 蒙皮 | ✅ 解开（第 14 轮）|
| 导出 glTF | ✅ 验证（第 15 轮）|
| SkeletalMesh in UE | ✅ 鸟已可见（第 15 轮）|
| **`.anm` 动画 + 30fps** | ✅ **本轮解开** |
| 导出动画 glTF | 待做（纯工程）|

### 五、新增文档与工具

| 产出 | 说明 |
| --- | --- |
| **`Docs/ANM-FORMAT-SOLVED.md`** | 完整格式 + 帧率推导 + 伪代码 |
| `Tools/inspect_anm.py` | dump 头部 + 首块 |
| `Tools/scan_anm_blocks.py` | 扫描所有块（不假设头长度）|
| `Tools/parse_anm_motion.py` | 按客户端结构解析 + 逐块验算 |
| `Tools/verify_anm_tickrate.py` | 跨 60 文件统计 → 帧率 |

### 六、下一轮

**写 `.anm` → glTF animation 导出器（纯工程）：**

```
1. 解析 .anm（工具已有）
2. 每个骨骼的 rot/pos/scale 关键帧 → glTF animation channel
3. time = ticks / 4800.0
4. 和网格一起导入（AssetImportTask 不钉 factory）
5. 验证：动画能否播
```
"""


def main():
    text = open(NEXT, encoding="utf-8").read()
    if "## 33." not in text:
        with open(NEXT, "a", encoding="utf-8") as handle:
            handle.write(SECTION)
        print("appended section 33")
    else:
        print("section already present")

    index = open(INDEX, encoding="utf-8").read()
    old = "| **`.mod` → UE 骨骼网格** |"
    new = ("| **`.anm` 动画格式 / 帧率** | **`Docs/ANM-FORMAT-SOLVED.md`** | "
           "**帧率 30 fps（ticks/4800 推导）** |\n"
           "| **`.mod` → UE 骨骼网格** |")
    if old in index and "ANM-FORMAT-SOLVED" not in index:
        index = index.replace(old, new, 1)
        open(INDEX, "w", encoding="utf-8").write(index)
        print("index updated")
    else:
        print("index row already changed")


if __name__ == "__main__":
    main()
