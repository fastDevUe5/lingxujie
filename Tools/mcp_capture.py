"""Save the image and metadata out of an MCP viewport capture.

The capture tool returns one JSON blob whose image field is a base64 PNG. The generic MCP helper
writes tool results as text, so the blob lands in a file as characters instead of as a picture. This
picks the base64 out, writes the PNG next to it, and prints where the camera was and what it could
see, which is what makes a screenshot verifiable rather than merely illustrative.

    python Tools/mcp_capture.py Saved/mcp_raw.json Saved/viewport.png
"""

import base64
import json
import os
import sys


def main():
    if len(sys.argv) < 3:
        print("usage: mcp_capture.py <raw json> <out png>")
        return 1
    raw_path, png_path = sys.argv[1], sys.argv[2]
    text = open(raw_path, encoding="utf-8-sig", errors="replace").read()

    start = text.find('"data"')
    if start < 0:
        print("no image data in the result")
        print(text[:400])
        return 1
    quote = text.find('"', text.find(":", start) + 1)
    end = text.find('"', quote + 1)
    payload = text[quote + 1:end]
    data = base64.b64decode(payload)
    os.makedirs(os.path.dirname(png_path) or ".", exist_ok=True)
    with open(png_path, "wb") as handle:
        handle.write(data)
    print("image %d bytes -> %s" % (len(data), png_path))

    for key in ("cameraLocation", "cameraRotation", "cameraFOV"):
        index = text.find('"%s"' % key)
        if index >= 0:
            print("  %s %s" % (key, text[index:index + 90].replace("\n", " ")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
