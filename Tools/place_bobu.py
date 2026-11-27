"""Place the imported character in the plaza and screenshot it.

The bird proved the pipeline on a nine-bone model. This is a thirty-one bone humanoid, and seeing it
standing in the city is the end of the road that started with a heuristic scan of a binary container.

    py "Tools/place_bobu.py"
"""

import unreal

MESH = "/Game/Moxiang/Skeletal/Characters/char_bobu/SkeletalMeshes/SK_Bobu.SK_Bobu"
LABEL = "MX_BOBU_TEST"
# Directly in front of the default camera, at eye height.
LOCATION = unreal.Vector(9600.0, -6200.0, 3660.0)


def log(text):
    unreal.log("[LingXuJie] PLACEBOBU: %s" % text)


def main():
    mesh = unreal.EditorAssetLibrary.load_asset(MESH)
    if mesh is None:
        log("mesh missing")
        return

    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for actor in subsystem.get_all_level_actors():
        if actor.get_actor_label() == LABEL:
            log("removing the earlier placement")
            subsystem.destroy_actor(actor)

    actor = subsystem.spawn_actor_from_class(
        unreal.SkeletalMeshActor, LOCATION, unreal.Rotator(0.0, 0.0, 0.0))
    if actor is None:
        log("spawn returned nothing")
        return
    actor.set_actor_label(LABEL)

    component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
    if component is None:
        log("no skeletal mesh component")
        return
    component.set_skeletal_mesh_asset(mesh)
    actor.set_actor_scale3d(unreal.Vector(1.5, 1.5, 1.5))
    log("placed %s at %.0f, %.0f, %.0f" % (LABEL, LOCATION.x, LOCATION.y, LOCATION.z))

    try:
        bounds = mesh.get_bounds()
        log("mesh bounds extent=(%.1f, %.1f, %.1f)"
            % (bounds.box_extent.x, bounds.box_extent.y, bounds.box_extent.z))
    except Exception:  # noqa: BLE001
        pass

    level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    level.save_current_level()
    log("level saved")


main()
