import unreal
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
unreal.SystemLibrary.execute_console_command(w, "listtextures boss_mob01")
unreal.SystemLibrary.execute_console_command(w, "listtextures tile_108_road01")
unreal.log("[LingXuJie] M3: done")
