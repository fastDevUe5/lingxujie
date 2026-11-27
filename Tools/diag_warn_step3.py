"""Case 004: before calling an empty slot a defect, check whether the placed actors override it.

All 101 Nanite meshes report WorldGridMaterial in their own material slots, while the viewport clearly
shows textured buildings. Per-component material overrides would explain that, and if they are present
the empty slot is a workflow choice rather than a fault. Reporting it as a defect without checking
would be exactly the mistake this series keeps warning about.

    py "Tools/diag_warn_step3.py"
"""

import unreal


def log(text):
    unreal.log("[LingXuJie] W3: %s" % text)


def main():
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    log("actors: %d" % len(actors))

    with_override = 0
    without_override = 0
    examples = []
    for actor in actors:
        component = actor.get_component_by_class(unreal.StaticMeshComponent)
        if component is None:
            continue
        mesh = component.get_editor_property("static_mesh")
        if mesh is None:
            continue

        # get_material(0) returns the effective material, override if set, else the mesh slot.
        try:
            effective = component.get_material(0)
        except Exception as error:  # noqa: BLE001
            log("  %-30s get_material failed: %r" % (actor.get_actor_label(), error))
            continue

        if effective is None:
            log("  %-30s effective material is None" % actor.get_actor_label())
            continue

        name = effective.get_name()
        if "WorldGrid" in name:
            without_override += 1
            if len(examples) < 6:
                examples.append((actor.get_actor_label(), name))
        else:
            with_override += 1

    log("static mesh components showing a real material: %d" % with_override)
    log("static mesh components still on WorldGridMaterial: %d" % without_override)
    for label, name in examples:
        log("    grid on %-28s (%s)" % (label, name))

    # A sample of what the effective materials actually are, to show the override path works.
    log("--- sample of effective materials ---")
    shown = 0
    for actor in actors:
        component = actor.get_component_by_class(unreal.StaticMeshComponent)
        if component is None:
            continue
        try:
            effective = component.get_material(0)
        except Exception:  # noqa: BLE001
            continue
        if effective is None or "WorldGrid" in effective.get_name():
            continue
        log("  %-30s -> %s" % (actor.get_actor_label(), effective.get_name()))
        shown += 1
        if shown >= 8:
            break

    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
