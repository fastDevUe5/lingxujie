"""Open an official demo scene as the practice ground, and restore the project level afterwards.

Practice has to happen on something the project did not generate. The free Fab packs ship their own
demo maps, so the rendering lessons are learned on assets whose textures and lighting were authored
by the pack, not on the 2003 client data.

Driven by Saved/learn_cmd.json so the editor console only has to type one fixed command:

    {"action": "open",   "map": "/Game/GeonchunmunComplex/Maps/Demo_GeonchunmunComplex"}
    {"action": "restore"}
    {"action": "survey"}

    py "Tools/learn_practice.py"
"""

import json
import os

import unreal


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(ROOT, "Saved", "learn_cmd.json")
PROJECT_MAP = "/Game/Maps/LingXuJie"
DEFAULT_VIEW = (8950.0, -6200.0, 3900.0, 0.0, -2.0)


def log(text):
    unreal.log("[LingXuJie] LEARN: %s" % text)


def load_config():
    # PowerShell 5.1 writes a BOM for -Encoding UTF8, so read tolerantly.
    with open(CONFIG, "r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def save_dirty():
    try:
        saved = unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
        log("saved dirty packages: %s" % saved)
    except Exception as error:  # noqa: BLE001
        log("save dirty failed: %r" % error)


def load_level(path):
    subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    subsystem.load_level(path)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    log("level now: %s" % world.get_name())
    log("actors: %d" % len(unreal.EditorLevelLibrary.get_all_level_actors()))


def survey():
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    log("actors: %d" % len(actors))
    counts = {}
    for actor in actors:
        try:
            kind = actor.get_class().get_name()
        except Exception:  # noqa: BLE001
            kind = "?"
        counts[kind] = counts.get(kind, 0) + 1
    for kind in sorted(counts, key=lambda k: -counts[k])[:12]:
        log("  %-28s %4d" % (kind, counts[kind]))

    lights = [a for a in actors if "Light" in a.get_class().get_name()]
    for light in lights[:8]:
        try:
            loc = light.get_actor_location()
            log("  light %-22s at %.0f, %.0f, %.0f" % (
                light.get_actor_label(), loc.x, loc.y, loc.z))
        except Exception:  # noqa: BLE001
            pass


def set_view(x, y, z, yaw, pitch):
    subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    location = unreal.Vector(x, y, z)
    rotation = unreal.Rotator(pitch=0.0, yaw=0.0, roll=0.0)
    rotation.pitch = pitch
    rotation.yaw = yaw
    subsystem.set_level_viewport_camera_info(location, rotation)
    current, current_rotation = subsystem.get_level_viewport_camera_info()
    log("camera at %.0f, %.0f, %.0f yaw %.0f pitch %.0f" % (
        current.x, current.y, current.z, current_rotation.yaw, current_rotation.pitch))


def main():
    config = load_config()
    action = config.get("action", "survey")
    log("action: %s" % action)

    if action == "open":
        save_dirty()
        load_level(config["map"])
    elif action == "restore":
        save_dirty()
        load_level(PROJECT_MAP)
        set_view(*DEFAULT_VIEW)
    elif action == "survey":
        survey()
    else:
        log("unknown action")

    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
