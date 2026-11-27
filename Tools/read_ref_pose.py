"""Read the imported skeleton's reference pose and compare it with the source file.

The previous attempt used a method that does not exist. The real one is AnimPoseExtensions whose
get_reference_pose returns the skeleton's bind pose, and get_bone_pose reads a single bone out of it.

This is the falsification test: if the imported bones sit where the .mod says they sit, the skeleton
survived the trip and the scattered appearance is the model's own bind pose. If they do not, the
pose in the engine differs from the file and the export is at fault.

    py "Tools/read_ref_pose.py"
"""

import unreal

MESH = "/Game/Moxiang/Skeletal/Characters/boss001/SkeletalMeshes/SK_Boss001.SK_Boss001"

# Bone world positions straight out of the .mod, in its own centimetres, Y up.
EXPECTED = {
    "Bone28": (-32.44, 94.35, -11.19),
    "Bone27": (-31.76, 112.12, -15.48),
    "Bone26": (-28.83, 126.99, -19.19),
    "Bone25": (-21.95, 143.83, -17.52),
}


def log(text):
    unreal.log("[LingXuJie] REFPOSE: %s" % text)


def main():
    mesh = unreal.EditorAssetLibrary.load_asset(MESH)
    if mesh is None:
        log("mesh missing")
        return
    skeleton = mesh.get_editor_property("skeleton")
    log("skeleton: %s" % (skeleton.get_name() if skeleton else "none"))
    if skeleton is None:
        return

    try:
        pose = unreal.AnimPoseExtensions.get_reference_pose(skeleton)
        log("reference pose obtained")
    except Exception as error:  # noqa: BLE001
        log("get_reference_pose failed: %s" % error)
        return

    try:
        names = list(unreal.AnimPoseExtensions.get_bone_names(pose) or [])
        log("bone count in pose: %d" % len(names))
        log("first twelve: %s" % names[:12])
    except Exception as error:  # noqa: BLE001
        log("get_bone_names failed: %s" % error)
        names = []

    for bone_name, expected in EXPECTED.items():
        try:
            transform = unreal.AnimPoseExtensions.get_bone_pose(pose, bone_name, unreal.AnimPoseSpaces.WORLD)
        except Exception as error:  # noqa: BLE001
            log("  %-10s unreadable: %s" % (bone_name, error))
            continue
        try:
            translation = transform.translation
            actual = (translation.x, translation.y, translation.z)
        except AttributeError:
            translation = transform.get_editor_property("translation")
            actual = (translation.x, translation.y, translation.z)

        log("  %-10s engine (%8.2f, %8.2f, %8.2f)" % (bone_name, actual[0], actual[1], actual[2]))
        log("  %-10s file   (%8.2f, %8.2f, %8.2f)" % ("", expected[0], expected[1], expected[2]))
        log("")

    # Also report the overall spread of the reference pose, which is the number to compare with the
    # two metres a character should occupy.
    xs = []
    ys = []
    zs = []
    for bone_name in (names[:80] if names else []):
        try:
            transform = unreal.AnimPoseExtensions.get_bone_pose(
                pose, bone_name, unreal.AnimPoseSpaces.WORLD)
            t = transform.translation
            xs.append(t.x)
            ys.append(t.y)
            zs.append(t.z)
        except Exception:  # noqa: BLE001
            continue
    if xs:
        log("reference pose span: X %.1f, Y %.1f, Z %.1f (engine units, cm)"
            % (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)))
    log("done")


main()
