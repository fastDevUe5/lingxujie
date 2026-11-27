"""List the tool names the shipped EditorAppToolset declares.

The console path stopped running scripts partway through this session, so a tool that can
execute Python or drive the console reliably would be the way out. The names live in the plugin's
own source, which is a better place to look than guessing against the live server.

    python Tools/list_mcp_tools.py
"""

import glob
import os

PLUGINS = r"C:\Program Files\Epic Games\UE_5.8\Engine\Plugins\Experimental"


def main():
    files = glob.glob(os.path.join(PLUGINS, "**", "*EditorAppToolset*"), recursive=True)
    if not files:
        print("no EditorAppToolset files found under %s" % PLUGINS)
        return

    for path in files:
        print("=== %s" % os.path.relpath(path, PLUGINS))
        text = open(path, encoding="utf-8", errors="replace").read()
        for line in text.splitlines():
            stripped = line.strip()
            lowered = stripped.lower()
            if ("tool" in lowered or "command" in lowered or "python" in lowered) and "(" in stripped:
                if len(stripped) < 160:
                    print("   ", stripped)
        print("")


if __name__ == "__main__":
    main()
