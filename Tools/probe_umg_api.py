"""Confirm whether the widget tree of a widget blueprint is reachable from Python at all.

The first attempt created the asset but could not read its widget_tree property. Before concluding
that UMG cannot be built from Python, this lists what the widget blueprint class actually exposes,
which distinguishes "the property has another name" from "the property is not reflected".

    py "Tools/probe_umg_api.py"
"""

import unreal


def log(text):
    unreal.log("[LingXuJie] UMGPROBE: %s" % text)


def main():
    asset = unreal.EditorAssetLibrary.load_asset("/Game/Moxiang/UI/WBP_Test.WBP_Test")
    if asset is None:
        log("widget blueprint missing")
        return

    log("class=%s" % asset.get_class().get_name())

    # Every property name the reflected object exposes.
    interesting = [name for name in dir(asset)
                   if not name.startswith("_")
                   and any(key in name.lower()
                           for key in ("widget", "tree", "root", "panel", "slot"))]
    log("properties matching widget/tree/root: %s" % (interesting or "none"))

    # Whether the class lists these at all, as distinct from the instance.
    cls = asset.get_class()
    class_props = [name for name in dir(cls) if "widget" in name.lower()]
    log("class-level widget names: %s" % (class_props[:10] or "none"))

    # Try the library that deals with widgets at runtime.
    for candidate in ("WidgetBlueprintLibrary", "UMGBlueprintLibrary"):
        if hasattr(unreal, candidate):
            log("library present: %s" % candidate)
        else:
            log("library absent: %s" % candidate)

    # Is the widget tree type itself exposed?
    for candidate in ("WidgetTree", "PanelWidget", "TextBlock", "CanvasPanel"):
        present = hasattr(unreal, candidate)
        log("type %-16s %s" % (candidate, "exposed" if present else "NOT exposed"))

    # And the editor subsystem that might own widget editing.
    for candidate in ("UMGEditorSubsystem", "WidgetBlueprintEditorSubsystem"):
        present = hasattr(unreal, candidate)
        log("subsystem %-28s %s" % (candidate, "exposed" if present else "NOT exposed"))


main()
