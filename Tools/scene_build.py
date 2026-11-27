"""Scene round 1: build a complete outdoor scene from official assets.

Reading Template_Default gave the canonical minimum for a playable scene: a directional light, sky
atmosphere, sky light, volumetric cloud, exponential height fog, a floor mesh and a player start. This
builds the same set in a fresh level using only engine content, so it can be compared with the official
template and then tuned.

A separate level keeps the dark light lab intact for the experiments that need it.

    py "Tools/scene_build.py"
"""

import unreal

LEVEL = "/Game/Learning/L_Scene01"
FLOOR = "/Engine/BasicShapes/Cube"
MATERIAL = "/Engine/Learning/Placeholder"


def log(text):
    unreal.log("[LingXuJie] SCENE: %s" % text)


def main():
    level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

    if level_subsystem.is_in_play_in_editor():
        level_subsystem.editor_request_end_play()
        log("end play requested -- rerun after it ends")
        return

    existing = unreal.EditorAssetLibrary.does_asset_exist(LEVEL)
    if existing:
        if not level_subsystem.load_level(LEVEL):
            log("could not load the existing level")
            return
        log("loaded the existing level")
        for actor in unreal.EditorLevelLibrary.get_all_level_actors():
            unreal.EditorLevelLibrary.destroy_actor(actor)
        log("cleared it")
    else:
        if not level_subsystem.new_level(LEVEL):
            log("could not create the level")
            return
        log("created %s" % LEVEL)

    placed = []

    def place(cls, location, label, rotation=(0.0, 0.0, 0.0)):
        actor = actor_subsystem.spawn_actor_from_class(
            cls, unreal.Vector(*location),
            unreal.Rotator(pitch=rotation[0], yaw=rotation[1], roll=rotation[2]))
        if actor is None:
            log("could not place %s" % label)
            return None
        actor.set_actor_label(label)
        placed.append(label)
        return actor

    # 1. Sun: angled so shadows read as afternoon.
    sun = place(unreal.DirectionalLight, (0.0, 0.0, 1000.0), "Sun", (0.0, -35.0, 0.0))
    if sun is not None:
        component = sun.get_component_by_class(unreal.DirectionalLightComponent)
        if component is not None:
            component.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
            component.set_editor_property("intensity", 8.0)
            log("sun: movable, intensity 8")

    # 2. Sky atmosphere.
    place(unreal.SkyAtmosphere, (0.0, 0.0, 0.0), "SkyAtmosphere")

    # 3. Sky light: receives light from the atmosphere.
    sky_light = place(unreal.SkyLight, (0.0, 0.0, 500.0), "SkyLight")
    if sky_light is not None:
        component = sky_light.get_component_by_class(unreal.SkyLightComponent)
        if component is not None:
            component.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
            component.set_editor_property("real_time_capture", True)
            log("sky light: movable, real time capture")

    # 4. Volumetric cloud.
    place(unreal.VolumetricCloud, (0.0, 0.0, 2000.0), "VolumetricCloud")

    # 5. Height fog for depth.
    fog = place(unreal.ExponentialHeightFog, (0.0, 0.0, 0.0), "HeightFog")
    if fog is not None:
        component = fog.get_component_by_class(unreal.ExponentialHeightFogComponent)
        if component is not None:
            try:
                component.set_editor_property("fog_density", 0.02)
                log("fog density 0.02")
            except Exception as error:  # noqa: BLE001
                log("fog density not settable: %r" % str(error)[:50])

    # 6. Floor: a cube scaled flat, 20 metres across.
    floor = place(unreal.StaticMeshActor, (0.0, 0.0, -10.0), "Floor")
    if floor is not None:
        mesh = unreal.load_asset(FLOOR)
        component = floor.get_component_by_class(unreal.StaticMeshComponent)
        if mesh is not None and component is not None:
            component.set_editor_property("static_mesh", mesh)
            floor.set_actor_scale3d(unreal.Vector(40.0, 40.0, 0.2))
            log("floor: 4000 x 4000 x 20 cm")

    # 7. Player start.
    place(unreal.PlayerStart, (0.0, -800.0, 100.0), "PlayerStart", (0.0, 0.0, 0.0))

    log("placed %d actors: %s" % (len(placed), placed))
    log("saved: %r" % level_subsystem.save_current_level())
    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
