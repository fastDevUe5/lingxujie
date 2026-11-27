"""Append the twenty-first round.

    python Tools/write_round_twentyone.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 38. 第二十一轮：批量导出跑通（2026-11-26 26:00）

### 一、结果

| 批次 | 导出 | 带动画 | 失败 |
| --- | --- | --- | --- |
| 前 25（初版）| 25 | 1 | **10** |
| 前 30（修后）| 30 | 1 | **0** |
| **前 100** | **100** | **2** | **0** |

**失败 10 → 0，靠两个解析修复。**

### 二、两个解析 bug

**① `.mod` 的法线是条件性的（gotcha #88）**

```c
if (shadeType == SHADE_TYPE_LIGHT_MAP)         ReadLightTexture();
else if (transformType != TRANSFORM_TYPE_ALIGN_VIEW)  FSRead(normals, 12*V);
```

**`mesh_flag` 位域：`0x0F`=SHADE_TYPE（3=LIGHT_MAP）、`0xF0`=TRANSFORM_TYPE（0x30=ALIGN_VIEW）。**

**我无条件读法线 → ALIGN_VIEW 和 LIGHT_MAP 的网格全部越界。**

**② `.anm` 走块撞进尾部资源引用（gotcha #89）**

**修法：块大小自校验**
```python
expected = 152 + pos_n*20 + rot_n*24 + scale_n*40
if expected != size: break
```

**同一个手法在 `.mod` 上已经用过：让数据自己证明自己。**

### 三、为什么 100 个里只有 2 个带动画

**全库统计：**

| 类别 | 数量 | 占比 |
| --- | --- | --- |
| `.mod` 总 | 5,305 | 100% |
| **`bones = 0`（道具/特效）** | **3,412** | **64%** |
| `bones > 0`（有骨架）| 1,893 | 36% |
| 其中 `bones > 60` | 1,385 | 26% |

**字母序前 100 个是 `101_*` … `108_*`，绝大多数是场景道具。
道具的动画走**顶点/UV 轨**（`dwAnimatedMeshKeyNum` 和 UV 矩形），不是骨骼 —— 这部分还没接。**

### 四、配对规则是错的（下一步）

**`70003cn02_*` 有 **68 骨骼**但没配上动画 —— 文件名和 `.anm` 完全对不上。**

**真正的映射在 `.chx` 容器（纯文本）：**
```
*MOD_FILE_NUM   1
*MOD_FILE_NAME  L001.MOD
*MOTION_NUM     12
    L001_01.anm
    L001_02.anm
```

**→ 下一轮：读 `.chx` 做正确配对，不猜文件名。**

### 五、新增工具与文档

| 产出 | 说明 |
| --- | --- |
| **`Tools/batch_export.py`** | **批量导出（`--limit` / `--pattern`）** |
| `Tools/find_shade_flag.py` | 查 mesh_flag 位域 |
| **`Docs/BATCH-EXPORT-STATUS.md`** | 完整统计 + 两个 bug + 下一步 |
| **gotcha #88/#89** | 法线条件性 / anm 自校验 |

### 六、用法

```powershell
python Tools\\batch_export.py --limit 100
python Tools\\batch_export.py --limit 30 --pattern "n0"
```

**输出：`Assets/Moxiang/ue_import/batch/`**

### 七、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **读 `.chx` 做正确配对** |
| 2 | 道具顶点/UV 动画 |
| 3 | 批量导入 UE |
| 4 | 材质接入 |
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 38." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 38; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
