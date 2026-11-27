"""Import the DDS texture with an explicit factory, then build and assign the material.

The first attempt left nothing on disk: import_asset_tasks with no factory goes through Interchange,
which does not handle a DDS, and the log's "contains no miplevels" was that path producing a
half-made asset. Naming the texture factory is the straightforward fix.

    py "Tools/apply_boss_material2.py"
"""

import os

import unreal

TEXTURE = "C:/Users/tk/Desktop/lingxujie/Assets/Moxiang/textures_png/boss_mob01.png"
TEX_FOLDER = "/Game/Moxiang/Textures"
TEX_NAME = "T_Boss_Mob01"
MAT_FOLDER = "/Game/Moxiang/Materials"
MAT_NAME = "M_Boss_Mob01"
MESH = "/Game/Moxiang/Skeletal/Characters/boss001/SkeletalMeshes/SK_Boss001.SK_Boss001"
LABEL = "MX_BOSS001"


def log(text):
    unreal.log("[LingXuJie] MAT2: %s" % text)


def import_texture():
    path = "%s/%s" % (TEX_FOLDER, TEX_NAME)
    existing = unreal.EditorAssetLibrary.load_asset(path)
    if existing is not None:
        log("texture already present")
        return existing

    task = unreal.AssetImportTask()
    task.filename = TEXTURE
    task.destination_path = TEX_FOLDER
    task.destination_name = TEX_NAME
    task.automated = False
    task.save = True
    task.replace_existing = True

    factory = None
    for candidate in ("TextureFactory", "Texture2DFactoryNew", "DDSFactory"):
        cls = getattr(unreal, candidate, None)
        if cls is not None:
            try:
                factory = cls()
                log("using %s" % candidate)
                break
            except Exception as error:  # noqa: BLE001
                log("%s could not be constructed: %s" % (candidate, error))
    if factory is not None:
        task.factory = factory

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    produced = list(task.imported_object_paths or [])
    log("import produced %d asset(s)" % len(produced))
    for entry in produced:
        log("  %s" % entry)

    texture = unreal.EditorAssetLibrary.load_asset(path)
    if texture is None and produced:
        texture = unreal.EditorAssetLibrary.load_asset(produced[0])
    return texture


def main():
    if not os.path.exists(TEXTURE):
        log("texture missing")
        return

    texture = import_texture()
    if texture is None:
        log("texture still unloadable; stopping before the material so the cause stays clear")
        return
    log("texture loaded: %s" % texture.get_name())
    try:
        log("size %dx%d" % (texture.blueprint_get_size_x(), texture.blueprint_get_size_y()))
    except Exception:  # noqa: BLE001
        pass

    mat_path = "%s/%s" % (MAT_FOLDER, MAT_NAME)
    material = unreal.EditorAssetLibrary.load_asset(mat_path)
    if material is None:
        tools = unreal.AssetToolsHelpers.get_asset_tools()
        material = tools.create_asset(MAT_NAME, MAT_FOLDER, unreal.Material,
                                      unreal.MaterialFactoryNew())
        log("created material")
    else:
        log("material existed")

    library = unreal.MaterialEditingLibrary
    try:
        library.delete_all_material_expressions(material)
    except Exception:  # noqa: BLE001
        pass

    sampler = library.create_material_expression(
        material, unreal.MaterialExpressionTextureSampleParameter2D, -400, 0)
    sampler.set_editor_property("parameter_name", "BaseTexture")
    sampler.set_editor_property("texture", texture)
    library.connect_material_property(sampler, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
    library.recompile_material(material)
    unreal.EditorAssetLibrary.save_asset(mat_path)
    log("material built and saved")

    mesh = unreal.EditorAssetLibrary.load_asset(MESH)
    if mesh is None:
        log("mesh missing")
        return
    slots = mesh.get_editor_property("materials")
    for index in range(len(slots)):
        mesh.set_material(index, material)
    log("assigned material to %d slot(s)" % len(slots))
    unreal.EditorAssetLibrary.save_asset(MESH)

    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for actor in subsystem.get_all_level_actors():
        if actor.get_actor_label() == LABEL:
            component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
            if component is not None:
                component.set_skeletal_mesh_asset(mesh)
                log("refreshed the actor")
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
