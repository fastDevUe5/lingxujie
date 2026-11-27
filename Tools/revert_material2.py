"""Restore MX_BOSS001_STATIC to WorldGridMaterial, the state the verification found it in.

clear_material_override does not exist on the component in this build, so the previous attempt failed
and the material is still assigned. Assigning the default material back is simpler and produces the
same end state.

    py "Tools/revert_material2.py"
"""

LABEL = "MX_BOSS001_STATIC"
DEFAULT_MATERIAL = "/Engine/EngineMaterials/WorldGridMaterial.WorldGridMaterial"


def main():
    import unreal

    def log(text):
        unreal.log("[LingXuJie] REV: %s" % text)

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

    current = component.get_material(0)
    log("current: %r" % (current.get_name() if current else None))
    if current is not None and "WorldGrid" in current.get_name():
        log("already restored")
        return

    default = unreal.load_asset(DEFAULT_MATERIAL)
    if default is None:
        log("could not load %s" % DEFAULT_MATERIAL)
        return

    count = component.get_num_materials()
    for slot in range(count):
        component.set_material(slot, default)

    after = component.get_material(0)
    log("after: %r" % (after.get_name() if after else None))
    log("restored: %s" % (after is not None and "WorldGrid" in after.get_name()))


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    unreal.log_error("[LingXuJie] REV: FATAL %r" % error)
    unreal.log_error(traceback.format_exc())


