"""Verify a full curriculum of documentation slugs before mirroring any of them.

Each topic carries candidate slugs, taken from web search results rather than invented. The site
answers HTTP 200 for missing paths too, so a candidate only counts when the response carries a page
title; the borrowed negative control is "this-page-does-not-exist-at-all-xyz".

    python Tools/verify_curriculum_slugs.py
"""

import re
import urllib.error
import urllib.request

BASE = "https://dev.epicgames.com/documentation/en-us/unreal-engine/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
TITLE = re.compile(r"<title>(.*?)</title>", re.S)
MISS = "this-page-does-not-exist-at-all-xyz"

# topic -> candidate slugs, in preference order. Suffix variants are tried automatically.
CURRICULUM = {
    # --- already mirrored, listed so the verification covers everything ---
    "python-scripting": ["scripting-the-unreal-editor-using-python"],
    "unreal-mcp": ["unreal-mcp-in-unreal-editor"],
    "nanite": ["nanite-virtualized-geometry-in-unreal-engine"],
    "nanite-technical": ["nanite-technical-details"],
    "lumen-technical": ["lumen-technical-details-in-unreal-engine"],
    "lumen-performance": ["lumen-performance-guide-for-unreal-engine"],
    "materials": ["unreal-engine-materials"],
    "import-static-meshes": ["importing-static-meshes-in-unreal-engine"],
    "landscape-technical": ["landscape-technical-guide-in-unreal-engine"],
    "world-partition": ["world-partition-in-unreal-engine"],
    "post-process-materials": ["post-process-materials-in-unreal-engine"],
    "asset-management": ["asset-management-in-unreal-engine"],
    "instanced-materials": ["instanced-materials-in-unreal-engine"],
    "fbx-static-mesh": ["fbx-static-mesh-pipeline-in-unreal-engine"],
    # --- newly resolved by search ---
    "umg-quick-start": ["umg-ui-designer-quick-start-guide-in-unreal-engine", "umg-ui-designer-user-guide"],
    "physics": ["physics-in-unreal-engine"],
    "static-mesh-lod": ["static-mesh-automatic-lod-generation-in-unreal-engine",
                        "static-mesh-lod-generation-in-unreal-engine"],
    "lighting-environment": ["lighting-the-environment-in-unreal-engine"],
    "audio-mixer": ["audio-mixer-overview-in-unreal-engine"],
    "networking": ["networking-overview-for-unreal-engine",
                   "networking-and-multiplayer-in-unreal-engine"],
    "blueprints": ["overview-of-blueprints-visual-scripting-in-unreal-engine"],
    "foliage": ["foliage-tool"],
    "water": ["water-system-in-unreal-engine"],
    "sky-atmosphere": ["sky-atmosphere-component-in-unreal-engine"],
    "virtual-shadow-maps": ["virtual-shadow-maps-in-unreal-engine"],
    "collision": ["collision-in-unreal-engine---overview", "collision-in-unreal-engine"],
    "animation-blueprints": ["animation-blueprints-in-unreal-engine"],
    "performance": ["introduction-to-performance-profiling-and-configuration-in-unreal-engine",
                    "performance-and-profiling"],
    # --- worth trying, unverified ---
    "reflections": ["reflections-in-unreal-engine", "reflections-environment-in-unreal-engine"],
    "temporal-super-resolution": ["temporal-super-resolution-in-unreal-engine"],
    "light-types": ["light-types-and-their-mobility-in-unreal-engine", "lighting-types-in-unreal-engine"],
    "material-expressions": ["material-expressions-in-unreal-engine"],
    "texture-editor": ["texture-editor-in-unreal-engine", "textures-in-unreal-engine"],
    "landscape": ["landscape-in-unreal-engine"],
    "navigation": ["navigation-system-in-unreal-engine"],
    "gameplay-framework": ["gameplay-framework-in-unreal-engine"],
    "game-mode": ["game-mode-and-game-state-in-unreal-engine", "agameplaymodemodule-in-unreal-engine"],
    "enhanced-input": ["enhanced-input-in-unreal-engine"],
    "control-rig": ["control-rig-in-unreal-engine"],
    "chaos-destruction": ["chaos-destruction-in-unreal-engine"],
    "sequencer": ["sequencer-in-unreal-engine", "real-time-compositing-with-sequencer-in-unreal-engine"],
}


def resolve(slug):
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
        return None, "no title"
    title = match.group(1).strip()
    if "|" not in title:
        return None, "generic title"
    return title, "ok"


def main():
    print("negative control: %r" % MISS, flush=True)
    control_title, control_reason = resolve(MISS)
    print("  -> %r %s" % (control_title, control_reason), flush=True)
    print("", flush=True)

    resolved = {}
    missing = []
    for topic, candidates in CURRICULUM.items():
        expanded = []
        for slug in candidates:
            expanded.append(slug)
            if not slug.endswith("-in-unreal-engine"):
                expanded.append(slug + "-in-unreal-engine")

        found = None
        for slug in expanded:
            title, reason = resolve(slug)
            if title:
                found = (slug, title)
                break

        if found:
            resolved[topic] = found
            print("%-28s %-58s %s" % (topic, found[0], found[1][:52]), flush=True)
        else:
            missing.append(topic)
            print("%-28s %-58s %s" % (topic, "(unresolved)", "tried %d" % len(expanded)), flush=True)

    print("", flush=True)
    print("resolved %d / %d" % (len(resolved), len(CURRICULUM)), flush=True)
    if missing:
        print("unresolved: %s" % ", ".join(missing), flush=True)

    print("", flush=True)
    print("PAGES = {", flush=True)
    for topic, (slug, _title) in resolved.items():
        print('    "%s": "%s",' % (slug, topic), flush=True)
    print("}", flush=True)


if __name__ == "__main__":
    main()
