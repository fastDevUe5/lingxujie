"""Step two: read the single-node animation data directly instead of a derived getter.

get_play_rate returned zero, which could mean the rate really is zero or could mean there is no
instance to ask. The struct holds the truth, so this dumps every field of it and compares the two boss
actors, then checks whether the animation asset itself carries usable data.

    py "Tools/diag_anim_step2.py"
"""

import unreal


def log(text):
    unreal.log("[LingXuJie] D2: %s" % text)


def dump_struct(value, prefix):
    """Print every field of a struct by name, since repr truncates."""
    if value is None:
        log("%s = None" % prefix)
        return
    log("%s type = %s" % (prefix, type(value).__name__))
    for name in dir(value):
        if name.startswith("_"):
            continue
        try:
            attribute = getattr(value, name)
        except Exception:  # noqa: BLE001
            continue
        if callable(attribute):
            continue
        log("    %s.%s = %r" % (prefix, name, attribute))


def main():
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    bosses = [a for a in actors
              if "BOSS" in a.get_actor_label().upper() and "STATIC" not in a.get_actor_label().upper()]
    log("found %d boss actor(s)" % len(bosses))

    for boss in bosses[:2]:
        log("========== %r ==========" % boss.get_actor_label())
        component = boss.get_component_by_class(unreal.SkeletalMeshComponent)
        if component is None:
            log("no skeletal component")
            continue

        data = component.get_editor_property("animation_data")
        dump_struct(data, "animation_data")

        # The derived getters, for contrast with the struct above.
        for name in ("get_play_rate", "is_playing"):
            try:
                attribute = getattr(component, name)
                log("component.%s() = %r" % (name, attribute()))
            except Exception as error:  # noqa: BLE001
                log("component.%s() raised: %r" % (name, error))

        # Does the animation asset itself hold usable data?
        try:
            anim = data.get_editor_property("anim_to_play")
            log("anim_to_play = %r" % (anim.get_path_name() if anim else None))
            if anim:
                for getter in ("get_play_length", "get_number_of_frames"):
                    try:
                        log("    %s() = %r" % (getter, getattr(anim, getter)()))
                    except Exception as error:  # noqa: BLE001
                        log("    %s unavailable: %r" % (getter, error))
        except Exception as error:  # noqa: BLE001
            log("anim_to_play raised: %r" % error)

        # How many bones does the component see? This is the mesh actually driving the skeleton.
        try:
            num = component.get_num_bones()
            log("component.get_num_bones() = %r" % num)
            if num and num > 0:
                log("    bone 0 = %r" % component.get_bone_name(0))
                log("    bone %d = %r" % (num - 1, component.get_bone_name(num - 1)))
        except Exception as error:  # noqa: BLE001
            log("get_num_bones raised: %r" % error)

    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
