"""Merge the city's building actors into one mesh, and measure what it does to the count.

Ninety-six material groups arrived as ninety-six separate actors. That is correct for texturing and
wrong for everything else: ninety-six actors means ninety-six draw calls, ninety-six entries in the
outliner, and ninety-six things to select when moving the city.

The engine has a merge operation for exactly this. The interesting question is not whether it works
but what it costs - a merged mesh cannot have per-group materials swapped independently, so the
merged asset carries all of them in slots.

    py "Tools/merge_buildings.py"
"""

import unreal


def log(text):
    unreal.log("[LingXuJie] MERGE: %s" % text)


def main():
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = [a for a in subsystem.get_all_level_actors()
              if a.get_actor_label().startswith("MX_LZ_")]
    log("found %d building actors" % len(actors))
    if not actors:
        log("nothing to merge")
        return

    # What they reference, before the merge changes it.
    mesh_count = 0
    material_count = 0
    triangle_total = 0
    for actor in actors:
        component = actor.get_component_by_class(unreal.StaticMeshComponent)
        if component is None:
            continue
        mesh = component.get_editor_property("static_mesh")
        if mesh is not None:
            mesh_count += 1
            try:
                triangle_total += unreal.StaticMeshEditorSubsystem().get_triangle_count(mesh) \
                    if hasattr(unreal, "StaticMeshEditorSubsystem") else 0
            except Exception:  # noqa: BLE001
                pass
        for index in range(component.get_num_materials()):
            if component.get_material(index) is not None:
                material_count += 1

    log("distinct meshes %d, material slots assigned %d" % (mesh_count, material_count))

    options = unreal.MergeStaticMeshActorsOptions()
    options.base_package_name = "/Game/Moxiang/Merged/SM_Lanzhou_City"
    options.new_actor_label = "MX_LANZHOU_MERGED"
    options.destroy_source_actors = False
    options.spawn_merged_actor = True

    level_path = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level().get_path_name()
    log("merging in %s" % level_path)

    # The merge lives on the static mesh editor subsystem; EditorLevelLibrary has no such call.
    subsystem_meshes = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    try:
        merged = subsystem_meshes.merge_static_mesh_actors(actors, options)
    except Exception as error:  # noqa: BLE001
        log("merge failed: %s" % error)
        return

    log("merge returned %s" % (merged.get_name() if merged else "None"))
    if merged is not None:
        component = merged.get_component_by_class(unreal.StaticMeshComponent)
        if component is not None:
            mesh = component.get_editor_property("static_mesh")
            log("merged mesh %s, material slots %d"
                % (mesh.get_name() if mesh else "none", component.get_num_materials()))

    level_editor = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    level_editor.save_current_level()

    remaining = [a for a in subsystem.get_all_level_actors()
                 if a.get_actor_label().startswith("MX_LZ_")]
    log("after merge: %d MX_LZ_ actors remain (originals kept), +1 merged"
        % len(remaining))


main()
