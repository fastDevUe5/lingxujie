"""Import a background track and place it in the city, so the level has sound.

The audio work so far proved a single effect can be imported and played. That is not the same as a
level that has music. This imports the field track, assigns the music sound class built earlier so
volume can be controlled by category, and places an ambient sound actor in the plaza.

An ambient actor rather than a one-shot call, because music has to loop, follow the player, and be
stopped - which is what a component does and a fire-and-forget call does not.

    py "Tools/add_level_music.py"
"""

import os

import unreal

SOURCE_DIR = "C:/Users/tk/Desktop/moxiang-study/installer_kr/Sound/bgm"
SOURCES = ["bg_field.mp3", "BG_Town1.mp3"]
DEST_DIR = "/Game/Moxiang/Audio"
MUSIC_CLASS = "/Game/Moxiang/Audio/SC_Music.SC_Music"
AMBIENT_LABEL = "MX_AMBIENT_MUSIC"
# The plaza, slightly above the ground so the sound is audible from the start point.
LOCATION = unreal.Vector(8950.0, -6200.0, 3800.0)


def log(text):
    unreal.log("[LingXuJie] MUSIC: %s" % text)


def import_track(filename):
    source = os.path.join(SOURCE_DIR, filename)
    if not os.path.exists(source):
        log("missing source %s" % filename)
        return None
    asset_name = "S_%s" % os.path.splitext(filename)[0]
    asset_path = "%s/%s" % (DEST_DIR, asset_name)

    existing = unreal.EditorAssetLibrary.load_asset("%s.%s" % (asset_path, asset_name))
    if existing is not None:
        log("already imported %s" % asset_name)
        return existing

    task = unreal.AssetImportTask()
    task.filename = source
    task.destination_path = DEST_DIR
    task.destination_name = asset_name
    task.automated = True
    task.save = True
    task.replace_existing = True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

    asset = unreal.EditorAssetLibrary.load_asset("%s.%s" % (asset_path, asset_name))
    if asset is None:
        log("import produced nothing for %s" % filename)
        return None
    log("imported %s as %s (%.1f s)"
        % (filename, asset.get_class().get_name(),
           asset.get_editor_property("duration")))
    return asset


def set_sound_class(sound, class_path):
    sound_class = unreal.EditorAssetLibrary.load_asset(class_path)
    if sound_class is None:
        log("music sound class missing")
        return
    try:
        sound.set_editor_property("sound_class_object", sound_class)
        unreal.EditorAssetLibrary.save_loaded_asset(sound)
        log("sound class set to %s" % sound_class.get_name())
    except Exception as error:  # noqa: BLE001
        log("could not set the sound class: %s" % error)


def main():
    track = None
    for filename in SOURCES:
        track = import_track(filename)
        if track is not None:
            break
    if track is None:
        log("no track imported")
        return

    set_sound_class(track, MUSIC_CLASS)

    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for actor in subsystem.get_all_level_actors():
        if actor.get_actor_label() == AMBIENT_LABEL:
            log("ambient actor already present")
            return

    actor = subsystem.spawn_actor_from_class(
        unreal.AmbientSound, LOCATION, unreal.Rotator(0.0, 0.0, 0.0))
    if actor is None:
        log("spawn returned nothing")
        return

    actor.set_actor_label(AMBIENT_LABEL)
    component = actor.get_component_by_class(unreal.AudioComponent)
    if component is None:
        log("no audio component on the ambient actor")
        return

    component.set_editor_property("sound", track)
    component.set_editor_property("auto_activate", True)
    component.set_editor_property("volume_multiplier", 0.6)
    log("ambient actor placed with %s" % track.get_name())

    level_editor = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    level_editor.save_current_level()
    log("level saved")

    # Verify by reading the component back.
    log("verify: sound=%s auto_activate=%s volume=%.2f"
        % (component.get_editor_property("sound").get_name(),
           component.get_editor_property("auto_activate"),
           component.get_editor_property("volume_multiplier")))


main()
