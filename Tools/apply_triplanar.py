"""Apply the triplanar material to the terrain actor so the result can be seen.

Building the material proves the tools work; assigning it proves the material is correct. Nothing
else in this project has been judged without a screenshot, and that rule applies to a shader just
as much as to a mesh.

    py "Tools/apply_triplanar.py"
"""

import unreal

MATERIAL = "/Game/Moxiang/M_Ground_Triplanar.M_Ground_Triplanar"
TERRAIN_LABEL = "MX_TERRAIN"


def log(text):
    unreal.log("[LingXuJie] APPLY: %s" % text)


def main():
    material = unreal.EditorAssetLibrary.load_asset(MATERIAL)
    if material is None:
        log("material missing")
        return

    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    found = None
    for actor in subsystem.get_all_level_actors():
        if actor.get_actor_label() == TERRAIN_LABEL:
            found = actor
            break
    if found is None:
        log("terrain actor not found")
        return

    component = found.get_component_by_class(unreal.StaticMeshComponent)
    if component is None:
        log("no static mesh component")
        return

    previous = component.get_material(0)
    component.set_material(0, material)
    log("replaced %s with %s"
        % (previous.get_name() if previous else "none", material.get_name()))

    level_editor = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    level_editor.save_current_level()
    log("level saved")


main()
