import unreal
def log(t): unreal.log("[LingXuJie] SLOTS: %s" % t)
mesh = unreal.EditorAssetLibrary.load_asset("/Game/Moxiang/Skeletal/Characters/boss001/SkeletalMeshes/SK_Boss001.SK_Boss001")
if mesh:
    mats = mesh.get_editor_property("materials")
    log("mesh material slots: %d" % len(mats))
    for i, m in enumerate(mats[:6]):
        log("  slot %d: %s" % (i, m.material_interface.get_name() if m.material_interface else "none"))
else:
    log("mesh missing")
log("done")
