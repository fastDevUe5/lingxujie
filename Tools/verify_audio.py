"""Import one sound and play it, so the audio path is verified rather than described.

Audio is the domain where reading achieves least: the classes are simple, and the only question
that matters is whether a file on disk becomes a sound in the world. This imports a real wave file
from the extracted Korean audio set, places an AudioComponent, and plays it - three steps that
cover the whole path from asset to output.

    py "Tools/verify_audio.py"
"""

import os

import unreal

# A short effect from the Korean set, present in both builds.
SOURCE = "C:/Users/tk/Desktop/moxiang-study/audio_extra_kr/monster/M004_Attack_01.wav"
FALLBACK = "C:/Users/tk/Desktop/moxiang-study/installer_kr/Sound/monster/M004_Attack_01.wav"
DEST_DIR = "/Game/Moxiang/Audio"
ASSET_NAME = "S_M004_Attack_01"


def log(text):
    unreal.log("[LingXuJie] AUDIO: %s" % text)


def main():
    source = SOURCE if os.path.exists(SOURCE) else FALLBACK
    if not os.path.exists(source):
        log("no source wav found")
        return
    log("source %s (%d bytes)" % (os.path.basename(source), os.path.getsize(source)))

    asset_path = "%s/%s" % (DEST_DIR, ASSET_NAME)
    if unreal.EditorAssetLibrary.does_asset_exist(asset_path):
        log("already imported")
        sound = unreal.EditorAssetLibrary.load_asset(asset_path)
    else:
        task = unreal.AssetImportTask()
        task.filename = source
        task.destination_path = DEST_DIR
        task.destination_name = ASSET_NAME
        task.automated = True
        task.save = True
        task.replace_existing = True
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
        sound = unreal.EditorAssetLibrary.load_asset(asset_path)
        if sound is None:
            log("import produced nothing")
            return
        log("imported %s" % asset_path)

    # What the import produced, which is the part that says whether the format survived.
    duration = sound.get_editor_property("duration")
    log("class=%s duration=%.3f s" % (sound.get_class().get_name(), duration))

    # Play it at a location, through the world's audio device.
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    if world is None:
        log("no world")
        return

    location = unreal.Vector(8950.0, -6200.0, 3900.0)
    rotation = unreal.Rotator(0.0, 0.0, 0.0)
    # The reflected signature requires the rotation explicitly; there is no overload without it.
    unreal.GameplayStatics.play_sound_at_location(world, sound, location, rotation)
    log("played at %.0f, %.0f, %.0f" % (location.x, location.y, location.z))


main()
