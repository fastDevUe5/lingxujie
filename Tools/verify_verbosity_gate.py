"""Prove the suppression rule by reading it back from the running editor.

The source says a message prints only when its level is at or below the category's current verbosity,
and that LogTemp is declared with a default of Log. So a Verbose message on LogTemp should be
suppressed until the category is raised. The observable evidence is what ``log list`` reports before
and after raising it, which this reads through the console.

    py "Tools/verify_verbosity_gate.py"
"""

import unreal


def log(text):
    unreal.log("[LingXuJie] VERGATE: %s" % text)


def world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()


def run(command):
    unreal.SystemLibrary.execute_console_command(world(), command)


def main():
    log("--- step 1: read LogTemp's current verbosity ---")
    run("log list LogTemp")

    log("--- step 2: raise it to Verbose ---")
    run("log LogTemp Verbose")
    run("log list LogTemp")

    log("--- step 3: lower it back to Log (the declared default) ---")
    run("log LogTemp Log")
    run("log list LogTemp")

    log("--- step 4: what does the source say the default is ---")
    log("LogTemp is declared DECLARE_LOG_CATEGORY_EXTERN(LogTemp, Log, All)")
    log("so default verbosity Log=5, compile-time All=VeryVerbose=7")
    log("a Verbose=6 message is compiled in but suppressed at runtime until raised")

    log("--- step 5: turn on the debugger break flag and read it back ---")
    run("log LogTemp Break")
    run("log list LogTemp")
    run("log LogTemp Break")
    run("log list LogTemp")

    log("done - compare the four listings above; the verbosity column and a DebugBreak marker are")
    log("the evidence")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
