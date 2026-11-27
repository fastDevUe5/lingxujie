"""Read one bone's position from the reference pose, with each call isolated.

get_reference_pose and get_bone_names both work. The per-bone read is what blocked, so this reads a
single bone three different ways and logs which one returns a number. Once one works, the comparison
against the .mod's matrix answers whether the skeleton came through intact.

    py "Tools/probe_one_bone.py"
"""

import unreal

MESH = "/Game/Moxiang/Skeletal/Characters/boss001/SkeletalMeshes/SK_Boss001.SK_Boss001"


def log(text):
    unreal.log("[LingXuJie] ONE: %s" % text)


mesh = unreal.EditorAssetLibrary.load_asset(MESH)
skeleton = mesh.get_editor_property("skeleton")
pose = unreal.AnimPoseExtensions.get_reference_pose(skeleton)
names = [str(n) for n in (unreal.AnimPoseExtensions.get_bone_names(pose) or [])]
log("bones: %d" % len(names))

target = "Bip01"
if target not in names:
    # Pick something that is there.
    target = names[0]
log("target bone: %s" % target)

# Attempt 1: get_bone_pose with an explicit space.
try:
    transform = unreal.AnimPoseExtensions.get_bone_pose(pose, target, unreal.AnimPoseSpaces.WORLD)
    t = transform.translation
    log("attempt1 get_bone_pose(WORLD): (%8.3f, %8.3f, %8.3f)" % (t.x, t.y, t.z))
except Exception as error:  # noqa: BLE001
    log("attempt1 failed: %r" % error)

# Attempt 2: get_bone_pose with no space argument.
try:
    transform = unreal.AnimPoseExtensions.get_bone_pose(pose, target)
    t = transform.translation
    log("attempt2 get_bone_pose(): (%8.3f, %8.3f, %8.3f)" % (t.x, t.y, t.z))
except Exception as error:  # noqa: BLE001
    log("attempt2 failed: %r" % error)

# Attempt 3: get_ref_bone_pose, which is listed separately and may take the skeleton instead.
for args in ((skeleton, target), (pose, target)):
    try:
        transform = unreal.AnimPoseExtensions.get_ref_bone_pose(*args)
        t = transform.translation
        log("attempt3 get_ref_bone_pose(%s): (%8.3f, %8.3f, %8.3f)"
            % (", ".join(type(a).__name__ for a in args), t.x, t.y, t.z))
        break
    except Exception as error:  # noqa: BLE001
        log("attempt3 with %s failed: %r" % (type(args[0]).__name__, error))

# Attempt 4: the plain library function for a reference pose position.
try:
    position = unreal.AnimPoseExtensions.get_ref_pose_position(skeleton, target)
    log("attempt4 get_ref_pose_position(skeleton, bone): %r" % (position,))
except Exception as error:  # noqa: BLE001
    log("attempt4 failed: %r" % error)

log("done")
