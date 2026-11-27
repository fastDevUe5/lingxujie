"""One health sweep across every domain the debugging series covered.

Eleven rounds produced twenty-odd one-off scripts. Each answered one question once. This is the part
worth keeping: a single pass that reports the state of the things that went wrong before, so a
regression shows up as a changed line rather than as a bug noticed weeks later.

It reports, and does not repair. A sweep that fixes things is a sweep nobody trusts.

    py "Tools/diagnose.py"
    py "Tools/diagnose.py --skeletal"     # include the per-mesh skeletal checks
"""

import math
import sys

import unreal


def log(text):
    unreal.log("[LingXuJie] DIAG: %s" % text)


def registry():
    return unreal.AssetRegistryHelpers.get_asset_registry()


def check_assets():
    log("=== assets ===")
    reg = registry()
    for path in ("/Game", "/Game/Moxiang"):
        try:
            assets = reg.get_assets_by_path(path, True, False)
            log("  %-20s %4d asset(s)" % (path, len(assets)))
        except Exception as error:  # noqa: BLE001
            log("  %-20s error: %r" % (path, error))

    # Count the classes that matter for this project.
    counts = {}
    try:
        for asset in reg.get_assets_by_path("/Game/Moxiang", True, False):
            try:
                kind = str(asset.asset_class_path.asset_name)
            except Exception:  # noqa: BLE001
                continue
            counts[kind] = counts.get(kind, 0) + 1
    except Exception as error:  # noqa: BLE001
        log("  class census error: %r" % error)

    for kind in sorted(counts, key=lambda k: -counts[k])[:10]:
        log("    %-28s %4d" % (kind, counts[kind]))


def check_level(mesh_checks):
    log("=== level ===")
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    log("  actors: %d" % len(actors))

    missing = 0
    checked = 0
    zero_span = []
    for actor in actors:
        label = actor.get_actor_label()

        # Static mesh references
        static_component = actor.get_component_by_class(unreal.StaticMeshComponent)
        if static_component is not None:
            mesh = static_component.get_editor_property("static_mesh")
            if mesh is not None:
                checked += 1
                if not unreal.EditorAssetLibrary.does_asset_exist(mesh.get_path_name()):
                    missing += 1
                    log("    MISSING static mesh on %s: %s" % (label, mesh.get_path_name()))

        if not mesh_checks:
            continue

        skeletal_component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
        if skeletal_component is None:
            continue
        mesh = skeletal_component.get_editor_property("skeletal_mesh_asset")
        if mesh is None:
            continue
        checked += 1

        # Case 003: a skeleton whose bones all sit at one point cannot skin anything.
        span = 0.0
        try:
            positions = []
            for index in range(skeletal_component.get_num_bones()):
                name = str(skeletal_component.get_bone_name(index))
                try:
                    positions.append(skeletal_component.get_bone_transform(name).translation)
                except Exception:  # noqa: BLE001
                    continue
            if positions:
                span = max(
                    max(p.x for p in positions) - min(p.x for p in positions),
                    max(p.y for p in positions) - min(p.y for p in positions),
                    max(p.z for p in positions) - min(p.z for p in positions),
                )
        except Exception as error:  # noqa: BLE001
            log("    %s: bone read failed: %r" % (label, error))
            continue

        if span < 1.0:
            zero_span.append(label)
            log("    COLLAPSED skeleton on %s: span %.2f cm" % (label, span))
        elif span > 2000.0:
            log("    OVERSIZED skeleton on %s: span %.0f cm" % (label, span))
        else:
            log("    %-22s bones span %.0f cm" % (label, span))

        # Case 001: an animation that exists but is not wired to anything.
        data = skeletal_component.get_editor_property("animation_data")
        if data is not None:
            anim = data.get_editor_property("anim_to_play")
            mode = skeletal_component.get_editor_property("animation_mode")
            if anim is None:
                log("    %-22s no animation assigned (mode=%r)" % (label, str(mode).split(".")[-1]))

    log("  mesh references checked: %d, missing: %d" % (checked, missing))
    if zero_span:
        log("  collapsed skeletons: %d" % len(zero_span))


def check_memory():
    log("=== memory ===")
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    unreal.SystemLibrary.execute_console_command(world, "obj cycles")


def check_config():
    log("=== config worth watching ===")
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    for cvar in ("t.TargetFrameTimeThreshold", "r.DynamicGlobalIlluminationMethod",
                 "r.AntiAliasingMethod", "r.Shadow.Virtual.Enable", "stat unit"):
        unreal.SystemLibrary.execute_console_command(world, cvar)


def main():
    args = sys.argv
    # Skeletal checks cost a few seconds but catch the two defects found in cases 001 and 003, so they
    # run by default. Pass --noskeletal to skip them on a large level.
    mesh_checks = "--noskeletal" not in args

    log("--- sweep start (skeletal=%s) ---" % mesh_checks)
    check_assets()
    check_level(mesh_checks)
    check_memory()
    check_config()
    log("--- sweep done ---")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())

