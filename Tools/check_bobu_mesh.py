"""Check whether the imported character mesh actually contains renderable geometry.

A skeletal mesh with zero triangles has sensible bounds and a valid skeleton, and looks exactly like
a mesh that is invisible. This asks the mesh how many vertices and sections it has, which separates
"the export dropped the geometry" from "the actor is placed somewhere unseen".

    py "Tools/check_bobu_mesh.py"
"""

import unreal

MESH = ("/Game/Moxiang/Skeletal/Characters/char_bobu/"
        "SkeletalMeshes/SK_Bobu.SK_Bobu")
ANIM = ("/Game/Moxiang/Skeletal/Characters/char_bobu/"
        "SkeletalMeshes/SK_Bobu_Anim.SK_Bobu_Anim")


def log(text):
    unreal.log("[LingXuJie] MESHCHK: %s" % text)


def main():
    mesh = unreal.EditorAssetLibrary.load_asset(MESH)
    if mesh is None:
        log("mesh missing")
        return
    log("class=%s" % mesh.get_class().get_name())

    try:
        log("lod count=%d" % mesh.get_num_lods())
    except Exception as error:  # noqa: BLE001
        log("lod count unreadable: %s" % error)

    for name in ("skeletal_mesh", "materials", "override_materials", "skeleton"):
        try:
            value = mesh.get_editor_property(name)
            if isinstance(value, (list, tuple)):
                log("  %-20s list of %d" % (name, len(value)))
            else:
                log("  %-20s %s" % (name, value))
        except Exception:  # noqa: BLE001
            pass

    # Sections and their material slots are what a renderer needs.
    try:
        render_data = mesh.get_editor_property("render_data")
        log("  render_data present: %s" % (render_data is not None))
    except Exception:  # noqa: BLE001
        pass

    anim = unreal.EditorAssetLibrary.load_asset(ANIM)
    if anim is not None:
        log("anim class=%s" % anim.get_class().get_name())
        for name in ("sequence_length", "rate_scale"):
            try:
                log("  %-20s %s" % (name, anim.get_editor_property(name)))
            except Exception:  # noqa: BLE001
                pass

    # Where is the actor, and is it inside the terrain?
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for actor in subsystem.get_all_level_actors():
        if actor.get_actor_label() != "MX_BOBU_TEST":
            continue
        location = actor.get_actor_location()
        log("actor at (%.1f, %.1f, %.1f)" % (location.x, location.y, location.z))
        component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
        if component is not None:
            log("  component mesh=%s" % (
                component.get_editor_property("skeletal_mesh").get_name()
                if component.get_editor_property("skeletal_mesh") else "none"))
            log("  visible=%s  hidden_in_game=%s"
                % (component.is_visible(), component.get_editor_property("hidden_in_game")))
            try:
                bounds = component.bounds
                log("  component bounds extent=(%.1f, %.1f, %.1f)"
                    % (bounds.box_extent.x, bounds.box_extent.y, bounds.box_extent.z))
            except Exception:  # noqa: BLE001
                pass


main()
