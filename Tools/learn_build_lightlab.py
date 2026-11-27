"""Lumen round 4: build a controlled practice level out of official engine assets.

The light leak experiment failed in the main level because the scene was already lit, so the variables
could not be isolated. This builds a small sealed room instead: a floor, four walls and a ceiling of
basic shape cubes, with one light inside. Inside that room a light leak is visible without ambiguity.

Two test subjects go in, both official assets:
  - a wall whose thinnest side is ten centimetres, the documented minimum
  - a wall made from s_cube_1cm, a one centimetre cube that is also scaled up five hundred times, which
    is the documented "imported small, scaled up" case

The level is saved to /Game/Learning so the game's own level is untouched.

    py "Tools/learn_build_lightlab.py"
"""

import unreal

LEVEL_PATH = "/Game/Learning/L_LightLab"
MATERIAL = "/Engine/BasicShapes/BasicShapeMaterial"
CUBE = "/Engine/BasicShapes/Cube"
PLANE = "/Engine/BasicShapes/Plane"
SMALL_CUBE = "/Engine/EngineMeshes/s_cube_1cm"

# Room dimensions in centimetres.
HALF = 500.0
HEIGHT = 400.0


def log(text):
    unreal.log("[LingXuJie] BUILD: %s" % text)


def main():
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()

    if world is None:
        log("no editor world")
        return

    # A new level starts empty, which is the point: nothing is already lit.
    if not level_subsystem.new_level(LEVEL_PATH):
        log("could not create %s" % LEVEL_PATH)
        return
    log("created %s" % LEVEL_PATH)

    cube = unreal.load_asset(CUBE)
    material = unreal.load_asset(MATERIAL)
    small = unreal.load_asset(SMALL_CUBE)

    if cube is None or material is None:
        log("core assets missing: cube=%r material=%r" % (cube, material))
        return

    def place(mesh, location, scale, label, yaw=0.0):
        actor = actor_subsystem.spawn_actor_from_class(
            unreal.StaticMeshActor, unreal.Vector(*location),
            unreal.Rotator(pitch=0.0, yaw=yaw, roll=0.0))
        if actor is None:
            log("could not spawn %s" % label)
            return None
        component = actor.get_component_by_class(unreal.StaticMeshComponent)
        component.set_editor_property("static_mesh", mesh)
        component.set_material(0, material)
        actor.set_actor_scale3d(unreal.Vector(*scale))
        actor.set_actor_label(label)
        return actor

    # The engine cube is 100 cm on a side, so scale is a fraction of that.
    unit = 100.0

    # Floor and ceiling.
    place(cube, (0.0, 0.0, 0.0), (HALF * 2 / unit, HALF * 2 / unit, 0.1), "LXJ_LAB_Floor")
    place(cube, (0.0, 0.0, HEIGHT), (HALF * 2 / unit, HALF * 2 / unit, 0.1), "LXJ_LAB_Ceiling")

    # Four sealed walls, 20 cm thick, well above the documented minimum.
    thickness = 20.0 / unit
    place(cube, (HALF, 0.0, HEIGHT / 2), (thickness, HALF * 2 / unit, HEIGHT / unit), "LXJ_LAB_Wall_E")
    place(cube, (-HALF, 0.0, HEIGHT / 2), (thickness, HALF * 2 / unit, HEIGHT / unit), "LXJ_LAB_Wall_W")
    place(cube, (0.0, HALF, HEIGHT / 2), (HALF * 2 / unit, thickness, HEIGHT / unit), "LXJ_LAB_Wall_S")
    place(cube, (0.0, -HALF, HEIGHT / 2), (HALF * 2 / unit, thickness, HEIGHT / unit), "LXJ_LAB_Wall_N")

    # Test subject A: a wall at exactly the documented minimum of ten centimetres.
    place(cube, (0.0, -260.0, HEIGHT / 2), (HALF * 0.6 / unit, 10.0 / unit, HEIGHT * 0.8 / unit),
          "LXJ_TEST_Wall10cm")

    # Test subject B: the one centimetre cube scaled up five hundred times.
    if small is not None:
        place(small, (0.0, 200.0, 40.0), (500.0, 500.0, 500.0), "LXJ_TEST_1cmScaled500x")
        log("placed s_cube_1cm at scale 500 (native 1 cm -> 5 m)")
    else:
        log("s_cube_1cm not found")

    # One point light inside, so anything lit outside it is a leak.
    light = actor_subsystem.spawn_actor_from_class(
        unreal.PointLight, unreal.Vector(0.0, 0.0, HEIGHT * 0.6), unreal.Rotator(0.0, 0.0, 0.0))
    if light is not None:
        light.set_actor_label("LXJ_LAB_Light")
        component = light.get_component_by_class(unreal.PointLightComponent)
        if component is not None:
            component.set_editor_property("intensity", 5000.0)
            component.set_editor_property("attenuation_radius", 900.0)
            component.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)

    # A player start so PIE lands inside the room.
    player_start = actor_subsystem.spawn_actor_from_class(
        unreal.PlayerStart, unreal.Vector(-350.0, -350.0, 100.0), unreal.Rotator(0.0, 45.0, 0.0))
    if player_start is not None:
        player_start.set_actor_label("LXJ_LAB_PlayerStart")

    count = len(unreal.EditorLevelLibrary.get_all_level_actors())
    log("actors: %d" % count)

    if level_subsystem.save_current_level():
        log("saved %s" % LEVEL_PATH)
    else:
        log("save failed")

    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
