"""Check whether the C++ API reference can be mirrored for the classes this project uses.

The project is seventeen C++ modules. Guide pages explain concepts, but the thing actually consulted
while writing C++ is the API reference for a specific class. Those pages live under the same host at
/API/<Module>/<Class>, so they should be mirrorable with the same fetch.

    python Tools/probe_cpp_api.py
"""

import re
import urllib.error
import urllib.request

BASE = "https://dev.epicgames.com/documentation/en-us/unreal-engine/API/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
TITLE = re.compile(r"<title>(.*?)</title>", re.S)

# Classes the project inherits from or calls, one per area.
CANDIDATES = [
    "Runtime/Engine/GameFramework/AHUD",
    "Runtime/Engine/GameFramework/ACharacter",
    "Runtime/Engine/GameFramework/AGameModeBase",
    "Runtime/Engine/GameFramework/AActor",
    "Runtime/Engine/GameFramework/APawn",
    "Runtime/Engine/GameFramework/APlayerController",
    "Runtime/Engine/GameFramework/UActorComponent",
    "Runtime/Engine/Engine/UCanvas",
    "Runtime/Engine/Engine/UTexture2D",
    "Runtime/Engine/Engine/UWorld",
    "Runtime/Engine/Engine/UDataTable",
    "Runtime/Engine/GameFramework/USaveGame",
    "Runtime/Engine/Engine/UMaterialInstanceDynamic",
    "Runtime/Engine/Engine/UStaticMeshComponent",
    "Runtime/Engine/Engine/USkeletalMeshComponent",
    "Runtime/Engine/Engine/UGameplayStatics",
]


def probe(path):
    url = BASE + path
    request = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            text = response.read(150000).decode("utf-8", errors="replace")
    except urllib.error.HTTPError as error:
        return None, 0, "http %d" % error.code
    except Exception as error:  # noqa: BLE001
        return None, 0, repr(error)[:40]

    match = TITLE.search(text)
    title = match.group(1).strip() if match else "(no title)"
    return title, len(text), "ok"


def main():
    print("%-52s %-10s %s" % ("API path", "bytes", "title"))
    print("-" * 130)
    ok = 0
    for path in CANDIDATES:
        title, size, reason = probe(path)
        if title:
            ok += 1
            print("%-52s %-10d %s" % (path, size, title[:60]))
        else:
            print("%-52s %-10s %s" % (path, "-", reason))
    print("")
    print("resolved %d / %d" % (ok, len(CANDIDATES)))


if __name__ == "__main__":
    main()
