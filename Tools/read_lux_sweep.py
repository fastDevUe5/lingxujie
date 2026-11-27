"""Reading round: the sun in this scene is eight lux, which is not a sun.

The directional light page says intensity is measured in lux, the photometric unit. Direct sunlight is
around a hundred thousand lux and a bright interior is a few hundred. This scene's sun was set to eight,
which under auto exposure still looks like a sunset because the camera compensates. That is worth testing
rather than assuming: setting a physically plausible value and measuring the frame tells you whether the
compensation is total or whether the scene was actually being carried by something else.

    intensities come from Saved/sun_lux.txt
"""

import unreal

SCENE = "/Game/Learning/L_Scene01"
MARKER = "C:/Users/tk/Desktop/lingxujie/Saved/sun_lux.txt"


def log(text):
    unreal.log("[LingXuJie] LUX: %s" % text)


def main():
    level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

    if level_subsystem.is_in_play_in_editor():
        level_subsystem.editor_request_end_play()
        log("end play requested -- rerun after it ends")
        return

    current = level_subsystem.get_current_level()
    if (current.get_name() if current else "") != "L_Scene01":
        if not level_subsystem.load_level(SCENE):
            log("could not load the scene")
            return
        log("loaded L_Scene01")

    intensity = 8.0
    try:
        intensity = float(open(MARKER, encoding="utf-8").read().strip())
    except (OSError, ValueError):
        pass

    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if actor.__class__.__name__ != "DirectionalLight":
            continue
        component = actor.get_component_by_class(unreal.DirectionalLightComponent)
        if component is None:
            continue
        component.set_editor_property("intensity", intensity)
        read_back = component.get_editor_property("intensity")
        try:
            units = component.get_editor_property("intensity_units")
            unit_name = units.name if hasattr(units, "name") else units
        except Exception:  # noqa: BLE001
            unit_name = "unreadable"
        log("intensity %.1f  units %r  mobility %r"
            % (read_back, unit_name, component.get_editor_property("mobility")))

    level_subsystem.save_current_level()
    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
