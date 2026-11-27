"""Lumen round 5, verification: does the practice level have any distance fields at all.

The atlas report in the practice level showed 8 MB total with 8 MB free, which reads as zero distance
fields being built. That matters because the previous round concluded light leaked through a ten
centimetre ceiling, and distance fields were the proposed mechanism. If there are none, the mechanism
was something else and that conclusion needs correcting.

This checks three things: whether Generate Mesh Distance Fields is on, what the atlas says now, and
whether the meshes in the level are the ones expected.

    py "Tools/learn_verify_df.py"
"""

import unreal

LAB = "/Game/Learning/L_LightLab"


def log(text):
    unreal.log("[LingXuJie] VDF: %s" % text)


def main():
    level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()

    current = level_subsystem.get_current_level()
    name = current.get_name() if current else ""
    log("current level: %s" % name)
    if name != "L_LightLab":
        if not level_subsystem.load_level(LAB):
            log("could not open %s" % LAB)
            return
        log("opened %s" % LAB)
        world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()

    def cmd(command):
        unreal.SystemLibrary.execute_console_command(world, command)

    log("--- settings ---")
    for cvar in ("r.GenerateMeshDistanceFields", "r.DynamicGlobalIlluminationMethod",
                 "r.DistanceFields.SurfaceBiasExpand", "r.DistanceFields.MaxObjectBoundingRadius"):
        cmd(cvar)

    log("--- actors in the lab ---")
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        component = actor.get_component_by_class(unreal.StaticMeshComponent)
        mesh_name = "-"
        if component is not None:
            mesh = component.get_editor_property("static_mesh")
            if mesh is not None:
                mesh_name = mesh.get_name()
        scale = actor.get_actor_scale3d()
        log("  %-26s %-22s scale %.2f/%.2f/%.3f"
            % (actor.get_actor_label(), mesh_name, scale.x, scale.y, scale.z))

    log("--- atlas ---")
    cmd("r.DistanceFields.LogAtlasStats 1")
    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
