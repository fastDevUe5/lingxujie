"""Build a minimal audio system: a sound class hierarchy and one attenuation.

Playing a clip is not a system. A system needs groups so volume can be controlled by category, and
an attenuation so distance matters. Both are assets with a small number of properties, and both are
creatable from Python through the asset tools.

The class tree is modelled on what the sets actually contain: music, effects, voice and monsters.

    py "Tools/build_audio_system.py"
"""

import unreal

DEST = "/Game/Moxiang/Audio"
CLASSES = [
    ("SC_Master", None),
    ("SC_Music", "SC_Master"),
    ("SC_SFX", "SC_Master"),
    ("SC_Voice", "SC_Master"),
    ("SC_Monster", "SC_SFX"),
]


def log(text):
    unreal.log("[LingXuJie] AUDIOSYS: %s" % text)


def load_class(name):
    return unreal.EditorAssetLibrary.load_asset("%s/%s.%s" % (DEST, name, name))


def make_sound_class(name, parent_name):
    path = "%s/%s" % (DEST, name)
    existing = unreal.EditorAssetLibrary.load_asset("%s.%s" % (path, name))
    if existing is not None:
        return existing

    tools = unreal.AssetToolsHelpers.get_asset_tools()
    sound_class = tools.create_asset(name, DEST, unreal.SoundClass, unreal.SoundClassFactory())
    if sound_class is None:
        log("could not create %s" % name)
        return None

    if parent_name:
        parent = load_class(parent_name)
        if parent is not None:
            try:
                sound_class.set_editor_property("parent_class", parent)
            except Exception as error:  # noqa: BLE001
                log("parent for %s failed: %s" % (name, error))
    return sound_class


def make_attenuation():
    name = "SA_Monster"
    path = "%s/%s.%s" % (DEST, name, name)
    existing = unreal.EditorAssetLibrary.load_asset(path)
    if existing is not None:
        return existing

    tools = unreal.AssetToolsHelpers.get_asset_tools()
    attenuation = tools.create_asset(
        name, DEST, unreal.SoundAttenuation, unreal.SoundAttenuationFactory())
    if attenuation is None:
        log("could not create the attenuation")
        return None

    # Distance in centimetres: audible from 5 m, gone by 60 m. The curve decides how fast it falls.
    try:
        settings = attenuation.get_editor_property("attenuation")
        settings.set_editor_property("attenuate", True)
        settings.set_editor_property("attenuation_shape_extents", unreal.Vector(400.0, 400.0, 400.0))
        attenuation.set_editor_property("attenuation", settings)
    except Exception as error:  # noqa: BLE001
        log("attenuation settings: %s" % error)
    return attenuation


def main():
    created = []
    for name, parent in CLASSES:
        sound_class = make_sound_class(name, parent)
        if sound_class is not None:
            created.append(name)
            unreal.EditorAssetLibrary.save_loaded_asset(sound_class)
    log("sound classes: %s" % ", ".join(created) if created else "none created")

    attenuation = make_attenuation()
    if attenuation is not None:
        unreal.EditorAssetLibrary.save_loaded_asset(attenuation)
        log("attenuation saved: %s" % attenuation.get_name())

    # Verify by reading back what now exists.
    for name in [c[0] for c in CLASSES] + ["SA_Monster"]:
        asset = unreal.EditorAssetLibrary.load_asset("%s/%s.%s" % (DEST, name, name))
        log("verify %-14s -> %s" % (name, asset.get_class().get_name() if asset else "missing"))


main()
