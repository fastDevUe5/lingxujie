"""Find out which cube and volume textures are eating the texture budget.

The memreport shows three TextureCube objects costing 16.5 MB and seven VolumeTexture objects costing
10.5 MB, against 251 Texture2D objects costing 43 MB. Ten assets outweigh a quarter of the rest, so
naming them is the whole point of this check.

    py "Tools/list_expensive_textures.py"
"""

import unreal


def log(text):
    unreal.log("[LingXuJie] TEX: %s" % text)


def world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()


def run(command):
    unreal.SystemLibrary.execute_console_command(world(), command)


def by_class(class_name):
    """Enumerate assets of one class through the asset registry."""
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    assets = registry.get_assets_by_class(unreal.TopLevelAssetPath("/Script/Engine", class_name), True)
    out = []
    for asset in assets:
        package = str(asset.package_name)
        out.append(package)
    return sorted(out)


def main():
    for class_name in ("TextureCube", "VolumeTexture", "FontFace"):
        names = by_class(class_name)
        log("%s: %d asset(s)" % (class_name, len(names)))
        for name in names[:12]:
            log("    %s" % name)

    # The engine's own listing, which includes objects that are not assets on disk.
    log("--- engine obj list for the two expensive classes ---")
    run("obj list class=TextureCube")
    run("obj list class=VolumeTexture")

    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
