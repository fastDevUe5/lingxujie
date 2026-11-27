"""Play the animation and detect motion from the component's bounds.

Reading individual bones hangs the Python thread, but the component reports its bounds, and a pose
that changes moves those bounds. So: put the component in single-node mode, assign the sequence, step
the position, and read the bounds at each step. If the numbers move, the animation is driving the
skeleton.

    py "Tools/play_and_measure.py"
"""

import unreal

ANIM = ("/Game/Moxiang/Skeletal/Characters/boss001/SkeletalMeshes/"
        "SK_Boss001_Anim.SK_Boss001_Anim")
MESH = "/Game/Moxiang/Skeletal/Characters/boss001/SkeletalMeshes/SK_Boss001.SK_Boss001"
LABEL = "MX_BOSS001"


def log(text):
    unreal.log("[LingXuJie] PAM: %s" % text)


def find_component():
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for actor in subsystem.get_all_level_actors():
        if actor.get_actor_label() == LABEL:
            return actor.get_component_by_class(unreal.SkeletalMeshComponent)
    return None


def bounds_of(component):
    box = component.bounds
    origin = box.origin
    extent = box.box_extent
    return (origin.x, origin.y, origin.z, extent.x, extent.y, extent.z)


def main():
    component = find_component()
    if component is None:
        log("actor not found")
        return
    log("component found; current mode %s" % component.get_animation_mode())

    anim = unreal.EditorAssetLibrary.load_asset(ANIM)
    if anim is None:
        log("animation missing at %s" % ANIM)
        return
    log("animation: %s, length %.3f s"
        % (anim.get_name(), anim.get_editor_property("sequence_length")))

    # Bounds before touching the animation.
    before = bounds_of(component)
    log("bounds before: origin (%.1f, %.1f, %.1f) extent (%.1f, %.1f, %.1f)" % before)

    # Single-node mode is the way to play one sequence without an animation blueprint.
    component.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    log("mode now %s" % component.get_animation_mode())

    instance = component.get_anim_instance()
    log("anim instance: %s" % (type(instance).__name__ if instance else "none"))
    if instance is None:
        log("no anim instance; cannot drive the sequence")
        return

    try:
        instance.set_animation(anim)
        log("animation assigned to the instance")
    except Exception as error:  # noqa: BLE001
        log("set_animation failed: %r" % error)

    samples = []
    for position in (0.0, 0.4, 0.85, 1.3, 1.7):
        try:
            instance.set_position(position, False)
        except Exception as error:  # noqa: BLE001
            log("set_position(%.2f) failed: %r" % (position, error))
            break
        try:
            instance.set_playing(False)
        except Exception:  # noqa: BLE001
            pass
        box = bounds_of(component)
        samples.append((position, box))
        log("at %.2f s: origin (%.2f, %.2f, %.2f) extent (%.2f, %.2f, %.2f)"
            % (position, box[0], box[1], box[2], box[3], box[4], box[5]))

    if len(samples) >= 2:
        first = samples[0][1]
        deltas = [max(abs(s[1][i] - first[i]) for i in range(6)) for s in samples[1:]]
        log("largest change across the samples: %.3f" % max(deltas))
        if max(deltas) > 0.01:
            log("VERDICT: the animation moves the mesh")
        else:
            log("VERDICT: bounds did not change; either the sequence is static or it is not driving")
            log("the skeleton. A static sequence would show identical numbers at every position.")

    # Put the viewport back where the person expects it.
    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
