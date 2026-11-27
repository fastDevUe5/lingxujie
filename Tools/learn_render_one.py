"""Apply one rendering variant, then let the frame finish so a capture can be taken.

Why this is one variant per run: Python in the editor executes on the game thread, so time.sleep
blocks the very thread that has to render and save a screenshot. Nine screenshots requested inside one
script produced exactly one file - the last one. One variant per run, with the capture taken after the
script returns, is the version that works.

    {"camera": [x, y, z, yaw, pitch],
     "reset": ["r.X 1"],
     "commands": ["r.DynamicGlobalIlluminationMethod 0"]}

    py "Tools/learn_render_one.py"
"""

import json
import os

import unreal


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(ROOT, "Saved", "learn_one.json")


def log(text):
    unreal.log("[LingXuJie] LEARN: %s" % text)


def set_camera(camera):
    x, y, z, yaw, pitch = camera
    rotation = unreal.Rotator(pitch=0.0, yaw=0.0, roll=0.0)
    rotation.pitch = pitch
    rotation.yaw = yaw
    subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    subsystem.set_level_viewport_camera_info(unreal.Vector(x, y, z), rotation)


def main():
    with open(CONFIG, "r", encoding="utf-8-sig") as handle:
        config = json.load(handle)

    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    if config.get("camera"):
        set_camera(config["camera"])

    for command in config.get("reset", []) + config.get("commands", []):
        try:
            unreal.SystemLibrary.execute_console_command(world, command)
            log("ran: %s" % command)
        except Exception as error:  # noqa: BLE001
            log("command error %r: %s" % (command, error))

    log("variant %s applied" % config.get("name", "?"))
    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
