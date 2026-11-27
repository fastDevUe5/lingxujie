"""Verify the imported bird: bone count, materials, bounds, and whether the skin bound.

The import produced three assets, which is what a skinned mesh import should produce. This reads
them back to confirm the skeleton actually carries the nine bones from the source, rather than an
empty skeleton with a mesh parented to it.

    py "Tools/verify_bird_import.py"
"""

import unreal

MESH = "/Game/Moxiang/Skeletal/bird/SkeletalMeshes/SK_Bird.SK_Bird"
SKELETON = "/Game/Moxiang/Skeletal/bird/SkeletalMeshes/SK_Bird_Skeleton.SK_Bird_Skeleton"


def log(text):
    unreal.log("[LingXuJie] BIRD: %s" % text)


def main():
    mesh = unreal.EditorAssetLibrary.load_asset(MESH)
    if mesh is None:
        log("mesh missing")
        return
    log("mesh class=%s" % mesh.get_class().get_name())

    try:
        log("lod count=%d" % mesh.get_num_lods())
    except Exception:  # noqa: BLE001
        pass

    skeleton = unreal.EditorAssetLibrary.load_asset(SKELETON)
    if skeleton is not None:
        log("skeleton class=%s" % skeleton.get_class().get_name())
        try:
            bone_tree = skeleton.get_editor_property("bone_tree")
            log("bone count=%d" % len(bone_tree))
            for index, bone in enumerate(bone_tree[:12]):
                try:
                    log("    [%d] %s" % (index, bone.get_editor_property("name")))
                except Exception:  # noqa: BLE001
                    log("    [%d] (name unreadable)" % index)
        except Exception as error:  # noqa: BLE001
            log("bone tree unreadable: %s" % error)

    # The mesh's own skeleton reference.
    try:
        log("mesh skeleton=%s" % mesh.get_editor_property("skeleton").get_name())
    except Exception as error:  # noqa: BLE001
        log("mesh skeleton unreadable: %s" % error)

    # Bounds tell us whether the geometry came through at a sane scale.
    try:
        bounds = mesh.get_bounds()
        log("bounds box extent=(%.1f, %.1f, %.1f)  sphere radius=%.1f"
            % (bounds.box_extent.x, bounds.box_extent.y, bounds.box_extent.z,
               bounds.sphere_radius))
    except Exception as error:  # noqa: BLE001
        log("bounds unreadable: %s" % error)

    # Material slots: the importer warned about a primitive with no material.
    try:
        slots = unreal.SkeletalMeshEditorSubsystem().get_material_slots(mesh) \
            if hasattr(unreal, "SkeletalMeshEditorSubsystem") else []
        log("material slots=%d %s" % (len(slots), slots[:4]))
    except Exception:  # noqa: BLE001
        pass


main()
