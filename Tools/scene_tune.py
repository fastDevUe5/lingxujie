"""Scene round 2: tune the scene - give the floor a material and add a post process volume.

The first build produced a working sunset field but the floor was unlit grey, because it had no material.
The official templates also omit a post process volume, relying on engine defaults; adding one with manual
exposure makes the look controllable rather than letting auto exposure decide.

Both changes connect earlier blocks: the material comes from the material round, the exposure control from
the Lumen observations about blown-out frames.

    py "Tools/scene_tune.py"
"""

import unreal

LEVEL = "/Game/Learning/L_Scene01"
NEW_MAT = "/Game/Learning/M_SceneFloor"


def log(text):
    unreal.log("[LingXuJie] TUNE: %s" % text)


def main():
    level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

    current = level_subsystem.get_current_level()
    if (current.get_name() if current else "") != "L_Scene01":
        if not level_subsystem.load_level(LEVEL):
            log("could not load %s" % LEVEL)
            return

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    library = unreal.MaterialEditingLibrary

    # A ground material: warm mid grey with high roughness, so it reads as earth.
    material = unreal.load_asset(NEW_MAT)
    if material is None:
        material = asset_tools.create_asset(
            "M_SceneFloor", "/Game/Learning", unreal.Material,
            unreal.MaterialFactoryNew())
        if material is None:
            log("could not create the floor material")
            return
        colour = library.create_material_expression(
            material, unreal.MaterialExpressionConstant3Vector, -400, 0)
        colour.set_editor_property("constant", unreal.LinearColor(0.18, 0.15, 0.12, 1.0))
        rough = library.create_material_expression(
            material, unreal.MaterialExpressionConstant, -400, 200)
        rough.set_editor_property("r", 0.9)
        library.connect_material_property(colour, "", unreal.MaterialProperty.MP_BASE_COLOR)
        library.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
        library.recompile_material(material)
        unreal.EditorAssetLibrary.save_asset(NEW_MAT)
        log("created M_SceneFloor: albedo 0.18/0.15/0.12, roughness 0.9")

    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if actor.get_actor_label() == "Floor":
            component = actor.get_component_by_class(unreal.StaticMeshComponent)
            if component is not None:
                component.set_material(0, material)
                applied = component.get_material(0)
                log("floor material: %r" % (applied.get_name() if applied else None))

    # A post process volume with manual exposure, so the look does not drift with adaptation.
    existing = None
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if actor.get_actor_label() == "PostProcess":
            existing = actor
            break

    if existing is None:
        volume = actor_subsystem.spawn_actor_from_class(
            unreal.PostProcessVolume, unreal.Vector(0.0, 0.0, 500.0),
            unreal.Rotator(pitch=0.0, yaw=0.0, roll=0.0))
        if volume is not None:
            volume.set_actor_label("PostProcess")
            volume.set_editor_property("unbound", True)
            settings = volume.get_editor_property("settings")
            try:
                settings.set_editor_property("override_auto_exposure_method", True)
                settings.set_editor_property(
                    "auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL)
                log("post process: unbound, manual exposure")
            except Exception as error:  # noqa: BLE001
                log("exposure settings not settable: %r" % str(error)[:70])
            try:
                settings.set_editor_property("override_bloom_intensity", True)
                settings.set_editor_property("bloom_intensity", 0.4)
                log("bloom intensity 0.4")
            except Exception as error:  # noqa: BLE001
                log("bloom not settable: %r" % str(error)[:60])
            volume.set_editor_property("settings", settings)

    log("actors: %d" % len(unreal.EditorLevelLibrary.get_all_level_actors()))
    log("saved: %r" % level_subsystem.save_current_level())
    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
