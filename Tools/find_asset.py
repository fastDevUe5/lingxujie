"""Find an asset by name instead of guessing its path.

"could not be found in the Asset Registry" is usually a wrong path rather than a missing file, and the
cure is to ask the registry where the asset actually lives. This searches under the project root and
prints every match with its real package path.

    py "Tools/find_asset.py SM_Boss001"
"""

import unreal


def log(text):
    unreal.log("[LingXuJie] FIND: %s" % text)


def registry():
    return unreal.AssetRegistryHelpers.get_asset_registry()


def main():
    args = unreal.SystemLibrary.get_command_line().split()
    needle = "SM_Boss001"
    for index, token in enumerate(args):
        if token == "--find" and index + 1 < len(args):
            needle = args[index + 1]

    reg = registry()
    log("searching /Game for assets whose name contains %r" % needle)

    try:
        assets = reg.get_assets_by_path("/Game", True, False)
    except Exception as error:  # noqa: BLE001
        log("get_assets_by_path raised: %r" % error)
        return

    log("registry holds %d asset(s) under /Game" % len(assets))

    matches = 0
    for asset in assets:
        try:
            # asset_data exposes the package and the object separately; the full object path is
            # package.object, which is what load_asset wants.
            package = str(asset.package_name)
            name = str(asset.asset_name)
        except Exception:  # noqa: BLE001
            continue
        if needle.lower() in name.lower():
            matches += 1
            log("    %s.%s" % (package, name))
            try:
                cls = asset.asset_class_path.asset_name
                log("        class=%s" % cls)
            except Exception:  # noqa: BLE001
                pass

    log("found %d match(es) for %r" % (matches, needle))

    # Then prove the found path actually loads, which is the second half of the diagnosis.
    if matches:
        for asset in assets:
            try:
                if needle.lower() in str(asset.asset_name).lower():
                    full = "%s.%s" % (asset.package_name, asset.asset_name)
                    loaded = unreal.load_asset(full)
                    log("load %s -> %s" % (full, "ok" if loaded else "None"))
                    break
            except Exception as error:  # noqa: BLE001
                log("load raised: %r" % error)

    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
