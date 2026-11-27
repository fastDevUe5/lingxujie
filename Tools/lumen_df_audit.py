"""Lumen round 1: does this project have the documented distance field problem.

The official Lumen page and RendererSettings.h both say distance field resolution comes from a mesh's
import scale, so a mesh authored small and scaled up in the level gets a distance field that is coarse
relative to how big it looks. This measures the ratio between each actor's scale and its mesh's own
bounds, which is exactly the condition the documentation warns about.

    py "Tools/lumen_df_audit.py"
"""

import unreal


def log(text):
    unreal.log("[LingXuJie] DF: %s" % text)


def main():
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    log("actors: %d" % len(actors))

    checked = 0
    scaled = []
    largest_ratio = 0.0
    largest_name = None

    for actor in actors:
        component = actor.get_component_by_class(unreal.StaticMeshComponent)
        if component is None:
            continue
        mesh = component.get_editor_property("static_mesh")
        if mesh is None:
            continue

        scale = actor.get_actor_scale3d()
        try:
            extent = mesh.get_bounds().box_extent
        except Exception:  # noqa: BLE001
            continue

        # The mesh's own size, from its own bounds.
        native = max(extent.x, extent.y, extent.z) * 2.0
        if native <= 0.0:
            continue

        uniform = (scale.x + scale.y + scale.z) / 3.0
        displayed = native * uniform
        checked += 1

        if abs(uniform - 1.0) > 0.01:
            scaled.append((actor.get_actor_label(), native, uniform, displayed))

        if uniform > largest_ratio:
            largest_ratio = uniform
            largest_name = actor.get_actor_label()

    log("static mesh components checked: %d" % checked)
    log("actors with scale != 1: %d" % len(scaled))
    log("largest uniform scale: %.2f on %r" % (largest_ratio, largest_name))

    # The documentation's concern is a mesh that is SMALL natively and LARGE on screen.
    log("--- meshes under 100 cm natively that are enlarged on screen ---")
    flagged = 0
    for label, native, uniform, displayed in sorted(scaled, key=lambda row: -row[3]):
        if native < 100.0 and displayed > 200.0:
            flagged += 1
            if flagged <= 12:
                log("  %-30s native %.0f cm x %.2f -> %.0f cm" % (label, native, uniform, displayed))
    log("flagged: %d" % flagged)

    # The project-wide voxel density that scales every distance field.
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    log("--- the two knobs ---")
    for cvar in ("r.DistanceFields.DefaultVoxelDensity", "r.GenerateMeshDistanceFields",
                 "r.DistanceFields.MaxPerMeshResolution"):
        unreal.SystemLibrary.execute_console_command(world, cvar)

    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
