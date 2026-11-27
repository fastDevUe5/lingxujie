"""Add gotcha 107 recording the Message Log rule and the two mistakes made adding it.

The person asked for the Message Log to stop covering the viewport and for that to be handled without
repeated reminders. The durable fix is the layout script, not a promise. Getting there produced two
errors worth recording because both are shapes I have hit before.

    python Tools/add_msglog_gotcha.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-Gotchas.md"

ENTRY = """
## 107. 「消息日志」窗口会遮挡视口 —— `SetupLayout.ps1` 现在自动最小化它

- **要求**：人明确说过，消息日志窗口要最小化/关闭，不要遮挡，**并且不要反复提醒他**
- **做法**：不是靠每次记住，而是写进 `Tools/SetupLayout.ps1` ——
  它本来就在摆窗口，顺手把遮挡视口的窗口最小化
- **判定方式：按**矩形重叠**，不按标题**
  ```powershell
  # 属于本编辑器进程、未最小化、矩形与编辑器重叠、且不在编辑器下方（内容浏览器在下方）
  bool overlaps = r.L < keep.Rt && r.Rt > keep.L && r.T < keep.B && r.B > keep.T;
  ```
  **因为 `SetupLayout.ps1` 必须保持纯 ASCII**（PowerShell 5.1 把无 BOM UTF-8 当 ANSI），
  不能直接匹配中文标题 `消息日志`
- **验证**：先手动恢复消息日志 → 跑 `SetupLayout.ps1` → 输出
  ```
  overlay      -> 1 overlapping window(s) minimised
  ```
- **写这段时犯的两个错（都是老毛病）**：
  1. **在 .ps1 里写了中文** —— 违反该文件自己第一条注释
     「keep this file ASCII-only」，`Find('消息日志')` 匹配不到，那行静默没执行
  2. **检查写成了 `if "GetWindowThreadProcessId" in text`** ——
     匹配到了**使用处**而不是**声明**，于是误判「已声明」，
     `Add-Type` 因为缺 `DllImport` 而编译失败
- **教训**：
  - **「已经存在」的检查要匹配**特征的完整形态**，不能只匹配子串**
  - **文件头部写着约束时，先读约束再动手**
- **出处**：2026-11-26，消息日志遮挡
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 107." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(ENTRY)
    print("added gotcha 107")


if __name__ == "__main__":
    main()
