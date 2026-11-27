"""Build the triplanar material correctly: world position divided, and weights normalised.

The first attempt looked flat because of two mistakes that are worth stating, since they are the
two that triplanar graphs always get wrong.

First, world position is in centimetres. Multiplying it by a tile count produced UVs in the
hundreds of thousands, and a texture sampled at that density averages out to a single colour. The
map is fifty-one thousand centimetres across, so the divisor has to be metres per tile, not a
multiplier.

Second, the blend weight has to be a ratio. Adding two components of the normal can exceed one, and
an alpha above one is clamped, which collapses the blend. The ratio of one component to the sum of
the pair is always within range.

    py "Tools/build_triplanar_material.py"
"""

import unreal

ASSET_DIR = "/Game/Moxiang"
NAME = "M_Ground_Triplanar"
# One tile every six metres. The map spans five hundred and twelve metres, so this repeats the
# texture about eighty-five times, which is the original intent expressed as a distance rather
# than a repeat count.
METRES_PER_TILE = 600.0


def log(text):
    unreal.log("[LingXuJie] TRI: %s" % text)


def find_texture():
    for candidate in ("/Game/Moxiang/T_tile_108_road01", "/Game/Moxiang/tile_108_road01"):
        asset = unreal.EditorAssetLibrary.load_asset(candidate)
        if asset is not None:
            return asset
    existing = unreal.EditorAssetLibrary.load_asset(
        "/Game/Moxiang/M_Moxiang_Ground.M_Moxiang_Ground")
    if existing is not None:
        for expression in unreal.MaterialEditingLibrary.get_material_expressions(existing):
            if expression.get_class().get_name() == "MaterialExpressionTextureSample":
                texture = expression.get_editor_property("texture")
                if texture is not None:
                    return texture
    return None


def main():
    path = "%s/%s" % (ASSET_DIR, NAME)
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        unreal.EditorAssetLibrary.delete_asset(path)

    tools = unreal.AssetToolsHelpers.get_asset_tools()
    material = tools.create_asset(NAME, ASSET_DIR, unreal.Material, unreal.MaterialFactoryNew())
    if material is None:
        log("could not create the material")
        return

    library = unreal.MaterialEditingLibrary
    texture = find_texture()
    if texture is None:
        log("no texture")
        return

    counter = [0]

    def make(expression_class, x, y):
        counter[0] += 1
        return library.create_material_expression(material, expression_class, x, y)

    def constant(value, x, y):
        node = make(unreal.MaterialExpressionConstant, x, y)
        node.set_editor_property("r", value)
        return node

    def link(source, source_pin, target, target_pin):
        library.connect_material_expressions(source, source_pin, target, target_pin)

    def mask(source, axes, x, y):
        node = make(unreal.MaterialExpressionComponentMask, x, y)
        node.set_editor_property("r", "X" in axes)
        node.set_editor_property("g", "Y" in axes)
        node.set_editor_property("b", "Z" in axes)
        node.set_editor_property("a", False)
        link(source, "", node, "")
        return node

    # --- world position, divided down to UV space -------------------------------------------
    world = make(unreal.MaterialExpressionWorldPosition, -2200, 0)
    inverse = constant(1.0 / METRES_PER_TILE, -2200, 200)
    scaled = make(unreal.MaterialExpressionMultiply, -1950, 0)
    link(world, "", scaled, "A")
    link(inverse, "", scaled, "B")

    # Three projection planes taken from the scaled world position.
    plane_xy = mask(scaled, "XY", -1700, -400)
    plane_zy = mask(scaled, "ZY", -1700, -100)
    plane_xz = mask(scaled, "XZ", -1700, 200)

    def sample(uv_node, x, y):
        node = make(unreal.MaterialExpressionTextureSample, x, y)
        node.set_editor_property("texture", texture)
        link(uv_node, "", node, "UVs")
        return node

    tex_xy = sample(plane_xy, -1350, -400)
    tex_zy = sample(plane_zy, -1350, -100)
    tex_xz = sample(plane_xz, -1350, 200)

    # --- normal weights, as ratios ----------------------------------------------------------
    normal = make(unreal.MaterialExpressionVertexNormalWS, -2200, 600)
    absolute = make(unreal.MaterialExpressionAbs, -1950, 600)
    link(normal, "", absolute, "")

    abs_x = mask(absolute, "X", -1700, 520)
    abs_y = mask(absolute, "Y", -1700, 660)
    abs_z = mask(absolute, "Z", -1700, 800)

    sum_xy = make(unreal.MaterialExpressionAdd, -1450, 590)
    link(abs_x, "", sum_xy, "A")
    link(abs_y, "", sum_xy, "B")

    # zero guard: the sum can be zero if the normal points straight up, so add a small epsilon.
    epsilon = constant(0.0001, -1450, 700)
    sum_safe = make(unreal.MaterialExpressionAdd, -1250, 620)
    link(sum_xy, "", sum_safe, "A")
    link(epsilon, "", sum_safe, "B")

    # ratio_y = |y| / (|x| + |y|)  -> how much of the vertical pair comes from the y projection
    ratio_y = make(unreal.MaterialExpressionDivide, -1000, 620)
    link(abs_y, "", ratio_y, "A")
    link(sum_safe, "", ratio_y, "B")

    # total = |x| + |y| + |z|, then weight_z = |z| / total
    total_xy = make(unreal.MaterialExpressionAdd, -1250, 800)
    link(sum_xy, "", total_xy, "A")
    link(abs_z, "", total_xy, "B")
    total_safe = make(unreal.MaterialExpressionAdd, -1000, 800)
    link(total_xy, "", total_safe, "A")
    link(epsilon, "", total_safe, "B")

    weight_z = make(unreal.MaterialExpressionDivide, -780, 800)
    link(abs_z, "", weight_z, "A")
    link(total_safe, "", weight_z, "B")

    # --- blend: (XZ, ZY) by ratio_y, then that with XY by weight_z ---------------------------
    pair = make(unreal.MaterialExpressionLinearInterpolate, -700, 0)
    link(tex_xz, "RGB", pair, "A")
    link(tex_zy, "RGB", pair, "B")
    link(ratio_y, "", pair, "Alpha")

    final = make(unreal.MaterialExpressionLinearInterpolate, -400, 0)
    link(pair, "", final, "A")
    link(tex_xy, "RGB", final, "B")
    link(weight_z, "", final, "Alpha")

    library.connect_material_property(final, "", unreal.MaterialProperty.MP_BASE_COLOR)

    roughness = constant(0.9, -400, 320)
    library.connect_material_property(roughness, "", unreal.MaterialProperty.MP_ROUGHNESS)

    log("built %d expressions" % counter[0])
    try:
        library.recompile_material(material)
        log("recompile ok")
    except Exception as error:  # noqa: BLE001
        log("recompile FAILED: %s" % error)
        return

    unreal.EditorAssetLibrary.save_loaded_asset(material)
    log("saved %s" % path)


main()
