"""Import the animated bird and report whether an AnimSequence appeared.

A glTF with an animation array should produce a SkeletalMesh, a Skeleton, a PhysicsAsset and at least
one AnimSequence. If only the first three appear, the animation did not survive the import, which is
a different failure from an animation that imported but plays wrongly.

    py "Tools/import_bird_anim.py"
"""

import os

import unreal

SOURCE = "C:/Users/tk/Desktop/lingxujie/Assets/Moxiang/ue_import/bird_anim.gltf"
FOLDER = "/Game/Moxiang/Skeletal/Animated"
NAME = "SK_BirdAnim"


def log(text):
    unreal.log("[LingXuJie] ANIM: %s" % text)


def main():
    if not os.path.exists(SOURCE):
        log("source missing")
        return

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
    # Leave the factory unset so Interchange handles the glTF.

    log("importing %s" % os.path.basename(SOURCE))
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

    paths = list(task.imported_object_paths or [])
    log("import produced %d assets" % len(paths))

    for path in paths:
        asset = unreal.EditorAssetLibrary.load_asset(path)
        if asset is None:
            log("  %s (could not load)" % path)
            continue
        kind = asset.get_class().get_name()
        log("  %-16s %s" % (kind, path))
        if kind == "AnimSequence":
            try:
                log("      length=%.3f s  keys=%d"
                    % (asset.get_editor_property("sequence_length"),
                       asset.get_editor_property("number_of_keys")))
            except Exception as error:  # noqa: BLE001
                log("      (properties unreadable: %s)" % error)

    if not paths:
        log("nothing imported")

    # Also look at the folder, in case paths were not reported.
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    assets = registry.get_assets_by_path(FOLDER, recursive=True)
    log("assets now in %s: %d" % (FOLDER, len(assets)))
    for entry in assets:
        log("  %-16s %s" % (str(entry.asset_class_path.asset_name), str(entry.asset_name)))

    level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    level.save_current_level()
    log("done")


main()
