"""Load and register the project's editor toolsets without restarting the editor.

init_unreal.py normally does this at startup, but the editor only reads it when it launches. This
does the same work on demand, through the console path that is already known to run scripts
reliably.

    py "C:/Users/tk/Desktop/lingxujie/Tools/load_toolsets.py"
"""

import os
import sys

import unreal

PYTHON_DIR = os.path.join(unreal.Paths.project_dir(), "Content", "Python")


def main():
    if PYTHON_DIR not in sys.path:
        sys.path.insert(0, PYTHON_DIR)

    try:
        import lingxujie_tools  # noqa: PLC0415

        registered = lingxujie_tools._registration.register()
        unreal.log("[LingXuJie] TOOLS: registration returned %s" % registered)
        # The classes are Python types, so __name__ is the right way to name them; calling the
        # reflected get_name() needs an instance.
        unreal.log("[LingXuJie] TOOLS: classes -> %s"
                   % [c.__name__ for c in lingxujie_tools._registration._toolset_classes])
    except Exception as error:  # noqa: BLE001
        unreal.log_error("[LingXuJie] TOOLS: failed: %s" % error)


main()
