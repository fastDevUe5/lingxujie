"""Assign the boss material to all forty slots.

All forty material blocks name the same texture - boss_mob01.tga - so the parts differ by UV region
rather than by image. That makes the assignment simple: one material onto every slot.

    py "Tools/assign_all_slots.py"
"""

import unreal

MAT = "/Game/Moxiang/Materials/M_Boss_Mob01"
MESH = "/Game/Moxiang/Skeletal/Characters/boss001/SkeletalMeshes/SK_Boss001.SK_Boss001"
LABEL = "MX_BOSS001"


def log(text):
    unreal.log("[LingXuJie] ALLSLOT: %s" % text)


def main():
    material = unreal.EditorAssetLibrary.load_asset(MAT)
    if material is None:
        log("material missing")
        return
    mesh = unreal.EditorAssetLibrary.load_asset(MESH)
    if mesh is None:
        log("mesh missing")
        return

    slots = mesh.get_editor_property("materials")
    log("mesh has %d slot(s)" % len(slots))

    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actor = None
    for candidate in subsystem.get_all_level_actors():
        if candidate.get_actor_label() == LABEL:
            actor = candidate
            break
    if actor is None:
        log("actor not found")
        return
    component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
    if component is None:
        log("no component")
        return

    applied = 0
    failed = 0
    for index in range(len(slots)):
        try:
            component.set_material(index, material)
            applied += 1
        except Exception as error:  # noqa: BLE001
            failed += 1
            if failed <= 3:
                log("slot %d failed: %r" % (index, error))
    log("assigned to %d of %d slots (%d failed)" % (applied, len(slots), failed))

    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    log("level saved")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
