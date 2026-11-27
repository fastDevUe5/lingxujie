# NEXT-SESSION 归档 · 第 41–60 节

> 从 `Docs/NEXT-SESSION.md` 分出来的历史（2026-11-27）。**当前状态看主文件。**

## 41. 第二十四轮：**一个字节数藏住了大部分动画**（2026-11-26 27:30）

### 一、决定性的一行算式

**追踪块走法时打印：**
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

### 二、修前 vs 修后

| 项 | 修前 | 修后 |
| --- | --- | --- |
| `Boss_cowf_01.anm` 走到的块数 | **7** | **69** |
| `boss_cowf_01` 动画通道 | **8** | **49** |
| `boss_cowf_01` glTF 大小 | 56,589 B | **81,815 B** |
| 全库 `anm` 解析成功 | 3,539 / 4,056 | **3,772 / 4,056** |
| 全库平均轨道数 | 37.0 | **38.2** |
| 全库总轨道 | 130,955 | **144,081** |

**12 个 Boss 里 8 个有骨骼的，现在全部 48–49 通道。**

### 三、怎么发现的（方法值得记）

**两条证据交叉：**

1. **全库统计：平均每文件 37 条轨道** —— 所以「Boss 只有 6 轨」是**异常值**
2. **文件里有 70 个块标记，只解析出 7 块** —— 说明**走法停了**

**两条一对，指向「算术有问题」，而不是「动画稀疏」。**

**然后追踪打印把算式显式打出来，`152 + 51×36 = 1988` 一眼可见。**

### 四、教训（gotcha #91）

> **结构体大小要按字段逐个加，不要估。**
>
> **而且要有算术自校验** —— 块自校验把「需要 2192，实际 1988」打了出来，
> 我才能一眼看出 36 是对的。
>
> **如果当初没写那个自校验，这个错误永远不会暴露 —— 只会表现为「动画有点少」。**

### 五、上一轮的结论被推翻

**第 23 轮我写「8 通道是**正确**的，源动画只动 6 根尾巴骨」。**

**那是**错的** —— 8 通道是我的 bug 造成的。**

**修正：源动画确实动画了 69 块（含 nub 和特效），38 骨骼的 Boss 出 49 通道是对的。**

**第 N 次同类错误：把「我解析出来的」当成了「源数据就是这样」。**

### 六、当前状态

| 项 | 值 |
| --- | --- |
| 全库 `.anm` 解析成功率 | **3,772 / 4,056 = 93%** |
| 剩余失败 | 284 个（6.9%）|
| 全库总轨道 | **144,081** |
| 平均每文件 | **38.2** |

**剩下 284 个失败的原因还没查（可能是另一种块结构或损坏文件）。**

### 七、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **查剩下 284 个 `.anm` 失败的原因** |
| 2 | 批量重导（步长修了，旧输出要重生成）|
| 3 | 批量导入 UE |
| 4 | 材质接入 |


## 42. 第二十五轮：「284 个失败」里 153 个是**正确行为**（2026-11-26 28:00）

### 一、分类结果

```
files with no bone tracks: 284

  顶点动画（无骨骼键，有 mesh 键）:  153    <- 正确行为
    这些文件共 66,068 个 mesh 键
  块起点定位不到:                   105    <- 待查
  其他形态:                          26
```

### 二、153 个顶点动画文件

**块头特征：`rot=0 pos=0 scale=0` 但 `mesh>0`。**

```
102_flame.anm      1 块,   15 mesh 键   Plane02
102_light.anm      4 块,  202 mesh 键
105_staywater.anm  2 块,   31 mesh 键
108_sea00.anm      1 块,  400 mesh 键
108_waterfall.anm 69 块, 3780 mesh 键
110_magma_01.anm  26 块, 2600 mesh 键
```

**动画数据全在 `dwAnimatedMeshKeyNum` 的顶点键里，没有骨骼轨道。
`parse_anm` 返回空是**正确的** —— 它们是水、火、瀑布、岩浆。**

### 三、修正后的真实分布

| 类别 | 数量 | 性质 |
| --- | --- | --- |
| 有骨骼动画 | **3,772（93%）** | 正常 |
| 只有顶点动画 | **153（3.8%）** | **预期行为** |
| 块起点定位不到 | **105（2.6%）** | 真正的待查项 |
| 形态未知 | **26（0.6%）** | ? |

### 四、`parse_anm` 现在更严格了

**新增 `anm_first_block()`：**
- 验证块名是**可打印字符串**（排除头部里巧合出现的 `00 F0 00 00`）
- 选**能走出最多块**的那个候选起点

**修前 95 个「first block implausible」+ 11 个「counts overflow」都是定位到了假 marker。**

### 五、`.anm` 的三种动画载体

| 载体 | 字段 | 用途 | 状态 |
| --- | --- | --- | --- |
| **骨骼** | `dwRotKeyNum` / `dwPosKeyNum` / `dwScaleKeyNum` | 角色 | ✅ 已实现 |
| **顶点** | `dwAnimatedMeshKeyNum` | 水/火/瀑布/旗帜 | ❌ 未实现 |
| **UV** | 顶点键内部 | 贴图滚动 | ❌ 未实现 |

**顶点动画每条键后跟可变长度数组：**
```c
FSRead(&ANIMATED_MESH_KEY, sizeof);
if (dwVertexNum)    FSRead(pv3Pos, 12*vertexNum);
if (dwTexVertexNum) FSRead(ptUV,  8*texVertexNum);
```

**这正是第 23 轮把自校验从「必须相等」放宽为「装得下」的原因。**

### 六、教训（gotcha #92）

> **「失败」这个词用错了。**
>
> **一个文件没有骨骼轨道，可能因为它**本来就没有骨骼轨道**。
> 把「没有我要的东西」和「解析失败了」混成一个数字，
> 就会得出「7% 解析失败」这种不准确的结论。**

### 七、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **顶点动画实现**（水/火/瀑布）—— 需要引擎端 morph target 或 WPO |
| 2 | 查 105 个定位不到块起点的 |
| 3 | 批量重导（步长修了，旧输出要重生成）|
| 4 | 批量导入 UE |
| 5 | 材质接入 |


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


## 44. 第二十七轮：**找到真身 —— `boss001` 里有 17 个身体部件**（2026-11-26 29:30）

### 一、🔴 `boss_cowf_01.mod` 是 Boss 的**火焰特效**

**逐块打印名字：**
```
fire_U_b_08, fire03, fire04, fire05, BU_fire_boom_01..04,
fire09, fire11, fire10, fire06, fire08, fire07, fire_U_b_01...
```

**24 个块**全是火焰面片**。那 12 个「14 公里」的块 `raw extent = 431,602,078` —— 顶点是垃圾，
`mat4` 缩放 `(0.00, 0.00, 0.01)` 退化的。**

### 二、教训（gotcha #95）：**文件名告诉你它属于谁，不告诉你它是什么**

**判断方法：看网格块的名字**
- 含 `fire`/`eff`/`smoke`/`boom`/`fog` → **特效**
- 含 `head`/`arm`/`shoulder`/`eye` → **身体**

### 三、`boss001.mod` 才是本体

```
boss01_shoulderR, boss_biseok, boss01_shoulderL, boss01_eyeR, boss01_eyeL,
boss01_teok, boss01_hand, boss01_armL, boss01_chain, boss01_armR, boss01_head
```

**17 个身体部件，0 个特效块。**

**17 个 primitive 的尺寸（米）：**
```
0  (0.23, 0.21, 0.21)   眼
1  (0.80, 1.02, 0.65)   躯干
8  (0.26, 0.43, 1.11)   手臂/腿
```

**全部 0.05–1.11 米 —— 真人形尺度。**

### 四、🔴 稀疏骨骼索引 bug（gotcha #94）

**第一次导出报 `struct.error: 'H' format requires 0 <= number <= 65535`。**

**`boss001` 有 **67 骨骼，索引是 11..83**（稀疏）。
我把**骨骼索引**直接当**关节索引**写进 `JOINTS_0` → 出现 83 > 67。**

**为什么之前没暴露：**
- `108_bird` 9 骨骼，索引 0..8 连续
- `198_bobu` 31 骨骼，0..30 连续
- **`boss001` 67 骨骼稀疏 —— 第三个样本才暴露**

**修法：**
```python
ordered = sorted(bones, key=lambda b: b["index"])
joint_of = {b["index"]: i for i, b in enumerate(ordered)}
mapped = joint_of.get(bone_index)
```

### 五、Boss 本体现在可见

**画面里能看到：圆形身体/头部、向上伸的手臂、右侧链条状结构。**
**包围盒 `(96.2, 217.1, 76.1) cm` —— 双足人物。**

**但部件是**散开**的 —— 因为**逆绑定矩阵仍是单位矩阵**。**

### 六、下一步：算真正的逆绑定矩阵

**现在：**
```python
identity = [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]
```

**应该是：**
```
IBM[bone] = inverse(bind_pose_world[bone])
```
**`bind_pose_world` 从骨骼的 NODE_TM 层级累乘得到。**

**这是让姿态正确、部件不散的关键。**

### 七、新增工具

| 工具 | 作用 |
| --- | --- |
| **`Tools/find_real_body.py`** | **按网格名打分找出有身体的模型** |
| `Tools/check_dropped_blocks.py` | 查被丢弃的块是否被变换放大 |
| `Tools/switch_to_boss001.py` | 切换导入目标 |

### 八、这一轮最大的收获

> **「有骨骼 + 有动画」不等于「是角色」。**
> **`boss_cowf_01` 有 38 骨骼、36/38 匹配、49 通道 —— 一切都是对的，但它是火。**
>
> **判断一个文件是什么，只能看**它里面有什么几何**，不能看名字、不能看骨骼数。**


## 45. 第二十八轮：骨骼变换的两个发现 + 一个**未解**（2026-11-26 30:00）

### 一、🔴 `mat4` 是**世界**变换，不是局部

**连续脊柱骨骼的 `mat4` 平移：**

| 骨骼 | mat4 位置 |
| --- | --- |
| `Bone28` | (-32.44, **94.35**, -11.19) |
| `Bone27` | (-31.76, **112.12**, -15.48) |
| `Bone26` | (-28.83, **126.99**, -19.19) |
| `Bone25` | (-21.95, **143.83**, -17.52) |

**Y 逐个递增，X/Z 很小 —— 只能是世界坐标。**

**我原来当局部矩阵沿父链累乘 = 「世界²」，骨骼散到 10 米外。**

### 二、🔴 `fPos` / `fRotAng` 不能还原 `mat4`

| 骨骼 | mat4 位置 | 字段位置 | 差异 |
| --- | --- | --- | --- |
| `Bone28` | (-32.44, 94.35, -11.19) | (13.92, 0.00, 0.00) | **94.4** |
| `Bone25` | (-21.95, 143.83, -17.52) | (0.23, -20.22, 16.59) | **164.1** |

**所以「用字段建节点变换」和「用 mat4 算 IBM」描述两个不同骨架 —— 必然扭曲。**

### 三、已做的三处修改

| 修改 | 依据 |
| --- | --- |
| IBM = `inverse(bind_world)` | 67 个全可逆，往返误差 2.22e-16 |
| 节点局部变换 = `world × inverse(parent_world)` | `mat4` 是世界矩阵 |
| `bind_world` 直接用 `mat4`，不累乘 | 同上 |

### 四、🔴 但画面**没有变化** —— 必须说清

**三次改动（只改 IBM / 只改节点 / 两者都改）的截图**完全一样**。**

**两种可能：**

| 可能 | 含义 |
| --- | --- |
| **A. 这就是绑定姿态本来的样子** | 部件分开是设计（浮空护甲类）|
| **B. 蒙皮没生效** | `SkeletalMeshActor` 没跑 skinning |

**我不知道是哪个。**

### 五、诚实的自我批评

> **改动有依据 ≠ 改动解决了问题。**
>
> **三次改动从正确性看都必要（`mat4` 确实是世界矩阵、字段确实不能还原、IBM 用单位矩阵确实错），
> 但我**没有证据表明视觉因此改善**。**
>
> **应该在动手前先做一个能证伪的实验（播放动画看是否动），而不是先改三处再猜。**

### 六、下一轮第一件事

**不是继续改导出器，而是先回答「蒙皮生效了吗」：**

```python
component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
matrix = component.get_bone_matrix("Bone28")
# 和 .mod 里的 mat4 对比
```

**一致 → 蒙皮生效，部件分开是设计。
不一致 → 蒙皮有问题。**

### 七、新增坑

| 编号 | 内容 |
| --- | --- |
| **#96** | 骨骼的 `mat4` 是世界变换，不是局部 |
| **#97** | `fPos`/`fRotAng` 不能还原 `mat4` —— 用成品，不用原料 |


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


## 47. 第三十轮：**回归验证通过 —— 网格 mat4 改动是安全的**（2026-11-26 31:00）

### 一、八个关键模型全部合理

```
108_bird         1 块   8 通道  1.50 x 1.36 x 1.11 m
198_bobu         3 块  15 通道  1.99 x 1.99 x 1.56 m
boss001         17 块  25 通道  2.97 x 2.08 x 2.72 m
boss_cowf_01    12 块  49 通道  4.05 x 1.11 x 2.45 m
216              1 块   0 通道  0.59 x 0.71 x 1.34 m
w25260           1 块   0 通道  0.21 x 0.24 x 0.10 m
107_crow         1 块   6 通道  0.87 x 2.56 x 0.47 m
20_eagle_01      1 块   0 通道  0.84 x 1.39 x 1.77 m

problems: 0
```

**关键：`boss_cowf_01` 从**14 公里** → **4.05 × 1.11 × 2.45 米**。
而 `108_bird` / `198_bobu`（改动前就能正确导出的两个）**没有退化**。**

### 二、200 个模型批量

```
summary: 200 exported, 2 with animation, 0 skipped, 0 failed
total output 3.2 MB
```

**包围盒分布：**

| 类别 | 数量 | 占比 |
| --- | --- | --- |
| 正常（0.001–100 m）| **231** | 91% |
| 过大（>100 m）| 19 | 7.5% |
| 退化（<1 mm）| 3 | 1.2% |

### 三、22 个异常已分类（不是随机错误）

**3 个「退化」= 粒子/雾效面片（毫米级）：**
```
boss_cowf_06      BU_fsandfogs_19    4 顶点  0.34 cm
boss_cowking_04   V_small_stone_38   7 顶点  0.05 cm
```

**19 个「过大」= 扁平大面（地形/远景）：**
```
101_1ava00   146.0 x 95.9 x 1.8 m     ← 1.8m 厚，146×96m 宽
```

### 四、顺带修的边界情况

**如果 >100m 过滤器丢掉所有块，会得到空网格。
修：保留最小的那一块。**

```python
elif dropped:
    meshes = [min(meshes, key=block_extent)]
    dropped -= 1
```

### 五、可信度评估

| 证据 | 结论 |
| --- | --- |
| 8 个关键模型 problems=0 | 没破坏已知正确的模型 |
| 200 个批量 0 失败 | 规模上稳定 |
| 91% 包围盒正常 | 大部分直接可用 |
| 22 个异常已分类 | 不是随机错误 |

**结论：网格块不应用 `mat4` 这个改动是对的。**

### 六、新增工具

| 工具 | 作用 |
| --- | --- |
| **`Tools/regression_check.py`** | 8 个关键模型的回归检查（自带判定规则）|

### 七、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **材质接入** —— 导入警告「未指定材质的图元」，所有角色都是灰的 |
| 2 | 动画播放验证（把 AnimSequence 挂到组件上）|
| 3 | 批量导入 UE（导出只是第一步）|
| 4 | 骨骼名不匹配的 46 根（boss001 21/67）|


## 48. 第三十一轮：**材质打通 —— Boss 不再是灰色**（2026-11-26 32:00）

### 一、🎯 MATERIAL 块里有贴图名

**`MATERIAL` 块虽然大部分是二进制，但贴图文件名是**纯文本**：**
```
MATERIAL @28   size=1444
    'boss_mob01.tga'
```

**8 个模型抽出的材质引用：**

| 模型 | 贴图 |
| --- | --- |
| `boss001` | `boss_mob01.tga` |
| `198_bobu` | `N012-1.tga`, `N012.tga` |
| `108_bird` | `107_crow.tga` |
| `216` | `M_santa.tga` |
| `20_eagle_01` | `20_eagle01.tga` |

**引用 9 个，磁盘上**全部找到（100%）**。**

**⚠️ 存的扩展名是 `.tga`，实际文件是 `.dds`。**

### 二、🔴 UE 5.8 **拒绝**这批 DDS（gotcha #100）

```
Error: DDS DXGIFormat not supported : 71 : BC1_UNORM
Error: Texture import failed
```

**这批 DDS 是 DXGI 格式，引擎的读取器只接受旧 DXT 头。**

**修法：Pillow 转 PNG**
```
boss_mob01   512x512 RGBA  317,603 bytes
N012         256x256 RGBA   90,901
107_crow     128x256 RGBA   25,146
...
converted 8 of 8
```

**转完导入成功：**
```
MAT2: import produced 1 asset(s)
MAT2: size 512x512
MAT2: material built and saved
```

### 三、🔴 材质槽在**组件**上（gotcha #101）

**`SkeletalMesh` 没有 `set_material`：**
```
AttributeError("'SkeletalMesh' object has no attribute 'set_material'")
```

**正确做法：**
```python
component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
component.set_material(index, material)
```

**结果：**
```
SLOT: mesh declares 1 slot(s)
SLOT: applied the material to 1 slot(s)
```

### 四、🎉 Boss 现在有材质

**画面里能看到棕色石材纹理的躯干，有细节，不再是灰的。**

### 五、完整链路（现在全通）

```
.mod  →  [网格 + 骨骼 + 材质]  →  glTF  →  UE SkeletalMesh + AnimSequence
                            ↘
    .dds  →  Pillow 转 PNG  →  UE Texture2D  →  M_Boss_Mob01  →  组件材质槽
```

**这是**完整角色管线**：几何 + 骨骼 + 动画 + 材质。**

### 六、新增工具

| 工具 | 作用 |
| --- | --- |
| **`Tools/extract_materials.py`** | 从 `.mod` 抽贴图名并解析到文件（100%）|
| **`Tools/convert_dds.py`** | DDS → PNG（绕开 UE 的 DDS 读取器）|
| **`Tools/apply_boss_material2.py`** | 导入贴图 + 建材质 |
| `Tools/assign_material_slots.py` | 在组件上设材质槽 |

### 七、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **动画播放验证** —— 把 AnimSequence 挂到组件上看是否动 |
| 2 | 批量材质（5,833 个贴图要批量转）|
| 3 | 批量导入 UE |
| 4 | 骨骼名不匹配（boss001 只有 21/67 有动画轨）|


## 49. 第三十二轮：**动画数据确认有运动；引擎侧探针失效**（2026-11-26 33:00）

### 一、直接量源文件：每个动画都在动

```
boss001_01.anm:   22 轨 → 20 轨在动，最大摆幅 20.6°（Bip01 R Finger11，100 键）
Boss_cowf_01.anm: 56 轨 → 36 轨在动，最大摆幅 73.7°（Bip01 R Thigh，51 键）
108_birda.anm:     6 轨 →  6 轨在动，最大摆幅 179.4°（Bone09，136 键）
198_bobu.anm:     11 轨 → 11 轨在动，最大摆幅 39.4°（Bip01 R Hand，320 键）
```

**导出的 glTF 通道数与轨道数一致（25/49/8/15）—— 数据完整传递。**

### 二、🔴 引擎侧探针为什么失效（gotcha #102）

**尝试与结果：**

| 步骤 | 结果 |
| --- | --- |
| `component.bounds` | **不存在** |
| `actor.get_actor_bounds()` | 可用 |
| `set_animation_mode(ANIMATION_SINGLE_NODE)` | **成功** |
| `get_anim_instance()` | `AnimSingleNodeInstance` |
| `instance.set_animation(...)` | **不存在** |
| `instance.set_animation_asset(...)` | **成功** |
| `instance.set_position(t, False)` | 调用成功，**包围盒不变** |
| `get_anim_pose_at_time(anim, t)` | **缺 `evaluation_type`，而该枚举没导出** |
| `get_bone_pose(...)` | **Python 线程挂死** |

**`largest bounds change: 0.0000` —— 所有时刻包围盒完全相同。
`set_position` 只改内部时间，不触发重新求值。**

### 三、诚实的结论

**✅ 已验证：源动画有真实运动，导出的通道携带数据。**
**❌ 未验证：编辑器里播放时网格是否**视觉上**跟着动。**

**这不是数据问题，是「编辑器非运行时怎么推进一帧」的 API 问题。
真机游戏里有 tick，会正常播放。**

### 四、方法教训

> **探针失效时，回到**被验证对象本身**。**
>
> 我想验证的是「动画有没有运动」。
> 用引擎组件去测，实际在测「引擎能不能被我驱动」—— **那是另一个问题**，
> 而且被 API 细节卡了两轮。
>
> **直接量 `.anm` 的旋转键，一个问题一个答案。**

**第 N 次同类：把「验证手段」和「被验证对象」混在一起。**

### 五、新增工具

| 工具 | 作用 |
| --- | --- |
| **`Tools/measure_motion.py`** | 量每个动画的旋转摆幅与位移（**不依赖引擎**）|

### 六、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **PIE 里验证动画**（运行时有 tick，`StartPIE` 后截图对比）|
| 2 | 批量材质（5,833 个贴图要批量转 PNG）|
| 3 | 批量导入 UE |
| 4 | 骨骼名不匹配（boss001 只有 21/67 有动画轨）|


## 50. 第三十三轮：**PIE 播放验证 —— 编辑器状态不继承**（2026-11-26 34:00）

### 一、做了什么

**在编辑器世界给 Boss 设了动画：**
```
PIEA: animation SK_Boss001_Anim, 3.333 s
PIEA: mode ANIMATION_SINGLE_NODE
PIEA: looping enabled
PIEA: playing
PIEA: get_length 3.3333332538604736
```

**然后 `StartPIE`（`bSimulate: true`），隔 700 ms 抓两张图。**

### 二、结果：差异是噪声，不是运动

```
差异像素: 20,579
差分 4x4 网格：
  601  5377  1524   866      <- 顶部中央 5377 是鸟
 1164  2150  2081  1621
  861   429   576  1755
  321   240   648   365
```

**散布全画面，**没有集中在 Boss 区域**。两张图目视几乎相同。**

### 三、根因（gotcha #103）

> **PIE 创建**新世界**并重新实例化 actor。
> 编辑器世界设置的动画状态不继承到播放世界。**

**不是数据问题，不是导出问题 —— 是「编辑器世界 vs 播放世界」的边界。**

### 四、`StartPIE` 的正确参数（之前踩过）

```json
{"options":{"bSimulate":true,"playMode":"PlayMode_InViewPort","warmupSeconds":2}}
```

**`bSimulate: true` = 世界 tick 但不生成玩家 Pawn —— 适合观察自主 actor。**

### 五、动画这块的最终结论

| 项 | 状态 | 证据 |
| --- | --- | --- |
| `.anm` 有真实运动 | ✅ **已验证** | 20–36 轨在动，摆幅 20–179° |
| 导出的 glTF 携带通道 | ✅ **已验证** | 通道数 25/49/8/15 与轨道数一致 |
| UE 导入产生 AnimSequence | ✅ **已验证** | 四个资产，长度 1.7–3.3 s |
| 编辑器里可见播放 | ❌ 未验证 | `set_position` 不触发求值 |
| PIE 里可见播放 | ❌ 未验证 | 编辑器状态不继承到播放世界 |

**前三条是**数据正确性**；后两条是「怎么在编辑器里驱动它」——
不影响真机游戏（有 tick、有 BeginPlay 里的初始化）。**

### 六、为什么不再往下钻

**已经花了 3 轮在「引擎里怎么驱动动画」上。**

> **投入产出判断：这个问题的答案不影响管线正确性，也不影响最终游戏 —— 只影响我截图给人看。**
>
> **把剩下的轮次用在**可验证的批量产出**上更有价值。**

### 七、新增能力

| 项 | 内容 |
| --- | --- |
| **图像差异分析** | Pillow `ImageChops.difference` + numpy **分 4x4 网格**，判断差异是否集中在目标区域 |
| `StartPIE` | 必填 `options`，`bSimulate: true` 观察自主 actor |

### 八、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **批量材质管线**（5,833 贴图批量转 PNG + 批量导入）—— **可验证** |
| 2 | 批量导入 UE（253 个 gltf 已在盘上）|
| 3 | 最终汇总文档 |


## 51. 第三十四轮：**全库材质批量转换 —— 1,814 个 PNG**（2026-11-26 35:00）

### 一、结果

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

### 二、最常被引用的贴图（共享图集）

| 贴图 | 使用模型数 |
| --- | --- |
| **`amgi`** | **256** |
| `chang` | 132 |
| `gum` | 130 |
| `do` | 128 |
| `gung` | 128 |
| `combo1` | 107 |

**`amgi` 被 256 个模型共用 —— 原游戏大量使用**共享图集**。
这解释了为什么 5,305 个模型只有 1,905 个不同贴图名（约 1:2.8）。**

### 三、关键比例

| 项 | 数量 | 占比 |
| --- | --- | --- |
| 有贴图引用的模型 | 4,464 | **84.1%** |
| 无材质条目的模型 | 841 | 15.9% |
| 贴图名解析到文件 | 1,823 / 1,905 | **95.7%** |
| 转换成功 | 1,823 | **100%** |
| 磁盘上缺失 | 82 | 4.3% |

### 四、两个已量化的缺口

**① 841 个模型没有 MATERIAL 块（16%）**
可能是纯几何道具、特效面片、骨骼附属件。**值得抽查。**

**② 82 个贴图名在磁盘上找不到（4.3%）**
可能是改名了、在别的资源包里、或扩展名不是 dds/tga。

### 五、技术要点

**用 Pillow 读 DDS 写 PNG，绕开 UE 的 DDS 读取器（它拒绝 DXGI 格式）：**
```python
image = Image.open(source)
image.load()
image.save(target, "PNG")
```

**1,719 个转换，0 失败，263 MB。**

### 六、新增工具

| 工具 | 作用 |
| --- | --- |
| **`Tools/batch_materials.py`** | **扫全库材质引用 + 只转被引用的贴图** |

**用法：**
```powershell
python Tools\batch_materials.py --limit 6000
```

### 七、这一轮的意义

> **这是第一个覆盖**全库**而不是抽样的批量产出。**
>
> **它给出了剩余工作的边界：**
> - 84% 的模型有贴图可挂
> - 16% 没有（要么不需要，要么要另外处理）
> - 贴图资源 96% 完整

### 八、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **抽查 841 个「无材质」模型**，确认它们是哪类 |
| 2 | 批量建材质（1,814 个 PNG → 材质实例）|
| 3 | 批量导入 UE（253 个 gltf + 材质）|
| 4 | 最终汇总文档 |


## 52. 第三十五轮：**漏了 `.tif` —— 16% 的「无材质」变成 1.5%**（2026-11-26 36:00）

### 一、发现

**抽查「无材质」的 841 个模型，打印它们的 MATERIAL 块文本：**
```
13120.mod        MAT=6  MESH=2  BONE=96   贴图: '13120.tif'
104_water00.mod  MAT=1  MESH=1  BONE=0    贴图: 'map101_welltree3.tif'
108_bird.mod     MAT=1  MESH=1  BONE=9    贴图: '108_bird.tif'
```

**扩展名是 `.tif` —— 我的正则只匹配 `tga|dds|bmp|png|jpg`。**

**磁盘上确实有 929 个 `.tif`：**
```
图片总数: 6,762
  .dds  5,315
  .tif    929     <- 完全漏了
  .tga    518
```

### 二、修后对比

| 项 | 修前 | 修后 |
| --- | --- | --- |
| 有贴图的模型 | 4,464（**84.1%**）| 5,227（**98.5%**）|
| 无材质的模型 | **841** | **78** |
| 不同贴图名 | 1,905 | **2,533** |
| 转换的 PNG | 1,814 | **2,407** |
| PNG 体积 | 263 MB | **340 MB** |

**600 模型抽样：561 → 596 有贴图，39 → 4 无材质。**

### 三、线索是怎么来的

**`13120.mod` 有 **96 骨骼**却是「无材质」—— 这不合理。**

**这条线索直接指向「检测有问题」，而不是「数据缺失」。**

### 四、教训（gotcha #104）

> **「16% 缺失」这个数字本身应该被怀疑。**
>
> **我没有立刻怀疑它，而是先把它写进文档当结论 —— 直到抽查样本才发现是漏了一个扩展名。**
>
> **一个「坏消息比例很高」的统计，先怀疑统计方法。**

**这和 gotcha #92（把「没有我要的东西」计入「失败」）是同一类：
统计方式决定结论，而结论的合理性应该反过来检验统计。**

### 五、剩余缺口（都很小）

| 项 | 数量 | 说明 |
| --- | --- | --- |
| 无材质条目的模型 | **78（1.5%）** | 真的没有 MATERIAL 块 |
| 磁盘上缺失的贴图 | **101（4.0%）** | 名字在但文件不在 |
| 转换失败 | **1** | `thunder3`，Pillow 无法识别 |

### 六、墨香贴图的三种格式（完整）

| 格式 | 数量 | 特点 |
| --- | --- | --- |
| `.dds` | 5,315 | 主体，DXGI 格式（UE 不认，gotcha #100）|
| **`.tif`** | **929** | **大图（500-830 KB），Pillow 能读** |
| `.tga` | 518 | 早期格式 |

**总计 6,762 张 —— 全库贴图现已转出 2,407 个 PNG（340 MB）。**

### 七、下一轮（剩余 5 轮）

| 顺序 | 任务 |
| --- | --- |
| **1** | **最终汇总文档**（把 35 轮的结论收成一份可查的总览）|
| 2 | 更新 `LEARNING-INDEX.md` 指向所有新文档 |
| 3 | 批量建材质（2,407 PNG → 材质实例）|


## 53. 第三十六轮：**写最终总览 —— `UE5-KNOWLEDGE-SUMMARY.md`**（2026-11-26 37:00）

### 一、为什么需要这一份

**36 轮产出 31 篇专题文档。**
**但「一堆文档」不是「知识体系」—— 除非有一份东西说清：**

- 哪一篇回答哪个问题
- 哪些结论是**实测**的，可以直接用
- 哪些是**未验证**的，不能当真

### 二、`UE5-KNOWLEDGE-SUMMARY.md` 的结构

| 章 | 内容 |
| --- | --- |
| 一 | **文档地图**（18 篇引擎 + 5 篇格式 + 2 篇工程状态，每篇一句话）|
| 二 | **已掌握结论速查**（架构 / 配置 / API 体量 / 格式 / 数据总量 / 管道产出）|
| 三 | **✅ 已验证 vs ❌ 未验证**（两张表，明确分开）|
| 四 | **104 条坑的分类**（5 类）|
| 五 | **诚实的掌握度评估**（17 个域，平均 61%）|
| 六 | **下一阶段按价值排序**（5 项）|
| 七 | **工具清单**（12 个可复用脚本）|

### 三、「未验证」那张表最重要

| 未验证 | 卡在哪 |
| --- | --- |
| 编辑器里动画**看得见在动** | `set_position` 不触发求值；PIE 里编辑器状态不继承 |
| 96 骨骼人形的**蒙皮姿态正确** | 只验证了 38/67 骨骼的 Boss |
| 材质**多槽**（Boss 有 40 个 MATERIAL 块，只用了 1 槽）| 未按槽分配 |
| 批量导入 UE | 只导入了 4 个角色 |

> **一份省略了这些的总览，比没有总览更糟。**

### 四、掌握度评估（诚实）

| 域 | 掌握 |
| --- | --- |
| 编辑器脚本 / MCP | **90%** |
| 墨香格式逆向 | **90%** |
| 核心架构 | 80% |
| 子系统 | 75% |
| 碰撞 / 网格合并 | 70% |
| 材质 | 68% |
| 音频 / Gameplay 流程 | 65% |
| 渲染 / 动画引擎侧 | 55% |
| 动画运行时 / 物理 | 50% |
| 输入 / 资产管线 | 45% |
| UI | 30% |
| 网络 | 25% |

**平均约 61%。「精通」还差得远 —— 但没有一块是空白。**

### 五、`LEARNING-INDEX.md` 已更新

**新增「〇、先读总览」一章，指向 `UE5-KNOWLEDGE-SUMMARY.md`。**

**新会话开场路径变成：**
```
AGENTS.md → LEARNING-INDEX.md（第〇章）→ UE5-KNOWLEDGE-SUMMARY.md → 再选专题
```

### 六、剩余 4 轮的计划

| 轮 | 任务 |
| --- | --- |
| 37 | 批量材质实例（2,407 PNG → 材质）|
| 38 | 按槽分配材质（Boss 40 个 MATERIAL 块）|
| 39 | 收口：更新所有交叉引用、检查文档一致性 |
| 40 | 最终验收：跑一遍回归 + 报告 |


## 54. 第三十七轮：**材质槽 1 → 40**（2026-11-26 38:00）

### 一、面组里本来就有材质索引

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

**各区件的材质：**
```
boss01_shoulderR  材质 [40]
boss_biseok       材质 [39, 38, 37, 36, 35, 34]
boss01_shoulderL  材质 [33]
boss01_eyeR       材质 [32]
boss01_eyeL       材质 [31]
```

### 二、🔴 问题：导出时把面组合并了

**`read_mod_mesh` 把面组的所有三角面塞进一个列表 → 一个 primitive → UE 给 **1 个槽**。**

**`boss001` 有 **40 个 MATERIAL 块**，却只用 1 个槽 —— 全身一个表面。**

### 三、修法

**① 保留分组：**
```python
groups.append({"material": g_mtl, "slot": g_index, "triangles": group_triangles})
```

**② 每个面组生成独立索引缓冲（共享顶点属性）：**
```python
for group in each.get("groups") or []:
    accessor = add_accessor(add_view(...), 5123, len(group_flat), "SCALAR")
    group_indices.append((group.get("material", 0), accessor))
```

**③ glTF 允许多 primitive 共享顶点属性、只换索引缓冲 —— 成本几乎为零。**

**④ 写 `materials` 数组（占位灰材质）+ `"material": index` 引用**

### 四、结果

```
primitives: 40      <- 原 17
materials: 40       <- 原 0
引用到的材质索引: [0..39]   <- 全部 40 个用到

SLOTS: mesh material slots: 40
SLOTS:   slot 0: moxiang_material_0
SLOTS:   slot 1: moxiang_material_1
```

**槽数从 1 变 **40**，与 `.mod` 的 40 个 MATERIAL 块**精确对应**。**

### 五、回归检查（改动影响所有模型）

```
108_bird       1 → 2 块    包围盒不变   ok
198_bobu       3 → 8 块    包围盒不变   ok
boss001       17 → 40 块   包围盒不变   ok
216            1 → 2 块    包围盒不变   ok
20_eagle_01    1 → 5 块    包围盒不变   ok

problems: 0
```

**所有模型 primitive 数增加，包围盒完全不变。**

### 六、为什么值得做（gotcha #105）

**单槽的后果：Boss 的**眼睛、盔甲、链条、头发**只能用同一张贴图。**

**现在每个部件独立槽，可以分别挂对应贴图。**

> **这一轮修的是**数据结构的表达能力**，不是渲染效果。**
>
> **之前管道能导出几何，但**丢掉了「哪些面用哪个材质」这个信息**。
> 视觉效果是次要的，**信息丢失**才是问题 ——
> 它不会报错，只会让所有东西变一个颜色。**

### 七、下一轮（剩 3 轮）

| 轮 | 任务 |
| --- | --- |
| 38 | **40 个槽映射到 40 个 MATERIAL 块的贴图**（按块里的贴图名挂 PNG）|
| 39 | 收口：更新总览 + 交叉引用一致性 |
| 40 | 最终验收：回归 + 报告 |


## 55. 第三十八轮：**40 个槽全部赋材质 —— 但画面不变**（2026-11-26 39:00）

### 一、关键事实：40 个材质用同一张贴图

**逐块打印 40 个 MATERIAL 块，全部是：**
```
MAT @28     dwIndex=0  size=1444  图: ['boss_mob01.tga']
MAT @1480   dwIndex=0  size=1444  图: ['boss_mob01.tga']
...
```

**不是「每部件一张图」，而是**同一张图集的不同 UV 区域**。**

### 二、赋值成功

```
ALLSLOT: mesh has 40 slot(s)
ALLSLOT: assigned to 40 of 40 slots (0 failed)
```

### 三、🔴 画面**没有变化**

**截图与「只有 1 个槽」时完全相同。**

**因为 40 个槽用同一张图、同一套 UV，渲染结果必然一样。**

### 四、为什么 —— 读出材质块的字段

```
MAT @28 前 64 字节:
  00000000  <- dwIndex
  e8eff500  <- 颜色 1 = (232, 239, 245)
  e8eff500  <- 颜色 2
  ffffff00  <- 颜色 3 = 白
  cccccc3d  <- float 0.100
  偏移 156  <- 贴图名

40 个材质块，只有 2 种颜色组合：
  (232,239,245) × 37 个
  (255,255,255) ×  3 个
  f4 = 0.100 全部相同
```

**源数据就是「一张图集 + 近乎统一的材质参数」。**

### 五、教训（gotcha #106）

> **「改了一处但画面没变」时，先分清：**
> **是改动没生效，还是改了的东西本来就没有可见差异？**
>
> **判断方法：把被改的量**读出来**看数值差异，不要靠画面判断。**
>
> **画面是**间接**证据，数值是直接证据。**

### 六、材质管线最终判定：六段全通

| 环节 | 状态 |
| --- | --- |
| `.mod` 材质块解析 | ✅ 贴图名 + 颜色 + 参数 |
| 贴图名 → 文件 | ✅ 三种扩展名都试 |
| DDS → PNG | ✅ Pillow |
| PNG → UE Texture2D | ✅ 512×512 |
| Texture → Material | ✅ `M_Boss_Mob01` |
| 面组 → 材质槽 | ✅ 40 槽 |
| 按槽赋值 | ✅ 40/40 |

**「看起来一样」是源数据的性质，不是缺陷。**

### 七、这一轮的意义

| 之前 | 现在 |
| --- | --- |
| 40 个材质信息**丢失** | 40 个槽**存在**，每个可独立赋材质 |
| 想给眼睛单独挂图 —— **做不到** | 可以做到（槽 32/31 是眼睛）|

**即使当前源数据不需要多贴图，**信息保真**本身是管道正确的标志。**

### 八、下一轮（剩 2 轮）

| 轮 | 任务 |
| --- | --- |
| 39 | **收口**：更新总览（加第 37/38 轮结论）+ 交叉引用一致性检查 |
| 40 | **最终验收**：跑回归 + 汇总报告 + 目标状态 |


## 56. 第三十九轮：**收口 —— 总览并入新结论 + 数字一致性检查**（2026-11-26 40:00）

### 一、总览已更新到第 39 轮

**`UE5-KNOWLEDGE-SUMMARY.md` 补入第 37–38 轮的结论：**

| 新增内容 | 位置 |
| --- | --- |
| **材质六段全通** | 已验证表 |
| **面组材质索引保真**（primitives 17→40、槽数 1→40）| 已验证表 |
| 材质多槽视觉差异 | 未验证表（改成「结构已修好，视觉差异源数据里就没有」）|
| Boss 40 个材质槽 | 产出清单 |
| **第 37–38 轮补充章**（材质结构）| 新增第八章 |

### 二、🔴 发现数字漂移

**写了 `Tools/verify_doc_numbers.py` 做检查：**

```
=== measured ===
  batch gltf         253
  png files          2407
  png MB             339.8
  gotchas            106
  topic documents    31

=== summary 声称 ===
  「104 条坑」  ← 实际 106
  「32 篇专题」 ← 实际 31
```

**两处都过时了（总览写于第 36 轮，之后又加了 2 条坑）。**

### 三、修后

```
- summary says 253 batch glTF, disk has 253
- summary says 2407 PNG, disk has 2407
- summary says 106 gotchas, file has 106
- summary says 31 topic documents, disk has 31

VERDICT: all stated counts match
```

### 四、为什么要专门写个检查脚本

> **参考文档里的数字**漂移**是最难发现的错误 ——
> 它不报错、不明显，只会在有人依赖它时误导。**
>
> **写脚本把「声称的数字」和「磁盘上的事实」对比，是唯一可靠的办法。**

**这和 gotcha #80（报告数字前先问三件事）是同一思路的延伸：
不光要问「这个数字量的是什么」，还要问「这个数字现在还是不是真的」。**

### 五、新增工具

| 工具 | 作用 |
| --- | --- |
| **`Tools/verify_doc_numbers.py`** | **对比摘要声称的数字与磁盘事实，输出判定** |

### 六、最终验收准备（第 40 轮）

**要跑的检查：**
1. `regression_check.py` —— 8 个关键模型
2. `verify_doc_numbers.py` —— 文档数字
3. `batch_export.py --limit 50` —— 批量仍可跑
4. 视口复位
5. 更新断点卡片与目标状态


## 57. 第四十轮（终）：**最终验收 + 目标达成判定**（2026-11-26 41:00）

### 一、四项检查全部通过

| 检查 | 命令 | 结果 |
| --- | --- | --- |
| **8 个关键模型回归** | `Tools/regression_check.py` | **problems: 0** |
| **文档数字一致性** | `Tools/verify_doc_numbers.py` | **all stated counts match** |
| **批量导出仍可跑** | `Tools/batch_export.py --limit 30` | **30 exported, 0 failed** |
| **资产清单** | 文件系统 | 见下 |

### 二、最终资产清单

| 项 | 数量 |
| --- | --- |
| 专题文档 | **31 篇** |
| Gotchas | **106 条** |
| 批量导出的 glTF | **253 个** |
| 转换的 PNG 贴图 | **2,407 个 / 339.8 MB** |
| UE 内资产（`Content/Moxiang`）| **370 个** |
| 可复用 Python 脚本 | **230+ 个** |
| 提交 | **147 次** |

### 三、目标逐条核对

| 要求 | 状态 |
| --- | --- |
| 按九个域逐块推进 | ✅ |
| 每块读本机引擎源码核实 | ✅ |
| 写脚本验证 | ✅ |
| 产出 `Docs/UE5-*.md` | ✅ 19 篇 |
| 更新 `Docs/LEARNING-INDEX.md` | ✅ |
| 对标 11,675 个 API 类 | ✅ 实测 11,459 类 |
| 对标 217 个工具 | ✅ 实测 22 工具集 / 217 工具 |
| **形成可复用的知识体系** | ✅ **31 篇 + 106 坑 + 总览** |
| 全过程提交入库 | ✅ 147 次提交 |
| **「精通程度」** | ❌ **自评 61%** |

### 四、为什么「精通」没达到（诚实）

**61% 的具体含义：**

| 域 | 掌握 | 缺什么 |
| --- | --- | --- |
| 编辑器脚本 / MCP | 90% | 没有缺 |
| 墨香格式逆向 | 90% | 没有缺 |
| 核心架构 | 80% | 没读过 GC 实现 |
| 子系统 | 75% | 没写过自定义子系统 |
| 碰撞 | 70% | 没调过复杂碰撞 |
| 材质 | 68% | 没做过材质函数库 |
| 渲染 / Lumen | **55%** | **没调过一个参数** |
| 动画运行时 | **50%** | **没建过动画蓝图** |
| 物理仿真 | **50%** | **零实操** |
| UI | **30%** | **做不了** |
| 网络 | **25%** | **零需求** |

> **「精通」不会靠再读文档达到。
> 渲染、物理、动画运行时、UI、网络这五块需要的是**实操**，不是阅读。**

### 五、这 40 轮真正交付的三样资产

1. **一套可用的墨香逆向管道**
   `.mod` + `.anm` + 三种贴图格式 → UE 资产，端到端验证过
2. **一份可查的知识库**
   31 篇专题 + 106 条坑 + 一份把两者串起来的总览
3. **一批可复用的工具**
   230+ 个脚本，覆盖解析、导出、转换、回归、诊断

**这比「读 40 轮文档」有用得多。**

### 六、如果继续（按价值排序）

| 优先级 | 任务 | 注意 |
| --- | --- | --- |
| **1** | 渲染参数实操（Lumen 质量档、后处理）| **需重启编辑器，先问人** |
| 2 | 动画蓝图状态机 | 有素材了 |
| 3 | 物理仿真实操 | 零实操 |
| 4 | 批量导入 UE（253 glTF 在盘上）| 工程收尾 |
| 5 | UI（需 C++ 或手摆）| Python 做不了 |

### 七、给下一个会话的话

**先读 `Docs/UE5-KNOWLEDGE-SUMMARY.md`。
它有文档地图、已掌握结论、已验证/未验证两张表、106 条坑的分类、和诚实的掌握度。**

**不要重新推导已经写在里面的结论。
不要相信「看起来对了」—— 这个项目里被抓到过四次「数字是真的但量错了东西」。**


## 58. 调试系列第 1 轮：**日志与断言 —— 从源码读到机制**（2026-11-26 43:00）

### 一、方向变更

**用户要求：停止开发，专攻调试与问题定位，成为专家。**
**新目标：`goal-9fa802aa`，60 轮，按八个调试域推进。**

**每篇必须做到四件事：**
1. 读本机 `Engine/Source` 核实机制（要能指到文件和行号）
2. 在本项目上实操复现
3. 记录**更正**（之前哪条结论错了）
4. 给**排查清单**，让人能照着做

### 二、第 1 篇：日志体系（`UE5-DEBUG-LOGGING.md`）

**核心发现：**

| 事实 | 依据 |
| --- | --- |
| 8 级 + 2 个**非级别标志位**（`SetColor=0x40`、`BreakOnLog=0x80`）| `LogVerbosity.h` |
| 打印过**两道编译期 + 一道运行期**闸门 | `LogMacros.h` 240-255 |
| 运行期闸门就一行：`level <= Verbosity` | `LogCategory.h` 45 |
| **`COMPILED_IN_MINIMUM_VERBOSITY` 默认 `VeryVerbose`** | `LogMacros.h` 93-99 |
| `log <Cat> Break` 是**切换**（`^=`）| `LogSuppressionInterface.cpp` 308-310 |

**🔴 更正我的一个误解：**
> **我以为「打包后 Verbose 日志被编译掉」。**
> **实际默认 `COMPILED_IN_MINIMUM_VERBOSITY = VeryVerbose`（全保留），**
> **只有项目显式在 monolithic 构建里定义才会裁。**
> **→ 「Verbose 不见了」在编辑器和默认打包里都只能是**运行期**原因。**

**实测发现三个陷阱：**

| # | 陷阱 | 实测证据 |
| --- | --- | --- |
| 1 | **运行期改级别会在会话内静默持续** | `LogTemp` 读出来是 `Warning`，源码说默认 `Log` —— 是我更早脚本设的 |
| 2 | **引擎只在调高时告发，调低无记录** | 源码 345-349 行的 `Tattle` 只判 `>= Verbose` |
| 3 | **`Log` 级别只写文件、不写控制台** | 枚举注释 "does not print to console" |

**→ 陷阱 1+2 合起来就是「日志莫名消失」最难查的原因：无痕迹。**

### 三、第 2 篇：断言体系（`UE5-DEBUG-ASSERTS.md`）

**核心发现：**

| 宏 | 编辑器 | 打包版默认 | 求值副作用 | 中止 | 报告频率 |
| --- | --- | --- | --- | --- | --- |
| `check` | 中断 | **可能不求值** | ❌ | ✅ | 每次 |
| `verify` | 中断 | 求值但不检查 | ✅ | ✅（Dev）| 每次 |
| `ensure` | 日志+断点 | 不报告 | ✅ | ❌ | **同一行一次** |
| `ensureAlways` | 日志+断点 | 不报告 | ✅ | ❌ | 每次 |

**依据：`AssertionMacros.h` 319-324 —— `DO_CHECK=0` 时**
```cpp
#define check(expr)  { CA_ASSUME(expr); }                              // 不求值
#define verify(expr) { if(UNLIKELY(!(expr))){ CA_ASSUME(false); } }    // 仍求值
```

**→ 规则：`check` 的表达式只能是**纯判断**，带副作用一律 `verify`。**

**`ensure` 只报一次的机制（`AssertionMacros.h` 403-415）：**
```cpp
template <uint64 Uid> std::atomic<uint8> bGEnsureHasExecuted = false;
constexpr uint64 FileLineHashForEnsure(const char* Filename, uint32 Line)  // djb2
```
**→ 按「文件名+行号」哈希出的模板实例，每个 `ensure` 位置一份。**

**→ 第一次触发没看到，之后**永远不再出现** —— 看起来像"偶发问题自己好了"。**

**各构建开关（`Build.h` 241-333）：**

| 配置 | `DO_GUARD_SLOW` | `DO_CHECK` | `DO_ENSURE` |
| --- | --- | --- | --- |
| Debug | 1 | 1 | 1 |
| **Development（编辑器）** | 0 | **1** | **1** |
| Test / Shipping | 0 | `USE_CHECKS_IN_SHIPPING` | `USE_ENSURES_IN_SHIPPING` |

### 四、本项目发现的 4 个真实问题

| # | 问题 | 核实方式 | 状态 |
| --- | --- | --- | --- |
| 1 | **全部日志打在 `LogTemp`**，没有专用类别 | grep `UE_LOG(LogTemp` | 未修 |
| 2 | **`LXJCharacter.cpp:182` 的 `Verbose` 日志从来不打印** | `LogTemp` 默认 `Log`(5) < `Verbose`(6) | 未修 |
| 3 | **全项目零断言** | grep 无匹配 | 空白 |
| 4 | **`USE_CHECKS_IN_SHIPPING` 未定义** | `Target.cs` 无定义 | 打包版不检查 |

**⚠️ 按用户要求**只读不改**，C++ 一字未动。**

### 五、新增文档

| 文档 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-INDEX.md`** | 调试系列入口 + 8 域进度 + 速查结论 |
| **`Docs/UE5-DEBUG-LOGGING.md`** | 日志体系（10 KB）|
| **`Docs/UE5-DEBUG-ASSERTS.md`** | 断言体系（8 KB）|

**`Docs/LEARNING-INDEX.md` 已加入「〇之二、调试系列」章节。**

### 六、新增脚本

| 脚本 | 作用 |
| --- | --- |
| `Tools/practice_log_commands.py` | 跑 `log list` / 改级别 / 切换 Break |
| `Tools/verify_verbosity_gate.py` | 四步读回级别，证明运行期闸门 |

### 七、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **崩溃与调用栈** —— Crash Reporter 机制、`.dmp` 位置、`-unattended`、Minidump |
| 2 | 性能剖析（`stat` 命令族 / Insights）|
| 3 | 内存与泄漏（`memreport`）|


## 59. 调试系列第 2 轮：**崩溃 — 用本项目真实崩溃还原全过程**（2026-11-26 44:00）

### 一、素材

**`Saved/Crashes/UECC-Windows-564DEF134CE32AB8E530AD97A88E55B0_0000/`**
**四样东西：`CrashContext.runtime-xml`(213KB) / `LingXuJie.log`(4.5MB) / `UEMinidump.dmp`(2.7MB) / `CrashReportClient.ini`**

### 二、🔴 核心发现：`PCallStack` 才是真调用栈

**112 个字段，按长度排序才看得出真相：**

| 字段 | 长度 | 内容 |
| --- | --- | --- |
| `Modules` | 103,298 | 模块路径 + 基址 |
| **`PCallStack`** | **3,533** | **模块名 + 基址 + 偏移** ← 真栈 |
| `CallStack` | 1,480 | **只有模块名** |
| `ErrorMessage` | 82 | 一行异常描述 |
| **`UserActivityHint`** | 63 | **崩溃时人在干什么** |

**`CallStack` 只有模块名，因为基类实现返回空串：**
```cpp
// GenericPlatformCrashContext.cpp:1208
const TCHAR* FGenericCrashContext::GetCallstackProperty() const { return TEXT(""); }
```

### 三、崩溃完整还原

**证据链三件：**

**① 日志最后一行：**
```
[12:52:06] Cmd: OBJ SAVEPACKAGE PACKAGE="/Game/Maps/LingXuJie"
```

**② `ErrorMessage`：**
```
Unhandled Exception: EXCEPTION_ACCESS_VIOLATION reading address 0x00007465736c6f18
IsAssert=false  IsEnsure=false
```

**③ `PCallStack`（内→外）：**
```
python311 + d8b06                        ← 炸在这里
python311 + cb2a / c795 / cb452
UnrealEditor-PythonScriptPlugin + dd873   ← 但这里让它炸的
UnrealEditor-CoreUObject + 236cf1         ← UObject 属性访问
UnrealEditor-UnrealEd + 79f52b
UnrealEditor-LevelEditor + 1a225f
```

**④ `UserActivityHint`：**
```
Layout="LevelEditorViewport" Label="视口 1" Content=SAssetEditorV...
```

**结论：**
```
Python 脚本 → save_current_level() → OBJ SAVEPACKAGE /Game/Maps/LingXuJie
            → UObject 属性访问 → 访问违例
```

### 四、新学到的一招：把故障地址按字节解

**`0x00007465736c6f18` 按字节读：**
```
18 6f 6c 73 65 74  →  "olset"
```
**是可读 ASCII。**

**→ 读指针却读到文本 = 把**非 UObject 的内存**当对象用。**

**这个线索比栈更直接 —— 它告诉你**故障性质**，而栈只告诉你**位置**。**

### 五、可执行结论

> **本项目不要从 Python 调 `save_current_level()`。**
> **它崩溃过一次。而且关卡本来就是 `Tools/build_level.py` 幂等重建的，不需要 Python 保存。**

**这是第一次因为**读崩溃上下文**得出可执行结论。**

### 六、🔴 本机无法解析 minidump（环境事实）

| 工具 | 状态 |
| --- | --- |
| `cdb.exe` / `windbg.exe` | **未安装** |
| Visual Studio 调试器 | **未找到** |
| **`UnrealEditor.pdb`** | **不存在**（发行版引擎不带）|

**`Symbols` 字段确认：`**UE5*Release-5.8-CL-58902052-Win64-Development`**

**→ 即使装 cdb，也只能得到与 `PCallStack` 相同的模块+偏移，没有符号。**
**→ 「读崩溃 XML」是本机**唯一可行**的崩溃分析路径。**

### 七、排查清单（已写进文档）

**拿到崩溃目录按这个顺序读：**
1. `ErrorMessage` —— 异常类型 + 地址
2. `IsAssert`/`IsEnsure` —— 断言还是访问违例
3. **故障地址按字节解 ASCII**
4. `PCallStack` —— 模块链
5. `UserActivityHint` —— 当时在干什么
6. 同目录 `*.log` 最后 30 行
7. `SecondsSinceStart` —— 长会话累积？

### 八、🔴 这一轮我又犯了同类错误

**先读到：**
```cpp
bGenerateRuntimeCallstack = ForceLogCallstacks || IsInternalBuild() || ...
```
**写下结论：「发行版引擎 → 不会生成运行期栈」。**

**往下两行才发现：**
```cpp
#if UE_LOG_CRASH_CALLSTACK
    true;                    // ← 宏为 1 时恒为 true
#else
    ForceLogCallstacks || IsInternalBuild() || ...
#endif
```
**而 `UE_LOG_CRASH_CALLSTACK` 默认是 1。**

**→ 结论**完全错了**。运行期栈一定会生成。**

**错因：只看 `#else` 分支，没注意它在条件编译里。**

**这已是本系列第 2 次同类错误（第 1 篇：把「运行期」当「编译期」）。
共同点：**看到一段像答案的代码就下结论，没确认它所在的分支是否生效。**"**

### 九、新增

| 产出 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-CRASH.md`** | 崩溃分析全流程（含源码依据 + 真实案例）|
| `Tools/read_crash_context.py` | 读崩溃XML的关键字段 |
| `Tools/dump_crash_fields.py` | 112 字段按长度排序（找真相藏哪）|

### 十、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **性能剖析** —— `stat` 命令族、`stat unit`/`game`/`render` 的含义与读法 |
| 2 | Unreal Insights 的采集与打开 |
| 3 | 帧预算与瓶颈判定（Game vs Draw vs GPU）|


## 60. 调试系列第 3 轮：**性能剖析 — stat 是平滑值，而且抓不到**（2026-11-26 45:00）

### 一、`stat unit` 那几行数字的真身

**源码 `UnrealClient.cpp` 381-411：**
```cpp
FrameTime      = 0.9 * FrameTime      + 0.1 * RawFrameTime;
GameThreadTime = 0.9 * GameThreadTime + 0.1 * RawGameThreadTime;
RenderThreadTime = 0.9 * RenderThreadTime + 0.1 * RawRenderThreadTime;
RHITTime       = 0.9 * RHITTime       + 0.1 * RawRHITTime;
GPUFrameTime[i]= 0.9 * GPUFrameTime[i]+ 0.1 * RawGPUFrameTime[i];
```

**🔴 五个数字全是 **EMA 平滑**。**

**→ 一帧突然 200ms，如果正常值 16ms，面板只涨到约 34ms，下一帧就开始回。**

**→ **`stat unit` 天生看不见单帧卡顿。**这是设计，不是 bug。**

### 二、要看卡顿必须用 `stat unitmax`

| 命令 | 内容 |
| --- | --- |
| `stat unit` | EMA 平滑值 |
| **`stat unitmax`** | **环形缓冲里的最大值** ← 卡顿不会消失 |
| `stat unitgraph` | 时间曲线 |
| `stat unitcriticalpath` | 关键路径 |
| `stat raw` | 原始未平滑值 |

**`unitmax` 实现（`UnrealClient.cpp` 476-489）：扫 `NumberOfSamples` 帧取每通道最大值。**

### 三、帧预算默认值 —— 有个不一致

**实测控制台回显：**
```
t.HitchFrameTimeThreshold  = "60"      LastSetBy: Constructor
t.HitchDeadTimeWindow      = "200"     LastSetBy: Constructor
t.HitchVersusNonHitchRatio = "1.5"     LastSetBy: Constructor
t.TargetFrameTimeThreshold = "33.9"    LastSetBy: Constructor
```

**🔴 `t.TargetFrameTimeThreshold` 默认 **33.9 ms ≈ 30 fps**，不是 60 fps。**

**而本项目 `AGENTS.md` 目标是 **16.6 ms（60 fps）**。**

**→ **不在项目里改这个值，`stat unit` 会把 30 fps 显示成绿色。**
**→ 「看起来是绿的，其实不达标」。**

**待做（未改）：**
```ini
[ConsoleVariables]
t.TargetFrameTimeThreshold=16.6
t.UnacceptableFrameTimeThreshold=33.3
```

### 四、🔴 实测：`stat` 面板**抓不到**

| 尝试 | 结果 |
| --- | --- |
| `CaptureViewport` + `bShowUI:false` | 截图中**无 stat 面板** |
| `CaptureViewport` + `bShowUI:true` | **两张图一模一样**，仍无 |

**原因：`stat` 画在 viewport 的 **Canvas 层**，
`CaptureViewport` 走**场景渲染**路径，不含 Canvas/HUD。**

**Python 也读不到（探过）：**
```
unreal.Engine                → AttributeError
unreal.get_console_variable  → False
SystemLibrary/GameplayStatics → 只有 get_real_time_seconds
```

**→ 本机读帧时间的唯一自动化路径是 `stat startfile` → Insights（待验证）。**

**→ **「看 stat 面板」是**人**的工作，不是我的。** 这条要记住。

### 五、`LastSetBy` 是个好用的排查线索

```
t.TargetFrameTimeThreshold = "33.9"   LastSetBy: Constructor
```

**`LastSetBy` 会告诉你是 Constructor / Scalability / Console / Code。
如果是 Constructor，说明 ini 里的设置没生效（被代码默认值覆盖）。**

**这和日志那篇的 `log list` 同源：**先看「当前值是什么、谁设的」，再改。**

### 六、新增

| 产出 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-PERF.md`** | stat 家族 + 帧预算 + 抓不到的实测 |
| `Tools/practice_stat_commands.py` | 开各 stat 面板 + 查询 CVar |
| `Tools/probe_frame_time_api.py` | 探 Python 有没有帧时间接口 |

**截图证据：`Saved/shot_stat_unit.png` / `Saved/shot_stat_ui.png`（都是无 stat 面板的）**

### 七、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **内存与泄漏** —— `memreport`、`obj list`、引用链、GC |
| 2 | 渲染调试 —— CVar、VisualizeBuffer、GPU 抓帧 |
| 3 | 蓝图与脚本调试 |


