"""Turn the per-variant CVar read-backs into one line per knob.

"Did the picture change" and "did the setting take" are different questions, and the first pass of
this series answered them with one number. Here the console value is read after the variant is applied
and before it is reset, so a zero pixel difference can be attributed instead of guessed at.

    python Tools/learn_cvar_read.py Saved/learn_ab3/cvar_readback.txt
"""

import json
import sys


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "Saved/learn_ab3/cvar_readback.txt"
    rows = []
    with open(path, encoding="utf-8-sig") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            variant, rest = line.split(" ", 1)
            probe, payload = rest.split(" => ", 1)
            try:
                outer = json.loads(payload)
                inner = json.loads(outer["returnValue"])
            except Exception as error:  # noqa: BLE001
                rows.append((variant, probe, "parse error: %r" % (error,)))
                continue
            if not inner:
                rows.append((variant, probe, "NOT FOUND"))
                continue
            for name, info in inner.items():
                rows.append((variant, name, info.get("value")))

    print("%-22s %-46s %s" % ("variant", "cvar", "value at capture time"))
    for variant, name, value in rows:
        print("%-22s %-46s %s" % (variant, name, value))
    return 0


if __name__ == "__main__":
    sys.exit(main())
