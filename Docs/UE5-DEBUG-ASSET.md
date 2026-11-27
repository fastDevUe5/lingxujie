# UE5 调试 · 九：资产与加载问题

> **本篇基于本项目日志里**八条真实的 `LoadAsset failed`** 记录，逐个字段拆解。
>
> **核心结论：`"could not be found in the Asset Registry"` **几乎总是路径写错了**，
> 不是文件不存在。正确做法是**按名字搜**，而不是猜路径。**
>
> **日期：2026-11-26 · UE 5.8.4**

---

## 一、真实案例：八条 `LoadAsset failed`

**日志原文（本项目的实际记录）：**
```
LogEditorAssetSubsystem: Error: LoadAsset failed: The AssetData
'/Game/Moxiang/Textures/T_Boss_Mob01.T_Boss_Mob01' could not be found in the Asset Registry.

LogEditorAssetSubsystem: Error: LoadAsset failed: The AssetData
'/Game/Moxiang/Static/SM_Boss001.SM_Boss001' could not be found in the Asset Registry.
```

### 1.1 🔴 这句话的真正含义

**关键字不是「文件不存在」，是 **"could not be found in the Asset Registry"**。**

**→ 意思是：资产注册表里**没有这个路径**。**

**两种可能：**
1. 资产**不在那个路径**（最常见）
2. 资产刚建好，注册表**还没扫描到**（少见）

### 1.2 本项目的根因：路径猜错了

**`/Game/Moxiang/Static/SM_Boss001` 从来不存在。**

**实际路径是：**
```
/Game/Moxiang/Static/boss001_static/StaticMeshes/SM_Boss001
```

**多出来的 `boss001_static/StaticMeshes/` 是 **Interchange 导入器自动嵌套**的
（目录名取自源文件名）。**

**→ 我的脚本按「扁平路径」猜，猜错了。**

**⚠️ 这和 gotcha #82/#83（glTF 用 Interchange 导入、会嵌套一层）是同一个根因。**

---

## 二、正确做法：**按名字搜，不要猜路径**

**`Tools/find_asset.py` 的核心（✅ 实测有效）：**
```python
reg = unreal.AssetRegistryHelpers.get_asset_registry()
assets = reg.get_assets_by_path("/Game", True, False)

for asset in assets:
    package = str(asset.package_name)   # /Game/Moxiang/Static/boss001_static/StaticMeshes
    name    = str(asset.asset_name)     # SM_Boss001
    if needle.lower() in name.lower():
        log("%s.%s" % (package, name))
```

**实测输出：**
```
registry holds 2194 asset(s) under /Game
    /Game/Moxiang/Static/boss001_static/StaticMeshes/SM_Boss001.SM_Boss001
        class=StaticMesh
found 1 match(es) for 'SM_Boss001'
load /Game/Moxiang/Static/boss001_static/StaticMeshes/SM_Boss001.SM_Boss001 -> ok
```

**→ 一次搜索就拿到真路径，然后加载成功。**

**给以后所有脚本的规则：**
> **不要手写 `/Game/...` 路径。
> 用 `get_assets_by_path` 搜，或者从已有的对象上 `get_path_name()` 读。**
> **路径是人猜的，注册表是事实。**

### 2.1 一个实测踩到的 API 坑

**我先试了 `get_asset_by_object_path(SoftObjectPath(...))`：**
```
TypeError("AssetRegistry: Failed to convert parameter 'object_path' when calling function")
```

**→ 这个 API 的 `object_path` 参数**不接受** `unreal.SoftObjectPath`。**

**→ 用 `get_assets_by_path` + 自己过滤更可靠。**

---

## 三、本项目资产分布（✅ 实测）

```
/Game                          2194 asset(s)
/Game/Moxiang                   370 asset(s)
/Game/Moxiang/Skeletal           59 asset(s)
/Game/Moxiang/Textures            1 asset(s)
/Game/Moxiang/Materials           1 asset(s)
/Game/Moxiang/Static              1 asset(s)
```

### 3.1 两个值得注意的数字

**① `/Game` 2194，但 `/Game/Moxiang` 只有 370**

**→ 1824 个是引擎模板/其他内容，不是墨香资产。**
**→ 「项目有 2194 个资产」这个说法是**错的** —— 项目自己的只有 370 个。**

**⚠️ 这类「分母搞错」的陷阱本系列已经出现过多次。**

**② `Textures` 只有 **1** 个资产**

**→ 但磁盘上有 2,407 张 PNG（`Assets/Moxiang/textures_png`）。**
**→ 说明贴图**基本没导入 UE**，只导了 Boss 那一张。**
**→ 这是一个**真实的待办**，不是缺陷。**

---

## 四、资产排查清单

### 4.1 按错误信息定位

| 错误文本 | 含义 | 第一步 |
| --- | --- | --- |
| **`could not be found in the Asset Registry`** | **路径不在注册表** | **按名字搜真实路径** |
| `Failed to load package` | 文件在但打不开 | 检查文件是否损坏 / 版本 |
| `LogLinker: Warning: Can't find file` | 引用的资产缺失 | 用 `obj refs` 找谁引用它 |
| `LogStreaming: Error` | 异步加载失败 | 检查资产是否被 GC |
| `Cook: ... not found` | **打包时**找不到 | 检查是否在 Cook 目录里 |

### 4.2 「这个资产为什么还在内存里」

```
obj refs name=/Game/路径/资产名.资产名 shortest
```

**→ 输出从该资产一路到根的持有链。**
**→ 详见 `UE5-DEBUG-MEMORY.md` 第 4.2 节。**

### 4.3 「哪个资产最大」

**UI 路径：** 内容浏览器右键 → **Size Map**。

**命令行路径：**
```
memreport -full
```
**→ `obj list -resourcesizesort` 段落按资源大小排序。**
**→ 详见 `UE5-DEBUG-MEMORY.md`。**

**⚠️ Size Map 和 `obj list` 量的都是**资源占用**，不含磁盘大小。**
**磁盘占用要看文件本身。**

### 4.4 「重定向器（Redirector）」

**资产被移动/重命名后会留下一个 Redirector，旧路径仍能加载但会变慢。**

**命令（源码 `EditorServer.cpp` 5707 行）：**
```
LISTMAPPKGDEPENDENCIES TEXTURE RESAVE
```

**UI 路径：** 内容浏览器右键文件夹 → **Fix Up Redirectors in Folder**。

**⚠️ 本项目还没做过这一步 —— 待做。**

---

## 五、预防：资产审计工具（✅ 实测）

**`Tools/audit_assets.py` 做的事：**

1. 列出各层级资产数量
2. 把所有 `/Game` 资产建成一个**集合**（这样查找是集合测试，不用尝试加载）
3. 遍历关卡里所有 `SkeletalMeshComponent`，检查引用的资产在不在集合里

**实测输出：**
```
known set holds 2194 object path(s)
level has 116 actor(s)
checked 4 skeletal mesh reference(s), 0 not in registry
```

**→ 本项目当前**零缺失引用**。**

**⚠️ 只检查了 `SkeletalMeshComponent`（4 个）。
`StaticMeshComponent` 还没加进去 —— 待扩展。**

**这个审计的价值：**
> **它会在「加载失败」发生**之前**告诉你路径不对。
> 而不是等日志里出现八条 Error 再回头查。**

---

## 六、打包版特有：Cook 找不到资产

**源码 `CookOnTheFlyServer.cpp` 里的错误（第 3751、3993、4084 行）：**
```
"Generated package %ls is missing its generation data and cannot be saved."
"CookPackageSplitter is missing %ls during PreSaveGeneratorPackage."
"CookPackageSplitter is missing %ls during BeginCachePostMove."
```

**以及 `CookGenerationHelper.cpp` 1884 行：**
```
"GeneratedInfo missing for package %ls."
```

**→ 这些是 **Cook 阶段**的错误，编辑器里跑得好好的也会出现。**

**常见原因：**
| 原因 | 表现 |
| --- | --- |
| 资产在 `Content` 外（如 `Plugins/`）但没配 `DirectoriesToAlwaysCook` | 打包后加载失败 |
| 只被**硬编码路径字符串**引用（不是资产引用）| Cook 分析不到依赖 |
| `EditorOnly` 数据被引用 | 打包后为空 |
| `SoftObjectPath` 拼错 | 运行时才发现 |

**⚠️ 「编辑器里好好的，打包后加载失败」的头号原因就是**硬编码路径**：
Cooker 靠引用图找资产，靠字符串猜的路径它看不见。**

**→ 这也解释了本系列的 `LoadAsset failed` 案例为什么危险：
如果用硬编码路径而不是资产引用，编辑器里报错还能看见，打包后就**静默失败**。**

---

## 七、待做

| 事项 | 为什么 |
| --- | --- |
| 扩展 `audit_assets.py` 检查 `StaticMeshComponent` | 现在只查了 4 个骨骼网格 |
| 做一次 Redirector 清理 | 没查过有没有残留 |
| 把 2,407 张 PNG 批量导入 | 现在 `Textures` 只有 1 个资产 |
| 给 `LoadObject` 调用加路径校验 | 避免再次手猜路径 |

**⚠️ 按用户要求本轮**只读不改**。**

---

## 八、本篇依据

| 事实 | 来源 |
| --- | --- |
| 八条 `LoadAsset failed` 原文 | **本项⽬ `Saved/Logs/LingXuJie.log`（真实记录）** |
| `SM_Boss001` 真实路径 | **实测 `find_asset.py`** |
| 2194 / 370 / 59 / 1 / 1 / 1 | **实测 `audit_assets.py`** |
| `get_asset_by_object_path` 不接受 SoftObjectPath | **实测（TypeError）** |
| Cook 阶段的错误文本 | `CookOnTheFlyServer.cpp` 3751/3993/4084、`CookGenerationHelper.cpp` 1884 |
| `LISTMAPPKGDEPENDENCIES ... RESAVE` | `EditorServer.cpp` 5707 |
