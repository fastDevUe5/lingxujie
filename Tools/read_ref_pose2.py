"""Read the imported skeleton's reference pose, with the whole run wrapped.

The previous version logged nothing at all, which means it failed before its first log call or the
module did not load. This wraps everything and reports the exception text so the next step is
informed by an error message rather than by silence.

    py "Tools/read_ref_pose2.py"
"""

import unreal

MESH = "/Game/Moxiang/Skeletal/Characters/boss001/SkeletalMeshes/SK_Boss001.SK_Boss001"


def log(text):
    unreal.log("[LingXuJie] RP2: %s" % text)


def run():
    mesh = unreal.EditorAssetLibrary.load_asset(MESH)
    log("mesh loaded: %s" % (mesh is not None))
    if mesh is None:
        return

    try:
        skeleton = mesh.get_editor_property("skeleton")
        log("skeleton: %s" % (skeleton.get_name() if skeleton else "none"))
    except Exception as error:  # noqa: BLE001
        log("reading skeleton property failed: %s" % error)
        return
    if skeleton is None:
        return

    pose = None
    try:
        pose = unreal.AnimPoseExtensions.get_reference_pose(skeleton)
        log("reference pose type: %s" % type(pose).__name__)
    except Exception as error:  # noqa: BLE001
        log("get_reference_pose failed: %r" % error)
        return

    names = []
    try:
        names = list(unreal.AnimPoseExtensions.get_bone_names(pose) or [])
        log("bones in pose: %d" % len(names))
        log("first: %s" % names[:10])
    except Exception as error:  # noqa: BLE001
        log("get_bone_names failed: %r" % error)

    if not names:
        return

    # Compare a handful of bones with the numbers read out of the .mod.
    expected = {
        "Bone28": (-32.44, 94.35, -11.19),
        "Bone27": (-31.76, 112.12, -15.48),
        "Bone26": (-28.83, 126.99, -19.19),
        "Bone25": (-21.95, 143.83, -17.52),
    }
    for bone_name, source in expected.items():
        if bone_name not in names:
            log("  %-8s not in pose" % bone_name)
            continue
        try:
            try:
                transform = unreal.AnimPoseExtensions.get_bone_pose(
                    pose, bone_name, unreal.AnimPoseSpaces.WORLD)
            except Exception:
                transform = unreal.AnimPoseExtensions.get_bone_pose(pose, bone_name)
            t = transform.translation
            log("  %-8s engine (%8.2f, %8.2f, %8.2f)  file (%8.2f, %8.2f, %8.2f)"
                % (bone_name, t.x, t.y, t.z, source[0], source[1], source[2]))
        except Exception as error:  # noqa: BLE001
            log("  %-8s read failed: %r" % (bone_name, error))

    # Overall spread of the reference pose.
    xs, ys, zs = [], [], []
    for bone_name in names:
        try:
            try:
                transform = unreal.AnimPoseExtensions.get_bone_pose(
                    pose, bone_name, unreal.AnimPoseSpaces.WORLD)
            except Exception:
                transform = unreal.AnimPoseExtensions.get_bone_pose(pose, bone_name)
            t = transform.translation
            xs.append(t.x)
            ys.append(t.y)
            zs.append(t.z)
        except Exception:  # noqa: BLE001
            continue
    if xs:
        log("reference pose span: X %.1f Y %.1f Z %.1f cm"
            % (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)))


try:
    run()
    log("ok")
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
