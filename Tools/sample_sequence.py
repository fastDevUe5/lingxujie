"""Sample the imported sequence at two times and compare the poses.

Driving a component from Python does not obviously re-evaluate its pose - bounds stayed identical at
every position even after the animation was assigned - so the component is the wrong instrument. The
sequence itself can be sampled: get_anim_pose_at_time returns the pose the clip describes at a given
time, with no component involved. If two times give different bone positions, the clip carries motion
and the import preserved it.

    py "Tools/sample_sequence.py"
"""

import unreal

ANIM = ("/Game/Moxiang/Skeletal/Characters/boss001/SkeletalMeshes/"
        "SK_Boss001_Anim.SK_Boss001_Anim")


def log(text):
    unreal.log("[LingXuJie] SEQ: %s" % text)


def main():
    anim = unreal.EditorAssetLibrary.load_asset(ANIM)
    if anim is None:
        log("sequence missing")
        return
    length = anim.get_editor_property("sequence_length")
    log("sequence %s, length %.3f s" % (anim.get_name(), length))

    extensions = unreal.AnimPoseExtensions
    poses = []
    for fraction in (0.0, 0.25, 0.5, 0.75):
        when = length * fraction
        try:
            pose = extensions.get_anim_pose_at_time(anim, when)
        except Exception as error:  # noqa: BLE001
            log("get_anim_pose_at_time(%.3f) failed: %r" % (when, error))
            continue
        if pose is None:
            log("no pose at %.3f" % when)
            continue
        try:
            names = [str(n) for n in (extensions.get_bone_names(pose) or [])]
        except Exception as error:  # noqa: BLE001
            log("bone names failed: %r" % error)
            continue
        poses.append((when, pose, names))
        log("t=%.3f s: pose with %d bones" % (when, len(names)))

    if len(poses) < 2:
        log("not enough poses; stopping")
        return

    # Compare the first bone's transform across poses.
    reference_names = poses[0][2]
    sample_names = [n for n in reference_names[:6]]
    log("comparing bones: %s" % sample_names)

    per_bone = {}
    for when, pose, names in poses:
        for bone in sample_names:
            if bone not in names:
                continue
            try:
                transform = extensions.get_bone_pose(pose, bone, unreal.AnimPoseSpaces.LOCAL)
                t = transform.translation
                r = transform.rotation
                per_bone.setdefault(bone, []).append((when, t.x, t.y, t.z, r.x, r.y, r.z, r.w))
            except Exception as error:  # noqa: BLE001
                log("  bone %s at %.3f failed: %r" % (bone, when, error))
                break

    moved = 0
    for bone, samples in per_bone.items():
        if len(samples) < 2:
            continue
        first = samples[0]
        worst = max(max(abs(s[i] - first[i]) for i in range(1, 8)) for s in samples[1:])
        log("  %-16s max change across times: %.5f" % (bone, worst))
        if worst > 1e-4:
            moved += 1

    log("")
    log("bones whose transform changes over time: %d of %d sampled" % (moved, len(per_bone)))
    if moved:
        log("VERDICT: the sequence carries motion and the import kept it")
    else:
        log("VERDICT: sampled bones are static across the whole clip")
    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
