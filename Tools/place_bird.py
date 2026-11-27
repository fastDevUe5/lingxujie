"""Place the imported bird in the plaza so the geometry can be seen.

Numbers saying nine bones and a hundred forty-six vertices are not the same as a bird standing in
the city. This puts a skeletal mesh actor in front of the camera and frames it.

    py "Tools/place_bird.py"
"""

import unreal

MESH = "/Game/Moxiang/Skeletal/bird/SkeletalMeshes/SK_Bird.SK_Bird"
LABEL = "MX_BIRD_TEST"
# Ten metres in front of the default camera position, at eye height.
LOCATION = unreal.Vector(9200.0, -6200.0, 3820.0)


def log(text):
    unreal.log("[LingXuJie] PLACE: %s" % text)


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
    # Scale up: the bird is about a metre and a half across, small from ten metres away.
    actor.set_actor_scale3d(unreal.Vector(4.0, 4.0, 4.0))
    log("placed %s at %.0f, %.0f, %.0f" % (LABEL, LOCATION.x, LOCATION.y, LOCATION.z))

    level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    level.save_current_level()
    log("level saved")


main()
