"""Scene round 3: lay the composition out properly for a viewer looking along +X.

Two layouts failed for the same reason, which I only saw after looking at the pictures. A camera at
yaw zero looks along +X, so the frame's width runs along Y, not X. Both earlier layouts placed props along
X and clustered them at one side in Y, so one object filled the frame while the rest sat off screen.

The correct arrangement puts the spread on Y and uses X for depth. At a distance d with a ninety degree
field of view the visible width is about 2d, so objects spread across roughly that distance read as a
composition rather than a pile.

    py "Tools/scene_relayout2.py"
"""

import unreal

LEVEL = "/Game/Learning/L_Scene01"

# Spread on Y (the frame's width), depth on X. Scale small enough not to swallow the frame.
LAYOUT = [
    ("Prop_0_Sphere", (2600.0, -2200.0, 200.0), 3.0),
    ("Prop_1_Cylinder", (3200.0, -900.0, 300.0), 4.0),
    ("Prop_2_Cone", (3800.0, 400.0, 400.0), 5.0),
    ("Prop_3_Cube", (3200.0, 1700.0, 250.0), 4.0),
    ("Prop_4_Sphere", (2600.0, 2900.0, 200.0), 3.0),
    ("Prop_5_Cylinder", (4600.0, -1500.0, 600.0), 6.0),
]


def log(text):
    unreal.log("[LingXuJie] LAYOUT2: %s" % text)


def main():
    level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

    if level_subsystem.is_in_play_in_editor():
        level_subsystem.editor_request_end_play()
        log("end play requested -- rerun after it ends")
        return

    current = level_subsystem.get_current_level()
    if (current.get_name() if current else "") != "L_Scene01":
        if not level_subsystem.load_level(LEVEL):
            log("could not load the scene")
            return

    existing = {actor.get_actor_label(): actor
                for actor in unreal.EditorLevelLibrary.get_all_level_actors()}

    moved = 0
    for label, location, scale in LAYOUT:
        actor = existing.get(label)
        if actor is None:
            log("missing %s" % label)
            continue
        actor.set_actor_location(unreal.Vector(*location), False, False)
        actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
        after = actor.get_actor_location()
        log("  %-18s (%.0f,%.0f,%.0f) scale %.0f" % (label, after.x, after.y, after.z, scale))
        moved += 1

    log("moved %d props" % moved)
    log("saved: %r" % level_subsystem.save_current_level())
    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
