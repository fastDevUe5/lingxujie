"""Import any exported glTF and report what came out.

Generalised from the bird-specific scripts so the same check runs on a character: how many assets,
which classes, and whether an AnimSequence appeared with a plausible length.

    py "Tools/import_gltf_any.py"
"""

import os
import sys

import unreal

# Set from the command line when invoked as `py script.py -- path name folder`, but the editor
# console form cannot pass arguments, so the defaults are what actually runs.
SOURCE = "C:/Users/tk/Desktop/lingxujie/Assets/Moxiang/ue_import/char_bobu.gltf"
FOLDER = "/Game/Moxiang/Skeletal/Characters"
NAME = "SK_Bobu"


def log(text):
    unreal.log("[LingXuJie] IMPORTA: %s" % text)


def main():
    if not os.path.exists(SOURCE):
        log("source missing: %s" % SOURCE)
        return
    log("source %s (%d bytes)" % (os.path.basename(SOURCE), os.path.getsize(SOURCE)))

    existing = "%s/%s" % (FOLDER, NAME)
    if unreal.EditorAssetLibrary.does_asset_exist(existing):
        unreal.EditorAssetLibrary.delete_asset(existing)
        log("removed the earlier attempt")

    task = unreal.AssetImportTask()
    task.filename = SOURCE
    task.destination_path = FOLDER
    task.destination_name = NAME
    task.automated = True
    task.save = True
    task.replace_existing = True

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

    paths = list(task.imported_object_paths or [])
    log("import produced %d assets" % len(paths))
    for path in paths:
        asset = unreal.EditorAssetLibrary.load_asset(path)
        if asset is None:
            log("  (unloadable) %s" % path)
            continue
        kind = asset.get_class().get_name()
        log("  %-16s %s" % (kind, path.rsplit("/", 1)[-1]))
        if kind == "AnimSequence":
            try:
                length = unreal.AnimationBlueprintLibrary.get_sequence_length(asset)
                frames = unreal.AnimationBlueprintLibrary.get_num_frames(asset)
                log("      length=%.4f s  frames=%d  implied fps=%.2f"
                    % (length, frames, frames / length if length else 0.0))
            except Exception as error:  # noqa: BLE001
                log("      (length unreadable: %s)" % error)

    if not paths:
        log("nothing imported - check the log for an Interchange error")

    level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    level.save_current_level()
    log("done")


main()
