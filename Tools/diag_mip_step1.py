"""Case 007: is the texture that failed to import in November healthy now.

The warning sequence records a failed DDS import - partial mip chain, no mip levels, object not found,
translator error - from an attempt that was later abandoned in favour of converting DDS to PNG first.
The question worth answering is whether the asset in place now came out correctly, not what went
wrong six hours ago.

    py "Tools/diag_mip_step1.py"
"""

import unreal


def log(text):
    unreal.log("[LingXuJie] M1: %s" % text)


def probe(path):
    texture = unreal.load_asset(path)
    if texture is None:
        log("%s: could not load" % path)
        return None

    log("=== %s ===" % path)
    try:
        size_x = texture.get_editor_property("blueprint_get_size_x") if False else None
    except Exception:  # noqa: BLE001
        pass

    # The import-time settings decide whether mips are generated at all.
    try:
        data = texture.get_editor_property("asset_import_data")
        if data is not None:
            for field in ("generate_mips", "source_file", "source_file_extension"):
                try:
                    log("  %-24s %r" % (field, data.get_editor_property(field)))
                except Exception:  # noqa: BLE001
                    pass
        else:
            log("  no asset_import_data (texture was not imported from a file)")
    except Exception as error:  # noqa: BLE001
        log("  asset_import_data unreadable: %r" % error)

    # Streaming and residency hints that only make sense with mips.
    for field in ("never_stream", "lod_group", "num_cinematic_mip_levels",
                  "virtual_texture_streaming", "lod_bias"):
        try:
            log("  %-24s %r" % (field, texture.get_editor_property(field)))
        except Exception:  # noqa: BLE001
            pass

    # What the platform data says the resource actually is.
    try:
        platform_data = texture.get_editor_property("platform_data")
        log("  platform_data entries: %d" % len(platform_data or []))
        for index, entry in enumerate(platform_data or []):
            for field in ("size_x", "size_y", "num_mips", "pixel_format", "max_texture_size"):
                try:
                    log("    [%d] %-18s %r" % (index, field, entry.get_editor_property(field)))
                except Exception:  # noqa: BLE001
                    pass
    except Exception as error:  # noqa: BLE001
        log("  platform_data unreadable: %r" % error)

    # The runtime resource size tells you whether there is more than one level.
    try:
        resource_size = texture.get_resource_size()
        log("  resource size: %d bytes" % resource_size)
    except Exception:  # noqa: BLE001
        pass

    return texture


def main():
    for path in ("/Game/Moxiang/Textures/T_Boss_Mob01.T_Boss_Mob01",
                 "/Game/Moxiang/tile_108_road01.tile_108_road01"):
        probe(path)
    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
