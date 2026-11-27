"""Case 005: does the order of the two assignments matter.

The engine starts an animation from the AnimToPlay property-change handler, which calls PlayAnimation.
PlayAnimation drives a single-node instance, and switching the mode to AnimationBlueprint with no
AnimClass destroys that instance. So setting the animation first and the mode second should end up
with a destroyed instance and nothing playing.

Testing both orders on the same actor, and restoring afterwards, settles whether the order in the
written fix is load-bearing or merely tidy.

    py "Tools/diag_order_step1.py"
"""

import unreal

TAG = "ORDER"


def log(text):
    unreal.log("[LingXuJie] %s: %s" % (TAG, text))


def bone_pos(component):
    name = component.get_bone_name(10)
    try:
        return component.get_bone_transform(name).translation
    except Exception:  # noqa: BLE001
        return None


def sample(component, data, position):
    data.set_editor_property("saved_position", position)
    component.set_editor_property("animation_data", data)
    return bone_pos(component)


def measure(component, anim, order):
    """Assign mode and animation in the given order, then sample two positions."""
    data = component.get_editor_property("animation_data")
    data.set_editor_property("anim_to_play", None)
    component.set_editor_property("animation_data", data)
    component.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)

    data = component.get_editor_property("animation_data")

    if order == "mode_first":
        component.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
        data.set_editor_property("anim_to_play", anim)
        data.set_editor_property("saved_playing", True)
        data.set_editor_property("saved_play_rate", 1.0)
        component.set_editor_property("animation_data", data)
    else:
        data.set_editor_property("anim_to_play", anim)
        data.set_editor_property("saved_playing", True)
        data.set_editor_property("saved_play_rate", 1.0)
        component.set_editor_property("animation_data", data)
        component.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)

    refresh = component.get_editor_property("animation_data")
    first = sample(component, refresh, 0.0)
    second = sample(component, refresh, 0.5)

    if first is None or second is None:
        log("%-12s could not sample" % order)
        return None

    delta = (abs(first.x - second.x) + abs(first.y - second.y) + abs(first.z - second.z))
    moved = delta > 0.1
    log("%-12s t=0 (%.1f, %.1f, %.1f)  t=0.5 (%.1f, %.1f, %.1f)  moved=%s"
        % (order, first.x, first.y, first.z, second.x, second.y, second.z, moved))
    return moved


def main():
    actor = None
    for candidate in unreal.EditorLevelLibrary.get_all_level_actors():
        if candidate.get_actor_label() == "MX_BOSS001":
            actor = candidate
            break
    if actor is None:
        log("MX_BOSS001 not found")
        return

    component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
    if component is None:
        log("no skeletal component")
        return

    anim = None
    reg = unreal.AssetRegistryHelpers.get_asset_registry()
    for asset in reg.get_assets_by_path("/Game/Moxiang/Skeletal/Characters/boss001", True, False):
        if str(asset.asset_class_path.asset_name) == "AnimSequence":
            anim = unreal.load_asset("%s.%s" % (asset.package_name, asset.asset_name))
            break
    if anim is None:
        log("no animation found")
        return
    log("animation: %s" % anim.get_name())

    saved_mode = component.get_editor_property("animation_mode")
    saved_data = component.get_editor_property("animation_data")
    saved_anim = saved_data.get_editor_property("anim_to_play")

    log("--- testing both orders ---")
    mode_first = measure(component, anim, "mode_first")
    anim_first = measure(component, anim, "anim_first")

    log("")
    log("mode first: animation moved the bone = %s" % mode_first)
    log("anim first: animation moved the bone = %s" % anim_first)
    if mode_first and not anim_first:
        log("VERDICT: the order matters - assign the mode before the animation")
    elif mode_first and anim_first:
        log("VERDICT: the order does not matter here")
    else:
        log("VERDICT: inconclusive; neither order drove the bone")

    # Restore.
    component.set_editor_property("animation_mode", saved_mode)
    restored = component.get_editor_property("animation_data")
    restored.set_editor_property("anim_to_play", saved_anim)
    component.set_editor_property("animation_data", restored)
    log("restored")

    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
