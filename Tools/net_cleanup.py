"""Network round 1, cleanup: end the play session and return to the game level.

Nothing was created; the simulated net driver could not start because no game net driver exists. This
only restores the editor.

    py "Tools/net_cleanup.py"
"""

import unreal

MAIN = "/Game/Maps/LingXuJie"


def log(text):
    unreal.log("[LingXuJie] CLEAN: %s" % text)


def main():
    level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

    log("in play: %s" % level_subsystem.is_in_play_in_editor())
    if level_subsystem.is_in_play_in_editor():
        level_subsystem.editor_request_end_play()
        log("end play requested -- rerun after it ends")
        return

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
