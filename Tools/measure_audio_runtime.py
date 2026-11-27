"""Find out what the imported music actually costs at runtime, as distinct from its file size.

The uasset went from eleven megabytes to eleven megabytes after lowering the compression quality,
which means the file on disk is not the compressed runtime data. The compressed form lives
elsewhere - in derived data while in the editor, and in the cooked package in a build. Reporting
the uasset size as the shipping cost would be wrong, so this measures the runtime footprint
directly.

    py "Tools/measure_audio_runtime.py"
"""

import os

import unreal

ASSETS = [
    "/Game/Moxiang/Audio/S_bg_field",
    "/Game/Moxiang/Audio/S_M004_Attack_01",
]
DISK_DIR = "C:/Users/tk/Desktop/lingxujie/Content/Moxiang/Audio"


def log(text):
    unreal.log("[LingXuJie] AUDIOSIZE: %s" % text)


def main():
    for path in ASSETS:
        name = path.rsplit("/", 1)[-1]
        sound = unreal.EditorAssetLibrary.load_asset("%s.%s" % (path, name))
        if sound is None:
            log("%s missing" % name)
            continue

        disk = os.path.join(DISK_DIR, name + ".uasset")
        file_size = os.path.getsize(disk) if os.path.exists(disk) else 0
        log("%s" % name)
        log("    uasset on disk      %.2f MB" % (file_size / (1024.0 * 1024.0)))

        # The runtime footprint, which is what the packaged build carries.
        try:
            resource = sound.get_resource_size()
            log("    runtime resource    %.2f MB" % (resource / (1024.0 * 1024.0)))
        except Exception as error:  # noqa: BLE001
            log("    runtime resource    (unavailable: %s)" % error)

        # Duration and the derived-data format tell us what the runtime actually decodes.
        try:
            log("    duration            %.2f s" % sound.get_editor_property("duration"))
        except Exception:  # noqa: BLE001
            pass
        try:
            log("    compression_quality %s" % sound.get_editor_property("compression_quality"))
        except Exception:  # noqa: BLE001
            pass
        log("")

    # Where the compressed data actually lives, for evidence.
    ddc = "C:/Users/tk/Desktop/lingxujie/DerivedDataCache"
    if os.path.exists(ddc):
        total = 0
        count = 0
        for root, dirs, files in os.walk(ddc):
            for filename in files:
                count += 1
                try:
                    total += os.path.getsize(os.path.join(root, filename))
                except OSError:
                    pass
        log("DDC: %d files, %.1f MB total (includes cooked audio)" % (count, total / (1024.0 * 1024.0)))
    else:
        log("DDC not found at %s" % ddc)

    log("note: uasset size includes the editor-side source wave; it is not the shipped size.")


main()
