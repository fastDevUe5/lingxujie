"""Append the twelfth debugging round.

    python Tools/write_debug_round12.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 69. 调试系列第 12 轮：**验证 IBM 修复 —— 修好一个，暴露第二个**（2026-11-26 54:00）

### 一、为什么要补这一步

**上一轮只做到「定位」。**定位不等于修好。**
**这一轮验证修复，并发现了**第二个**同源的 bug。**

### 二、方法：改副本，量完删

**不动真资产：复制 glTF → 只改矩阵字节 → 导入 `/Game/Moxiang/Test/` → 量 → 删。**

### 三、第一次只修槽位顺序

```
moved the translation on 67 of 67 matrices
verification: matrices with translation in slots 12/13/14: 67
```

**导入后量骨骼（✅ 实测）：**
```
BROKEN (original):  67 bones, span X=0.0     Y=0.0     Z=0.0     cm
SLOTS FIXED:        67 bones, span X=31351.3 Y=28949.8 Z=39738.4 cm
```

**→ 骨骼有偏移了，槽位修复**有效**。**
**→ 但跨度 **397 米**，明显过大。**

### 四、🔴 修 bug 1 才让 bug 2 露出来：**单位没缩放**

| 项 | 值 | 量级 |
| --- | --- | --- |
| glTF **节点**平移 | `[-0.00145, -3.49e-10, -1.3319]` | **1.33 米** |
| IBM 平移（未缩放）| `(32.15, -129.25, 0.145)` | **129** |
| IBM 平移（×0.01）| `(0.3215, -1.2925, 0.0015)` | **1.29 米** |

**→ `cp()` 把顶点从厘米转成米，但 `invert()` 用的是**厘米**矩阵。单位不一致。**
**→ 39738 cm ÷ 100 = **3.97 米** —— 正好是 Boss 的合理身高。**

### 五、两个 bug 必须都修

| # | 缺陷 | 修复 |
| --- | --- | --- |
| **1** | `invert()` 已是列主序，`build()` 又转置 | `column_major = inverse` |
| **2** | IBM 用厘米，顶点用米 | 平移部分 `× 0.01` |

**⚠️ 只修 #1 会得到「能蒙皮但放大 100 倍」的模型。**

**→ 这是**顺序调试**的典型：第一个修复把第二个 bug 从「被掩盖」变成「显形」。**

### 六、🔴 验证过程中我自己犯的两个错

| 错 | 后果 | 教训 |
| --- | --- | --- |
| 用 `-replace` 批量改脚本文本 | 路径被改成 `boss001_IBMFIX222.gltf`，导入失败 | **改路径用编辑工具，不用字符串替换** |
| `Get-Process` 里 `@{}` 缺 key 导致命令报错 | 我**误读成「编辑器进程没了」**，虚惊一场 | **报错不是空结果；先读报错本身** |

**→ 第二条是本轮最该记的：我把**命令报错**当成了**命令结果**。**

**（实际编辑器一直在跑：PID 4544 / 4582 MB，无新崩溃目录。）**

### 七、清理

```
CLEAN: deleted /Game/Moxiang/Test -> True
CLEAN: removed boss001_ibmfix.gltf / .bin / ibmfix2.gltf / .bin
```

**✅ 已确认测试资产和四个补丁文件都不在了，原资产一字未动。**

### 八、新增

| 产出 | 内容 |
| --- | --- |
| `Docs/UE5-DEBUG-CASE-IBM.md` **第 12 节** | 完整验证记录（含两个 bug 与自造错误）|
| `Tools/patch_ibm.py` | 只修槽位 |
| `Tools/patch_ibm2.py` | 槽位 + 缩放（带 `--noscalc` 开关）|
| `Tools/measure_imported_skeleton.py` | **量已导入资产（不需要导入，最简单可靠）** |
| `Tools/cleanup_ibm_test.py` | 清理测试资产与副本 |

### 九、三个实战案例的当前状态

| 案例 | 定位 | 修复验证 |
| --- | --- | --- |
| 001 动画 | ✅ | ✅ 骨骼四个时间点四位姿 |
| 002 法线 | ✅ | ❌ 未验证 |
| **003 IBM** | ✅ | ✅ **槽位+缩放两处都证实** |

### 十、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | 把这三处的修复**应用到导出器**，跑回归 |
| 2 | 或继续找案例 |

**⚠️ 代码仍未改 —— 等指示。**
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 69." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 69; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
