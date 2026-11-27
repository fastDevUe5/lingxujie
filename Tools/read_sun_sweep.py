"""Reading round, practice: sweep the sun's elevation and watch the sky colour follow.

The sky atmosphere page attributes sunset colour to Rayleigh scattering removing blue light over a long
path. That claim makes a prediction: as the sun sinks, its light travels through more atmosphere and the sky
should shift from blue toward orange and red. Sweeping one number - the directional light's pitch - is the
cheapest way to test it, and the result is a sequence rather than a single pair.

The light's rotation is restored afterwards.

    angle comes from Saved/sun_angle.txt
"""

import unreal

SCENE = "/Game/Learning/L_Scene01"
MARKER = "C:/Users/tk/Desktop/lingxujie/Saved/sun_angle.txt"


def log(text):
    unreal.log("[LingXuJie] SUN: %s" % text)


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

    angle = -35.0
    try:
        angle = float(open(MARKER, encoding="utf-8").read().strip())
    except (OSError, ValueError):
        pass

    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if actor.__class__.__name__ != "DirectionalLight":
            continue
        actor.set_actor_rotation(
            unreal.Rotator(pitch=angle, yaw=-35.0, roll=0.0), False)
        rotation = actor.get_actor_rotation()
        log("sun pitch %.1f yaw %.1f" % (rotation.pitch, rotation.yaw))

    level_subsystem.save_current_level()
    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
