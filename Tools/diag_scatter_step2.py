"""Case 003: measure which axis the boss mesh is long along.

The viewport shows a creature lying on the ground rather than standing, and the actor bounds have Y as
the largest extent. If the mesh's own bounding box is long along Y while the actor has no rotation,
the model is authored Z-up but exported Y-up, or the source is genuinely Y-long.

    py "Tools/diag_scatter_step2.py"
"""

import unreal


def log(text):
    unreal.log("[LingXuJie] S2: %s" % text)


def main():
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        label = actor.get_actor_label()
        if "BOSS" not in label.upper():
            continue

        rotation = actor.get_actor_rotation()
        scale = actor.get_actor_scale3d()
        log("%-22s rot=(%.1f, %.1f, %.1f) scale=(%.2f, %.2f, %.2f)"
            % (label, rotation.roll, rotation.pitch, rotation.yaw,
               scale.x, scale.y, scale.z))

        # Static mesh path
        component = actor.get_component_by_class(unreal.StaticMeshComponent)
        if component is not None:
            mesh = component.get_editor_property("static_mesh")
            if mesh is not None:
                bounds = mesh.get_bounds()
                e = bounds.box_extent
                log("    StaticMesh local extent: (%.1f, %.1f, %.1f) cm" % (e.x, e.y, e.z))
                log("    StaticMesh long axis: %s"
                    % ("X" if e.x >= e.y and e.x >= e.z else ("Y" if e.y >= e.z else "Z")))
                log("    StaticMesh: %s" % mesh.get_path_name())
            continue

        # Skeletal mesh path
        component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
        if component is not None:
            mesh = component.get_editor_property("skeletal_mesh_asset")
            if mesh is not None:
                bounds = mesh.get_bounds()
                e = bounds.box_extent
                log("    SkeletalMesh local extent: (%.1f, %.1f, %.1f) cm" % (e.x, e.y, e.z))
                log("    SkeletalMesh long axis: %s"
                    % ("X" if e.x >= e.y and e.x >= e.z else ("Y" if e.y >= e.z else "Z")))
                log("    SkeletalMesh: %s" % mesh.get_path_name())

    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
