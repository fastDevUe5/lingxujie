"""Material round 1, cleanup: restore a sane light level, save, and return to the game level.

The dark material is kept, because it makes the practice level usable for visual work. The light is set
to a moderate value, since five thousand inside a room that size blows out any view near it.

    py "Tools/mat_cleanup.py"
"""

import unreal

LAB = "/Game/Learning/L_LightLab"
MAIN = "/Game/Maps/LingXuJie"
LIGHT = "LXJ_LAB_Light"
INTENSITY = 1200.0


def log(text):
    unreal.log("[LingXuJie] FIN: %s" % text)


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

    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if actor.get_actor_label() == LIGHT:
            component = actor.get_component_by_class(unreal.PointLightComponent)
            if component is not None:
                log("light was %.0f, setting %.0f"
                    % (component.get_editor_property("intensity"), INTENSITY))
                component.set_editor_property("intensity", INTENSITY)
    log("lab actors: %d" % len(unreal.EditorLevelLibrary.get_all_level_actors()))
    log("saved: %r" % level_subsystem.save_current_level())

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
