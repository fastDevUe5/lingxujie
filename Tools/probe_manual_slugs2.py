"""Probe documentation slugs by reading the page title rather than the byte count.

The previous probe called read(4000) and then treated 4000 bytes as success, which is the truncation
length rather than anything about the page. Every slug "resolved" because every response was at least
that long. A title tells you whether the page exists, and a known-bad slug gives the negative control.

    python Tools/probe_manual_slugs2.py
"""

import re
import urllib.error
import urllib.request

BASE = "https://dev.epicgames.com/documentation/en-us/unreal-engine/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

TITLE = re.compile(r"<title>(.*?)</title>", re.S)

CANDIDATES = [
    # A deliberately invented slug, to see what a miss looks like.
    "this-page-does-not-exist-at-all-xyz",
    # The three that are already mirrored, as positive controls.
    "scripting-the-unreal-editor-using-python",
    "unreal-mcp-in-unreal-editor",
    # The twelve that failed.
    "nanite-virtualized-geometry",
    "static-mesh-lod-generation",
    "importing-static-meshes",
    "fbx-static-mesh-pipeline",
    "material-editor",
    "instanced-materials",
    "landscape-technical-guide",
    "lighting-basics",
    "level-editor",
    "unreal-engine-command-line-arguments",
    "asset-management",
    "skeletal-mesh-animation-system",
    # And the ones this learning round wants.
    "lumen-technical-details-in-unreal-engine",
    "niagara-visual-effects",
    "physics-simulation",
    "umg-ui-designer-quick-start",
    "world-partition",
    "nanite",
]


def title_of(url):
    request = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            text = response.read(80000).decode("utf-8", errors="replace")
            match = TITLE.search(text)
            title = match.group(1).strip() if match else "(no title)"
            # The site marks misses by keeping the generic site title with no page name.
            has_body = "Lumen" in text or "Nanite" in text or len(text) > 50000
            return response.status, title[:78], has_body
    except urllib.error.HTTPError as error:
        return error.code, "(http error)", False
    except Exception as error:  # noqa: BLE001
        return "err", repr(error)[:60], False


def main():
    print("%-42s %-8s %-9s %s" % ("slug", "status", "has_body", "title"))
    print("-" * 130)
    for slug in CANDIDATES:
        code, title, body = title_of(BASE + slug)
        print("%-42s %-8s %-9s %s" % (slug[:42], code, body, title))


if __name__ == "__main__":
    main()
