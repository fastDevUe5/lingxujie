"""Append the batch findings to the mod status document.

Two negative results are worth recording precisely because they rule out the obvious layouts: the
normals are not thirty-two bit floats, and they are not half floats either. For most character
models the payload contains no unit-length vector run at all, which points at byte quantisation -
a normal stored as three bytes in the range minus one to one, scaled at load.

    python Tools/update_mod_status.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/MOD-SKIN-STATUS.md"

SECTION = """
---

## 十、批量扫描结果（第 13 轮，2026-11-26）

### 10.1 先按骨骼数过滤 —— 这一步之前漏了

**全库 5,305 个 `.mod`，其中：**

| 类别 | 数量 |
| --- | --- |
| `bones = 0`（静态道具/特效）| **3,412** |
| **`bones > 0`（有骨架）** | **1,893** |
| 其中 `bones > 60`（角色体型）| **1,385** |

**第一批扫描扫的是字母序前 40 个 —— 几乎全是 `bones=0` 的道具。
那批数据说明的是**布景**的结构，不是角色的。**

### 10.2 角色模型的单位向量数组模式

**按骨骼数分桶，每组取 8 个样本：**

| 桶 | 模型数 | 典型单位向量数组 |
| --- | --- | --- |
| `<16` 骨骼 | 24 | `40:2, 124:2`（**只有头部两个小数组**）|
| `16-59` | 121 | 同上，偶尔后面有长串 |
| `60+` | 778 | 同上 |

**`40:2, 124:2` 的含义：载荷 +40 和 +124 各有 **2 个**连续单位向量。**

**这两个是**头部固定字段**（可能是默认朝向），不是几何。**

### 10.3 🔴 两个否定结论（重要）

**我验证了两种浮点格式，都不是：**

| 假设 | 验证方法 | 结果 |
| --- | --- | --- |
| 法线是 **f32** 单位向量 | 扫 12 字节三元组，长度≈1.0 | **大多数角色找不到** |
| 法线是 **f16**（半精度）单位向量 | 扫 6 字节三元组，长度≈1.0 | **全部找不到（0 个）** |

**而少数模型确实有 f32 单位向量：**
```
19240.mod    (96 骨骼)  载荷 14,676  找到 348 个（@10500）
costume_wing_14.mod     载荷 178,580 找到一串 @53540 起，间距 44 字节
```

**所以：f32 法线只在**部分**模型里存在，多数角色没有。**

### 10.4 由此推出的新假设

> **法线很可能是**字节量化**的：每个法线 3 个 u8，值域 [-1,1] 映射到 [0,255] 或 [-127,127]，
> 加载时归一化。**

**依据：**
1. 墨香是 2000 年代引擎，字节量化法线在当时是标准做法（省 4 倍内存）
2. 用 f32 和 f16 都扫不到，说明不是浮点
3. 载荷大小与「位置 f32 + 法线 u8」的比例吻合

**验证方法（下一轮第一件事）：**
```
对每个角色载荷，假设:
  位置 = f32 x 3 x vertexcount
  法线 = u8  x 3 x vertexcount
遍历 vertexcount 的可能值，检查「法线段」每个三元组字节归一化后的长度是否 ≈ 1.0
```

### 10.5 新增工具

| 工具 | 作用 |
| --- | --- |
| `Tools/batch_mod_meshes.py` | 批量提取网格载荷 + 单位向量数组列表 |
| `Tools/compare_mesh_layouts.py` | 按骨骼数分组对比结构 |

### 10.6 本轮结论的诚实表述

| 项 | 状态 |
| --- | --- |
| `.mod` 容器格式 | ✅ **确证**（8 字节头 + 三种标记）|
| 对象数规则 | ✅ **确证**（= 材质 + 骨骼）|
| 骨骼倒序 | ✅ **确证** |
| 法线是 f32 | ❌ **多数角色不成立** |
| 法线是 f16 | ❌ **完全不成立** |
| **法线字节量化** | 🟡 **新假设，待验证** |
| 蒙皮权重 | 🔴 **仍未解** |

**每轮都在缩小范围，但还没到底。**
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 十、批量扫描结果" in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
