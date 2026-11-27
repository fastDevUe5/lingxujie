"""Append the twenty-second round.

    python Tools/write_round_twentytwo.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 39. 第二十二轮：`.chx` 配对接入（2026-11-26 26:30）

### 一、`.chx` 解析结果

```
chx files parsed: 1081 models, 12 without a parse
animation references: 21919 across 1081 models
models with at least one animation: 926
animation references resolved: 21878, missing: 41     <- 99.8%
```

**12 个解析失败是 `m_do+N.chx` / `m_gum+N.chx`（武器强化文件，结构不同）。**

### 二、格式与两个坑（gotcha #90）

**文本格式：**
```
*MOD_FILE_NUM	1

*MOD_FILE_NAME	P005_A.MOD
*MOTION_NUM		10
	P005_A_01.ANM
	...
```

**坑 1**：部分 `.chx` 前面有**二进制头**（`}   Q     øê`）→ 从 `*MOD_FILE_NUM` 定位
**坑 2**：名字大小写和磁盘不一致（`boss_cowi_01` → `Boss_cowI_01.anm`）→ 不区分大小写 + 目录扫描兜底

### 三、真角色导出来了

**`--pattern boss` 实测：**

| 模型 | 骨骼 | 网格 | 通道 | glTF |
| --- | --- | --- | --- | --- |
| `boss_cowf_01` | 38 | 24 | **8** | 56 KB |
| `boss_cowi_01` | 38 | 35 | **8** | 73 KB |
| `boss_cowking_01` | 38 | 10 | **8** | 35 KB |
| `boss_cowking_05` | **86** | 67 | 0 | 134 KB |

**目前 150 个 gltf 落盘，其中 5 个带动画。**

### 四、两个已记录但未解决的缺口

**① 每个模型只导第一个动画**

**`.chx` 里每个模型列**几十个**动画：**
```
boss_01 -> boss01_stand, boss01_move, boss01_attack01, boss01_attack02
```
**当前只取 `listed[0]`。**

**② 38 骨骼只出 8 通道**

**两个可能：**
- 这个 `.anm` 只驱动 8 根骨骼（其余不动）
- 骨骼名不匹配

**判断方法：比对 `.anm` 骨骼名与 `.mod` 骨骼名的交集大小。**

### 五、新增工具

| 工具 | 作用 |
| --- | --- |
| **`Tools/parse_chx.py`** | **解析所有 `.chx`，建映射（1,081 模型）** |
| `Tools/wire_chx.py` | 接入批量导出 |
| `Tools/batch_export.py` | 已用 `.chx` 优先、文件名兜底 |

### 六、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **一个模型导出多个动画**（`listed` 全部） |
| 2 | **比对骨骼名交集**，查明为何 38 骨骼只有 8 通道 |
| 3 | 批量导入 UE |
| 4 | 材质接入 |
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 39." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 39; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
