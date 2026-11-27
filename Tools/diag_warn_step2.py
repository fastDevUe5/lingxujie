"""Case 004: does any Nanite mesh reference a material that is not marked for Nanite.

The MapCheck warning about M_Ground_Triplanar said the flag was missing but only matters if the asset
is not re-saved, which suggests the in-memory value and the saved value disagree. A separate and
sharper question is whether a mesh that actually uses Nanite is paired with a material that does not
declare support, because that pairing is what breaks outside the editor.

    py "Tools/diag_warn_step2.py"
"""

import unreal


def log(text):
    unreal.log("[LingXuJie] W2: %s" % text)


def main():
    unreal.SystemLibrary.execute_console_command(
        unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(), "map check")

    reg = unreal.AssetRegistryHelpers.get_asset_registry()

    log("=== static meshes: Nanite on, and which materials they use ===")
    nanite_meshes = []
    for asset in reg.get_assets_by_path("/Game/Moxiang", True, False):
        if str(asset.asset_class_path.asset_name) != "StaticMesh":
            continue
        path = "%s.%s" % (asset.package_name, asset.asset_name)
        mesh = unreal.load_asset(path)
        if mesh is None:
            continue
        try:
            nanite_settings = mesh.get_editor_property("nanite_settings")
            enabled = nanite_settings.get_editor_property("enabled")
        except Exception:  # noqa: BLE001
            enabled = None

        if enabled is None:
            continue

        if enabled:
            nanite_meshes.append(path)
            log("  %-50s nanite=ON" % asset.asset_name)
            # Which materials does it reference?
            for slot in range(mesh.get_num_lods() and 1 or 1):
                break
            try:
                static_materials = mesh.get_editor_property("static_materials")
                for entry in static_materials or []:
                    material = entry.get_editor_property("material_interface")
                    if material is None:
                        continue
                    try:
                        flag = material.get_editor_property("used_with_nanite")
                    except Exception:  # noqa: BLE001
                        flag = None
                    marker = "" if flag else "   <-- NOT marked for Nanite"
                    log("      uses %-44s flag=%r%s" % (material.get_name(), flag, marker))
            except Exception as error:  # noqa: BLE001
                log("      material slots unreadable: %r" % error)

    log("nanite-enabled static meshes: %d of the scanned set" % len(nanite_meshes))

    log("=== material saved-state ===")
    for asset in reg.get_assets_by_path("/Game/Moxiang", True, False):
        if str(asset.asset_class_path.asset_name) not in ("Material", "MaterialInstanceConstant"):
            continue
        path = "%s.%s" % (asset.package_name, asset.asset_name)
        material = unreal.load_asset(path)
        if material is None:
            continue
        try:
            dirty = material.get_outer().get_editor_property("is_dirty")
        except Exception:  # noqa: BLE001
            dirty = None
        if dirty:
            log("  %-50s package is dirty (unsaved changes)" % asset.asset_name)

    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
