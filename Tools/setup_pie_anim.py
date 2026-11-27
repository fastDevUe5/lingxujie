"""Put the boss in single-node playback, looping, so PIE can show whether it animates.

The previous round could not detect motion from the editor because nothing ticks the animation
outside play mode. Set the clip up and let the engine play it: start PIE, wait, look. If the mesh
moves between two captures, the animation works, and if it does not, the state is worth reporting.

    py "Tools/setup_pie_anim.py"
"""

import unreal

ANIM = ("/Game/Moxiang/Skeletal/Characters/boss001/SkeletalMeshes/"
        "SK_Boss001_Anim.SK_Boss001_Anim")
LABEL = "MX_BOSS001"


def log(text):
    unreal.log("[LingXuJie] PIEA: %s" % text)


def main():
    anim = unreal.EditorAssetLibrary.load_asset(ANIM)
    if anim is None:
        log("animation missing")
        return
    log("animation %s, %.3f s"
        % (anim.get_name(), anim.get_editor_property("sequence_length")))

    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actor = None
    for candidate in subsystem.get_all_level_actors():
        if candidate.get_actor_label() == LABEL:
            actor = candidate
            break
    if actor is None:
        log("actor not found")
        return

    component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
    if component is None:
        log("no component")
        return

    component.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    log("mode %s" % component.get_animation_mode())

    instance = component.get_anim_instance()
    if instance is None:
        log("no instance")
        return
    instance.set_animation_asset(anim)
    try:
        instance.set_looping(True)
        log("looping enabled")
    except Exception as error:  # noqa: BLE001
        log("set_looping failed: %r" % error)
    try:
        instance.set_play_rate(1.0)
    except Exception:  # noqa: BLE001
        pass
    try:
        instance.set_playing(True)
        log("playing")
    except Exception as error:  # noqa: BLE001
        log("set_playing failed: %r" % error)

    # Report the instance state so the next step knows what is actually set.
    for attribute in ("get_playing", "get_length", "get_current_asset"):
        method = getattr(instance, attribute, None)
        if method is None:
            log("  %-20s not available" % attribute)
            continue
        try:
            log("  %-20s %s" % (attribute, method()))
        except Exception as error:  # noqa: BLE001
            log("  %-20s failed: %r" % (attribute, error))

    level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    level.save_current_level()
    log("level saved")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
