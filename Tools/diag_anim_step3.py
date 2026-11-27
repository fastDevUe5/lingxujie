"""Verify the animation diagnosis, passing bone names rather than indices.

get_bone_transform takes a name, which the previous attempt learned by failing. Everything else is
unchanged: sample a bone at several animation positions and restore the actor afterwards.

    py "Tools/diag_anim_step3.py"
"""

import unreal


def log(text):
    unreal.log("[LingXuJie] D3: %s" % text)


def snapshot(component, bone_name):
    # One argument only. Passing a BoneSpaces member raises a TypeError for this function in 5.8, and
    # the default is already world space, which is what we want to compare against the actor location.
    transform = component.get_bone_transform(bone_name)
    loc = transform.translation
    return (round(loc.x, 3), round(loc.y, 3), round(loc.z, 3))


def apply_position(component, data, position):
    """Setting the struct then writing it back is what makes the change take effect."""
    data.set_editor_property("saved_position", position)
    component.set_editor_property("animation_data", data)


def main():
    boss = None
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if actor.get_actor_label() == "MX_BOSS001":
            boss = actor
            break
    if boss is None:
        log("MX_BOSS001 not found")
        return

    component = boss.get_component_by_class(unreal.SkeletalMeshComponent)
    if component is None:
        log("no skeletal component")
        return

    num = component.get_num_bones()
    bone_name = component.get_bone_name(10)
    log("bone count: %d, sampling bone 10 = %r" % (num, bone_name))

    before = snapshot(component, bone_name)
    log("bind pose -> %r" % (before,))

    reg = unreal.AssetRegistryHelpers.get_asset_registry()
    anim = None
    for asset in reg.get_assets_by_path("/Game/Moxiang/Skeletal/Characters/boss001", True, False):
        if str(asset.asset_class_path.asset_name) == "AnimSequence":
            full = "%s.%s" % (asset.package_name, asset.asset_name)
            log("found animation: %s" % full)
            anim = unreal.load_asset(full)
            break

    if anim is None:
        log("no AnimSequence found under the boss folder")
        return

    saved_mode = component.get_editor_property("animation_mode")
    saved_data = component.get_editor_property("animation_data")
    saved_anim = saved_data.get_editor_property("anim_to_play")
    log("state before: mode=%r anim=%r" % (saved_mode, saved_anim))

    # The fix hypothesis: without these two lines nothing can ever play.
    component.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    data = component.get_editor_property("animation_data")
    data.set_editor_property("anim_to_play", anim)
    data.set_editor_property("saved_playing", True)
    data.set_editor_property("saved_play_rate", 1.0)
    component.set_editor_property("animation_data", data)
    log("applied single node mode and an animation")

    samples = {}
    for position in (0.0, 0.25, 0.5, 0.75):
        apply_position(component, data, position)
        samples[position] = snapshot(component, bone_name)
        log("  t=%.2f -> %r" % (position, samples[position]))

    distinct = len(set(samples.values()))
    log("distinct poses across four times: %d" % distinct)
    if distinct > 1:
        log("VERDICT: the animation moves the skeleton once it is assigned")
    else:
        log("VERDICT: assigning did not change the pose; the cause is elsewhere")

    # Restore so the level is left as found.
    component.set_editor_property("animation_mode", saved_mode)
    restored = component.get_editor_property("animation_data")
    restored.set_editor_property("anim_to_play", saved_anim)
    component.set_editor_property("animation_data", restored)
    log("restored: mode=%r anim=%r"
        % (component.get_editor_property("animation_mode"),
           component.get_editor_property("animation_data").get_editor_property("anim_to_play")))

    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
