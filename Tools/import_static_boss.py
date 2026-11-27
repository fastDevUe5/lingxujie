import unreal, os
SRC = "C:/Users/tk/Desktop/lingxujie/Assets/Moxiang/ue_import/boss001_static.gltf"
FOLDER = "/Game/Moxiang/Static"
NAME = "SM_Boss001"
def log(t): unreal.log("[LingXuJie] STATIC: %s" % t)
existing = "%s/%s" % (FOLDER, NAME)
if unreal.EditorAssetLibrary.does_asset_exist(existing):
    unreal.EditorAssetLibrary.delete_asset(existing)
task = unreal.AssetImportTask()
task.filename = SRC
task.destination_path = FOLDER
task.destination_name = NAME
task.automated = True
task.save = True
task.replace_existing = True
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
paths = list(task.imported_object_paths or [])
log("import produced %d assets" % len(paths))
for p in paths:
    a = unreal.EditorAssetLibrary.load_asset(p)
    log("  %s %s" % (a.get_class().get_name() if a else "?", p.rsplit("/",1)[-1]))
sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for actor in sub.get_all_level_actors():
    if actor.get_actor_label() == "MX_BOSS001_STATIC":
        sub.destroy_actor(actor)
mesh = unreal.EditorAssetLibrary.load_asset(existing)
if mesh:
    actor = sub.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(9550.0, -6200.0, 3740.0), unreal.Rotator(0,0,0))
    actor.set_actor_label("MX_BOSS001_STATIC")
    comp = actor.get_component_by_class(unreal.StaticMeshComponent)
    if comp: comp.set_static_mesh(mesh)
    b = mesh.get_bounds()
    log("placed static at (9550, -6200, 3740); extent (%.1f, %.1f, %.1f) cm" % (b.box_extent.x, b.box_extent.y, b.box_extent.z))
lvl = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
lvl.save_current_level()
log("level saved")
