"""Bisect which AnimPoseExtensions call blocks.

The full script produced no output and then timed out, so something inside it never returns. Logging
before and after each call identifies the culprit, and if the hang is in obtaining the pose at all,
that tells us the API needs an argument this code is not giving it.

    py "Tools/probe_pose_steps.py"
"""

import unreal

MESH = "/Game/Moxiang/Skeletal/Characters/boss001/SkeletalMeshes/SK_Boss001.SK_Boss001"


def log(text):
    unreal.log("[LingXuJie] STEP: %s" % text)


log("start")

mesh = unreal.EditorAssetLibrary.load_asset(MESH)
log("load_asset returned %s" % (mesh is not None))

skeleton = None
try:
    skeleton = mesh.get_editor_property("skeleton")
    log("skeleton property read: %s" % (skeleton.get_name() if skeleton else "none"))
except Exception as error:  # noqa: BLE001
    log("skeleton property failed: %r" % error)

log("about to inspect AnimPoseExtensions signature")
extensions = unreal.AnimPoseExtensions
for name in ("get_reference_pose", "get_bone_names", "get_bone_pose", "get_ref_bone_pose"):
    method = getattr(extensions, name, None)
    log("  %s present: %s" % (name, method is not None))

log("about to call get_reference_pose")
pose = None
try:
    pose = extensions.get_reference_pose(skeleton)
    log("get_reference_pose returned %r" % (pose,))
except Exception as error:  # noqa: BLE001
    log("get_reference_pose raised: %r" % error)

if pose is not None:
    log("about to call get_bone_names")
    try:
        names = list(extensions.get_bone_names(pose) or [])
        log("get_bone_names returned %d names, first: %s" % (len(names), names[:6]))
    except Exception as error:  # noqa: BLE001
        log("get_bone_names raised: %r" % error)

log("end")
