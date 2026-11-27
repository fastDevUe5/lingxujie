"""Practise the memory diagnostics on this project and report what they give.

Reading the source says obj cycles finds reference cycles and memreport defers to after a GC. Running
them here shows what this level actually contains, which is the only way to learn to read the output.

    py "Tools/practice_memory_commands.py"
"""

import unreal


def log(text):
    unreal.log("[LingXuJie] MEM: %s" % text)


def world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()


def run(command):
    unreal.SystemLibrary.execute_console_command(world(), command)


def main():
    # obj cycles walks the whole reference graph looking for strongly connected components - the
    # shape that keeps objects alive past a GC.
    log("--- obj cycles: reference cycles in this editor ---")
    run("obj cycles")

    # Count objects by class, which is the fastest way to spot something growing.
    log("--- obj classes ---")
    run("obj classes")

    # The two that matter for a content-heavy project.
    log("--- mesh object counts ---")
    run("obj list class=SkeletalMesh")
    run("obj list class=StaticMesh")

    # Texture memory, split by compressed and not.
    log("--- texture listings ---")
    run("listtextures nonvt")

    # Memory totals, the same command memreport starts with.
    log("--- mem from report ---")
    run("Mem FromReport")
    run("stat memory")

    log("--- asked memreport to write a full profile ---")
    run("memreport -full")

    log("done - the report lands in Saved/Profiling/MemReports")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
