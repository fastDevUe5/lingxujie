"""Rewrite the physics audit so components without the property are skipped rather than fatal.

ArrowComponent and similar helper components derive from PrimitiveComponent but carry none of the
simulation settings, so reading them blindly throws. A safe getter that returns a default is the
fix, and it is worth noting because the same mistake will recur on any component-class query.

    python Tools/fix_physics_audit.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Tools/audit_level_physics.py"

OLD = '''    for actor in actors:
        components = actor.get_components_by_class(unreal.PrimitiveComponent)
        for component in components:
            mobility = component.get_editor_property("mobility")
            key = str(mobility)
            by_mobility[key] = by_mobility.get(key, 0) + 1

            if component.get_editor_property("simulate_physics"):
                simulating += 1
                try:
                    mass_total += component.get_editor_property("mass")
                except Exception:  # noqa: BLE001
                    pass
            if component.get_editor_property("enable_gravity"):
                gravity_on += 1
            try:
                if component.get_editor_property("phys_material_override") is not None:
                    with_physics_material += 1
            except Exception:  # noqa: BLE001
                pass'''

NEW = '''    def safe(component, name, default=None):
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
                with_physics_material += 1'''

OLD2 = '''    ragdoll_ready = 0
    for actor in actors:
        for component in actor.get_components_by_class(unreal.SkeletalMeshComponent):
            if component.get_editor_property("physics_asset") is not None:
                ragdoll_ready += 1'''

NEW2 = '''    ragdoll_ready = 0
    for actor in actors:
        for component in actor.get_components_by_class(unreal.SkeletalMeshComponent):
            try:
                if component.get_editor_property("physics_asset") is not None:
                    ragdoll_ready += 1
            except Exception:  # noqa: BLE001
                pass'''


def main():
    text = open(PATH, encoding="utf-8").read()
    changed = 0
    for old, new in ((OLD, NEW), (OLD2, NEW2)):
        if old in text:
            text = text.replace(old, new)
            changed += 1
    if changed == 0:
        print("nothing to replace; already patched")
        return
    open(PATH, "w", encoding="utf-8").write(text)
    print("patched %d block(s) with guarded property reads" % changed)


if __name__ == "__main__":
    main()
