"""Map the physics side, which is the half of the physics curriculum not yet covered.

Collision was studied as a query system - channels, responses, trace flags. That answers "can this
be hit". It does not answer "does this fall", which is simulation, and simulation has its own set of
switches on the primitive component plus two asset types that carry the material and the body
shape.

The header sizes say where the substance is: PrimitiveComponent is a hundred and ninety kilobytes
because it carries both the query and the simulation settings, and BodyInstance is eighty-one
because it holds the actual solver binding.

    python Tools/map_physics.py
"""

import os
import re

ENGINE = r"C:\Program Files\Epic Games\UE_5.8\Engine\Source"

TARGETS = [
    ("UPrimitiveComponent", "PrimitiveComponent.h"),
    ("FBodyInstance", "BodyInstance.h"),
    ("UPhysicalMaterial", "PhysicalMaterial.h"),
    ("UPhysicsConstraintComponent", "PhysicsConstraintComponent.h"),
    ("UPhysicsAsset", "PhysicsAsset.h"),
    ("UPhysicsSettings", "PhysicsSettings.h"),
]

# The switches that decide whether a body simulates at all.
SIMULATION_SWITCHES = [
    "SetSimulatePhysics", "SetEnableGravity", "SetMassOverrideInKg",
    "SetPhysicsLinearVelocity", "SetPhysicsAngularVelocityInDegrees",
    "AddForce", "AddImpulse", "AddTorqueInDegrees",
    "SetLinearDamping", "SetAngularDamping", "SetCollisionEnabled",
    "SetNotifyRigidBodyCollision", "SetConstraintMode",
]

# Physical material fields, which decide how it feels when it lands.
MATERIAL_FIELDS = [
    "Friction", "StaticFriction", "Restitution", "Density",
    "RaiseMassToPower", "SleepThresholdMultiplier", "LinearDamping",
    "AngularDamping", "FrictionCombineMode", "RestitutionCombineMode",
]


def find(filename):
    for root, dirs, files in os.walk(ENGINE):
        if filename in files:
            return os.path.join(root, filename)
    return None


def main():
    print("%-30s %-46s %s" % ("class", "header", "size"))
    print("-" * 88)
    loaded = {}
    for class_name, filename in TARGETS:
        path = find(filename)
        if path is None:
            print("%-30s %-46s missing" % (class_name, filename))
            continue
        text = open(path, encoding="utf-8", errors="replace").read()
        loaded[class_name] = text
        print("%-30s %-46s %7d B"
              % (class_name, os.path.relpath(path, ENGINE)[:46], len(text)))
    print("")

    primitive = loaded.get("UPrimitiveComponent", "")
    if primitive:
        present = [name for name in SIMULATION_SWITCHES if name in primitive]
        print("UPrimitiveComponent simulation switches present: %d of %d"
              % (len(present), len(SIMULATION_SWITCHES)))
        for name in present:
            print("   %s" % name)
        missing = [name for name in SIMULATION_SWITCHES if name not in primitive]
        if missing:
            print("   absent: %s" % ", ".join(missing))
        print("")

    material = loaded.get("UPhysicalMaterial", "")
    if material:
        present = [name for name in MATERIAL_FIELDS if name in material]
        print("UPhysicalMaterial fields present: %d of %d"
              % (len(present), len(MATERIAL_FIELDS)))
        for name in present:
            print("   %s" % name)
        print("")

    body = loaded.get("FBodyInstance", "")
    if body:
        print("FBodyInstance notable members:")
        for name in ("bSimulatePhysics", "bEnableGravity", "MassInKgOverride",
                     "LinearDamping", "AngularDamping", "PhysMaterialOverride",
                     "SleepFamily", "CollisionProfileName"):
            if name in body:
                print("   %s" % name)
        print("")


if __name__ == "__main__":
    main()
