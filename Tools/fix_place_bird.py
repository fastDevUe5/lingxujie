"""Make the bird placement repeatable, so the shot can be reframed without duplicates.

    python Tools/fix_place_bird.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Tools/place_bird.py"

OLD = """    for actor in subsystem.get_all_level_actors():
        if actor.get_actor_label() == LABEL:
            log("already placed")
            return"""

NEW = """    for actor in subsystem.get_all_level_actors():
        if actor.get_actor_label() == LABEL:
            log("removing the earlier placement")
            subsystem.destroy_actor(actor)"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if OLD not in text:
        print("target not found; already patched?")
        return
    open(PATH, "w", encoding="utf-8").write(text.replace(OLD, NEW))
    print("placement is now repeatable")


if __name__ == "__main__":
    main()
