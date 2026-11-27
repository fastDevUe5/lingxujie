"""Remove the scratch assets and patched files this investigation created.

Everything under /Game/Moxiang/Test and the patched glTF copies are artefacts of the verification, not
part of the project. The originals are untouched and the level is left exactly as it was found.

    py "Tools/cleanup_ibm_test.py"
"""

import os

import unreal

FOLDERS = ["/Game/Moxiang/Test"]
FILES = [
    "C:/Users/tk/Desktop/lingxujie/Assets/Moxiang/ue_import/boss001_ibmfix.gltf",
    "C:/Users/tk/Desktop/lingxujie/Assets/Moxiang/ue_import/boss001_ibmfix.bin",
    "C:/Users/tk/Desktop/lingxujie/Assets/Moxiang/ue_import/boss001_ibmfix2.gltf",
    "C:/Users/tk/Desktop/lingxujie/Assets/Moxiang/ue_import/boss001_ibmfix2.bin",
]

# The mangled path a bad string substitution produced; harmless but worth removing if it exists.
EXTRA = ["C:/Users/tk/Desktop/lingxujie/Assets/Moxiang/ue_import/boss001_IBMFIX222.gltf"]


def log(text):
    unreal.log("[LingXuJie] CLEAN: %s" % text)


def main():
    for folder in FOLDERS:
        if unreal.EditorAssetLibrary.does_directory_exist(folder):
            ok = unreal.EditorAssetLibrary.delete_directory(folder)
            log("deleted %s -> %s" % (folder, ok))
        else:
            log("%s not present" % folder)

    # Actors spawned for measurement.
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    removed = 0
    for actor in list(subsystem.get_all_level_actors()):
        label = actor.get_actor_label()
        if label.startswith("MEAS_") or label.startswith("MX_TEST_"):
            subsystem.destroy_actor(actor)
            removed += 1
    log("removed %d measurement actor(s)" % removed)

    for path in FILES + EXTRA:
        if os.path.exists(path):
            try:
                os.remove(path)
                log("removed %s" % os.path.basename(path))
            except OSError as error:
                log("could not remove %s: %r" % (os.path.basename(path), error))

    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
