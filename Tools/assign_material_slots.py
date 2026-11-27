"""Assign the material on the component rather than on the mesh asset.

A SkeletalMesh has no set_material - only a list of materials it was imported with. Overrides belong
to the component, which is where a placement decides what a mesh looks like.

    py "Tools/assign_material_slots.py"
"""

import unreal

MAT = "/Game/Moxiang/Materials/M_Boss_Mob01"
MESH = "/Game/Moxiang/Skeletal/Characters/boss001/SkeletalMeshes/SK_Boss001.SK_Boss001"
LABEL = "MX_BOSS001"


def log(text):
    unreal.log("[LingXuJie] SLOT: %s" % text)


def main():
    material = unreal.EditorAssetLibrary.load_asset(MAT)
    if material is None:
        log("material missing at %s" % MAT)
        return
    log("material: %s" % material.get_name())

    mesh = unreal.EditorAssetLibrary.load_asset(MESH)
    if mesh is None:
        log("mesh missing")
        return

    slots = mesh.get_editor_property("materials")
    log("mesh declares %d slot(s)" % len(slots))

    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actor = None
    for candidate in subsystem.get_all_level_actors():
        if candidate.get_actor_label() == LABEL:
            actor = candidate
            break
    if actor is None:
        log("actor %s not found" % LABEL)
        return

    component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
    if component is None:
        log("no component")
        return

    # Overrides live on the component. Set every slot so no part stays grey.
    applied = 0
    for index in range(len(slots)):
        try:
            component.set_material(index, material)
            applied += 1
        except Exception as error:  # noqa: BLE001
            log("slot %d failed: %r" % (index, error))
    log("applied the material to %d slot(s)" % applied)

    # Also try overriding the mesh's own list, which persists with the asset rather than the actor.
    try:
        mesh.set_editor_property("materials", [material] * len(slots))
        unreal.EditorAssetLibrary.save_asset(MESH)
        log("also wrote the material into the mesh's slot list")
    except Exception as error:  # noqa: BLE001
        log("mesh-level assignment failed: %r" % error)

    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
