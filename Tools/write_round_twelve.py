"""Append the twelfth round to the handoff.

A file rather than an inline command: the text mixes backticks, quotes and Chinese punctuation that
PowerShell corrupts when a heredoc goes through python -c.

    python Tools/write_round_twelve.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 29. 第十二轮：`.mod` 容器格式确证（2026-11-26 21:30）

### 一、之前三种块头长度全错

试过 28 / 30 / 12 字节 —— **全错。正确的块头是 8 字节。**

```
+0  u32  block_type    (标记符)
+4  u32  block_size    (载荷字节数，不含这 8 字节)
+8  载荷开始
```

### 二、标记不是常量 —— 这是走不通的真正原因

| 标记 | 类型 |
| --- | --- |
| **0x00F00000** | **MATERIAL** |
| **0xF5000000** | **BONE** |
| **0xF4000000** | **MESH** |

**按标记分类后，块数与文件头声明精确匹配：**

```
jp03_dht00: 声明 4 骨骼 -> 走到 4 个 BONE 块   OK
w25260:     声明 38 骨骼 -> 走到 38 个 BONE 块 OK
```

### 三、两个新规则（两个文件都成立）

**① 对象数 = 材质数 + 骨骼数（不含网格）**

```
jp03:  1 + 4  = 5   OK
w25260: 1 + 38 = 39 OK
```

**② 骨骼块倒序存储，载荷第一个 int 是骨骼编号**

```
jp03: [1] word0=4, [2] word0=3, [3] word0=2, [4] word0=1
```

**倒序意味着网格里的骨骼索引可能也从后往前算 —— 这解释了以前对不上父骨骼。**

### 四、推翻了旧文档两条结论

| 旧说法 | 实际 |
| --- | --- |
| 「+36 开始是法线」 | **法线在载荷靠后位置，且有多组单位向量** |
| 「头后面 20 个零 + 名字」 | **名字在载荷里，不在头里** |

### 五、蒙皮权重仍未解 —— 但卡点变精确了

**三种扫描（u8 和=255 / u16 和=65535 / f32 和=1.0）都没匹配。**

**可能原因：**
1. 每顶点影响数不是 4
2. 权重不归一化（原引擎存原始值）
3. 索引与权重交错存

**下一步（明确，不是「继续试」）：**

```
1. 提取所有 .mod 的 MESH 载荷
2. 统计每组单位向量数组的长度
3. 找长度 == 顶点数 x 影响数 的那个数组
4. 用值域/单调性区分骨骼索引 vs 权重
```

### 六、新增工具

| 工具 | 作用 |
| --- | --- |
| `Tools/parse_mod.py` | 走完全部块（8 字节头）|
| `Tools/classify_mod_blocks.py` | 按标记分类 + 载荷首几字 |
| `Tools/find_unit_normals.py` | 单位向量数组定位 |
| `Tools/brute_mod_layout.py` | 暴力验证走法 |

### 七、掌握度

| 项 | 上一轮 | 本轮 |
| --- | --- | --- |
| **`.mod` 容器格式** | 走不通 | **确证** |
| **块类型标记** | 未知 | **三种已分类** |
| **网格载荷结构** | 错（旧结论） | **未知，但知道法线在后面** |
| **蒙皮权重** | 未解 | **未解（卡点更精确）** |
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 29." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 29; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
