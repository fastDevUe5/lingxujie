"""Point the merge at the subsystem that actually owns it.

Reading the shipped SceneTools implementation showed the call: it goes through
StaticMeshEditorSubsystem.merge_static_mesh_actors with MergeStaticMeshActorsOptions, not through
EditorLevelLibrary. That is the fastest way to find a reflected call - read what the engine's own
tools use.

    python Tools/fix_merge_script.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Tools/merge_buildings.py"

OLD = """    try:
        merged = unreal.EditorLevelLibrary.merge_actors(
            actors, "/Game/Moxiang/Merged/SM_Lanzhou_City", replace_source_actors=False,
            options=options)
    except Exception as error:  # noqa: BLE001
        log("merge failed: %s" % error)
        return"""

NEW = """    # The merge lives on the static mesh editor subsystem; EditorLevelLibrary has no such call.
    subsystem_meshes = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    try:
        merged = subsystem_meshes.merge_static_mesh_actors(actors, options)
    except Exception as error:  # noqa: BLE001
        log("merge failed: %s" % error)
        return"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if OLD not in text:
        print("target block not found; already updated?")
        return
    open(PATH, "w", encoding="utf-8").write(text.replace(OLD, NEW))
    print("merge call replaced with the subsystem form")


if __name__ == "__main__":
    main()
