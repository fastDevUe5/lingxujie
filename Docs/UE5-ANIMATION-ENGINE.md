# UE5 动画引擎侧：数据结构与写入配方（引擎源码核实）

> **本文补上 `UE5-ANIMATION.md` 缺的那一半 —— 引擎**内部**怎么存和播动画。**
> **核心结论：`AnimSequence` 不再直接存轨道，它持有一个 `DataModel`，
> 而 `DataModel` 通过 `IAnimationDataController` 写入。**

---

## 一、四层的结构（源码实测）

```
UAnimSequenceBase        14,508 字节
  ├ DataModel            ← 动画数据（现代存储）
  ├ Notifies             ← 通知事件
  ├ Curves               ← 曲线
  ├ RateScale            ← 播放速率
  └ PlayLength           ← 时长

UAnimSequence            41,027 字节
  ├ DataModel
  ├ Curves
  ├ **Skeleton**         ← 引用骨架（关键）
  └ Montage

UAnimInstance            98,676 字节   ← 最大，但抽象
UAnimMontage             39,517 字节
UBlendSpace              39,704 字节
UAnimBlueprintGeneratedClass  25,185 字节
  ├ GetBakedStateMachines    ← 烘焙好的状态机
  ├ GetSyncGroupNames
  └ GetTargetSkeleton
```

**`UAnimInstance` 头文件最大（98,676 字节）但代码体最小 —— 因为它主要是纯虚接口，
实际实现在动画蓝图生成的类里。**

---

## 二、`UAnimationDataModel` —— 42 个**读**方法

### 2.1 时长与帧率（关键）

```
GetPlayLength           ← 时长（秒）
GetNumberOfFrames       ← 帧数
GetNumberOfKeys
**GetFrameRate**        ← 帧率
IsEditorOnly
```

**🔴 帧率的取得方式（修正）**

**`GetFrameRate` 在 C++ 的 `UAnimationDataModel` 上，**但 Python 侧没有这个方法**。
不过 Python 侧有等价的组合：**

```
AnimationBlueprintLibrary.GetSequenceLength   ← 时长（秒）
AnimationBlueprintLibrary.GetNumFrames        ← 帧数
AnimationBlueprintLibrary.GetTimeAtFrame / GetFrameAtTime
```

**所以：`帧率 = GetNumFrames / GetSequenceLength`。**

**实测：`AnimationBlueprintLibrary.h` 里 `GetFrameRate` 出现 0 次，
但 `GetSequenceLength` / `GetNumFrames` 都在。**

**这意味着两件事：**
1. **将来导入之后可以**验证**帧率对不对**
2. **如果有任何现成的 UE 动画资产，可以读它的帧率作对照**

**（我们现在还没有 UE 动画资产 —— 所以这是"将来能用"，不是"现在已知"。）**

### 2.2 骨骼轨道

```
GetBoneAnimationTracks        ← 所有轨道
GetBoneTrackByIndex / ByName
GetBoneTrackIndex / IndexByName
GetNumBoneTracks
GetBoneTrackNames
**GetBoneTrackTransform**      ← 取某帧某骨骼的变换
GetBoneTrackTransforms
EvaluateBoneTrackTransform     ← 按时间求值（会插值）
IsValidBoneTrackName
```

### 2.3 曲线

```
GetCurveData
GetNumberOfTransformCurves / GetNumberOfFloatCurves
GetFloatCurves / GetTransformCurves
GetCurve / GetFloatCurve / GetTransformCurve / GetRichCurve
```

### 2.4 动画属性（Anim Attributes）

```
GetAttributes / GetNumberOfAttributes
GetNumberOfAttributesForBoneIndex / GetAttributesForBone / GetAttribute
```

**这是 UE5 的新机制（骨骼之外的通用属性动画），本项目不需要。**

### 2.5 🔴 写入入口

```
GetController    ← 从模型拿到 IAnimationDataController
GetNotifier
GetModifiedEvent / GetModifiedDynamicEvent
```

**`GetController()` 是关键 —— 它是通往写入接口的唯一大门。**

---

## 三、`IAnimationDataController` —— 42 个**写**方法

### 3.1 事务边界（必须成对）

```
OpenBracket      ← 开始批量修改
CloseBracket     ← 结束并提交
```

**官方约定：成批改动画数据必须包在 bracket 里，否则每次都触发通知，极慢。**

### 3.2 元数据

```
SetModel
SetNumberOfFrames    ← 设帧数
SetPlayLength        ← 设时长（秒）
SetFrameRate         ← 设帧率
```

### 3.3 🔴 骨骼轨道写入（核心）

```
AddBoneTrack                ← 加一根骨骼的轨道
InsertBoneTrack
RemoveBoneTrack
RemoveAllBoneTracks
**SetBoneTrackKeys**         ← 🔴 写入关键帧！
UpdateBoneTrackKeys
RemoveBoneTracksMissingFromSkeleton
```

**`SetBoneTrackKeys` 就是"给某根骨骼写入一串关键帧"的那个方法。**

### 3.4 曲线与属性

```
AddCurve / RemoveCurve / RemoveAllCurvesOfType
SetCurveKey / SetCurveKeys / RemoveCurveKey
SetCurveFlag / SetCurveFlags / SetCurveColor / SetCurveComment
SetTransformCurveKey(s) / RemoveTransformCurveKey
AddAttribute / RemoveAttribute / SetAttributeKey(s) / RemoveAttributeKey
UpdateCurveNamesFromSkeleton
UpdateAttributesFromSkeleton
UpdateWithSkeleton
```

---

## 四、完整的 C++ 写入配方

**这是从引擎源码推出的、把解码后的轨道写进 `AnimSequence` 的确切步骤：**

```cpp
// 1. 拿序列的数据模型
UAnimationDataModel* Model = Sequence->GetDataModel();

// 2. 从模型拿控制器
IAnimationDataController& Controller = Model->GetController();

// 3. 开事务
Controller.OpenBracket(NSLOCTEXT("Import", "Importing", "Importing animation"));

// 4. 设元数据 —— 帧率和帧数决定时间轴
Controller.SetFrameRate(FFrameRate(30, 1));
Controller.SetNumberOfFrames(TotalFrames);
Controller.SetPlayLength(TotalFrames / 30.0f);

// 5. 逐骨骼写轨道
for (each bone) {
    Controller.AddBoneTrack(BoneName);
    Controller.SetBoneTrackKeys(
        BoneName,
        PositionKeys,      // TArray<FVector>
        RotationKeys,      // TArray<FQuat>
        ScaleKeys);        // TArray<FVector>
}

// 6. 关事务（提交）
Controller.CloseBracket();
```

**三个 `TArray` 的长度必须一致（= 帧数），否则数据的对齐全乱。**

---

## 五、这对本项目意味着什么

### 5.1 三条路，现在能定了

| 路线 | 可行性 | 结论 |
| --- | --- | --- |
| **A. C++ 直接写 DataModel** | ✅ 完全可行，配方已明确 | **最直接，但要写 C++** |
| **B. glTF 中转** | ✅ Python 能写 glTF，引擎能导入 | **不用写 C++** |
| C. Python 直接写 | ❌ `GetController` 不在 Python 反射里 | 不行 |

**推荐仍走 B（glTF），理由：**
- Python 能完整生成 glTF
- `import_asset(factory=None)` 走 Interchange
- **不需要动工程 C++**

**但 A 的配方要留着 —— 如果 glTF 路线在"蒙皮"这关卡住，A 是备份方案。**

### 5.2 帧率问题：现在有两条信息来源

| 来源 | 说明 |
| --- | --- |
| **`GetSequenceLength` / `GetNumFrames`（Python 可用）** | 导入后可**验证**帧率 |
| **`Controller.SetFrameRate`** | **写入时由我们决定** |

**所以"墨香原始帧率"这个未知，其实**不影响能不能导入** ——
只影响"动画播放速度是否和原作一致"。可以先定 30 fps，观感不对再调。**

**这是重要的降级：从"阻塞"降为"调参"。**

### 5.3 骨架必须匹配

**`UAnimSequence` 持有 `Skeleton` 引用，`Controller.UpdateWithSkeleton` 会按骨架校正轨道。
所以骨骼名必须和骨架**完全一致**，否则轨道会被丢弃。**

**这条印证了之前的判断：必须先有带骨架的 SkeletalMesh，才能挂动画。**

---

## 六、掌握程度（动画引擎侧）

| 内容 | 掌握 |
| --- | --- |
| 四层结构（Base → Sequence → DataModel → Controller） | 🟢 **清楚** |
| `DataModel` 的 42 个读方法 | 🟢 **列全了** |
| `IAnimationDataController` 的 42 个写方法 | 🟢 **列全了** |
| **完整写入配方（OpenBracket → SetFrameRate → SetBoneTrackKeys → CloseBracket）** | 🟢 **能写出来** |
| 帧率问题的影响范围 | 🟢 **降级为调参** |
| 骨架匹配的必要性 | 🟢 **清楚** |
| `UAnimInstance` / 动画蓝图内部 | 🔴 **没深入** |
| 状态机 / 混合空间的实际使用 | 🔴 **没碰** |

**总体：动画引擎侧从 30% → **55%**。**

**涨的部分：数据结构与写入路径完全清楚，能写出配方。
没涨的部分：运行时怎么播（`UAnimInstance` 那一层）还是空白。**

---

## 七、还没学的（下一轮）

| 主题 | 为什么重要 |
| --- | --- |
| **`UAnimInstance` 与动画蓝图** | 决定动画怎么在运行时被播放 |
| **状态机（`GetBakedStateMachines`）** | 决定"走路→跑→攻击"怎么切 |
| **混合空间（`UBlendSpace`）** | 决定"按速度混合两个动作" |
| 动画通知（Notifies） | 决定"第 15 帧触发攻击判定" |

**这四项是"动画能播"和"动画能用"的差别。**

---

## 八、重查命令

```powershell
python Tools\map_animation_engine.py       # 四层的规模与拥有的成员
python Tools\read_animation_data_model.py  # 读写方法的完整列表
```
