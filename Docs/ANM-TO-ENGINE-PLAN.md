# `.anm` → 引擎：选 glTF 而不是 FBX（2026-11-26 决定）

> **结论：走 glTF。**
> **理由不是"更现代"，是**结构正好对得上、且 Python 能直接写**。**

---

## 一、两条路的对比

| | **FBX** | **glTF** |
| --- | --- | --- |
| 格式 | 二进制或 ASCII（私有规范） | **JSON + 二进制 buffer（公开规范）** |
| Python 写 | ❌ 需 Autodesk FBX SDK | ✅ **`json` + `struct` 就够** |
| UE 导入 | `FbxImportUI`（`import_file` 硬编码） | **Interchange（`import_asset(factory=None)`）** |
| 动画支持 | ✅ | ✅ **确认有 `GLTFAnimation.h`** |
| 依赖 | 需装 SDK | **零依赖** |

**FBX 那条路的死结：Python 没有免费可靠的 FBX 写入库。**
`py-fbx` 是 Autodesk SDK 的绑定，需要装 SDK 且授权复杂。

**glTF 那条路：自己拼 JSON 即可，一晚上能写完。**

---

## 二、结构对得上（这是决定性理由）

### 2.1 我们手上有什么（研究区已解）

| 轨道 | `.anm` 记录 | 内容 |
| --- | --- | --- |
| 位移 | 20 字节 | `[索引][x,y,z][0]` cm |
| **旋转** | **24 字节** | **`[索引][四元数 x,y,z,w][填充0]`** |
| 缩放 | 36 字节 | `[索引][8 个浮点]`，前 3 个是 sx/sy/sz |
| UV | 56 字节 | 特效专用，动画不需要 |

### 2.2 glTF 的动画结构（引擎源码 `GLTFAnimation.h` 原文）

```cpp
struct FAnimation {
    enum class EPath { Translation, Rotation, Scale, Weights };
    enum class EInterpolation { Linear, Step, CubicSpline };

    struct FTarget { const FNode& Node; EPath Path; };
    struct FChannel { int32 Sampler; FTarget Target; };
    struct FSampler {
        EInterpolation Interpolation;
        const FAccessor& Input;   // 时间，秒，float
        const FAccessor& Output;  // 值
    };

    FString Name;
    TArray<FSampler> Samplers;
    TArray<FChannel> Channels;
};
```

**`EPath { Translation, Rotation, Scale }` —— 和我们的三条轨道**一一对应**。**

**这不是"能转换"，是"根本就是同一个数据模型换了个外壳"。**

---

## 三、转换映射（写代码时照这个表）

| `.anm` | glTF |
| --- | --- |
| 骨骼名表（N × 160 字节） | `nodes[]`（每个 node 一个名字）|
| 骨骼层级 | `nodes[].children` ← **⚠️ 见第四节** |
| 位移节（20 字节） | `animations[].channels[]`，`path: "translation"` |
| **旋转节（24 字节）** | `path: "rotation"`，**四元数直接可用** |
| 缩放节（36 字节） | `path: "scale"` |
| 帧索引（u32） | `samplers[].input`（**要乘 1/fps 变成秒**）|
| 记录值 | `samplers[].output` |

**`samplers[].interpolation` 用 `LINEAR`（墨香是逐帧数据，线性插值最接近）。**

---

## 四、必须先解决的三个问题

### 4.1 ⚠️ 帧率未知 —— 这是唯一的硬阻塞

**glTF 的 `input` 是**秒**（`"Always float and seconds"`，源码注释原文）。**

**我们知道每个骨骼有 N 条记录（= N 帧），但不知道**每秒多少帧**。**

**三条路搞清楚：**

| 方式 | 做法 |
| --- | --- |
| **① 看动作时长反推** | 同一个动作（如"走路循环"）在游戏里播多久，除以帧数 |
| ② 找游戏配置 | `.chr` / `.chx` / 某个表里可能有 fps 字段 |
| **③ 先假设 30 fps** | **最小验证时用 30，看动作快慢是否合理** |

**建议走 ③ 做最小验证，同时并行查 ①。**

### 4.2 骨骼层级从哪来

**`.anm` 里只有骨骼名，**没有父子关系**。**

**两个可能来源：**

| 来源 | 可行性 |
| --- | --- |
| **`.mod` 的 `dwParentObjectIndex`** | ✅ **已知有**（研究区验证过：192 骨骼，190 有合法父索引）|
| `.anm` 文件内部 | ❌ 未发现 |

**所以层级从 `.mod` 取，按骨骼名与 `.anm` 对齐。**

**⚠️ 但要先验证：`.anm` 的 `Bip01 R Thigh` 和 `.mod` 的骨骼名是不是同一套。**
**研究区可以用 `get_bone_names` 或直接比对 CSV。**

### 4.3 旋转坐标系

**墨香和 UE 坐标系不同（Y/Z 轴不同）。**
**四元数要换手性，不是简单取反。**

**最小验证时先用单位变换，看动作对不对，再调。**

---

## 五、最小验证步骤（下一步就做这个）

```
① 挑一个最短的 .anm（帧数最少，比如 30 帧以内）
② 解析出 1 根骨骼的位移 + 旋转 + 缩放
③ 手写一个最小 glTF（JSON，一个 node、一条通道）
④ import_asset("/Game/Moxiang/Anim", "test", "test.gltf", factory=None)
⑤ 在编辑器里看：动画时长对不对、有没有动
```

**过了再放大到全部 4,056 个。**

---

## 六、UE 侧的导入调用（已确认存在）

```python
# 通用导入，走 Interchange（支持 glTF）
from editor_toolset.toolsets.asset import import_asset

import_asset(
    folder_path="/Game/Moxiang/Anim",
    asset_name="bobu",
    source_file=r"C:\...\bobu.gltf",
    factory=None,        # ← 关键：None 走 Interchange
    options=None)
```

**源码注释原文：**
> `factory`: ... Leave None to let the engine pick (which preserves the Interchange path).

**如果是 FBX，才需要 `SkeletalMeshTools.import_file(import_animations=True)`。**

---

## 七、已查清的：**不能只转动画，必须网格 + 骨架 + 动画一起转**

**这条原本是"最大未知"，现在已经查清，而且是**坏消息**。**

**证据：`InterchangeGltfAnimation.cpp` 第 729 行**
```cpp
UInterchangeSkeletalAnimationTrackNode* AcquireTrackNode(
    const FString& SkeletonNodeUid, FAnimationTimes& AnimTimes)
```

**动画轨道要绑在 `SkeletonNodeUid` 上。这个 uid 来自**带蒙皮的网格节点**，
不是凭空建得出来的。**

**所以"只给一个带动画的 glTF"大概不会产生 `AnimSequence`。**

### 修正后的方案

```
① .mod（网格 + 骨骼层级）→ glTF（含 skin + joints）
② .anm（三条轨道）→ 写进同一个 glTF 的 animations[]
③ import_asset(factory=None) → SkeletalMesh + Skeleton + AnimSequence
```

**工作量比原以为的大，但都是机械活：**
- `.mod` 的几何我们已经能导出（`build_map_obj.py` 已有 OBJ 路径）
- 骨骼层级在 `.mod` 的 `dwParentObjectIndex`
- 蒙皮权重在 `.mod` 里（未验证，**这是新的未知**）

### 新的未知（比原来少，但更具体）

| 项 | 状态 |
| --- | --- |
| **`.mod` 的蒙皮权重在不在** | ❓ **最关键**。没有权重就建不出 `skin`，UE 不会认为那是骨骼网格 |
| 骨骼层级 | ✅ `.mod` 的 `dwParentObjectIndex` 有 |
| 三条轨道 | ✅ 已解 |
| 帧率 | ❓ 仍未知 |

**所以下一步该去研究区查：`.mod` 有没有蒙皮权重数据。**

---

## 八、最小验证步骤（修正版）

**不能只做动画。最小验证要包含一个网格：**

```
① 挑一个最简单的 .mod（骨骼数最少，比如 3–5 根）
② 转成 glTF：nodes(骨骼) + skin(关节索引 + 逆绑定矩阵) + 网格顶点
③ 加一条动画：1 根骨骼的 3 个关键帧
④ import_asset("/Game/Moxiang/Anim", "test", "test.gltf", factory=None)
⑤ 看：SkeletalMesh 出来了吗？AnimSequence 出来了吗？动画播得动吗？
```

**①②是关键，③可以后补。**

---

## 九、来源

| 内容 | 出处 |
| --- | --- |
| glTF 动画结构 | `Engine\Plugins\Interchange\Runtime\Source\Parsers\GLTFCore\Public\GLTFAnimation.h` |
| glTF 解析器存在 | `GLTFCore` 目录，`GLTFReader.cpp` 有 19 处 Animation 引用 |
| `import_asset` 走 Interchange | `editor_toolset\toolsets\asset.py` 注释 |
| `.anm` 三条轨道 | 研究区 `anm-rotation-solved.md` |
| `.mod` 骨骼层级 | 研究区 `mod-format.md` |
