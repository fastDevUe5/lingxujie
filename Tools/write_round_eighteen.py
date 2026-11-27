"""Append the eighteenth round.

    python Tools/write_round_eighteen.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 35. 第十八轮：人形角色 — 两个只有复杂模型才暴露的 bug（2026-11-26 24:30）

### 一、结果

**角色**渲染出来了**，但还趴着。两个真 bug 已修。**

### 二、bug 1：只导出第一个网格块

**`198_bobu.mod` 有 **3 个 MESH 块**：**

| 块 | 名字 | 顶点 |
| --- | --- | --- |
| `[2]` | `N012-1` | 164 |
| `[3]` | **`N012`** | **632** ← 主体 |
| `[4]` | `N012-2` | 37 |

**我的导出器取 `meshes[0]` —— 导的是 164 顶点的小零件。**

**症状：包围盒 34.3 × 44.0 × 39.5 cm。**

**修法：每个网格块生成一个 glTF primitive，共用同一个 skin。**

**修后：包围盒 99.6 × 77.8 × 99.4 cm。**

### 三、🔴 bug 2：顶点坐标是世界位置，不是局部坐标

**修完多网格后，角色**完全不渲染** —— actor 位置对、`visible=True`、有材质、骨骼正常。**

**查 glTF 的 `POSITION` min/max：**
```
primitive 0: min=[22.44, 23.98, -0.89]  max=[23.12, 24.77, -0.01]
primitive 1: min=[23.17, 24.58, -1.55]  max=[24.43, 25.67, 0.00]
```

**所有顶点都在 **(23, 25, -1) 米** —— 即 (2300, 2500, -100) 厘米。**

**也就是说 `.mod` 的顶点是**模型在原地图里的世界位置**。
actor 放到 (9100, -6200)，几何实际在 (11400, -3700) —— 画面外。**

**修法：导出时减去顶点中心。**
```python
centre = [sum(p[i] for p in positions) / len(positions) for i in range(3)]
positions = [(p[0]-centre[0], p[1]-centre[1], p[2]-centre[2]) for p in positions]
```

**修后 min/max 全部居中，角色立刻渲染。**

### 四、为什么鸟没暴露这两个 bug

| bug | 鸟为什么没事 |
| --- | --- |
| 只导第一个网格 | 鸟只有 1 个网格块 |
| 顶点不在原点 | 鸟的顶点恰好接近原点 |

> **单一小样本通过，不代表管道正确。**

**这和前面几輪的错误同类：拿一个样本证明规则。**

### 五、还没解决的：朝向（趴着）

**包围盒 99.4 × 77.8 × **54.8** —— Z（高度）最小，人形应该 Z 最大。**

**最可能的原因：**
> **对象的 `NODE_TM` 变换（`fRotAng` / `fRotAxis` / `fPos` / `fScale`）
> 我只写进了节点，没有应用到顶点上。**
> **如果原模型靠对象旋转来"立起来"，顶点本身就是躺着的。**

**下一步：把 NODE_TM 构造成矩阵，乘到顶点上。**

### 六、动画长度核对

```
SK_Bobu_Anim: sequence_length = 10.666666984558105 秒
```

**320 键 × 每帧 1 键 = 320 帧 ÷ 30 fps = **10.67 秒** ✓**

**（鸟是每 2 帧 1 键，136 键 = 270 帧 = 9 秒。两个文件关键帧密度不同。）**

### 七、新增文档与坑

| 产出 | 说明 |
| --- | --- |
| **`Docs/CHARACTER-IMPORT-STATUS.md`** | 两个 bug + 未解决项 + 下一步 |
| **gotcha #84** | 一个模型可能有多个网格块 |
| **gotcha #85** | `.mod` 顶点是世界位置不是局部坐标 |
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 35." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 35; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
