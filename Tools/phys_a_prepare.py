"""Physics round 1, step A: place the sphere, save, start simulate, and exit immediately.

A sleep inside a console command blocks the game thread, so the world cannot advance while the script
runs. That is why the previous attempts saw either no game world or an already-resting sphere: whichever
they observed, the simulation had only progressed while the script was not executing.

So the work is split. This run only prepares and starts; the reading happens in a later run, with real
time passing in between because the editor is free to tick.

    py "Tools/phys_a_prepare.py"
"""

import unreal

LAB = "/Game/Learning/L_LightLab"
LABEL = "LXJ_PHYS_SPHERE"
SPHERE = "/Engine/BasicShapes/Sphere"
MATERIAL = "/Engine/BasicShapes/BasicShapeMaterial"
START_Z = 300.0


def log(text):
    unreal.log("[LingXuJie] PA: %s" % text)


def main():
    level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

    current = level_subsystem.get_current_level()
    if (current.get_name() if current else "") != "L_LightLab":
        if not level_subsystem.load_level(LAB):
            log("could not open the lab")
            return

    if level_subsystem.is_in_play_in_editor():
        level_subsystem.editor_request_end_play()
        log("end play requested for the previous session")

    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if actor.get_actor_label() == LABEL:
            unreal.EditorLevelLibrary.destroy_actor(actor)

    mesh = unreal.load_asset(SPHERE)
    material = unreal.load_asset(MATERIAL)
    if mesh is None:
        log("sphere missing")
        return

    actor = actor_subsystem.spawn_actor_from_class(
        unreal.StaticMeshActor, unreal.Vector(0.0, 0.0, START_Z),
        unreal.Rotator(pitch=0.0, yaw=0.0, roll=0.0))
    actor.set_actor_label(LABEL)
    component = actor.get_component_by_class(unreal.StaticMeshComponent)
    component.set_editor_property("static_mesh", mesh)
    if material is not None:
        component.set_material(0, material)
    actor.set_actor_scale3d(unreal.Vector(0.4, 0.4, 0.4))
    component.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    component.set_simulate_physics(True)
    component.set_enable_gravity(True)
    log("placed at z=%.0f with physics on" % START_Z)

    log("saved: %r" % level_subsystem.save_current_level())
    level_subsystem.editor_play_simulate()
    log("simulate requested; do not sleep here")
    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
