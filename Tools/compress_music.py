"""Measure what the imported music actually costs, and whether compression settings help.

The previous round found that a one and a half megabyte mp3 became an eleven megabyte asset. That
is worth fixing before there are twelve of them, but fixing it blindly is worse than measuring it:
the compression quality has to be set on the sound wave, the asset re-saved, and the size read back
to know whether anything changed.

    py "Tools/compress_music.py"
"""

import os

import unreal

ASSET = "/Game/Moxiang/Audio/S_bg_field"
DISK = "C:/Users/tk/Desktop/lingxujie/Content/Moxiang/Audio/S_bg_field.uasset"


def log(text):
    unreal.log("[LingXuJie] COMPRESS: %s" % text)


def disk_size():
    return os.path.getsize(DISK) if os.path.exists(DISK) else 0


def report(label, sound):
    size = disk_size()
    log("%s: on disk %.2f MB" % (label, size / (1024.0 * 1024.0)))
    for name in ("compression_quality", "sound_group", "loading_behavior",
                 "virtualization_mode", "sound_class_object"):
        try:
            value = sound.get_editor_property(name)
            log("    %-24s %s" % (name, value))
        except Exception:  # noqa: BLE001
            log("    %-24s (not readable)" % name)
    return size


def main():
    sound = unreal.EditorAssetLibrary.load_asset(ASSET + ".S_bg_field")
    if sound is None:
        log("asset missing")
        return

    before = report("before", sound)

    # Compression quality is a property of the sound wave; lower means smaller and lossier.
    try:
        sound.set_editor_property("compression_quality", 40)
        log("set compression_quality to 40")
    except Exception as error:  # noqa: BLE001
        log("could not set compression quality: %s" % error)

    # Streaming avoids holding the whole track in memory, which matters more than size here.
    try:
        sound.set_editor_property("loading_behavior",
                                  unreal.SoundWaveLoadingBehavior.RETAIN_ON_LOAD)
        log("loading_behavior set")
    except Exception as error:  # noqa: BLE001
        log("could not set loading behavior: %s" % error)

    unreal.EditorAssetLibrary.save_loaded_asset(sound)

    # The saved file only shrinks after a re-cook of the compressed data, which happens on save
    # in the editor but is worth checking rather than assuming.
    after = report("after", sound)
    if after and before:
        log("change: %.2f MB -> %.2f MB (%.0f%%)"
            % (before / (1024.0 * 1024.0), after / (1024.0 * 1024.0),
               100.0 * after / before))


main()
