"""Append the eleventh debugging round: case 003, the provable one-line bug.

    python Tools/write_debug_round11.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 68. 调试系列第 11 轮：**实战 003 — 逆绑定矩阵转置两次，一行 bug**（2026-11-26 53:00）

### 一、起点：一句记录，而且**是错的**

**既有记录：「`MX_BOSS001_STATIC` 仍然散开」。**

**✅ 实测 bounds 立即推翻：**
```
MX_BOSSCOWF        extent (924.5, 512.7, 550.7) cm   ← 9.2×5.1×5.5 米，这才是散开的
MX_BOSS001_STATIC  extent ( 96.2, 217.1,  76.1) cm   ← 正常
MX_BOSS001         extent (149.9, 194.2, 132.7) cm   ← 正常
```

**→ **第三次「既有记录不可信」。**

### 二、六步定位（其中一步是陷阱）

| 步 | 做法 | 结果 |
| --- | --- | --- |
| 1 | 查 bounds | **推翻记录** |
| 2 | 截图 | 看见散落部件 |
| 3 | 量长轴 | **假线索**：三个模型 Z 都最小，像躺平了 |
| 4 | **查骨骼位置** | **🔴 67 根骨骼全在同一位置，跨度 0** |
| 5 | 查 glTF 关节节点 | 节点平移正确，**IBM 平移全零** |
| 6 | **查 3/7/11 槽** | **67/67 平移在这** → 证明转置两次 |

### 三、🔴 根因

**`export_mod_anim_gltf.py` 第 683-697 行 `invert()` 返回的列表**已经是列主序**（平移在 12/13/14）。**

**第 733-738 行 `build()` 又转置了一次：**
```python
inverse = invert(world)
# Transpose into glTF's column-major order.      ← 注释说的事 invert() 已经做完了
column_major = [inverse[c * 4 + r] for r in range(4) for c in range(4)]
```

**→ 平移从 12/13/14 被推到 3/7/11，glTF 读 12/13/14 得到全零。**
**→ 每根骨骼的绑定姿态被声称在原点 → 蒙皮公式 `globalTransform × IBM` 抵消不掉 → 网格散开。**

**修复：`column_major = inverse`。一行。**

### 四、🔴 为什么之前没发现 —— 最重要的方法论教训

**之前记录的验收方式是「往返误差 2.22e-16」。**

**→ 那个测试是「自己算 IBM，自己再逆回去，比对」——
证明了**算术对**，但**完全没碰到写进文件时的字节顺序**。**

> **验证必须用**独立的读取者**，不能用自己写的那一半去验另一半。**
>
> **正确做法：写完后用 glTF 规范位置（12/13/14）读回来，检查是否等于 `-R^T·t`。**
> **这正是第 6 步做的事，一次就抓到。**

### 五、影响面

**所有用这个导出器导出的**带骨骼模型**都受影响。**
**回归基线 8 个模型里带骨骼的 5 个：`108_bird` / `198_bobu` / `boss001` / `boss_cowf_01` / `107_crow`。**

**⚠️ 这些模型的**包围盒都对**（顶点没被改），但**绑定姿态和蒙皮全错**。**

**→ 这解释了「包围盒每次正常，但看起来就是不对」的长期困惑。**
**→ 包围盒量的是**顶点**，而问题是**矩阵**。**

### 六、三个方法论教训

| 教训 | 依据 |
| --- | --- |
| **验证要用独立读取者** | 自证误差 2e-16 掩盖了字节顺序错误 |
| **包围盒正常 ≠ 模型正确** | 它不量矩阵和绑定姿态 |
| **退化数据比错误数据更危险** | 67 根骨骼全同一点，「看起来没坏」 |

### 七、新增

| 产出 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-CASE-IBM.md`** | 六步完整定位 + 根因 + 方法论教训 |
| `Tools/diag_scatter_step2.py` | 量网格长轴与 actor 变换 |
| `Tools/diag_scatter_step3.py` | 量源空间三轴跨度 |
| `Tools/diag_scatter_step4.py` | 读骨骼位置（找到真机制）|
| `Tools/diag_scatter_step5.py` | 查 glTF 关节节点与 IBM |
| `Tools/diag_scatter_step6.py` | **验 3/7/11 槽（证明转置两次）** |

### 八、三个实战案例汇总

| 案例 | 症状 | 根因 | 定位关键 |
| --- | --- | --- | --- |
| 001 动画 | 看不见动 | 脚本没赋 animation_mode/anim_to_play | 读结构体 |
| 002 法线 | 引擎警告 | NOT_SOLID 几何本无语义法线 | 查反编译源码 |
| **003 IBM** | **模型散开** | **逆绑定矩阵转置两次** | **用规范位置读回来** |

**→ 三个都推翻了一个既有判断。**
**→ 三个的根因都在**导出器**，不在 UE。**

### 九、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | 应用三个修复（动画 / NOT_SOLID 法线 / IBM 转置），然后回归验证 |
| 2 | 或继续找案例 |

**⚠️ 按用户要求「先不要急着开发」，代码仍未改。**
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 68." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 68; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
