"""Lumen round 3, practice: prove or disprove light leaking through the zero-thickness wall.

A distance field cannot represent a zero-thickness plane as solid, so a light on one side should be
visible from the other. This places a bright point light in front of the wall and reports its position;
the caller captures from behind the wall, then this script removes the light again.

The light is spawned at runtime and destroyed at the end, so nothing is saved into the level.

    py "Tools/lumen_leak_test.py"         (spawn)
    py "Tools/lumen_leak_test.py --clean" (remove)
"""

import sys

import unreal

TARGET = "MX_LZ_JP_WALL03"
LIGHT_LABEL = "LXJ_LEAK_TEST_LIGHT"


def log(text):
    unreal.log("[LingXuJie] LEAK: %s" % text)


def clean():
    removed = 0
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if actor.get_actor_label() == LIGHT_LABEL:
            unreal.EditorLevelLibrary.destroy_actor(actor)
            removed += 1
    log("removed %d test light(s)" % removed)


def spawn():
    subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)

    target = None
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if actor.get_actor_label() == TARGET:
            target = actor
            break
    if target is None:
        log("%s not found" % TARGET)
        return

    origin, extent = target.get_actor_bounds(False)
    log("wall centre (%.0f, %.0f, %.0f)" % (origin.x, origin.y, origin.z))

    # In front of the wall on -Y, the side the earlier camera did not stand on.
    light_location = unreal.Vector(origin.x, origin.y - 150.0, origin.z)

    light = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.PointLight, light_location, unreal.Rotator(0.0, 0.0, 0.0))
    if light is None:
        log("could not spawn the light")
        return
    light.set_actor_label(LIGHT_LABEL)

    component = light.get_component_by_class(unreal.PointLightComponent)
    if component is not None:
        component.set_editor_property("intensity", 20000.0)
        component.set_editor_property("attenuation_radius", 2500.0)
        component.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
        log("light intensity 20000, radius 2500, set movable")

    log("light at (%.0f, %.0f, %.0f)" % (light_location.x, light_location.y, light_location.z))

    # Look from behind the wall, the +Y side: if light appears on this face, it leaked through.
    back_distance = 500.0
    camera = unreal.Vector(origin.x, origin.y + back_distance, origin.z + extent.z * 0.3)
    rotation = unreal.Rotator(pitch=0.0, yaw=0.0, roll=0.0)
    rotation.yaw = -90.0
    rotation.pitch = -3.0
    subsystem.set_level_viewport_camera_info(camera, rotation)
    log("camera behind wall at %.0f, %.0f, %.0f yaw -90 pitch -3"
        % (camera.x, camera.y, camera.z))
    log("done")


try:
    if "--clean" in sys.argv:
        clean()
    else:
        spawn()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
