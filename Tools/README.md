# Tools

**这个目录里混着两类东西：会反复用的工具链，和 300 多个一次性历史脚本。找工具看这一页，不要在文件名里翻。**

---

## 一、工具链（会反复用，改动要小心）

| 用途 | 文件 |
| --- | --- |
| 编译 + 生成关卡 | `BuildAll.ps1`、`BuildLevel.ps1` |
| 编辑器生命周期 | `EditorGuard.ps1`（check / dismiss / restart / watch / stop）、`RebuildInEditor.ps1` |
| 开工自检 | **`Status.ps1`**（一屏：编辑器 / MCP / 关卡 / actor 数 / 相机是否默认位 / git / 磁盘） |
| 窗口布局 | `SetupLayout.ps1` |
| MCP 调用 | `mcp.ps1`、`mcp_capture.py`、`mcp_tools.py`、`list_mcp_tools.py` |
| 视口复位 | `reset_view.py`（规则 3b 的兜底；MCP `SetCameraTransform` 也能做） |
| 清理 | `Cleanup.ps1`（默认只算不删，见 AGENTS 第 13 条） |
| 检查与审计 | `RunTests.ps1`、`CheckAssets.ps1`、`audit_project_config.py`、`audit_focus.py`、`audit_level_physics.py` |
| 关卡真源 | `build_level.py`（+ `Assets/Map/p0_world.json`，见 DECISIONS D12）、`build_world.py` |
| 打包发布 | `Package.ps1`、`VerifyPackage.ps1`、`MakeRelease.ps1`、`PublishRepo.ps1` |
| 截图对比 | `diff_captures.py`、`diff_region.py`、`crop_region.py` |
| 断点卡片 | `breakpoint.py` |
| Fab 素材 | `ImportFab.ps1`、`fab_add*.ps1`、`WatchFabDownloads.ps1` |

---

## 二、一次性历史脚本（**不要改、不要当 API 用**）

按前缀就能认出来，它们都是某一轮的记录，跑完就不再需要：

| 前缀 | 数量 | 当时在干什么 |
| --- | --- | --- |
| `write_*` | 55 | 写文档 / 写调试记录 |
| `link_*` | 35 | 文档之间的互链 |
| `add_*` | 28 | 往 gotcha 或索引里追加内容 |
| `diag_*` | 19 | 分步诊断（normals / mip / scatter / order / warn） |
| `mark_*` | 18 | 在索引里把某个案例标记成已完成 |
| `document_*` | 15 | 把某一轮的结论落成文档 |
| `fix_*` | 13 | 修某个具体文档或脚本 |
| `learn_*` | 12 | 渲染 A/B 的探针与实验 |
| 其他 `*_step*.py` / `*_probe*.py` | 若干 | 同一次诊断的中间步骤 |

**要查历史，用 `git log -- Tools/<名字>` 或 `git log -S "<关键字>"`，不要在这 400 个文件里翻。**

---

## 三、新的一次性脚本放哪儿

**放 `Saved\scratch\`（`Saved/` 不入库），不要往 `Tools` 里丢。**
`Tools` 只放"下次还会用"的东西；一次性的东西进了 `Tools` 就是永久的技术债。

---

## 四、为什么不做"把历史脚本搬到 `Tools/archive/`"

搬动会让 `Docs/` 里一票 `Tools/write_debug_roundXX.py` 的引用失效，而收益只有"列表变短"。
这些文件一共 1.6 MB，对编译、编辑器、加载都零影响。**要的是可发现性，所以加这一页；不是要搬家。**
