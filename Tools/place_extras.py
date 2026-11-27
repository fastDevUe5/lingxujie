"""Put back the actors that build_level.py does not create itself.

The level is rebuilt from scratch on every run (new_level), so anything that was placed by
a one-off script disappears on the next rebuild: the boss statue with its material, the bird
and bobu reference models, and the background music. That is how a rebuild silently turned
116 actors into 110 and dropped the boss material fix along with the actors.

This module puts them back, idempotently, and build_level.py calls place_all() before saving
the level. Nothing here is new content: every number comes from the script that placed it
first (place_static_boss.py, place_bird.py, place_bobu.py, add_level_music.py).

Two actors that used to sit in the level are deliberately not restored: MX_BOSS001 and
MX_BOSSCOWF. Both imported with a collapsed skeleton (span 0.00 cm, recorded in
NEXT-SESSION 第 23 节) and existed only as diagnostics for that bug.
"""

import unreal

BOSS_STATIC = {
    "label": "MX_BOSS001_STATIC",
    "mesh": "/Game/Moxiang/Static/boss001_static/StaticMeshes/SM_Boss001.SM_Boss001",
    "material": "/Game/Moxiang/Materials/M_Boss_Mob01.M_Boss_Mob01",
    "location": (9550.0, -6200.0, 3740.0),
    "scale": 1.0,
}

BIRD = {
    "label": "MX_BIRD_TEST",
    "mesh": "/Game/Moxiang/Skeletal/bird/SkeletalMeshes/SK_Bird.SK_Bird",
    "location": (9200.0, -6200.0, 3820.0),
    "scale": 4.0,
}

BOBU = {
    "label": "MX_BOBU_TEST",
    "mesh": "/Game/Moxiang/Skeletal/Characters/char_bobu/SkeletalMeshes/SK_Bobu.SK_Bobu",
    "location": (9600.0, -6200.0, 3660.0),
    "scale": 1.0,
}

MUSIC = {
    "label": "MX_AMBIENT_MUSIC",
    "sound": "/Game/Moxiang/Audio/S_bg_field.S_bg_field",
    "location": (8950.0, -6200.0, 3800.0),
    "volume": 0.6,
}

LABELS = [BOSS_STATIC["label"], BIRD["label"], BOBU["label"], MUSIC["label"]]


def log(text):
    unreal.log("[LingXuJie] EXTRA: %s" % text)


def _remove(subsystem, labels):
    removed = 0
    for actor in subsystem.get_all_level_actors():
        if actor.get_actor_label() in labels:
            subsystem.destroy_actor(actor)
            removed += 1
    return removed


def _place_static(subsystem, spec):
    mesh = unreal.EditorAssetLibrary.load_asset(spec["mesh"])
    if mesh is None:
        log("%s: mesh missing %s" % (spec["label"], spec["mesh"]))
        return 0
    location = unreal.Vector(*spec["location"])
    actor = subsystem.spawn_actor_from_class(unreal.StaticMeshActor, location,
                                             unreal.Rotator(0.0, 0.0, 0.0))
    if actor is None:
        log("%s: spawn returned nothing" % spec["label"])
        return 0
    actor.set_actor_label(spec["label"])
    if spec.get("scale", 1.0) != 1.0:
        actor.set_actor_scale3d(unreal.Vector(spec["scale"], spec["scale"], spec["scale"]))

    component = actor.get_component_by_class(unreal.StaticMeshComponent)
    if component is None:
        log("%s: no static mesh component" % spec["label"])
        return 0
    component.set_static_mesh(mesh)

    material_path = spec.get("material")
    if material_path:
        material = unreal.EditorAssetLibrary.load_asset(material_path)
        if material is None:
            log("%s: material missing %s" % (spec["label"], material_path))
        else:
            for slot in range(component.get_num_materials()):
                component.set_material(slot, material)
            log("%s: %d slot(s) -> %s" % (spec["label"], component.get_num_materials(),
                                          material.get_name()))
    return 1


def _place_skeletal(subsystem, spec):
    mesh = unreal.EditorAssetLibrary.load_asset(spec["mesh"])
    if mesh is None:
        log("%s: mesh missing %s" % (spec["label"], spec["mesh"]))
        return 0
    location = unreal.Vector(*spec["location"])
    actor = subsystem.spawn_actor_from_class(unreal.SkeletalMeshActor, location,
                                             unreal.Rotator(0.0, 0.0, 0.0))
    if actor is None:
        log("%s: spawn returned nothing" % spec["label"])
        return 0
    actor.set_actor_label(spec["label"])
    if spec.get("scale", 1.0) != 1.0:
        actor.set_actor_scale3d(unreal.Vector(spec["scale"], spec["scale"], spec["scale"]))

    component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
    if component is None:
        log("%s: no skeletal mesh component" % spec["label"])
        return 0
    component.set_skeletal_mesh_asset(mesh)
    return 1


def _place_music(subsystem, spec):
    track = unreal.EditorAssetLibrary.load_asset(spec["sound"])
    if track is None:
        log("%s: sound missing %s" % (spec["label"], spec["sound"]))
        return 0
    location = unreal.Vector(*spec["location"])
    actor = subsystem.spawn_actor_from_class(unreal.AmbientSound, location,
                                             unreal.Rotator(0.0, 0.0, 0.0))
    if actor is None:
        log("%s: spawn returned nothing" % spec["label"])
        return 0
    actor.set_actor_label(spec["label"])

    component = actor.get_component_by_class(unreal.AudioComponent)
    if component is None:
        log("%s: no audio component" % spec["label"])
        return 0
    component.set_editor_property("sound", track)
    component.set_editor_property("auto_activate", True)
    component.set_editor_property("volume_multiplier", spec.get("volume", 1.0))
    return 1


def place_all():
    """Remove the previous copies and place them again. Safe to call on every rebuild."""
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    removed = _remove(subsystem, LABELS)

    placed = 0
    placed += _place_static(subsystem, BOSS_STATIC)
    placed += _place_skeletal(subsystem, BIRD)
    placed += _place_skeletal(subsystem, BOBU)
    placed += _place_music(subsystem, MUSIC)

    log("extras: %d of %d placed (%d removed first)" % (placed, len(LABELS), removed))
    return placed
