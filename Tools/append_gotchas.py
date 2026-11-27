"""Append the gotchas found in this session to the shared list.

Writing through Python because the file is UTF-8 Chinese and PowerShell 5.1 mangles both the
content and the inline quoting. Each entry follows the existing shape: symptom, root cause,
fix, source.
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-Gotchas.md"

ENTRIES = """
## 65. `CaptureViewport` 的 `captureTransform` 不改编辑器视口相机 —— 截图好看，人的屏幕还是黑的

- **症状**：用 MCP `EditorAppToolset.CaptureViewport` 带 `captureTransform` 截图，
  出来的图是漂亮的兰州街景；但人切到编辑器，视口里还是建筑内部一片黑。
- **根因**：`captureTransform` 只对**那一次渲染**生效，它创建一个临时相机拍一张图，
  **完全不移动编辑器视口相机**。两次犯同一个错，都是拿截图当"视口已恢复"的证据。
- **修法**：真正移动相机的是编辑器子系统：
  ```python
  subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
  subsystem.set_level_viewport_camera_info(location, rotation)
  # 读回来确认
  loc, rot = subsystem.get_level_viewport_camera_info()
  ```
  已封装 `Tools/reset_view.py`，用 `RebuildInEditor.ps1 -Script Tools/reset_view.py` 调用。
- **验证也要换**：`Tools/grab_editor_window.py` 走 Windows API 直接抓编辑器窗口，
  **看到的就是人看到的**。MCP 渲染的图不能用来证明"视口是什么样"。
- **出处**：2026-11-26，兰州城做图；`AGENTS.md` 规则 3b

## 66. PowerShell 把目录名里的 `[Server]` 当成通配符字符集 —— 明明有文件却报"0 个"

- **症状**：`Get-ChildItem '源码\[Server]Agent'` 报 0 个文件，但源码里明明有 55 个。
- **根因**：PowerShell 路径里的方括号是**字符集通配符**，`[Server]Agent` 表示
  「S/e/r/v/e/r 中任一字符 + Agent」，所以它去找 `SAgent`、`eAgent`… 而真实目录叫 `[Server]Agent`。
- **修法**：查这类目录一律用 `-LiteralPath`：
  ```powershell
  Get-ChildItem -LiteralPath '源码\[Server]Agent'
  ```
  或者干脆用 Python 的 `os.walk` / `os.listdir`（没有通配符语义）。
- **教训**：任何带 `[ ] * ?` 的路径都要当心。这个坑让我误判"服务端源码是空的"，
  差点得出完全错误的结论。
- **出处**：2026-11-26，查台服源码的服务端目录

## 67. PIE 开着时 `new_level` 返回 False，重建报 `Could not create or load`

- **症状**：`build_level.py` 执行到 `new_level` 返回 `False`，
  `RuntimeError: Could not create or load /Game/Maps/LingXuJie`。
- **根因**：PIE（Play In Editor）运行时关卡处于被占用状态，不能新建/替换。
- **修法**：重建前先 MCP `StopPIE`（`EditorAppToolset.StopPIE`，参数传 `{}`）。
- **注意**：这个错在 `AGENTS.md` 规则 8 里写过，但实际执行时还是会忘 ——
  **重建脚本应该在开头自己检查并 StopPIE**，不要指望调用者记得。
- **出处**：2026-11-26，兰州城重建；`AGENTS.md` 规则 8

## 68. 墨香 OBJ 的坐标：导出写 `(x, z, height)`，UE 导入会**取反 Y**

- **症状**：按 OBJ 文件里的坐标去摆相机，永远对不上城市的位置；按顶点范围算出来的"城中心"
  在引擎里是空地，算出来的"空地"是建筑内部。
- **根因**：`Tools/build_map_obj.py` 把墨香坐标 `(wx, wy, height)` 写成 OBJ 的
  `v wx wy height`，但**墨香是 Z 向上、UE 是 Z 向上但 Y 取反** ——
  UE 的 OBJ 导入器会把 OBJ 的 Y 变成 `-Y`。
  所以：**OBJ 里 Y 为正的区域 → 引擎里 Y 为负。**
- **修法**：读 OBJ 算位置时，最后输出 UE 坐标要 `y_ue = -y_obj`。
  `Tools/find_open_spot.py` 就是栽在这里，第二轮才修正。
- **记忆点**：墨香地图 51,200 cm 见方；地形 Y 在 UE 是 `-51200..0`；
  兰州建筑 OBJ Y 是 `0..46000` → UE `-46000..0`。
- **出处**：2026-11-26，兰州城定位
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 65." in text:
        print("already appended")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(ENTRIES)
    count = text.count("\n## ") + ENTRIES.count("\n## ")
    print("appended 4 entries; the file now holds %d" % count)


if __name__ == "__main__":
    main()
