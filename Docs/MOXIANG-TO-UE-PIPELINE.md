# 墨香 → UE5 完整资产管道：**全链路验证通过**（2026-11-26）

> **状态：`.mod`（网格+蒙皮）+ `.anm`（动画）→ glTF → UE 四个资产，全部验证通过。**
>
> **这是第 11–17 轮七轮的成果。**

---

## 一、最终结果（实测）

```
导入 bird_anim.gltf 产生 4 个资产：

  Skeleton        SK_BirdAnim_Skeleton
  SkeletalMesh    SK_BirdAnim
  PhysicsAsset    SK_BirdAnim_PhysicsAsset
  AnimSequence    SK_BirdAnim_Anim        ← 动画序列
```

**日志原文：**
```
ANIM: import produced 4 assets
ANIM:   AnimSequence  .../SK_BirdAnim_Anim.SK_BirdAnim_Anim
```

### 1.1 动画长度验证

**导入后 `sequence_length = 9.0` 秒。**

**我从源码推导：**
```
136 个关键帧，间隔 320 ticks
160 ticks/帧  →  每个关键帧间隔 2 帧
→ 最后一帧 = 135 × 2 = 270
→ 270 帧 / 30 fps = 9.0 秒  ✓
```

**导入器算得**完全正确**。（我最初以为应该是 4.5 秒，是把「关键帧数」当成了「帧数」——
关键帧每 2 帧一个，所以跨度是 270 帧。）**

---

## 二、完整管道

```
resources/mod/108_bird.mod        网格 + 蒙皮（9 骨骼 / 146 顶点 / 190 三角）
resources/anm/108_birda.anm       动画（11 块，6 轨有键，30 fps）
        ↓  Tools/export_mod_anim_gltf.py
bird_anim.gltf + bird_anim.bin    一次导出，网格 + 动画在一个文件
        ↓  AssetImportTask（不给 factory → Interchange）
SK_BirdAnim                       SkeletalMesh
SK_BirdAnim_Skeleton              9 根骨骼
SK_BirdAnim_PhysicsAsset          自动生成
SK_BirdAnim_Anim                  9.0 秒动画
```

---

## 三、两个格式的对照表

| 项 | `.mod`（网格） | `.anm`（动画） |
| --- | --- | --- |
| 块标记 | `0xF4000000` = MESH<br>`0xF5000000` = BONE<br>`0x00F00000` = MATERIAL | **`0x0000F000`** |
| 块头 | 8 字节（marker + size）| 8 字节（marker + size）|
| 载荷头 | `FILE_BASE_OBJECT_HEADER` 324 + `FILE_MESH_HEADER` 48 | `FILE_MOTION_OBJECT_HEADER` **152** |
| 骨骼名 | 基类头 +196，128 字节 | 对象头 +20，128 字节 |
| 层级 | `dwParentObjectIndex`（基类头 +192） | — （动画按名字匹配）|
| 关键 | 每顶点 `bBonesNum`（1~3）个 BONE 记录，`fWeight` 在 +4 | POS(20) → ROT(24) → SCALE(40) |
| 时间 | — | **`dwTicks`，4800 ticks/秒** |
| 文件头长度 | 固定 28 字节 | **不固定（要扫描）** |

---

## 四、四个必须记住的实现细节

### 4.1 glTF 必须补齐到 4 个权重

**源：每顶点 1~3 个影响（`bBonesNum` 可变）。**
**glTF：`JOINTS_0` / `WEIGHTS_0` 必须正好 4 个。**

```
读 bBonesNum 个 (index, weight)
→ 补 0 到 4
→ 归一化（保证和 = 1）
```

### 4.2 坐标转换

```
位置:  (x, z, -y) × 0.01      Z朝上厘米 → Y朝上米
法线:  (x, z, -y)
四元数: (x, z, -y, w)
缩放:  (x, z, y)
UV:    (u, 1-v)               glTF 原点在左上
```

### 4.3 🔴 `byteLength` 必须在所有 accessor 写完后才算

**我踩过这个坑：**
```python
gltf = { ..., "buffers": [{"byteLength": len(binary)}] }   # ← 算早了
# 之后 add_view() 往 binary 追加动画数据
```

**结果：声明的缓冲大小比实际小，导入器报**
```
LogInterchangeEngine: Error: 缓冲文件大小不匹配
LogInterchangeEngine: Error: 提供的源数据中没有要导入的内容
```

**修法：在 return 之前重新赋值 `gltf["buffers"][0]["byteLength"] = len(binary)`。**

### 4.4 只有 6/9 骨骼有动画轨

```
matched bones: 6 of 9 -> Bone02, Bone01, Bone05, Bone04, Bone07, Bone09
```

**其余 3 根（`Bone03`、`Bone06`、`Bone08`）在 `.anm` 里 `rot=0 pos=0 scale=0` ——
它们在这个动作里不动，是**正常的**，不是丢失。**

---

## 五、七轮的完整弧线

| 轮次 | 关键进展 | 方法 |
| --- | --- | --- |
| 11 | API 体量实测 11,459 类 | 实测代替引用 |
| 12 | `.mod` 容器格式（8 字节头 / 三种标记）| 暴力搜索 + 验证 |
| 13 | 排除 f32/f16 法线 | 否定实验 |
| **14** | **`.mod` 完全解开** | **读研究区客户端源码** ← 转折点 |
| 15 | 导出 + 导入 → 骨骼网格 | 工程实现 |
| **16** | **`.anm` 解开 + 帧率 30 fps** | **先读源码（gotcha #81 生效）** |
| **17** | **动画导入 → AnimSequence** | 工程实现 |

**第 14 轮发现的教训（先读源码）在第 16 轮直接省了四轮。**

---

## 六、工具清单

| 工具 | 作用 |
| --- | --- |
| `Tools/parse_mod.py` | `.mod` 容器走块 |
| `Tools/verify_mod_layout.py` | `.mod` 逐字节验证（tail=0）|
| `Tools/export_mod_gltf.py` | 只导出网格 |
| `Tools/inspect_anm.py` | `.anm` 头部 dump |
| `Tools/scan_anm_blocks.py` | `.anm` 扫描块（不假设头长度）|
| `Tools/parse_anm_motion.py` | `.anm` 解析 + 逐块验算 |
| `Tools/verify_anm_tickrate.py` | 跨 60 文件统计 → 帧率 |
| **`Tools/export_mod_anim_gltf.py`** | **网格 + 动画合并导出** |
| `Tools/import_bird_anim.py` | 导入（Interchange）|
| `Tools/verify_bird_anim.py` | 验证动画长度 |

---

## 七、下一批（纯工程）

| 任务 | 说明 |
| --- | --- |
| **批量导出** | 现在一次一个；5,305 模型 + 4,014 动画要脚本化 |
| **材质** | 导入警告「未指定材质的图元」—— 要挂上贴图 |
| **逆绑定矩阵** | 当前是单位矩阵；如果动画姿态不对，要算真的 |
| **角色模型** | 现在只验证了鸟（9 骨骼）；要试 96 骨骼的人形角色 |
| **动画蓝图** | 有了 AnimSequence，可以建状态机了 |

---

## 八、重查命令

```powershell
# 导出（网格 + 动画）
python Tools\export_mod_anim_gltf.py `
  "C:\...\resources\mod\108_bird.mod" `
  "C:\...\resources\anm\108_birda.anm" `
  "C:\...\Assets\Moxiang\ue_import\bird_anim.gltf"

# 导入
py "Tools/import_bird_anim.py"

# 验证
py "Tools/verify_bird_anim.py"
```
