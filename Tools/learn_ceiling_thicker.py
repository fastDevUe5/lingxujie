"""Lumen round 4, experiment: thicken the ceiling and see whether the leak reduces.

The previous attempt passed the thickness as a command line argument, but RebuildInEditor.ps1 treats the
whole -Script value as a path, so "path 40" was not a file and nothing ran. The thickness is hardcoded
here instead and changed by editing this line.

The sealed room has one light inside and no light outside, yet the ceiling's outer face glows. A distance
field is built from a mesh's bounds, so a thin slab gets few voxels and light passes through it. If that
is the mechanism, a much thicker ceiling should stop glowing.

    py "Tools/learn_ceiling_thicker.py"
"""

import unreal

CEILING = "LXJ_LAB_Ceiling"
UNIT = 100.0          # the engine cube is 100 cm on a side
THICKNESS_CM = 60.0   # was 10.0


def log(text):
    unreal.log("[LingXuJie] THICK: %s" % text)


def main():
    target = None
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if actor.get_actor_label() == CEILING:
            target = actor
            break
    if target is None:
        log("%s not found" % CEILING)
        return

    scale = target.get_actor_scale3d()
    log("before: Z scale %.3f = %.1f cm" % (scale.z, scale.z * UNIT))

    target.set_actor_scale3d(unreal.Vector(scale.x, scale.y, THICKNESS_CM / UNIT))

    after = target.get_actor_scale3d()
    log("after:  Z scale %.3f = %.1f cm" % (after.z, after.z * UNIT))
    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
