import unreal
def log(t): unreal.log("[LingXuJie] SM: %s" % t)
MAT = "/Game/Moxiang/Materials/M_Boss_Mob01.M_Boss_Mob01"
sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in sub.get_all_level_actors():
    if a.get_actor_label() == "MX_BOSS001_STATIC":
        sub.destroy_actor(a)
mesh = unreal.EditorAssetLibrary.load_asset("/Game/Moxiang/Static/boss001_static/StaticMeshes/SM_Boss001.SM_Boss001")
log("mesh loaded: %s" % (mesh is not None))
if mesh:
    b = mesh.get_bounds()
    log("bounds extent: (%.1f, %.1f, %.1f) cm" % (b.box_extent.x, b.box_extent.y, b.box_extent.z))
    actor = sub.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(9550.0, -6200.0, 3740.0), unreal.Rotator(0,0,0))
    actor.set_actor_label("MX_BOSS001_STATIC")
    comp = actor.get_component_by_class(unreal.StaticMeshComponent)
    if comp:
        comp.set_static_mesh(mesh)
        log("component mesh set")
        # The mesh asset's own slot is WorldGridMaterial and the component carries an explicit
        # WorldGrid override, so the override is the one the renderer uses. Set every slot.
        material = unreal.EditorAssetLibrary.load_asset(MAT)
        if material:
            for slot in range(comp.get_num_materials()):
                comp.set_material(slot, material)
            log("materials set: %d slot(s) -> %s" % (comp.get_num_materials(), MAT))
        else:
            log("ERROR: could not load %s" % MAT)
    log("placed at (9550, -6200, 3740)")
lvl = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
lvl.save_current_level()
log("saved")

