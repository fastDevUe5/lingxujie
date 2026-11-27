"""Read the ground material's tiling and report what actually controls it.

The visible problem is a regular grid across the terrain, which comes from repeating one tile a
fixed number of times across the whole map. The texture coordinate node holds that number, so
reading it turns a description into a figure.

    python Tools/inspect_ground_material.py
"""

import unreal

MATERIAL = "/Game/Moxiang/M_Moxiang_Ground.M_Moxiang_Ground"


def main():
    material = unreal.EditorAssetLibrary.load_asset(MATERIAL)
    if material is None:
        unreal.log_error("[LingXuJie] MAT: material not found")
        return

    unreal.log("[LingXuJie] MAT: %s" % material.get_name())

    # Walk the expressions and report the ones that carry the tiling.
    library = unreal.MaterialEditingLibrary
    expressions = library.get_material_expressions(material)
    unreal.log("[LingXuJie] MAT: %d expressions" % len(expressions))

    for expression in expressions:
        name = expression.get_class().get_name()
        if name == "MaterialExpressionTextureCoordinate":
            u = expression.get_editor_property("u_tiling")
            v = expression.get_editor_property("v_tiling")
            unreal.log("[LingXuJie] MAT: TextureCoordinate u_tiling=%.1f v_tiling=%.1f" % (u, v))
            unreal.log("[LingXuJie] MAT: over 51200 cm, one tile covers %.1f cm"
                       % (51200.0 / u if u else 0.0))
        elif name == "MaterialExpressionTextureSample":
            texture = expression.get_editor_property("texture")
            label = texture.get_name() if texture else "none"
            sample_type = expression.get_editor_property("sampler_type")
            unreal.log("[LingXuJie] MAT: TextureSample texture=%s sampler=%s"
                       % (label, sample_type))
        elif name == "MaterialExpressionConstant":
            unreal.log("[LingXuJie] MAT: Constant r=%.2f"
                       % expression.get_editor_property("r"))


main()
