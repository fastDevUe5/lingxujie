"""Build the recovered 墨香 map inside the engine.

The geometry was exported from the client in world centimetres with the axes already swapped into the engine's
convention, so importing it is a matter of loading the OBJ files as static meshes and placing them at the origin. No
scaling is applied: the client's map is a fifty-one thousand centimetre square and the meshes were exported at the
positions they occupy in it.

Two meshes are imported - the height field as the land, and the merged static meshes as the architecture - and then the
map's own light list is replayed as point lights, subsampled because a thousand of them in one place is more than the
renderer needs to convey the layout.

Everything here runs inside the editor through the Python plugin, called from build_level.py.
"""

import os

import unreal

ROOT = "C:/Users/tk/Desktop/lingxujie"
STUDY = "C:/Users/tk/Desktop/moxiang-study"
# The map OBJs are engine import sources, so they live with the engine assets rather than in the
# research workspace. Tools/build_map_obj.py writes them here.
IMPORT_DIR = os.path.join(ROOT, "Assets", "Moxiang", "ue_import")
ASSET_DIR = "/Game/Moxiang"

log = unreal.log


def import_obj(path, name):
    """Import an OBJ as a static mesh and return the asset, or None.

    An existing asset is deleted first. Asking the importer to replace it is not enough: it sees the
    asset already present and skips the work, so a changed OBJ silently keeps the old geometry and
    the triangle count never moves.
    """
    if not os.path.exists(path):
        log("[LingXuJie] missing %s" % path)
        return None

    asset_path = "%s/%s" % (ASSET_DIR, name)
    if unreal.EditorAssetLibrary.does_asset_exist(asset_path):
        unreal.EditorAssetLibrary.delete_asset(asset_path)
        log("[LingXuJie] removed the previous %s" % name)

    task = unreal.AssetImportTask()
    task.set_editor_property("filename", path)
    task.set_editor_property("destination_path", ASSET_DIR)
    task.set_editor_property("destination_name", name)
    task.set_editor_property("automated", True)
    task.set_editor_property("replace_existing", True)
    task.set_editor_property("save", True)
    try:
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    except Exception as exc:  # noqa: BLE001
        log("[LingXuJie] import failed for %s: %s" % (name, exc))
        return None

    if not unreal.EditorAssetLibrary.does_asset_exist(asset_path):
        log("[LingXuJie] import produced nothing for %s" % name)
        return None
    return unreal.EditorAssetLibrary.load_asset(asset_path)


def make_surface_material(name, colour, roughness=0.85):
    """A plain surface material, created if it is not already there."""
    path = "%s/%s" % (ASSET_DIR, name)
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        return unreal.EditorAssetLibrary.load_asset(path)

    tools = unreal.AssetToolsHelpers.get_asset_tools()
    material = tools.create_asset(name, ASSET_DIR, unreal.Material,
                                  unreal.MaterialFactoryNew())
    if material is None:
        return None
    base = unreal.MaterialEditingLibrary.create_material_expression(
        material, unreal.MaterialExpressionConstant3Vector, -400, 0)
    base.set_editor_property("constant", colour)
    unreal.MaterialEditingLibrary.connect_material_property(
        base, "", unreal.MaterialProperty.MP_BASE_COLOR)
    rough = unreal.MaterialEditingLibrary.create_material_expression(
        material, unreal.MaterialExpressionConstant, -400, 200)
    rough.set_editor_property("r", roughness)
    unreal.MaterialEditingLibrary.connect_material_property(
        rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    unreal.MaterialEditingLibrary.recompile_material(material)
    unreal.EditorAssetLibrary.save_loaded_asset(material)
    return material


def place(mesh, material, label, quiet=False):
    """Spawn one static mesh actor at the world origin, with collision.

    The imported OBJ carries no collision setup of its own, so without this the character falls
    straight through the land and the camera ends up under it looking at the sky.
    """
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actor = subsystem.spawn_actor_from_class(
        unreal.StaticMeshActor, unreal.Vector(0.0, 0.0, 0.0))
    if actor is None:
        log("[LingXuJie] could not spawn %s" % label)
        return None
    actor.set_actor_label(label)
    component = actor.static_mesh_component
    component.set_static_mesh(mesh)
    if material is not None:
        component.set_material(0, material)
    # Make the surface solid to the character. The mesh arrives Nanite-enabled, and a Nanite mesh
    # serves no complex collision, so the character falls straight through it. Turning the setting
    # off on the asset is not enough - the mesh has to be rebuilt for the change to take, which is
    # what the editor subsystem call does.
    try:
        subsystem_mesh = unreal.get_editor_subsystem(
            unreal.StaticMeshEditorSubsystem)
        if subsystem_mesh is not None:
            settings = subsystem_mesh.get_nanite_settings(mesh)
            if not quiet:
                log("[LingXuJie] nanite enabled before: %s"
                    % settings.get_editor_property("enabled"))
            settings.set_editor_property("enabled", False)
            subsystem_mesh.set_nanite_settings(mesh, settings)
            if not quiet:
                settings = subsystem_mesh.get_nanite_settings(mesh)
                log("[LingXuJie] nanite enabled after: %s"
                    % settings.get_editor_property("enabled"))
            # Turn collision on for the section as well; a section can carry geometry that no
            # body setup ever sees.
            try:
                subsystem_mesh.enable_section_collision(mesh, 0, 0, True)
                if not quiet:
                    log("[LingXuJie] section collision enabled for %s" % label)
            except Exception as exc:  # noqa: BLE001
                log("[LingXuJie] section collision failed: %s" % exc)
    except Exception as exc:  # noqa: BLE001
        log("[LingXuJie] nanite disable failed for %s: %s" % (label, exc))
    try:
        body = mesh.get_editor_property("body_setup")
        if body is not None:
            body.set_editor_property(
                "collision_trace_flag",
                unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
            if not quiet:
                log("[LingXuJie] complex-as-simple set on %s" % label)
    except Exception as exc:  # noqa: BLE001
        log("[LingXuJie] body setup failed for %s: %s" % (label, exc))
    try:
        component.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
        component.set_collision_profile_name("BlockAll")
    except Exception as exc:  # noqa: BLE001
        log("[LingXuJie] collision setup failed for %s: %s" % (label, exc))
    # A single mesh this large would otherwise be culled as one unit.
    try:
        component.set_editor_property("cast_shadow", True)
    except Exception:  # noqa: BLE001
        pass
    return actor


def light_specs(limit=60):
    """Read the map's light list and return every nth one, as (x, y, z, colour)."""
    path = os.path.join(STUDY, "tables", "extra_lights.csv")
    if not os.path.exists(path):
        return []
    import csv

    rows = []
    with open(path, encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            if not row.get("file", "").startswith("22."):
                continue
            rows.append(row)

    specs = []
    step = max(1, len(rows) // limit)
    for row in rows[::step]:
        try:
            colour = int(row["field1"], 16)
            position = [float(value) for value in row["field2"].split()]
            if len(position) != 3:
                continue
            specs.append((position[0], position[1], position[2], colour))
        except (KeyError, ValueError):
            continue
    return specs


def build_lights(compensation=1.0):
    """Replay the map's lights as point lights."""
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    specs = light_specs()
    spawned = 0
    for x, y, z, colour in specs:
        # The importer negates Y when it reads the OBJ, so the mesh sits at negative Y; the lights
        # have to be placed in the same space or they light an empty patch of sky.
        actor = subsystem.spawn_actor_from_class(
            unreal.PointLight, unreal.Vector(x, -z, y) * compensation)
        if actor is None:
            continue
        actor.set_actor_label("MX_LIGHT_%04d" % spawned)
        light = actor.point_light_component
        red = ((colour >> 16) & 0xFF) / 255.0
        green = ((colour >> 8) & 0xFF) / 255.0
        blue = (colour & 0xFF) / 255.0
        light.set_editor_property("light_color",
                                  unreal.Color(r=int(red * 255),
                                               g=int(green * 255),
                                               b=int(blue * 255), a=255))
        light.set_editor_property("intensity", 900.0)
        light.set_editor_property("attenuation_radius", 1800.0)
        spawned += 1
    log("[LingXuJie] lights: %d of the map's own list" % spawned)
    return spawned


def spawn_player_start():
    """Put the player on the ground at the middle of the map.

    The height there is read from the same grid the terrain mesh was built from, so the camera
    starts just above the surface rather than inside it or under it.
    """
    x, y = 25600.0, -25600.0
    height = 4748.0
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actor = subsystem.spawn_actor_from_class(
        unreal.PlayerStart, unreal.Vector(x, y, height + 180.0))
    if actor is not None:
        actor.set_actor_label("MX_PLAYERSTART")
        log("[LingXuJie] player start at %.0f, %.0f, %.0f"
            % (x, y, height + 180.0))
    return actor


TILE_SOURCE = os.path.join(ROOT, "Assets", "Moxiang")
# The city's textures, converted from the client's DDS by Tools/build_map_obj.py.
BUILDING_DIR = os.path.join(TILE_SOURCE, "textures")


def import_texture(name, path):
    """Import one of the client's textures as a texture asset.

    The client ships most of them as DDS with a header the engine's translator refuses, so they are
    converted to PNG by Tools/build_map_obj.py on the way in; the map's own tiles are a few hundred
    pixels square, which is all the detail the original art has.
    """
    if not os.path.exists(path):
        log("[LingXuJie] missing texture %s" % path)
        return None
    asset_path = "%s/%s" % (ASSET_DIR, name)
    if unreal.EditorAssetLibrary.does_asset_exist(asset_path):
        unreal.EditorAssetLibrary.delete_asset(asset_path)

    task = unreal.AssetImportTask()
    task.set_editor_property("filename", path)
    task.set_editor_property("destination_path", ASSET_DIR)
    task.set_editor_property("destination_name", name)
    task.set_editor_property("automated", True)
    task.set_editor_property("save", True)
    try:
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    except Exception as exc:  # noqa: BLE001
        log("[LingXuJie] texture import failed for %s: %s" % (name, exc))
        return None
    if not unreal.EditorAssetLibrary.does_asset_exist(asset_path):
        log("[LingXuJie] texture import produced nothing for %s" % name)
        return None
    return unreal.EditorAssetLibrary.load_asset(asset_path)


def make_building_master(name, masked=False):
    """The single shader family the city needs: a base colour texture and nothing else.

    Every building texture the client uses is a diffuse map, so one material with a texture
    parameter covers all of them and each of the ninety-six textures becomes a material instance
    instead of its own separately compiled shader.

    Many of the pieces are single-sided walls and roof undersides, so the master is two-sided; the
    masked variant is for the handful of textures that carry cut-out alpha (tree cards, flags).
    """
    path = "%s/%s" % (ASSET_DIR, name)
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        unreal.EditorAssetLibrary.delete_asset(path)

    tools = unreal.AssetToolsHelpers.get_asset_tools()
    material = tools.create_asset(name, ASSET_DIR, unreal.Material,
                                  unreal.MaterialFactoryNew())
    if material is None:
        log("[LingXuJie] could not create %s" % name)
        return None

    library = unreal.MaterialEditingLibrary
    sample = library.create_material_expression(
        material, unreal.MaterialExpressionTextureSampleParameter2D, -520, 0)
    sample.set_editor_property("parameter_name", "BaseTex")
    library.connect_material_property(
        sample, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)

    roughness = library.create_material_expression(
        material, unreal.MaterialExpressionConstant, -520, 240)
    roughness.set_editor_property("r", 0.8)
    library.connect_material_property(
        roughness, "", unreal.MaterialProperty.MP_ROUGHNESS)

    material.set_editor_property("two_sided", True)
    if masked:
        library.connect_material_property(
            sample, "A", unreal.MaterialProperty.MP_OPACITY_MASK)
        material.set_editor_property("blend_mode", unreal.BlendMode.BLEND_MASKED)

    library.recompile_material(material)
    unreal.EditorAssetLibrary.save_loaded_asset(material)
    log("[LingXuJie] building master %s (masked=%s)" % (name, masked))
    return material


def make_texture_instance(name, master, texture):
    """A material instance that points the master at one texture."""
    path = "%s/%s" % (ASSET_DIR, name)
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        unreal.EditorAssetLibrary.delete_asset(path)
    if master is None:
        return None

    tools = unreal.AssetToolsHelpers.get_asset_tools()
    instance = tools.create_asset(name, ASSET_DIR, unreal.MaterialInstanceConstant,
                                  unreal.MaterialInstanceConstantFactoryNew())
    if instance is None:
        log("[LingXuJie] could not create instance %s" % name)
        return None
    library = unreal.MaterialEditingLibrary
    library.set_material_instance_parent(instance, master)
    library.set_material_instance_texture_parameter_value(
        instance, "BaseTex", texture)
    unreal.EditorAssetLibrary.save_loaded_asset(instance)
    return instance


def load_city_manifest(path):
    """The list of texture groups Tools/build_map_obj.py wrote for the city."""
    if not os.path.exists(path):
        log("[LingXuJie] MX: no build manifest at %s" % path)
        return []
    import json
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle).get("groups", [])
    except Exception as exc:  # noqa: BLE001
        log("[LingXuJie] MX: manifest unreadable: %s" % exc)
        return []


def make_ground_material(texture, tiles=96.0):
    """A ground material that repeats the client's tile across the whole map.

    The mesh carries a 0..1 texture coordinate across the full fifty-one thousand centimetres, so
    the repeat count is what sets the physical size of one tile: ninety-six repeats over that span
    is a little over five metres a tile, which is the scale the original art was drawn at.
    """
    name = "M_Moxiang_Ground"
    path = "%s/%s" % (ASSET_DIR, name)
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        unreal.EditorAssetLibrary.delete_asset(path)

    tools = unreal.AssetToolsHelpers.get_asset_tools()
    material = tools.create_asset(name, ASSET_DIR, unreal.Material,
                                  unreal.MaterialFactoryNew())
    if material is None:
        return None

    library = unreal.MaterialEditingLibrary
    coords = library.create_material_expression(
        material, unreal.MaterialExpressionTextureCoordinate, -700, 0)
    coords.set_editor_property("u_tiling", tiles)
    coords.set_editor_property("v_tiling", tiles)
    sample = library.create_material_expression(
        material, unreal.MaterialExpressionTextureSample, -450, 0)
    sample.set_editor_property("texture", texture)
    library.connect_material_expressions(coords, "", sample, "UVs")
    library.connect_material_property(
        sample, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)

    roughness = library.create_material_expression(
        material, unreal.MaterialExpressionConstant, -450, 220)
    roughness.set_editor_property("r", 0.95)
    library.connect_material_property(
        roughness, "", unreal.MaterialProperty.MP_ROUGHNESS)

    library.recompile_material(material)
    unreal.EditorAssetLibrary.save_loaded_asset(material)
    log("[LingXuJie] ground material built from %s, %.0f repeats"
        % (texture.get_name(), tiles))
    return material


def build():
    """Rebuild the Lanzhou map: the real terrain and the city's own architecture.

    Map 17 is Lanzhou, confirmed from the client's MapKindInfo table, which lists every map by
    number and name. It carries fifteen hundred mesh objects - the whole city, not a sample - and
    the client kept one texture per face group, so the city arrives as one mesh per texture. The
    height field becomes the land, each texture group becomes a mesh with its own material, and
    both are already in world centimetres.
    """
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

    cleared = 0
    for actor in list(subsystem.get_all_level_actors()):
        label = actor.get_actor_label()
        if isinstance(actor, unreal.PlayerStart) or label.startswith("MX_"):
            subsystem.destroy_actor(actor)
            cleared += 1
    log("[LingXuJie] MX: cleared %d old spawn and map actors" % cleared)

    terrain = import_obj(os.path.join(IMPORT_DIR, "17_terrain.obj"),
                         "SM_Lanzhou_Terrain")
    if terrain is None:
        log("[LingXuJie] MX: terrain import failed")
        return 0
    log("[LingXuJie] MX: terrain imported")

    tile = import_texture("tile_108_road01",
                          os.path.join(TILE_SOURCE, "tile_108_road01.png"))
    ground = make_ground_material(tile) if tile is not None else None
    if ground is None:
        ground = make_surface_material("M_Moxiang_Ground",
                                       unreal.LinearColor(0.20, 0.19, 0.14, 1.0),
                                       0.92)
    stone = make_surface_material("M_Lanzhou_Stone",
                                  unreal.LinearColor(0.42, 0.39, 0.34, 1.0), 0.85)

    if place(terrain, ground, "MX_TERRAIN") is None:
        log("[LingXuJie] MX: could not place the terrain")
        return 0
    placed = 1

    # The city: one mesh per texture at its own world position, each wearing a material instance
    # over the texture the client used for that group. Tools/build_map_obj.py writes both the OBJs
    # and the manifest this loop reads.
    groups = load_city_manifest(os.path.join(IMPORT_DIR, "17_arch.json"))
    textured = 0
    untextured = 0
    failed = 0
    triangles = 0
    if groups:
        masters = {
            "opaque": make_building_master("M_Moxiang_Building", False),
            "masked": make_building_master("M_Moxiang_Building_Masked", True),
        }
        for entry in groups:
            mesh = import_obj(os.path.join(IMPORT_DIR, entry["obj"]),
                              entry["mesh"])
            if mesh is None:
                failed += 1
                continue
            material = None
            if entry.get("png"):
                texture = import_texture(
                    entry["slug"], os.path.join(BUILDING_DIR, entry["png"]))
                if texture is not None:
                    key = "masked" if entry.get("masked") else "opaque"
                    material = make_texture_instance(
                        entry["material"], masters[key], texture)
            if material is None:
                material = stone
                untextured += 1
            else:
                textured += 1
            if place(mesh, material, entry["label"], quiet=True) is not None:
                placed += 1
                triangles += entry.get("triangles", 0)
    else:
        # Older builds carried the whole city as one untextured mesh; keep that path so the map
        # still opens if the manifest is missing.
        arch = import_obj(os.path.join(IMPORT_DIR, "17_arch.obj"),
                          "SM_Lanzhou_Arch")
        if arch is not None and place(arch, stone, "MX_LANZHOU") is not None:
            placed += 1
    log("[LingXuJie] MX: city %d texture groups (%d textured, %d plain, %d failed), "
        "%d triangles" % (placed - 1, textured, untextured, failed, triangles))

    # Map 17 is flat around grid (40, 88); the height there is 3484 cm.
    start = subsystem.spawn_actor_from_class(
        unreal.PlayerStart, unreal.Vector(4000.0, -8800.0, 3684.0))
    if start is not None:
        start.set_actor_label("MX_PLAYERSTART")
        log("[LingXuJie] MX: player start at 4000, -8800, 3684")

    # A stand-in at the plaza so scale can be judged in the editor without starting the game.
    # (8950, -6200) is the most open cell the city geometry offers while still being surrounded
    # by buildings; its ground height is 3675 cm.
    character = spawn_stand_in(subsystem, unreal.Vector(8950.0, -6200.0, 3675.0))
    log("[LingXuJie] MX: stand-in character = %s" % (character is not None))

    log("[LingXuJie] MX: Lanzhou placed, %d surfaces" % placed)
    return placed


def spawn_stand_in(subsystem, location):
    """Put the game's own character in the level so a doorway has a person beside it.

    Tries the C++ class first and falls back to the blueprint, because whether the class is
    exposed to Python depends on whether the module was loaded when the editor started.
    """
    for name in ("LXJCharacter", "LXJCharacter_C"):
        cls = getattr(unreal, name, None)
        if cls is None:
            continue
        actor = subsystem.spawn_actor_from_class(
            cls, location, unreal.Rotator(0.0, 0.0, 180.0))
        if actor is not None:
            actor.set_actor_label("MX_CHARACTER")
            log("[LingXuJie] MX: character from %s at %.0f, %.0f, %.0f"
                % (name, location.x, location.y, location.z))
            return actor
    log("[LingXuJie] MX: character class not found in unreal module")
    return None
