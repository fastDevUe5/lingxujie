"""Append the twenty-ninth round.

    python Tools/write_round_twentynine.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 46. 第二十九轮：**Boss 终于有实体 —— 网格块的 mat4 不该应用**（2026-11-26 30:30）

### 一、决定性对比

**同一批顶点，两种读法：**

| 读法 | 总包围盒 | 块中心散布 |
| --- | --- | --- |
| **应用每块 `mat4`** | 192.4 × **434.2** × 152.2 cm | 158.8 × **383.0** × 75.2 |
| **不应用 `mat4`** | 296.9 × 272.2 × 207.7 cm | 181.0 × 191.2 × 104.5 |

**应用 mat4 把模型沿 Y 拉了**两倍**。**

### 二、关键的不对称（gotcha #98）

| 对象 | `mat4` 该用吗 | 证据 |
| --- | --- | --- |
| **骨骼** | **该用** | 连续脊柱骨骼 Y = 94→112→127→144 递增，是真世界坐标 |
| **网格** | **不该用** | 应用后包围盒 Y 从 272 拉到 434 |

**同一个 `NODE_TM.mat4` 字段，在两类对象上语义不同。**

### 三、修后

```
总包围盒: 2.97 x 2.08 x 2.72 m
```

**画面里能看到实体躯干/护甲板，占屏幕三分之一。**

**对比：`MX_BOSS001_STATIC`（用旧方式导的静态网格）仍然散开。**

### 四、怎么找到的（方法对了）

**上一轮的错误：先改三处（IBM、节点变换、累乘方式）再猜。**

**这一轮先测量：**

1. **做「无蒙皮静态网格」版本** —— 发现包围盒和骨骼版**一模一样**
   → 证明散开不是蒙皮造成的，是顶点数据本身
2. **再对比「应用/不应用 mesh mat4」两种读法**
   → 数据直接指向答案

> **先测量，再改一处。**

### 五、MCP 相关的两个操作坑

**① 逐骨骼读姿态（`get_bone_pose`）会让 Python 线程**挂死**。**
- `get_reference_pose` 和 `get_bone_names` 正常（得到 67 个骨骼名）
- `get_bone_pose` / `get_ref_bone_pose` 一调就卡

**② 「恢复包」对话框挡住所有自动化。**
- `EditorGuard -Action dismiss` 的坐标兜底点不掉它
- 手动点对话框右上角 X（截图上 (1213,137) × 1.499 = (1818,205)）才关掉

### 六、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **回归验证：重新导出 `198_bobu` / `108_bird`，确认这次改动没弄坏它们** |
| 2 | 批量重导（改动影响所有模型）|
| 3 | 材质接入 |
| 4 | 动画播放验证 |
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 46." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 46; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
