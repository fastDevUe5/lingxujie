"""Find which documentation slugs actually resolve, so the manual mirror stops producing empty pages.

Twelve of the fifteen slugs in mirror_manual_pages.py returned nothing. One page fetched successfully
this session used the suffix "-in-unreal-engine", which suggests most slugs carry it. This tries each
candidate with and without the suffix and reports the HTTP status, so the list can be corrected from
evidence rather than by guessing again.

    python Tools/probe_manual_slugs.py
"""

import urllib.error
import urllib.request

BASE = "https://dev.epicgames.com/documentation/en-us/unreal-engine/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
SUFFIX = "-in-unreal-engine"

CANDIDATES = [
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
    # The ones this learning round needs most.
    "lumen-technical-details",
    "lumen-performance-guide",
    "niagara-visual-effects",
    "physics-simulation",
    "umg-ui-designer-quick-start",
    "post-process-materials",
    "world-partition",
    "nanite",
]


def status(url):
    request = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(request, timeout=40) as response:
            body = response.read(4000)
            return response.status, len(body)
    except urllib.error.HTTPError as error:
        return error.code, 0
    except Exception as error:  # noqa: BLE001
        return "err", 0


def main():
    print("%-46s %-28s %s" % ("slug tried", "variant", "result"))
    print("-" * 92)

    resolved = {}
    for slug in CANDIDATES:
        tried = False
        for variant, candidate in (("plain", slug), ("suffix", slug + SUFFIX)):
            code, size = status(BASE + candidate)
            ok = code == 200 and size > 2000
            if ok:
                print("%-46s %-28s %s (%d bytes)" % (slug, variant, code, size))
                resolved[slug] = candidate
                tried = True
                break
        if not tried:
            print("%-46s %-28s %s" % (slug, "both", "not found"))

    print("")
    print("resolved: %d of %d" % (len(resolved), len(CANDIDATES)))
    print("")
    print("copy these into mirror_manual_pages.py PAGES:")
    print("")
    for slug, candidate in resolved.items():
        print('    "%s": "%s",' % (candidate, slug.replace(SUFFIX, "")))


if __name__ == "__main__":
    main()
