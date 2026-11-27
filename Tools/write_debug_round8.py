"""Append the eighth debugging round, which closes the eight-domain plan.

    python Tools/write_debug_round8.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 65. 调试系列第 8 轮：**资产 — 八条真实失败，根因是路径猜错**（2026-11-26 50:00）

### 一、真实素材：日志里八条 `LoadAsset failed`

```
LogEditorAssetSubsystem: Error: LoadAsset failed: The AssetData
'/Game/Moxiang/Static/SM_Boss001.SM_Boss001' could not be found in the Asset Registry.
```

### 二、🔴 这句话的真正含义

**关键字不是「文件不存在」，是 **"could not be found in the Asset Registry"**。**
**→ 资产注册表里**没有这个路径**。**

**两种可能：路径不对（常见）／注册表还没扫到（少见）。**

### 三、本项目的根因：**Interchange 自动嵌套**

**`/Game/Moxiang/Static/SM_Boss001` 从来不存在。**

**真路径：**
```
/Game/Moxiang/Static/boss001_static/StaticMeshes/SM_Boss001
```

**多出来的 `boss001_static/StaticMeshes/` 是 Interchange 导入器按**源文件名**自动嵌套的。**

**→ 我的脚本按扁平路径猜，猜错了。**
**→ 和 gotcha #82/#83 同一个根因。**

### 四、正确做法：**按名字搜，不要猜路径**

**`Tools/find_asset.py` 实测：**
```
registry holds 2194 asset(s) under /Game
    /Game/Moxiang/Static/boss001_static/StaticMeshes/SM_Boss001.SM_Boss001
        class=StaticMesh
found 1 match(es) for 'SM_Boss001'
load .../SM_Boss001.SM_Boss001 -> ok
```

**→ 一次搜索拿到真路径，然后加载成功。**

**规则（以后所有脚本）：**
> **不要手写 `/Game/...` 路径。用 `get_assets_by_path` 搜，或从已有对象 `get_path_name()` 读。**
> **路径是人猜的，注册表是事实。**

**⚠️ 实测坑：`get_asset_by_object_path(SoftObjectPath(...))` 会**
**`TypeError: Failed to convert parameter 'object_path'`** —— 不接受这个类型。**

### 五、本项目资产分布（实测）

```
/Game                        2194 asset(s)
/Game/Moxiang                 370 asset(s)
/Game/Moxiang/Skeletal         59 asset(s)
/Game/Moxiang/Textures          1 asset(s)     ← 但磁盘有 2,407 张 PNG
/Game/Moxiang/Materials         1 asset(s)
/Game/Moxiang/Static            1 asset(s)
```

**🔴 两个陷阱：**
1. **`/Game` 2194，但项目自己的只有 370** —— 另外 1824 个是引擎模板。
   「项目有 2194 个资产」是**错的**。
2. **`Textures` 只有 1 个资产，磁盘却有 2,407 张 PNG** —— 贴图基本没导入。

### 六、预防：资产审计工具（实测）

**`Tools/audit_assets.py`：**
```
known set holds 2194 object path(s)
level has 116 actor(s)
checked 4 skeletal mesh reference(s), 0 not in registry
```

**→ 本项目当前**零缺失引用**。**

**价值：在「加载失败」发生**之前**发现路径不对。**

**⚠️ 只查了 `SkeletalMeshComponent`（4 个），`StaticMeshComponent` 还没加。**

### 七、打包版特有：Cook 找不到资产

**源码错误文本：**
```
"Generated package %ls is missing its generation data and cannot be saved."   CookOnTheFlyServer.cpp:3751
"CookPackageSplitter is missing %ls during PreSaveGeneratorPackage."         同上 :3993
```

**→ 「编辑器里好好的、打包后加载失败」的头号原因是**硬编码路径**：
**Cooker 靠引用图找资产，靠字符串猜的路径它看不见。****

**→ 这也说明本篇那个 `LoadAsset failed` 案例为什么危险：
编辑器里报错还能看见，打包后就**静默失败**。**

### 八、🎯 八个域全部完成

| # | 域 | 文档 | 实测程度 |
| --- | --- | --- | --- |
| 1 | 日志与断言 | `UE5-DEBUG-LOGGING.md` + `ASSERTS.md` | ✅ 全部实测 |
| 2 | 崩溃与调用栈 | `UE5-DEBUG-CRASH.md` | ✅ 用本项目真实崩溃 |
| 3 | 性能剖析 | `UE5-DEBUG-PERF.md` | ✅ 部分（面板抓不到）|
| 4 | 内存与泄漏 | `UE5-DEBUG-MEMORY.md` | ✅ 全部实测 |
| 5 | 渲染调试 | `UE5-DEBUG-RENDER.md` | ✅ 含像素级 A/B |
| 6 | 蓝图与脚本 | `UE5-DEBUG-SCRIPT.md` | ✅ 故意失败实测 |
| 7 | 网络调试 | `UE5-DEBUG-NET.md` | ⚠️ **源码为主，未实测** |
| 8 | 资产与加载 | `UE5-DEBUG-ASSET.md` | ✅ 用本项目真实日志 |

**共 10 篇调试文档（含索引）。**

### 九、下一轮该做什么

**按目标原文「直到能独立定位真实 UE5 故障为止」——现在该**实战**了。**

**不再继续写文档，而是：**
1. 找项目里一个**还没解决的问题**
2. 用这九篇的方法从头定位（不查既有结论）
3. 记录用了哪篇的哪个方法、定位过程、结论

**候选问题（从 `Docs/BATCH-EXPORT-STATUS.md` 的未解决项里挑）：**
- 78 个模型没有 MATERIAL 块
- 101 个贴图名对应文件不存在
- `thunder3` 转换失败
- 动画在编辑器里看不见播放
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 65." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 65; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
