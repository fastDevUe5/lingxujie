import unreal
ls = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
if w is not None:
    unreal.SystemLibrary.execute_console_command(w, "r.Nanite 1")
    unreal.SystemLibrary.execute_console_command(w, "r.VolumetricCloud 1")
    unreal.SystemLibrary.execute_console_command(w, "r.Nanite")
    unreal.SystemLibrary.execute_console_command(w, "r.VolumetricCloud")
    unreal.log("[LingXuJie] RES: nanite and clouds restored")
ls.load_level("/Game/Maps/LingXuJie")
unreal.log("[LingXuJie] RES: main actors=%d" % len(unreal.EditorLevelLibrary.get_all_level_actors()))
unreal.log("[LingXuJie] RES: done")
