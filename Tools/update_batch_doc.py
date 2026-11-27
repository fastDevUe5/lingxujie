"""Record the chx pairing result in the batch status document.

    python Tools/update_batch_doc.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/BATCH-EXPORT-STATUS.md"

SECTION = """
---

## 八、`.chx` 配对：已接入（第 22 轮）

### 8.1 `.chx` 解析结果

**全库 1,211 个 `.chx`，解析出 1,081 个模型：**

```
chx files parsed: 1081 models, 12 without a parse
animation references: 21919 across 1081 models
models with at least one animation: 926
animation references resolved: 21878, missing: 41     <- 99.8%
```

**12 个解析失败的是 `m_do+N.chx` / `m_gum+N.chx`（武器强化文件，结构不同）。**

### 8.2 格式与两个坑

**文本格式：**
```
*MOD_FILE_NUM	1

*MOD_FILE_NAME	P005_A.MOD
*MOTION_NUM		10
	P005_A_01.ANM
	P005_A_02.ANM
	...
```

**坑 1：有些 `.chx` 前面有**二进制头****
```
m_do+10.chx 开头是 `}   Q     øê`，然后才是 `*MOD_FILE_NUM`
```
**→ 从 `*MOD_FILE_NUM` 定位文本起点，不要从字节 0 开始。**

**坑 2：列表后面还有二进制尾**
**→ 遇到不以 `.ANM` 结尾的行就停止收集。**

### 8.3 配对效果（远胜猜文件名）

**`--pattern boss` 的实测输出：**

| 模型 | 骨骼 | 网格 | 通道 | 动画 | glTF |
| --- | --- | --- | --- | --- | --- |
| `boss_cowf_01` | 38 | 24 | **8** | `Boss_cowf_01.anm` | 56 KB |
| `boss_cowi_01` | 38 | 35 | **8** | `Boss_cowI_01.anm` | 73 KB |
| `boss_cowking_01` | 38 | 10 | **8** | `Boss_cowking_01.anm` | 35 KB |
| `boss_cowking_05` | **86** | 67 | 0 | `Boss_cowking_05.anm` | 134 KB |

**注意 `boss_cowi_01` → `Boss_cowI_01.anm` —— **大小写不一致**，
靠 `resolve_animation` 里的不区分大小写扫描才对上。**

### 8.4 还没做的：一个模型有多个动画

**`.chx` 里每个模型列出**多个**动画：**
```
boss_01 -> boss01_stand, boss01_move, boss01_attack01, boss01_attack02
```

**当前导出器**只导第一个**（`listed[0]`）。**

**所以 `boss_cowf_01` 只带了 8 通道的一个动作，实际它有几十个。**

**→ 下一步：一个模型导出多个 `AnimSequence`，或一次导出一个动作。**

### 8.5 通道数偏少的可能原因

**`boss_cowf_01` 有 38 骨骼，但只得到 8 通道。**

**两个可能：**
1. 这个 `.anm` 只驱动 8 根骨骼（其余骨骼在该动作里不动）
2. 骨骼名不匹配（`.anm` 里的名字和 `.mod` 里的对不上）

**判断方法：比对 `.anm` 的骨骼名与 `.mod` 的骨骼名，看交集大小。**

### 8.6 新增工具

| 工具 | 作用 |
| --- | --- |
| **`Tools/parse_chx.py`** | **解析所有 `.chx`，建模型→动画映射** |
| `Tools/wire_chx.py` | 把映射接入批量导出 |
| `Tools/batch_export.py` | 已用 `.chx` 优先、文件名兜底 |
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 八、`.chx` 配对：已接入" in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
