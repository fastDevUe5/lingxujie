"""Reading round, practice: author a post process material from scratch and apply it.

The page states three requirements that can be checked by building one: the material domain must be Post
Process, the output must go through Emissive Color alone, and the blendable location decides whether it
runs before or after tonemapping. Building it exercises the material editing API end to end and, unlike
reading it, produces something whose effect on the frame can be measured.

The material is a desaturation, which is a simple and obvious change: SceneTexture post process input 0
as scene colour, a post process input for scene colour again, and a lerp between the desaturated and
original using a saturation constant.

    py "Tools/pp_build.py"
"""

import unreal

MAT_PATH = "/Game/Learning"
MAT_NAME = "M_PPDesat"


def log(text):
    unreal.log("[LingXuJie] PP: %s" % text)


def main():
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    library = unreal.MaterialEditingLibrary

    full = "%s/%s" % (MAT_PATH, MAT_NAME)
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        unreal.EditorAssetLibrary.delete_asset(full)
        log("deleted the previous version")

    material = asset_tools.create_asset(MAT_NAME, MAT_PATH, unreal.Material,
                                        unreal.MaterialFactoryNew())
    if material is None:
        log("could not create the material")
        return
    log("created %s" % full)

    # The domain has to be post process, or the emissive connection means something else.
    material.set_editor_property("material_domain", unreal.MaterialDomain.MD_POST_PROCESS)
    log("domain: %r" % material.get_editor_property("material_domain"))

    scene = library.create_material_expression(
        material, unreal.MaterialExpressionSceneTexture, -700, 0)
    scene.set_editor_property("scene_texture_id", unreal.SceneTextureId.PPI_POST_PROCESS_INPUT0)
    log("scene texture: PPI_POST_PROCESS_INPUT0")

    # Desaturated copy: dot with the luma weights, done as a multiply and add is fiddly, so use
    # the built in Desaturation expression which exists for exactly this.
    desat = library.create_material_expression(
        material, unreal.MaterialExpressionDesaturation, -400, 0)
    desat.set_editor_property("luminance_factors", unreal.LinearColor(0.3, 0.59, 0.11, 0.0))

    library.connect_material_expressions(scene, "Color", desat, "")
    log("scene -> desaturation")

    # Strength: a constant that blends the desaturated result toward the original.
    strength = library.create_material_expression(
        material, unreal.MaterialExpressionScalarParameter, -400, 220)
    strength.set_editor_property("parameter_name", "Desaturation")
    strength.set_editor_property("default_value", 1.0)
    log("scalar parameter Desaturation = 1.0")

    blend = library.create_material_expression(
        material, unreal.MaterialExpressionLinearInterpolate, -120, 80)
    library.connect_material_expressions(scene, "Color", blend, "A")
    library.connect_material_expressions(desat, "", blend, "B")
    library.connect_material_expressions(strength, "", blend, "Alpha")
    log("lerp: A = scene colour, B = desaturated, alpha = Desaturation")

    library.connect_material_property(blend, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    log("lerp -> Emissive Color")

    library.recompile_material(material)
    unreal.EditorAssetLibrary.save_asset(full)

    # Report the blendable location, which the page says decides before or after tonemapping.
    for field in ("blendable_location", "blendable_priority"):
        try:
            log("%-22s %r" % (field, material.get_editor_property(field)))
        except Exception as error:  # noqa: BLE001
            log("%-22s unreadable" % field)

    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
