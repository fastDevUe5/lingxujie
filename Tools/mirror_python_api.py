"""Mirror the Python API reference pages for the classes this project actually uses.

The whole Unreal documentation set is tens of thousands of pages and changes with every release,
so a local copy of all of it would be large and quietly wrong. The Python API reference is a
different matter: it is generated per release - the 5.8 pages match the engine installed here -
it is small, and it is the one thing the C++ headers under Engine/Source cannot tell us, namely
the Python names and signatures.

This fetches only the classes the project touches, strips the navigation, and writes one file per
class plus an index. Re-run it after an engine upgrade.

    python Tools/mirror_python_api.py
"""

import os
import re
import urllib.error
import urllib.request

OUT_DIR = "C:/Users/tk/Desktop/lingxujie/Docs/PythonAPI"
BASE = "https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/"

CLASSES = [
    # Subsystems this project drives
    "UnrealEditorSubsystem",
    "LevelEditorSubsystem",
    "EditorActorSubsystem",
    "EditorAssetSubsystem",
    "StaticMeshEditorSubsystem",
    "EditorSubsystem",
    # Asset work
    "AssetTools",
    "AssetImportTask",
    "EditorAssetLibrary",
    "MeshEditingLibrary",
    "StaticMesh",
    "StaticMeshComponent",
    # Materials
    "MaterialEditingLibrary",
    "MaterialInstanceConstantFactoryNew",
    "MaterialFactoryNew",
    # Structure and maths
    "Vector",
    "Rotator",
    "Transform",
    "LinearColor",
    "ToolsetDefinition",
    "ToolAccessMode",
]


def strip_html(html):
    """Reduce the page to its content, which is all that is worth keeping."""
    # The interesting part starts at the class heading and ends at the table of contents.
    start = html.find("<h1")
    if start < 0:
        start = 0
    end = html.find("Table of Contents")
    body = html[start:end] if end > start else html[start:]

    body = re.sub(r"<script.*?</script>", "", body, flags=re.S)
    body = re.sub(r"<style.*?</style>", "", body, flags=re.S)
    body = re.sub(r"<[^>]+>", "", body)
    body = body.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<")
    body = body.replace("&gt;", ">").replace("&quot;", '"').replace("&#182;", "")
    body = re.sub(r"[ \t]+", " ", body)
    body = re.sub(r"\n\s*\n\s*\n+", "\n\n", body)
    return body.strip()


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    saved = []
    failed = []

    for name in CLASSES:
        url = BASE + name
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                html = response.read().decode("utf-8", errors="replace")
        except (urllib.error.URLError, TimeoutError) as error:
            failed.append((name, str(error)[:90]))
            continue

        text = strip_html(html)
        if len(text) < 200:
            failed.append((name, "page looked empty"))
            continue

        header = "# unreal.%s  (UE 5.8 Python API)\n\nSource: %s\n\n" % (name, url)
        with open(os.path.join(OUT_DIR, name + ".txt"), "w", encoding="utf-8") as handle:
            handle.write(header + text)
        saved.append(name)

    with open(os.path.join(OUT_DIR, "README.md"), "w", encoding="utf-8") as handle:
        handle.write("# 本地 UE 5.8 Python API 索引\n\n")
        handle.write("来源：`dev.epicgames.com/documentation/en-us/unreal-engine/python-api/`，"
                     "对应 **UE 5.8**（与本机引擎一致）。\n\n")
        handle.write("**只镜像了本项目实际用到的类**，不是整站。"
                     "整站有数万页且随版本变化，镜像下来既大又会悄悄过期。\n\n")
        handle.write("权威顺序：**本机 `Engine/Source` 源码 > 这里的 Python 签名 > 概念文档**。\n\n")
        if saved:
            handle.write("## 已收录 (%d)\n\n" % len(saved))
            for name in saved:
                handle.write("- `%s.txt`\n" % name)
        if failed:
            handle.write("\n## 抓取失败 (%d)\n\n" % len(failed))
            for name, why in failed:
                handle.write("- `%s` — %s\n" % (name, why))

    print("saved %d, failed %d -> %s" % (len(saved), len(failed), OUT_DIR))
    for name, why in failed:
        print("  failed %s: %s" % (name, why))


if __name__ == "__main__":
    main()
