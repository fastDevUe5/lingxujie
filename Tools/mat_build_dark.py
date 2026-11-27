"""Material round 1: author a material from scratch and use it to darken the practice level.

The practice level's white box is why nothing could be seen in it: forty small particles against white
walls have no contrast. Fixing that needs a dark material, and building one is exactly the exercise this
block is about - create the asset, add expressions, wire them to material properties, recompile, assign.

MaterialEditingLibrary exposes the whole graph API, and AssetTools.create_asset with MaterialFactoryNew
creates the asset, so the entire workflow is reachable from Python.

    py "Tools/mat_build_dark.py"
"""

import unreal

PACKAGE = "/Game/Learning"
NAME = "M_LabDark"
DARK = 0.04  # near black, linear


def log(text):
    unreal.log("[LingXuJie] MAT1: %s" % text)


def main():
    asset_path = "%s/%s" % (PACKAGE, NAME)
    existing = unreal.load_asset(asset_path)
    if existing is not None:
        log("%s already exists, reusing it" % asset_path)
        material = existing
    else:
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        factory = unreal.MaterialFactoryNew()
        material = asset_tools.create_asset(NAME, PACKAGE, unreal.Material, factory)
        if material is None:
            log("could not create the material")
            return
        log("created %s" % asset_path)

    library = unreal.MaterialEditingLibrary
    log("expressions before: %d" % library.get_num_material_expressions(material))

    if library.get_num_material_expressions(material) == 0:
        colour = library.create_material_expression(
            material, unreal.MaterialExpressionConstant3Vector, -400, 0)
        if colour is None:
            log("could not add a constant vector")
            return
        colour.set_editor_property("constant", unreal.LinearColor(DARK, DARK, DARK, 1.0))
        log("added a constant vector at %.2f" % DARK)

        roughness = library.create_material_expression(
            material, unreal.MaterialExpressionConstant, -400, 200)
        if roughness is not None:
            roughness.set_editor_property("r", 0.6)
            log("added a roughness constant at 0.6")

        wired = library.connect_material_property(
            colour, "", unreal.MaterialProperty.MP_BASE_COLOR)
        log("base colour connected: %r" % wired)

        if roughness is not None:
            wired = library.connect_material_property(
                roughness, "", unreal.MaterialProperty.MP_ROUGHNESS)
            log("roughness connected: %r" % wired)
    else:
        log("material already has expressions, not touching the graph")

    log("expressions now: %d" % library.get_num_material_expressions(material))
    log("recompiled: %r" % library.recompile_material(material))
    log("saved: %r" % unreal.EditorAssetLibrary.save_asset(asset_path))

    # Report what the material thinks its shading is.
    for field in ("blend_mode", "shading_model", "two_sided"):
        try:
            log("  %-16s %r" % (field, material.get_editor_property(field)))
        except Exception:  # noqa: BLE001
            pass

    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
