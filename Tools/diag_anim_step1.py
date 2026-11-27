"""Step one of a real diagnosis: observe before hypothesising.

A previous round established that setting an animation on a component and calling set_position did not
move the pose. The question now is why, and the first job is to gather facts rather than recall old
conclusions. This lists what the actor actually has, what the animation asset actually contains, and
which bone-reading APIs exist on the component.

    py "Tools/diag_anim_step1.py"
"""

import unreal


def log(text):
    unreal.log("[LingXuJie] D1: %s" % text)


def main():
    # Find the boss actor by looking at what the level actually holds.
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    log("level holds %d actor(s)" % len(actors))

    boss = None
    for actor in actors:
        label = actor.get_actor_label()
        if "BOSS" in label.upper() and "STATIC" not in label.upper():
            log("candidate actor: %r (%s)" % (label, actor.get_class().get_name()))
            if boss is None:
                boss = actor

    if boss is None:
        log("no boss actor found")
        return

    log("--- inspecting %r ---" % boss.get_actor_label())
    component = boss.get_component_by_class(unreal.SkeletalMeshComponent)
    if component is None:
        log("no SkeletalMeshComponent on this actor")
        return

    # What mesh is assigned, and does it resolve?
    mesh = component.get_editor_property("skeletal_mesh_asset")
    log("mesh asset: %r" % (mesh.get_path_name() if mesh else None))
    if mesh is None:
        log("STOP: no mesh assigned")
        return

    # How many bones, and what are the first few named? This tells us the skeleton is real.
    num_bones = mesh.get_num_bones() if hasattr(mesh, "get_num_bones") else None
    log("num bones: %r" % num_bones)

    # What animation is currently set, if any?
    for prop in ("animation_data", "anim_class", "anim_to_play"):
        try:
            value = component.get_editor_property(prop)
            log("component.%s = %r" % (prop, value))
        except Exception as error:  # noqa: BLE001
            log("component.%s unavailable: %r" % (prop, error))

    # Which bone-reading APIs does the component expose? This decides how the next step measures.
    log("--- bone-reading APIs on the component ---")
    for name in sorted(dir(component)):
        lowered = name.lower()
        if "bone" in lowered or "socket" in lowered:
            log("    %s" % name)

    # What does the component think its playback state is?
    log("--- playback state ---")
    for name in ("is_playing", "get_play_rate", "get_position", "playing"):
        try:
            value = getattr(component, name)
            log("    %s -> %r" % (name, value() if callable(value) else value))
        except Exception as error:  # noqa: BLE001
            log("    %s unavailable: %r" % (name, error))

    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
