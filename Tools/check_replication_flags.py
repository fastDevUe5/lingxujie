"""Check the replication markers on the gameplay framework classes.

The claim that GameMode lives only on the server and GameState is what clients see is widely
repeated, and it has a checkable origin: the flags in the class bodies. This reads them rather
than restating the folklore.

    python Tools/check_replication_flags.py
"""

import os
import re

CLASSES = r"C:\Program Files\Epic Games\UE_5.8\Engine\Source\Runtime\Engine\Classes\GameFramework"

FILES = [
    "GameModeBase.h",
    "GameStateBase.h",
    "PlayerController.h",
    "Pawn.h",
    "Character.h",
    "HUD.h",
    "Actor.h",
    "Info.h",
    "Controller.h",
]

FLAGS = ["bReplicates", "bAlwaysRelevant", "bReplicateMovement", "bNetLoadOnClient",
         "bOnlyRelevantToOwner", "bNetUseOwnerRelevancy"]


def main():
    print("%-22s %-12s %-12s %-12s %s"
          % ("file", "bReplicates", "bAlwaysRelevant", "RepMovement", "GetLifetimeReplicatedProps"))
    print("-" * 84)

    for name in FILES:
        path = os.path.join(CLASSES, name)
        if not os.path.exists(path):
            continue
        text = open(path, encoding="utf-8", errors="replace").read()

        def flag_state(flag):
            # The declaration is either a default in the constructor or a property line.
            if re.search(r"%s\s*=\s*true" % flag, text):
                return "true"
            if re.search(r"%s\s*=\s*false" % flag, text):
                return "false"
            if flag in text:
                return "present"
            return "-"

        replicated_props = "yes" if "GetLifetimeReplicatedProps" in text else "no"
        print("%-22s %-12s %-12s %-12s %s"
              % (name, flag_state("bReplicates"), flag_state("bAlwaysRelevant"),
                 flag_state("bReplicateMovement"), replicated_props))

    print("")
    print("What the flags mean:")
    print("  bReplicates            the actor exists on clients as well as the server")
    print("  bAlwaysRelevant        every client gets it, regardless of distance")
    print("  bReplicateMovement     position and rotation are sent each update")
    print("  GetLifetimeReplicatedProps  the class declares which members replicate")


if __name__ == "__main__":
    main()
