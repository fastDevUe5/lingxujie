# 地图复刻 SOP（常驻编辑器 + MCP）

> 2026-11-26 定稿。**这份是硬规则，不是建议。**
> 上一次会话因为反复违反，被连续纠正了七八次，浪费了大量时间。
> 新会话开工前必须读完这一份。

---

## 零、一句话原则

**编辑器常开、窗口不动、一次只改一样、改完必须给截图、错了先还原。**

---

## 一、开工前的准备工作（不做完不许动手）

| # | 步骤 | 命令 | 通过标准 |
| --- | --- | --- | --- |
| 1 | 摆窗口 | `Tools\SetupLayout.ps1` | 编辑器 `0,0 1494×864`、内容浏览器 `0,870`、聊天 `1500,646` |
| 2 | 起编辑器（**仅当没开时**） | `Tools\EditorGuard.ps1 -Action restart` | 等到 `MCP server is listening on 127.0.0.1:8000` |
| 3 | 自检 | `Tools\EditorGuard.ps1 -Action check` | 输出 `CHECK: healthy` |

**做完这三步再谈任务。**

---

## 二、绝对不许做的四件事

| # | 禁止 | 原因 |
| --- | --- | --- |
| 1 | **关编辑器** | 人在看画面，关掉就看不见了 |
| 2 | **改窗口尺寸/位置** | 人是按固定布局看画面的（2026-11-23 犯过一次，被明确批评） |
| 3 | **用 `Tools\RunGame.ps1`** | **它第 144 行会 `Stop-Process` 掉编辑器再起游戏** —— 这就是"编辑器老被关"的真凶 |
| 4 | **一次改好几样** | 材质+布景+光照一起改，出问题查不出是谁的锅 |

---

## 三、正确的验证链路（全程不碰编辑器）

```powershell
# 1. 编辑器内重建关卡（不关编辑器）
powershell -ExecutionPolicy Bypass -File Tools\RebuildInEditor.ps1

# 2. 编辑器内起 PIE（要传 options，可以为空）
'{"options":{}}' | Set-Content Saved\mcp_args.json -Encoding ASCII
powershell -ExecutionPolicy Bypass -File Tools\mcp.ps1 `
    -Toolset "EditorToolset.EditorAppToolset" -Tool "StartPIE" `
    -ArgsFile "Saved\mcp_args.json" -OutFile "Saved\mcp_probe.txt"

# 3. 读游戏内玩家坐标（决定性证据）
Select-String -Path Saved\Logs\LingXuJie.log -Pattern 'Player ready at'

# 4. 停 PIE（不停掉就重建不了关卡）
'{"options":{}}' | Set-Content Saved\mcp_args.json -Encoding ASCII
powershell -ExecutionPolicy Bypass -File Tools\mcp.ps1 `
    -Toolset "EditorToolset.EditorAppToolset" -Tool "StopPIE" `
    -ArgsFile "Saved\mcp_args.json" -OutFile "Saved\mcp_probe.txt"
```

**MCP 读引擎日志（不要打开「消息日志」窗口）：**

```powershell
'{"category":"","pattern":"LingXuJie","maxEntries":20}' | Set-Content Saved\mcp_args.json -Encoding ASCII
powershell -ExecutionPolicy Bypass -File Tools\mcp.ps1 `
    -Toolset "EditorToolset.LogsToolset" -Tool "GetLogEntries" `
    -ArgsFile "Saved\mcp_args.json" -OutFile "Saved\mcp_log.txt"
```

| 参数 | 含义 |
| --- | --- |
| `category` | 留空 = 全部类别；也可填 `LogTemp` / `LogPython` 等 |
| `pattern` | **必填**，正则 |
| `maxEntries` | 从日志末尾取几条，默认 1000 |

**「消息日志 / Message Log」窗口会挡住视口、打断自动化点击 —— 没有任何理由打开它。**

**MCP 截图（干净、无 UI 遮挡）：**

```powershell
'{"captureTransform":{"location":{"x":..,"y":..,"z":..},"rotation":{"pitch":..,"yaw":..,"roll":0}},"annotations":{"showLabels":false}}' | Set-Content Saved\mcp_args.json -Encoding ASCII
powershell -ExecutionPolicy Bypass -File Tools\mcp.ps1 `
    -Toolset "EditorToolset.EditorAppToolset" -Tool "CaptureViewport" `
    -ArgsFile "Saved\mcp_args.json" -OutFile "Saved\mcp_raw.txt"
Copy-Item Saved\mcp_raw.txt Saved\mcp_raw.json -Force
python Tools\mcp_capture.py Saved\mcp_raw.json Saved\shot.png
```

**MCP 工具的两个参数坑：**

| 工具 | 必须参数 |
| --- | --- |
| `CaptureViewport` | **`captureTransform` + `annotations`** 两个都要，少一个报 `needs a default value` |
| `StartPIE` / `StopPIE` | **`options`**，传 `{}` 即可 |

---

## 四、工作节奏（一次一个块）

```
说清这一步改什么、预期看到什么
  → 改一处
  → RebuildInEditor
  → 读日志确认
  → MCP 截图
  → 一句话结论 + 图片
  → 问下一步
```

**不要一口气改完再解释。不要"顺手"多改一样。**

---

## 五、出问题时（这条最重要）

1. **先还原到上一个可用状态**，不要在上一步的基础上继续瞎调。
2. **用证据定位，不要猜**：
   - 看 `Saved\Logs\LingXuJie.log` 里的 `[LingXuJie]` 行
   - 看 `Player ready at V(...)` 这类引擎自己打的坐标
   - 读 `Source/LingXuJie/*.cpp` 的相关函数
3. **同一个问题连试两次没成就停下**，把已知事实列出来重新推。
4. **不确定就问一句**，尤其涉及"要不要关编辑器 / 改方向 / 花时间"。

---

## 六、地图复刻的技术坑（已踩过，别再踩）

### 地形

| # | 坑 | 症状 | 正确做法 |
| --- | --- | --- | --- |
| 1 | **OBJ 没 UV** | 网格导入成功但**三角面为 0** | 导出的 OBJ 必须带 `vt`，面写 `f v/vt` |
| 2 | **三角形绕序反了** | 地形碎成漂浮板块 | 从上方看逆时针：`f a-b-c` / `f b-d-c` |
| 3 | **导入器把 Y 取反** | 网格跑到 `Y = -51200..0` | 出生点要放在**负 Y** 侧 |
| 4 | **资产已存在时导入被跳过** | 改了 OBJ 但面数/形状不变 | **导入前先 `delete_asset`** |
| 5 | **Nanite 网格不提供碰撞** | 角色穿地掉到 Z=0，游戏里只剩天空 | **用 `StaticMeshEditorSubsystem.set_nanite_settings()` 关 Nanite**；只改 `nanite_settings.enabled` **不触发重建，无效** |
| 6 | **多个 PlayerStart** | 角色生在旧坐标 | 建之前先销毁所有 `PlayerStart` 和 `MX_` 前缀的演员 |

### 贴图

| # | 坑 | 症状 | 正确做法 |
| --- | --- | --- | --- |
| 7 | **客户端 DDS 头 UE 不认** | `DXGIFormat不支持：71 : BC1_UNORM` | **先转 PNG 再导入**（PIL 可读） |
| 8 | **平铺过密** | 看出规则网格 | 降低重复次数 / 混第二种图块 |
| 9 | **陡坡贴图拉伸** | 垂直面被拉长 | 需要三向投影（triplanar） |

### 编辑器内重建

| # | 坑 | 症状 | 正确做法 |
| --- | --- | --- | --- |
| 10 | **Python 模块被缓存** | 改了代码但行为不变 | `build_level.py` 里 `importlib.reload(sys.modules["..."])` |
| 11 | **PIE 开着时建不了关卡** | `new_level -> False` | 先 `StopPIE` |
| 12 | **`log()` 定义前调用** | `NameError`，整个脚本静默失败 | import 阶段的日志等 `log` 定义后再打 |

---

## 七、坐标约定（墨香 ↔ UE）

| 项 | 值 |
| --- | --- |
| 墨香世界 | `51200 × 51200` cm，**Y 是高度** |
| UE 轴向 | **Z 是高度** |
| 导出 OBJ 时 | 写 `(X, Y, 高度)` —— 即 UE 的 `(X, Y, Z)` |
| **导入后** | **UE 把 Y 取反** → 网格落在 `Y = -51200..0` |
| 出生点 | 世界 `Y` 必须是**负数** |
| 比例 | **1:1**，墨香 1 cm = UE 1 cm |

**查高度用：** `moxiang-study/terrain/<地图号>.hfl.csv`（513×513，单位 cm）。

---

## 八、当前进度快照（2026-11-26）

| 项 | 状态 |
| --- | --- |
| 关卡内容 | 天空 + 墨香 22 号图真实地形 + 原版草地材质 + 出生点 = **13 actors** |
| 地形 | ✅ 52 万面完整导入，角色站得住（日志 `Z=3477`） |
| 地面材质 | ✅ `tile_104_grass01` 平铺 96 次 |
| 待办 | 平铺重复感、陡坡拉伸、建筑、灯光 |
| **旧 P0 世界** | **已清空**（`p0_world.json` 和 `build_level.py` 里的旧函数仍在，可随时恢复） |

---

## 九、命令速查

```powershell
Tools\SetupLayout.ps1                              # 摆窗口
Tools\EditorGuard.ps1 -Action check                # 自检
Tools\RebuildInEditor.ps1                          # 编辑器内重建（常用）
Tools\mcp.ps1 -Top "list_toolsets"                 # 列 MCP 工具集
python Tools\mcp_capture.py <raw.json> <out.png>   # 从 MCP 结果里取出图片
```

**永远别用的：** `Tools\RunGame.ps1`（杀编辑器）、`Tools\BuildAll.ps1`（要关编辑器）。
