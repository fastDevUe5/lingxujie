"""Measure the skeleton of an already-imported test asset, with no import step at all.

The previous attempt waited on an import that never started. The first test import did succeed and its
assets are on disk, so the measurement can be taken straight from them - which avoids the import path
entirely and is a smaller thing to go wrong.

    py "Tools/measure_imported_skeleton.py"
"""

import unreal

# The asset imported earlier from the slot-fixed (but unscaled) glTF.
TEST_MESH = ("/Game/Moxiang/Test/IBMFix/boss001_ibmfix/SkeletalMeshes/SK_Boss001_IBMFix."
             "SK_Boss001_IBMFix")
REFERENCE = ("/Game/Moxiang/Skeletal/Characters/boss001/SkeletalMeshes/SK_Boss001."
             "SK_Boss001")


def log(text):
    unreal.log("[LingXuJie] MEAS: %s" % text)


def bone_span(component, label):
    positions = []
    for index in range(component.get_num_bones()):
        name = str(component.get_bone_name(index))
        try:
            positions.append(component.get_bone_transform(name).translation)
        except Exception:  # noqa: BLE001
            continue
    if not positions:
        log("%s: no bones readable" % label)
        return None
    spans = (
        max(p.x for p in positions) - min(p.x for p in positions),
        max(p.y for p in positions) - min(p.y for p in positions),
        max(p.z for p in positions) - min(p.z for p in positions),
    )
    log("%s: %d bones, span X=%.1f Y=%.1f Z=%.1f cm"
        % (label, len(positions), spans[0], spans[1], spans[2]))
    return spans


def spawn_and_measure(mesh_path, label, location):
    mesh = unreal.load_asset(mesh_path)
    if mesh is None:
        log("%s: could not load %s" % (label, mesh_path))
        return None

    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    tag = "MEAS_%s" % label.replace(" ", "_")
    for actor in subsystem.get_all_level_actors():
        if actor.get_actor_label() == tag:
            subsystem.destroy_actor(actor)

    actor = subsystem.spawn_actor_from_class(
        unreal.SkeletalMeshActor, location, unreal.Rotator(0.0, 0.0, 0.0))
    if actor is None:
        log("%s: spawn failed" % label)
        return None
    actor.set_actor_label(tag)

    component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
    if component is None:
        log("%s: no component" % label)
        return None
    component.set_skeletal_mesh_asset(mesh)

    result = bone_span(component, label)
    subsystem.destroy_actor(actor)
    return result


def main():
    log("comparing two imports of the same model")
    broken = spawn_and_measure(REFERENCE, "BROKEN (original)", unreal.Vector(9350, -5200, 3740))
    fixed = spawn_and_measure(TEST_MESH, "SLOTS FIXED", unreal.Vector(9550, -5200, 3740))

    if broken and fixed:
        log("")
        log("broken max span: %.1f cm" % max(broken))
        log("fixed  max span: %.1f cm" % max(fixed))
        if max(broken) < 1.0 and max(fixed) > 1.0:
            ratio = max(fixed) / max(broken) if max(broken) else float("inf")
            log("the slot fix restores bone offsets")
            log("fixed span in metres: %.1f" % (max(fixed) / 100.0))
            if max(fixed) / 100.0 > 20.0:
                log("and it is far too large, consistent with centimetres not being scaled to metres")
    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
