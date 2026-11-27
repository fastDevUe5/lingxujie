"""Measure animation motion through the actor's bounds.

A SkeletalMeshComponent has no bounds property in Python, but the actor it belongs to does. Bounds
change when the pose changes, so the actor's bounds are just as good a signal.

    py "Tools/play_and_measure2.py"
"""

import unreal

ANIM = ("/Game/Moxiang/Skeletal/Characters/boss001/SkeletalMeshes/"
        "SK_Boss001_Anim.SK_Boss001_Anim")
LABEL = "MX_BOSS001"


def log(text):
    unreal.log("[LingXuJie] PAM2: %s" % text)


def find_actor():
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for actor in subsystem.get_all_level_actors():
        if actor.get_actor_label() == LABEL:
            return actor
    return None


def main():
    actor = find_actor()
    if actor is None:
        log("actor not found")
        return
    component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
    if component is None:
        log("no component")
        return

    log("mode before: %s" % component.get_animation_mode())

    anim = unreal.EditorAssetLibrary.load_asset(ANIM)
    if anim is None:
        log("animation missing")
        return
    log("animation %s length %.3f s"
        % (anim.get_name(), anim.get_editor_property("sequence_length")))

    def measure(tag):
        try:
            origin, extent = actor.get_actor_bounds(False)
            log("%-10s origin (%.2f, %.2f, %.2f) extent (%.2f, %.2f, %.2f)"
                % (tag, origin.x, origin.y, origin.z, extent.x, extent.y, extent.z))
            return (origin.x, origin.y, origin.z, extent.x, extent.y, extent.z)
        except Exception as error:  # noqa: BLE001
            log("%-10s bounds failed: %r" % (tag, error))
            return None

    before = measure("before")

    component.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    log("mode after: %s" % component.get_animation_mode())

    instance = component.get_anim_instance()
    log("instance: %s" % (type(instance).__name__ if instance else "none"))
    if instance is None:
        log("no instance; stopping")
        return

    try:
        instance.set_animation_asset(anim)
        log("animation assigned")
    except Exception as error:  # noqa: BLE001
        log("set_animation failed: %r" % error)

    samples = []
    for position in (0.0, 0.5, 1.0, 1.6, 2.2, 3.0):
        try:
            instance.set_playing(False)
            instance.set_position(position, False)
        except Exception as error:  # noqa: BLE001
            log("position %.2f failed: %r" % (position, error))
            break
        box = measure("at %.1fs" % position)
        if box:
            samples.append((position, box))

    if len(samples) >= 2:
        first = samples[0][1]
        worst = max(max(abs(s[1][i] - first[i]) for i in range(6)) for s in samples[1:])
        log("largest bounds change: %.4f" % worst)
        if worst > 0.01:
            log("VERDICT: the animation does move the mesh")
        else:
            log("VERDICT: bounds identical at every position")

    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())

