"""Append the twenty-sixth round.

    python Tools/write_round_twentysix.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 43. 第二十六轮：**真角色进引擎 —— 36/38 骨骼 + 49 通道**（2026-11-26 29:00）

### 一、导出结果

```
mod: 38 bones, 24 meshes
anm: 56 tracks
matched bones: 36 of 38            <- 全身动画
nodes=39 joints=38 animation channels=49
```

**第 23 轮我以为「这个 Boss 只动画尾巴」。**
**`SCALE_KEY=36` 修好后，**36/38 骨骼匹配** —— 全身都在动。**

### 二、导入结果

```
BOSS: import produced 4 assets
  Skeleton         SK_BossCowf_Skeleton
  SkeletalMesh     SK_BossCowf
  PhysicsAsset     SK_BossCowf_PhysicsAsset
  AnimSequence     SK_BossCowf_Anim
  animation length 1.7000 s
```

### 三、🔴 修掉两个「作用域」错误

**修前包围盒：`(1419593, 1323043, 1973751) cm` = **14 公里**。
修后：`(279.8, 161.6, 87.5) cm` = **2.8 米**。**

#### 错误 1：每个网格块独立居中

**24 块各自减自己的重心 → 全叠到原点，相对位置全毁。**

**修法：整个模型算**一个**重心，所有块共用。**

#### 错误 2：背景/特效网格也被保留

**24 块里 12 块的顶点跨 **14–22 公里**（背景板、天空面）。**

**它们**也有骨骼权重**，所以按「有无绑定」筛选**无效**。**

**只能按尺寸筛：`if block_extent > 10000 cm: drop`。**

**实测 `dropped 12 block(s) larger than 100 m` → 剩 12 块，最大 2.51 米。**

### 四、对照表

| 项 | 修前 | 修后 |
| --- | --- | --- |
| 包围盒 | **14 公里** | **2.8 米** |
| 网格块 | 24 | **12** |
| 骨骼匹配 | — | **36 / 38** |
| 动画通道 | — | **49** |
| AnimSequence | — | **1.70 秒** |
| glTF | 81,812 B | 63,247 B |

### 五、两种「作用域」错误的共同点（gotcha #93）

| 错误 | 作用域错在哪 |
| --- | --- |
| 每块独立居中 | 居中应该是**整个模型**的操作 |
| 保留背景网格 | 「哪些块属于角色」是**模型级**判断 |

> **两次都是把「整体」的运算写在了「局部」上。**
>
> **而症状（14 公里包围盒）指向的是**数据**，不是**代码结构** ——
> 所以一开始会去怀疑顶点坐标、怀疑缩放、怀疑坐标系。**

### 六、仍待解决

**画面里角色仍不清晰（看到的是它的一块 2.5m 平面）。**

**这属于**摆放与朝向**，不是数据：包围盒已证明几何是对的（2.8 米 / 36 骨骼 / 49 通道）。**

### 七、新增工具

| 工具 | 作用 |
| --- | --- |
| **`Tools/import_and_place.py`** | 导入 + 摆放一体（参数在文件头）|

### 八、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **摆放与朝向校准**（角色已在引擎里，位置/朝向要调）|
| 2 | 批量重导（步长修了，旧输出要重生成）|
| 3 | 材质接入 |
| 4 | 动画蓝图状态机 |
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 43." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 43; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
