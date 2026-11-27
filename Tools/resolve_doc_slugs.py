"""Resolve the documentation slugs this learning plan needs, using the miss signature from the negative control.

A miss returns HTTP 200 with no <title> and a short body. That signature is reliable and was confirmed
against an invented slug. This walks a candidate list built from real search results plus both suffix
variants, and prints the ones that actually resolve so the mirror script can be corrected from evidence.

    python Tools/resolve_doc_slugs.py
"""

import re
import urllib.error
import urllib.request

BASE = "https://dev.epicgames.com/documentation/en-us/unreal-engine/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
TITLE = re.compile(r"<title>(.*?)</title>", re.S)

# topic -> candidate slugs, best guess first. Suffixes are tried too.
TOPICS = {
    "nanite": ["nanite-virtualized-geometry-in-unreal-engine", "nanite-virtualized-geometry", "nanite"],
    "nanite-technical": ["nanite-technical-details", "nanite-technical-details-in-unreal-engine"],
    "lumen-technical": ["lumen-technical-details-in-unreal-engine", "lumen-technical-details"],
    "lumen-performance": ["lumen-performance-guide-for-unreal-engine", "lumen-performance-guide"],
    "niagara": ["creating-visual-effects-in-niagara-for-unreal-engine",
                "niagara-visual-effects-in-unreal-engine", "niagara-visual-effects"],
    "umg": ["umg-ui-designer-user-guide", "umg-ui-designer", "umg-ui-designer-quick-start"],
    "animation": ["skeletal-mesh-animation-system", "animation-system-in-unreal-engine",
                  "skeletal-mesh-animation-system-in-unreal-engine"],
    "physics": ["physics-simulation-in-unreal-engine", "physics-simulation",
                "physics-overview-in-unreal-engine"],
    "materials": ["material-editor-in-unreal-engine", "material-editor", "unreal-engine-materials"],
    "static-mesh-lod": ["static-mesh-lod-generation-in-unreal-engine", "static-mesh-lod-generation"],
    "import": ["importing-static-meshes-in-unreal-engine", "importing-static-meshes"],
    "lighting": ["lighting-basics-in-unreal-engine", "lighting-basics"],
    "landscape": ["landscape-technical-guide-in-unreal-engine", "landscape-technical-guide"],
    "world-partition": ["world-partition-in-unreal-engine", "world-partition"],
    "post-process": ["post-process-materials-in-unreal-engine", "post-process-materials"],
    "asset-management": ["asset-management-in-unreal-engine", "asset-management"],
    "command-line": ["unreal-engine-command-line-arguments", "command-line-arguments"],
    "level-editor": ["level-editor-in-unreal-engine", "level-editor"],
    "instanced-materials": ["instanced-materials-in-unreal-engine", "instanced-materials"],
    "fbx-pipeline": ["fbx-static-mesh-pipeline-in-unreal-engine", "fbx-static-mesh-pipeline"],
}


def fetch_title(slug):
    url = BASE + slug
    request = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            text = response.read(120000).decode("utf-8", errors="replace")
    except urllib.error.HTTPError as error:
        return None, "http %d" % error.code
    except Exception as error:  # noqa: BLE001
        return None, repr(error)[:40]

    match = TITLE.search(text)
    if not match:
        return None, "no title (miss signature)"
    title = match.group(1).strip()
    if "|" not in title:
        return None, "generic title"
    return title, "ok"


def main():
    resolved = {}
    for topic, candidates in TOPICS.items():
        found = None
        for slug in candidates + [c + "-in-unreal-engine" for c in candidates]:
            title, reason = fetch_title(slug)
            if title:
                found = (slug, title)
                break
        if found:
            resolved[topic] = found
            print("%-20s %-52s %s" % (topic, found[0], found[1][:56]))
        else:
            print("%-20s %-52s %s" % (topic, "(none)", reason if 'reason' in dir() else "not found"))

    print("")
    print("resolved %d of %d topics" % (len(resolved), len(TOPICS)))
    print("")
    print("PAGES = {")
    for topic, (slug, _title) in resolved.items():
        print('    "%s": "%s",' % (slug, topic))
    print("}")


if __name__ == "__main__":
    main()
