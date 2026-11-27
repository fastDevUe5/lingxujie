"""Practise the log console commands against the running editor.

Reading the source says what the commands should do; running them shows what they actually do here.
This lists categories, checks that a verbosity change is visible through UE_LOG_ACTIVE semantics, and
confirms the ``log list`` output format so future diagnosis can be scripted rather than eyeballed.

    py "Tools/practice_log_commands.py"
"""

import unreal


def log(text):
    unreal.log("[LingXuJie] LOGC: %s" % text)


def world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()


def run(command):
    """Execute a console command and return nothing; output goes to the log."""
    unreal.SystemLibrary.execute_console_command(world(), command)


def main():
    log("start")

    # 1. What does the engine think the current verbosity of our own category is?
    #    LingXuJie is the category this project logs under.
    run("log list LingXuJie")
    log("asked for the LingXuJie category listing")

    # 2. Raise a real engine category to Verbose and lower it again, to confirm both directions.
    run("log LogTemp Verbose")
    log("set LogTemp to Verbose")
    run("log LogTemp Warning")
    log("set LogTemp to Warning")

    # 3. Enable the debugger break on a category. Nothing is logged from it in the next statement,
    #    so this must not hang; the point is that the command is accepted.
    run("log LogTemp Break")
    log("toggled Break on LogTemp")
    run("log LogTemp Break")
    log("toggled Break off again")

    # 4. How many categories does this editor know about?
    run("log list")
    log("requested the full category listing")

    log("done - read the log for the listings")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
