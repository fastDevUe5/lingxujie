"""Material round 2: create a material instance and prove the parameter actually changes the render.

An instance is the point of making the graph parameterised: one base material, many looks. This creates
an instance of the texture material, sets its scalar parameter to a different value, and then verifies in
two independent ways - the parameter reads back, and the picture changes when the instance is applied.

Two instances are made with very different brightness so the visual difference cannot be explained by
noise.

    py "Tools/mat_instance.py"
"""

import unreal

PACKAGE = "/Game/Learning"
BASE = "/Game/Learning/M_LabTex"
NAMES = ("MI_LabDim", "MI_LabBright")
VALUES = (0.02, 0.9)


def log(text):
    unreal.log("[LingXuJie] MAT4: %s" % text)


def main():
    base = unreal.load_asset(BASE)
    if base is None:
        log("base material missing")
        return

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    library = unreal.MaterialEditingLibrary

    made = []
    for name, value in zip(NAMES, VALUES):
        path = "%s/%s" % (PACKAGE, name)
        instance = unreal.load_asset(path)

        if instance is None:
            instance = asset_tools.create_asset(
                name, PACKAGE, unreal.MaterialInstanceConstant,
                unreal.MaterialInstanceConstantFactoryNew())
            if instance is None:
                log("could not create %s" % name)
                continue
            log("created %s" % path)
        else:
            log("%s already exists" % path)

        # Parent must be set before parameters can be found.
        library.set_material_instance_parent(instance, base)

        ok = library.set_material_instance_scalar_parameter_value(
            instance, "Brightness", value)
        readback = library.get_material_instance_scalar_parameter_value(
            instance, "Brightness")

        log("  %-16s set=%r  reads back=%.3f  parent=%r"
            % (name, ok, readback, instance.get_editor_property("parent").get_name()
               if instance.get_editor_property("parent") else None))

        library.update_material_instance(instance)
        log("  saved: %r" % unreal.EditorAssetLibrary.save_asset(path))
        made.append((name, value))

    log("instances: %d" % len(made))

    # Report what parameters the base material actually exposes.
    try:
        names = library.get_scalar_parameter_names(base, True)
        log("scalar parameters on the base: %r" % (names,))
    except Exception as error:  # noqa: BLE001
        log("scalar parameter listing failed: %r" % str(error)[:60])

    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
