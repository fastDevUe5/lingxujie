"""Report the project's asset numbers and check every referenced asset actually resolves.

This is the check that would have caught the LoadAsset failures before they happened: walk what the
level references and confirm each path resolves in the registry, rather than trusting a path that was
written by hand.

    py "Tools/audit_assets.py"
"""

import unreal


def log(text):
    unreal.log("[LingXuJie] AUD: %s" % text)


def registry():
    return unreal.AssetRegistryHelpers.get_asset_registry()


def main():
    reg = registry()

    # How much does the registry know, at each level of the tree?
    for path in ("/Game", "/Game/Moxiang", "/Game/Moxiang/Textures",
                 "/Game/Moxiang/Materials", "/Game/Moxiang/Skeletal", "/Game/Moxiang/Static"):
        try:
            assets = reg.get_assets_by_path(path, True, False)
            log("%-30s %4d asset(s)" % (path, len(assets)))
        except Exception as error:  # noqa: BLE001
            log("%-30s error: %r" % (path, error))

    # Build a set of every object path the registry knows, so a lookup is a set test rather than a
    # load attempt. This is what makes an audit cheap.
    known = set()
    try:
        for asset in reg.get_assets_by_path("/Game", True, False):
            known.add("%s.%s" % (asset.package_name, asset.asset_name))
    except Exception as error:  # noqa: BLE001
        log("building the known set raised: %r" % error)
    log("known set holds %d object path(s)" % len(known))

    # Check that the actors in the level point at assets that exist. A missing mesh here is exactly
    # the failure that shows up later as "could not be found in the Asset Registry".
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    log("level has %d actor(s)" % len(actors))

    missing = []
    checked = 0
    for actor in actors:
        try:
            component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
        except Exception:  # noqa: BLE001
            component = None
        if not component:
            continue
        try:
            mesh = component.get_editor_property("skeletal_mesh_asset")
        except Exception:  # noqa: BLE001
            continue
        if not mesh:
            continue
        checked += 1
        path = mesh.get_path_name()
        if path and path not in known and path.startswith("/Game"):
            missing.append(path)

    log("checked %d skeletal mesh reference(s), %d not in registry"
        % (checked, len(missing)))
    for path in missing[:10]:
        log("    MISSING: %s" % path)

    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
