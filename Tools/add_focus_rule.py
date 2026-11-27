"""Add rule 12 to AGENTS.md and gotcha 108: automation must never take focus.

The person works in other applications while this agent works in the editor. A SetForegroundWindow, a
cursor move, or a SendKeys breaks that independence, and each is easy to add by accident. The rule
belongs next to the other hard rules, and the reasoning belongs in the gotchas.

    python Tools/add_focus_rule.py
"""

AGENTS = "C:/Users/tk/Desktop/lingxujie/AGENTS.md"
GOTCHAS = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-Gotchas.md"

RULE = """
11b. **自动化绝不能抢焦点 —— 人在同时做别的事。**
   **人在左边跑编辑器、右边跟我对话，中间还可能切去别的窗口。
   我任何一次 `SetForegroundWindow`、移动鼠标、`SendKeys`，
   都会把人手上的操作打断。这是硬性要求，不是"尽量"。**

   **优先顺序（从上到下，能停在前一层就不要往下）：**

   | 优先 | 手段 | 为什么安全 |
   | --- | --- | --- |
   | **1** | **MCP 工具调用** | 跑在编辑器进程内，完全不碰窗口焦点 |
   | **2** | **UI Automation 按名字点按钮** | 不移动光标 |
   | **3** | **`PostMessage(WM_CLOSE)`** | 关对话框不需要点，也不激活 |
   | **4** | **`SetWindowPos` + `SWP_NOACTIVATE`** | 移动/改大小不抢焦点 |
   | 5 | 坐标点击 | **仅当 1–4 全失败**，且日志里要明说 |

   **已修好的（2026-11-26）：**
   - `SetupLayout.ps1`：删掉 `SetForegroundWindow`，改用 `SWP_NOACTIVATE`；
     清理遮挡窗口从 `SW_MINIMIZE` 改为 `SW_HIDE`（后者不激活任何窗口）
   - `EditorGuard.ps1`：关崩溃报告器/恢复包，改成先 `PostMessage(WM_CLOSE)`，
     坐标点击只在 WM_CLOSE 无效时兜底

   **自查命令：**
   ```powershell
   python Tools/audit_focus.py
   ```
   **它会列出所有 `SetForegroundWindow` / `mouse_event` / `SendKeys` 的**调用**（自动排除 DllImport 声明）。
   新增脚本后跑一次。**
"""

GOTCHA = """
## 108. 自动化抢焦点会打断人 —— 优先 MCP，不用鼠标

- **要求**：人会在左侧编辑器/右侧对话之外还切去别的窗口做事。
  **agent 的自动化一旦抢焦点，人的操作就被打断。**
- **我自己犯过的**：
  - 用 `mouse_event` 点「恢复包」对话框 —— **真的移动了人的鼠标**
  - `SetupLayout.ps1` 里 `SetForegroundWindow($editor)` —— **每次跑都抢焦点**
  - 清理遮挡窗口用 `SW_MINIMIZE` —— 把焦点交给了下一个窗口
- **正确顺序**：

  | 优先 | 手段 | 为什么安全 |
  | --- | --- | --- |
  | 1 | **MCP 工具调用** | 跑在编辑器进程内，不碰焦点 |
  | 2 | UI Automation 按名字点 | 不动光标 |
  | 3 | `PostMessage(WM_CLOSE)` | 关对话框不必点击 |
  | 4 | `SetWindowPos` + `SWP_NOACTIVATE` | 移动不抢焦点 |
  | 5 | 坐标点击 | 仅最后手段 |

- **已修**：
  - `SetupLayout.ps1` 删掉 `SetForegroundWindow`，`Place()` 改 `SWP_NOACTIVATE`，
    遮挡窗口清理改 `SW_HIDE`
  - `EditorGuard.ps1` 加 `PostClose()`（`PostMessage` + `WM_CLOSE`），
    两个对话框关闭都先走它
- **验证**：跑 `SetupLayout` / `EditorGuard check` / `EditorGuard dismiss` 后，
  **前台窗口仍是原来那个**（实测三次都是聊天窗口）
- **自查**：`python Tools/audit_focus.py`
- **写审计脚本时又犯了同一个错**：`name + "("` 也匹配到
  `DllImport ... extern bool name(` **声明**，于是把已修好的文件报成有问题。
  **修：跳过含 `DllImport` / `extern` 的行**
- **教训**：**「匹配到名字」不等于「匹配到调用」。**
  和 #107 里那两次是同一类：**检查的是子串，不是语义**
- **出处**：2026-11-26，焦点问题
"""


def main():
    agents = open(AGENTS, encoding="utf-8").read()
    if "11b." in agents:
        print("rule already present")
    else:
        anchor = "11. **人手动创建的文件，一律不许动"
        if anchor in agents:
            agents = agents.replace(anchor, RULE.strip() + "\n\n" + anchor, 1)
            open(AGENTS, "w", encoding="utf-8").write(agents)
            print("rule 11b added")
        else:
            print("anchor for rule not found")

    gotchas = open(GOTCHAS, encoding="utf-8").read()
    if "## 108." in gotchas:
        print("gotcha already present")
    else:
        with open(GOTCHAS, "a", encoding="utf-8") as handle:
            handle.write(GOTCHA)
        print("gotcha 108 added")

    agents = open(AGENTS, encoding="utf-8").read()
    agents = agents.replace("（**107 条**）", "（**108 条**）")
    agents = agents.replace("新增的 #28–#107", "新增的 #28–#108")
    open(AGENTS, "w", encoding="utf-8").write(agents)
    print("count synced to 108")


if __name__ == "__main__":
    main()
