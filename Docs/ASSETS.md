# 资产台账 + 重建清单

> **一句话：仓库里只有文本（`git ls-files` 约 1,148 个文件 / 16.3 MB）；其余 ~5.2 GB 在这台机器上。**
>
> **万一 `Content/` 没了，照第 2 节按顺序做就能重建。** 第 1 节说明每块东西从哪来、丢不丢得起。
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 1. 一页速查

| # | 资产 | 体积 / 文件 | 在 git 里 | 来源 | 重建方式 |
| --- | --- | --- | --- | --- | --- |
| 1 | 代码 / 文档 / 工具 / 关卡布局 JSON | **16.3 MB** / 1,148 | ✅ | 本项目 | `git clone` |
| 2 | **自绘贴图** `Assets/Textures`（16 张 PNG） | 2.1 MB | ✅ | 自绘（原生成脚本已不在） | 已在库里 |
| 3 | 关卡参数 `Assets/Map/p0_world.json`、`Assets/Gate/*.json`、`Assets/Village/*.json` | 0.2 MB | ✅ | 采集/手写 | 已在库里 |
| 4 | **KCISA 甫吉岛洗然亭** `Content/SeyeonjeongPavilion` | **3.77 GB** / 859 | ❌ | Fab 库 | Fab 重下 → `ImportFab.ps1` |
| 5 | **Megaplant Library** `Content/Megaplant_Library` | 342 MB / 149 | ❌ | Fab 库 | 同上 |
| 6 | **KHS 建春门** `Content/GeonchunmunComplex` | 320 MB / 417 | ❌ | Fab 库 | 同上（只是练习场，关卡不依赖） |
| 7 | **Fab Megascans** `Content/Fab/Megascans`（QMF_* 材质函数） | 219 MB / 41 | ❌ | Fab 库 | 同上 |
| 8 | **兰州城几何源** `Assets/Moxiang/ue_import/*_arch_*.obj`（96 个）+ `textures_png`（2,407 张） | 86 MB + 340 MB | ❌ 本地 | **研究区**（`moxiang-study` 解析好的 map） | `build_map_obj.py` 重跑 |
| 9 | **角色/骨骼 glTF** `Assets/Moxiang/ue_import/batch/*.gltf`（253 个） | 6 MB | ❌ 本地 | 研究区 `resources/mod` | `batch_export.py` 重跑 |
| 10 | **Polyfork 试用资产** `Assets/Polyfork` | 5.5 MB / 37 | ❌ **授权原因不入库** | Polyfork | 重下（见第 3 节） |
| 11 | `Content/Props`（BP_Terrain / Roof / GrassField / StoneField） | 8.1 MB / 111 | ❌ | **由 `Assets/Polyfork` 生成** | `build_level.py` |
| 12 | `Content/Materials`、`Content/Textures` | 12 MB | ❌ | **生成物** | `build_level.py` |
| 13 | `Content/Maps/LingXuJie.umap` | 0.2 MB | ❌ | **生成物** | `build_level.py` |

**判据（AGENTS 硬约束 5）**：**"丢了能不能重建"** —— 能重建的不进 git，不能重建的（源码、文档、参数、2 MB 的自绘贴图）才进。

---

## 2. 从零重建（按顺序做）

**触发场景：换机器 / `Content/` 被删 / 磁盘坏了。**

### 第 0 步：拿回文本

```powershell
git clone git@github.com:fastDevUe5/lingxujie.git
# 仓库约 16 MB，只有文本；Content/ 是空的
```

### 第 1 步：把 Fab 包装回工程

**Fab 面板 → 找到第 1 节的 4 个包 → 下载 2K 档 → 「添加到项目」。**
或命令行（zip 已在本地时）：

```powershell
powershell -ExecutionPolicy Bypass -File Tools\ImportFab.ps1 -Source <zip所在目录>
# 解压在 Saved\FabStaging，坏包不会碰 Content
```

**⚠️ Fab 原始 zip 目前不在本机**（`Downloads` 与 `Saved\FabStaging` 都空），只能重新下载。

### 第 2 步：重建墨香资产（**两条路，别混**）

**A. 兰州城（96 个 `SM_LZ_*` + 95 个 `M_LZ_*`，关卡的主体）—— 来自 OBJ，不是 glTF：**

```powershell
# 源：研究区  C:/Users/tk/Desktop/moxiang-study（解析好的 map）
py Tools/build_map_obj.py
#   → Assets/Moxiang/ue_import/*_arch_*.obj（96 个，86 MB）+ textures_png/（2,407 张，340 MB）

py Tools/build_moxiang_map.py
#   → /Game/Moxiang：96 个 SM_LZ_* + 95 个 M_LZ_* + M_Moxiang_Ground
```

**B. 角色 / 骨骼（`Content/Moxiang/Skeletal`，59 个）—— 来自 glTF：**

```powershell
py Tools/batch_export.py
#   → Assets/Moxiang/ue_import/batch/*.gltf（253 个，6 MB）
# 再逐个导入 /Game/Moxiang/Skeletal/...（⚠️ 这一步仍是**一次性脚本**，见第 7 节缺口 ②）
```

### 第 3 步：生成关卡（材质、道具、地形都在这一步）

```powershell
powershell -ExecutionPolicy Bypass -File Tools\BuildAll.ps1
# 编辑器开着就改用 Tools\RebuildInEditor.ps1
```

### 第 4 步：验证

```
日志出现  [LingXuJie] Done. N actors      N 应与上次接近（当前 116）
MCP 截图：广场应能看到红牌坊、石板路、建筑群
```

---

## 3. 几张必须知道的事实

- **`Assets/Polyfork` 不入库是授权原因**（旧的 `.gitignore` 写着 "trial only, not committed"），
  不是体积 —— 5.5 MB。**删了它 `Content/Props` 就生成不出来**，关卡会缺石头/草丛/屋顶。
- **`Assets/Textures` 那 16 张 PNG 没有生成脚本**（`Tools/paint_textures.py` 已不在），
  所以是**不可再生**的，才破例放进仓库（2.1 MB）。
- **`Content/Textures` 是导入产物**，不是原件；原件在 `Assets/Textures`。
- **兰州城的源是 OBJ，不是 glTF。** `17_arch_101_10_soongsan_door.obj` → `SM_LZ_101_10_SOONGSAN_DOOR`。
  `Assets/Moxiang/ue_import/batch` 那 253 个 glTF 是**角色**（`batch_export.py` 产出），
  **和建筑名对不上是正常的，不是资产丢了。**
- **两个大包不在生成流程里**：`SeyeonjeongPavilion` 和 `GeonchunmunComplex` 目前只是素材池 +
  练习场（后者的 Demo 地图用于渲染实验）。**关卡的 116 个 actor 不依赖它们。**

---

## 4. 已在 Fab 库、还没导入的

| 资产 | 角色 | 网格 | 状态 |
| --- | --- | --- | --- |
| KHS Naganeupseong Walled Town | 民居（茅草院屋成组） | 206 | 未导入 |
| KCISA Korean Traditional Smart Materials Vol.1 | 地面材质（砖/石/草/土） | — | 未导入 |
| KCISA Korean Traditional Heritage Props | 道具（罐/灯笼/条凳/农具） | 145 | 未导入 |
| tharlevfx Water Materials | 水面材质 | — | 未导入 |
| KHS House Of Changwon | 院落住宅 | 228 | 未导入 |
| KHS Gwolnaegaksa（官署） | 院落/门楼 | — | 未导入 |
| KHS Soswaewon（园林） | 竹/松/叠石 | 99 | 未导入 |

**导入流程**：编辑器 Fab 面板 → 拉到右栏「添加到项目」→ 弹「与 5.8 不兼容」选 **5.7**。

---

## 5. 署名要求（CC-BY，发布时必须写）

- KHS（Korea Heritage Service）系列：`Korea Heritage Service`
- KCISA 系列：`Korea Culture Information Service Agency`
- Megascans / Quixel：Epic Games（Fab 标准许可）

---

## 6. 参照资料（不是素材，不能进 `Content/`）

`C:/Users/tk/Desktop/moxiang-study/Docs/MoXiang/`（**仓库外，不入库**）：参照截图与逆向资料；
其中 `maps/` 目前只有 3 张（1 张城镇广场、1 张俯视地形、1 张含地图内嵌的宣传图），**世界地图还缺**。

---

## 7. 已知缺口（这一版没做完的三件事）

| # | 缺口 | 影响 |
| --- | --- | --- |
| ① | **Fab 包的准确库名与档位**只在下表里，没核实到 Fab 页面 | 重下时可能选错包/选错质量档 |
| ② | **角色 glTF（253 个）没有批量导入脚本** —— 当年是一个一个 `import_gltf_any.py` 导的 | 第 2 步 B 只能手工补，`Content/Moxiang/Skeletal` 的 59 个资产恢复不了 |
| ③ | **"每个包被哪些 actor 用"没反查** | 不知道丢了哪个包会少哪片景 |

**已核实（不再算缺口）**：兰州城那条链路两个脚本都在
（`build_map_obj.py` → 96 个 `*_arch_*.obj`；`build_moxiang_map.py` → `/Game/Moxiang`），
且产物命名能对上现有资产（`17_arch_<stem>.obj` → `SM_LZ_<STEM>`）。
