"""Import an exported glTF and put it in the level, in one pass.

The earlier scripts were written for one model at a time and named after it. This takes the folder
and asset name as constants at the top so the same file serves any export, which matters now that
there are characters worth placing rather than a single bird.

    py "Tools/import_and_place.py"
"""

import os

import unreal

SOURCE = "C:/Users/tk/Desktop/lingxujie/Assets/Moxiang/ue_import/boss001.gltf"
FOLDER = "/Game/Moxiang/Skeletal/Characters"
NAME = "SK_Boss001"
LABEL = "MX_BOSS001"
# In front of the default camera, at a height that puts the feet near the ground.
LOCATION = unreal.Vector(9350.0, -6200.0, 3740.0)
SCALE = 1.0


def log(text):
    unreal.log("[LingXuJie] BOSS: %s" % text)


def main():
    if not os.path.exists(SOURCE):
        log("source missing: %s" % SOURCE)
        return
    log("source %s (%d bytes)" % (os.path.basename(SOURCE), os.path.getsize(SOURCE)))

    existing = "%s/%s" % (FOLDER, NAME)
    if unreal.EditorAssetLibrary.does_asset_exist(existing):
        unreal.EditorAssetLibrary.delete_asset(existing)
        log("removed the earlier import")

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
    mesh = None
    anim = None
    for path in paths:
        asset = unreal.EditorAssetLibrary.load_asset(path)
        if asset is None:
            log("  (unloadable) %s" % path)
            continue
        kind = asset.get_class().get_name()
        log("  %-16s %s" % (kind, path.rsplit("/", 1)[-1]))
        if kind == "SkeletalMesh":
            mesh = asset
        elif kind == "AnimSequence":
            anim = asset

    if anim is not None:
        try:
            length = anim.get_editor_property("sequence_length")
            log("  animation length %.4f s" % length)
        except Exception:  # noqa: BLE001
            pass

    if mesh is None:
        log("no skeletal mesh came out - nothing to place")
        return

    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for actor in subsystem.get_all_level_actors():
        if actor.get_actor_label() == LABEL:
            subsystem.destroy_actor(actor)

    actor = subsystem.spawn_actor_from_class(
        unreal.SkeletalMeshActor, LOCATION, unreal.Rotator(0.0, 0.0, 0.0))
    if actor is None:
        log("spawn returned nothing")
        return
    actor.set_actor_label(LABEL)

    component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
    if component is not None:
        component.set_skeletal_mesh_asset(mesh)
    actor.set_actor_scale3d(unreal.Vector(SCALE, SCALE, SCALE))

    bounds = mesh.get_bounds()
    log("placed %s at (%.0f, %.0f, %.0f) scale %.1f"
        % (LABEL, LOCATION.x, LOCATION.y, LOCATION.z, SCALE))
    log("mesh extent (%.1f, %.1f, %.1f) cm"
        % (bounds.box_extent.x, bounds.box_extent.y, bounds.box_extent.z))

    level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    level.save_current_level()
    log("level saved")


main()
