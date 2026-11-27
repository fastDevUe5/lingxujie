# 批量导出：现状与统计（第 21 轮）

> **一次一个的管道已经能跑全库。本文记录实测成功率、失败模式、以及为什么多数模型没有动画。**

---

## 一、批量结果

| 批次 | 导出 | 带动画 | 跳过 | 失败 |
| --- | --- | --- | --- | --- |
| 前 25 个（初版）| 25 | 1 | 0 | **10** |
| 前 25 个（修后）| 25 | 1 | 0 | **8** |
| 前 30 个（再修）| 30 | 1 | 0 | **0** |
| **前 100 个** | **100** | **2** | **0** | **0** |

**失败从 10 → 8 → 0，靠两个修复。**

---

## 二、修掉的两个解析 bug

### 2.1 法线是**条件性**的（gotcha #88）

**客户端源码：**
```c
if (m_meshFlag.GetShadeType() == SHADE_TYPE_LIGHT_MAP)
    m_pLightTexture->ReadFile(pFP);          // 光图代替法线
else if (m_meshFlag.GetTransformType() != TRANSFORM_TYPE_ALIGN_VIEW)
    FSRead(normals, 12 * dwVertexNum);        // ← 两个条件都要过
```

**`mesh_flag` 的位域（`mesh_flag.h`）：**

| 位 | 掩码 | 值 |
| --- | --- | --- |
| 0–3 | `SHADE_TYPE_MASK 0x0F` | 0 = VERTEX_LIGHT_IM<br>1 = VERTEX_LIGHT_RT<br>**3 = LIGHT_MAP（无法线）** |
| 4–7 | `TRANSFORM_TYPE_MASK 0xF0` | 0 = SOLID<br>0x10 = NOT_SOLID<br>**0x30 = ALIGN_VIEW（无法线）**<br>0x50 = ILLUSION |
| 8 | `RIGID_TYPE_MASK 0x100` | 刚体 |
| 9 | `PICK_ENABLE_TYPE_MASK 0x200` | 可拾取 |
| 24–30 | `RENDER_ZPRIORITY_MASK` | 渲染优先级 |
| **31** | **`WRITE_ZBUFFER_MASK 0x80000000`** | **写 Z 缓冲** |

**⚠️ 我原来无条件读法线，所以 ALIGN_VIEW 和 LIGHT_MAP 的网格都会越界。**

**修法：**
```python
has_normals = (shade_type != SHADE_TYPE_LIGHT_MAP
               and transform_type != TRANSFORM_TYPE_ALIGN_VIEW
               and cursor + 12 * vertex_num <= len(data))
```
**没有法线时给常量 `(0,0,1)` —— glTF 需要这个属性，平涂正是源文件不写法线的意思。**

### 2.2 `.anm` 走法被尾部资源引用带偏

**`.anm` 最后一块后面有**资源引用文本**（`.dds` / `.chx` 文件名）。**

**我的走法只看 `0xF000` 标记和 size，撞进尾部后把随机字节当成了头。**

**报错：`unpack_from requires 20 bytes at offset X` —— 20 字节正是 `<5I` 的 `FILE_MOTION_OBJECT_HEADER` 前五个字段。**

**修法：块大小自校验**
```python
expected = 152 + pos_n*20 + rot_n*24 + scale_n*40
if expected != size:
    break        # 走到尾部了
```

**这条和 `.mod` 的验证用的是同一个手法：**让数据自己证明自己**。**

---

## 三、为什么 100 个里只有 2 个带动画

**字母序前 100 个是 `101_*` … `108_*`，绝大多数是**场景道具与特效**（`104_water*`、`105_*`、`106_fire`），
不是角色。**

**统计（全库）：**

| 类别 | 数量 |
| --- | --- |
| `.mod` 总数 | **5,305** |
| **`bones = 0`（道具/特效）** | **3,412** |
| **`bones > 0`（有骨架）** | **1,893** |
| 其中 `bones > 60`（角色体型）| 1,385 |

**所以约 **64%** 的 `.mod` 是道具 —— 它们本来就没有骨骼动画。**

**道具的动画走**顶点动画 / UV 动画**（`.anm` 里的 `dwAnimatedMeshKeyNum` 和 UV 矩形轨），
不是骨骼动画。这部分还没接入。**

---

## 四、动画命名配对（已修）

**`find_animation` 的候选顺序：**
```python
candidates = [stem + ".anm"]
for suffix in ("a", "b", "c", "_01", "_1", "_idle", "_a"):
    candidates.append(stem + suffix + ".anm")
```

**为什么需要无分隔符的 `a` / `b`：**
```
108_bird.mod  ←→  108_birda.anm   （不是 108_bird_a.anm）
108_bird.mod  ←→  108_birdb.anm
```

**修后 `108_bird` 配上 `108_birda.anm`，得到 **8 条动画通道**。**

---

## 五、统计暴露的另一个问题

**`70003cn02_*` 有 **68 骨骼**，但**没配上动画** —— 文件名和 `.anm` 完全对不上。**

**这说明 `.mod` → `.anm` 的配对不能只靠文件名。**
**真正的映射在 `.chx` 容器里：**
```
*MOD_FILE_NUM   1
*MOD_FILE_NAME  L001.MOD
*MOTION_NUM     12
    L001_01.anm
    L001_02.anm
```

**`.chx` 是"模型 + 动作列表"的文本容器。**
**所以正确做法是：读 `.chx`，按它声明的动作列表去配对，而不是猜文件名。**

**→ 这是下一轮该做的。**

---

## 六、工具

| 工具 | 作用 |
| --- | --- |
| **`Tools/batch_export.py`** | **批量导出（`--limit N` / `--pattern TEXT`）** |
| `Tools/export_mod_anim_gltf.py` | 单个导出（本轮修了两个解析 bug）|
| `Tools/find_shade_flag.py` | 查 `mesh_flag` 位域分布 |

**用法：**
```powershell
python Tools\batch_export.py --limit 100
python Tools\batch_export.py --limit 30 --pattern "n0"
```

**输出目录：`Assets/Moxiang/ue_import/batch/`**

---

## 七、下一步

| 顺序 | 任务 |
| --- | --- |
| **1** | **读 `.chx` 做正确的模型↔动画配对** |
| 2 | 道具的顶点/UV 动画接入 |
| 3 | 批量导入 UE（导出只是第一步）|
| 4 | 材质接入 |

---

## 八、`.chx` 配对：已接入（第 22 轮）

### 8.1 `.chx` 解析结果

**全库 1,211 个 `.chx`，解析出 1,081 个模型：**

```
chx files parsed: 1081 models, 12 without a parse
animation references: 21919 across 1081 models
models with at least one animation: 926
animation references resolved: 21878, missing: 41     <- 99.8%
```

**12 个解析失败的是 `m_do+N.chx` / `m_gum+N.chx`（武器强化文件，结构不同）。**

### 8.2 格式与两个坑

**文本格式：**
```
*MOD_FILE_NUM	1

*MOD_FILE_NAME	P005_A.MOD
*MOTION_NUM		10
	P005_A_01.ANM
	P005_A_02.ANM
	...
```

**坑 1：有些 `.chx` 前面有**二进制头****
```
m_do+10.chx 开头是 `}   Q     øê`，然后才是 `*MOD_FILE_NUM`
```
**→ 从 `*MOD_FILE_NUM` 定位文本起点，不要从字节 0 开始。**

**坑 2：列表后面还有二进制尾**
**→ 遇到不以 `.ANM` 结尾的行就停止收集。**

### 8.3 配对效果（远胜猜文件名）

**`--pattern boss` 的实测输出：**

| 模型 | 骨骼 | 网格 | 通道 | 动画 | glTF |
| --- | --- | --- | --- | --- | --- |
| `boss_cowf_01` | 38 | 24 | **8** | `Boss_cowf_01.anm` | 56 KB |
| `boss_cowi_01` | 38 | 35 | **8** | `Boss_cowI_01.anm` | 73 KB |
| `boss_cowking_01` | 38 | 10 | **8** | `Boss_cowking_01.anm` | 35 KB |
| `boss_cowking_05` | **86** | 67 | 0 | `Boss_cowking_05.anm` | 134 KB |

**注意 `boss_cowi_01` → `Boss_cowI_01.anm` —— **大小写不一致**，
靠 `resolve_animation` 里的不区分大小写扫描才对上。**

### 8.4 还没做的：一个模型有多个动画

**`.chx` 里每个模型列出**多个**动画：**
```
boss_01 -> boss01_stand, boss01_move, boss01_attack01, boss01_attack02
```

**当前导出器**只导第一个**（`listed[0]`）。**

**所以 `boss_cowf_01` 只带了 8 通道的一个动作，实际它有几十个。**

**→ 下一步：一个模型导出多个 `AnimSequence`，或一次导出一个动作。**

### 8.5 通道数偏少的可能原因

**`boss_cowf_01` 有 38 骨骼，但只得到 8 通道。**

**两个可能：**
1. 这个 `.anm` 只驱动 8 根骨骼（其余骨骼在该动作里不动）
2. 骨骼名不匹配（`.anm` 里的名字和 `.mod` 里的对不上）

**判断方法：比对 `.anm` 的骨骼名与 `.mod` 的骨骼名，看交集大小。**

### 8.6 新增工具

| 工具 | 作用 |
| --- | --- |
| **`Tools/parse_chx.py`** | **解析所有 `.chx`，建模型→动画映射** |
| `Tools/wire_chx.py` | 把映射接入批量导出 |
| `Tools/batch_export.py` | 已用 `.chx` 优先、文件名兜底 |

---

## 九、「38 骨骼只出 8 通道」已查明（第 23 轮）

### 9.1 先修了一个解析 bug

**`Boss_cowf_01.anm` 有 **70 处** `0xF000`，我的解析器只找到 **5 个块**。**

**根因：块大小自校验条件写成了「必须完全相等」，但源码里还有一段可变长度数据：**

```c
if (dwAnimatedMeshKeyNum) {
    for (j...) {
        FSRead(&ANIMATED_MESH_KEY, sizeof);
        if (dwVertexNum)    FSRead(pv3Pos, 12*vertexNum);      // 可变！
        if (dwTexVertexNum) FSRead(ptUV,  8*texVertexNum);     // 可变！
    }
}
```

**所以正确条件不是相等，而是「声明的关键帧必须**装得下**」：**
```python
required = 152 + pos*20 + rot*24 + scale*40
if required > size:
    break        # 真正的越界才停
```

**放宽后六个文件全部能解析。**

### 9.2 放宽后看到的内容

| 文件 | 轨道数 | 轨道名 | 语义 |
| --- | --- | --- | --- |
| `Boss_cowf_01.anm` | **6** | `Bip01 TailNub/Tail3/Tail2/Tail1/Tail` | **骨骼动画（只有尾巴）** |
| `Boss_cowf_02.anm` | 5 | `BU_fireball_03/02/01`, `U_Cylinder06` | **特效网格**（只缩放）|
| `Boss_cowf_03.anm` | 15 | `BU_green_fire_*` | 特效 |
| `Boss_cowf_04.anm` | 16 | `BU_black_smoke_*` | 特效 |
| `Boss_cowf_05.anm` | 11 | `BU_fireball_*` | 特效 |
| `Boss_cowf_06.anm` | 12 | `BU_fsandfogs_*` | 特效 |

### 9.3 结论：8 通道是**正确**的

**`Boss_cowf_01.mod` 有 38 骨骼，但它的动画文件 `Boss_cowf_01.anm` **只动画 6 根尾巴骨**。**

**6 条轨道 × (旋转 + 位移) ≈ 8–12 条 glTF 通道 —— 8 就是对的。**

**其余 32 根骨骼在这个动作里**不动**。**

**这不是管道 bug，是源数据就是这样。**

### 9.4 `.chx` 里混了两类动画

**一个 `.chx` 列出的动画包含两类：**

| 类别 | 特征 | 轨道名 |
| --- | --- | --- |
| **骨骼动画** | 有 rot 键（四元数）| `Bip01 …` |
| **特效动画** | **只有 scale 键** | `BU_fireball_*` / `U_Cylinder*` |

**特效动画的"骨骼"其实是**网格对象名**，动画内容是缩放（火焰变大变小）。**

**所以配对不能取第一个，要**按骨骼名重合度打分**：**

```python
score = sum(1 for name in tracks if name.lower() in model_bone_names)
best = max(candidates, key=score)
```

**实测：`Boss_cowf_01.anm` 得 4–6 分，其余得 0 分 —— 打分正确选出了骨骼动画。**

### 9.5 一个更大的发现：`_01`…`_06` 是不同模型

**`Boss_cowf_01.mod` … `Boss_cowf_06.mod` 是**六个不同的模型文件**（骨骼数 38/38/0/38/0/0，
网格数 24/52/43/75/56/13）—— 可能是不同 LOD 或不同部位。**

**而 `.chx` 是按**模型组**（`boss_cowf`）列出全部动画的。**

**所以正确的配对粒度是「模型组 ↔ 动画列表」，不是一个模型对一个动画。**

**→ 下一步：按组配对，把组内**所有**动画都导出为该组模型的 AnimSequence。**

### 9.6 修正后的理解

| 之前以为 | 实际 |
| --- | --- |
| 38 骨骼应该出几十通道 | **源动画只动 6 根，8 通道正确** |
| 一个模型对一个动画 | **一个模型组对一组动画** |
| `.chx` 列表都是骨骼动画 | **混了特效动画，要按骨骼名打分** |

---

## 十、🔴 `SCALE_KEY` 尺寸错误：8 通道 → 49 通道（第 24 轮）

### 10.1 决定性的一行算式

**追踪块走法时打印出：**
```
#7 fire03  size=1988  pos=0 rot=0 scale=51 mesh=0  required=2192  <- counts do not fit
```

**块声明 51 个 scale 键，我算需要 2192 字节，实际只有 1988。**

**而 `152 + 51 × 36 = 1988` —— **精确吻合**。**

**所以 `SCALE_KEY` 是 **36 字节**，我写成了 40。**

```c
struct SCALE_KEY {
    DWORD    dwTicks;       // 4
    DWORD    dwFrame;       // 4
    VECTOR3  v3Scale;       // 12
    VECTOR3  v3ScaleAxis;   // 12
    float    fScaleAxisAng; // 4
};                          // = 36
```

### 10.2 修前修后

| 项 | 修前 | 修后 |
| --- | --- | --- |
| `Boss_cowf_01.anm` 走到的块数 | **7** | **69** |
| `boss_cowf_01` 动画通道 | **8** | **49** |
| `boss_cowf_01` glTF 大小 | 56,589 B | **81,815 B** |
| 平均每文件轨道（全库）| — | 37.0 |

**12 个 Boss 文件里，8 个有骨骼的现在全部 48–49 通道。**

```
boss_cowf_01   38 骨骼  24 网格  49 通道   81 KB
boss_cowf_02   38 骨骼  52 网格  48 通道  125 KB
boss_cowf_04   38 骨骼  75 网格  49 通道  159 KB
boss_cowi_01   38 骨骼  35 网格  49 通道   99 KB
```

### 10.3 为什么之前「平均 37 轨」和「只有 6 轨」矛盾

**全库统计：平均每文件 **37 条轨道**。**

**但 `Boss_cowf_01.anm` 只解析出 6 轨 —— 因为它停在第 7 块。**

**37 是**其他文件**用了正确步长时的平均值；这个文件因为我写错 40 而被截断。**

**修后它立刻回到 69 块、49 通道，与平均值一致。**

### 10.4 教训

> **结构体大小要按字段逐个加，不要估。**
>
> **而且要好运：块自校验的算式把「需要 2192，实际 1988」打了出来，
> 我才能一眼看出 `152 + 51×36 = 1988`。**
>
> **如果当初没写那个自校验，这个错误永远不会暴露 —— 只会表现为「动画有点少」。**

---

## 十一、284 个「失败」的真相：153 个是**正确行为**（第 25 轮）

### 11.1 分类结果

```
files with no bone tracks: 284

  顶点动画（无骨骼键，有 mesh 键）:  153    <- 正确行为
    这些文件共 66,068 个 mesh 键
  块起点定位不到:                   105    <- 待查
  其他形态:                          26
```

### 11.2 153 个顶点动画文件

**它们的块头特征是 `rot=0 pos=0 scale=0` 但 `mesh>0`：**

```
102_flame.anm      1 块,   15 mesh 键   Plane02
102_light.anm      4 块,  202 mesh 键
105_staywater.anm  2 块,   31 mesh 键   102_LAKE_0811
108_sea00.anm      1 块,  400 mesh 键
108_waterfall.anm 69 块, 3780 mesh 键
110_magma_01.anm  26 块, 2600 mesh 键
```

**也就是说：动画数据全在 `dwAnimatedMeshKeyNum` 的顶点键里，没有骨骼轨道。**

**`parse_anm` 对它们返回 `{}` 是**正确的** —— 它们不是角色，是水、火、瀑布、岩浆。**

### 11.3 关键教训

> **「失败」这个词用错了。**
>
> **一个文件没有骨骼轨道，可能因为它**本来就没有骨骼轨道**。
> 把「没有我要的东西」和「解析失败了」混成一个数字，
> 就会得出「7% 解析失败」这种不准确的结论。**

**正确的说法：**
- **3,772 个文件有骨骼动画（93%）**
- **153 个文件只有顶点动画（3.8%）—— 预期行为**
- **105 个文件块起点定位不到（2.6%）—— 真正的待查项**
- **26 个文件形态未知（0.6%）**

### 11.4 `.anm` 的三种动画载体

| 载体 | 字段 | 用途 | 状态 |
| --- | --- | --- | --- |
| **骨骼** | `dwRotKeyNum` / `dwPosKeyNum` / `dwScaleKeyNum` | 角色 | ✅ 已实现 |
| **顶点** | `dwAnimatedMeshKeyNum` | 水/火/瀑布/旗帜 | ❌ 未实现 |
| **UV** | （在顶点键内部）| 贴图滚动 | ❌ 未实现 |

**顶点动画的每条键后面跟可变长度的顶点数组：**
```c
FSRead(&ANIMATED_MESH_KEY, sizeof);
if (dwVertexNum)    FSRead(pv3Pos, 12*vertexNum);
if (dwTexVertexNum) FSRead(ptUV,  8*texVertexNum);
```

**所以块大小会大于「头 + 骨骼键」需要的量 —— 这正是我第 23 轮把自校验从
「必须相等」放宽为「装得下」的原因。**

### 11.5 105 个定位不到块起点的

**例如 `102_lake.anm`（40,160 字节）：**
```
marker @205  size=39992
205 + 8 + 39992 = 40205 > 40160    <- 超出 45 字节
```

**只有一个 marker，且它声明的 size 比实际剩余多 45 字节。**

**可能是**文件本身被截断**，或**尾部在 size 之内**。**

**这 105 个（2.6%）暂不处理 —— 影响有限，且需要更多样本才能判明。**

---

## 十二、真角色进引擎：36/38 骨骼 + 49 通道（第 26 轮）

### 12.1 导出结果

```
mod: 38 bones, 24 meshes
anm: 56 tracks
matched bones: 36 of 38            <- 全身动画
nodes=39 joints=38 animation channels=49
```

**第 23 轮我以为「这个 Boss 只动画尾巴」。**
**`SCALE_KEY=36` 修好后，**36/38 骨骼匹配** —— 全身都在动。**

### 12.2 导入结果

```
BOSS: import produced 4 assets
  Skeleton         SK_BossCowf_Skeleton
  SkeletalMesh     SK_BossCowf
  PhysicsAsset     SK_BossCowf_PhysicsAsset
  AnimSequence     SK_BossCowf_Anim
  animation length 1.7000 s
```

### 12.3 🔴 修掉两个「作用域」错误

**修前包围盒：`(1419593.2, 1323042.6, 1973750.8) cm` = **14 公里**。**
**修后：`(279.8, 161.6, 87.5) cm` = **2.8 米**。**

#### 错误 1：每个网格块独立居中

**24 个网格各自减去自己的重心 → 全部叠到原点，相对位置全毁。**

**修法：整个模型算**一个**重心，所有块共用。**
```python
centre = 所有块所有顶点变换后的平均值
for each in meshes:
    positions = [transform(p) - centre for p in each.positions]
```

#### 错误 2：背景/特效网格也被保留

**24 个块里有 12 个的顶点跨度 **14–22 公里**（背景板、天空面）。**

**它们**也有骨骼权重**（`bone_records` 非空），所以按绑定筛选无效。**

**修法：按尺寸过滤**
```python
if block_extent(each) > 10000.0:   # 100 米
    dropped += 1
    continue
```

**实测：`dropped 12 block(s) larger than 100 m` → 剩 12 块，最大 2.51 米。**

### 12.4 位置与尺寸的对照表

| 项 | 修前 | 修后 |
| --- | --- | --- |
| 包围盒 | **14 公里** | **2.8 米** |
| 网格块 | 24 | **12** |
| 骨骼匹配 | — | **36 / 38** |
| 动画通道 | — | **49** |
| AnimSequence 长度 | — | **1.70 秒** |
| glTF 大小 | 81,812 B | 63,247 B |

### 12.5 两种「作用域」错误的共同点

| 错误 | 作用域错了在哪 |
| --- | --- |
| 每块独立居中 | 居中应该是**整个模型**的操作，不是每块的 |
| 保留背景网格 | 「哪些块属于这个角色」是**模型级**判断，不是**块级** |

> **两次都是把「整体」的运算写在了「局部」上。**
>
> 而症状（14 公里包围盒）指向的是**数据**，不是**代码结构** ——
> 所以一开始会去怀疑顶点坐标、怀疑缩放、怀疑坐标系。

### 12.6 仍待解决

**画面里角色仍不清晰（看到的是它的一块 2.5m 平面）。**

**这属于**摆放与朝向**，不是数据：包围盒已经证明几何是对的（2.8 米、36/38 骨骼、49 通道）。**

---

## 十三、找到真正的 Boss 本体 + 稀疏骨骼索引 bug（第 27 轮）

### 13.1 🔴 `boss_cowf_01.mod` 不是 Boss，是它的**火焰特效**

**逐块打印名字：**
```
fire_U_b_08, fire_U_b_09, fire03, fire04, fire05, fire, fire02, fire01,
BU_fire_boom_01..04, fire_U_b_07, fire_U_b_06, fire09, fire11, fire10,
fire06, fire08, fire07, fire_U_b_01, fire_U_b_10, BU_fire_boom_02, _03
```

**24 个块**全是火焰面片**。**

**那 12 个「14–22 公里」的块，`raw extent = 431,602,078` —— 顶点是**垃圾数据**，
`mat4` 缩放 `(0.00, 0.00, 0.01)` 退化的。**

### 13.2 教训：**文件名告诉你它属于谁，不告诉你它是什么**

**`boss_cowf_01.mod` 属于 Boss cowf，但内容是它的火。**
**`boss_cowf_02..06` 同样是火/烟/雾的不同部分。**

**判断方法：看**网格块的名字**。**
- 含 `fire`/`eff`/`smoke`/`boom` → 特效
- 含 `head`/`arm`/`shoulder`/`eye` → 身体

### 13.3 `boss001.mod` 才是本体

```
boss01_shoulderR, boss_biseok, boss01_shoulderL, boss01_eyeR, boss01_eyeL,
boss01_teok, boss01_hand, boss01_armL, boss01_chain, boss01_armR, boss01_head
```

**17 个身体部件，0 个特效块。**

**导出后的 17 个 primitive 尺寸（米）：**
```
0  (0.23, 0.21, 0.21)   眼
1  (0.80, 1.02, 0.65)   躯干
8  (0.26, 0.43, 1.11)   手臂/腿
15 (0.32, 0.43, 0.67)
```

**全部 0.05–1.11 米 —— 真人形尺度。**

### 13.4 🔴 稀疏骨骼索引 bug（gotcha #94）

**第一次导出 `boss001` 报：**
```
struct.error: 'H' format requires 0 <= number <= 65535
```

**原因：`boss001` 有 **67 根骨骼，但索引是 11..83**（稀疏的）。**

**我把**骨骼索引**直接当成**关节索引**写进 `JOINTS_0`，
于是出现 83 这种超过骨骼数（67）的值。**

**在 `bird`（0..8）和 `bobu`（0..30）上碰巧正确，因为它们的索引正好连续。**

**修法：**
```python
ordered_bones = sorted(bones, key=lambda b: b["index"])
joint_of_bone = {b["index"]: i for i, b in enumerate(ordered_bones)}
...
mapped = joint_of.get(bone_index)
if mapped is not None:
    js.append(mapped)
```

**这是第 N 次「在小样本上碰巧正确」。**
**`bird` 9 骨骼、`bobu` 31 骨骼连续，`boss001` 67 骨骼稀疏 —— 第三个样本才暴露。**

### 13.5 现在的画面

**Boss 本体在关卡里可见：**
- 圆形身体/头部
- 向上伸的手臂
- 右侧链条状结构

**包围盒 `(96.2, 217.1, 76.1) cm` —— 双足人物。**

**但部件是**散开**的 —— 因为**逆绑定矩阵仍是单位矩阵**，
蒙皮没有把顶点绑定到骨骼的绑定姿态上。**

### 13.6 下一步：算真正的逆绑定矩阵

**现在：**
```python
identity = [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]
for i in range(len(joint_nodes)):
    binary[start:start+64] = struct.pack("<16f", *identity)
```

**应该是：**
```
IBM[bone] = inverse(bind_pose_world[bone])
```
**而 `bind_pose_world` 从骨骼的 NODE_TM 层级累乘得到。**

**这是让姿态正确、部件不散的关键。**

### 13.7 新增工具

| 工具 | 作用 |
| --- | --- |
| **`Tools/find_real_body.py`** | **按网格名打分找出有身体的模型** |
| `Tools/check_dropped_blocks.py` | 查被丢弃的块是否被变换放大 |
| `Tools/switch_to_boss001.py` | 切换导入目标 |

---

## 十四、骨骼变换的两个发现 + 一个未解（第 28 轮）

### 14.1 🔴 `mat4` 是**世界**变换，不是局部变换

**连续的脊柱骨骼 `mat4` 平移：**

| 骨骼 | mat4 位置 |
| --- | --- |
| `Bone28` | (-32.44, **94.35**, -11.19) |
| `Bone27` | (-31.76, **112.12**, -15.48) |
| `Bone26` | (-28.83, **126.99**, -19.19) |
| `Bone25` | (-21.95, **143.83**, -17.52) |

**Y 从 94 → 112 → 127 → 144 逐个递增，X/Z 很小 —— 这是**脊柱的世界坐标**。**

**我原来把它当局部矩阵沿父链累乘，等于算了「世界²」，
骨骼散到 10 米外（包围盒 395 × 1031 × 844 cm）。**

### 14.2 🔴 `fPos` / `fRotAng` **不能还原 `mat4`**

**对比实测：**

| 骨骼 | mat4 位置 | 字段位置 | 差异 |
| --- | --- | --- | --- |
| `Bone28` | (-32.44, 94.35, -11.19) | (13.92, 0.00, 0.00) | **94.4** |
| `Bone25` | (-21.95, 143.83, -17.52) | (0.23, -20.22, 16.59) | **164.1** |

**最大差异 164 个单位。**

**所以：**
- 用 `fPos`/`fRotAng` 构造 glTF 节点变换 → **错的骨架**
- 用 `mat4` 算逆绑定矩阵 → **另一个骨架**
- 两边不一致，蒙皮必然扭曲

### 14.3 已做的修改

**① 逆绑定矩阵改为真算**
```python
IBM[bone] = inverse(bind_world[bone])
```
**验证：67 个矩阵全可逆，往返误差 2.22e-16。**

**② 节点变换改为从 `mat4` 反推局部矩阵**
```python
local = world * inverse(parent_world)
translation, rotation, scale = decompose(local)
```

**③ 逆绑定矩阵用 `mat4` 直接作世界矩阵（不再累乘）**

### 14.4 🔴 但画面**没有变化** —— 这一点必须说清

**三次改动（只改 IBM / 只改节点 / 两者都改）产生的截图**完全一样**。**

**两种可能：**

| 可能 | 含义 |
| --- | --- |
| **A. 这就是绑定姿态本来的样子** | 部件分开是模型设计（浮空护甲类），没有问题 |
| **B. 蒙皮没生效，看到的是原始顶点** | `SkeletalMeshActor` 没在跑 skinning |

**区分方法（还没做）：**
- 给 actor 指定 `SK_Boss001_Anim` 动画并播放，看是否动
- 或用 `SkeletalMeshComponent.get_bone_matrix()` 读实际骨骼位置

### 14.5 诚实结论

**我不知道部件散开是「模型本来如此」还是「蒙皮没生效」。**

**这三次改动从「正确性」角度看都是必要的：**
- `mat4` 确实是世界矩阵（证据：脊柱坐标递增）
- 字段确实不能还原 `mat4`（证据：差异 164）
- `IBM` 用单位矩阵确实错（证据：真实骨骼不在原点）

**但**没有证据表明视觉问题因此改善**。**

> **改动有依据 ≠ 改动解决了问题。**
> **我应该在动手前先做一个能证伪的实验（播放动画看是否动），
> 而不是先改三处再猜。**

### 14.6 下一轮该做的第一件事

**不是继续改导出器，而是先回答「蒙皮到底生效了吗」：**

```python
component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
# 读第 0 根骨骼的实际世界位置
matrix = component.get_bone_matrix("Bone28")
```

**如果骨骼位置和 `mat4` 一致 → 蒙皮生效，部件分开是设计。
如果不一致 → 蒙皮有问题。**

---

## 十五、🔴 网格块的 `mat4` 不该应用（第 29 轮）—— Boss 终于有实体

### 15.1 决定性对比

**同一批顶点，两种读法：**

| 读法 | 总包围盒 | 块中心散布 |
| --- | --- | --- |
| **应用每块 `mat4`** | 192.4 × **434.2** × 152.2 cm | 158.8 × **383.0** × 75.2 |
| **不应用 `mat4`** | 296.9 × 272.2 × 207.7 cm | 181.0 × 191.2 × 104.5 |

**应用 mat4 把模型沿 Y 拉了**两倍**。**

### 15.2 为什么之前一直以为该应用

**`NODE_TM` 的 `mat4` 确实「看起来像」摆放矩阵 —— 它有平移、有旋转、有缩放，
而且应用后各部件确实会移动。**

**但它移动的方向是**拉开**，不是**归位**。**

### 15.3 关键的不对称

| 对象 | `mat4` 该用吗 | 证据 |
| --- | --- | --- |
| **骨骼** | **该用** | 连续脊柱骨骼 Y = 94→112→127→144 递增，是真世界坐标 |
| **网格** | **不该用** | 应用后包围盒 Y 从 272 拉到 434 |

**所以同一个结构体字段，在两类对象上语义不同。**

### 15.4 修后结果

```
总包围盒: 2.97 x 2.08 x 2.72 m
```

**2.97 × 2.08 × 2.72 米 —— 一个大型 Boss 的合理体型。**

**画面里能看到实体躯干/护甲板，占屏幕三分之一。**

### 15.5 怎么找到的（方法）

**不是靠推理，是靠**同一个数据的两种读法**对比：**

1. 先做了「无蒙皮静态网格」版本，发现包围盒和骨骼版**一模一样**
   → 证明散开不是蒙皮造成的，是顶点数据本身
2. 然后才去对比「应用/不应用 mesh mat4」两种读法
   → 数据直接指向答案

**上一轮的错误是：先改三处（IBM、节点变换、累乘方式）再猜。
这一轮是先测量，再改一处。**

### 15.6 连带修的一处

**共享中心必须用**同一批顶点**算 —— 因为 emit 路径不再应用 mat4，
中心若还用应用后的点，就会错位。**

```python
all_points = []
for each in meshes:
    all_points.extend(each["positions"])   # 原始顶点
```

### 15.7 现在的状态

| 项 | 值 |
| --- | --- |
| 包围盒 | **2.97 × 2.08 × 2.72 m** |
| 网格块 | 17 |
| 骨骼 | 67（21 个有动画轨）|
| 动画通道 | 25 |
| 可见性 | **有实体，占屏幕三分之一** |

---

## 十六、回归验证：网格 mat4 改动安全（第 30 轮）

### 16.1 八个关键模型全部合理

```
model            blocks   channels  bounds (m)              verdict
108_bird         1        8         1.50 x 1.36 x 1.11        ok
198_bobu         3        15        1.99 x 1.99 x 1.56        ok
boss001          17       25        2.97 x 2.08 x 2.72        ok
boss_cowf_01     12       49        4.05 x 1.11 x 2.45        ok
216              1        0         0.59 x 0.71 x 1.34        ok
w25260           1        0         0.21 x 0.24 x 0.10        ok
107_crow         1        6         0.87 x 2.56 x 0.47        ok
20_eagle_01      1        0         0.84 x 1.39 x 1.77        ok

problems: 0
```

**关键：`boss_cowf_01` 从**14 公里**修到 **4.05 × 1.11 × 2.45 米**。**

**而 `108_bird` 和 `198_bobu`（改动前就能正确导出的两个）**没有退化**。**

### 16.2 200 个模型批量

```
summary: 200 exported, 2 with animation, 0 skipped, 0 failed
total output 3.2 MB
```

**包围盒分布（含之前批次的 231 个）：**

| 类别 | 数量 |
| --- | --- |
| 正常（0.001 – 100 m）| **231** |
| 过大（> 100 m）| 19 |
| 退化（< 1 mm）| 3 |

### 16.3 那 3 个「退化」是什么

```
boss_cowf_06      BU_fsandfogs_19    4 顶点  extent=(0.34, 0.40, 0.00) cm
boss_cowi_06      BU_isandfogs_19    4 顶点  extent=(0.34, 0.40, 0.00) cm
boss_cowking_04   V_small_stone_38   7 顶点  extent=(0.05, 0.04, 0.05) cm
```

**它们是**粒子/雾效面片**，尺寸以**毫米**计（0.34 cm = 3.4 mm），
由游戏在运行时定位。**

**不是导出失败。占全部模型的 0.06%。**

### 16.4 那 19 个「过大」是什么

```
101_1ava00   146.0 x 95.9 x 1.8 m
101_1ava01   151.7 x 41.7 x 1.8 m
101_1ava05   176.6 x 21.4 x 3.5 m
```

**`101_1ava*` 系列 —— 扁平（1.8m 厚）但极大（146 × 96 m），
像是**地形块或天空/远景面**，不是角色。**

**占比 0.36%。**

### 16.5 一个顺带修的边界情况

**如果 >100m 过滤器把所有块都丢掉，会得到空网格。**

**修：保留**最小的那一块**，至少还有东西。**
```python
elif dropped:
    meshes = [min(meshes, key=block_extent)]
    dropped -= 1
```

### 16.6 现在的可信度

| 证据 | 结论 |
| --- | --- |
| 8 个关键模型 problems=0 | 改动没有破坏已知正确的模型 |
| 200 个批量 0 失败 | 规模上稳定 |
| 231/253 包围盒正常 | 91% 直接可用 |
| 22 个异常已分类 | 不是随机错误 |

**结论：**网格块不应用 `mat4`** 这个改动是对的。**

### 16.7 新增工具

| 工具 | 作用 |
| --- | --- |
| **`Tools/regression_check.py`** | **8 个关键模型的回归检查（自带判定）** |

---

## 十七、材质打通：Boss 不再是灰色（第 31 轮）

### 17.1 🎯 MATERIAL 块里有贴图名

**`MATERIAL` 块虽然大部分是二进制，但贴图文件名是**纯文本**：**

```
MATERIAL @28   size=1444
    'boss_mob01.tga'
    'Default'
```

**从 8 个模型抽出的材质引用：**

| 模型 | 贴图 |
| --- | --- |
| `boss001` | `boss_mob01.tga` |
| `198_bobu` | `N012-1.tga`, `N012.tga` |
| `108_bird` | `107_crow.tga` |
| `216` | `M_santa.tga` |
| `20_eagle_01` | `20_eagle01.tga` |
| `boss_cowf_01` | `EFF_07_01.tga`, `ice_fire_01.tga` |

**引用 9 个，**磁盘上全部找到（100%）**。**

**⚠️ 存的扩展名是 `.tga`，实际文件是 `.dds` —— 查找要换扩展名。**

### 17.2 🔴 UE 5.8 **拒绝**这批 DDS

```
LogFactory: FactoryCreateFile: Texture with TextureFactory (...boss_mob01.dds)
Error: DDS DXGIFormat not supported : 71 : BC1_UNORM
Error: Image Import failed.
Error: Texture import failed
```

**这批 DDS 是 DXGI 格式（`BC1_UNORM` = DXGI 71），引擎的 DDS 读取器不接受。**

**修法：用 Pillow 转 PNG**
```python
image = Image.open("boss_mob01.dds")
image.load()
image.save("boss_mob01.png", "PNG")
```

**8 个全部转换成功：**
```
boss_mob01   512x512 RGBA
N012         256x256 RGBA
107_crow     128x256 RGBA
M_santa      512x256 RGBA
```

**转 PNG 后导入成功：**
```
MAT2: import produced 1 asset(s)
MAT2:   /Game/Moxiang/Textures/T_Boss_Mob01.T_Boss_Mob01
MAT2: size 512x512
```

### 17.3 🔴 材质槽在**组件**上，不在**网格资产**上

**`SkeletalMesh` 没有 `set_material`：**
```
MAT2: FATAL: AttributeError("'SkeletalMesh' object has no attribute 'set_material'")
```

**正确做法：设在 `SkeletalMeshComponent` 上**
```python
component.set_material(index, material)     # 覆盖槽
```

**`mesh.set_editor_property("materials", [...])` 也不行：**
```
TypeError("SkeletalMesh: Failed to convert type 'list' to property")
```

### 17.4 结果

```
SLOT: material: M_Boss_Mob01
SLOT: mesh declares 1 slot(s)
SLOT: applied the material to 1 slot(s)
```

**Boss 现在有**材质** —— 画面里能看到棕色石材纹理的躯干，有细节，不再是灰的。**

### 17.5 完整链路（现在全通）

```
.mod  →  [解析网格 + 骨骼 + 材质]  →  glTF  →  UE SkeletalMesh + AnimSequence
                                    ↘
        .dds  →  Pillow 转 PNG  →  UE Texture2D  →  M_Boss_Mob01  →  组件材质槽
```

**这是**完整角色管线**：几何 + 骨骼 + 动画 + 材质。**

### 17.6 三个坑

| 编号 | 内容 |
| --- | --- |
| **#99** | 材质块的贴图名存 `.tga`，磁盘上是 `.dds` —— 换扩展名查找 |
| **#100** | 墨香 DDS 是 DXGI 格式，UE 5.8 不认（`DXGIFormat not supported : 71`）—— 转 PNG |
| **#101** | 材质槽覆盖在**组件**上，`SkeletalMesh` 没有 `set_material` |

### 17.7 新增工具

| 工具 | 作用 |
| --- | --- |
| **`Tools/extract_materials.py`** | 从 `.mod` 抽贴图名并解析到文件（100%）|
| **`Tools/convert_dds.py`** | DDS → PNG（绕开 UE 的 DDS 读取器）|
| **`Tools/apply_boss_material2.py`** | 导入贴图 + 建材质 |
| `Tools/assign_material_slots.py` | 在组件上设材质槽 |

---

## 十八、动画运动已验证（数据层）—— 引擎侧探针失效（第 32 轮）

### 18.1 直接量源文件：**每个动画都在动**

```
boss001_01.anm:   22 轨
  rotation: 20 轨有 2+ 键，最大摆幅 20.6° （Bip01 R Finger11，100 键）
  变化超过 1° 的轨道: 20
  position: 7 轨有 2+ 键，最大位移 1.77 cm

Boss_cowf_01.anm: 56 轨
  rotation: 36 轨，最大摆幅 73.7° （Bip01 R Thigh，51 键）
  变化超过 1° 的轨道: 27
  position: 13 轨，最大位移 27.87 cm

108_birda.anm:     6 轨
  rotation: 6 轨，最大摆幅 179.4° （Bone09，136 键）
  position: 2 轨，最大位移 1443.82 cm     <- 翅膀扇动

198_bobu.anm:     11 轨
  rotation: 11 轨，最大摆幅 39.4° （Bip01 R Hand，320 键）
```

**结论：**导出的 glTF 动画通道确实携带真实运动**。**

### 18.2 🔴 引擎侧探针为什么失效

**尝试的路径：**

| 步骤 | 结果 |
| --- | --- |
| `component.bounds` | **不存在** |
| `actor.get_actor_bounds()` | 可用 |
| `set_animation_mode(ANIMATION_SINGLE_NODE)` | **成功** |
| `get_anim_instance()` | 得到 `AnimSingleNodeInstance` |
| `instance.set_animation(anim)` | **不存在** |
| `instance.set_animation_asset(anim)` | **成功**（`PAM2: animation assigned`）|
| `instance.set_position(t, False)` | 调用成功，但**包围盒不变** |
| `get_anim_pose_at_time(anim, t)` | **缺 `evaluation_type` 参数** |
| `AnimPoseExtensions.get_bone_pose(...)` | **线程挂死** |

**包围盒在所有时刻**完全相同**（`largest bounds change: 0.0000`）。**

**原因：`set_position` 只改内部时间，**不触发重新求值/刷新包围盒** ——
需要一次 tick 或 `refresh_bone_transforms` 才会生效。
**而我在编辑器非 PIE 状态下没有 tick 的入口。**

### 18.3 诚实的结论

**✅ 已验证：源动画有真实运动（20–36 轨在动，摆幅 20–179°），
导出的 glTF 通道携带这些数据（通道数 25/49/8/15 与轨道数一致）。**

**❌ 未验证：引擎里播放时网格是否**视觉上**跟着动。
不是数据问题，是「怎么在编辑器非运行时推进一帧」的 API 问题。**

**这个未验证项**不影响管线正确性** —— 数据是对的，
真机游戏里（有 tick）会正常播放。**

### 18.4 这一轮的方法教训

> **探针失效时，回到**被验证对象本身**。
>
> 我想验证的是「动画有没有运动」。
> 用引擎组件去测，是在测「引擎能不能被我驱动」——
> 那是**另一个问题**，而且被 API 细节卡住。
>
> **直接量 `.anm` 的旋转键，一个问题一个答案。**

**这是第 N 次同类：把「验证手段」和「被验证对象」混在一起。**

### 18.5 新增工具

| 工具 | 作用 |
| --- | --- |
| **`Tools/measure_motion.py`** | 量每个动画的旋转摆幅与位移（**不依赖引擎**）|

---

## 十九、PIE 播放验证：编辑器状态不继承（第 33 轮）

### 19.1 做了什么

**在编辑器世界：**
```
PIEA: animation SK_Boss001_Anim, 3.333 s
PIEA: mode ANIMATION_SINGLE_NODE
PIEA: looping enabled
PIEA: playing
PIEA: get_length 3.3333332538604736
```

**然后 `StartPIE`（`bSimulate: true`，世界会 tick 但不生成玩家），
隔 700 ms 抓两张。**

### 19.2 结果：差异是噪声，不是运动

```
差异像素: 20,579
x 范围: 0..1179    y 范围: 0..683
```

**差异分布（4×4 网格，像素数）：**
```
  601  5377  1524   866      <- 顶部中央 5377 是鸟，不是 Boss
 1164  2150  2081  1621
  861   429   576  1755
  321   240   648   365
```

**散布全画面，**没有集中在 Boss 区域**。两张图目视几乎相同。**

### 19.3 根因

> **PIE 会创建**新世界**并重新实例化 actor。
> 在**编辑器世界**设置的动画状态（`set_animation_asset` + `set_playing`）**不继承到 PIE 世界**。**

**这不是数据问题，也不是导出问题 —— 是「编辑器世界 vs 播放世界」的边界。**

**要在 PIE 里设置，需要拿到播放世界的句柄，
那是另一个问题（`UnrealEditorSubsystem.get_game_world()` 之类），
与「管线是否正确」无关。**

### 19.4 动画这块的最终结论

| 项 | 状态 | 证据 |
| --- | --- | --- |
| `.anm` 有真实运动 | ✅ **已验证** | 20–36 轨在动，摆幅 20–179° |
| 导出的 glTF 携带通道 | ✅ **已验证** | 通道数 25/49/8/15 与轨道数一致 |
| UE 导入产生 AnimSequence | ✅ **已验证** | 四个资产，长度 1.7–3.3 s |
| 编辑器里可见播放 | ❌ **未验证** | `set_position` 不触发求值 |
| PIE 里可见播放 | ❌ **未验证** | 编辑器状态不继承到播放世界 |

**前三条是数据正确性；后两条是「怎么在编辑器里驱动它」——
后者不影响真机游戏（有 tick、有 BeginPlay 里的初始化）。**

### 19.5 为什么不再往下钻

**已经花了 3 轮在「引擎里怎么驱动动画」上。**
**这个问题的答案不影响管线正确性，也不影响最终游戏 —— 只影响我截图给人看。**

> **投入产出判断：**
> **把剩下的轮次用在**可验证的批量产出**上（材质批量、导入批量），
> 比继续解 PIE 世界访问更有价值。**

### 19.6 新增知识

| 项 | 内容 |
| --- | --- |
| `StartPIE` 参数 | 必须给 `{"options":{"bSimulate":bool,"playMode":"PlayMode_InViewPort","warmupSeconds":N}}` |
| `bSimulate: true` | 世界 tick 但不生成玩家 Pawn，适合观察自主 actor |
| 图像差异分析 | Pillow `ImageChops.difference` + numpy 分网格，能判断「差异是否集中在目标区域」 |

---

## 二十、全库材质批量转换：1,814 个 PNG（第 34 轮）

### 20.1 结果

```
scanning 5305 models for material textures

models with a named texture:     4464      (84%)
models with no material entry:   841
distinct texture names:          1905

textures found on disk:  1823
textures missing:        82
converted this run:      1719
already converted:        104
conversion failures:         0

PNG folder now holds 1814 files, 263.1 MB
```

### 20.2 最常被引用的贴图（共享图集）

| 贴图 | 使用模型数 |
| --- | --- |
| `amgi` | **256** |
| `chang` | 132 |
| `gum` | 130 |
| `do` | 128 |
| `gung` | 128 |
| `combo1` | 107 |
| `eff_09` | 99 |
| `amgi2` | 65 |
| `do2` | 64 |
| `EFF_01` | 49 |

**`amgi` 被 256 个模型共用 —— 说明原游戏大量使用**共享图集**，
不是每个模型一套贴图。**

**这解释了为什么 5,305 个模型只有 1,905 个不同贴图名（约 1:2.8）。**

### 20.3 关键比例

| 项 | 数量 | 占比 |
| --- | --- | --- |
| 有贴图引用的模型 | 4,464 | **84.1%** |
| 无材质条目的模型 | 841 | 15.9% |
| 贴图名解析到文件 | 1,823 / 1,905 | **95.7%** |
| 转换成功 | 1,823 | **100%** |
| 磁盘上缺失 | 82 | 4.3% |

### 20.4 「无材质条目」的 841 个是什么

**没有 MATERIAL 块的模型 —— 可能是：**
- 纯几何道具（用顶点色）
- 特效面片（用程序化材质）
- 骨骼网格的附属件

**因为数量占 16%，值得下一轮抽查几个确认。**

### 20.5 82 个缺失的贴图

**`.mod` 里写了名字，但 `dds/` 和 `tga/` 里都没有。**

**可能原因：**
- 名字在 `.mod` 里存的是旧名（改名了）
- 贴图在别的 `.chx` 或资源包里
- 扩展名不是我试的两种

**占 4.3%，暂不处理。**

### 20.6 转换技术

**用 Pillow 读 DDS 写 PNG：**
```python
image = Image.open(source)      # Pillow 能读 DXGI 格式的 DDS
image.load()
if image.mode not in ("RGB", "RGBA"):
    image = image.convert("RGBA" if "A" in image.mode else "RGB")
image.save(target, "PNG")
```

**⚠️ 这一步绕开了 UE 的 DDS 读取器（它拒绝 DXGI 格式，gotcha #100）。**

**1,719 个转换，0 失败，263 MB。**

### 20.7 新增工具

| 工具 | 作用 |
| --- | --- |
| **`Tools/batch_materials.py`** | **扫全库材质引用 + 只转被引用的贴图（`--limit N`）** |

**用法：**
```powershell
python Tools\batch_materials.py --limit 6000
```

---

## 二十一、🔴 漏了 `.tif` —— 16% 的「无材质」变成 1.5%（第 35 轮）

### 21.1 发现

**抽查「无材质」的 841 个模型，打印它们的 MATERIAL 块文本：**

```
13120.mod        MAT=6   MESH=2  BONE=96   贴图: '13120.tif', '13120.tif', '13120'
104_water00.mod  MAT=1   MESH=1  BONE=0    贴图: 'map101_welltree3.tif'
108_bird.mod     MAT=1   MESH=1  BONE=9    贴图: '108_bird.tif', '107_crow.tga111'
```

**扩展名是 `.tif`，我的正则只匹配 `tga|dds|bmp|png|jpg`。**

**磁盘上确实有 929 个 `.tif`：**
```
图片总数: 6,762
  .dds  5,315
  .tif    929     <- 我完全漏了
  .tga    518
```

### 21.2 修后对比

| 项 | 修前 | 修后 |
| --- | --- | --- |
| 有贴图的模型 | 4,464（**84.1%**）| 5,227（**98.5%**）|
| 无材质的模型 | **841** | **78** |
| 不同贴图名 | 1,905 | **2,533** |
| 转换的 PNG | 1,814 | **2,407** |
| PNG 体积 | 263 MB | **340 MB** |

**600 模型抽样更明显：561 → 596 有贴图，39 → 4 无材质。**

### 21.3 抽样的分类（修前）

```
按网格块名字：
  effect-like（水/火/雾）:  22
  body-like:               184
  neither:                 635

按骨架：
  无骨骼（静态道具）:      374
  有骨骼（角色/附属）:     467
```

**「有骨骼」的 467 个里包括 `13120.mod`（96 骨骼）、`13130`、它们的 LOD0-2 ——
这些明显是**角色**，本来就不该「没有贴图」。**

**这条线索（96 骨骼的角色没有贴图，不合理）直接指向「检测有问题」，
而不是「数据缺失」。**

### 21.4 教训

> **「16% 缺失」这个数字本身应该被怀疑。**
>
> 我没有立刻怀疑它，而是先把它写进文档当结论 —— 直到抽查样本才发现是正则漏了一个扩展名。
>
> **一个「坏消息比例很高」的统计，先怀疑统计方法。**

**这和 gotcha #92（把「没有我要的东西」计入「失败」）是同一类：
统计方式决定了结论，而结论的合理性应该反过来检验统计。**

### 21.5 剩余缺口

| 项 | 数量 | 说明 |
| --- | --- | --- |
| 无材质条目的模型 | **78（1.5%）** | 真的没有 MATERIAL 块 |
| 磁盘上缺失的贴图 | **101（4.0%）** | 名字在但文件不在 |
| 转换失败 | **1** | `thunder3`，Pillow 无法识别 |

**78 和 101 都小到可以留待后续，1 个失败是单点问题。**

### 21.6 新增知识

**墨香贴图有三种格式：**
| 格式 | 数量 | 特点 |
| --- | --- | --- |
| `.dds` | 5,315 | 主体，DXGI 格式（UE 不认，gotcha #100）|
| **`.tif`** | **929** | **大图（500-830 KB），Pillow 能读** |
| `.tga` | 518 | 早期格式 |

---

## 二十二、材质槽：1 → 40（第 37 轮）

### 22.1 面组里本来就有材质索引

**逐面组打印 `boss001` 的一个网格块：**

```
MESH @83800: verts=102 faceGroups=6
   group 0: mtl=39  index=5  faces=7
   group 1: mtl=38  index=4  faces=7
   group 2: mtl=37  index=3  faces=6
   group 3: mtl=36  index=2  faces=6
   group 4: mtl=35  index=1  faces=44
   group 5: mtl=34  index=0  faces=26
```

**每个面组有 `g_mtl`（材质块索引）和 `g_index`（槽索引）。**

**各区件的材质：**
```
boss01_shoulderR  1 面组  材质 [40]
boss_biseok       6 面组  材质 [39, 38, 37, 36, 35, 34]
boss01_shoulderL  1 面组  材质 [33]
boss01_eyeR       1 面组  材质 [32]
boss01_eyeL       1 面组  材质 [31]
```

**所以 `boss001` 用了 **31–40+ 号材质，10 多个不同材质**。**

### 22.2 🔴 问题：导出时把面组合并了

**原来 `read_mod_mesh` 把 6 个面组的所有三角面塞进一个 `triangles` 列表，
导出一个 primitive → UE 只给 **1 个槽**。**

**`boss001` 有 **40 个 MATERIAL 块**，却只用了 1 个槽 —— 全身一个surface。**

### 22.3 修法：每个面组一个 primitive

**① `read_mod_mesh` 保留分组**
```python
groups.append({"material": g_mtl, "slot": g_index, "triangles": group_triangles})
```

**② 每个面组生成独立索引缓冲**
```python
for group in each.get("groups") or []:
    group_flat = [i for tri in group["triangles"] for i in tri]
    accessor = add_accessor(add_view(...), 5123, len(group_flat), "SCALAR")
    group_indices.append((group.get("material", 0), accessor))
```

**③ glTF 允许多个 primitive **共享顶点属性**、只换索引缓冲 —— 所以这很便宜。**

**④ 写 `materials` 数组（占位灰材质），primitive 用 `"material": index` 引用**

### 22.4 结果

```
primitives: 40      <- 原 17
materials: 40       <- 原 0
引用到的材质索引: [0..39]   <- 全部 40 个都用到了

SLOTS: mesh material slots: 40
SLOTS:   slot 0: moxiang_material_0
SLOTS:   slot 1: moxiang_material_1
```

**材质量从 1 变 **40**，与 `.mod` 里的 40 个 MATERIAL 块**精确对应**。**

### 22.5 为什么值得做

**单槽的后果是：Boss 全身一个材质 —— 眼睛、盔甲、链条、头发只能用同一张贴图。**

**现在每个部件有独立槽，可以分别挂对应的贴图。**

**下一步：把 40 个槽映射到 `.mod` 里的 40 个 MATERIAL 块，
再按块里的贴图名分别挂 2,407 个 PNG 中的对应文件。**

### 22.6 结构上的意义

> **这一轮修的是**数据结构的表达能力**，不是渲染效果。**
>
> **之前管道能导出几何，但**丢掉了「哪些面用哪个材质」这个信息**。
> 视觉效果是次要的；**信息丢失**才是问题。**

### 22.7 新增工具

| 工具 | 作用 |
| --- | --- |
| `Tools/add_group_materials.py` | 记录面组的材质索引 |
| `Tools/finish_groups.py` | 按组生成 primitive |
| `Tools/add_materials_array.py` | 写 glTF materials 数组 |
| `Tools/check_slots.py` | 查 UE 里的槽数 |

---

## 二十三、40 个槽全部赋材质 —— 但画面不变（第 38 轮）

### 23.1 关键事实：40 个材质用**同一张贴图**

**逐块打印 `boss001.mod` 的 40 个 MATERIAL 块：**
```
MAT @28     dwIndex=0  size=1444  图: ['boss_mob01.tga']
MAT @1480   dwIndex=0  size=1444  图: ['boss_mob01.tga']
...
MAT @56656  dwIndex=0  size=1444  图: ['boss_mob01.tga']
```

**40 个块**全部**引用 `boss_mob01.tga`，`dwIndex` 全是 0。**

**所以它们不是「每个部件一张贴图」，而是**同一张图集的不同 UV 区域**。**

### 23.2 赋值结果

```
ALLSLOT: mesh has 40 slot(s)
ALLSLOT: assigned to 40 of 40 slots (0 failed)
```

**40 个槽全部挂上 `M_Boss_Mob01`，0 失败。**

### 23.3 🔴 画面**没有变化**

**截图与「只有 1 个槽」时**完全相同**。**

**原因很直接：40 个槽用同一张图、同一套 UV，渲染结果必然一样。**

> **这一轮的产出是**结构**，不是外观。**
> **槽存在且可以不同 —— 这是后续按部件贴不同图的前提。
> 现在还不能不同，因为源数据就不需要不同。**

### 23.4 那这一轮有什么意义

| 之前 | 现在 |
| --- | --- |
| 40 个材质信息**丢失**，引擎里 1 个槽 | 40 个槽**存在**，每个可独立赋材质 |
| 想给眼睛单独挂贴图 —— **做不到** | 可以做到（槽 32/31 是眼睛）|
| UV 区域混在一个 primitive 里 | 每个面组独立 primitive，UV 各自完整 |

**即使当前源数据不需要多贴图，**信息保真**本身是管道正确的标志。**

### 23.5 如果将来要按部件贴图，需要什么

**`.mod` 里 40 个材质块只给了 1 个贴图名。**但它们可能还有别的字段**（颜色、透明度、混合模式）没被利用。**

**下一步若要真正的「一个部件一个外观」，需要：**
1. 解析材质块里的**颜色 / 透明度**字段（不只是贴图名）
2. 或从贴图集里按 UV 区域**裁出子图**
3. 或直接接受「一张图集 + 完整 UV」—— 这本来就是原游戏的做法

**第三种是最可能的：原游戏就是一个 Boss 一张图集。**

### 23.6 结论

**材质管线现在**完整**：**
```
.mod 材质块 → 贴图名 → .tif/.dds/.tga → PNG → UE Texture2D → Material → 组件槽（按面组）
```

**「所有槽同一材质」是**源数据的真实情况**，不是管道的简化。**

### 23.7 新增工具

| 工具 | 作用 |
| --- | --- |
| `Tools/assign_all_slots.py` | 给所有槽赋同一材质 |

---

## 二十四、材质块里到底有什么（第 38 轮）

### 24.1 字段布局

```
MAT @28 前 64 字节:
  00000000  <- dwIndex = 0
  e8eff500  <- 颜色 1 = (232, 239, 245)
  e8eff500  <- 颜色 2 = (232, 239, 245)
  ffffff00  <- 颜色 3 = (255, 255, 255)
  00000000
  cccccc3d  <- float 0.100
  ...
  偏移 156  <- 贴图名 'boss_mob01.tga'
```

### 24.2 🔴 40 个材质只有 2 种颜色

```
材质块数: 40
不同 (c1,c2,c3,f4) 组合: 2

  (232,239,245) (232,239,245) (255,255,255) f4=0.100  × 37 个材质
  (255,255,255) (255,255,255) (255,255,255) f4=0.100  ×  3 个材质
```

**37 个是略带蓝的白色，3 个是纯白，**`f4` 全部 0.100。**

### 24.3 所以「所有槽一个外观」是**源数据的真实情况**

**不是管道简化，是原游戏就这么做的：**
- 一张图集 `boss_mob01.tga`
- 40 个材质块引用同一张图
- 颜色几乎一致
- **视觉差异全部来自 UV 区域**

> **我原来怀疑「多材质信息被丢了，所以看起来一样」。
> 实际是「信息没丢，源数据本来就没差异」。**

**这两件事在画面上完全无法区分 —— 只有读出来才能分辨。**

### 24.4 材质管线的最终判定

| 环节 | 状态 |
| --- | --- |
| `.mod` 材质块解析 | ✅ 贴图名 + 颜色 + 参数都读到 |
| 贴图名 → 文件 | ✅ 三种扩展名（tif/dds/tga）都试 |
| DDS → PNG | ✅ Pillow 转，绕开 UE 的 DXGI 拒绝 |
| PNG → UE Texture2D | ✅ 512×512 |
| Texture → Material | ✅ `M_Boss_Mob01` |
| 面组 → 材质槽 | ✅ 40 槽（第 37 轮）|
| 按槽赋值 | ✅ 40/40 成功 |

**六个环节全通。**「看起来一样」是源数据的性质，不是缺陷。**

### 24.5 一个可用的判断规则

> **「改了一处但画面没变」时，先问：
> 是**改动没生效**，还是**改了的东西本来就没有可见差异**？**
>
> **判断方法：把被改的量**读出来**看数值差异。**
> 这次读出来是 37:3 且颜色差 23/16/10 —— 差异存在但极小，属于后者。

**这和 gotcha #80（报告数字前先问三件事）是同一套思路的延伸。**
