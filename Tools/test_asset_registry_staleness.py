"""Test whether load_asset failures here come from a stale asset registry rather than a missing file.

The log holds eight "could not be found in the Asset Registry" errors for assets that plainly existed,
which suggests the registry had not scanned them yet rather than the path being wrong. This checks the
two claims separately: is the asset in the registry, and does loading it succeed before and after a
synchronous scan.

    py "Tools/test_asset_registry_staleness.py"
"""

import unreal


def log(text):
    unreal.log("[LingXuJie] REG: %s" % text)


def registry():
    return unreal.AssetRegistryHelpers.get_asset_registry()


def in_registry(package_path, asset_name):
    """Ask the registry directly, without trying to load anything."""
    try:
        data = registry().get_asset_by_object_path(
            unreal.SoftObjectPath("%s.%s" % (package_path, asset_name)))
        return data.is_valid() if hasattr(data, "is_valid") else bool(data)
    except Exception as error:  # noqa: BLE001
        log("get_asset_by_object_path raised: %r" % error)
        return None


def try_load(package_path, asset_name):
    full = "%s.%s" % (package_path, asset_name)
    try:
        asset = unreal.load_asset(full)
        return "loaded" if asset else "returned None"
    except Exception as error:  # noqa: BLE001
        return "raised %r" % error


def main():
    # The two assets that failed in the log.
    targets = [
        ("/Game/Moxiang/Textures/T_Boss_Mob01", "T_Boss_Mob01"),
        ("/Game/Moxiang/Materials/M_Boss_Mob01", "M_Boss_Mob01"),
        ("/Game/Moxiang/Static/boss001_static/StaticMeshes/SM_Boss001", "SM_Boss001"),
    ]

    log("=== before any scan ===")
    for path, name in targets:
        log("  %-56s registry=%r  load=%s"
            % (path, in_registry(path, name), try_load(path, name)))

    log("=== scanning the content root synchronously ===")
    try:
        registry().scan_paths_synchronous(["/Game/Moxiang"], True, True)
        log("  scan_paths_synchronous completed")
    except Exception as error:  # noqa: BLE001
        log("  scan raised: %r" % error)

    log("=== after the scan ===")
    for path, name in targets:
        log("  %-56s registry=%r  load=%s"
            % (path, in_registry(path, name), try_load(path, name)))

    # How many assets does the registry know about under the project root?
    try:
        assets = registry().get_assets_by_path("/Game/Moxiang", True, False)
        log("registry knows %d asset(s) under /Game/Moxiang" % len(assets))
    except Exception as error:  # noqa: BLE001
        log("get_assets_by_path raised: %r" % error)

    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
