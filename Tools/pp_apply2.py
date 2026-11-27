"""Reading round, practice: attach the post process material using the real field names.

The first attempt failed on two guessed names. Introspection settled it: the container exposes its list as
array, and the entry stores the material in a field called object rather than material. With those, the
volume can actually be given the blendable and the weight can be varied to prove the effect is real.

    weight comes from Saved/pp_weight.txt
"""

import unreal

SCENE = "/Game/Learning/L_Scene01"
MAT = "/Game/Learning/M_PPDesat"
MARKER = "C:/Users/tk/Desktop/lingxujie/Saved/pp_weight.txt"


def log(text):
    unreal.log("[LingXuJie] PP4: %s" % text)


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

    material = unreal.load_asset(MAT)
    if material is None:
        log("material missing")
        return

    weight = 0.0
    try:
        weight = float(open(MARKER, encoding="utf-8").read().strip())
    except (OSError, ValueError):
        pass

    volume = None
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if actor.get_actor_label() == "PostProcess":
            volume = actor
            break
    if volume is None:
        log("no PostProcess actor")
        return

    settings = volume.get_editor_property("settings")
    container = settings.get_editor_property("weighted_blendables")
    entries = container.get_editor_property("array")

    kept = []
    for entry in entries:
        existing = entry.get_editor_property("object")
        if existing is not None and existing.get_name() == material.get_name():
            continue
        kept.append(entry)

    entry = unreal.WeightedBlendable()
    entry.set_editor_property("weight", weight)
    entry.set_editor_property("object", material)
    kept.append(entry)

    container.set_editor_property("array", kept)
    settings.set_editor_property("weighted_blendables", container)
    volume.set_editor_property("settings", settings)
    level_subsystem.save_current_level()

    check = volume.get_editor_property("settings").get_editor_property("weighted_blendables")
    final = check.get_editor_property("array")
    log("blendables now: %d" % len(final))
    for item in final:
        obj = item.get_editor_property("object")
        log("  %-20s weight %.2f"
            % (obj.get_name() if obj else None, item.get_editor_property("weight")))
    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
