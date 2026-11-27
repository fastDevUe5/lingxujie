"""Append the fourteenth round: the format was solved.

    python Tools/write_round_fourteen.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 31. 第十四轮：`.mod` 网格与蒙皮格式**完全解开**（2026-11-26 22:30）

### 一、结果：四文件逐字节验证通过

| 文件 | 顶点 | 面组 | 骨骼记录 | 影响数 | 法线 | tail |
| --- | --- | --- | --- | --- | --- | --- |
| `216.mod` | 517 | 2 | 669 | {1:180, 2:229, 3:108} | **517/517** | **0** |
| `19240.mod` | 348 | 1 | 0 | — | **348/348** | **0** |
| `choco.mod` | 190 | 6 | 174 | {1:118, 2:72} | **190/190** | **0** |
| `108_bird.mod` | 146 | 2 | 134 | {1:132, 2:14} | **146/146** | **0** |

**四条验证标准全过：法线 100% 单位长度、权重 0..1、骨骼索引在范围、字节精确消耗完。**

### 二、完整读取顺序（源码 + 实测）

```
FILE_BASE_OBJECT_HEADER   324 字节  (dwIndex 4 + NODE_TM 184 + children 4 + parent 4 + name 128)
FILE_MESH_HEADER           48 字节
positions                  12 x V
uvs                         8 x T
extIndices                  4 x E
faceGroups                 每組 28 字节头 + 2*faces*3 + 8*lightUV1 + 8*lightUV2
FILE_PHYSIQUE_HEADER       12 字节
PHYSIQUE_VERTEX x n         5 字节each  (bBonesNum u8 + 起始索引 u32)
BONE x boneNum             44 字节each (索引 u32 + 权重 f32 + 3xVECTOR3)
normals                    12 x V     <- 在最后
```

### 三、🔴 为什么之前四轮全错

**三个错误叠在一起：**

| 错误 | 实际 |
| --- | --- |
| 网格头是 36 字节 | **48 字节** |
| 载荷直接从网格头开始 | **前面有 324 字节基类头** |
| 面组是 `[count][indices]` | **28 字节 7 字段头** |

**而蒙皮扫不到的根本原因：**
> **`PHYSIQUE_VERTEX.bBonesNum` 每顶点**可变**（1~3）。
> `108_bird.mod` 有 132 个顶点只受 1 个骨骼影响 —— 刚性绑定是常态。**

**我一直假设「固定 4 个影响、权重之和 = 255/1.0」，所以永远扫不到。**

### 四、🔴 更重要的教训：答案在源码里

**研究区 `client_src\\tw\\4DyuchiGXGeometry\\` 有**完整客户端 C++ 源码**：**
```
geom_obj.cpp     -- CMeshObject::ReadFile
object.cpp       -- CBaseObject::ReadFile
face_group.cpp   -- CFaceGroup::ReadFile
Physique.cpp     -- CPhysique::ReadFile   <- 蒙皮，15 行
typedef.h        -- BONE / PHYSIQUE_VERTEX / NODE_TM
```

**`FORMAT-REFERENCE.md` 里甚至摘录了这些源码。**

**我把「研究区是数据仓库」当成「研究区只有数据」。实际它有一手源码。**

**→ gotcha #81：逆向任何格式前，先查研究区有没有读取代码。**

### 五、动画路径现在通了

**之前阻塞的三个未知：**

| 未知 | 状态 |
| --- | --- |
| 蒙皮权重格式 | ✅ **解开** |
| 骨骼层级来源 | ✅ **`dwParentObjectIndex` 在基类头 +192** |
| `.anm` 帧率 | 🟡 仍未知，但不阻塞 |

**剩下的是纯工程：写 glTF 导出器。**
**每顶点 `bBonesNum` 个影响要**补齐到 4** 才能写 glTF 的 `JOINTS_0`/`WEIGHTS_0`。**

### 六、新增文档与工具

| 产出 | 说明 |
| --- | --- |
| **`Docs/MOD-FORMAT-SOLVED.md`** | 完整格式参考（含源码出处）|
| `Tools/verify_mod_layout.py` | 逐字节验证（四样本，tail=0）|
| `Docs/MOD-SKIN-STATUS.md` | 保留为历史（含四轮失败的记录）|
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 31." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 31; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
