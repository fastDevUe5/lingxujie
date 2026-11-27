"""Material round 3, cleanup: remove the test cube, restore the cube asset, save, return to the game level.

The engine cube was modified to enable Nanite and a test actor was saved into the level. Both are undone
so the shared engine asset and the practice level are back as they were.

M_LabTex keeps its Nanite override and its usage flag, because those are the findings worth leaving in
place; the test actor is what has to go.

    py "Tools/mat_nanite_cleanup.py"
"""

import unreal

LAB = "/Game/Learning/L_LightLab"
MAIN = "/Game/Maps/LingXuJie"
LABEL = "LXJ_NANITE_TEST"
CUBE = "/Engine/BasicShapes/Cube"


def log(text):
    unreal.log("[LingXuJie] CLEAN: %s" % text)


def main():
    level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

    if level_subsystem.is_in_play_in_editor():
        level_subsystem.editor_request_end_play()
        log("end play requested -- rerun after it ends")
        return

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
    log("removed %d test actor(s)" % removed)
    log("lab actors: %d" % len(unreal.EditorLevelLibrary.get_all_level_actors()))
    log("lab saved: %r" % level_subsystem.save_current_level())

    # The engine cube was switched to Nanite for the test; put it back.
    cube = unreal.load_asset(CUBE)
    if cube is not None:
        try:
            settings = cube.get_editor_property("nanite_settings")
            enabled = settings.get_editor_property("enabled")
            log("cube nanite is currently %r" % enabled)
            if enabled:
                settings.set_editor_property("enabled", False)
                cube.set_editor_property("nanite_settings", settings)
                log("cube nanite restored to %r"
                    % cube.get_editor_property("nanite_settings").get_editor_property("enabled"))
        except Exception as error:  # noqa: BLE001
            log("could not restore the cube: %r" % str(error)[:60])

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
