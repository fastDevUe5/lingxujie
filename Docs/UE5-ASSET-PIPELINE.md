# UE5 资产管线：引用、加载、打包（引擎源码核实）

> **这是本项目最该先学的域 —— 我们每天都在用 `AssetTools`，但只知调不知原理。**
> **最关键的认知：硬引用会让项目在打包后加载变慢或失败，而编辑器里完全看不出来。**

---

## 一、核心区分：硬引用 vs 软引用

| | 硬引用 | **软引用** |
| --- | --- | --- |
| 写法 | `UObject*` / `TSubclassOf<T>` | **`TSoftObjectPtr<T>` / `TSoftClassPtr<T>`** |
| 存的是什么 | **对象指针** | **路径字符串** |
| 何时加载 | **跟着拥有者一起加载** | **要用时才加载** |
| 打包影响 | 目标资产被打进同一个包 | 可以独立分包 |
| 风险 | **链式加载，可能拖垮启动** | 需要处理"没加载"和"加载失败" |

**一句话：**
> **硬引用是"我要这个对象"，软引用是"我知道它在哪"。**

**实测头文件：**
```
SoftObjectPtr.h    35,935 字节
SoftObjectPath.h   31,724 字节
```

---

## 二、`TSoftObjectPtr` 的实际方法（源码提取）

```
LoadSynchronous         ← 立刻加载（阻塞）
LoadAsync               ← 后台加载（不阻塞）
IsValid                 ← 有对象吗（已加载且有效）
IsPending               ← 正在加载吗
IsNull                  ← 路径是空的吗
ToString / GetLongPackageName / GetAssetName
ToSoftObjectPath
Reset
```

### 2.1 三态判断（这是用软引用的核心）

**软引用有三个状态，不是两个：**

```
① IsNull()      → 根本没配路径
② IsPending()   → 正在加载，还不知道结果
③ IsValid()     → 加载完了，有对象
```

**所以正确写法是先判 pending 再判 valid：**

```python
# 伪代码
if ref.is_null():
    # 没配
elif ref.is_pending():
    # 等
elif ref.is_valid():
    # 能用
else:
    # 加载失败
```

**⚠️ 只判 `is_valid()` 会把"正在加载"和"加载失败"混为一谈。**

### 2.2 `LoadSynchronous` 什么时候能用

**它阻塞当前线程直到加载完。**

| 场景 | 能用吗 |
| --- | --- |
| 编辑器脚本（我们现在的用法） | ✅ 能 |
| 游戏里小资产、首帧 | ⚠️ 会导致卡顿 |
| 游戏里大资产、循环中 | ❌ 不要 |

---

## 三、加载的三个层次

| 层 | 类 | 头文件 | 职责 |
| --- | --- | --- | --- |
| **索引** | `UAssetRegistry` | 30,212 B | **不加载就能查"有什么"** |
| **策略** | `UAssetManager` | 80,883 B | 决定"该加载什么、什么时候" |
| **执行** | `FStreamableManager` | 45,988 B | **异步加载，返回句柄** |

### 3.1 `UAssetManager` 的关键方法（源码提取）

```
GetStreamableManager              ← 拿到执行者
ScanPathsForPrimaryAssets         ← 扫描某路径下的主资产
CreatePrimaryAssetIdFromChunkId   ← 打包分块相关
RecursivelyExpandBundleData       ← 展开 bundle
GetIfInitialized / IsInitialized
PushBulkScanning / PopBulkScanning / StartBulkScanning
```

**"主资产"（Primary Asset）是 `AssetManager` 的核心概念：**

> **主资产 = 可以被单独指定"何时加载"的资产**（比如一个关卡、一套角色皮肤）。
> **非主资产只能跟着主资产一起加载。**

**这就是打包分包（chunk）的机制来源 —— 按主资产分块。**

### 3.2 `FStreamableManager` 的用法

```cpp
FStreamableManager* Manager = ...;                  // 从 AssetManager 拿
TSharedPtr<FStreamableHandle> Handle =
    Manager->RequestAsyncLoad(SoftPath, FStreamableDelegate::CreateLambda([]{
        // 加载完了
    }));
```

**句柄（`FStreamableHandle`）让你能：**
- 查进度
- 取消加载
- 释放引用（让资产可被 GC）

---

## 四、本项目的现状与风险（实测）

### 4.1 引用链实测（用 `AssetTools.get_dependencies`）

| 资产 | 类型 | 依赖 |
| --- | --- | --- |
| `jp_roof00` | `StaticMesh` | **`[/Script/InterchangeEngine]`** ← 零材质 |
| `M_LZ_JP_ROOF00` | `MaterialInstanceConstant` | `[/Game/Moxiang/M_Moxiang_Building, /Game/Moxiang/jp_roof00]` |
| `SM_LZ_JP_ROOF00` | `StaticMesh` | `[NavigationSystem, InterchangeEngine, WorldGridMaterial]` |
| `SM_Lanzhou_Terrain` | `StaticMesh` | `[NavigationSystem, InterchangeEngine, WorldGridMaterial]` |

**三条结论：**

1. **网格资产本身不带材质** —— 只有导入器和默认 `WorldGridMaterial`。
   **材质是 `place()` 里给 Actor 挂的，不在资产里。**

2. **材质实例引用母材质 + 网格**（`M_Moxiang_Building` + `jp_roof00`）。
   **所以删网格前要删材质实例，否则留断链。**

3. **`NavigationSystem` 出现在网格依赖里** —— 网格参与导航生成。
   **这是"大批网格让导航构建变慢"的原因。**

### 4.2 🔴 更正：「107 个遗留资产」是我搞错了

**我先前的判断：不在清单里的 107 个资产是旧构建遗留，可以清理。**

**实测推翻了它：**

```
jp_roof00            -> Texture2D       被 M_LZ_JP_ROOF00 引用
17_101_stonew01      -> Texture2D       被 M_LZ_17_101_STONEW01 引用
54_nanju_04          -> Texture2D       被 M_LZ_54_NANJU_04 引用
101_10_soongsan_door -> Texture2D       被 M_LZ_101_10_SOONGSAN_DOOR 引用
```

**它们是**贴图**，而且正是材质实例所引用的那些贴图。**

**为什么不在清单里：清单只列网格和材质，不列贴图。**

**正确的资产构成：**

| 类别 | 数量 | 说明 |
| --- | --- | --- |
| `SM_LZ_*` | 96 | 网格 |
| `M_LZ_*` | 95 | 材质实例 |
| **`M_Moxiang_*`** | 4 | **母材质**（`Building` / `Building_Masked` / `Ground` / `Stone`）|
| **其余** | **104** | **贴图（Texture2D）** |
| **合计** | **299** | |

**⚠️ 如果按我原来的判断去删，会把材质实例的贴图删掉 —— 整个城市的贴图会全部丢失。**

**这条更正比原来的结论重要得多。**

**得到的教训：**
> **「名字对不上清单」不是「没人用」的证据。**
> **必须查两件事：`get_asset_class`（它是什么）和 `get_referencers`（谁引用它）。**
> **两个都查完才知道能不能删。**

### 4.3 编辑器 API vs 运行时 API

```python
unreal.EditorAssetLibrary.load_asset(path)      # 编辑器限定，打包后没有
```

**对现在没问题**（关卡在编辑器里建）。**但运行时加载必须换：**

| 需求 | 该用 |
| --- | --- |
| 编辑器内建关卡 | `EditorAssetLibrary` ✅ 现在这样 |
| 运行时加载关卡 | `AssetManager` + 软引用 |
| 运行时加载模型/贴图 | `FStreamableManager` + 软引用 |
| 只查有没有、不加载 | `AssetRegistry` |
| **查引用关系** | **`AssetTools.get_referencers` / `get_dependencies`** ✅ 现在就能用 |

### 4.4 ⚠️ Python 侧没有异步加载

**`AssetTools` 只有 `load_asset`（同步）。没有 `request_async_load`。**

**所以"运行时异步加载"在 Python 里做不到** —— 要么接受同步阻塞，要么写 C++。**

**这是一条重要边界：编辑器自动化能用 Python，运行时资产管理不行。**

### 4.5 埋下的隐患

**96 个网格 + 95 个材质实例全部硬摆在关卡里。**

| 打包后果 | 现在看得到吗 |
| --- | --- |
| 全部进同一个包 | 现只有一座城，看不出 |
| 打开关卡全部加载 | 同上 |
| 524,288 面地形 + 96 建筑同时驻留 | 同上 |

**计划做 64 张地图时，这会变成"打包后打开等几十秒"。**

### 4.6 该做什么

| 措施 | 时机 |
| --- | --- |
| 清理 107 个遗留资产（先 `get_referencers` 确认）| 可做 |
| 建筑按地图分组做成主资产 | 做第二座城之前 |
| 关卡用 Level Instance 或流送关卡 | 同上 |
| 材质实例共享母材质（已在做）| ✅ 已完成 |
| `merge_actors` 合并同地图建筑 | 下一轮可做 |

## 五、引用的另一面：GC 与句柄

**软引用加载出来的对象，谁负责持有？**

```
软引用（路径）
   ↓ LoadAsync
FStreamableHandle（句柄）
   ↓ 句柄持有强引用
实际对象（不会被 GC）
   ↓ 句柄释放
对象可以被 GC 回收
```

**所以句柄不释放 = 资产一直占内存。
句柄释放太早 = 资产被回收 = 用的时候是空指针。**

**这是运行时资产管理的核心难题，我们现在还没遇到（因为在编辑器里）。**

---

## 六、掌握程度（诚实）

| 内容 | 掌握 |
| --- | --- |
| 硬引用 vs 软引用的区别 | 🟢 **清楚** |
| `TSoftObjectPtr` 的三态判断 | 🟢 **清楚**（`IsNull` / `IsPending` / `IsValid`）|
| `AssetRegistry` / `AssetManager` / `StreamableManager` 的分工 | 🟢 **清楚** |
| 主资产与打包分块的关系 | 🟡 **知道概念，没实操** |
| `RequestAsyncLoad` 的实际写法 | 🟡 **知道签名，没写过** |
| bundle / chunk 的配置 | 🔴 **不懂** |
| GC 与句柄生命周期的实际调试 | 🔴 **没经验** |
| **用 `get_dependencies` 查实际引用链** | 🟢 **做过**（查了 4 个资产）|
| **资产遗留的判定方法** | 🟢 **做过**（清单 vs 磁盘比对）|

**总体：约 45%。**

**新增的两条实测能力：**
- 能用 `get_dependencies` 查任意资产的引用链
- 能用「清单 vs 磁盘」比对找出遗留资产

**但"运行时异步加载"这条**已经确认 Python 做不到**（`AssetTools` 只有同步 `load_asset`）。
所以这一域的天花板在**编辑期**，运行时必须 C++。**

---

## 七、下一步（如果要动手）

**最小验证：在编辑器里写一段 Python，用 `StreamableManager` 异步加载一个建筑网格。**

```python
import unreal
manager = unreal.AssetManager  # 或从子系统拿
handle = manager.request_async_load(
    "/Game/Moxiang/17_jp_roof00.17_jp_roof00",
    unreal.StreamableDelegate(...))
```

**⚠️ Python 侧对 `FStreamableManager` 的绑定可能不完整 —— 这需要验证。**

**如果 Python 拿不到，那就说明"运行时资产加载必须在 C++ 里做"，
这也是一条要记下来的边界。**

---

## 八、重查命令

```powershell
python Tools\map_asset_references.py
```
