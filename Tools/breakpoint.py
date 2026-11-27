"""Print the handoff card for the current breakpoint.

The card exists so that starting a fresh conversation does not depend on anyone remembering what was
in flight. It reads the newest section of the handoff document - the one with the highest number -
and prints where the work stands, what was verified, and what comes next, in a shape that can be
pasted into a new conversation as its opening message.

Because it reads the document rather than the conversation, it produces the same answer whatever
the context looks like, including from a session that has only just started.

    python Tools/breakpoint.py
"""

import os
import re
import subprocess

DOC = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"


def latest_section(lines):
    starts = []
    for index, line in enumerate(lines):
        match = re.match(r"^## (\d+)\.\s*(.+?)\s*$", line)
        if match:
            starts.append((int(match.group(1)), index, match.group(2)))
    if not starts:
        return None
    starts.sort()
    number, begin, title = starts[-1]
    end = len(lines)
    for other_number, other_index, _ in starts:
        if other_index > begin:
            end = other_index
            break
    return number, title, lines[begin:end]


def main():
    if not os.path.exists(DOC):
        print("missing %s" % DOC)
        return 1
    with open(DOC, encoding="utf-8") as handle:
        lines = handle.read().split("\n")
    section = latest_section(lines)
    if section is None:
        print("no numbered section found")
        return 1
    number, title, body = section

    print("=" * 60)
    print("断点卡片  |  NEXT-SESSION.md 第 %d 节：%s" % (number, title))
    print("=" * 60)
    for line in body[1:]:
        stripped = line.rstrip()
        if stripped:
            print(stripped)

    try:
        log = subprocess.run(
            ["git", "-C", os.path.dirname(os.path.dirname(DOC)), "log",
             "-1", "--oneline"],
            capture_output=True, text=True, timeout=30)
        if log.returncode == 0 and log.stdout.strip():
            print("")
            print("最近提交： " + log.stdout.strip())
    except (OSError, subprocess.SubprocessError):
        pass

    print("")
    print("新会话开场指令（复制即可）：")
    print("  先读 AGENTS.md 和 Docs/MAP-RECONSTRUCTION-SOP.md，"
          "再读 Docs/NEXT-SESSION.md 第 %d 节，从那里接着做。" % number)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
