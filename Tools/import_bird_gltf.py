"""Import the exported glTF as a skeletal mesh, trying the interchange path.

SkeletalMeshTools.import_file pins the FBX factory, which rejects glTF outright. The asset toolset's
own import helper leaves the factory unset so the engine can pick, which is the path that reaches
Interchange - and Interchange is what supports glTF.

This calls the same code that helper calls, from inside the editor.

    py "Tools/import_bird_gltf.py"
"""

import os

import unreal

SOURCE = "C:/Users/tk/Desktop/lingxujie/Assets/Moxiang/ue_import/bird.gltf"
FOLDER = "/Game/Moxiang/Skeletal"
NAME = "SK_Bird"


def log(text):
    unreal.log("[LingXuJie] GLTF: %s" % text)


def main():
    if not os.path.exists(SOURCE):
        log("source missing: %s" % SOURCE)
        return

    # Clear any earlier attempt so the import does not refuse to overwrite.
    existing = "%s/%s.%s" % (FOLDER, NAME, NAME)
    if unreal.EditorAssetLibrary.does_asset_exist("%s/%s" % (FOLDER, NAME)):
        unreal.EditorAssetLibrary.delete_asset("%s/%s" % (FOLDER, NAME))
        log("removed the earlier attempt")

    task = unreal.AssetImportTask()
    task.filename = SOURCE
    task.destination_path = FOLDER
    task.destination_name = NAME
    task.automated = True
    task.save = True
    task.replace_existing = True
    # Deliberately no factory: let the engine choose, which reaches Interchange for glTF.

    log("importing %s" % os.path.basename(SOURCE))
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

    created = [asset.get_name() for asset in (task.imported_object_paths or [])]
    log("imported paths: %s" % created)

    for path in (task.imported_object_paths or []):
        asset = unreal.EditorAssetLibrary.load_asset(path)
        if asset is None:
            log("  %s -> could not load" % path)
            continue
        log("  %s -> %s" % (path, asset.get_class().get_name()))
        if asset.get_class().get_name() == "SkeletalMesh":
            skeletal = asset
            try:
                log("    skeleton: %s" % skeletal.get_editor_property("skeleton").get_name())
            except Exception as error:  # noqa: BLE001
                log("    skeleton not readable: %s" % error)
            try:
                log("    bones: %d" % len(skeletal.get_editor_property("skeleton")
                                          .get_editor_property("bone_tree")))
            except Exception:  # noqa: BLE001
                pass

    level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    level.save_current_level()
    log("done")


main()
