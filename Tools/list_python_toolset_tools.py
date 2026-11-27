"""List every tool the shipped Python toolsets expose, with its signature and summary.

Sixteen toolsets turned up after the Toolset Registry loaded, and none of them were known about
before. Reading their source is faster than probing the server, and it gives the docstrings,
which say what each tool is for rather than just its name.

The point is to stop writing tools that already exist. Anything here is a capability available
today with no code to maintain.

    python Tools/list_python_toolset_tools.py [toolset_name ...]
"""

import os
import re
import sys

TOOLSETS_DIR = (
    r"C:\Program Files\Epic Games\UE_5.8\Engine\Plugins\Experimental\Toolsets"
    r"\EditorToolset\Content\Python\editor_toolset\toolsets"
)


def summarise(path):
    """Pull out each tool: its name, signature and first docstring line."""
    text = open(path, encoding="utf-8", errors="replace").read()
    tools = []

    # A tool is a static method carrying the tool_call decorator.
    pattern = re.compile(
        r"@toolset_registry\.tool_call[^\n]*\n(?:\s*@[\w.]+\n)*\s*@staticmethod\s*\n"
        r"\s*def\s+(\w+)\s*\(([^)]*)\)\s*(?:->\s*([\w\[\], .]+))?\s*:\s*\n"
        r"\s*(?:'''|\"\"\")(.*?)(?:'''|\"\"\")",
        re.S)

    for match in pattern.finditer(text):
        name, args, returns, doc = match.groups()
        first = " ".join(doc.split())[:110]
        tools.append((name, " ".join(args.split())[:70], (returns or "").strip(), first))
    return tools


def main():
    wanted = sys.argv[1:]
    files = sorted(f for f in os.listdir(TOOLSETS_DIR) if f.endswith(".py"))
    total = 0

    for filename in files:
        stem = filename[:-3]
        if stem in ("__init__", "blueprint_dsl", "blueprint_layout", "blueprint_node"):
            continue
        if wanted and stem not in wanted:
            continue
        path = os.path.join(TOOLSETS_DIR, filename)
        tools = summarise(path)
        if not tools:
            continue
        total += len(tools)
        print("=" * 78)
        print("%s   %d tools" % (stem, len(tools)))
        print("")
        for name, args, returns, doc in tools:
            print("  %-32s -> %s" % (name, returns or "void"))
            if args:
                print("      args: %s" % args)
            if doc:
                print("      %s" % doc)
        print("")

    print("total tools across shipped Python toolsets: %d" % total)


if __name__ == "__main__":
    main()
