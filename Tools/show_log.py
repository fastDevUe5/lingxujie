"""Pull the LingXuJie lines out of an MCP log response.

The reply is JSON wrapped in the harness's own envelope, and quoting it inline in PowerShell
mangles both the escaping and the Chinese characters. Reading it from a file avoids the shell
entirely.

    python Tools/show_log.py Saved/mcp_log.txt
"""

import json
import re
import sys


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "Saved/mcp_log.txt"
    raw = open(path, encoding="utf-8", errors="replace").read()

    lines = []
    try:
        payload = json.loads(raw)
        stack = [payload]
        while stack:
            node = stack.pop()
            if isinstance(node, dict):
                for key in ("text", "message", "line"):
                    value = node.get(key)
                    if isinstance(value, str) and value.strip():
                        lines.append(value)
                stack.extend(node.values())
            elif isinstance(node, list):
                stack.extend(node)
    except (json.JSONDecodeError, ValueError):
        lines = [line for line in raw.split("\n") if "LingXuJie" in line]

    seen = []
    for line in lines:
        clean = line.replace("\r", "").strip()
        if clean and clean not in seen:
            seen.append(clean)
    for line in seen[-40:]:
        print(line[:200])


if __name__ == "__main__":
    main()
