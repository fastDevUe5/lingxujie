"""Record the verification of the IBM fix, including the second bug it exposed.

    python Tools/write_verify_ibm.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-DEBUG-CASE-IBM.md"

SECTION = """

---

## 十二、验证：修完之后到底对不对

**这一节是 2026-11-26 补做的。诊断只是第一步，**验证修复有效**才是闭环。**

### 12.1 方法：改一份副本，量完再删

**不动真资产，三步：**
1. 复制 `boss001.gltf` / `.bin`，只改逆绑定矩阵的字节
2. 导入到 `/Game/Moxiang/Test/`（临时路径）
3. 量骨骼跨度，然后**删掉测试资产和副本**

### 12.2 第一次：只修槽位顺序

**补丁：把平移从 3/7/11 挪到 12/13/14。**
```
moved the translation on 67 of 67 matrices
verification: matrices with translation in slots 12/13/14: 67
```

**导入后量骨骼（✅ 实测）：**
```
BROKEN (original):  67 bones, span X=0.0     Y=0.0     Z=0.0     cm
SLOTS FIXED:        67 bones, span X=31351.3 Y=28949.8 Z=39738.4 cm
```

**→ 骨骼**有偏移了**（0 → 39738 cm），**槽位修复确实有效**。**
**→ 但跨度是 **397 米** —— 明显过大。**

### 12.3 🔴 修 bug 1 才让 bug 2 露出来：单位没缩放

**对比量级（✅ 实测）：**

| 项 | 值 | 量级 |
| --- | --- | --- |
| glTF **节点**平移（`Bip01`）| `[-0.00145, -3.49e-10, -1.3319]` | **1.33 米** |
| IBM 平移（**未缩放**）| `(32.15, -129.25, 0.145)` | **129** |
| IBM 平移（**×0.01 后**）| `(0.3215, -1.2925, 0.0015)` | **1.29 米** |

**→ 只有缩放后才和节点平移**同量级**。**

**根因：`cp()` 把顶点从厘米转成米（`* 0.01`），
但 `invert()` 用的是 `parse_mod` 读出的**厘米**矩阵。两者单位不一致。**

**→ 39738 cm ÷ 100 = **397.4 cm ≈ 3.97 米** —— 正好是 Boss 的合理身高
（原 bounds 是 2.97 × 2.72 × 2.08 米）。**

### 12.4 两个 bug 的完整结论

| # | 缺陷 | 现象 | 修复 |
| --- | --- | --- | --- |
| **1** | `invert()` 已是列主序，`build()` 又转置 | 平移跑到 3/7/11，骨骼塌缩到原点 | `column_major = inverse` |
| **2** | IBM 用厘米，顶点用米 | 修了 #1 后骨骼跨度 397 米 | 平移部分 `× 0.01` |

**→ **必须两个都修**。只修 #1 会得到「能蒙皮但放大 100 倍」的模型。**

**⚠️ 这是**顺序调试**的典型：第一个修复把第二个 bug 从「被掩盖」变成「显形」。**

### 12.5 验证过程中我自己犯的错

| 错 | 后果 | 教训 |
| --- | --- | --- |
| 用 `-replace` 批量改脚本文本 | 文件路径被改成 `boss001_IBMFIX222.gltf`，导入失败 | **改路径用编辑工具，不用字符串替换** |
| `Get-Process \| Select-Object @{}` 缺 key | 命令报错，我**误读成「编辑器进程没了」** | **报错不是空结果；先读报错本身** |

**⚠️ 第二条是这一轮最该记的：我把**命令报错**当成了**命令结果**。**

### 12.6 清理

```
CLEAN: deleted /Game/Moxiang/Test -> True
CLEAN: removed boss001_ibmfix.gltf / .bin / ibmfix2.gltf / .bin
```

**✅ 已确认 `Content/Moxiang/Test` 和四个补丁文件都不在了，原资产一字未动。**
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "十二、验证" in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended the verification section")


if __name__ == "__main__":
    main()
