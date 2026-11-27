"""Read back the imported AnimSequence and check it against the source timeline.

The source is one hundred thirty-six rotation keys at thirty frames per second, which is four and a
half seconds. If the imported sequence reports that length, then the tick conversion is right and
the animation survived the round trip intact. If it reports something else, the conversion is wrong
and everything downstream would be paced incorrectly.

    py "Tools/verify_bird_anim.py"
"""

import unreal

ANIM = ("/Game/Moxiang/Skeletal/Animated/bird_anim/SkeletalMeshes/"
        "SK_BirdAnim_Anim.SK_BirdAnim_Anim")
MESH = ("/Game/Moxiang/Skeletal/Animated/bird_anim/SkeletalMeshes/"
        "SK_BirdAnim.SK_BirdAnim")


def log(text):
    unreal.log("[LingXuJie] ANIMVERIFY: %s" % text)


def main():
    anim = unreal.EditorAssetLibrary.load_asset(ANIM)
    if anim is None:
        log("animation missing")
        return
    log("class=%s" % anim.get_class().get_name())

    # The library reports length and frame count; the property names differ by version, so try
    # both the editor property and the library call.
    for name in ("sequence_length", "play_length", "rate_scale"):
        try:
            log("  %-16s %s" % (name, anim.get_editor_property(name)))
        except Exception:  # noqa: BLE001
            pass

    library = unreal.AnimationLibrary if hasattr(unreal, "AnimationLibrary") else None
    bp_library = unreal.AnimationBlueprintLibrary
    try:
        length = bp_library.get_sequence_length(anim)
        frames = bp_library.get_num_frames(anim)
        log("  library length=%.4f s  frames=%d" % (length, frames))
        if frames:
            log("  implied frame rate = %.2f fps" % (frames / length if length else 0.0))
    except Exception as error:  # noqa: BLE001
        log("  library read failed: %s" % error)

    # Track names tell us whether the six animated bones carried over.
    try:
        names = bp_library.get_bone_track_names(anim)
        log("  bone tracks=%d: %s" % (len(names), [str(n) for n in names][:12]))
    except Exception as error:  # noqa: BLE001
        log("  track names unreadable: %s" % error)

    # The mesh should reference the same skeleton the animation targets.
    mesh = unreal.EditorAssetLibrary.load_asset(MESH)
    if mesh is not None:
        try:
            log("  mesh skeleton=%s" % mesh.get_editor_property("skeleton").get_name())
        except Exception:  # noqa: BLE001
            pass
    try:
        log("  anim skeleton=%s" % anim.get_editor_property("skeleton").get_name())
    except Exception:  # noqa: BLE001
        pass


main()
