"""Case 004: confirm the single actor that has no material, and say what it should have.

Ninety-eight of ninety-nine static mesh components resolve a material through an override; one does
not. This checks that actor's slots directly, and whether a material for it exists in the project -
which decides whether this is an oversight or a missing asset.

    py "Tools/diag_warn_step4.py"
"""

import unreal


def log(text):
    unreal.log("[LingXuJie] W4: %s" % text)


def main():
    target = None
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if actor.get_actor_label() == "MX_BOSS001_STATIC":
            target = actor
            break

    if target is None:
        log("MX_BOSS001_STATIC not found")
        return

    component = target.get_component_by_class(unreal.StaticMeshComponent)
    if component is None:
        log("no static mesh component")
        return

    mesh = component.get_editor_property("static_mesh")
    log("mesh: %s" % (mesh.get_path_name() if mesh else None))
    if mesh is None:
        return

    log("--- the mesh's own slots ---")
    try:
        slots = mesh.get_editor_property("static_materials")
        log("slot count: %d" % len(slots or []))
        for index, entry in enumerate(slots or []):
            material = entry.get_editor_property("material_interface")
            name = material.get_name() if material else None
            log("  slot %d: %r" % (index, name))
    except Exception as error:  # noqa: BLE001
        log("mesh slots unreadable: %r" % error)

    log("--- the component's effective materials ---")
    try:
        count = component.get_num_materials()
        log("component material count: %d" % count)
        for index in range(count):
            material = component.get_material(index)
            log("  effective %d: %r" % (index, material.get_name() if material else None))
    except Exception as error:  # noqa: BLE001
        log("component materials unreadable: %r" % error)

    # Is there a material in the project that looks meant for this mesh?
    log("--- candidate materials in the project ---")
    reg = unreal.AssetRegistryHelpers.get_asset_registry()
    for asset in reg.get_assets_by_path("/Game/Moxiang", True, False):
        name = str(asset.asset_name)
        if "Boss" in name or "boss" in name:
            kind = str(asset.asset_class_path.asset_name)
            if kind in ("Material", "MaterialInstanceConstant"):
                log("  %-40s (%s)" % (name, kind))

    # Does this mesh report Nanite, and does its missing material matter for that?
    try:
        nanite = mesh.get_editor_property("nanite_settings").get_editor_property("enabled")
        log("nanite enabled on this mesh: %r" % nanite)
    except Exception:  # noqa: BLE001
        pass

    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
