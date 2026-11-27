"""UI round 1: create a widget blueprint and populate its tree from Python.

The mirror listed no UMG classes, but the runtime has them: WidgetBlueprintFactory, WidgetTree,
CanvasPanel and TextBlock are all present, so a widget can be built without opening the designer.
This creates one, adds a canvas panel as the root and a text block inside it, then reads the tree back to
confirm the structure exists rather than assuming the calls did something.

    py "Tools/ui_build_widget.py"
"""

import unreal

PACKAGE = "/Game/Learning"
NAME = "WBP_LabLabel"


def log(text):
    unreal.log("[LingXuJie] UI2: %s" % text)


def main():
    asset_path = "%s/%s" % (PACKAGE, NAME)
    blueprint = unreal.load_asset(asset_path)

    if blueprint is None:
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        factory = unreal.WidgetBlueprintFactory()
        blueprint = asset_tools.create_asset(
            NAME, PACKAGE, unreal.WidgetBlueprint, factory)
        if blueprint is None:
            log("could not create the widget blueprint")
            return
        log("created %s" % asset_path)
    else:
        log("%s already exists" % asset_path)

    tree = blueprint.get_editor_property("widget_tree")
    log("widget tree: %r" % (tree is not None))
    if tree is None:
        return

    root = tree.get_editor_property("root_widget")
    log("existing root: %r" % (root.get_name() if root else None))

    if root is None:
        # A canvas panel as root gives absolute positioning for children.
        canvas = tree.construct_widget(unreal.CanvasPanel, "RootCanvas")
        log("constructed a CanvasPanel: %r" % (canvas is not None))
        if canvas is not None:
            tree.set_editor_property("root_widget", canvas)
            root = canvas

    if root is not None:
        text = tree.construct_widget(unreal.TextBlock, "LabelText")
        log("constructed a TextBlock: %r" % (text is not None))
        if text is not None:
            try:
                text.set_editor_property("text", unreal.Text("灵虚界 · 练习关卡"))
                log("text set")
            except Exception as error:  # noqa: BLE001
                log("text not settable: %r" % str(error)[:60])
            try:
                text.set_editor_property("font", unreal.SlateFontInfo())
            except Exception:  # noqa: BLE001
                pass

    # Read the tree back.
    log("--- tree after edits ---")
    root_now = tree.get_editor_property("root_widget")
    log("root: %r (%r)" % (root_now.get_name() if root_now else None,
                           type(root_now).__name__ if root_now else None))
    if root_now is not None:
        try:
            children = root_now.get_all_children()
            log("children of root: %d" % len(children))
            for child in children:
                log("  %s (%s)" % (child.get_name(), type(child).__name__))
        except Exception as error:  # noqa: BLE001
            log("could not list children: %r" % str(error)[:60])

    try:
        all_widgets = tree.get_all_widgets()
        log("all widgets in the tree: %d" % len(all_widgets))
    except Exception as error:  # noqa: BLE001
        log("get_all_widgets failed: %r" % str(error)[:60])

    log("saved: %r" % unreal.EditorAssetLibrary.save_asset(asset_path))
    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
