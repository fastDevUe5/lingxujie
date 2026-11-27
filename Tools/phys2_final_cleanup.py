"""Physics round 2, final cleanup: end play, remove every test actor, save, return to the game level.

The cleanup inside step D ran while the level was mid-reload, so it removed nothing. This does it in the
right order with the session already ended.

    py "Tools/phys2_final_cleanup.py"
"""

import unreal

LAB = "/Game/Learning/L_LightLab"
MAIN = "/Game/Maps/LingXuJie"
TEST_LABELS = ("LXJ_PHYS_SPHERE", "LXJ_PHYS_CUBE", "LXJ_PHYS_DAMPED")


def log(text):
    unreal.log("[LingXuJie] FIN: %s" % text)


def main():
    level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

    log("in play: %s" % level_subsystem.is_in_play_in_editor())
    if level_subsystem.is_in_play_in_editor():
        level_subsystem.editor_request_end_play()
        log("end play requested")

    current = level_subsystem.get_current_level()
    name = current.get_name() if current else ""
    log("current level: %r, actors: %d"
        % (name, len(unreal.EditorLevelLibrary.get_all_level_actors())))

    if name != "L_LightLab":
        if not level_subsystem.load_level(LAB):
            log("could not open the lab")
            return
        log("opened the lab")

    removed = 0
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if actor.get_actor_label() in TEST_LABELS:
            unreal.EditorLevelLibrary.destroy_actor(actor)
            removed += 1
            log("  removed %s" % actor.get_actor_label())
    log("removed %d test actor(s)" % removed)
    log("lab actors now: %d" % len(unreal.EditorLevelLibrary.get_all_level_actors()))
    log("lab saved: %r" % level_subsystem.save_current_level())

    if level_subsystem.load_level(MAIN):
        log("reopened the game level, actors: %d"
            % len(unreal.EditorLevelLibrary.get_all_level_actors()))
    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
