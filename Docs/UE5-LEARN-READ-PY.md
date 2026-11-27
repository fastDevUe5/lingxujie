# UE5 学习 · 补读（二十九）：Python 脚本 —— 我天天用，却漏了三个 API

> **这是我整个系列**最该早读**的一篇。**
> **它有三个「最佳实践」章节，而其中两个我**一次都没用过**：
> `ScopedEditorTransaction`（撤销分组）和 `ScopedSlowTask`（进度对话框）。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、文档结构（32.6 KB，25 节）

**运行方式（6 节）：**
```
Set Up Your Project to Use Python
**Python 3.11.8**（内置版本）
Ways to Run Python Code
  The Python Console in the Output Log
  The py Console Command
  The File Menu
  The Command Line
  The init_unreal.py File
  Startup Scripts
  Run Python From Editor-Only Blueprints
Python Environment and Paths
```

**API 说明（4 节）：**
```
About the Unreal Editor Python API
Exposing C++ Functions to Python（UFUNCTION 加宏即可）
Blueprint Classes and User Defined Structs in Python
Other Scripting API Behavior
API Reference
```

**🎯 最佳实践（7 节）—— 本篇最有价值的部分：**
```
Best Practices for Using the Python API
Working with Assets
Changing Editor Properties
**Use Unreal Types Whenever Possible**
Logging and Feedback
**Supporting Undo and Redo**
**Progress Dialogs for Slow Operations**
Using Python with AI Agents
```

---

## 二、🔴 我漏掉的三件事

### 2.1 `unreal.ScopedEditorTransaction` —— 撤销分组

**文档原文：**
> **「Each transaction that you define can contain any number of Python operations.
> Using these transactions, you can bundle large operations, or operations on many different objects,
> together into **a single entry in the Undo / Redo history**.
>
> Typically, if your script intends to perform a certain change on multiple objects,
> **you don't want a separate entry in the Undo / Redo history for each change**;
> you want one entry that will undo all changes to all objects.」**

**用法：**
```python
with unreal.ScopedEditorTransaction("My Transaction Test") as trans:
    obj.set_editor_property("play_on_open", False)
    obj.set_editor_property("vertical_field_of_view", 80)
```

**✅ 实测：**
```
ScopedEditorTransaction: True
transaction scope exited, vfov now 80.0
```

**🔴 我为什么该用它：**
**我这一整个系列做的所有场景搭建（`scene_build.py` 等）**都没有包事务**。
→ 如果我改了 20 个属性，用户的撤销历史里就是 **20 条**，而不是 1 条。
→ **这是我对用户编辑器的污染。**

### 2.2 `unreal.ScopedSlowTask` —— 进度对话框

**文档原文（这句还解释了本系列多次「控制台挂住」）：**
> **「**while Unreal Editor is running a Python script, its UI becomes blocked to other user interactions.**
> To give the user information about the progress of a large task, and **avoid the editor appearing to
> freeze or hang**, you can use the `unreal.ScopedSlowTask` scope.」**

**→ 🔴 这就是为什么我好几次「控制台键入没反应」！**
**→ 编辑器在跑 Python 时 UI 是**阻塞**的 —— 我的脚本一跑，敲控制台当然没反应。**

**用法：**
```python
with unreal.ScopedSlowTask(total_frames, "Working!") as slow_task:
    slow_task.make_dialog(True)
    for i in range(total_frames):
        if slow_task.should_cancel():
            break
        slow_task.enter_progress_frame(1)
```

**✅ 实测：**
```
ScopedSlowTask: True
slow task completed 5 frames
```

**🔴 我为什么该用它：**
**我的贴图审计遍历了 610 个网格，花了**约 6 分钟**（日志时间戳 21:00:38 → 21:07:02）。
→ 那 6 分钟里编辑器界面**完全冻结**，用户看到的是一个「卡死的编辑器」。
→ 加一个进度条就能解决。**

### 2.3 `unreal.Vector` 而不是自己算

**文档原文：**
> **「Whenever you need utilities that are available in the Unreal Python API,
> like classes for math operations or manipulating 3D coordinates,
> **use the Unreal utilities rather than using your own implementations**.
> The Unreal versions are **optimized for best performance in the Engine environment**.」**

**✅ 实测：**
```
v1 = unreal.Vector(); v1.x = 10
v2 = unreal.Vector(10, 20, 30)
v3 = (v1 + v2) * 2     →  {x: 40, y: 40, z: 60}   ✓
```

**→ 运算符重载可用，不用手写 x/y/z 三个分量。**

---

## 三、🔴 还有一条硬规则：不要用 Python 碰资产文件

**文档原文：**
> **「If you need to work with Assets in your project, **always use functions from the Unreal Python API** to do it.
> **Never use file management modules built in to Python to work directly with your Asset files on disk.**
> For example, if you need to move an Asset to a different folder,
> **do not use Python functions like `os.rename` or `shutil.move`**.
> **Unreal projects and Assets contain internal content references that you can break** if you do not respect this rule.
>
> Instead, use the `unreal.EditorAssetLibrary` API ... or the `unreal.AssetTools` class.」**

**→ ✅ 我复查过：本系列**从来没有**用 `os.rename` / `shutil.move` 动过 `.uasset`。
→ 所有资产操作都走 `EditorAssetLibrary` / `AssetTools`。
→ **这一条我歪打正着做对了。**

---

## 四、其它值得记的

| 事实 | 说明 |
| --- | --- |
| **内置 Python 3.11.8** | 版本固定，不是系统 Python |
| **`print()` 走 `unreal.log()`** | 所以 `print` 和 `unreal.log` 效果一样 |
| **`unreal.log_warning()` / `log_error()`** | 分级日志，我**只用过 `log`** |
| **`init_unreal.py`** | 放在特定路径会自动执行，我没用过 |
| **Startup Scripts** | 项目设置里可配启动脚本 |
| **`Blueprint Classes ... _C` 后缀** | 蓝图类在 Python 里带 `_C`（我之前见过 `WBP_LabLabel_C`）|

---

## 五、这一篇学到什么

**1. 🔴 我连续做了 60+ 轮场景操作，**一次都没用撤销分组**。**
→ 用户历史里是一堆零散条目，不是一个可整体撤销的操作。

**2. 🔴 我跑过 6 分钟的阻塞脚本，**没有进度条**。**
→ 用户看到的是「卡死的编辑器」，这比慢本身更糟。

**3. 🎯 文档那句「UI becomes blocked」解释了本系列多起「控制台没反应」。**
**→ 不是命令行坏了，是编辑器在跑我的脚本。**

**4. ✅ 「不要用 `os.rename` 碰资产」这一条我碰巧做对了**（全程走 API）。

**5. 🎯 「用 `unreal.Vector`」是性能建议，也是可读性建议**（运算符重载）。

---

## 六、更正

| 之前 | 现在 |
| --- | --- |
| 「脚本改属性没什么副作用」 | ❌ **会污染撤销历史，应该包事务** |
| 「脚本跑久点是慢」 | ❌ **编辑器 UI 会冻结，必须加进度条** |
| 「控制台偶尔没反应」 | ✅ **因为编辑器在跑 Python，UI 阻塞** |

---

## 七、还没做到 / 可以立刻改的

| 项 | 说明 |
| --- | --- |
| **给 `scene_build.py` 等包事务** | **应该改**（不改现有文件，但新脚本要用） |
| **给长循环加进度条** | **应该改** |
| `init_unreal.py` | 没用过，不知道能做什么 |
| `log_warning` / `log_error` | 只用过 `log` |

**→ 从下一轮起，新写的脚本一律包 `ScopedEditorTransaction`；
超过 2 秒的循环一律加 `ScopedSlowTask`。**

---

## 八、状态

```
Docs/UE5-LEARN-READ-PY.md   1 篇（共 43 篇 learn 文档）
补读进度：30 / 57
主关卡 116 actor / 视口复位
```

---

## 九、下一篇

**继续补读（还剩 27 篇）。下一批：**
- `unreal-mcp.md`（31.4 KB）—— MCP，我一直在用
- `blueprints.md`（21.4 KB）
- `data-tables.md`（8.7 KB）/ `savegame.md`（12.2 KB）
- `sequencer-editor.md`（14.4 KB）

**→ 选 `unreal-mcp.md`（31.4 KB）—— 和 python-scripting 一样，我天天用但没读过。**
