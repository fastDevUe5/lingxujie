"""Physics round 1, step B: read where the sphere ended up, then clean the level.

Runs after step A with real time in between, so the simulation has actually advanced. No sleep here
either, for the same reason: blocking the game thread freezes what is being measured.

    py "Tools/phys_b_read.py"
"""

import unreal

LABEL = "LXJ_PHYS_SPHERE"
START_Z = 300.0


def log(text):
    unreal.log("[LingXuJie] PB: %s" % text)


def main():
    level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)

    log("in play: %s" % level_subsystem.is_in_play_in_editor())

    game_world = subsystem.get_game_world()
    log("game world: %r" % (game_world.get_name() if game_world else None))

    if game_world is not None:
        sphere = None
        for candidate in unreal.GameplayStatics.get_all_actors_of_class(
                game_world, unreal.StaticMeshActor):
            if candidate.get_actor_label() == LABEL:
                sphere = candidate
                break

        if sphere is not None:
            loc = sphere.get_actor_location()
            log("sphere now at (%.1f, %.1f, %.1f)" % (loc.x, loc.y, loc.z))
            log("fell %.1f cm from the start height" % (START_Z - loc.z))

            component = sphere.get_component_by_class(unreal.StaticMeshComponent)
            try:
                velocity = component.get_physics_linear_velocity()
                log("velocity (%.1f, %.1f, %.1f)" % (velocity.x, velocity.y, velocity.z))
            except Exception as error:  # noqa: BLE001
                log("velocity unreadable: %r" % str(error)[:50])

            try:
                log("mass %.2f kg" % component.get_mass())
            except Exception as error:  # noqa: BLE001
                log("mass unreadable: %r" % str(error)[:50])
        else:
            log("sphere not found in the game world")

    # Ending play reloads the level from disk, which is exactly what should happen: the saved copy still
    # contains the sphere, so it is removed and saved afterwards.
    level_subsystem.editor_request_end_play()
    log("end play requested")
    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
