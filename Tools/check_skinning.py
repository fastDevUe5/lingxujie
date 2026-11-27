"""Answer one question before any more changes: is skinning actually happening?

Three separate fixes produced the same picture. Rather than guess a fourth time, this asks the
engine what pose the mesh is in. If a bone's world matrix in the component matches the .mod's
NODE_TM matrix, the skeleton came through correctly and the pieces being apart is the model's own
bind pose. If they disagree, the skin is not being applied.

    py "Tools/check_skinning.py"
"""

import unreal

MESH = ("/Game/Moxiang/Skeletal/Characters/boss001/SkeletalMeshes/SK_Boss001.SK_Boss001")
LABEL = "MX_BOSS001"

# From the .mod, for comparison. These are world positions in the source file's centimetres.
EXPECTED = {
    "Bone28": (-32.44, 94.35, -11.19),
    "Bone27": (-31.76, 112.12, -15.48),
    "Bone26": (-28.83, 126.99, -19.19),
    "Bone25": (-21.95, 143.83, -17.52),
}


def log(text):
    unreal.log("[LingXuJie] SKINCHK: %s" % text)


def main():
    mesh = unreal.EditorAssetLibrary.load_asset(MESH)
    if mesh is None:
        log("mesh missing at %s" % MESH)
        return

    # How many bones does the imported skeleton have?
    try:
        skeleton = mesh.get_editor_property("skeleton")
        log("skeleton: %s" % (skeleton.get_name() if skeleton else "none"))
    except Exception as error:  # noqa: BLE001
        log("skeleton unreadable: %s" % error)

    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actor = None
    for candidate in subsystem.get_all_level_actors():
        if candidate.get_actor_label() == LABEL:
            actor = candidate
            break
    if actor is None:
        log("actor %s not in the level" % LABEL)
        return

    component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
    if component is None:
        log("no skeletal mesh component")
        return

    asset = component.get_editor_property("skeletal_mesh")
    log("component mesh: %s" % (asset.get_name() if asset else "none"))

    # The decisive read: where does the component say its bones are?
    for name, expected in EXPECTED.items():
        try:
            matrix = component.get_bone_matrix(name)
        except Exception as error:  # noqa: BLE001
            log("  %-10s unreadable: %s" % (name, error))
            continue
        try:
            translation = matrix.get_editor_property("translation")
            actual = (translation.x, translation.y, translation.z)
        except Exception:  # noqa: BLE001
            translation = matrix.translation if hasattr(matrix, "translation") else None
            actual = (translation.x, translation.y, translation.z) if translation else (0, 0, 0)

        # The component works in Unreal units with the actor's scale applied; the source is
        # centimetres with Y up after conversion, so compare magnitudes loosely first.
        distance = ((actual[0] - expected[0]) ** 2 + (actual[1] - expected[1]) ** 2
                    + (actual[2] - expected[2]) ** 2) ** 0.5
        log("  %-10s got (%8.2f, %8.2f, %8.2f) expected (%8.2f, %8.2f, %8.2f) distance %.1f"
            % (name, actual[0], actual[1], actual[2],
               expected[0], expected[1], expected[2], distance))

    # Are any bones at all away from the origin? If every bone sits at zero, the skeleton collapsed.
    try:
        count = mesh.get_editor_property("skeleton")
        bone_names = []
        if count is not None:
            # Skeleton exposes its bone names through the editor property list.
            for entry in unreal.SkeletonUtilitiesLibrary.get_bone_names(count) or []:
                bone_names.append(str(entry))
    except Exception:  # noqa: BLE001
        bone_names = []

    if bone_names:
        log("bone count: %d, first few: %s" % (len(bone_names), bone_names[:6]))
    else:
        log("bone list unavailable through this API")

    log("interpretation: matching positions mean the skin is intact and the bind pose is what")
    log("renders. Divergence means the pose applied differs from the file.")


main()
