"""Measure how much physics the level actually uses.

The simulation switches all exist on the primitive component, which says nothing about whether any
of them are on. A city where every mesh is static and a city where everything is a rigid body look
identical in the editor until something is hit.

    py "Tools/audit_level_physics.py"
"""

import unreal


def log(text):
    unreal.log("[LingXuJie] PHYS: %s" % text)


def main():
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = list(subsystem.get_all_level_actors())
    log("actors %d" % len(actors))

    simulating = 0
    with_physics_material = 0
    gravity_on = 0
    by_mobility = {}
    mass_total = 0.0

    def safe(component, name, default=None):
        """Helper components such as ArrowComponent have no simulation settings at all."""
        try:
            return component.get_editor_property(name)
        except Exception:  # noqa: BLE001
            return default

    for actor in actors:
        components = actor.get_components_by_class(unreal.PrimitiveComponent)
        for component in components:
            key = str(safe(component, "mobility", "unknown"))
            by_mobility[key] = by_mobility.get(key, 0) + 1

            if safe(component, "simulate_physics", False):
                simulating += 1
                mass_total += safe(component, "mass", 0.0) or 0.0
            if safe(component, "enable_gravity", False):
                gravity_on += 1
            if safe(component, "phys_material_override") is not None:
                with_physics_material += 1

    log("primitive components by mobility: %s" % by_mobility)
    log("simulating physics: %d" % simulating)
    log("gravity enabled: %d" % gravity_on)
    log("with a physical material override: %d" % with_physics_material)
    if simulating:
        log("total simulated mass: %.1f kg" % mass_total)

    # Constraints, the other half of a physics setup.
    constraints = [a for a in actors if a.get_class().get_name() == "PhysicsConstraintActor"]
    log("physics constraints: %d" % len(constraints))

    # A physics asset on any skeletal mesh is what makes a character ragdoll.
    ragdoll_ready = 0
    for actor in actors:
        for component in actor.get_components_by_class(unreal.SkeletalMeshComponent):
            try:
                if component.get_editor_property("physics_asset") is not None:
                    ragdoll_ready += 1
            except Exception:  # noqa: BLE001
                pass
    log("skeletal meshes with a physics asset: %d" % ragdoll_ready)

    log("done")


main()
