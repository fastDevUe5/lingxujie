"""Material round 2: author a material whose values are parameters, so an instance can change them.

The dark material from the previous round wires constants, which an instance cannot vary - a constant is
baked into the graph. Making a material instanceable means using parameter nodes instead: a texture
sample parameter and a scalar parameter. Then the instance supplies different values and the base graph is
unchanged.

The texture is the engine's own default grid, which is what WorldGridMaterial uses, so it is official
content and needs no import.

    py "Tools/mat_build_tex.py"
"""

import unreal

PACKAGE = "/Game/Learning"
NAME = "M_LabTex"
TEXTURE = "/Engine/EngineMaterials/T_Default_Material_Grid_M.T_Default_Material_Grid_M"


def log(text):
    unreal.log("[LingXuJie] MAT3: %s" % text)


def main():
    asset_path = "%s/%s" % (PACKAGE, NAME)
    material = unreal.load_asset(asset_path)

    if material is None:
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        material = asset_tools.create_asset(
            NAME, PACKAGE, unreal.Material, unreal.MaterialFactoryNew())
        if material is None:
            log("could not create the material")
            return
        log("created %s" % asset_path)
    else:
        log("%s already exists" % asset_path)

    library = unreal.MaterialEditingLibrary
    texture = unreal.load_asset(TEXTURE)
    log("texture loaded: %r (%r)" % (texture is not None,
                                     texture.get_name() if texture else None))

    if library.get_num_material_expressions(material) > 0:
        log("graph already populated (%d expressions), leaving it alone"
            % library.get_num_material_expressions(material))
    else:
        # A scalar parameter multiplies the texture so an instance can tint or darken it.
        scalar = library.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -700, 300)
        if scalar is not None:
            scalar.set_editor_property("parameter_name", "Brightness")
            scalar.set_editor_property("default_value", 0.08)
            log("scalar parameter 'Brightness' default 0.08")

        if texture is not None:
            sample = library.create_material_expression(
                material, unreal.MaterialExpressionTextureSampleParameter2D, -700, 0)
            if sample is not None:
                sample.set_editor_property("parameter_name", "BaseTexture")
                sample.set_editor_property("texture", texture)
                log("texture parameter 'BaseTexture' set to %s" % texture.get_name())

                # Texture -> multiply -> base colour.
                multiply = library.create_material_expression(
                    material, unreal.MaterialExpressionMultiply, -400, 100)
                if multiply is not None:
                    library.connect_material_expressions(sample, "RGB", multiply, "A")
                    if scalar is not None:
                        library.connect_material_expressions(scalar, "", multiply, "B")
                    log("texture and brightness combined through a multiply")
                    log("base colour connected: %r"
                        % library.connect_material_property(
                            multiply, "", unreal.MaterialProperty.MP_BASE_COLOR))

        roughness = library.create_material_expression(
            material, unreal.MaterialExpressionConstant, -400, 320)
        if roughness is not None:
            roughness.set_editor_property("r", 0.7)
            log("roughness connected: %r"
                % library.connect_material_property(
                    roughness, "", unreal.MaterialProperty.MP_ROUGHNESS))

    log("expressions: %d" % library.get_num_material_expressions(material))
    log("recompiled")
    library.recompile_material(material)
    log("saved: %r" % unreal.EditorAssetLibrary.save_asset(asset_path))
    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
