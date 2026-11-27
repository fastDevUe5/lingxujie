"""Material round 3, part three: set the Nanite override using the field names the source actually uses.

The first attempt guessed b_override_material and nanite_override_material inside the struct; neither
exists. Reading FMaterialOverrideNanite in the engine gives the real names: bEnableOverride,
OverrideMaterialEditor (editor only, this is the one to set), and a protected OverrideMaterial that only
exists in cooked packages. There is also a SetOverrideMaterial function, but the editor property is
enough here.

    py "Tools/mat_nanite_set2.py"
"""

import unreal

BASE = "/Game/Learning/M_LabTex"
RED = "/Game/Learning/M_LabRedOverride"


def log(text):
    unreal.log("[LingXuJie] NAN3: %s" % text)


def main():
    base = unreal.load_asset(BASE)
    red = unreal.load_asset(RED)
    if base is None:
        log("base missing")
        return
    if red is None:
        log("the red override material is missing")
        return

    structure = base.get_editor_property("nanite_override_material")
    log("struct: %r" % type(structure).__name__)

    for field, value in (("b_enable_override", True),
                         ("override_material_editor", red)):
        try:
            structure.set_editor_property(field, value)
            log("  set %-26s ok" % field)
        except Exception as error:  # noqa: BLE001
            log("  set %-26s failed: %r" % (field, str(error)[:70]))

    try:
        base.set_editor_property("nanite_override_material", structure)
        log("struct written back")
    except Exception as error:  # noqa: BLE001
        log("write back failed: %r" % str(error)[:70])

    # Read back both ways.
    again = base.get_editor_property("nanite_override_material")
    for field in ("b_enable_override", "override_material_editor", "override_material"):
        try:
            value = again.get_editor_property(field)
            log("  %-26s %r" % (field, value.get_name() if hasattr(value, "get_name") else value))
        except Exception as error:  # noqa: BLE001
            log("  %-26s unreadable: %r" % (field, str(error)[:50]))

    via_library = unreal.MaterialEditingLibrary.get_nanite_override_material(base)
    log("library says: %r" % (via_library.get_name() if via_library else None))

    log("saved: %r" % unreal.EditorAssetLibrary.save_asset(BASE))

    # Also flip the usage flag, which is the separate thing the MapCheck complains about.
    try:
        before = base.get_editor_property("used_with_nanite")
        base.set_editor_property("used_with_nanite", True)
        after = base.get_editor_property("used_with_nanite")
        log("used_with_nanite: %r -> %r" % (before, after))
        log("saved after usage flag: %r" % unreal.EditorAssetLibrary.save_asset(BASE))
    except Exception as error:  # noqa: BLE001
        log("used_with_nanite not settable: %r" % str(error)[:60])

    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
