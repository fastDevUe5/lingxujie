"""Case 003: let the skeleton settle which axis is up.

Bounding-box extents cannot distinguish a wide creature from one lying down. A humanoid skeleton can:
the head bone sits far from the root along the up axis, and the feet sit the other way. Measuring head
and root positions on each axis says which axis the figure stands along, without guessing.

    py "Tools/diag_scatter_step4.py"
"""

import unreal


def log(text):
    unreal.log("[LingXuJie] S4: %s" % text)


def main():
    targets = ["MX_BOSS001", "MX_BOSSCOWF"]
    for label in targets:
        actor = None
        for candidate in unreal.EditorLevelLibrary.get_all_level_actors():
            if candidate.get_actor_label() == label:
                actor = candidate
                break
        if actor is None:
            log("%s not found" % label)
            continue

        component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
        if component is None:
            log("%s has no skeletal component" % label)
            continue

        num = component.get_num_bones()
        log("=== %s: %d bones ===" % (label, num))

        # Report the root and a few interesting bones by name and position.
        interesting = []
        for index in range(num):
            name = str(component.get_bone_name(index))
            lowered = name.lower()
            if any(k in lowered for k in ("bip01", "head", "tail", "foot", "hand", "pelvis", "root")):
                interesting.append((index, name))

        log("  bones of interest: %d" % len(interesting))
        for index, name in interesting[:14]:
            transform = component.get_bone_transform(name)
            t = transform.translation
            log("    %-24s idx=%-3d world=(%.1f, %.1f, %.1f)" % (name, index, t.x, t.y, t.z))

        # Compute the extent the skeleton actually spans on each axis.
        positions = []
        for index in range(num):
            name = str(component.get_bone_name(index))
            try:
                positions.append(component.get_bone_transform(name).translation)
            except Exception:  # noqa: BLE001
                continue
        if positions:
            for axis, getter in (("X", lambda v: v.x), ("Y", lambda v: v.y), ("Z", lambda v: v.z)):
                values = [getter(p) for p in positions]
                log("    bone span %s: %.1f cm" % (axis, max(values) - min(values)))
            tallest = max(
                (("X", max(getter(p) for p in positions) - min(getter(p) for p in positions))
                 for axis, getter in (("X", lambda v: v.x), ("Y", lambda v: v.y), ("Z", lambda v: v.z))),
                key=lambda kv: kv[1])
            log("    -> skeleton is longest along %s" % tallest[0])

    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
