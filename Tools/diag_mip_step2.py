import unreal
def log(t): unreal.log("[LingXuJie] M2: %s" % t)
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
log("--- listtextures with a name filter ---")
unreal.SystemLibrary.execute_console_command(w, "listtextures boss_mob01")
log("--- listtextures short form ---")
unreal.SystemLibrary.execute_console_command(w, "listtextures")
log("done")
