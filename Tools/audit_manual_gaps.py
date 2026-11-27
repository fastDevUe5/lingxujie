"""Measure what the local manual is actually missing, rather than accepting the page count.

Page count is a poor completeness measure: a landing page contributes one to the count and nothing to
the learning. Length in lines separates an article (many paragraphs) from an index (a few bullets),
which character count alone does not - niagara is 3231 characters across 21 lines and is an index.

    python Tools/audit_manual_gaps.py
"""

import glob
import os
import re

MANUAL = "C:/Users/tk/Desktop/lingxujie/Docs/UEManual"
API = "C:/Users/tk/Desktop/lingxujie/Docs/PythonAPI"

# An article has paragraphs; an index is a short list. Lines is the better separator.
ARTICLE_LINES = 40
ARTICLE_CHARS = 4000


def classify(path):
    text = open(path, encoding="utf-8").read()
    lines = [ln for ln in text.split("\n") if ln.strip()]
    chars = len(text)
    is_article = len(lines) >= ARTICLE_LINES and chars >= ARTICLE_CHARS
    return chars, len(lines), is_article


def main():
    manual = sorted(f for f in glob.glob(os.path.join(MANUAL, "*.md"))
                    if not f.endswith("README.md"))

    articles = []
    indexes = []
    for path in manual:
        name = os.path.basename(path)[:-3]
        chars, lines, is_article = classify(path)
        (articles if is_article else indexes).append((name, chars, lines))

    print("manual pages: %d" % len(manual))
    print("  articles (>= %d lines and >= %d chars): %d"
          % (ARTICLE_LINES, ARTICLE_CHARS, len(articles)))
    print("  indexes (one or both below): %d" % len(indexes))
    print("")

    print("--- INDEX PAGES, these teach nothing on their own ---")
    for name, chars, lines in sorted(indexes, key=lambda r: -r[1]):
        print("  %-28s %6d chars %4d lines" % (name, chars, lines))
    print("")

    # Which curriculum areas have no article at all.
    #
    # Both the index page and the real article are listed for each area, because which one is an
    # index only becomes clear after mirroring. A previous version of this dictionary named only the
    # index pages, so it kept reporting areas as uncovered after their articles had been added.
    GROUPS = {
        "rendering geometry": ["nanite", "nanite-technical", "virtual-shadow-maps",
                               "temporal-super-resolution", "static-mesh-lod"],
        "rendering lighting": ["lumen-technical", "lumen-performance",
                               "lighting-environment", "light-types", "directional-lights",
                               "sky-atmosphere", "reflections", "reflections-captures",
                               "post-process-materials"],
        "materials": ["materials", "material-editor-guide", "instanced-materials",
                      "material-expressions", "textures", "texture-asset-editor"],
        "world": ["landscape-technical", "world-partition", "foliage", "water",
                  "water-bodies", "collision", "navigation", "navigation-basic",
                  "navigation-mesh"],
        "animation": ["skeletal-animation", "animation-editors", "animation-blueprints",
                      "state-machines", "control-rig", "control-rig-editor",
                      "sequencer", "sequencer-editor"],
        "simulation": ["physics", "chaos-destruction", "chaos-fracture",
                       "niagara", "niagara-overview", "niagara-modules"],
        "gameplay": ["gameplay-framework", "game-mode", "enhanced-input", "blueprints",
                     "umg-quick-start"],
        "audio network perf": ["audio", "audio-engine-overview", "sound-cue-editor",
                               "sound-cue-reference", "attenuation",
                               "networking", "performance"],
        "editor scripting": ["python-scripting", "python-with-ai-agents", "unreal-mcp",
                             "level-editor", "asset-management", "command-line-arguments"],
    }
    article_names = {name for name, _c, _l in articles}
    print("--- coverage by area: an area counts as covered when it has at least one article ---")
    for group, names in GROUPS.items():
        have = [n for n in names if n in article_names]
        status = "ok" if have else "MISSING"
        print("  %-20s %-8s %d article(s): %s"
              % (group, status, len(have), ", ".join(have) if have else "-"))
    print("")

    # The Python API gap, in the same terms the status document uses.
    api_files = glob.glob(os.path.join(API, "*.txt"))
    print("--- python api ---")
    print("  mirrored: %d classes" % len(api_files))
    print("  engine total measured earlier: about 11,459")
    if api_files:
        print("  coverage: %.1f%%" % (100.0 * len(api_files) / 11459.0))


if __name__ == "__main__":
    main()
