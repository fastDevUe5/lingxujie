# `.mod` 网格与蒙皮格式：**已完全解开**（2026-11-26）

> **状态：完全解决。四个样本文件全部逐字节验证通过（tail = 0）。**
>
> **关键：答案一直在研究区的 `client_src\tw\` 客户端 C 源码里。
> 我之前花了四轮重新推导一个已经写在源码里的格式。**

---

## 一、最重要的教训

**研究区有 `client_src\tw\` —— 5,035 个文件，包含 `4DyuchiGXGeometry\` 的完整 C++ 源码。**

**`FORMAT-REFERENCE.md` 里甚至有源码摘录。**

**我应该**第一步就去读源码**，而不是从二进制猜。**
**这条已写进 gotcha #81。**

---

## 二、完整读取顺序（源码 + 实测）

**`CMeshObject::ReadFile`（`geom_obj.cpp`）：**

```c
CBaseObject::ReadFile(pFP, dwVersion);              // 324 字节，见 2.1
FSRead(FILE_MESH_HEADER, 48);                       // 见 2.2
if (dwVertexNum)    FSRead(positions, 12 * V);      // VECTOR3
if (dwTexVertexNum) FSRead(uvs,        8 * T);      // TVERTEX = {u,v}
if (dwExtVertexNum) FSRead(extIndices, 4 * E);      // DWORD
for (i = 0; i < dwFaceGroupNum; i++)
    m_pFaceGroup[i].ReadFile(pFP);                  // 见 2.3
m_Physique.ReadFile(pFP);                           // ★ 蒙皮，见 2.4
if (shadeType == LIGHT_MAP)  LightTexture->ReadFile(pFP);
else if (transformType != ALIGN_VIEW)
    FSRead(normals, 12 * V);                        // ★ 法线在最后
```

### 2.1 `FILE_BASE_OBJECT_HEADER` = **324 字节**

```c
struct FILE_BASE_OBJECT_HEADER {
    DWORD    dwIndex;              // +0    4
    NODE_TM  TM;                   // +4  184
    DWORD    dwChildObjectNum;     // +188  4
    DWORD    dwParentObjectIndex;  // +192  4
    char     szObjName[128];       // +196 128
};

struct NODE_TM {                   // 184 字节
    float  fRotAng;                            // 4
    float  fPosX, fPosY, fPosZ;                // 12
    float  fRotAxisX, fRotAxisY, fRotAxisZ;    // 12
    float  fScaleX, fScaleY, fScaleZ;          // 12
    float  fScaleAxisX, fScaleAxisY, fScaleAxisZ; // 12
    float  fScaleAngle;                        // 4
    MATRIX4 mat4;                              // 64
    MATRIX4 mat4Inverse;                       // 64
};
```

**⚠️ `NODE_TM` 里有两个 `MATRIX4`（各 64 字节）—— 这是最容易漏的部分。**

### 2.2 `FILE_MESH_HEADER` = **48 字节**

```c
struct FILE_MESH_HEADER {          // #pragma pack(4)
    DWORD    dwMaxVertexNum;       // +0
    DWORD    dwVertexNum;          // +4   ★ 顶点数
    DWORD    dwOriginalVertexNum;  // +8
    DWORD    dwExtVertexNum;       // +12  ★ 扩展索引数
    DWORD    dwTexVertexNum;       // +16  ★ UV 数
    DWORD    dwMtlIndex;           // +20
    DWORD    dwFaceGroupNum;       // +24  ★ 面组数
    CMeshFlag meshFlag;            // +28
    DWORD    dwGridIndex;          // +32
    VECTOR3  v3Dir;                // +36  (12 字节)
};
```

### 2.3 `FILE_FACE_GROUP_HEADER` = **28 字节**

```c
struct FILE_FACE_GROUP_HEADER {    // 7 个 DWORD
    DWORD dwMtlIndex, dwIndex, dwFacesNum, dwMaxFacesNum,
          dwVertexIndexNum, dwLightUVNum1, dwLightUVNum2;
};

// 读取：
FSRead(header, 28);
if (dwFacesNum)      FSRead(m_pFace,       2 * dwFacesNum * 3);   // WORD 三元组
if (dwLightUVNum1)   FSRead(m_ptLightUV1,  8 * dwLightUVNum1);
if (dwLightUVNum2)   FSRead(m_ptLightUV2,  8 * dwLightUVNum2);
```

**⚠️ 不是 `[count][indices]` —— 是 7 个字段的头。**

### 2.4 🔴 `CPhysique` —— 蒙皮（**这就是之前解不出的部分**）

```c
struct FILE_PHYSIQUE_HEADER {      // 12 字节
    DWORD dwVertexNum;             // +0
    DWORD dwTotalBonesNum;         // +4
    DWORD dwAllocBonesNum;         // +8
};

CPhysique::ReadFile:
    if (header.dwVertexNum) {
        FSRead(m_pPhyVertexList, 5 * dwVertexNum);         // PHYSIQUE_VERTEX
        FSRead(m_pBoneList,      44 * dwTotalBonesNum);    // BONE
    }
```

**`PHYSIQUE_VERTEX`（**5 字节**，`#pragma pack(1)`）：**
```c
struct PHYSIQUE_VERTEX {
    BYTE   bBonesNum;     // +0  ★ 这个顶点有几个骨骼影响（可变！）
    BONE*  pBoneList;     // +1  磁盘上存的是 u32 起始索引
};
```

**`BONE`（**44 字节**，`#pragma pack(1)`）：**
```c
struct BONE {
    void*    pBone;            // +0   4  磁盘上是骨骼索引
    float    fWeight;          // +4   4  ★ 权重！
    VECTOR3  v3Offset;         // +8  12  位置偏移
    VECTOR3  v3NormalOffset;   // +20 12  法线偏移
    VECTOR3  v3TangentOffset;  // +32 12  切线偏移
};
```

**这就是我扫不到的蒙皮权重 —— `fWeight` 在每条 44 字节 BONE 记录的第 4 字节。**

**为什么之前扫不到：**
> **我以为「每顶点固定 4 个影响，权重之和 = 255/1.0」。**
> **实际：每顶点影响数**可变**（1/2/3 个），权重是 f32 存在交错的结构里。**

---

## 三、实测验证（四个文件，全部通过）

| 文件 | 顶点 | 面组 | 骨骼记录 | 影响数分布 | 法线 | tail |
| --- | --- | --- | --- | --- | --- | --- |
| `216.mod` | 517 | 2 | 669 | {1:180, 2:229, 3:108} | **517/517** | **0** |
| `19240.mod` | 348 | 1 | 0 | — | **348/348** | **0** |
| `choco.mod` | 190 | 6 | 174 | {1:118, 2:72} | **190/190** | **0** |
| `108_bird.mod` | 146 | 2 | 134 | {1:132, 2:14} | **146/146** | **0** |

**验证标准（三条全过才算对）：**
1. **法线 100% 单位长度**（最强验证 —— 任何偏移错一位它就不成立）
2. **权重全在 0..1**
3. **骨骼索引全在 `[0, totalBonesNum)`**
4. **tail = 0**（字节精确消耗完）

**四个文件四条标准全过。**

### 3.1 真实蒙皮数据样本（`216.mod`）
```
influences {1:180, 2:229, 3:108}     ← 517 个顶点，影响数 1~3 不等
bone sample: (2, 0.8000), (1, 0.1000), (3, 0.1000)   ← 权重和 = 1.0 ✓
```

### 3.2 真实蒙皮数据样本（`choco.mod`）
```
influences {1:118, 2:72}
bone sample: (9, 0.5000), (10, 0.5000)    ← 两骨骼各半
```

**`108_bird.mod` 更有意思：`{1:132, 2:14}` —— 大部分顶点只受 1 个骨骼影响。**
**所以「刚性绑定」在这个格式里是常态，不是例外。**

---

## 四、这对动画导入意味着什么

### 4.1 之前阻塞的三个未知，两个已解决

| 未知 | 状态 |
| --- | --- |
| **蒙皮权重格式** | ✅ **完全解开** |
| **骨骼层级从哪来** | ✅ **`dwParentObjectIndex` 在 324 字节基类头里（+192）** |
| `.anm` 帧率 | 🟡 仍未知（但不阻塞，见 `UE5-ANIMATION-ENGINE.md`）|

### 4.2 现在可以做 glTF 导出了

**要写的数据全部齐了：**

```
每个 .mod:
  1. 每个对象的 NODE_TM（位置/旋转/缩放）→ glTF node 的 transform
  2. dwParentObjectIndex → glTF node 的父子关系（骨架层级！）
  3. positions (f32×3×V) → glTF mesh 的 POSITION
  4. normals (f32×3×V，末尾) → glTF mesh 的 NORMAL
  5. uvs (f32×2×T) → glTF mesh 的 TEXCOORD_0
  6. faceGroups 的 faces (u16×3×F) → glTF mesh 的 indices
  7. PHYSIQUE_VERTEX + BONE → glTF 的 JOINTS_0 + WEIGHTS_0
```

**第 2 条是关键：`dwParentObjectIndex` 直接给出骨骼父子关系，
所以骨架层级**不需要猜**。**

### 4.3 权重必须重排

**墨香的 `PHYSIQUE_VERTEX.bBonesNum` 是可变的（1~3 个），
但 glTF 的 `JOINTS_0`/`WEIGHTS_0` 是**固定 4 个**。**

**所以要做补齐：**
```
每顶点读 bBonesNum 个 (bone_index, weight) 对
→ 补 0 到 4 个
→ 写入 JOINTS_0 / WEIGHTS_0
```

**这也是为什么之前扫「固定 4 个」失败 —— 源格式本来就不是 4 个。**

---

## 五、剩余的一步：写导出器

**格式已经完全清楚，剩下的是工程量：**

| 步骤 | 难度 |
| --- | --- |
| 解析所有块（容器 + 基类 + 网格 + 面组 + 蒙皮）| ✅ **已有工具** |
| 建节点树（用 `dwParentObjectIndex`）| 低 |
| 写 positions / normals / uvs / indices | 低 |
| **写 JOINTS_0 / WEIGHTS_0（补齐到 4）** | 中 |
| 写 glTF accessor / bufferView | 中 |
| 用 `SkeletalMeshTools.import_file` 导入 | 低（工具已验证）|

**下一步是纯工程，不是逆向。**

---

## 六、重查命令

```powershell
python Tools\verify_mod_layout.py     # 逐字节验证布局（四个样本）
python Tools\parse_mod.py             # 容器块结构
python Tools\classify_mod_blocks.py   # 按标记分类
```

**源码出处：**
```
研究区 client_src\tw\4DyuchiGXGeometry\geom_obj.cpp     -- CMeshObject::ReadFile
研究区 client_src\tw\4DyuchiGXGeometry\object.cpp       -- CBaseObject::ReadFile
研究区 client_src\tw\4DyuchiGXGeometry\face_group.cpp   -- CFaceGroup::ReadFile
研究区 client_src\tw\4DyuchiGXGeometry\Physique.cpp     -- CPhysique::ReadFile
研究区 client_src\tw\4DyuchiGRX_common\typedef.h        -- BONE / PHYSIQUE_VERTEX / NODE_TM
研究区 Docs\reverse-engineering\FORMAT-REFERENCE.md     -- 汇总参考
```
