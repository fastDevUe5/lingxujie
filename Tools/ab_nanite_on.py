"""Reading round: a proper Nanite A/B, done the way the noise investigation says it must be done.

The earlier attempt failed because the editor world was not ready, and the failure exposed a noise floor of
five to eight percent that every previous pixel comparison had ignored. This repeats the Nanite test with
that controlled: hide the volumetric clouds so nothing in the frame animates, confirm the floor is low, then
toggle r.Nanite and compare.

The main level is used because the practice scene's basic shapes are not Nanite meshes.

    py "Tools/ab_nanite_on.py"
"""

import unreal

MAIN = "/Game/Maps/LingXuJie"


def log(text):
    unreal.log("[LingXuJie] AB: %s" % text)


def main():
    level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

    if level_subsystem.is_in_play_in_editor():
        level_subsystem.editor_request_end_play()
        log("end play requested -- rerun after it ends")
        return

    current = level_subsystem.get_current_level()
    if (current.get_name() if current else "") != "LingXuJie":
        if not level_subsystem.load_level(MAIN):
            log("could not load the main level")
            return
        log("loaded the main level")

    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    if world is None:
        log("no editor world yet -- rerun")
        return

    # Does this level animate anything on its own?
    clouds = 0
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if "Cloud" in actor.__class__.__name__:
            clouds += 1
    log("volumetric cloud actors in the level: %d" % clouds)

    # Freeze the variables that made the practice scene noisy.
    unreal.SystemLibrary.execute_console_command(world, "r.VolumetricCloud 0")
    unreal.SystemLibrary.execute_console_command(world, "r.Nanite 1")
    unreal.SystemLibrary.execute_console_command(world, "r.Nanite")
    unreal.SystemLibrary.execute_console_command(world, "r.VolumetricCloud")

    log("clouds off, nanite on -- capture A now")
    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
