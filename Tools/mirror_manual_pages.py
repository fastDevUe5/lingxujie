"""Mirror the manual pages this project actually reads.

The Python API reference gives signatures; the manual gives the reasoning behind them - what
Nanite does to collision, how asset import handles coordinate systems, why a material compiles
the way it does. Those pages are worth having locally because they are short, stable, and
answering the same question twice over the network is slow.

Like the API mirror, this keeps only the article body, and is safe to re-run.

    python Tools/mirror_manual_pages.py
"""

import html as html_module
import os
import re
import time
import urllib.error
import urllib.request

OUT_DIR = "C:/Users/tk/Desktop/lingxujie/Docs/UEManual"
BASE = "https://dev.epicgames.com/documentation/en-us/unreal-engine/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# slug -> filename-friendly title
#
# Every slug here was verified by checking that the page carries a real <title>. The site answers
# HTTP 200 for paths that do not exist, so a 200 proves nothing; a page with no title is a miss.
# The negative control is "this-page-does-not-exist-at-all-xyz", which returns 200 and no title.
# Tools/verify_curriculum_slugs.py does the checking and prints this dictionary.
PAGES = {
    # --- editor scripting ---
    "scripting-the-unreal-editor-using-python": "python-scripting",
    "using-python-with-ai-agents-in-unreal-engine": "python-with-ai-agents",
    "unreal-mcp-in-unreal-editor": "unreal-mcp",
    # --- rendering: geometry ---
    "nanite-virtualized-geometry-in-unreal-engine": "nanite",
    "nanite-technical-details": "nanite-technical",
    "virtual-shadow-maps-in-unreal-engine": "virtual-shadow-maps",
    "temporal-super-resolution-in-unreal-engine": "temporal-super-resolution",
    # --- rendering: lighting ---
    "lumen-technical-details-in-unreal-engine": "lumen-technical",
    "lumen-performance-guide-for-unreal-engine": "lumen-performance",
    "lighting-the-environment-in-unreal-engine": "lighting-environment",
    "light-types-and-their-mobility-in-unreal-engine": "light-types",
    "directional-lights-in-unreal-engine": "directional-lights",
    "sky-atmosphere-component-in-unreal-engine": "sky-atmosphere",
    "reflections-environment-in-unreal-engine": "reflections",
    "reflections-captures-in-unreal-engine": "reflections-captures",
    "post-process-materials-in-unreal-engine": "post-process-materials",
    # --- materials ---
    "unreal-engine-materials": "materials",
    "unreal-engine-material-editor-user-guide": "material-editor-guide",
    "instanced-materials-in-unreal-engine": "instanced-materials",
    "unreal-engine-material-expressions-reference": "material-expressions",
    "textures-in-unreal-engine": "textures",
    "texture-asset-editor-in-unreal-engine": "texture-asset-editor",
    # --- meshes and pipelines ---
    "importing-static-meshes-in-unreal-engine": "import-static-meshes",
    "static-mesh-automatic-lod-generation-in-unreal-engine": "static-mesh-lod",
    "fbx-static-mesh-pipeline-in-unreal-engine": "fbx-static-mesh",
    # --- world ---
    "landscape-technical-guide-in-unreal-engine": "landscape-technical",
    "landscape-outdoor-terrain-in-unreal-engine": "landscape",
    "world-partition-in-unreal-engine": "world-partition",
    "foliage-mode-in-unreal-engine": "foliage",
    "water-system-in-unreal-engine": "water",
    "collision-in-unreal-engine---overview": "collision",
    "navigation-system-in-unreal-engine": "navigation",
    # --- animation ---
    "skeletal-mesh-animation-system-in-unreal-engine": "skeletal-animation",
    "animation-editors-in-unreal-engine": "animation-editors",
    "animation-blueprints-in-unreal-engine": "animation-blueprints",
    "state-machines-in-unreal-engine": "state-machines",
    "control-rig-in-unreal-engine": "control-rig",
    "control-rig-editor-in-unreal-engine": "control-rig-editor",
    "real-time-compositing-with-sequencer-in-unreal-engine": "sequencer",
    "sequencer-cinematic-editor-unreal-engine": "sequencer-editor",
    # --- simulation ---
    "physics-in-unreal-engine": "physics",
    "chaos-destruction-in-unreal-engine": "chaos-destruction",
    "fracturing-geometry-collections-user-guide": "chaos-fracture",
    "creating-visual-effects-in-niagara-for-unreal-engine": "niagara",
    "overview-of-niagara-effects-for-unreal-engine": "niagara-overview",
    "system-and-emitter-module-reference-for-niagara-effects-in-unreal-engine": "niagara-modules",
    # --- navigation and water, whose parent pages are only indexes ---
    "navigation-system-in-unreal-engine": "navigation",
    "basic-navigation-in-unreal-engine": "navigation-basic",
    "modifying-the-navigation-mesh-preparation-guide-in-unreal-engine": "navigation-mesh",
    "water-system-in-unreal-engine": "water",
    "water-body-actors-in-unreal-engine": "water-bodies",
    # --- gameplay and systems ---
    "gameplay-framework-in-unreal-engine": "gameplay-framework",
    "game-mode-and-game-state-in-unreal-engine": "game-mode",
    "enhanced-input-in-unreal-engine": "enhanced-input",
    "overview-of-blueprints-visual-scripting-in-unreal-engine": "blueprints",
    "umg-ui-designer-quick-start-guide-in-unreal-engine": "umg-quick-start",
    # --- audio, network, performance ---
    "audio-in-unreal-engine-5": "audio",
    "audio-engine-overview": "audio-engine-overview",
    "sound-cue-editor-in-unreal-engine": "sound-cue-editor",
    "sound-cue-reference-for-unreal-engine": "sound-cue-reference",
    "attenuation": "attenuation",
    "networking-overview-for-unreal-engine": "networking",
    "introduction-to-performance-profiling-and-configuration-in-unreal-engine": "performance",
    # --- reference ---
    "asset-management-in-unreal-engine": "asset-management",
    "level-editor-in-unreal-engine": "level-editor",
    "command-line-arguments-in-unreal-engine": "command-line-arguments",
    # --- systems this project actually uses ---
    "user-interfaces-and-huds-in-unreal-engine": "user-interfaces-huds",
    "data-driven-gameplay-elements-in-unreal-engine": "data-tables",
    "saving-and-loading-your-game-in-unreal-engine": "savegame",
    "unreal-insights-in-unreal-engine": "insights",
    "hierarchical-level-of-detail-outliner-in-unreal-engine": "hlod",
    "geometry-scripting-through-blueprints-in-unreal-engine": "geometry-scripting",
}


def fetch(url, timeout=50):
    last = None
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read().decode("utf-8", errors="replace")
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            last = error
            time.sleep(1.5 * (attempt + 1))
    raise last if last else RuntimeError("unknown failure")


def strip_html(raw):
    start = raw.find("<h1")
    if start < 0:
        start = raw.find("<body")
    if start < 0:
        start = 0
    end = raw.find("Ask questions and help your peers")
    body = raw[start:end] if end > start else raw[start:]

    body = re.sub(r"<script.*?</script>", "", body, flags=re.S)
    body = re.sub(r"<style.*?</style>", "", body, flags=re.S)
    body = re.sub(r"<(h[1-6])[^>]*>", r"\n\n## ", body)
    body = re.sub(r"<li[^>]*>", "\n- ", body)
    body = re.sub(r"<tr[^>]*>", "\n", body)
    body = re.sub(r"<t[dh][^>]*>", " | ", body)
    body = re.sub(r"<[^>]+>", "", body)
    body = html_module.unescape(body).replace("\u00b6", "")
    body = re.sub(r"[ \t]+", " ", body)
    body = re.sub(r"\n\s*\n\s*\n+", "\n\n", body)
    return body.strip()


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    saved = []
    failed = []

    for slug, name in PAGES.items():
        target = os.path.join(OUT_DIR, name + ".md")
        if os.path.exists(target) and os.path.getsize(target) > 400:
            saved.append(name)
            continue

        url = BASE + slug
        try:
            raw = fetch(url)
        except Exception as error:  # noqa: BLE001
            failed.append((name, str(error)[:70]))
            print("  FAIL %s" % name, flush=True)
            continue

        text = strip_html(raw)
        if len(text) < 300:
            failed.append((name, "page too short"))
            print("  SHORT %s (%d chars)" % (name, len(text)), flush=True)
            continue

        with open(target, "w", encoding="utf-8") as handle:
            handle.write("# %s\n\nSource: %s\n\n" % (slug, url))
            handle.write(text)
        saved.append(name)
        print("  [ok] %s  %d chars" % (name, len(text)), flush=True)

    with open(os.path.join(OUT_DIR, "README.md"), "w", encoding="utf-8") as handle:
        handle.write("# 本地 UE 官方手册摘录\n\n")
        handle.write("来源：`dev.epicgames.com/documentation/en-us/unreal-engine/`\n\n")
        handle.write("**只镜像本项目会读的页**，不是整站。整站几万页且随版本漂移。\n\n")
        handle.write("已收录 %d 篇：\n\n" % len(saved))
        for name in saved:
            handle.write("- `%s.md`\n" % name)
        if failed:
            handle.write("\n抓取失败 %d 篇：\n\n" % len(failed))
            for name, why in failed:
                handle.write("- `%s` — %s\n" % (name, why))

    print("DONE saved %d failed %d -> %s" % (len(saved), len(failed), OUT_DIR), flush=True)


if __name__ == "__main__":
    main()
