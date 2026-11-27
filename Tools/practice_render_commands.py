"""Ask the renderer to describe its own visualisation commands.

The parser handles help and pool as first-class commands, so the authoritative syntax comes from
running vis help rather than from reading the token loop. This also checks whether the visualisation
state survives into a viewport capture, which decides whether render debugging can be automated.

    py "Tools/practice_render_commands.py"
"""

import unreal


def log(text):
    unreal.log("[LingXuJie] REN: %s" % text)


def world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()


def run(command):
    unreal.SystemLibrary.execute_console_command(world(), command)


def main():
    log("--- the renderer's own help for vis ---")
    run("vis help")

    log("--- what pooled render targets exist right now ---")
    run("vis pool")

    log("--- which views exist ---")
    run("vis view=?")

    log("--- a few r.* switches worth knowing ---")
    for cvar in ("r.ShaderPrint", "r.RDG.ImmediateMode", "r.RDG.Debug",
                 "r.Freeze", "r.RenderTargetPoolMin", "r.VisualizeBuffer"):
        run(cvar)

    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
