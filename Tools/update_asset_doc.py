"""Replace the placeholder section of the asset pipeline document with measured findings.

The section was written from expectation; the measurements that follow replaced it. Editing
through a script rather than the edit tool because the target block is long and contains table
pipes and code fences that are easier to match by its two boundary markers than by quoting.

    python Tools/update_asset_doc.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-ASSET-PIPELINE.md"

NEW_SECTION = """## 四、本项目的现状与风险（实测）

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

### 4.2 发现 107 个历史遗留资产

**`Content/Moxiang` 共 298 个资产：**

| 类别 | 数量 | 状态 |
| --- | --- | --- |
| `SM_LZ_*`（网格） | **96** | 与清单**完全一致** |
| `M_LZ_*`（材质实例） | **95** | 与清单一致（1 个未生成）|
| **`jp_*`** | **49** | **旧构建遗留** |
| **`17_*`** | **12** | **旧构建遗留** |
| 其他（M_/SM_/贴图） | 46 | 混合 |

**成因：** 早期构建按 OBJ 文件名导入资产；后来改成按清单命名（`SM_LZ_*`）。**旧的那批没清理。**

**验证：清单里 96 个网格名与磁盘上 96 个 `SM_LZ_*` 完全一一对应，零差异。
所以那 107 个不是"在用但名字不同"，是真没人用。**

**但删之前必须用 `get_referencers` 确认 —— 不能凭"名字对不上"就删，那是猜。**

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

"""


def main():
    text = open(PATH, encoding="utf-8").read()
    start = text.find("## 四、本项目的现状与风险")
    end = text.find("## 五、引用的另一面")
    if start < 0 or end < 0:
        print("boundaries not found: start=%d end=%d" % (start, end))
        return
    updated = text[:start] + NEW_SECTION + text[end:]
    open(PATH, "w", encoding="utf-8").write(updated)
    print("replaced section four: %d -> %d bytes" % (len(text), len(updated)))


if __name__ == "__main__":
    main()
