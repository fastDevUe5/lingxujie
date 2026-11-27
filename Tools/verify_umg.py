"""Create a widget blueprint and add a text block, to establish whether UMG is reachable from Python.

No toolset covers user interface. Widget blueprints are a blueprint subclass, so the blueprint
factory path may work, but the widget tree inside is edited through a different API - and whether
that API is reflected is the question this answers.

It is worth answering directly rather than working around: the project needs a UI that the current
Canvas HUD cannot produce, so knowing whether Python can build one decides the approach.

    py "Tools/verify_umg.py"
"""

import unreal


def log(text):
    unreal.log("[LingXuJie] UMG: %s" % text)


def main():
    dest = "/Game/Moxiang/UI"
    name = "WBP_Test"

    if unreal.EditorAssetLibrary.does_asset_exist("%s/%s" % (dest, name)):
        asset = unreal.EditorAssetLibrary.load_asset("%s/%s.%s" % (dest, name, name))
        log("already exists, class=%s" % (asset.get_class().get_name() if asset else "?"))
    else:
        factory = unreal.WidgetBlueprintFactory()
        tools = unreal.AssetToolsHelpers.get_asset_tools()
        asset = tools.create_asset(name, dest, None, factory)
        if asset is None:
            log("create_asset returned nothing")
            return
        log("created, class=%s" % asset.get_class().get_name())
        unreal.EditorAssetLibrary.save_loaded_asset(asset)

    # The widget tree is the part that matters: can Python add a widget to it?
    widget_tree = None
    for attribute in ("widget_tree", "WidgetTree"):
        try:
            widget_tree = asset.get_editor_property(attribute)
            if widget_tree is not None:
                log("widget_tree read via %s" % attribute)
                break
        except Exception:  # noqa: BLE001
            continue

    if widget_tree is None:
        log("no widget_tree property reachable")
        return

    log("widget_tree class=%s" % widget_tree.get_class().get_name())
    root = widget_tree.get_editor_property("root_widget")
    log("existing root=%s" % (root.get_name() if root else "none"))

    # Try to construct a text block and attach it.
    try:
        text_block = unreal.new_object(unreal.TextBlock, widget_tree)
        log("made a TextBlock: %s" % text_block.get_name())
        text_block.set_editor_property("text", unreal.Text("灵虚界"))
    except Exception as error:  # noqa: BLE001
        log("could not make a TextBlock: %s" % error)
        return

    try:
        widget_tree.set_editor_property("root_widget", text_block)
        log("root assigned")
    except Exception as error:  # noqa: BLE001
        log("could not set root: %s" % error)
        return

    unreal.EditorAssetLibrary.save_loaded_asset(asset)
    log("saved with a text block")


main()
