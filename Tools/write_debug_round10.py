"""Append the tenth debugging round: the second real case.

    python Tools/write_debug_round10.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 67. 调试系列第 10 轮：**实战 002 — 退化法线，根因在 `.mod` 的标志位**（2026-11-26 52:00）

### 一、起点是一条我一直没查的警告

```
LogStaticMeshOperations: Display: Mesh 0 has NaNs in it's vertex instance tangent space!
LogStaticMesh: Warning: SM_Boss001 拥有一些近零的法线，其可能诱发问题。（容差为 1E-4）
```

### 二、四步定位

| 步 | 做法 | 结果 |
| --- | --- | --- |
| 1 | 想在 `StaticMesh` 上读法线 | **Python 没接口**（只有 `get_num_lods` 等）|
| 2 | 改查 glTF 源文件 | **88.55% 退化**（550 零 / 569 非单位 / 2 NaN）|
| 3 | 想怪导出器 | **排除了** —— 缺失时写的是 (0,0,1)，不是零 |
| 4 | 查 `.mod` 原始数据 | **按 flag 完美分组** |
| 5 | 查反编译源码 | **`0x10` = NOT_SOLID** |

### 三、🔴 规律完美对应

| `mesh_flag & 0xF0` | 块 | 法线质量 |
| --- | --- | --- |
| **`0x00`（SOLID）** | mesh 0-5 | **全干净** |
| **`0x10`（NOT_SOLID）** | mesh 6-16 | **全退化** |

```
TOTAL: 1266 normals
  恰好为零: 103    非单位长度: 579    非有限: 24    退化: 706 (55.77%)
```

### 四、反编译源码给出语义

**`client_src/tw/4DyuchiGRX_common/mesh_flag.h`：**
```cpp
enum TRANSFORM_TYPE {
    TRANSFORM_TYPE_SOLID      = 0x0000000,
    TRANSFORM_TYPE_NOT_SOLID  = 0x00000010,   // ← 元凶
    TRANSFORM_TYPE_ALIGN_VIEW = 0x00000030,
    TRANSFORM_TYPE_ILLUSION   = 0x00000050
};
#define TRANSFORM_TYPE_MASK  0x000000f0
```

**`0x10` = **非实体几何** —— 特效/贴片/加色层，原始渲染器**根本不用它们的法线**。**

### 五、根因：导出器的 `has_normals` 漏了两种类型

```python
has_normals = (shade_type != SHADE_TYPE_LIGHT_MAP          # 排除了 0x03
               and transform_type != TRANSFORM_TYPE_ALIGN_VIEW   # 排除了 0x30
               and ...)
```
**⚠️ 漏了 `NOT_SOLID (0x10)` 和 `ILLUSION (0x50)`。**

### 六、影响面

**`boss001` 里 17 个 mesh 块，**11 个是 NOT_SOLID**，
占 **1046 / 1266 = 83% 的顶点**。**

**→ 这个 Boss 的**大部分表面**用退化法线 → 黑块、错误高光、法线贴图方向乱。**

### 七、🔴 对 `MOD-FORMAT-SOLVED.md` 的重要补充

| 之前 | 现在 |
| --- | --- |
| 「法线是条件性的，只有 LIGHT_MAP 和 ALIGN_VIEW 没有」 | **「有没有法线」和「法线能不能用」是两件事** |

**→ 客户端**确实读了** NOT_SOLID 的法线（按反编译的读取条件），
但它**读了不用** —— 因为是加色/半透明绘制。**

**→ 我们不知道这一点，就当正常数据用了。**

### 八、修复方案（**未应用**）

**保守方案：**
```python
if not has_normals or transform_type in (TRANSFORM_TYPE_NOT_SOLID, TRANSFORM_TYPE_ILLUSION):
    normals = [(0.0, 0.0, 1.0)] * vertex_num    # 复用现有的 filler 逻辑
```
**代价：NOT_SOLID 几何变成平面着色。但它们本来是特效层，比黑块好。**

**彻底方案：把 NOT_SOLID / ILLUSION 导出成独立 primitive，
在 UE 里赋双面 + 无光照/加色材质 —— 这才符合原始语义。**

**⚠️ 按用户要求「先不要急着开发」，**代码一字未改**。**

### 九、新增

| 产出 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-CASE-NORMALS.md`** | 完整定位记录 |
| `Tools/diag_normals_step1.py` | 想在 UE 里量（失败，记录 API 限制）|
| `Tools/diag_normals_gltf.py` | 纯 Python 解 glTF accessor 量法线 |
| `Tools/diag_normals_mod.py` | 复用导出器 parser 分类 `.mod` 法线 |

### 十、两个实战的共同点

| | 实战 001（动画）| 实战 002（法线）|
| --- | --- | --- |
| 表面症状 | 看不见动 | 引擎警告 |
| 真根因 | 脚本没赋值 | 源数据无语义 |
| 定位关键 | 读结构体 | 查反编译源码 |
| 都推翻了一个直觉假设 | 「引擎不求值」 | 「导出器写坏了」 |

**→ **两次都是「先排除最像的原因」，然后才找到真的。****

### 十一、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | 第三个实战（候选：`MX_BOSS001_STATIC` 仍然散开 / `thunder3` 转换失败）|
| 2 | 或者：应用已定位的两个修复（等指示）|
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 67." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 67; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
