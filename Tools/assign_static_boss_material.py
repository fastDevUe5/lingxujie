"""Assign the missing material to MX_BOSS001_STATIC, so the change can be photographed.

The actor reports WorldGridMaterial in both its mesh slot and its component, and M_Boss_Mob01 exists in
the project for exactly this model. Assigning it and capturing makes the difference measurable; the
caller reverts afterwards.

    py "Tools/assign_static_boss_material.py"
"""

LABEL = "MX_BOSS001_STATIC"
MATERIAL = "/Game/Moxiang/Materials/M_Boss_Mob01.M_Boss_Mob01"


def main():
    import unreal

    def log(text):
        unreal.log("[LingXuJie] ASSIGN: %s" % text)

    material = unreal.load_asset(MATERIAL)
    if material is None:
        log("could not load %s" % MATERIAL)
        return

    target = None
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if actor.get_actor_label() == LABEL:
            target = actor
            break
    if target is None:
        log("%s not found" % LABEL)
        return

    component = target.get_component_by_class(unreal.StaticMeshComponent)
    if component is None:
        log("no static mesh component")
        return

    before = component.get_material(0)
    log("before: %r" % (before.get_name() if before else None))

    # Every slot, not just zero, because the mesh may have several.
    count = component.get_num_materials()
    log("material slots: %d" % count)
    for slot in range(count):
        component.set_material(slot, material)

    after = component.get_material(0)
    log("after:  %r" % (after.get_name() if after else None))
    log("changed: %s" % (before != after))


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    unreal.log_error("[LingXuJie] ASSIGN: FATAL %r" % error)
    unreal.log_error(traceback.format_exc())
