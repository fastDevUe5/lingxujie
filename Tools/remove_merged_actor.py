"""Remove the merged duplicate, leaving the level as it was.

The merge proved the operation works and reported the numbers - ninety-six material slots, sixty
four thousand triangles - but the level still builds from the ninety-six separate actors. Keeping
both means two copies of the same geometry in the same place: invisible, but real, and doubled in
any count.

The merged asset stays on disk as evidence; only the actor goes.

    py "Tools/remove_merged_actor.py"
"""

import unreal


def log(text):
    unreal.log("[LingXuJie] CLEAN: %s" % text)


def main():
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    removed = 0
    for actor in list(subsystem.get_all_level_actors()):
        label = actor.get_actor_label()
        component = actor.get_component_by_class(unreal.StaticMeshComponent)
        if component is None:
            continue
        mesh = component.get_editor_property("static_mesh")
        if mesh is None:
            continue
        # The merged actor is the one whose mesh is the merged asset.
        if mesh.get_name() == "SM_SM_Lanzhou_City":
            log("removing %s (mesh %s)" % (label, mesh.get_name()))
            subsystem.destroy_actor(actor)
            removed += 1

    log("removed %d merged actor(s); originals untouched" % removed)

    level_editor = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    level_editor.save_current_level()

    remaining = [a for a in subsystem.get_all_level_actors()
                 if a.get_actor_label().startswith("MX_LZ_")]
    log("MX_LZ_ actors now: %d" % len(remaining))


main()
