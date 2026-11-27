"""Physics round 1, cleanup: remove the test sphere, save the lab, and return to the game level.

The sphere was saved into the level so the simulation would load it, so it has to be removed and the
level saved again. Then the game level is reopened and the viewport reset, because that is what the
person watching the editor expects to see.

    py "Tools/phys_cleanup.py"
"""

import unreal

LAB = "/Game/Learning/L_LightLab"
MAIN = "/Game/Maps/LingXuJie"
LABEL = "LXJ_PHYS_SPHERE"


def log(text):
    unreal.log("[LingXuJie] CLEAN: %s" % text)


def main():
    level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

    if level_subsystem.is_in_play_in_editor():
        level_subsystem.editor_request_end_play()
        log("end play requested")

    current = level_subsystem.get_current_level()
    if (current.get_name() if current else "") != "L_LightLab":
        if not level_subsystem.load_level(LAB):
            log("could not open the lab")
            return

    removed = 0
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if actor.get_actor_label() == LABEL:
            unreal.EditorLevelLibrary.destroy_actor(actor)
            removed += 1
    log("removed %d test sphere(s)" % removed)
    log("lab saved: %r" % level_subsystem.save_current_level())

    if level_subsystem.load_level(MAIN):
        log("reopened the game level")
        log("actors: %d" % len(unreal.EditorLevelLibrary.get_all_level_actors()))
    else:
        log("could not reopen the game level")

    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
