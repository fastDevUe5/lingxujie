"""Ask the engine what networking diagnostics it offers here, and what net mode we are in.

This project is single player, so real replication cannot be exercised. What can be established is
which diagnostics exist in this build, what the editor world's net mode actually is, and whether the
emulation entry points respond - all of which is needed before any future networking work.

    py "Tools/practice_net_commands.py"
"""

import unreal


def log(text):
    unreal.log("[LingXuJie] NET: %s" % text)


def world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()


def run(command):
    unreal.SystemLibrary.execute_console_command(world(), command)


def main():
    # No arguments prints the engine's own usage text, which is the authoritative syntax.
    log("--- net, with no arguments ---")
    run("net")

    # Where does this world sit in the network model?
    log("--- net mode of the editor world ---")
    w = world()
    for attribute in ("get_net_mode", "net_mode", "get_net_driver"):
        try:
            value = getattr(w, attribute)
            if callable(value):
                log("%s -> %r" % (attribute, value()))
            else:
                log("%s -> %r" % (attribute, value))
        except Exception as error:  # noqa: BLE001
            log("%s unavailable: %r" % (attribute, error))

    # Which net driver, if any, is active.
    log("--- what the world knows about net drivers ---")
    for name in dir(w):
        lowered = name.lower()
        if "net" in lowered and not lowered.startswith("_"):
            log("    %s" % name)

    # The CVars that matter for diagnosing replication, printed for the record.
    log("--- replication diagnostics CVars ---")
    for cvar in ("net.AllowPIESeamlessTravel", "net.PackageMap.LocateNetDriver",
                 "net.RepDriver", "net.UseAdaptiveNetUpdateFrequency",
                 "net.Iris.UseIrisReplication", "net.MaxRepArraySize",
                 "net.DebugDrawRelevant", "net.DebugDrawCullDistance"):
        run(cvar)

    # Emulation: does the entry point exist in this build?
    log("--- emulation entry point ---")
    run("NetEmulation.PktEmulationProfile")

    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
