"""Reading round, practice: change the two scattering scales and see what they do.

The page explains that Rayleigh scattering depends strongly on wavelength and is why the sky looks blue and
sunsets red, while Mie scattering comes from larger particles and makes the sky hazy with a bright halo
around the sun. Both scales are readable on this scene's component at their Earth defaults. This sets each
one in turn and captures, so the descriptions become pictures.

The scene is saved afterwards with the defaults restored.

    py "Tools/sky_set_%.0f.py" is not used; a single script takes the mode from a marker file instead.
"""

import unreal

SCENE = "/Game/Learning/L_Scene01"
MARKER = "C:/Users/tk/Desktop/lingxujie/Saved/sky_mode.txt"


def log(text):
    unreal.log("[LingXuJie] SKY3: %s" % text)


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

    mode = "default"
    try:
        mode = open(MARKER, encoding="utf-8").read().strip() or "default"
    except OSError:
        pass

    profiles = {
        "default": (0.0331, 0.003996, "Earth defaults"),
        "hazy":    (0.0331, 0.05,     "Mie x12.5: heavy haze"),
        "blue":    (0.15,   0.003996, "Rayleigh x4.5: thick atmosphere"),
        "clean":   (0.0331, 0.0005,   "Mie x0.125: crisp air"),
    }
    rayleigh, mie, label = profiles.get(mode, profiles["default"])

    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if actor.__class__.__name__ != "SkyAtmosphere":
            continue
        component = actor.get_component_by_class(unreal.SkyAtmosphereComponent)
        if component is None:
            continue
        component.set_editor_property("rayleigh_scattering_scale", rayleigh)
        component.set_editor_property("mie_scattering_scale", mie)
        log("mode %-8s -> rayleigh %.4f mie %.5f (%s)"
            % (mode, component.get_editor_property("rayleigh_scattering_scale"),
               component.get_editor_property("mie_scattering_scale"), label))

    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
