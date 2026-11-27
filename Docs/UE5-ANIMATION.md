# 动画系统：把墨香 4,056 个 `.anm` 弄进 UE（2026-11-26 研究）

> **目的：搞清楚 UE5 动画系统的实际可达路径，为 `.anm` 导入器定方向。**
> 每条结论都注明是**引擎源码核实**还是**官方 API 文档**。

---

## 一、结论先行

**Python 无法直接写动画骨骼轨道。**

| 能力 | Python 可达？ | 依据 |
| --- | --- | --- |
| **读**原始轨道数据 | ✅ 可以 | `AnimationBlueprintLibrary.GetRawTrackPositionData` 等，69 个 BlueprintCallable |
| **写**原始轨道数据 | ❌ **不能** | `IAnimationDataController` 在 `Developer/AnimationDataController`，**该模块 BlueprintCallable UFUNCTION 数量 = 0** |

**所以导入器只有两条路：**

| 路线 | 做法 | 需要 C++？ |
| --- | --- | --- |
| **A（推荐）** | `.anm` → **FBX** → `AssetImportTask` 导入 | ❌ **不需要** |
| B | 用 C++ 实现 `IAnimationDataController` 写入 | ✅ 需要，且要改工程源码 |

**选 A。** 理由：`FbxImportUI` / `FbxSkeletalMeshImportData` 都是 Python 可达的
（`FbxImportUI` 的 API 页有 9,405 字符），而 C++ 路线要动引擎接口、还要重编译。

---

## 二、关键类与它们的可达性（引擎源码核实）

### 2.1 读：`AnimationBlueprintLibrary`

**头文件：** `Engine\Source\Editor\AnimationBlueprintLibrary\Public\AnimationBlueprintLibrary.h`（48,818 字节）
**BlueprintCallable 函数：69 个**（源码里 BlueprintCallable 出现 69 次）

**跟本项目直接相关的：**

| 函数 | 用途 |
| --- | --- |
| `GetAnimationTrackNames` | 列出所有骨骼轨道名 |
| `GetRawTrackPositionData` | **读位移轨道** |
| `GetRawTrackRotationData` | **读旋转轨道** |
| `GetRawTrackScaleData` | **读缩放轨道** |
| `GetRawTrackData` | 一次读三种 |
| `ExtractRootTrackTransform` | 取指定时刻的根骨骼变换 |
| `AddAnimationSyncMarker` | ✅ **写**同步标记 |
| `AddAnimationNotifyEvent` | ✅ **写**通知事件 |
| `SetAnimationInterpolationType` | ✅ 写插值类型 |
| `SetRootMotionEnabled` | ✅ 写根运动开关 |
| `SetBoneCompressionSettings` | ✅ 写压缩设置 |

**注意这个不对称：`AddAnimationSyncMarker` 能写，`GetRawTrack*` 却只有读版本。**
**这不是文档漏写 —— 头文件里就没有对应的 `SetRawTrack*`。**

### 2.2 写：`IAnimationDataController`（C++ 专属）

**头文件：** `Engine\Source\Runtime\Engine\Classes\Animation\AnimData\IAnimationDataController.h`
**实现：** `Engine\Source\Developer\AnimationDataController\Private\AnimDataController.cpp`（78,424 字节）

**它有的方法：**
```
AddBoneTrack
AddBoneCurve
SetBoneTrackKeys
OpenBracket / CloseBracket
SetPlayLength
SetNumberOfFrames
SetFrameRate
SetModel
```

**🔴 但注意两点：**
1. **`Developer` 模块** —— 这是编辑器/开发期模块，不是运行时代码
2. **`AnimDataController.cpp` 的 BlueprintCallable UFUNCTION 数量 = 0**
   → **Python 拿不到这些方法**

**`OpenBracket` / `CloseBracket` 是事务式修改的边界**（成批改动画数据要包在里面），
这是 C++ 里改动画的标准做法。

### 2.3 `UAnimSequence` 本身

**头文件：** `Engine\Source\Runtime\Engine\Classes\Animation\AnimSequence.h`（41,027 字节）
**BlueprintCallable 只有 4 个**，全是重定向源的（`SetRetargetSourceAsset` 等）。

**→ `AnimSequence` 上没有任何 Python 可达的"写入轨道"入口。**

---

## 三、推荐路线：`.anm` → FBX → 导入

### 3.1 为什么 FBX

| 理由 | 说明 |
| --- | --- |
| **Python 完全可达** | `AssetImportTask` + `FbxImportUI` 是标准导入流程 |
| **UE 官方支持** | FBX 是 UE 的一等公民格式 |
| **能同时带骨架 + 动画** | 一次导入骨骼和动画，不用分开处理 |
| **不需要改引擎** | 纯项目层 Python 就能做 |

### 3.2 我们手上有什么

| 项 | 数量 | 位置（研究区） |
| --- | --- | --- |
| 动画文件 | **4,056** | `animations/` |
| 已解码的明文 | 2,485 | `anm_plain/` |
| 骨骼 | 157,997 根 | `mod_skeletons/` |
| 骨架 | 2,094 套 | 同上 |
| 模型 | 5,305 | `resources/mod/` |
| 动画集容器 | 1,211 | `resources/chx/` |

### 3.3 需要写的东西

```
① 墨香 .anm 解析器 → 骨骼轨道（时间轴 + 每根骨骼的位移/旋转/缩放关键帧）
② 轨道 → FBX 序列化     ← 这一步是主要工作量
③ FBX → UE 导入（Python 调 AssetImportTask）
④ 校验（帧数、时长、骨骼名是否匹配）
```

**②是关键：FBX 的动画部分是 ASCII 或二进制格式，UE 能读的动画 FBX 需要：**
- Skeleton 节点层级（与骨骼名对应）
- AnimationStack / AnimationLayer / AnimationCurveNode
- 每帧的 `T`（位移）/ `R`（旋转）/ `S`（缩放）关键帧

---

## 四、还没搞清的（下一轮要查）

| 问题 | 为什么重要 |
| --- | --- |
| **墨香 `.anm` 的帧率是多少？** | 决定 FBX 里时间轴怎么填 |
| **旋转是四元数还是欧拉角？** | 决定 FBX 里怎么序列化 |
| **骨骼名是否与 `.mod` 的骨骼名一致？** | 不一致的话 FBX 导入会丢轨道 |
| **`.chx` 动画集怎么关联多个 `.anm`？** | 一套动作可能拆成多个文件 |
| **UE 的 FBX 动画导入需要哪些必需节点？** | 缺一个就静默失败 |

**这些在研究区可以查（`.anm` 格式已解），不需要在工程区重做逆向。**

---

## 五、给下一轮的最小验证步骤

**不要一上来写完整导入器。先做单根骨骼的单段动画：**

```
1. 从研究区挑一个最短的 .anm（帧数最少）
2. 解析出 1 根骨骼的 3 个关键帧
3. 手写一个最小 FBX（ASCII 格式，几十行）
4. 用 Python AssetImportTask 导入
5. 在编辑器里确认：动画时长对、骨骼名认得出、播放有动作
```

**这一步过了，再放大到全部 4,056 个。**

---

## 六、记录在案的坑（本次调研踩到的）

| 坑 | 说明 |
| --- | --- |
| **API 页可能是空的** | `AnimSequenceImportData` / `FbxAnimImportData` / `AnimationEditorSubsystem` 抓回来只有 144 字符（重定向页）。**看到 144 字符就当没有这个页，去查引擎源码。** |
| **`IAnimationDataController` 名字像接口、实际在 Developer 模块** | 名字带 `I` 前缀容易误以为是运行时接口 |
| **读函数有、写函数没有** | 头文件里搜 `GetRawTrack` 能搜到，搜 `SetRawTrack` 是零 —— **不要假设"既然能读就能写"** |

---

## 七、来源

| 内容 | 出处 |
| --- | --- |
| 读轨道 API 与数量 | `Engine\Source\Editor\AnimationBlueprintLibrary\Public\AnimationBlueprintLibrary.h` |
| 写入接口位置 | `Engine\Source\Runtime\Engine\Classes\Animation\AnimData\IAnimationDataController.h` |
| 写入实现与模块 | `Engine\Source\Developer\AnimationDataController\Private\AnimDataController.cpp` |
| `AnimSequence` 可达面 | `Engine\Source\Runtime\Engine\Classes\Animation\AnimSequence.h` |
| Python 签名 | `Docs/PythonAPI/` 下对应 `.txt`（UE 5.8 官方页） |
| 每次调查的脚本 | `Tools/read_animation_source.py`、`Tools/find_animation_write_path.py` |
