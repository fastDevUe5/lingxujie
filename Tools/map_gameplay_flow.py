"""Trace the gameplay flow: what happens between a level loading and a player being control.

The classes were mapped in an earlier block; what was missing is the order they are called in.
That order explains most "my spawn is in the wrong place" and "my input does nothing" problems,
because each step has an overridable hook and getting the hook wrong is invisible until runtime.

Each function below was found in the header named beside it, so the sequence is drawn from the
engine's own declarations rather than from memory.

    python Tools/map_gameplay_flow.py
"""

import os
import re

ENGINE = r"C:\Program Files\Epic Games\UE_5.8\Engine\Source"

# name -> file it should appear in
FLOW = [
    ("UGameInstance::Init", "GameInstance.h"),
    ("UWorld::BeginPlay", "World.h"),
    ("UWorld::SpawnActor", "World.h"),
    ("AGameModeBase::InitGame", "GameModeBase.h"),
    ("AGameModeBase::PostLogin", "GameModeBase.h"),
    ("AGameModeBase::HandleStartingNewPlayer", "GameModeBase.h"),
    ("AGameModeBase::RestartPlayer", "GameModeBase.h"),
    ("AGameModeBase::ChoosePlayerStart", "GameModeBase.h"),
    ("AGameModeBase::SpawnDefaultPawnFor", "GameModeBase.h"),
    ("AGameModeBase::RestartPlayerAtPlayerStart", "GameModeBase.h"),
    ("APlayerController::SetPawn", "Controller.h"),
    ("APlayerController::AcknowledgePossession", "PlayerController.h"),
    ("APawn::PossessedBy", "Pawn.h"),
    ("AActor::BeginPlay", "Actor.h"),
]

# The overridable hooks an actor can react to, which is where gameplay code goes.
HOOKS = {
    "AActor": ["BeginPlay", "EndPlay", "Tick", "PostInitializeComponents",
               "OnConstruction", "SetActorHiddenInGame"],
    "APawn": ["PossessedBy", "UnPossessed", "Restart", "SetupPlayerInputComponent"],
    "APlayerController": ["BeginPlay", "SetupInputComponent", "OnPossess", "OnUnPossess",
                          "AcknowledgePossession", "PlayerTick"],
    "AGameModeBase": ["InitGame", "PostLogin", "HandleStartingNewPlayer", "RestartPlayer",
                      "ChoosePlayerStart", "SpawnDefaultPawnFor"],
    "AGameStateBase": ["HandleBeginPlay"],
}


def find(filename):
    for root, dirs, files in os.walk(ENGINE):
        if filename in files:
            return os.path.join(root, filename)
    return None


def main():
    print("%-46s %-14s %s" % ("step", "in file", "found"))
    print("-" * 80)
    missing = 0
    for step, filename in FLOW:
        function = step.split("::")[1]
        path = find(filename)
        if path is None:
            print("%-46s %-14s file missing" % (step, filename))
            missing += 1
            continue
        text = open(path, encoding="utf-8", errors="replace").read()
        found = re.search(r"\b%s\s*\(" % function, text) is not None
        if not found:
            missing += 1
        print("%-46s %-14s %s" % (step, filename, "yes" if found else "NOT FOUND"))
    print("")
    print("%d of %d steps verified in headers" % (len(FLOW) - missing, len(FLOW)))
    print("")

    print("overridable hooks per class:")
    for class_name, hooks in HOOKS.items():
        filename = {
            "AActor": "Actor.h",
            "APawn": "Pawn.h",
            "APlayerController": "PlayerController.h",
            "AGameModeBase": "GameModeBase.h",
            "AGameStateBase": "GameStateBase.h",
        }[class_name]
        path = find(filename)
        if path is None:
            continue
        text = open(path, encoding="utf-8", errors="replace").read()
        present = [h for h in hooks if re.search(r"\b%s\s*\(" % h, text)]
        print("  %-20s %s" % (class_name, ", ".join(present) or "none matched"))
    print("")


if __name__ == "__main__":
    main()
