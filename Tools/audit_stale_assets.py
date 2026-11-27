"""Report which assets are unreferenced, without deleting anything.

A hundred and seven assets in the Moxiang folder are not in the manifest, which suggests they are
left over from an earlier naming scheme. Suggestion is not evidence. The only way to know is to ask
the asset registry who references each one, and to say plainly that an empty referencer list is not
proof either - the level itself holds references that the registry reports under a different path.

This script therefore produces a report and stops.

    py "Tools/audit_stale_assets.py"
"""

import json
import os

import unreal

MANIFEST = "C:/Users/tk/Desktop/lingxujie/Assets/Moxiang/ue_import/17_arch.json"
FOLDER = "/Game/Moxiang"


def log(text):
    unreal.log("[LingXuJie] AUDIT: %s" % text)


def main():
    manifest = json.load(open(MANIFEST, encoding="utf-8"))
    wanted = set()
    for group in manifest["groups"]:
        wanted.add(group["mesh"])
        wanted.add(group["material"])
    wanted.add(manifest["terrain"])
    log("manifest names %d" % len(wanted))

    # Everything on disk in the folder.
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    assets = registry.get_assets_by_path(FOLDER, recursive=False)
    log("assets on disk %d" % len(assets))

    generated_materials = set()
    for asset in assets:
        name = str(asset.asset_name)
        if name.startswith("M_LZ_"):
            generated_materials.add(name)

    candidates = []
    for asset in assets:
        name = str(asset.asset_name)
        if name in wanted or name in generated_materials:
            continue
        if name.startswith("M_LZ_") or name.startswith("SM_LZ_"):
            continue
        candidates.append(name)

    log("candidates not named by the manifest: %d" % len(candidates))

    referenced = []
    unreferenced = []
    for name in sorted(candidates):
        path = "%s/%s" % (FOLDER, name)
        try:
            dependencies = registry.get_referencers(path)
        except Exception as error:  # noqa: BLE001
            log("referencers failed for %s: %s" % (name, error))
            continue
        if dependencies:
            referenced.append((name, len(dependencies)))
        else:
            unreferenced.append(name)

    log("--- referenced by something (%d) ---" % len(referenced))
    for name, count in referenced:
        log("    %-34s %d referencer(s)" % (name, count))

    log("--- no referencers (%d) ---" % len(unreferenced))
    for name in unreferenced:
        log("    %s" % name)

    # A file-level size total, so the size of the decision is known.
    total = 0
    disk_folder = "C:/Users/tk/Desktop/lingxujie/Content/Moxiang"
    for name in unreferenced:
        path = os.path.join(disk_folder, name + ".uasset")
        if os.path.exists(path):
            total += os.path.getsize(path)
    log("unreferenced total %d files, %.1f KB" % (len(unreferenced), total / 1024.0))
    log("report only - nothing deleted")


main()
