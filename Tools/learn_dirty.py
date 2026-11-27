"""Report what the editor considers dirty, before any practice scene touches the world.

Creating or switching a level can discard unsaved packages. This prints them first so the decision
to save, keep or rebuild is made on evidence instead of on a guess.

    py "Tools/learn_dirty.py"
"""

import unreal


def log(text):
    unreal.log("[LingXuJie] LEARN: %s" % text)


def names(packages):
    out = []
    for package in packages or []:
        try:
            out.append(str(package.get_name()))
        except Exception:  # noqa: BLE001
            out.append(repr(package))
    return out


def main():
    utils = unreal.EditorLoadingAndSavingUtils

    for label, getter in (
        ("dirty maps", "get_dirty_map_packages"),
        ("dirty content", "get_dirty_content_packages"),
    ):
        try:
            packages = getattr(utils, getter)()
            listed = names(packages)
            log("%s: %d %s" % (label, len(listed), listed[:12]))
        except Exception as error:  # noqa: BLE001
            log("%s: error %r" % (label, error))

    try:
        pie = unreal.get_editor_subsystem(unreal.EditorAppSubsystem) if hasattr(
            unreal, "EditorAppSubsystem") else None
    except Exception:  # noqa: BLE001
        pie = None

    try:
        world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
        log("current level: %s" % world.get_name())
    except Exception as error:  # noqa: BLE001
        log("current level: error %r" % error)

    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
