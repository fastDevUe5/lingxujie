"""Map the replication system from the headers that define it.

This project's slice is single-player, so networking is not on the critical path - but a handover
document that says "we did not look" is worth less than one that says what the mechanism is and why
it is not needed yet.

Replication in Unreal comes down to three declarations: an actor opts in with bReplicates, a
property opts in with the Replicated specifier, and the class lists those properties in
GetLifetimeReplicatedProps. Everything else is policy on top of that.

    python Tools/map_networking.py
"""

import os
import re

ENGINE = r"C:\Program Files\Epic Games\UE_5.8\Engine\Source"

TARGETS = [
    ("UNetDriver", "NetDriver.h"),
    ("FRepLayout", "RepLayout.h"),
    ("FRepState", "RepLayout.h"),
    ("UNetConnection", "NetConnection.h"),
    ("FNetBitWriter", "NetSerialization.h"),
]

SPECIFIERS = ["Replicated", "ReplicatedUsing", "RepNotify", "Server", "Client",
              "NetMulticast", "Reliable", "Unreliable", "WithValidation"]


def find(filename):
    for root, dirs, files in os.walk(ENGINE):
        if filename in files:
            return os.path.join(root, filename)
    return None


def main():
    print("%-22s %-46s %s" % ("class", "header", "size"))
    print("-" * 84)
    for class_name, filename in TARGETS:
        path = find(filename)
        if path is None:
            print("%-22s %-46s missing" % (class_name, filename))
            continue
        print("%-22s %-46s %7d B"
              % (class_name, os.path.relpath(path, ENGINE)[:46], os.path.getsize(path)))
    print("")

    # What a class has to declare to take part, and how many engine classes do.
    driver = find("NetDriver.h")
    if driver:
        text = open(driver, encoding="utf-8", errors="replace").read()
        print("UNetDriver: %d bytes" % len(text))
        for name in ("ServerTravel", "ClientTravel", "TickDispatch", "TickFlush",
                     "ProcessRemoteFunction", "ReplicateActors"):
            if name in text:
                print("   has %s" % name)
        print("")

    layout = find("RepLayout.h")
    if layout:
        text = open(layout, encoding="utf-8", errors="replace").read()
        print("FRepLayout: %d bytes" % len(text))
        for name in ("InitFromObject", "SerializeProperties", "SendProperties",
                     "ReceiveProperties", "BuildSharedSerialization"):
            if name in text:
                print("   has %s" % name)
        print("")

    # How widely each replication specifier is used in the engine itself.
    print("engine usage of the replication specifiers:")
    counts = {name: 0 for name in SPECIFIERS}
    scanned = 0
    for root, dirs, files in os.walk(ENGINE):
        for filename in files:
            if not filename.endswith(".h"):
                continue
            scanned += 1
            if scanned > 6000:
                break
            try:
                text = open(os.path.join(root, filename), encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            if "UFUNCTION" not in text and "UPROPERTY" not in text:
                continue
            for name in SPECIFIERS:
                counts[name] += len(re.findall(r"\b%s\b" % name, text))
        if scanned > 6000:
            break
    for name, count in sorted(counts.items(), key=lambda item: -item[1]):
        print("   %-18s %6d" % (name, count))
    print("")
    print("headers scanned: %d" % scanned)


if __name__ == "__main__":
    main()
