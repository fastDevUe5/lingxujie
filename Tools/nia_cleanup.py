"""Niagara round 1, cleanup: restore exposure, remove the particle actor, save, return to the game level.

Several console variables were changed for the capture attempts and the particle actor was saved into the
practice level. All of it is undone.

    py "Tools/nia_cleanup.py"
"""

import unreal

LAB = "/Game/Learning/L_LightLab"
MAIN = "/Game/Maps/LingXuJie"
PARTICLE = "LXJ_PARTICLE"
LIGHT = "LXJ_LAB_Light"
LIGHT_INTENSITY = 5000.0


def log(text):
    unreal.log("[LingXuJie] CLEAN: %s" % text)


def main():
    level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)

    log("in play: %s" % level_subsystem.is_in_play_in_editor())
    if level_subsystem.is_in_play_in_editor():
        level_subsystem.editor_request_end_play()
        log("end play requested -- rerun after it finishes")
        return

    current = level_subsystem.get_current_level()
    log("level: %r actors: %d"
        % (current.get_name() if current else None,
           len(unreal.EditorLevelLibrary.get_all_level_actors())))
    if (current.get_name() if current else "") != "L_LightLab":
        if not level_subsystem.load_level(LAB):
            log("could not open the lab")
            return

    removed = 0
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if actor.get_actor_label() == PARTICLE:
            unreal.EditorLevelLibrary.destroy_actor(actor)
            removed += 1
            log("removed the particle actor")
        elif actor.get_actor_label() == LIGHT:
            component = actor.get_component_by_class(unreal.PointLightComponent)
            if component is not None:
                component.set_editor_property("intensity", LIGHT_INTENSITY)
                log("light restored to %.0f" % LIGHT_INTENSITY)
    log("removed %d actor(s)" % removed)
    log("lab actors now: %d" % len(unreal.EditorLevelLibrary.get_all_level_actors()))
    log("saved: %r" % level_subsystem.save_current_level())

    # Put the console variables back to their defaults.
    world = subsystem.get_editor_world()
    if world is not None:
        for cvar, value in (("r.EyeAdaptationQuality", "2"),
                            ("r.DefaultFeature.AutoExposure", "1"),
                            ("r.DefaultFeature.MotionBlur", "1")):
            unreal.SystemLibrary.execute_console_command(world, "%s %s" % (cvar, value))
        log("console variables restored")

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
