"""Scene round 2: add composition to the scene, using only official shapes.

A sunset field with a flat plane is structurally complete but tells you nothing about how objects read in
it. A small arrangement of the engine's basic shapes gives surfaces at different angles and distances,
which is what makes lighting differences visible - and it is the same set of meshes the material rounds
already proved can be given materials.

    py "Tools/scene_compose.py"
"""

import unreal

LEVEL = "/Game/Learning/L_Scene01"


def log(text):
    unreal.log("[LingXuJie] COMP: %s" % text)


def main():
    level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

    current = level_subsystem.get_current_level()
    if (current.get_name() if current else "") != "L_Scene01":
        if not level_subsystem.load_level(LEVEL):
            log("could not load the scene")
            return

    # Remove any earlier composition so this is idempotent.
    removed = 0
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if actor.get_actor_label().startswith("Prop_"):
            unreal.EditorLevelLibrary.destroy_actor(actor)
            removed += 1
    log("cleared %d earlier props" % removed)

    shapes = {
        "Sphere": "/Engine/BasicShapes/Sphere",
        "Cylinder": "/Engine/BasicShapes/Cylinder",
        "Cone": "/Engine/BasicShapes/Cone",
        "Cube": "/Engine/BasicShapes/Cube",
    }
    materials = {
        "Sphere": "/Game/Learning/M_SceneFloor",
        "Cylinder": "/Game/Learning/M_LabTex",
        "Cone": "/Game/Learning/M_LabRedOverride",
        "Cube": "/Game/Learning/M_LabDark",
    }

    # A short arc of objects at different distances and heights.
    layout = [
        ("Sphere", (-300.0, -400.0, 150.0), 3.0),
        ("Cylinder", (0.0, -200.0, 200.0), 2.0),
        ("Cone", (300.0, -400.0, 180.0), 3.5),
        ("Cube", (600.0, -100.0, 150.0), 3.0),
        ("Sphere", (-700.0, 100.0, 250.0), 5.0),
        ("Cylinder", (900.0, 200.0, 300.0), 6.0),
    ]

    placed = 0
    for index, (kind, location, scale) in enumerate(layout):
        mesh = unreal.load_asset(shapes[kind])
        if mesh is None:
            log("missing shape %s" % kind)
            continue

        actor = actor_subsystem.spawn_actor_from_class(
            unreal.StaticMeshActor, unreal.Vector(*location),
            unreal.Rotator(pitch=0.0, yaw=index * 30.0, roll=0.0))
        if actor is None:
            continue
        actor.set_actor_label("Prop_%d_%s" % (index, kind))
        component = actor.get_component_by_class(unreal.StaticMeshComponent)
        component.set_editor_property("static_mesh", mesh)
        actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))

        material = unreal.load_asset(materials[kind])
        if material is not None:
            component.set_material(0, material)
        placed += 1
        log("  Prop_%d_%s at (%.0f, %.0f, %.0f) scale %.1f"
            % (index, kind, location[0], location[1], location[2], scale))

    log("placed %d props" % placed)
    log("actors: %d" % len(unreal.EditorLevelLibrary.get_all_level_actors()))
    log("saved: %r" % level_subsystem.save_current_level())
    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
