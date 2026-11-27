"""Lumen round 3: measure the thinnest dimension of every placed mesh.

The technical page states that walls should be no thinner than ten centimetres to avoid light leaking
through the distance field. Distance fields are built from a mesh's bounds, so a surface thinner than a
voxel cannot be represented as solid and light passes through it.

This reports each static mesh's smallest dimension, sorted, so anything under the threshold is visible
without judgement calls about which actor counts as a wall.

    py "Tools/lumen_wall_thickness.py"
"""

import unreal

THIN_CM = 10.0


def log(text):
    unreal.log("[LingXuJie] WT: %s" % text)


def main():
    rows = []
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        component = actor.get_component_by_class(unreal.StaticMeshComponent)
        if component is None:
            continue
        mesh = component.get_editor_property("static_mesh")
        if mesh is None:
            continue
        origin, extent = actor.get_actor_bounds(False)
        # Bounds are half-extents in cm.
        dims = sorted([extent.x * 2.0, extent.y * 2.0, extent.z * 2.0])
        rows.append((actor.get_actor_label(), mesh.get_name(), dims))

    log("static meshes: %d" % len(rows))

    thin = [r for r in rows if r[2][0] < THIN_CM]
    log("thinnest dimension under %.0f cm: %d actor(s)" % (THIN_CM, len(thin)))
    for label, mesh, dims in sorted(thin, key=lambda r: r[2][0])[:15]:
        log("  %-28s %-26s %.1f x %.1f x %.1f cm" % (label, mesh, dims[0], dims[1], dims[2]))

    # Also worth reporting: anything extremely flat, whether or not it is under the threshold.
    flat = [r for r in rows if r[2][0] < 30.0]
    log("thinnest dimension under 30 cm: %d actor(s)" % len(flat))

    log("--- the 12 thinnest overall ---")
    for label, mesh, dims in sorted(rows, key=lambda r: r[2][0])[:12]:
        log("  %-28s %-26s %.1f / %.1f / %.1f cm" % (label, mesh, dims[0], dims[1], dims[2]))

    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
