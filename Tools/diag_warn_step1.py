"""Case 004: two warnings the log produced that nobody examined.

"Texture2D ... contains no miplevels" means the texture will alias badly at distance, because there is
only one resolution to sample. "Material ... missing the Used with Nanite flag" means a material the
Nanite meshes reference may fail outside the editor.

Both are measurable through the asset objects themselves, so this reports the actual state rather
than restating the warning.

    py "Tools/diag_warn_step1.py"
"""

import unreal


def log(text):
    unreal.log("[LingXuJie] W1: %s" % text)


def main():
    reg = unreal.AssetRegistryHelpers.get_asset_registry()

    log("=== textures and their mip settings ===")
    textures = []
    for asset in reg.get_assets_by_path("/Game/Moxiang", True, False):
        if str(asset.asset_class_path.asset_name) == "Texture2D":
            textures.append("%s.%s" % (asset.package_name, asset.asset_name))

    log("found %d Texture2D asset(s)" % len(textures))

    no_mip = []
    for path in textures[:200]:
        texture = unreal.load_asset(path)
        if texture is None:
            continue
        try:
            mip_gen = texture.get_editor_property("mip_gen_settings")
            never_stream = mip_gen.get_editor_property("never_stream")
            num_mips = texture.get_editor_property("mip_gen_settings")
            # The reliable signal in the asset: the derived data mip count.
            platform_data = texture.get_editor_property("platform_data")
            num_mips_value = None
            if platform_data:
                num_mips_value = platform_data[0].get_editor_property("mip_gen_settings")
            log("  %-52s never_stream=%s" % (path.rsplit("/", 1)[-1][:52], never_stream))
        except Exception as error:  # noqa: BLE001
            log("  %-52s read failed: %r" % (path.rsplit("/", 1)[-1][:52], error))
            continue

        # import settings carry the "generate mips" switch that decides whether there is one level.
        try:
            build_settings = texture.get_editor_property("asset_import_data")
            if build_settings is not None:
                mips = build_settings.get_editor_property("generate_mips")
                if not mips:
                    no_mip.append(path)
                    log("  %-52s generate_mips = False  <-- no mip levels" % path.rsplit("/", 1)[-1][:52])
        except Exception:  # noqa: BLE001
            pass

    log("textures with mips disabled: %d" % len(no_mip))

    log("=== materials and the Nanite flag ===")
    materials = []
    for asset in reg.get_assets_by_path("/Game/Moxiang", True, False):
        if str(asset.asset_class_path.asset_name) in ("Material", "MaterialInstanceConstant"):
            materials.append("%s.%s" % (asset.package_name, asset.asset_name))
    log("found %d material asset(s)" % len(materials))

    for path in materials[:40]:
        material = unreal.load_asset(path)
        if material is None:
            continue
        try:
            used_with_nanite = material.get_editor_property("used_with_nanite")
            if not used_with_nanite:
                log("  %-52s used_with_nanite = False" % path.rsplit("/", 1)[-1][:52])
        except Exception:  # noqa: BLE001
            pass

    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
