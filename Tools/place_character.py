"""Drop a stand-in character into the plaza so scale can be judged.

Looking at streets with no person in them makes it impossible to say whether a doorway is two
metres or six. This spawns the project's own character class at a chosen point, then the caller
photographs it from a short distance - the same character the game itself uses, so what the
editor shows is what the game will show.

    python Tools/place_character.py 8950 -6200 3845
"""

import unreal

LEVEL_PY = "C:/Users/tk/Desktop/lingxujie/Tools"

CANDIDATES = ["LXJCharacter", "LXJCharacter_C", "Character", "BP_ThirdPersonCharacter"]


def log(message):
    unreal.log("[LingXuJie] PLACE: %s" % message)


def find_character_class():
    for name in CANDIDATES:
        cls = unreal.EditorAssetLibrary.load_class(None, "/Script/LingXuJie.%s" % name)
        if cls is not None:
            log("class found: %s" % name)
            return cls
    # The C++ class is reachable through the module regardless of the blueprint search.
    try:
        cls = unreal.LXJCharacter
        log("class found: LXJCharacter (direct)")
        return cls
    except AttributeError:
        pass
    return None


def main():
    location = unreal.Vector(8950.0, -6200.0, 3845.0)
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

    for actor in list(subsystem.get_all_level_actors()):
        if actor.get_actor_label().startswith("MX_CHARACTER"):
            subsystem.destroy_actor(actor)
            log("removed old stand-in")

    cls = find_character_class()
    if cls is None:
        log("character class not found; labels tried: %s" % ", ".join(CANDIDATES))
        return

    character = subsystem.spawn_actor_from_class(cls, location, unreal.Rotator(0.0, 0.0, 0.0))
    if character is None:
        log("spawn failed")
        return

    character.set_actor_label("MX_CHARACTER")
    character.set_actor_scale3d(unreal.Vector(1.0, 1.0, 1.0))
    log("spawned at %.0f, %.0f, %.0f" % (location.x, location.y, location.z))


main()
