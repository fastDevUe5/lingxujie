"""Dump every project setting that matters, from one place.

Twice now an assessment has been wrong because it came from memory or from a name rather than from
the configuration file: a hundred assets called stale that were the textures, and Lumen called
absent while it had been running since the first commit. Both would have been settled by reading
four ini files.

This tool reads them and prints the settings grouped by what they decide, so "is X on" has an
answer that does not depend on recollection.

    python Tools/audit_project_config.py
"""

import os
import re

CONFIG = "C:/Users/tk/Desktop/lingxujie/Config"

# What we actually want to know, and why.
QUESTIONS = [
    ("渲染 - 全局光照", "r.DynamicGlobalIlluminationMethod",
     {0: "None", 1: "Lumen", 2: "ScreenSpace (deprecated)", 3: "Plugin"}),
    ("渲染 - 反射", "r.ReflectionMethod",
     {0: "None", 1: "Lumen", 2: "ScreenSpace", 3: "RayTraced"}),
    ("渲染 - 抗锯齿", "r.AntiAliasingMethod",
     {0: "None", 1: "FXAA", 2: "TAA", 3: "MSAA", 4: "TSR"}),
    ("渲染 - 虚拟阴影", "r.Shadow.Virtual.Enable", None),
    ("渲染 - 网格距离场", "r.GenerateMeshDistanceFields", None),
    ("渲染 - 静态光照", "r.AllowStaticLighting", None),
    ("渲染 - 自动曝光", "r.DefaultFeature.AutoExposure", None),
    ("渲染 - 泛光", "r.DefaultFeature.Bloom", None),
    ("渲染 - 运动模糊", "r.DefaultFeature.MotionBlur", None),
    ("渲染 - 硬件光追", "r.Lumen.HardwareRayTracing", None),
    ("输入 - 玩家输入类", "DefaultPlayerInputClass", None),
    ("输入 - 输入组件类", "DefaultInputComponentClass", None),
]

# Sections worth mentioning even when we do not interpret them.
NOTABLE_SECTIONS = [
    "GameMapsSettings", "RendererSettings", "InputSettings",
    "ProjectPackagingSettings", "GeneralProjectSettings", "DeviceProfile",
]


def read_all():
    """Return every key=value from every ini, with the file it came from."""
    values = {}
    for filename in sorted(os.listdir(CONFIG)):
        if not filename.endswith(".ini"):
            continue
        path = os.path.join(CONFIG, filename)
        text = open(path, encoding="utf-8", errors="replace").read()
        for line in text.split("\n"):
            stripped = line.strip()
            if not stripped or stripped.startswith((";", "#", "[")):
                continue
            if "=" not in stripped:
                continue
            key, _, value = stripped.partition("=")
            values[key.strip().lstrip("+-!")] = (value.strip(), filename)
    return values


def main():
    values = read_all()
    print("config files read: %s" % ", ".join(
        f for f in sorted(os.listdir(CONFIG)) if f.endswith(".ini")))
    print("keys collected: %d" % len(values))
    print("")

    print("%-22s %-34s %-22s %s" % ("what", "key", "value", "source"))
    print("-" * 96)
    for label, key, meanings in QUESTIONS:
        entry = values.get(key)
        if entry is None:
            print("%-22s %-34s %-22s %s" % (label, key, "(not set)", "-"))
            continue
        raw, filename = entry
        shown = raw
        if meanings is not None:
            try:
                shown = "%s (%s)" % (raw, meanings.get(int(raw), "?"))
            except ValueError:
                pass
        print("%-22s %-34s %-22s %s" % (label, key, shown[:22], filename))
    print("")

    # Sections present, so nothing is invisible just because we did not ask about it.
    print("sections present per file:")
    for filename in sorted(os.listdir(CONFIG)):
        if not filename.endswith(".ini"):
            continue
        text = open(os.path.join(CONFIG, filename), encoding="utf-8", errors="replace").read()
        sections = re.findall(r"^\[([^\]]+)\]", text, re.M)
        print("  %-28s %s" % (filename, ", ".join(sections) or "(none)"))
    print("")

    # Anything mentioning a notable keyword that we did not already report.
    reported = {key for _, key, _ in QUESTIONS}
    extras = []
    for key, (value, filename) in values.items():
        if key in reported:
            continue
        if any(part in key for part in ("Lumen", "Ray", "Shadow", "Exposure", "Scalability")):
            extras.append((key, value, filename))
    if extras:
        print("other render-related keys:")
        for key, value, filename in sorted(extras):
            print("  %-46s %-16s %s" % (key[:46], value[:16], filename))
        print("")

    print("reminder: a key that is absent means the engine default applies, and the default is")
    print("sometimes on. Reading a config file cannot tell you what the default is - that needs")
    print("the engine's own header.")


if __name__ == "__main__":
    main()
