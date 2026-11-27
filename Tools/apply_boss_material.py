"""Give the imported boss a surface instead of default grey.

The material block names boss_mob01.tga and the file exists as boss_mob01.dds. This imports that
texture, builds a material that samples it, and assigns the material to every slot of the boss's
skeletal mesh - enough to see whether the colour comes through.

    py "Tools/apply_boss_material.py"
"""

import os

import unreal

TEXTURE = "C:/Users/tk/Desktop/moxiang-study/resources/dds/boss_mob01.dds"
TEX_FOLDER = "/Game/Moxiang/Textures"
TEX_NAME = "T_Boss_Mob01"
MAT_FOLDER = "/Game/Moxiang/Materials"
MAT_NAME = "M_Boss_Mob01"
MESH = "/Game/Moxiang/Skeletal/Characters/boss001/SkeletalMeshes/SK_Boss001.SK_Boss001"
LABEL = "MX_BOSS001"


def log(text):
    unreal.log("[LingXuJie] MAT: %s" % text)


def main():
    if not os.path.exists(TEXTURE):
        log("texture missing: %s" % TEXTURE)
        return
    log("texture %s (%d bytes)" % (os.path.basename(TEXTURE), os.path.getsize(TEXTURE)))

    # Import the texture.
    tex_path = "%s/%s" % (TEX_FOLDER, TEX_NAME)
    if not unreal.EditorAssetLibrary.does_asset_exist(tex_path):
        task = unreal.AssetImportTask()
        task.filename = TEXTURE
        task.destination_path = TEX_FOLDER
        task.destination_name = TEX_NAME
        task.automated = True
        task.save = True
        task.replace_existing = True
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
        paths = list(task.imported_object_paths or [])
        log("texture import produced %d assets" % len(paths))
        for path in paths:
            log("  %s" % path)
    texture = unreal.EditorAssetLibrary.load_asset(tex_path)
    if texture is None:
        log("texture failed to load at %s" % tex_path)
        return
    try:
        log("texture %dx%d" % (texture.blueprint_get_size_x(), texture.blueprint_get_size_y()))
    except Exception:  # noqa: BLE001
        pass

    # Build a material that samples it.
    mat_path = "%s/%s" % (MAT_FOLDER, MAT_NAME)
    material = unreal.EditorAssetLibrary.load_asset(mat_path)
    if material is None:
        tools = unreal.AssetToolsHelpers.get_asset_tools()
        material = tools.create_asset(MAT_NAME, MAT_FOLDER, unreal.Material,
                                      unreal.MaterialFactoryNew())
        log("created material %s" % mat_path)
    else:
        log("material already exists")

    library = unreal.MaterialEditingLibrary
    # Clear any earlier attempt so re-running is idempotent.
    try:
        library.delete_all_material_expressions(material)
    except Exception:  # noqa: BLE001
        pass

    sampler = library.create_material_expression(
        material, unreal.MaterialExpressionTextureSampleParameter2D, -400, 0)
    sampler.set_editor_property("parameter_name", "BaseTexture")
    sampler.set_editor_property("texture", texture)
    library.connect_material_property(
        sampler, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
    log("connected texture to base colour")

    try:
        library.recompile_material(material)
        log("material recompiled")
    except Exception as error:  # noqa: BLE001
        log("recompile failed: %s" % error)

    unreal.EditorAssetLibrary.save_asset(mat_path)

    # Assign to every slot of the mesh.
    mesh = unreal.EditorAssetLibrary.load_asset(MESH)
    if mesh is None:
        log("mesh missing")
        return
    try:
        slots = mesh.get_editor_property("materials")
        log("mesh has %d material slot(s)" % len(slots))
        for index in range(len(slots)):
            mesh.set_material(index, material)
        log("assigned the material to %d slot(s)" % len(slots))
    except Exception as error:  # noqa: BLE001
        log("slot assignment failed: %r" % error)

    unreal.EditorAssetLibrary.save_asset(MESH)

    # Make sure the placed actor is using this mesh so the change is visible.
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for actor in subsystem.get_all_level_actors():
        if actor.get_actor_label() == LABEL:
            component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
            if component is not None:
                component.set_skeletal_mesh_asset(mesh)
                log("refreshed the placed actor")

    level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    level.save_current_level()
    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
