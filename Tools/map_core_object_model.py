"""Map the core object model from the engine's own headers.

Most confusion about Unreal comes from not holding the object graph clearly: what owns what, what
ticks, what can be garbage collected, and which of the three "component" words means which thing.
The engine's headers answer all of it, and answering it from the headers rather than from memory
is the difference between a claim and a fact.

This reads the class declarations and prints what each inherits from, which is the skeleton the
rest of the system hangs on.

    python Tools/map_core_object_model.py
"""

import os
import re

ENGINE = r"C:\Program Files\Epic Games\UE_5.8\Engine\Source"

WANTED = {
    "UObject": "Runtime/CoreUObject/Public/UObject/Object.h",
    "AActor": "Runtime/Engine/Classes/GameFramework/Actor.h",
    "UActorComponent": "Runtime/Engine/Classes/Components/ActorComponent.h",
    "USceneComponent": "Runtime/Engine/Classes/Components/SceneComponent.h",
    "UPrimitiveComponent": "Runtime/Engine/Classes/Components/PrimitiveComponent.h",
    "UWorld": "Runtime/Engine/Classes/Engine/World.h",
    "ULevel": "Runtime/Engine/Classes/Engine/Level.h",
    "AGameModeBase": "Runtime/Engine/Classes/GameFramework/GameModeBase.h",
    "AGameStateBase": "Runtime/Engine/Classes/GameFramework/GameStateBase.h",
    "APlayerController": "Runtime/Engine/Classes/GameFramework/PlayerController.h",
    "APawn": "Runtime/Engine/Classes/GameFramework/Pawn.h",
    "ACharacter": "Runtime/Engine/Classes/GameFramework/Character.h",
    "AHUD": "Runtime/Engine/Classes/GameFramework/HUD.h",
    "UEngine": "Runtime/Engine/Classes/Engine/Engine.h",
    "UGameInstance": "Runtime/Engine/Classes/Engine/GameInstance.h",
}


def find_class_header(class_name, hint):
    """Try the hinted path first, then fall back to a search."""
    candidate = os.path.join(ENGINE, hint.replace("/", os.sep))
    if os.path.exists(candidate):
        return candidate
    stem = class_name[1:] + ".h"
    for root, dirs, files in os.walk(ENGINE):
        if stem in files:
            return os.path.join(root, stem)
    return None


def inheritance(path, class_name):
    """Read the class declaration and pull out its base list."""
    text = open(path, encoding="utf-8", errors="replace").read()
    # Class declarations may span lines and carry API macros.
    pattern = re.compile(
        r"class\s+(?:\w+_API\s+)?%s\s*(?:final\s*)?:\s*public\s+([^{]+)\{" % re.escape(class_name),
        re.S)
    match = pattern.search(text)
    if not match:
        return None, len(text)
    bases = " ".join(match.group(1).split())
    return bases, len(text)


def count_of(text, needle):
    return text.count(needle)


def main():
    print("%-20s %-52s %s" % ("class", "inherits from", "header size"))
    print("-" * 96)
    resolved = {}
    for class_name, hint in WANTED.items():
        path = find_class_header(class_name, hint)
        if path is None:
            print("%-20s %-52s NOT FOUND" % (class_name, "-"))
            continue
        resolved[class_name] = path
        bases, size = inheritance(path, class_name)
        print("%-20s %-52s %d B" % (class_name, (bases or "(declaration not matched)")[:52], size))
    print("")

    # What each of these offers is more useful than what it inherits, so count the notable pieces.
    print("%-20s %8s %8s %8s %8s" % ("class", "UFUNCTION", "UPROPERTY", "public:", "private:"))
    print("-" * 60)
    for class_name, path in resolved.items():
        text = open(path, encoding="utf-8", errors="replace").read()
        print("%-20s %8d %8d %8d %8d"
              % (class_name, count_of(text, "UFUNCTION"), count_of(text, "UPROPERTY"),
                 count_of(text, "public:"), count_of(text, "private:")))
    print("")

    # Component vs actor: the three words that get confused.
    print("the three words that get confused:")
    for class_name in ("AActor", "UActorComponent", "USceneComponent", "UPrimitiveComponent"):
        path = resolved.get(class_name)
        if not path:
            continue
        text = open(path, encoding="utf-8", errors="replace").read()
        has_tick = "virtual void Tick" in text or "TickComponent" in text
        has_transform = "SetActorLocation" in text or "SetRelativeLocation" in text
        has_render = "SetMaterial" in text or "GetMaterial" in text
        print("  %-22s tick=%-5s transform=%-5s material=%-5s"
              % (class_name, has_tick, has_transform, has_render))


if __name__ == "__main__":
    main()
