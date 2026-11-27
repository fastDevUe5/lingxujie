"""LingXuJie level builder (sandbox for phase 0).

Runs inside the Unreal Editor commandlet:

    UnrealEditor-Cmd.exe LingXuJie.uproject -run=pythonscript -script=Tools/build_level.py

Creates the project materials and a cultivation-flavoured sandbox level
(a stone terrace, a spirit gate, rock pillars and an emissive qi circle),
then saves /Game/Maps/LingXuJie. The level is always rebuilt from scratch.
"""

import os
import sys
import traceback

import math
import unreal

# The commandlet does not put this script's own folder on the import path, so add it before
# reaching for the sibling module.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# The map reconstruction lives in its own module: it imports the geometry recovered from the
# client and replays the map's light list, which is a different job from the sandbox decoration
# this file grew up doing. Reload it when the editor rebuilds in place, otherwise the copy cached
# from the previous run keeps running and edits appear to do nothing.
import importlib
if "build_moxiang_map" in sys.modules:
    importlib.reload(sys.modules["build_moxiang_map"])
import build_moxiang_map

LEVEL_PATH = "/Game/Maps/LingXuJie"
MATERIAL_DIR = "/Game/Materials"

ASSET_TOOLS = unreal.AssetToolsHelpers.get_asset_tools()
ACTORS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LEVELS = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
MATERIAL_EDITING = unreal.MaterialEditingLibrary
EDITOR_ASSETS = unreal.EditorAssetLibrary


def log(message):
    unreal.log("[LingXuJie] " + str(message))


def safe_set(obj, name, value):
    """Set an optional editor property, warning instead of failing the build."""
    try:
        obj.set_editor_property(name, value)
        return True
    except Exception as exc:  # noqa: BLE001 - engine property names vary by version
        # Structs (like FPostProcessSettings) have no get_name(), so fall back to the type.
        label = obj.get_name() if hasattr(obj, "get_name") else type(obj).__name__
        log("skip property %s on %s (%s)" % (name, label, exc))
        return False


def set_grade(settings, name, value):
    """Set one PostProcessSettings value *and* its bOverride_ flag.

    An unbound post-process volume only applies the settings whose override flag is on; writing
    the value alone is accepted by Python and then ignored by the renderer. That is why the whole
    v1 grade (bloom, vignette, ambient occlusion) never showed up on screen (gotcha #55).
    """
    if safe_set(settings, name, value):
        safe_set(settings, "override_" + name, True)


def ensure_empty_level():
    """Load the existing map and wipe it, or create a fresh map if there is none."""
    if EDITOR_ASSETS.does_asset_exist(LEVEL_PATH):
        try:
            if LEVELS.load_level(LEVEL_PATH):
                cleared = 0
                for actor in ACTORS.get_all_level_actors():
                    if ACTORS.destroy_actor(actor):
                        cleared += 1
                log("Cleared %d actors from existing map" % cleared)
                return True
        except Exception as exc:  # noqa: BLE001
            log("Could not reuse existing map: %s" % exc)

    if EDITOR_ASSETS.does_asset_exist(LEVEL_PATH):
        EDITOR_ASSETS.delete_asset(LEVEL_PATH)

    created = LEVELS.new_level(LEVEL_PATH)
    log("new_level -> %s" % created)
    return created


def make_material(name, color, emissive_strength=0.0, roughness=0.5, metallic=0.0):
    path = MATERIAL_DIR + "/" + name
    if EDITOR_ASSETS.does_asset_exist(path):
        EDITOR_ASSETS.delete_asset(path)

    material = ASSET_TOOLS.create_asset(name, MATERIAL_DIR, unreal.Material, unreal.MaterialFactoryNew())
    if material is None:
        log("ERROR: could not create material " + name)
        return None

    base = MATERIAL_EDITING.create_material_expression(
        material, unreal.MaterialExpressionConstant3Vector, -420, -120)
    base.set_editor_property(
        "constant", unreal.LinearColor(color[0], color[1], color[2], 1.0))

    if emissive_strength > 0.0:
        material.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
        strength = MATERIAL_EDITING.create_material_expression(
            material, unreal.MaterialExpressionConstant, -420, 90)
        strength.set_editor_property("r", emissive_strength)
        multiply = MATERIAL_EDITING.create_material_expression(
            material, unreal.MaterialExpressionMultiply, -180, -120)
        MATERIAL_EDITING.connect_material_expressions(base, "", multiply, "A")
        MATERIAL_EDITING.connect_material_expressions(strength, "", multiply, "B")
        MATERIAL_EDITING.connect_material_property(
            multiply, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    else:
        MATERIAL_EDITING.connect_material_property(
            base, "", unreal.MaterialProperty.MP_BASE_COLOR)

        roughness_expr = MATERIAL_EDITING.create_material_expression(
            material, unreal.MaterialExpressionConstant, -420, 60)
        roughness_expr.set_editor_property("r", roughness)
        MATERIAL_EDITING.connect_material_property(
            roughness_expr, "", unreal.MaterialProperty.MP_ROUGHNESS)

        metallic_expr = MATERIAL_EDITING.create_material_expression(
            material, unreal.MaterialExpressionConstant, -420, 190)
        metallic_expr.set_editor_property("r", metallic)
        MATERIAL_EDITING.connect_material_property(
            metallic_expr, "", unreal.MaterialProperty.MP_METALLIC)

    MATERIAL_EDITING.recompile_material(material)
    EDITOR_ASSETS.save_asset(path)
    log("Material ready: " + path)
    return material


def make_materials():
    # Realism test: the flat colours are replaced by CC0 Poly Haven PBR sets. Tiling is
    # roughly "one texture tile per 2 m", so a 30 m terrace gets ~15 repeats.
    stone_tex = make_textured_material("M_Terrace_Stone", "precast_stone_paving", tiling=15.0)
    # The Poly Haven set is dry tundra grass (yellow-tan); a green multiply turns it into the
    # wet valley floor the gufeng direction needs. rebuild=True so the tint actually lands.
    ground_tex = make_textured_material("M_Ground_Grass", "grass_ground", tiling=42.0,
                                        tint=(0.40, 0.55, 0.32), rebuild=True)

    return {
        # Megascans paving (2K base/normal/ORM), flat placeholder otherwise. Tiling 3 keeps the
        # stone scale of the old 4K set: that scan covered 1x2 m, this one covers 2x4 m, so half
        # the repeats cover the same physical size.
        "stone": tiled_megascans("stone", "M_MS_Stone_Tiled", 6.0, rebuild=True) or stone_tex or make_material("M_Stone", (0.160, 0.170, 0.190), roughness=0.85, metallic=0.0),
        "moss": ground_tex or make_material("M_Moss", (0.080, 0.150, 0.110), roughness=0.9, metallic=0.0),
        # Terrain: packed dirt beside the road, blending into grass away from it. The blend lives
        # in the material (world-X mask) because a dirt strip laid on the ground always reads as a
        # band with a hard edge - the thing D8 keeps rejecting.
        "terrain": make_ground_blend_material("M_Terrain_Blend", inner=560.0, outer=1250.0,
                                             rebuild=True),
        "jade": make_material("M_Jade", (0.150, 0.620, 0.520), roughness=0.35, metallic=0.1),
        "qi": make_material("M_Qi", (0.450, 0.950, 1.000), emissive_strength=1.6),
        "gold": make_material("M_Gold", (1.000, 0.760, 0.260), emissive_strength=0.8),
        # Dirt patches fade into grass at their border; a plain dirt rectangle on grass is
        # exactly the "strip of tape" the eye keeps catching.
        "dirt": make_feathered_material("M_Ground_Dirt_Feather", "clay_plaster",
                                        tiling=7.0, feather=4.0),
        # House shell: rammed earth + timber; roof comes from the Megascans roof surface.
        "wall": make_textured_material("M_Wall_Plaster", "clay_plaster", tiling=6.0),
        "water": make_material("M_Water", (0.026, 0.062, 0.058), roughness=0.03, metallic=0.15),
        "wood": tiled_megascans("wood", "M_MS_Wood_Tiled", 5.0) or make_textured_material("M_Wood_Beam", "wood_planks", tiling=4.0),
        "roof": tiled_megascans("roof", "M_MS_Roof_Tiled", 8.0),
        # The 墨香-era village look: near-black timber and grey tiles. The raw Megascans scane are
        # pale grey planks and beige pottery tiles, which read as "beach house" on these houses.
        "wood_dark": make_megascans_tiled("M_MS_Wood_Dark", *MEGASCANS_TEXTURES["wood"], 2.0,
                                          tint=(0.26, 0.19, 0.14), rebuild=True),
        "roof_dark": make_megascans_tiled("M_MS_Roof_Dark", *MEGASCANS_TEXTURES["roof"], 3.0,
                                          tint=(0.18, 0.20, 0.24), rebuild=True),
        # 墨香 splits its roof language in two: village houses wear brown thatch / wood shingle at a
        # steep pitch, towns and gates wear green glazed tile. Two tints over the same scans.
        "roof_thatch": make_megascans_tiled("M_MS_Roof_Thatch", *MEGASCANS_TEXTURES["wood"], 2.5,
                                            tint=(0.46, 0.31, 0.20), rebuild=True),
        "roof_green": make_megascans_tiled("M_MS_Roof_Green", *MEGASCANS_TEXTURES["roof"], 2.5,
                                           tint=(0.30, 0.52, 0.38), rebuild=True),
        # 白墙: the clay plaster is a tan scan; multiplying it up turns it into the lime-washed
        # wall a 墨香 village has, without another texture download.
        "plaster_white": make_textured_material("M_Wall_White", "clay_plaster", tiling=6.0,
                                                tint=(1.75, 1.72, 1.60), rebuild=True),
        # Our own painted sheets (Tools/paint_textures.py): the 墨香 look is simple geometry plus
        # purpose-drawn textures - tile courses, straw, lime wash, dark timber, alpha lattice.
        # Palette follows the in-game Lanzhou screenshots (style-spec 7.3): red-brown tile, cream
        # plaster, blue-grey posts, pale tan braces, green painted soffit.
        "paint_wall": make_painted_material("M_Paint_Wall", "T_Plaster_Cream", tiling=1.0, rebuild=True),
        "paint_wood": make_painted_material("M_Paint_Wood", "T_Wood_Blue", tiling=1.0, rebuild=True),
        "paint_wood_tan": make_painted_material("M_Paint_Wood_Tan", "T_Wood_Tan", tiling=1.0, rebuild=True),
        "paint_thatch": make_painted_material("M_Paint_Thatch", "T_Roof_Thatch", tiling=2.0, rebuild=True),
        "paint_tile_red": make_painted_material("M_Paint_Tile_Red", "T_Roof_Red", tiling=2.0, rebuild=True),
        "paint_ridge": make_painted_material("M_Paint_Ridge", "T_Ridge_Pink", tiling=3.0, rebuild=True),
        "paint_tile_grey": make_painted_material("M_Paint_Tile_Grey", "T_Roof_Grey", tiling=2.0, rebuild=True),
        "paint_soffit": make_painted_material("M_Paint_Soffit", "T_Soffit_Green", tiling=3.0, rebuild=True),
        "paint_awning": make_painted_material("M_Paint_Awning", "T_Awning", tiling=2.0, rebuild=True),
        "paint_lantern": make_painted_material("M_Paint_Lantern", "T_Lantern", tiling=1.0,
                                               masked=True, rebuild=True),
        "paint_lattice": make_painted_material("M_Paint_Lattice", "T_Lattice_Alpha", tiling=1.0,
                                               masked=True, rebuild=True),
        "paint_gable": make_painted_material("M_Paint_Gable", "T_Gable_Triangle_UX", tiling=1.0,
                                             masked=True, rebuild=True),
    }


def spawn(cls, location, rotation=(0.0, 0.0, 0.0), label=None):
    actor = ACTORS.spawn_actor_from_class(
        cls, unreal.Vector(location[0], location[1], location[2]),
        unreal.Rotator(roll=rotation[0], pitch=rotation[1], yaw=rotation[2]))
    if actor is not None and label:
        actor.set_actor_label(label)
    return actor


def spawn_skeletal(label, mesh_path, location, yaw=0.0, scale=1.0, material=None):
    """Place a skeletal mesh actor (marketplace foliage is skinned, not a static mesh).

    Megaplants/Megascans plants ship as SKM_* + a skeleton, so they need a SkeletalMeshActor.
    With no animation they render their bind pose, which is all a still scene needs.
    """
    mesh = unreal.load_asset(mesh_path)
    if mesh is None:
        log("missing skeletal mesh: " + mesh_path)
        return None

    actor = spawn(unreal.SkeletalMeshActor, (location[0], location[1], location[2]),
                  rotation=(0.0, 0.0, yaw), label=label)
    if actor is None:
        return None

    component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
    if component is None:
        return actor

    safe_set(component, "animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    component.set_skeletal_mesh_asset(mesh)
    if material is not None:
        # Every material slot, not just 0: the billboard/LOD slots otherwise render with the
        # default material, which is where the little white "paper" triangles came from.
        for slot in range(component.get_num_materials()):
            component.set_material(slot, material)
    actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
    return actor


CUBE = unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
CYLINDER = unreal.load_asset("/Engine/BasicShapes/Cylinder.Cylinder")


def block(location, scale, material, label, mesh=None):
    actor = spawn(unreal.StaticMeshActor, location, label=label)
    if actor is None:
        return None
    component = actor.static_mesh_component
    safe_set(component, "mobility", unreal.ComponentMobility.STATIC)
    component.set_static_mesh(mesh if mesh is not None else CUBE)
    if material is not None:
        component.set_material(0, material)
    actor.set_actor_scale3d(unreal.Vector(scale[0], scale[1], scale[2]))
    return actor


def build_terrace(materials):
    stone = materials.get("stone")
    moss = materials.get("moss")
    jade = materials.get("jade")

    # Ground: 80 m x 80 m stone slab, top surface at Z = 0.
    build_terrain(materials)

    # Central terrace, 30 m square, 80 cm high, with a wide staircase to the south.
    block((0.0, 0.0, 40.0), (30.0, 30.0, 0.8), stone, "SM_Terrace")
    for i in range(4):
        block((0.0, -1700.0 + i * 100.0, 10.0 + i * 20.0), (8.0, 1.0, 0.2 + i * 0.2), stone,
              "SM_Step_%d" % i)

    # Spirit gate: two jade pillars with a lintel, facing the spawn point.
    # The spirit gate itself is a real Polyfork city gate now (see PROPS); these two jade
    # markers stay as the "qi pillars" flanking it so the old landmark silhouette survives.
    block((-760.0, -1200.0, 300.0), (0.8, 0.8, 6.0), jade, "SM_Gate_Pillar_W")
    block((760.0, -1200.0, 300.0), (0.8, 0.8, 6.0), jade, "SM_Gate_Pillar_E")

    # Rock pillars scattered around the terrace for parallax.
    pillars = (
        (-2200.0, 1800.0, 3.0),
        (2400.0, 1500.0, 4.5),
        (-2600.0, -600.0, 2.0),
        (1900.0, -2400.0, 3.5),
        (0.0, 2600.0, 5.0),
    )
    for index, (x, y, height) in enumerate(pillars):
        half = height * 100.0
        block((x, y, half), (3.0, 3.0, height * 2.0), stone, "SM_RockPillar_%d" % index)


def build_qi_circle(materials):
    qi = materials.get("qi")
    # Emissive ring of small cubes around the terrace centre, reads as a qi formation.
    import math
    for i in range(12):
        angle = (i / 12.0) * math.pi * 2.0
        radius = 900.0
        block((math.cos(angle) * radius, math.sin(angle) * radius, 95.0),
              (1.2, 1.2, 0.5), qi, "SM_QiNode_%d" % i, mesh=CYLINDER)


def build_training_dummies():
    """Optional C++ training dummies (ALXJTrainingDummy). Off in M0.3: real monsters took over.

    Handy for damage-number / HUD debugging: flip TRAINING_DUMMIES to True and rebuild.
    """
    TRAINING_DUMMIES = False
    if not TRAINING_DUMMIES:
        return

    dummy_class = unreal.load_class(None, "/Script/LingXuJie.LXJTrainingDummy")
    if dummy_class is None:
        log("skip training dummies: /Script/LingXuJie.LXJTrainingDummy not found")
        return

    spots = (
        (0.0, -1200.0, 180.0),
        (500.0, -700.0, 180.0),
        (-500.0, -700.0, 180.0),
    )
    for index, (x, y, z) in enumerate(spots):
        actor = ACTORS.spawn_actor_from_class(
            dummy_class, unreal.Vector(x, y, z), unreal.Rotator(roll=0.0, pitch=0.0, yaw=0.0))
        if actor is not None:
            actor.set_actor_label("TrainingDummy_%d" % index)
            log("Spawned training dummy %d at (%.0f, %.0f, %.0f)" % (index, x, y, z))


def build_monsters():
    """M0.3 step 2: 2 spirit beasts (melee chargers) + 2 evil cultivators (ranged kiters)."""
    # z = 170 sits on the terrace (top at 80 + capsule half height), z = 100 is on the ground.
    spawns = (
        ("/Script/LingXuJie.LXJSpiritBeast", "SpiritBeast_0", (900.0, 300.0, 170.0), 200.0),
        ("/Script/LingXuJie.LXJSpiritBeast", "SpiritBeast_1", (-900.0, 100.0, 170.0), 20.0),
        ("/Script/LingXuJie.LXJEvilCultivator", "EvilCultivator_0", (0.0, 1100.0, 170.0), 180.0),
        ("/Script/LingXuJie.LXJEvilCultivator", "EvilCultivator_1", (1500.0, 1500.0, 100.0), 220.0),
        # Village zone: spirit beasts wander the paddies (ground level, z = 100).
        ("/Script/LingXuJie.LXJSpiritBeast", "SpiritBeast_Village_0", (1150.0, -4300.0, 100.0), 160.0),
        ("/Script/LingXuJie.LXJSpiritBeast", "SpiritBeast_Village_1", (-1150.0, -4650.0, 100.0), 20.0),
    )
    for class_path, label, (x, y, z), yaw in spawns:
        monster_class = unreal.load_class(None, class_path)
        if monster_class is None:
            log("skip monster %s: %s not found" % (label, class_path))
            continue
        actor = ACTORS.spawn_actor_from_class(
            monster_class, unreal.Vector(x, y, z), unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw))
        if actor is not None:
            actor.set_actor_label(label)
            if "Village" in label:
                # Village beasts should guard the fields, not invade the spawn point.
                safe_set(actor, "aggro_radius", 700.0)
            log("Spawned monster %s at (%.0f, %.0f, %.0f)" % (label, x, y, z))


SPAWN_ACCENT_LIGHTS = False   # gate lamps + qi-ring glow: gone with the blockout


def build_lighting():
    # Golden hour, not noon: a high sun over bare ground read as "desert", which fights the
    # gufeng/xianxia direction. A low warm sun gives long shadows through the gate, a warm
    # rim on the roof tiles and blue shadows that the qi lights can play against.
    sun = spawn(unreal.DirectionalLight, (0.0, 0.0, 1200.0), rotation=(0.0, -42.0, 35.0), label="Sun")
    if sun is not None:
        sun_component = sun.get_component_by_class(unreal.DirectionalLightComponent)
        sun_component.set_mobility(unreal.ComponentMobility.MOVABLE)
        safe_set(sun_component, "intensity", 7.5)
        # Near-white on purpose: SkyAtmosphere scales the whole sky by this colour, so an orange
        # sun puts out the blue sky and the real-time SkyLight goes dark with it (gotcha #54).
        safe_set(sun_component, "light_color", unreal.Color(r=255, g=243, b=230, a=255))
        safe_set(sun_component, "atmosphere_sun_light", True)
        # A softer source angle keeps the terminator on the stone from looking cut out.
        safe_set(sun_component, "light_source_angle", 1.4)
        safe_set(sun_component, "cast_shadows", True)
        # Volumetric shadows are what turn the sun into visible shafts through the gate.
        safe_set(sun_component, "cast_volumetric_shadow", True)

    sky = spawn(unreal.SkyLight, (0.0, 0.0, 400.0), label="SkyLight")
    if sky is not None:
        sky_component = sky.get_component_by_class(unreal.SkyLightComponent)
        sky_component.set_mobility(unreal.ComponentMobility.MOVABLE)
        safe_set(sky_component, "real_time_capture", True)
        # Cool, low-intensity fill: keeps the shadow side blue instead of grey, and stops the
        # ambient from flattening the warm/cool split the sun and the rim light set up.
        safe_set(sky_component, "intensity", 1.25)
        safe_set(sky_component, "light_color", unreal.Color(r=165, g=190, b=235, a=255))

    # Sky: procedural atmosphere. The DIY HDRI dome needs the material "Is Sky" usage flag,
    # which Python cannot set (see gotcha #39), and Epic's HDRIBackdrop plugin is an
    # Editor-module plugin, so it stays out of the shipping path for now.
    # Sky: procedural atmosphere (the blue daylight sky). BP_Sky_Sphere was tried and
    # reverted: it ignores the directional light unless the blueprint variable is bound,
    # so it rendered a permanent sunset. Clouds are a separate layer (build_cloud_plane).
    spawn(unreal.SkyAtmosphere, (0.0, 0.0, 0.0), label="SkyAtmosphere")
    # Blue sky + engine volumetric clouds (the cloud material lives in a VolumetricClouds/ subfolder).
    build_clouds()

    # Cool rim light from behind: separates the gate pillars from the sky.
    rim = spawn(unreal.DirectionalLight, (0.0, 0.0, 1200.0), rotation=(0.0, -22.0, 215.0), label="RimLight")
    if rim is not None:
        rim_component = rim.get_component_by_class(unreal.DirectionalLightComponent)
        rim_component.set_mobility(unreal.ComponentMobility.MOVABLE)
        safe_set(rim_component, "intensity", 0.9)
        safe_set(rim_component, "light_color", unreal.Color(r=110, g=165, b=255, a=255))
        safe_set(rim_component, "cast_shadows", False)
        safe_set(rim_component, "atmosphere_sun_light", False)
        # Without an explicit priority the engine warns about competing directional lights.
        safe_set(rim_component, "forward_shading_priority", -1)

    # Warm lamp fire at the gate + a cyan glow on the qi ring: two-tone lighting adds depth.
    # Switched off with the rest of the old blockout - these lights belonged to the spirit gate
    # and the qi ring that no longer exist, and they were floating over empty ground.
    if SPAWN_ACCENT_LIGHTS:
        accent_light((-620.0, -1200.0, 320.0), unreal.Color(r=255, g=170, b=90, a=255), 900.0, 1000.0, "GateLight_W")
        accent_light((620.0, -1200.0, 320.0), unreal.Color(r=255, g=170, b=90, a=255), 900.0, 1000.0, "GateLight_E")
    import math
    for index in range(4):
        angle = index / 4.0 * math.pi * 2.0
        accent_light((math.cos(angle) * 900.0, math.sin(angle) * 900.0, 200.0),
                     unreal.Color(r=90, g=230, b=255, a=255), 600.0, 800.0, "QiLight_%d" % index)

    # One unbound post process volume carries the grade. Exposure itself is locked globally
    # (r.DefaultFeature.AutoExposure=False in DefaultEngine.ini) so it is not overridden here:
    # auto exposure chasing the added lights is what washed the earlier attempts out.
    volume = spawn(unreal.PostProcessVolume, (0.0, 0.0, 0.0), label="PostProcess")
    if volume is not None:
        safe_set(volume, "unbound", True)
        settings = unreal.PostProcessSettings()
        # Every graded value needs its bOverride_ flag, otherwise the volume silently ignores it
        # (gotcha #55: the whole v1 grade - bloom, vignette, AO - was set but never applied).
        set_grade(settings, "bloom_intensity", 0.9)
        set_grade(settings, "bloom_threshold", 1.05)
        set_grade(settings, "vignette_intensity", 0.10)
        set_grade(settings, "ambient_occlusion_intensity", 0.8)
        # Light grade: the warmth lives here instead of the sun light colour (gotcha #54), so the
        # sky keeps its blue while the stone reads golden.
        set_grade(settings, "white_temp", 5600.0)
        set_grade(settings, "color_saturation", unreal.Vector4(1.05, 1.05, 1.05, 1.0))
        set_grade(settings, "color_contrast", unreal.Vector4(1.04, 1.04, 1.04, 1.0))
        set_grade(settings, "color_gain", unreal.Vector4(1.03, 1.00, 0.97, 1.0))
        safe_set(volume, "settings", settings)

    fog = spawn(unreal.ExponentialHeightFog, (0.0, 0.0, 0.0), label="HeightFog")
    if fog is not None:
        fog_component = fog.get_component_by_class(unreal.ExponentialHeightFogComponent)
        # Thicker, cool fog: it separates the three zones by depth and gives the gate a haze to
        # silhouette against - the cheapest way to make a flat boxout read as a valley.
        safe_set(fog_component, "fog_density", 0.004)
        safe_set(fog_component, "fog_height_falloff", 0.05)
        safe_set(fog_component, "fog_inscattering_luminance", unreal.LinearColor(0.55, 0.66, 0.85, 1.0))
        safe_set(fog_component, "enable_volumetric_fog", True)
        safe_set(fog_component, "volumetric_fog_extinction_scale", 1.2)
        safe_set(fog_component, "volumetric_fog_scattering_distribution", 0.6)
        safe_set(fog_component, "volumetric_fog_albedo", unreal.Color(r=200, g=215, b=245, a=255))

    # Village south entrance, facing north up the one street: P0 starts in 桃源村, not in 兰州.
    spawn(unreal.PlayerStart, (0.0, -10800.0, 120.0), rotation=(0.0, 0.0, 90.0), label="PlayerStart")


def accent_light(location, color, intensity, radius, label):
    """Colored point light used to sell the qi ring and the gate lamps."""
    light = spawn(unreal.PointLight, location, label=label)
    if light is None:
        return None

    component = light.get_component_by_class(unreal.PointLightComponent)
    component.set_mobility(unreal.ComponentMobility.MOVABLE)
    safe_set(component, "intensity", intensity)
    safe_set(component, "light_color", color)
    safe_set(component, "attenuation_radius", radius)
    safe_set(component, "cast_shadows", False)
    return light


TEXTURE_SOURCE_DIR = os.path.join("Assets", "Textures")


def apply_texture_flags(texture, is_normal, is_linear):
    """Colour maps are sRGB; normal/roughness maps are linear and normals need TC_NORMALMAP."""
    if texture is None:
        return
    safe_set(texture, "srgb", not is_linear)
    if is_normal:
        safe_set(texture, "compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
    EDITOR_ASSETS.save_asset(texture.get_path_name().split(".")[0])


def ensure_texture(texture_set, map_name, is_normal=False, is_linear=True):
    """Imports one Poly Haven JPG once and returns the Texture2D (or None)."""
    asset_name = "%s_%s" % (texture_set, map_name)
    path = "/Game/Textures/%s/%s" % (texture_set, asset_name)
    if EDITOR_ASSETS.does_asset_exist(path):
        existing = unreal.load_asset(path)
        # Re-apply on every run: an earlier import may have guessed sRGB wrong.
        apply_texture_flags(existing, is_normal, is_linear)
        return existing

    source = os.path.join(unreal.Paths.project_dir(), TEXTURE_SOURCE_DIR, texture_set,
                          "%s_%s_1k.jpg" % (texture_set, map_name))
    if not os.path.isfile(source):
        log("missing texture source: " + source)
        return None

    task = unreal.AssetImportTask()
    task.filename = source
    task.destination_path = "/Game/Textures/" + texture_set
    task.destination_name = asset_name
    task.automated = True
    task.replace_existing = True
    task.save = True

    # sRGB has to be decided at import time: flipping it on an imported Texture2D through
    # Python does not rebuild the resource, so the flag silently stays wrong.
    factory = unreal.TextureFactory()
    safe_set(factory, "srgb", not is_linear)
    if is_normal:
        safe_set(factory, "compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
    task.factory = factory

    ASSET_TOOLS.import_asset_tasks([task])

    texture = unreal.load_asset(path)
    if texture is None:
        log("texture import produced nothing: " + path)
        return None

    apply_texture_flags(texture, is_normal, is_linear)
    return texture


def make_feathered_material(name, texture_set, tiling, tint=None, feather=6.0):
    """Dirt that dissolves into grass at the patch border.

    A dirt rectangle laid on grass always reads as a strip of tape, whatever colour it is: the
    eye locks onto the straight colour boundary. So the dirt patch is drawn with a mask that is
    1 in the middle and falls to 0 at the UV border, and the border half of that mask is the
    grass texture - the patch fades into the ground instead of being cut out of it.
    """
    path = MATERIAL_DIR + "/" + name
    if EDITOR_ASSETS.does_asset_exist(path):
        return unreal.load_asset(path)

    dirt = ensure_texture(texture_set, "diff", is_linear=False)
    grass = ensure_texture("grass_ground", "diff", is_linear=False)
    if dirt is None or grass is None:
        log("no textures for feathered material " + name)
        return None

    material = ASSET_TOOLS.create_asset(name, MATERIAL_DIR, unreal.Material, unreal.MaterialFactoryNew())
    if material is None:
        return None

    dirt_coords = MATERIAL_EDITING.create_material_expression(
        material, unreal.MaterialExpressionTextureCoordinate, -1200, -240)
    safe_set(dirt_coords, "u_tiling", tiling)
    safe_set(dirt_coords, "v_tiling", tiling)
    dirt_sample = MATERIAL_EDITING.create_material_expression(
        material, unreal.MaterialExpressionTextureSample, -960, -240)
    safe_set(dirt_sample, "texture", dirt)
    MATERIAL_EDITING.connect_material_expressions(dirt_coords, "", dirt_sample, "UVs")

    grass_coords = MATERIAL_EDITING.create_material_expression(
        material, unreal.MaterialExpressionTextureCoordinate, -1200, 40)
    safe_set(grass_coords, "u_tiling", 12.0)
    safe_set(grass_coords, "v_tiling", 12.0)
    grass_sample = MATERIAL_EDITING.create_material_expression(
        material, unreal.MaterialExpressionTextureSample, -960, 40)
    safe_set(grass_sample, "texture", grass)
    MATERIAL_EDITING.connect_material_expressions(grass_coords, "", grass_sample, "UVs")

    # Border mask: u*(1-u) + v*(1-v) peaks at 0.5 in the middle and is 0 on every edge.
    uv = MATERIAL_EDITING.create_material_expression(
        material, unreal.MaterialExpressionTextureCoordinate, -1200, 320)
    safe_set(uv, "u_tiling", 1.0)
    safe_set(uv, "v_tiling", 1.0)

    def component(source, row):
        mask = MATERIAL_EDITING.create_material_expression(
            material, unreal.MaterialExpressionComponentMask, -1000, row)
        safe_set(mask, "r", True)
        safe_set(mask, "g", False)
        safe_set(mask, "b", False)
        safe_set(mask, "a", False)
        MATERIAL_EDITING.connect_material_expressions(source, "", mask, "")
        return mask

    def scalar(value, row):
        node = MATERIAL_EDITING.create_material_expression(
            material, unreal.MaterialExpressionConstant, -1000, row)
        node.set_editor_property("r", value)
        return node

    def binary(cls, a, b, row):
        node = MATERIAL_EDITING.create_material_expression(material, cls, -800, row)
        MATERIAL_EDITING.connect_material_expressions(a, "", node, "A")
        MATERIAL_EDITING.connect_material_expressions(b, "", node, "B")
        return node

    u = component(uv, 400)
    v_mask = MATERIAL_EDITING.create_material_expression(
        material, unreal.MaterialExpressionComponentMask, -1000, 470)
    safe_set(v_mask, "r", False)
    safe_set(v_mask, "g", True)
    safe_set(v_mask, "b", False)
    safe_set(v_mask, "a", False)
    MATERIAL_EDITING.connect_material_expressions(uv, "", v_mask, "")

    one = scalar(1.0, 540)
    u_inv = binary(unreal.MaterialExpressionSubtract, one, u, 400)
    u_term = binary(unreal.MaterialExpressionMultiply, u, u_inv, 460)
    v_inv = binary(unreal.MaterialExpressionSubtract, one, v_mask, 520)
    v_term = binary(unreal.MaterialExpressionMultiply, v_mask, v_inv, 580)
    total = binary(unreal.MaterialExpressionAdd, u_term, v_term, 640)
    # 4.0 puts the fade over the outer ~25% of the patch.
    gain = scalar(feather, 700)
    strength = binary(unreal.MaterialExpressionMultiply, total, gain, 700)

    lerp = MATERIAL_EDITING.create_material_expression(
        material, unreal.MaterialExpressionLinearInterpolate, -420, 200)
    MATERIAL_EDITING.connect_material_expressions(grass_sample, "RGB", lerp, "A")
    MATERIAL_EDITING.connect_material_expressions(dirt_sample, "RGB", lerp, "B")
    MATERIAL_EDITING.connect_material_expressions(strength, "", lerp, "Alpha")

    if tint is None:
        MATERIAL_EDITING.connect_material_property(lerp, "", unreal.MaterialProperty.MP_BASE_COLOR)
    else:
        tinted = MATERIAL_EDITING.create_material_expression(
            material, unreal.MaterialExpressionMultiply, -220, 200)
        tint_expr = MATERIAL_EDITING.create_material_expression(
            material, unreal.MaterialExpressionConstant3Vector, -420, 300)
        tint_expr.set_editor_property(
            "constant", unreal.LinearColor(tint[0], tint[1], tint[2], 1.0))
        MATERIAL_EDITING.connect_material_expressions(lerp, "", tinted, "A")
        MATERIAL_EDITING.connect_material_expressions(tint_expr, "", tinted, "B")
        MATERIAL_EDITING.connect_material_property(tinted, "", unreal.MaterialProperty.MP_BASE_COLOR)

    MATERIAL_EDITING.recompile_material(material)
    EDITOR_ASSETS.save_asset(path)
    log("feathered material ready: " + path)
    return material


def make_ground_blend_material(name, inner=560.0, outer=1250.0, noise_amount=260.0,
                               sand_y0=-6600.0, sand_y1=6000.0, sand_fade=900.0, rebuild=False):
    """Ground material that turns from packed dirt beside the road into grass further out.

    The map's one road runs along X = 0, so the blend is a function of |world X|: dirt inside
    `inner` (just past the paving edge), grass past `outer`, with a low-frequency noise offset so
    the boundary wanders instead of being a ruler-straight line. Everything happens in the
    material - a coloured patch laid on the ground is exactly the "strip of tape" D8 rejects.
    """
    path = MATERIAL_DIR + "/" + name
    if EDITOR_ASSETS.does_asset_exist(path):
        if not rebuild:
            return unreal.load_asset(path)
        EDITOR_ASSETS.delete_asset(path)
        log("rebuilding material asset: " + path)

    grass = ensure_texture("grass_ground", "diff", is_linear=False)
    dirt = ensure_texture("clay_plaster", "diff", is_linear=False)
    if grass is None or dirt is None:
        log("no textures for ground blend " + name)
        return None

    material = ASSET_TOOLS.create_asset(name, MATERIAL_DIR, unreal.Material, unreal.MaterialFactoryNew())
    if material is None:
        return None

    def node(cls, x, y):
        return MATERIAL_EDITING.create_material_expression(material, cls, x, y)

    def constant(value, x, y):
        expr = node(unreal.MaterialExpressionConstant, x, y)
        expr.set_editor_property("r", value)
        return expr

    def binary(cls, a, b, x, y):
        expr = node(cls, x, y)
        MATERIAL_EDITING.connect_material_expressions(a, "", expr, "A")
        MATERIAL_EDITING.connect_material_expressions(b, "", expr, "B")
        return expr

    # --- two surfaces -------------------------------------------------------------------------
    grass_uv = node(unreal.MaterialExpressionTextureCoordinate, -1500, -300)
    safe_set(grass_uv, "u_tiling", 1.0)
    safe_set(grass_uv, "v_tiling", 1.0)
    grass_sample = node(unreal.MaterialExpressionTextureSample, -1280, -300)
    safe_set(grass_sample, "texture", grass)
    MATERIAL_EDITING.connect_material_expressions(grass_uv, "", grass_sample, "UVs")

    # Same green multiply the plain grass terrain used, so the valley floor keeps its colour.
    grass_tint = node(unreal.MaterialExpressionConstant3Vector, -1280, -120)
    grass_tint.set_editor_property("constant", unreal.LinearColor(0.40, 0.55, 0.32, 1.0))
    grass_colour = binary(unreal.MaterialExpressionMultiply, grass_sample, grass_tint, -1040, -260)

    dirt_uv = node(unreal.MaterialExpressionTextureCoordinate, -1500, 60)
    safe_set(dirt_uv, "u_tiling", 2.0)
    safe_set(dirt_uv, "v_tiling", 2.0)
    dirt_sample = node(unreal.MaterialExpressionTextureSample, -1280, 60)
    safe_set(dirt_sample, "texture", dirt)
    MATERIAL_EDITING.connect_material_expressions(dirt_uv, "", dirt_sample, "UVs")
    # clay_plaster is a warm sandy tan; the 赭石 direction calls for a duller earth, so pull the
    # saturation down a touch before it is blended in.
    dirt_tint = node(unreal.MaterialExpressionConstant3Vector, -1280, 220)
    dirt_tint.set_editor_property("constant", unreal.LinearColor(0.82, 0.76, 0.68, 1.0))
    dirt_colour = binary(unreal.MaterialExpressionMultiply, dirt_sample, dirt_tint, -1040, 120)

    # --- |world X| ----------------------------------------------------------------------------
    world = node(unreal.MaterialExpressionWorldPosition, -1500, 380)
    world_x = node(unreal.MaterialExpressionComponentMask, -1320, 380)
    safe_set(world_x, "r", True)
    safe_set(world_x, "g", False)
    safe_set(world_x, "b", False)
    safe_set(world_x, "a", False)
    MATERIAL_EDITING.connect_material_expressions(world, "", world_x, "")
    abs_x = node(unreal.MaterialExpressionAbs, -1160, 380)
    MATERIAL_EDITING.connect_material_expressions(world_x, "", abs_x, "")

    # Low-frequency wobble: the grass texture sampled at 1/25 scale is as good as a Noise node and
    # costs one sampler.
    wobble_uv = node(unreal.MaterialExpressionTextureCoordinate, -1500, 620)
    safe_set(wobble_uv, "u_tiling", 0.04)
    safe_set(wobble_uv, "v_tiling", 0.04)
    wobble_sample = node(unreal.MaterialExpressionTextureSample, -1320, 620)
    safe_set(wobble_sample, "texture", grass)
    MATERIAL_EDITING.connect_material_expressions(wobble_uv, "", wobble_sample, "UVs")
    wobble = node(unreal.MaterialExpressionComponentMask, -1140, 620)
    safe_set(wobble, "r", True)
    safe_set(wobble, "g", False)
    safe_set(wobble, "b", False)
    safe_set(wobble, "a", False)
    MATERIAL_EDITING.connect_material_expressions(wobble_sample, "", wobble, "")
    wobble_scaled = binary(unreal.MaterialExpressionMultiply, wobble, constant(noise_amount, -1320, 720), -1080, 640)

    # t = saturate((|x| + wobble - inner) / (outer - inner)); dirt = 1 - t
    shifted = binary(unreal.MaterialExpressionAdd, abs_x, wobble_scaled, -960, 460)
    inside = binary(unreal.MaterialExpressionSubtract, shifted, constant(inner, -960, 560), -820, 460)
    scaled = binary(unreal.MaterialExpressionDivide, inside, constant(outer - inner, -820, 560), -680, 480)
    # Clamp's input pin does not bind from Python here ("Missing Clamp input"), so saturate with
    # max(x, 0) followed by min(x, 1) - both take plain A/B pins.
    above_zero = binary(unreal.MaterialExpressionMax, scaled, constant(0.0, -680, 660), -540, 500)
    t_clamped = binary(unreal.MaterialExpressionMin, above_zero, constant(1.0, -540, 700), -420, 520)
    dirt_amount = binary(unreal.MaterialExpressionSubtract, constant(1.0, -680, 620), t_clamped, -300, 540)

    blend = node(unreal.MaterialExpressionLinearInterpolate, -260, 0)
    MATERIAL_EDITING.connect_material_expressions(grass_colour, "", blend, "A")
    MATERIAL_EDITING.connect_material_expressions(dirt_colour, "", blend, "B")
    MATERIAL_EDITING.connect_material_expressions(dirt_amount, "", blend, "Alpha")

    # --- sand band along world Y --------------------------------------------------------------
    # 敦煌 is desert between the city and 秦皇陵, so the same trick runs on the other axis: full sand
    # inside the band, fading over `sand_fade` at each end. Done in the material for the same reason
    # as the dirt band - a tan rectangle laid on the ground reads as tape (D8).
    world_y = node(unreal.MaterialExpressionComponentMask, -1500, 900)
    safe_set(world_y, "r", False)
    safe_set(world_y, "g", True)
    safe_set(world_y, "b", False)
    safe_set(world_y, "a", False)
    MATERIAL_EDITING.connect_material_expressions(world, "", world_y, "")

    def ramp(value_expr, x, y):
        """saturate(value): Max then Min, because Clamp's input pin does not bind from Python."""
        above = binary(unreal.MaterialExpressionMax, value_expr, constant(0.0, x - 140, y + 100), x, y)
        return binary(unreal.MaterialExpressionMin, above, constant(1.0, x + 20, y + 140), x + 160, y)

    north_in = binary(unreal.MaterialExpressionSubtract, world_y,
                      constant(sand_y0, -960, 900), -820, 900)
    north = ramp(binary(unreal.MaterialExpressionDivide, north_in,
                        constant(sand_fade, -820, 1000), -680, 900), -540, 900)
    south_in = binary(unreal.MaterialExpressionSubtract, constant(sand_y1, -960, 1120),
                      world_y, -820, 1120)
    south = ramp(binary(unreal.MaterialExpressionDivide, south_in,
                        constant(sand_fade, -820, 1220), -680, 1120), -540, 1120)
    sand_amount = binary(unreal.MaterialExpressionMultiply, north, south, -360, 1000)

    sand_tint = node(unreal.MaterialExpressionConstant3Vector, -1280, 1340)
    sand_tint.set_editor_property("constant", unreal.LinearColor(0.86, 0.74, 0.52, 1.0))
    sand_colour = binary(unreal.MaterialExpressionMultiply, dirt_sample, sand_tint, -1040, 1340)

    sand_blend = node(unreal.MaterialExpressionLinearInterpolate, -120, 1150)
    MATERIAL_EDITING.connect_material_expressions(blend, "", sand_blend, "A")
    MATERIAL_EDITING.connect_material_expressions(sand_colour, "", sand_blend, "B")
    MATERIAL_EDITING.connect_material_expressions(sand_amount, "", sand_blend, "Alpha")
    MATERIAL_EDITING.connect_material_property(sand_blend, "", unreal.MaterialProperty.MP_BASE_COLOR)

    roughness = constant(0.92, -400, 700)
    MATERIAL_EDITING.connect_material_property(roughness, "", unreal.MaterialProperty.MP_ROUGHNESS)
    specular = constant(0.1, -400, 780)
    MATERIAL_EDITING.connect_material_property(specular, "", unreal.MaterialProperty.MP_SPECULAR)

    MATERIAL_EDITING.recompile_material(material)
    EDITOR_ASSETS.save_asset(path)
    log("ground blend material ready: %s (dirt < %.0f cm, grass > %.0f cm)" % (path, inner, outer))
    return material


PAINTED_TEX_DIR = "/Game/Textures"
PAINTED_SRC_DIR = os.path.join("Assets", "Textures")


def ensure_painted_texture(asset_name, rebuild=False):
    """Import one of our own painted PNGs (Assets/Textures) as a Texture2D asset.

    rebuild=True deletes and re-imports: editing the PNG on disk does nothing otherwise, the
    existing asset keeps serving the old pixels (the same trap as the generated materials).
    """
    path = PAINTED_TEX_DIR + "/" + asset_name
    if EDITOR_ASSETS.does_asset_exist(path):
        if not rebuild:
            return unreal.load_asset(path)
        EDITOR_ASSETS.delete_asset(path)
    source = os.path.join(unreal.Paths.project_dir(), PAINTED_SRC_DIR, asset_name + ".png")
    if not os.path.isfile(source):
        log("missing painted texture source: " + source)
        return None
    task = unreal.AssetImportTask()
    task.filename = source
    task.destination_path = PAINTED_TEX_DIR
    task.destination_name = asset_name
    task.automated = True
    task.replace_existing = True
    task.save = True
    factory = unreal.TextureFactory()
    # TC_DEFAULT keeps the alpha channel, which the lattice / gable sheets depend on.
    safe_set(factory, "compression_settings", unreal.TextureCompressionSettings.TC_DEFAULT)
    task.factory = factory
    ASSET_TOOLS.import_asset_tasks([task])
    imported = unreal.load_asset(path)
    log("painted texture imported: %s -> %s" % (source, "ok" if imported else "FAILED"))
    return imported


def make_painted_material(name, texture_name, tiling=1.0, masked=False, rebuild=False):
    """A material over one of our own painted sheets.

    masked=True builds a two-sided masked material that reads the sheet's alpha, which is how a
    flat board becomes a window lattice or a triangular gable.
    """
    path = MATERIAL_DIR + "/" + name
    if EDITOR_ASSETS.does_asset_exist(path):
        if not rebuild:
            return unreal.load_asset(path)
        EDITOR_ASSETS.delete_asset(path)

    texture = ensure_painted_texture(texture_name, rebuild=rebuild)
    if texture is None:
        return None

    material = ASSET_TOOLS.create_asset(name, MATERIAL_DIR, unreal.Material, unreal.MaterialFactoryNew())
    if material is None:
        return None
    if masked:
        safe_set(material, "blend_mode", unreal.BlendMode.BLEND_MASKED)
        safe_set(material, "two_sided", True)

    coords = MATERIAL_EDITING.create_material_expression(
        material, unreal.MaterialExpressionTextureCoordinate, -700, 0)
    safe_set(coords, "u_tiling", tiling)
    safe_set(coords, "v_tiling", tiling)
    sample = MATERIAL_EDITING.create_material_expression(
        material, unreal.MaterialExpressionTextureSample, -420, 0)
    safe_set(sample, "texture", texture)
    MATERIAL_EDITING.connect_material_expressions(coords, "", sample, "UVs")
    MATERIAL_EDITING.connect_material_property(sample, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
    if masked:
        MATERIAL_EDITING.connect_material_property(sample, "A",
                                                   unreal.MaterialProperty.MP_OPACITY_MASK)
    # Flat roughness: these sheets are painted, not scanned, so keep the light response simple.
    roughness = MATERIAL_EDITING.create_material_expression(
        material, unreal.MaterialExpressionConstant, -420, 220)
    roughness.set_editor_property("r", 0.85 if not masked else 0.7)
    MATERIAL_EDITING.connect_material_property(roughness, "", unreal.MaterialProperty.MP_ROUGHNESS)

    MATERIAL_EDITING.recompile_material(material)
    EDITOR_ASSETS.save_asset(path)
    log("painted material ready: " + path)
    return material


def make_textured_material(name, texture_set, tiling, roughness_scale=1.0, tint=None, rebuild=False):
    """Creates a PBR material from a Poly Haven set (diffuse + normal + roughness).

    ``tint`` multiplies the diffuse by a colour - that is how the dry tundra-grass photo is
    pushed towards the green of a Jiangnan valley without needing a second texture set.
    ``rebuild`` throws the existing asset away first: tiling/tint changes are not picked up by a
    material that already exists (gotcha #50's caching trap).
    """
    path = MATERIAL_DIR + "/" + name
    if EDITOR_ASSETS.does_asset_exist(path):
        existing = unreal.load_asset(path)
        if not rebuild:
            # The texture flags may have been corrected since this material was compiled;
            # a recompile is cheap and makes the run idempotent.
            MATERIAL_EDITING.recompile_material(existing)
            return existing
        EDITOR_ASSETS.delete_asset(path)

    diffuse = ensure_texture(texture_set, "diff", is_linear=False)
    normal = ensure_texture(texture_set, "nor_gl", is_normal=True)
    rough = ensure_texture(texture_set, "rough")
    if diffuse is None:
        log("no diffuse for " + texture_set + ", skipping textured material")
        return None

    material = ASSET_TOOLS.create_asset(name, MATERIAL_DIR, unreal.Material, unreal.MaterialFactoryNew())
    if material is None:
        return None

    coords = MATERIAL_EDITING.create_material_expression(
        material, unreal.MaterialExpressionTextureCoordinate, -900, 0)
    safe_set(coords, "u_tiling", tiling)
    safe_set(coords, "v_tiling", tiling)

    base = MATERIAL_EDITING.create_material_expression(
        material, unreal.MaterialExpressionTextureSample, -620, -160)
    safe_set(base, "texture", diffuse)
    MATERIAL_EDITING.connect_material_expressions(coords, "", base, "UVs")
    if tint is None:
        MATERIAL_EDITING.connect_material_property(base, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
    else:
        # Multiply.ConstB is a float, so the tint has to arrive as a Constant3Vector input.
        tinted = MATERIAL_EDITING.create_material_expression(
            material, unreal.MaterialExpressionMultiply, -380, -160)
        tint_expr = MATERIAL_EDITING.create_material_expression(
            material, unreal.MaterialExpressionConstant3Vector, -600, -60)
        tint_expr.set_editor_property(
            "constant", unreal.LinearColor(tint[0], tint[1], tint[2], 1.0))
        MATERIAL_EDITING.connect_material_expressions(base, "RGB", tinted, "A")
        MATERIAL_EDITING.connect_material_expressions(tint_expr, "", tinted, "B")
        MATERIAL_EDITING.connect_material_property(tinted, "", unreal.MaterialProperty.MP_BASE_COLOR)

    if normal is not None:
        normal_expr = MATERIAL_EDITING.create_material_expression(
            material, unreal.MaterialExpressionTextureSample, -620, 40)
        safe_set(normal_expr, "texture", normal)
        safe_set(normal_expr, "sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
        MATERIAL_EDITING.connect_material_expressions(coords, "", normal_expr, "UVs")
        MATERIAL_EDITING.connect_material_property(normal_expr, "RGB", unreal.MaterialProperty.MP_NORMAL)

    if rough is not None:
        rough_expr = MATERIAL_EDITING.create_material_expression(
            material, unreal.MaterialExpressionTextureSample, -620, 240)
        safe_set(rough_expr, "texture", rough)
        MATERIAL_EDITING.connect_material_expressions(coords, "", rough_expr, "UVs")
        scale = MATERIAL_EDITING.create_material_expression(
            material, unreal.MaterialExpressionMultiply, -340, 240)
        safe_set(scale, "const_b", roughness_scale)
        MATERIAL_EDITING.connect_material_expressions(rough_expr, "R", scale, "A")
        MATERIAL_EDITING.connect_material_property(scale, "", unreal.MaterialProperty.MP_ROUGHNESS)

    MATERIAL_EDITING.recompile_material(material)
    EDITOR_ASSETS.save_asset(path)
    log("textured material ready: %s (%s)" % (path, texture_set))
    return material


def ensure_hdri_texture(hdri_id):
    """Imports a Poly Haven .hdr once as a linear HDR Texture2D."""
    asset_name = hdri_id
    path = "/Game/Textures/hdri/" + asset_name
    if EDITOR_ASSETS.does_asset_exist(path):
        return unreal.load_asset(path)

    source = os.path.join(unreal.Paths.project_dir(), TEXTURE_SOURCE_DIR, "hdri", hdri_id + ".hdr")
    if not os.path.isfile(source):
        log("missing HDRI source: " + source)
        return None

    task = unreal.AssetImportTask()
    task.filename = source
    task.destination_path = "/Game/Textures/hdri"
    task.destination_name = asset_name
    task.automated = True
    task.replace_existing = True
    task.save = True

    # HDR skies must be linear and stored as HDR, exactly like the PBR maps (gotcha #38).
    factory = unreal.TextureFactory()
    safe_set(factory, "compression_settings", unreal.TextureCompressionSettings.TC_HDR)
    task.factory = factory

    ASSET_TOOLS.import_asset_tasks([task])
    texture = unreal.load_asset(path)
    if texture is None:
        log("HDRI import produced nothing: " + path)
        return None

    apply_texture_flags(texture, False, True)
    log("HDRI ready: " + path)
    return texture


def make_sky_material(hdri_texture):
    """Unlit, two-sided material that samples the equirect HDRI with the sphere's UVs.

    A huge inverted sphere plus this material is enough for a believable sky without the
    HDRIBackdrop plugin; the SkyLight's real-time capture then lights the scene from it.
    """
    path = MATERIAL_DIR + "/M_Sky_HDRI"
    if EDITOR_ASSETS.does_asset_exist(path):
        existing = unreal.load_asset(path)
        # The flag is what makes the renderer treat this as sky (far-plane draw + SkyLight
        # capture). It is re-applied here because a material created before it existed
        # would otherwise keep rendering as an opaque sphere in front of the level.
        safe_set(existing, "is_sky", True)
        safe_set(existing, "shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
        safe_set(existing, "two_sided", True)
        MATERIAL_EDITING.recompile_material(existing)
        EDITOR_ASSETS.save_asset(path)
        return existing

    material = ASSET_TOOLS.create_asset("M_Sky_HDRI", MATERIAL_DIR, unreal.Material,
                                        unreal.MaterialFactoryNew())
    if material is None:
        return None

    safe_set(material, "shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    safe_set(material, "two_sided", True)
    # "Is Sky" makes the renderer draw this at the far plane behind all geometry AND lets a
    # real-time-capture SkyLight pick it up (otherwise the sky light warns and the dome
    # occludes the whole level).
    safe_set(material, "is_sky", True)

    tex = MATERIAL_EDITING.create_material_expression(
        material, unreal.MaterialExpressionTextureSample, -520, 0)
    safe_set(tex, "texture", hdri_texture)
    safe_set(tex, "sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)

    # Sky intensity: the HDRI is authored for IBL, so a small multiplier keeps it from
    # blowing out next to a sun-lit scene.
    multiply = MATERIAL_EDITING.create_material_expression(
        material, unreal.MaterialExpressionMultiply, -300, 0)
    safe_set(multiply, "const_b", 0.85)
    MATERIAL_EDITING.connect_material_expressions(tex, "RGB", multiply, "A")
    MATERIAL_EDITING.connect_material_property(multiply, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)

    MATERIAL_EDITING.recompile_material(material)
    EDITOR_ASSETS.save_asset(path)
    log("sky material ready: " + path)
    return material


def build_sky(hdri_id="belfast_sunset_puresky"):
    """Replaces the procedural sky with an HDRI dome (and lets the SkyLight capture it)."""
    hdri = ensure_hdri_texture(hdri_id)
    if hdri is None:
        log("no HDRI, keeping the atmosphere-only sky")
        return None

    material = make_sky_material(hdri)
    dome = spawn(unreal.StaticMeshActor, (0.0, 0.0, 0.0), label="SM_SkyDome")
    if dome is None or material is None:
        return None

    sphere = unreal.load_asset("/Engine/BasicShapes/Sphere.Sphere")
    component = dome.static_mesh_component
    safe_set(component, "mobility", unreal.ComponentMobility.STATIC)
    component.set_static_mesh(sphere)
    component.set_material(0, material)
    # 100 cm sphere x 800 = 800 m across, comfortably outside the play area.
    dome.set_actor_scale3d(unreal.Vector(800.0, 800.0, 800.0))
    safe_set(component, "cast_shadow", False)
    safe_set(component, "affect_dynamic_indirect_lighting", False)
    log("HDRI sky dome spawned")
    return dome


def build_clouds():
    """Volumetric clouds using the material instance that ships with the engine.

    The sky was a clean gradient before, which is the single biggest "this is an engine
    default" tell. The engine ships m_SimpleVolumetricCloud_Inst, so no asset work needed.
    """
    cloud = spawn(unreal.VolumetricCloud, (0.0, 0.0, 0.0), label="VolumetricCloud")
    if cloud is None:
        log("could not spawn VolumetricCloud")
        return None

    component = cloud.get_component_by_class(unreal.VolumetricCloudComponent)
    if component is None:
        log("VolumetricCloud has no component")
        return cloud

    instance = unreal.load_asset("/Engine/EngineSky/VolumetricClouds/m_SimpleVolumetricCloud_Inst.m_SimpleVolumetricCloud_Inst")
    if instance is None:
        # Wrong path is the usual cause: it is /Engine/EngineSky/VolumetricClouds/.
        log("volumetric cloud material unavailable")
        return cloud

    safe_set(component, "material", instance)
    # Keep the layer above the play area and thin enough that the sun still reads.
    safe_set(component, "layer_bottom_altitude", 6.0)
    safe_set(component, "layer_height", 4.0)
    safe_set(component, "tracing_max_distance", 12.0)
    log("volumetric clouds ready")
    return cloud


def build_sky_sphere():
    """Classic engine sky sphere (BP_Sky_Sphere): gradient + painted clouds in one actor.

    Used instead of SkyAtmosphere because the engine's volumetric-cloud materials do not
    load in this install (gotcha #40). The blueprint exposes the sky dome material and the
    cloud texture that ships with the engine, so the sky stops being a flat gradient.
    """
    sky_class = unreal.load_class(None, "/Engine/EngineSky/BP_Sky_Sphere.BP_Sky_Sphere_C")
    if sky_class is None:
        log("BP_Sky_Sphere not found")
        return None

    actor = ACTORS.spawn_actor_from_class(sky_class, unreal.Vector(0.0, 0.0, 0.0),
                                          unreal.Rotator(roll=0.0, pitch=0.0, yaw=0.0))
    if actor is None:
        log("could not spawn BP_Sky_Sphere")
        return None

    actor.set_actor_label("SkySphere")
    log("sky sphere spawned")
    return actor


def build_cloud_plane():
    """A high, slow-panning cloud sheet using the engine's cloud material.

    BP_Sky_Sphere turned out to ignore the sun (no bound light actor) and painted a fixed
    sunset, so the sky is SkyAtmosphere again; clouds come from a translucent plane with
    Engine/EngineSky/M_Sky_Panning_Clouds2_Inst, which does load.
    """
    material = unreal.load_asset("/Engine/EngineSky/M_Sky_Panning_Clouds2_Inst.M_Sky_Panning_Clouds2_Inst")
    if material is None:
        log("cloud material missing, sky has no clouds")
        return None

    # A flat cube rather than a plane: a plane is single-sided and gets culled from below.
    plane = unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
    if plane is None:
        return None

    actor = spawn(unreal.StaticMeshActor, (0.0, 0.0, 3000.0), rotation=(0.0, 0.0, 0.0),
                  label="SM_CloudLayer")
    if actor is None:
        return None

    component = actor.static_mesh_component
    safe_set(component, "mobility", unreal.ComponentMobility.STATIC)
    component.set_static_mesh(plane)
    component.set_material(0, material)
    safe_set(component, "cast_shadow", False)
    # 100 cm plane x 9000 = 9 km across, well above the 14 m bell tower and the sky sphere radius.
    actor.set_actor_scale3d(unreal.Vector(9000.0, 9000.0, 0.02))
    log("cloud layer spawned")
    return actor


TERRAIN_CENTRE = (0.0, -500.0)
TERRAIN_SIZE = 25000.0      # cm across: covers every zone (x +-12500, y -13000..12000)
TERRAIN_STEP = 250.0        # cm per quad (2.5 m)

# The land is flat wherever the player can walk, and rolls outside it: the flat plain is what
# made the scene read as a boxout, but a slope under the village would tilt the paving.
# load_p0_world() replaces this tuple with the zone rectangles from Assets/Map/p0_world.json;
# the values below are only a fallback for a build started without that file.
TERRAIN_FLAT_AREAS = (
    (-3000.0, 3000.0, -11600.0, -5600.0),  # 桃源村
    (-4500.0, 4500.0, -9300.0, -300.0),    # 兰州
    (-6000.0, 6000.0, -6300.0, 5700.0),    # 敦煌
    (-4000.0, 4000.0, 2600.0, 10600.0),    # 秦皇陵
)


def build_terrain(materials):
    """Ground: an actor that rebuilds its own procedural mesh whenever the level loads.

    The heights live in C++ (ALXJGround), not here, because procedural mesh sections are not
    serialised: a mesh built once at build time came back empty as soon as the level was reopened
    or the game was launched straight from disk (the "black ground" bug).
    """
    grass = materials.get("terrain")
    ground_class = unreal.load_class(None, "/Script/LingXuJie.LXJGround")
    if grass is None or ground_class is None:
        log("terrain skipped (material or LXJGround class missing)")
        return

    actor = spawn(ground_class, (0.0, 0.0, 0.0), label="TERRAIN")
    if actor is None:
        log("terrain skipped (LXJGround could not be spawned)")
        return

    actor.set_editor_property("centre", unreal.Vector2D(TERRAIN_CENTRE[0], TERRAIN_CENTRE[1]))
    actor.set_editor_property("size", TERRAIN_SIZE)
    actor.set_editor_property("step", TERRAIN_STEP)
    actor.set_editor_property("ground_material", grass)
    # FVector4 packs a rectangle as (min x, min y, max x, max y) to keep the JSON mapping simple.
    actor.set_editor_property("flat_areas",
                             [unreal.Vector4(x0, y0, x1, y1)
                              for (x0, x1, y0, y1) in TERRAIN_FLAT_AREAS])
    actor.rebuild()
    log("terrain: LXJGround %.0f cm across, %d flat areas" % (TERRAIN_SIZE, len(TERRAIN_FLAT_AREAS)))



def kerb_ring(material, centre, size, yaw, label):
    """A raised stone kerb around a paved platform.

    Chinese courtyards edge their paving with a kerb course; besides being right for the style it
    is what makes a straight edge read as built rather than as a cut-out.
    """
    half_x = size[0] * 0.5
    half_y = size[1] * 0.5
    width = 0.30          # metres
    top = 15.0            # cm above the ground: 3 cm proud of the paving
    rad = math.radians(yaw)
    cos_y, sin_y = math.cos(rad), math.sin(rad)

    sides = (
        (0.0, half_y + width * 0.5, size[0] + width * 2.0, width),
        (0.0, -(half_y + width * 0.5), size[0] + width * 2.0, width),
        (half_x + width * 0.5, 0.0, width, size[1] + width * 2.0),
        (-(half_x + width * 0.5), 0.0, width, size[1] + width * 2.0),
    )
    built = 0
    for index, (local_x, local_y, side_x, side_y) in enumerate(sides):
        world_x = centre[0] + (local_x * cos_y - local_y * sin_y) * 100.0
        world_y = centre[1] + (local_x * sin_y + local_y * cos_y) * 100.0
        actor = ground_patch("%s_Kerb_%d" % (label, index), material,
                             (world_x, world_y), (side_x, side_y),
                             z=top - 4.0, yaw=yaw, thickness=0.08)
        if actor is not None:
            built += 1
    return built


GATE_LAYOUT = os.path.join("Assets", "Gate", "geonchunmun_gate.json")
GATE_PLACEMENT = (0.0, -8200.0)     # the gate is the south entrance, per Docs/P0-LAYOUT.md
GATE_YAW = 0.0
BOSS_PLACEMENT = (0.0, -700.0)      # training ground stone platform
MAIN_ROAD = ((0.0, -7900.0), (0.0, -700.0), 1000.0, 800.0)   # from, to, half width, slab height

# The pavilion garden (KCISA Seyeonjeong) came as a finished scene too: pond, stone revetment,
# rocks, planting and the pavilion itself. Its layout is harvested the same way as the gate.
GARDEN_LAYOUT = os.path.join("Assets", "Village", "seyeonjeong_layout.json")
GARDEN_PLACEMENT = (150.0, -4650.0)   # village pond, per Docs/P0-LAYOUT.md
GARDEN_YAW = 0.0
# The harvested z is relative to the *lowest* mesh of the demo map (its pond floor), so every
# piece lands ~one pond-depth too high and the rocks read as floating. Drop them by that depth.
GARDEN_Z_OFFSET = -35.0
# Per-actor line-trace snapping; off until the KismetSystemLibrary signature is right
# (actors_to_ignore must be an array - passing a bool broke the build).
TRACE_SNAP = False


def place_layout(relative_json, placement, yaw, label_prefix, exclude=(), ground_material=None,
                 z_offset=0.0):
    """Rebuild a harvested layout file (mesh path + transform per actor) at a world position."""
    path = os.path.join(unreal.Paths.project_dir(), relative_json)
    if not os.path.isfile(path):
        log("%s skipped (layout file missing: %s)" % (label_prefix, relative_json))
        return 0

    import json
    # utf-8-sig: PowerShell 5.1 writes a BOM with -Encoding UTF8.
    with open(path, "r", encoding="utf-8-sig") as handle:
        records = json.load(handle)
    if not records:
        log("%s skipped (layout file empty)" % label_prefix)
        return 0

    rad = math.radians(yaw)
    cos_y, sin_y = math.cos(rad), math.sin(rad)
    placed = 0
    missing = 0
    reskinned = 0
    skipped = 0
    snapped = 0

    def is_ground(mesh_name):
        return "SM_Ground_" in mesh_name or "SM_Floor" in mesh_name

    # Two passes: bank/terrace meshes first (they are the surface to land on), then everything
    # else gets a downward line trace, so each rock and tree sits on whatever is under it.
    ordered = sorted(records,
                     key=lambda r: 0 if is_ground(r["mesh"].rsplit("/", 1)[-1]) else 1)
    for record in ordered:
        mesh = unreal.load_asset(record["mesh"])
        if mesh is None:
            missing += 1
            continue
        name = record["mesh"].rsplit("/", 1)[-1]
        if any(token in name for token in exclude):
            skipped += 1
            continue
        local_x = record["x"]
        local_y = record["y"]
        world_x = placement[0] + local_x * cos_y - local_y * sin_y
        world_y = placement[1] + local_x * sin_y + local_y * cos_y
        actor = spawn(unreal.StaticMeshActor, (world_x, world_y, record["z"] + z_offset),
                      rotation=(record["roll"], record["pitch"], record["yaw"] + yaw),
                      label="%s_%03d" % (label_prefix, placed))
        if actor is None:
            continue
        component = actor.static_mesh_component
        safe_set(component, "mobility", unreal.ComponentMobility.STATIC)
        component.set_static_mesh(mesh)
        if ground_material is not None and is_ground(name):
            # The pack's own bank/terrace meshes: keep the geometry (its basin matches the
            # revetment) but swap their dark asphalt material for ours.
            for slot in range(component.get_num_materials()):
                component.set_material(slot, ground_material)
            reskinned += 1
        actor.set_actor_scale3d(unreal.Vector(record["sx"], record["sy"], record["sz"]))
        if TRACE_SNAP and not is_ground(name):
            start = unreal.Vector(world_x, world_y, record["z"] + z_offset + 400.0)
            end = unreal.Vector(world_x, world_y, record["z"] + z_offset - 2000.0)
            hit = unreal.SystemLibrary.line_trace_single(
                ACTORS, start, end, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, False,
                [actor], unreal.DrawDebugTrace.NONE, True)
            if hit:
                location = actor.get_actor_location()
                location.z = hit.location.z
                actor.set_actor_location(location, False, False)
                snapped += 1
        placed += 1

    log("%s: %d pieces placed, %d missing, %d reskinned, %d snapped" % (
        label_prefix, placed, missing, reskinned, snapped))
    return placed


def build_main_road(materials):
    """The one road P0 needs: gate -> village -> training ground, 20 m wide."""
    stone = materials.get("stone")
    if stone is None:
        log("main road skipped (no stone material)")
        return 0
    (x0, y0), (x1, y1), half_width, height = MAIN_ROAD
    length = math.hypot(x1 - x0, y1 - y0)
    yaw = math.degrees(math.atan2(y1 - y0, x1 - x0))
    centre = ((x0 + x1) / 2.0, (y0 + y1) / 2.0)
    ground_patch("ROAD", stone, centre, (length / 100.0, half_width * 2.0 / 100.0),
                 z=height, yaw=yaw, thickness=0.02)
    log("main road: %.0f m long at yaw %.0f" % (length / 100.0, yaw))
    return 1


def build_boss_platform(materials):
    """Stone platform for the training-ground boss."""
    stone = materials.get("stone")
    if stone is None:
        log("boss platform skipped (no stone material)")
        return 0
    ground_patch("BOSS_Platform", stone, BOSS_PLACEMENT, (14.0, 14.0), z=40.0, thickness=0.02)
    log("boss platform at %.0f, %.0f" % BOSS_PLACEMENT)
    return 1

def build_gate():
    """Lay out the purchased Geonchunmun gate from a harvested layout file.

    The Fab pack ships as 400+ modular pieces assembled in its own demo map. Rather than guess
    the assembly, Tools/dump_level_layout.py harvests the demo map's mesh transforms, the pieces
    are filtered to the gate family (SM_GCM_*) and centred, and this rebuilds them at our own
    coordinates. Everything else in the level stays procedural.
    """
    return place_layout(GATE_LAYOUT, GATE_PLACEMENT, GATE_YAW, "GATE")


GARDEN_POOL = (150.0, -4650.0, 52.0, 42.0, -10.0)   # centre x, y, size x, y (m), water height (cm)


def build_garden_water(materials):
    """Fill the pavilion's stone basin with water.

    The pack's own water plane was filtered out with its ground: it belongs to their demo map.
    One slab of our water material inside the revetment walls is enough at this stage - the
    reflection is what sells it, not the shader.
    """
    water = materials.get("water")
    if water is None:
        log("garden water skipped (no water material)")
        return 0
    x, y, size_x, size_y, height = GARDEN_POOL
    actor = ground_patch("GARDEN_Water", water, (x, y), (size_x, size_y), z=height, thickness=0.02)
    log("garden water: %.0f x %.0f m at z=%.0f" % (size_x, size_y, height))
    return 1 if actor is not None else 0


def build_garden(materials):
    """The Seyeonjeong pond garden: pavilion, revetment, rocks and planting in one layout."""
    # Skip the demo map's own ground/water planes: our level supplies terrain and water.
    return place_layout(GARDEN_LAYOUT, GARDEN_PLACEMENT, GARDEN_YAW, "GARDEN",
                        exclude=("Plane",), ground_material=None,
                        z_offset=GARDEN_Z_OFFSET)


def ground_patch(label, material, center, size, z=1.0, yaw=0.0, thickness=0.02):
    """A slab laid over the terrain to break the single-grass-plane look.

    ``thickness`` is in metres and matters more than it looks: a 2 cm slab shows a paper-thin
    edge where it meets the grass, which reads as tape stuck on the floor. Paving gets 12 cm so
    its side faces read as a stone edge instead.
    """
    if material is None:
        return None

    actor = spawn(unreal.StaticMeshActor, (center[0], center[1], z),
                  rotation=(0.0, 0.0, yaw), label=label)
    if actor is None:
        return None

    cube = unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
    component = actor.static_mesh_component
    safe_set(component, "mobility", unreal.ComponentMobility.STATIC)
    component.set_static_mesh(cube)
    component.set_material(0, material)
    # 100 cm cube: size is in metres.
    actor.set_actor_scale3d(unreal.Vector(size[0], size[1], thickness))
    safe_set(component, "cast_shadow", False)
    return actor


# --- Village ground layout -------------------------------------------------------------
# The Polyfork pack used to dress the village (street tiles, rice paddies, fences), and it is
# disabled in the official-assets-only pass - which is why the ground read as one bare plain.
# These tables lay the same places out with procedural slabs instead.
# (label, centre in cm, size in metres, yaw)
VILLAGE_PAVING = (
    # The square around the well: one slab plus a side alley, no longer a 14x14 card.
    ("GND_SquareMain", (300.0, -4300.0), (12.0, 9.0), 0.0),
    ("GND_SquareWestWing", (-800.0, -4450.0), (6.0, 6.0), 8.0),
    # Stone approach to the mountain gate: it ends where the terrace begins (y = -15 m).
    ("GND_GatePath_0", (0.0, -1850.0), (6.0, 5.0), 0.0),
    ("GND_GatePath_1", (30.0, -2350.0), (6.0, 6.0), 4.0),
    ("GND_GatePath_2", (0.0, -2850.0), (6.0, 5.0), 0.0),
    # shrine courtyard in front of the altars
    ("GND_ShrineCourt", (0.0, 4500.0), (22.0, 16.0), 0.0),
)

# Packed earth sits 0.2 cm *under* the paving, so where a road runs beneath a paved square the
# overlap is hidden instead of z-fighting.
# Dirt roads are switched off for now: even with the feathered material the rectangles still read
# as colour strips lying on the grass, and there is no blend surface to lay them on yet. The
# entries are kept here so the layout is not lost.
VILLAGE_EARTH = ()
PADDY_CENTRES = ()   # the 12 teal rectangles read as more colour noise than water; water waits
PADDY_SIZE = (4.0, 3.2)


def build_ground_patches(materials):
    """Paving / packed earth / paddies - the ground layer of the village and the shrine."""
    paving = materials.get("stone")
    earth = materials.get("dirt")
    water = materials.get("water")

    # The paved areas are flat slabs again: the individual-cobble version was more "correct" but
    # read worse on screen at this scale, so it stays behind the flag below. No kerb and no raised
    # platform either: a band of anything along the edge reads as tape, so the edge is hidden
    # under spilled stones instead (build_edge_gravel).
    for label, centre, size, yaw in VILLAGE_PAVING:
        ground_patch(label, paving, centre, size, z=1.0, yaw=yaw, thickness=0.02)
    for label, centre, size, yaw in VILLAGE_EARTH:
        # Dirt roads stay almost flush: they are ground, not a platform.
        ground_patch(label, earth, centre, size, z=0.4, yaw=yaw, thickness=0.02)

    # Puddles: a wet dirt road is the cheapest way to make the ground read as weather, not paint.
    for index, centre in enumerate(PUDDLES):
        ground_patch("GND_Puddle_%d" % index, water, centre, (2.6, 1.5), z=1.6, yaw=(index * 37.0) % 90.0)

    paddies = 0
    for index, centre in enumerate(PADDY_CENTRES):
        rim = (PADDY_SIZE[0] + 0.7, PADDY_SIZE[1] + 0.7)
        ground_patch("GND_PaddyRim_%02d" % index, earth, centre, rim, z=2.0)
        if water is not None:
            ground_patch("GND_PaddyWater_%02d" % index, water, centre, PADDY_SIZE, z=7.0)
            paddies += 1

    log("ground patches: %d beds, %d earth, %d paddies" % (
        len(VILLAGE_PAVING), len(VILLAGE_EARTH), paddies))
    build_cobbles(materials)
    # build_edge_gravel(materials)  # the spill read as black crates; no border treatment for now


def _noise(seed, salt):
    """Deterministic 0..1 hash - the layout has to be identical on every rebuild."""
    value = math.sin(seed * 12.9898 + salt * 78.233) * 43758.5453
    return value - math.floor(value)


COBBLE_TILE = (0.70, 0.45)      # metres per stone cell - a hand-laid village paving scale
PUDDLES = ()


def cobble_rect(component, centre, size, yaw, seed_offset=0):
    """Cover one rectangle with individual stone slabs - the centre in cm, the size in metres.

    Stones are laid slightly *oversize* so they butt up against each other: the joints then read
    as the shadow/AO line between two heights instead of as grass showing through a gap. Every
    stone gets its own thickness and a couple of degrees of yaw, which is what kills the "printed
    texture on a card" look.
    """
    tile_x, tile_y = COBBLE_TILE
    cols = max(1, int(round(size[0] / tile_x)))
    rows = max(1, int(round(size[1] / tile_y)))
    cell_x = size[0] / cols
    cell_y = size[1] / rows
    rad = math.radians(yaw)
    cos_y, sin_y = math.cos(rad), math.sin(rad)

    placed = 0
    for row in range(rows):
        # Odd rows are offset by half a stone and get one extra column, otherwise the stagger
        # leaves a ragged gap along one edge.
        stagger = 0.5 * cell_x if row % 2 else 0.0
        columns = cols + 1 if row % 2 else cols
        for col in range(columns):
            key = row * 131 + col + seed_offset * 977
            local_x = (col + 0.5) * cell_x - size[0] * 0.5 + stagger
            local_y = (row + 0.5) * cell_y - size[1] * 0.5
            world_x = centre[0] + (local_x * cos_y - local_y * sin_y) * 100.0
            world_y = centre[1] + (local_x * sin_y + local_y * cos_y) * 100.0
            thickness = 0.08 + 0.03 * _noise(key, 3)
            scale_x = cell_x * (0.94 + 0.05 * _noise(key, 4))
            scale_y = cell_y * (0.94 + 0.05 * _noise(key, 5))
            transform = unreal.Transform(
                location=unreal.Vector(world_x, world_y, 5.5 + 4.0 * _noise(key, 7)),
                rotation=unreal.Rotator(roll=0.0, pitch=0.0,
                                        yaw=yaw + (_noise(key, 6) - 0.5) * 8.0),
                scale=unreal.Vector(scale_x, scale_y, thickness))
            component.add_instance(transform, True)
            placed += 1
    return placed


def gravel_ring(component, centre, size, yaw, seed_offset=0, count=22, min_size=0.05, size_range=0.09):
    """Small stones spilling out of a paved edge - the gravel shoulder a road rubs into grass."""
    rad = math.radians(yaw)
    cos_y, sin_y = math.cos(rad), math.sin(rad)
    half_x, half_y = size[0] * 0.5, size[1] * 0.5
    placed = 0
    for side in range(4):
        for index in range(count):
            key = side * 311 + index + seed_offset * 733
            along = _noise(key, 1) - 0.5
            out = 0.35 + 0.9 * _noise(key, 2)
            if side in (0, 1):
                local_x = along * size[0]
                local_y = (half_y + out) * (1.0 if side == 0 else -1.0)
            else:
                local_y = along * size[1]
                local_x = (half_x + out) * (1.0 if side == 2 else -1.0)
            world_x = centre[0] + (local_x * cos_y - local_y * sin_y) * 100.0
            world_y = centre[1] + (local_x * sin_y + local_y * cos_y) * 100.0
            size_scale = min_size + size_range * _noise(key, 3)
            transform = unreal.Transform(
                location=unreal.Vector(world_x, world_y, 1.5 + size_scale * 20.0),
                rotation=unreal.Rotator(roll=0.0, pitch=0.0, yaw=_noise(key, 4) * 360.0),
                scale=unreal.Vector(size_scale, size_scale * (0.7 + 0.5 * _noise(key, 5)),
                                    size_scale * 0.7))
            component.add_instance(transform, True)
            placed += 1
    return placed


COBBLES_ENABLED = False   # individual stones lost to the slab look on screen; kept for reference


def build_edge_gravel(materials):
    """Spill stones along the paved edges.

    A straight material boundary on the ground always reads as tape, whatever colour it is. The
    fix is not a border band but irregularity: stones tumbling out of the paving into the grass,
    which is also what a worn village square actually looks like.
    """
    stone = materials.get("stone")
    slab_mesh = unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
    stone_class = unreal.load_class(None, "/Game/Props/BP_StoneField.BP_StoneField_C")
    if stone is None or slab_mesh is None or stone_class is None:
        log("edge gravel skipped (no stone material / mesh / BP_StoneField)")
        return

    actor = spawn(stone_class, (0.0, 0.0, 0.0), label="EDGE_GRAVEL")
    component = actor.get_component_by_class(unreal.InstancedStaticMeshComponent) if actor else None
    if component is None:
        log("edge gravel skipped (no ISM on BP_StoneField)")
        return
    component.set_static_mesh(slab_mesh)
    for slot in range(component.get_num_materials()):
        component.set_material(slot, stone)

    placed = 0
    for index, (_label, centre, size, yaw) in enumerate(VILLAGE_PAVING):
        placed += gravel_ring(component, centre, size, yaw, seed_offset=index + 1,
                              count=70, min_size=0.10, size_range=0.22)
    log("edge gravel: %d stones" % placed)


def build_cobbles(materials):
    """Lay the paved areas stone by stone, plus a gravel shoulder - one instanced component."""
    if not COBBLES_ENABLED:
        return
    stone = materials.get("stone")
    slab_mesh = unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
    cobble_class = unreal.load_class(None, "/Game/Props/BP_StoneField.BP_StoneField_C")
    if stone is None or slab_mesh is None:
        log("cobbles skipped (no stone material or cube mesh)")
        return
    if cobble_class is None:
        log("cobbles skipped (BP_StoneField missing - run Tools/make_stone_bp.py in the editor)")
        return

    actor = spawn(cobble_class, (0.0, 0.0, 0.0), label="COBBLE_FIELD")
    component = actor.get_component_by_class(unreal.InstancedStaticMeshComponent) if actor else None
    if component is None:
        log("cobbles skipped (no InstancedStaticMeshComponent on BP_StoneField)")
        return

    component.set_static_mesh(slab_mesh)
    for slot in range(component.get_num_materials()):
        component.set_material(slot, stone)

    stones = 0
    gravel = 0
    for index, (label, centre, size, yaw) in enumerate(VILLAGE_PAVING):
        stones += cobble_rect(component, centre, size, yaw, seed_offset=index + 1)
        gravel += gravel_ring(component, centre, size, yaw, seed_offset=index + 1)
    log("cobbles: %d stones, %d gravel in COBBLE_FIELD" % (stones, gravel))


def make_decal_material(name, texture_set, tint=(1.0, 1.0, 1.0)):
    """Deferred-decal material: texture colour + its alpha as opacity.

    Decals are how a scene gets "old": moss at wall bases, dirt under the eaves, worn paths.
    """
    path = MATERIAL_DIR + "/" + name
    if EDITOR_ASSETS.does_asset_exist(path):
        return unreal.load_asset(path)

    diffuse = ensure_texture(texture_set, "diff", is_linear=False)
    if diffuse is None:
        log("no diffuse for decal " + name)
        return None

    material = ASSET_TOOLS.create_asset(name, MATERIAL_DIR, unreal.Material, unreal.MaterialFactoryNew())
    if material is None:
        return None

    safe_set(material, "material_domain", unreal.MaterialDomain.MD_DEFERRED_DECAL)
    safe_set(material, "blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)

    coords = MATERIAL_EDITING.create_material_expression(
        material, unreal.MaterialExpressionTextureCoordinate, -700, 0)
    safe_set(coords, "u_tiling", 1.0)
    safe_set(coords, "v_tiling", 1.0)

    sample = MATERIAL_EDITING.create_material_expression(
        material, unreal.MaterialExpressionTextureSample, -460, 0)
    safe_set(sample, "texture", diffuse)
    MATERIAL_EDITING.connect_material_expressions(coords, "", sample, "UVs")

    tint_expr = MATERIAL_EDITING.create_material_expression(
        material, unreal.MaterialExpressionConstant3Vector, -460, 220)
    tint_expr.set_editor_property("constant", unreal.LinearColor(tint[0], tint[1], tint[2], 1.0))
    multiply = MATERIAL_EDITING.create_material_expression(
        material, unreal.MaterialExpressionMultiply, -220, 80)
    MATERIAL_EDITING.connect_material_expressions(sample, "RGB", multiply, "A")
    MATERIAL_EDITING.connect_material_expressions(tint_expr, "", multiply, "B")
    MATERIAL_EDITING.connect_material_property(multiply, "", unreal.MaterialProperty.MP_BASE_COLOR)

    # Opacity from the texture's alpha, scaled down so patches blend instead of covering.
    opacity = MATERIAL_EDITING.create_material_expression(
        material, unreal.MaterialExpressionMultiply, -220, 260)
    safe_set(opacity, "const_b", 0.75)
    MATERIAL_EDITING.connect_material_expressions(sample, "A", opacity, "A")
    MATERIAL_EDITING.connect_material_property(opacity, "", unreal.MaterialProperty.MP_OPACITY)

    MATERIAL_EDITING.recompile_material(material)
    EDITOR_ASSETS.save_asset(path)
    log("decal material ready: " + path)
    return material


SPAWN_DECALS = False   # the source JPGs have no alpha, so every decal was a solid colour strip


def build_decals(materials):
    """Moss and dirt decals at wall bases, under the eaves and around the well."""
    if not SPAWN_DECALS:
        log("decals skipped (opaque source textures read as paper tape on the ground)")
        return
    moss = make_decal_material("M_Decal_Moss", "grass_ground", tint=(0.30, 0.38, 0.24))
    dirt = make_decal_material("M_Decal_Dirt", "clay_plaster", tint=(0.72, 0.62, 0.48))
    if moss is None and dirt is None:
        return

    # Borders: moss creeps over a paved edge first, so a decal straddling the seam is what stops
    # a slab from looking like a card cut out of the grass. Sizes below are in metres.
    edges = []
    for x in (-160.0, 760.0):
        edges.append((moss, (x, -4760.0, 0.0), (3.0, 1.2, 2.0), 0.0))
        edges.append((moss, (x, -3840.0, 0.0), (3.0, 1.2, 2.0), 0.0))
    for y in (-4560.0, -4040.0):
        edges.append((moss, (-320.0, y, 0.0), (1.2, 3.0, 2.0), 0.0))
        edges.append((moss, (920.0, y, 0.0), (1.2, 2.6, 2.0), 0.0))
    for y in (-5250.0, -4700.0, -3900.0):
        edges.append((dirt, (-430.0, y, 0.0), (1.2, 3.0, 2.0), 0.0))

    decals = (
        # moss where walls meet the ground
        (moss, (-2350.0, -4050.0, 0.0), (6.0, 3.0, 2.0), 90.0),        (moss, (2400.0, -4250.0, 0.0), (6.0, 3.0, 2.0), 270.0),
        (moss, (-2350.0, -3100.0, 0.0), (6.0, 3.0, 2.0), 90.0),
        (moss, (-1200.0, 4200.0, 0.0), (5.0, 2.5, 2.0), 90.0),
        (moss, (1200.0, 4200.0, 0.0), (5.0, 2.5, 2.0), 90.0),
        # dirt around the well and the street junction
        (dirt, (420.0, -4250.0, 0.0), (5.0, 5.0, 2.0), 15.0),
        (dirt, (520.0, -5050.0, 0.0), (4.0, 4.0, 2.0), 0.0),
        (dirt, (0.0, 4750.0, 0.0), (7.0, 5.0, 2.0), 0.0),
        # worn dirt where the street meets the plaza
        (dirt, (0.0, -2600.0, 0.0), (8.0, 6.0, 2.0), 0.0),
    ) + tuple(edges)

    spawned = 0
    for material, location, size, yaw in decals:
        if material is None:
            continue
        actor = spawn(unreal.DecalActor, location, rotation=(0.0, -90.0, yaw), label="DECAL_%d" % spawned)
        if actor is None:
            continue
        component = actor.get_component_by_class(unreal.DecalComponent)
        if component is None:
            continue
        safe_set(component, "decal_material", material)
        # DecalSize is in centimetres, but the tables above are written in metres - passing the
        # metre values straight through made every decal a 6 cm speck nobody could see.
        safe_set(component, "decal_size",
                 unreal.Vector(size[0] * 100.0, size[1] * 100.0, size[2] * 100.0))
        spawned += 1

    log("decals spawned: %d" % spawned)


BULRUSH_MESHES = (
    "/Game/Megaplant_Library/Plant_Bulrush/Plant_Bulrush_01/Plant_Common_Bulrush_01_A",
    "/Game/Megaplant_Library/Plant_Bulrush/Plant_Bulrush_01/Plant_Common_Bulrush_01_B",
    "/Game/Megaplant_Library/Plant_Bulrush/Plant_Bulrush_01/Plant_Common_Bulrush_01_C",
    "/Game/Megaplant_Library/Plant_Bulrush/Plant_Bulrush_01/Plant_Common_Bulrush_01_D",
)
BULRUSH_MATERIAL = "/Game/Megaplant_Library/Plant_Bulrush/Materials/MI_Bulrush_01_Foliage"

# Marsh reeds around the paddies and along the shrine walls: real Quixel Megaplants geometry
# instead of the placeholder reeds we were using.
BULRUSH_SPOTS = (
    ((-1180.0, -4750.0, 0.0), 15.0, 1.05), ((760.0, -4700.0, 0.0), 95.0, 0.95),
    ((-1560.0, -3820.0, 0.0), 130.0, 1.10), ((1520.0, -3760.0, 0.0), 250.0, 1.00),
    ((-880.0, -3350.0, 0.0), 45.0, 0.90), ((980.0, -3300.0, 0.0), 175.0, 1.05),
    ((-1320.0, -2350.0, 0.0), 210.0, 1.00), ((1380.0, -2280.0, 0.0), 30.0, 0.95),
    ((-1260.0, 4050.0, 0.0), 80.0, 1.00), ((1240.0, 4120.0, 0.0), 200.0, 1.05),
    ((-620.0, 4620.0, 0.0), 155.0, 0.95), ((640.0, 4680.0, 0.0), 285.0, 1.00),
    ((-1180.0, 5150.0, 0.0), 25.0, 1.10), ((1120.0, 5200.0, 0.0), 120.0, 1.00),
    ((-1520.0, -1500.0, 0.0), 65.0, 0.95), ((1580.0, -1420.0, 0.0), 215.0, 1.05),
)


# Megaplants are procedural vegetation: the Plant_* skeletal meshes carry a skeleton and bounds
# but no baked triangles, they are generated by the Procedural Vegetation Editor at runtime.
# A plain SkeletalMeshActor therefore renders nothing (verified: bounds 1.3 m, no visible
# geometry in the viewport), so this stays off until we wire the PVE workflow properly.
SPAWN_MEGAPLANT_REEDS = True


BULRUSH_CLUSTERS = (
    # (centre x, centre y, plants, radius cm, base yaw)
    (-1180.0, -4750.0, 4, 380.0, 15.0),
    (760.0, -4700.0, 4, 340.0, 95.0),
    (-880.0, -3350.0, 3, 300.0, 45.0),
    (980.0, -3300.0, 3, 300.0, 175.0),
    (-620.0, 4620.0, 3, 260.0, 155.0),
    (640.0, 4680.0, 3, 260.0, 285.0),
)

# Reeds follow the field ridges and the water channels, so they read as bands rather than
# isolated tufts: (start x, start y, end x, end y, plants, lateral jitter cm).
BULRUSH_BANDS = (
    (-1620.0, -4900.0, -1620.0, -4180.0, 8, 90.0),
    (1500.0, -4860.0, 1500.0, -4120.0, 8, 90.0),
    (-1520.0, -3700.0, -760.0, -3700.0, 7, 80.0),
    (760.0, -3640.0, 1480.0, -3640.0, 7, 80.0),
    (-1220.0, 4020.0, -1220.0, 4520.0, 6, 70.0),
    (1220.0, 4060.0, 1220.0, 4560.0, 6, 70.0),
)


def _bulrush_spots():
    """Deterministic scatter: no random module, so the level rebuilds identically."""
    spots = []
    for cluster_index, (cx, cy, count, radius, base_yaw) in enumerate(BULRUSH_CLUSTERS):
        for i in range(count):
            angle = math.radians(base_yaw + (i * 137.5) % 360.0)
            dist = radius * (0.35 + 0.65 * (((i * 7 + cluster_index * 3) % 5) / 5.0))
            x = cx + math.cos(angle) * dist
            y = cy + math.sin(angle) * dist
            yaw = (base_yaw + i * 53.0) % 360.0
            scale = 0.85 + 0.30 * (((i * 3 + cluster_index) % 4) / 3.0)
            spots.append(((x, y, 0.0), yaw, scale))

    for band_index, (x1, y1, x2, y2, count, jitter) in enumerate(BULRUSH_BANDS):
        dx = x2 - x1
        dy = y2 - y1
        length = math.hypot(dx, dy) or 1.0
        # unit normal, used to push plants off the exact line so the band looks grown, not planted
        nx = -dy / length
        ny = dx / length
        for i in range(count):
            t = (i + 0.5) / count
            offset = jitter * math.sin((i * 2.399 + band_index) * 3.1)
            x = x1 + dx * t + nx * offset
            y = y1 + dy * t + ny * offset
            yaw = (band_index * 47.0 + i * 61.0) % 360.0
            scale = 0.80 + 0.35 * (((i * 5 + band_index * 2) % 4) / 3.0)
            spots.append(((x, y, 0.0), yaw, scale))
    return spots


def build_foliage():
    """Megaplants reeds (skeletal meshes) around the paddies and the shrine."""
    if not SPAWN_MEGAPLANT_REEDS:
        log("megaplant reeds skipped (procedural meshes need the PVE workflow)")
        return
    material = unreal.load_asset(BULRUSH_MATERIAL)
    spawned = 0
    for index, (location, yaw, scale) in enumerate(_bulrush_spots()):
        if _in_paving(location[0], location[1], 120.0):
            continue
        mesh_path = BULRUSH_MESHES[index % len(BULRUSH_MESHES)]
        actor = spawn_skeletal("REEDS_%02d" % index, mesh_path, location, yaw, scale, material)
        if actor is None:
            continue
        spawned += 1
        if index == 0:
            # One diagnostic line is enough to tell "mesh loaded but tiny/invisible" apart
            # from "actor never got a mesh"; the editor captures were ambiguous.
            component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
            origin, extent = actor.get_actor_bounds(False)
            log("reed debug: mesh=%s loc=%s scale=%s origin=%s extent=%s" % (
                mesh_path, actor.get_actor_location(), scale, origin, extent))
    log("megaplants reeds spawned: %d" % spawned)


MEGASCANS_SURFACES = {
    # Friendly name -> material instance shipped with a Megascans surface from Fab.
    "roof": "/Game/Fab/Megascans/Surfaces/Roof_Tiles_tk4gcgldy/Medium/"
            "tk4gcgldy_tier_2/Materials/MI_tk4gcgldy",
    "roof_red": "/Game/Fab/Megascans/Surfaces/Red_Roof_Tiles_tfqnfggs/Medium/"
                "tfqnfggs_tier_2/Materials/MI_tfqnfggs",
    "wood": "/Game/Fab/Megascans/Surfaces/Wood_Planks_throbglfw/Medium/"
            "throbglfw_tier_2/Materials/MI_throbglfw",
}


def load_megascans(name):
    """Return a Megascans material instance if that surface is present, else None.

    Megascans surfaces arrive as MI_* instances over the shared M_MS_Srf master material, so
    they bring their own 2K base/normal/ORM sets - far better than the flat tiled placeholders.
    """
    path = MEGASCANS_SURFACES.get(name)
    if not path:
        return None
    material = unreal.load_asset(path)
    if material is None:
        log("megascans surface not installed: " + path)
        return None
    log("using megascans surface: " + name)
    return material


# Second official plant: Quixel Megaplants Bracken Fern (variants A-D from the same pack).
FERN_MESHES = (
    "/Game/Megaplant_Library/Plant_Bracken_Fern/Plant_Bracken_Fern_01/Plant_Bracken_Fern_01_A",
    "/Game/Megaplant_Library/Plant_Bracken_Fern/Plant_Bracken_Fern_01/Plant_Bracken_Fern_01_B",
    "/Game/Megaplant_Library/Plant_Bracken_Fern/Plant_Bracken_Fern_01/Plant_Bracken_Fern_01_C",
    "/Game/Megaplant_Library/Plant_Bracken_Fern/Plant_Bracken_Fern_01/Plant_Bracken_Fern_01_D",
)
FERN_MATERIAL = "/Game/Megaplant_Library/Plant_Bracken_Fern/Materials/MI_Bracken_Fern_01"

# Ferns prefer shade: house walls, the shrine walls and the tree line rather than open fields.
FERN_SPOTS = (
    ((-2500.0, -4050.0, 0.0), 20.0, 0.9), ((-2450.0, -3900.0, 0.0), 115.0, 1.05),
    ((-2300.0, -3150.0, 0.0), 200.0, 0.95), ((2300.0, -4200.0, 0.0), 40.0, 1.0),
    ((2420.0, -4050.0, 0.0), 150.0, 0.9), ((2250.0, -3050.0, 0.0), 285.0, 1.1),
    ((-1250.0, 3650.0, 0.0), 60.0, 1.0), ((1280.0, 3720.0, 0.0), 210.0, 0.95),
    ((-1180.0, 5250.0, 0.0), 15.0, 1.05), ((1150.0, 5300.0, 0.0), 175.0, 0.9),
    ((-1650.0, -1800.0, 0.0), 90.0, 1.0), ((1700.0, -1650.0, 0.0), 250.0, 1.05),
)


def build_ferns():
    """Bracken ferns hugging walls and tree lines - the shaded half of the planting."""
    material = unreal.load_asset(FERN_MATERIAL)
    if not SPAWN_MEGAPLANT_REEDS:
        log("bracken ferns skipped (same Nanite-foliage flag as the reeds)")
        return
    spawned = 0
    for index, (location, yaw, scale) in enumerate(FERN_SPOTS):
        mesh_path = FERN_MESHES[index % len(FERN_MESHES)]
        actor = spawn_skeletal("FERN_%02d" % index, mesh_path, location, yaw, scale, material)
        if actor is not None:
            spawned += 1
    log("bracken ferns spawned: %d" % spawned)


# Third official plant: Quixel Megaplants Giant Bamboo (a small grove, not a forest).
BAMBOO_MESHES = (
    "/Game/Megaplant_Library/Tree_Giant_Bamboo/Tree_Giant_Bamboo_01/Tree_Giant_Bamboo_01_A",
    "/Game/Megaplant_Library/Tree_Giant_Bamboo/Tree_Giant_Bamboo_01/Tree_Giant_Bamboo_01_B",
    "/Game/Megaplant_Library/Tree_Giant_Bamboo/Tree_Giant_Bamboo_01/Tree_Giant_Bamboo_01_C",
)

BAMBOO_GROVE = (
    ((-2050.0, -5150.0, 0.0), 20.0, 1.0), ((-1880.0, -5230.0, 0.0), 100.0, 1.15),
    ((-1750.0, -5080.0, 0.0), 210.0, 0.9), ((-2140.0, -4980.0, 0.0), 145.0, 1.05),
    ((2080.0, -5050.0, 0.0), 60.0, 1.1), ((2260.0, -5150.0, 0.0), 175.0, 0.95),
    ((-1600.0, -2600.0, 0.0), 250.0, 1.0), ((1700.0, -2500.0, 0.0), 30.0, 1.05),
)


def build_bamboo():
    """A few Giant Bamboo clumps at the village edges - the vertical accent the scene lacked."""
    if not SPAWN_MEGAPLANT_REEDS:
        log("giant bamboo skipped (same Nanite-foliage flag as the reeds)")
        return
    spawned = 0
    for index, (location, yaw, scale) in enumerate(BAMBOO_GROVE):
        mesh_path = BAMBOO_MESHES[index % len(BAMBOO_MESHES)]
        actor = spawn_skeletal("BAMBOO_%02d" % index, mesh_path, location, yaw, scale)
        if actor is not None:
            spawned += 1
    log("giant bamboo spawned: %d" % spawned)


# Official Megascans plant: Tundra Grass (9 static-mesh variants + one material instance).
GRASS_MESHES = tuple(
    "/Game/Fab/Megascans/Plants/Tundra_Grass_wk2oaeyqx/Medium/wk2oaeyqx_tier_2/"
    "StaticMeshes/SM_wk2oaeyqx_Var%s" % suffix for suffix in "ABCDEFGHI"
)
GRASS_MATERIAL = ("/Game/Fab/Megascans/Plants/Tundra_Grass_wk2oaeyqx/Medium/"
                  "wk2oaeyqx_tier_2/Materials/MI_wk2oaeyqx")

# Ground cover along the street verges, the paddies and the shrine approach.
GRASS_PATCHES = (
    ((-700.0, -4700.0, 0.0), 8, 900.0), ((700.0, -4650.0, 0.0), 8, 900.0),
    ((-900.0, -3600.0, 0.0), 7, 800.0), ((950.0, -3550.0, 0.0), 7, 800.0),
    ((-800.0, 3900.0, 0.0), 6, 700.0), ((850.0, 3950.0, 0.0), 6, 700.0),
    ((0.0, -2950.0, 0.0), 6, 900.0),
    # Road verges: bare ground either side of the street read as a mown field. These clumps run
    # along the dirt edges, so the street is bounded by growth instead of by a colour change.
    ((-470.0, -5000.0, 0.0), 9, 520.0), ((470.0, -4400.0, 0.0), 9, 520.0),
    ((-470.0, -3900.0, 0.0), 8, 500.0), ((520.0, -3350.0, 0.0), 8, 480.0),
)


def _in_paving(x, y, margin=0.0):
    """True when a point falls on a paved rectangle - plants must not grow out of the stone."""
    for (_label, centre, size, _yaw) in VILLAGE_PAVING:
        if (abs(x - centre[0]) <= size[0] * 50.0 + margin
                and abs(y - centre[1]) <= size[1] * 50.0 + margin):
            return True
    return False


def build_grass():
    """Tundra Grass batched into one InstancedStaticMeshComponent.

    Instanced Foliage is unreachable from Python, but Tools/make_grass_bp.py creates
    BP_GrassField (an Actor whose root component is an InstancedStaticMeshComponent), so the
    level spawns that blueprint and feeds it instances: one draw call for all 48 clumps.
    """
    if not SPAWN_MEGAPLANT_REEDS:
        log("tundra grass skipped (same flag as the reeds)")
        return

    transforms = []
    for patch_index, (centre, count, radius) in enumerate(GRASS_PATCHES):
        for i in range(count):
            angle = math.radians((patch_index * 61.0 + i * 137.5) % 360.0)
            dist = radius * (0.3 + 0.7 * (((i * 3 + patch_index) % 5) / 5.0))
            scale = 0.9 + 0.35 * (((i * 2 + patch_index) % 4) / 3.0)
            gx = centre[0] + math.cos(angle) * dist
            gy = centre[1] + math.sin(angle) * dist
            if _in_paving(gx, gy, 80.0):
                continue
            transforms.append(unreal.Transform(
                location=unreal.Vector(gx, gy, 0.0),
                rotation=unreal.Rotator(roll=0.0, pitch=0.0,
                                        yaw=(patch_index * 37.0 + i * 53.0) % 360.0),
                scale=unreal.Vector(scale, scale, scale)))

    mesh = unreal.load_asset(GRASS_MESHES[0])
    material = unreal.load_asset(GRASS_MATERIAL)
    if mesh is None:
        log("tundra grass mesh missing")
        return

    grass_class = unreal.load_class(None, "/Game/Props/BP_GrassField.BP_GrassField_C")
    if grass_class is not None:
        actor = spawn(grass_class, (0.0, 0.0, 0.0), label="GRASS_INSTANCES")
        component = actor.get_component_by_class(unreal.InstancedStaticMeshComponent) if actor else None
        if component is not None:
            component.set_static_mesh(mesh)
            if material is not None:
                # The grass mesh has a foliage slot *and* a billboard slot. Setting only slot 0
                # left the billboard LOD on the default material - those were the white paper
                # scraps scattered over the ground in the distance.
                for slot in range(component.get_num_materials()):
                    component.set_material(slot, material)
            added = 0
            for transform in transforms:
                try:
                    component.add_instance(transform, True)
                    added += 1
                except Exception as exc:  # noqa: BLE001
                    log("add_instance failed: %s" % exc)
                    break
            log("tundra grass instances: %d in BP_GrassField" % added)
            return

    log("BP_GrassField missing, falling back to per-actor clumps")
    spawned = 0
    for index, transform in enumerate(transforms):
        actor = block((transform.translation.x, transform.translation.y, 0.0),
                      (transform.scale3d.x, transform.scale3d.x, transform.scale3d.x),
                      material, "GRASS_%03d" % index, mesh=mesh)
        if actor is not None:
            spawned += 1
    log("tundra grass clumps spawned (fallback): %d" % spawned)


def box(location, scale, material, label, mesh=None, roll=0.0, yaw=0.0):
    """A cube with rotation - the roof slabs need a tilt, block() cannot express that."""
    actor = block(location, scale, material, label, mesh=mesh)
    if actor is not None and (roll or yaw):
        actor.set_actor_rotation(unreal.Rotator(roll=roll, pitch=0.0, yaw=yaw), False)
    return actor


# Chinese-style village houses built from official/material-only parts: stone plinth, rammed
# earth walls, tiled gable roof, timber posts and a dark door. (x, y, width, depth, wall height,
# roof pitch degrees, yaw)
HOUSES = (
    (-1450.0, -4750.0, 7.0, 5.4, 3.2, 26.0, 0.0),
    (-1450.0, -3950.0, 6.4, 5.0, 3.0, 26.0, 0.0),
    (-1450.0, -3150.0, 7.2, 5.6, 3.4, 28.0, 0.0),
    (1450.0, -4800.0, 6.8, 5.2, 3.1, 26.0, 180.0),
    (1450.0, -4000.0, 7.0, 5.4, 3.3, 27.0, 180.0),
    (1450.0, -3200.0, 6.2, 4.8, 3.0, 25.0, 180.0),
)


USE_CURVED_ROOF = False  # procedural curve is WIP: the generated topology is broken
# (big stray quads). Slab gable is the shipping look until the mesh is rebuilt from a proper
# MeshDescription or a verified PMC grid.


def build_curved_roof(centre_x, centre_y, ridge_z, width, depth, pitch, roof_material, yaw=0.0,
                      upturn=0.85, flare=0.55, nu=12, nv=8):
    """A curved Chinese roof surface: concave sag, upturned corners and a flared eave.

    Cubes cannot express this silhouette, so the surface is generated as a procedural mesh
    (BP_CurvedRoof owns a ProceduralMeshComponent) and handed to the renderer as one section.
    """
    roof_class = unreal.load_class(None, "/Game/Props/BP_CurvedRoof.BP_CurvedRoof_C")
    if roof_class is None:
        log("BP_CurvedRoof missing - falling back to flat slabs")
        return None

    actor = spawn(roof_class, (centre_x, centre_y, 0.0), rotation=(0.0, 0.0, yaw),
                  label="ROOF_Curved")
    if actor is None:
        return None
    component = actor.get_component_by_class(unreal.ProceduralMeshComponent)
    if component is None:
        log("BP_CurvedRoof has no ProceduralMeshComponent")
        return actor

    theta = math.radians(pitch)
    half_depth = depth * 0.5 + 0.9
    drop = half_depth * math.tan(theta)

    vertices = []
    normals = []
    uvs = []
    triangles = []
    for side in (-1, 1):
        base = len(vertices)
        for i in range(nu + 1):
            ux = (i / nu - 0.5) * 2.0
            for j in range(nv + 1):
                v = j / nv
                sag = drop * (v ** 1.7)
                lift = upturn * 100.0 * ((abs(ux)) ** 3) * (v ** 4)
                # Local space: the actor transform carries the yaw, otherwise yaw 90 houses get it twice.
                x = ux * (width * 0.5 + flare * (v ** 2))
                y = side * half_depth * v
                z = ridge_z - sag + lift
                vertices.append(unreal.Vector(x, y, z))
                slope = -side * math.sin(theta) * (0.35 + 0.65 * v)
                length = math.sqrt(1.0 + slope * slope)
                normals.append(unreal.Vector(0.0, slope / length, 1.0 / length))
                uvs.append(unreal.Vector2D(x / 220.0, (ridge_z - z) / 220.0))
        for i in range(nu):
            for j in range(nv):
                a = base + i * (nv + 1) + j
                b = a + 1
                c = a + (nv + 1)
                d = c + 1
                if side > 0:
                    triangles.extend([a, c, b, b, c, d])
                else:
                    triangles.extend([a, b, c, b, d, c])

    try:
        component.create_mesh_section(0, vertices, triangles, normals, uvs, [], [], False)
        component.set_material(0, roof_material)
    except Exception as exc:  # noqa: BLE001 - signature changes between versions
        log("create_mesh_section failed: %s" % exc)
        return actor
    return actor


def build_house(centre_x, centre_y, width, depth, wall_height, pitch, yaw, materials):
    """One Chinese village house: stone plinth, rammed-earth walls, timber posts, lattice
    windows, a door with a stone step, and a tiled gable roof with closed gable ends."""
    stone = materials.get("stone")
    wall = materials.get("wall")
    roof = materials.get("roof")
    wood = materials.get("wood")
    if roof is None:
        log("no roof material - houses need the Megascans roof surface")
        return 0

    plinth_h = 0.5
    box((centre_x, centre_y, plinth_h * 50.0),
        (width + 1.0, depth + 1.0, plinth_h), stone, "HOUSE_Plinth")

    wall_base = plinth_h * 100.0
    box((centre_x, centre_y, wall_base + wall_height * 50.0),
        (width, depth, wall_height), wall, "HOUSE_Walls")

    theta = math.radians(pitch)
    eave = 0.9
    half_depth = depth * 0.5 + eave
    slab_len = half_depth / math.cos(theta)
    drop = half_depth * math.tan(theta)
    ridge_z = wall_base + wall_height * 100.0 + drop * 100.0

    # timber corner posts carry the roof, as in a Chinese timber-frame house
    for sx in (-1, 1):
        for sy in (-1, 1):
            box((centre_x + sx * width * 50.0, centre_y + sy * depth * 50.0,
                 wall_base + wall_height * 50.0),
                (0.34, 0.34, wall_height + 0.2), wood, "HOUSE_Post")


    # front face in dark timber: door, two lattice windows, stone doorstep
    face = -1.0 if yaw == 0.0 else 1.0
    face_x = centre_x + face * (width * 50.0 + 1.0)
    box((face_x, centre_y, wall_base + 115.0), (0.22, 1.5, 2.3), wood, "HOUSE_Door")
    box((face_x, centre_y - 190.0, wall_base + 155.0), (0.16, 1.2, 1.0), wood, "HOUSE_Window")
    box((face_x, centre_y + 190.0, wall_base + 155.0), (0.16, 1.2, 1.0), wood, "HOUSE_Window")
    box((face_x + face * 28.0, centre_y, plinth_h * 50.0 + 4.0),
        (0.9, 1.9, 0.16), stone, "HOUSE_Step")

    # tiled gable roof and its ridge
    # curved, upturned tiled roof generated as a procedural mesh (see build_curved_roof)
    build_curved_roof(centre_x, centre_y, ridge_z, width, depth, pitch, roof, yaw)
    box((centre_x, centre_y, ridge_z + 8.0), (width + 1.8, 0.36, 0.24), roof,
        "HOUSE_Ridge", roll=0.0, yaw=yaw)

    # dark timber frieze under the eaves: the detail that reads as a Chinese house
    for sign in (-1, 1):
        box((centre_x, centre_y + sign * (depth * 50.0 - 6.0), ridge_z - drop * 100.0 - 12.0),
            (width + 1.2, 0.22, 0.30), wood, "HOUSE_Frieze", roll=0.0, yaw=yaw)
    return 1


def build_houses(materials):
    built = 0
    for (x, y, w, d, h, pitch, yaw) in HOUSES:
        built += build_house(x, y, w, d, h, pitch, yaw, materials)
    log("houses built: %d" % built)


def make_megascans_tiled(name, base_path, normal_path, orm_path, tiling, roughness_scale=1.0,
                         tint=None, rebuild=False):
    """Our own material over the Megascans texture assets, with a tiling we control.

    The shipped MI_* instances have no exposed UV parameter, so a 7 m wall showed a single giant
    tile. Sampling the same textures with an explicit TextureCoordinate multiply fixes the scale.
    tint multiplies the base colour: the Megascans planks are pale grey, Chinese timber is dark.
    """
    path = MATERIAL_DIR + "/" + name
    if EDITOR_ASSETS.does_asset_exist(path):
        if not rebuild:
            return unreal.load_asset(path)
        # Tiling is baked into the graph, so a retile needs a fresh asset (gotcha #50).
        EDITOR_ASSETS.delete_asset(path)

    base_tex = unreal.load_asset(base_path) if base_path else None
    normal_tex = unreal.load_asset(normal_path) if normal_path else None
    orm_tex = unreal.load_asset(orm_path) if orm_path else None
    if base_tex is None:
        log("megascans texture missing for " + name)
        return None

    material = ASSET_TOOLS.create_asset(name, MATERIAL_DIR, unreal.Material, unreal.MaterialFactoryNew())
    if material is None:
        return None

    coords = MATERIAL_EDITING.create_material_expression(
        material, unreal.MaterialExpressionTextureCoordinate, -900, 0)
    safe_set(coords, "u_tiling", tiling)
    safe_set(coords, "v_tiling", tiling)

    base = MATERIAL_EDITING.create_material_expression(
        material, unreal.MaterialExpressionTextureSample, -620, -160)
    safe_set(base, "texture", base_tex)
    MATERIAL_EDITING.connect_material_expressions(coords, "", base, "UVs")
    if tint is None:
        MATERIAL_EDITING.connect_material_property(base, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
    else:
        tinted = MATERIAL_EDITING.create_material_expression(
            material, unreal.MaterialExpressionMultiply, -380, -160)
        tint_expr = MATERIAL_EDITING.create_material_expression(
            material, unreal.MaterialExpressionConstant3Vector, -540, -40)
        tint_expr.set_editor_property(
            "constant", unreal.LinearColor(tint[0], tint[1], tint[2], 1.0))
        MATERIAL_EDITING.connect_material_expressions(base, "RGB", tinted, "A")
        MATERIAL_EDITING.connect_material_expressions(tint_expr, "", tinted, "B")
        MATERIAL_EDITING.connect_material_property(tinted, "", unreal.MaterialProperty.MP_BASE_COLOR)

    if normal_tex is not None:
        normal = MATERIAL_EDITING.create_material_expression(
            material, unreal.MaterialExpressionTextureSample, -620, 40)
        safe_set(normal, "texture", normal_tex)
        safe_set(normal, "sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
        MATERIAL_EDITING.connect_material_expressions(coords, "", normal, "UVs")
        MATERIAL_EDITING.connect_material_property(normal, "RGB", unreal.MaterialProperty.MP_NORMAL)

    if orm_tex is not None:
        orm = MATERIAL_EDITING.create_material_expression(
            material, unreal.MaterialExpressionTextureSample, -620, 240)
        safe_set(orm, "texture", orm_tex)
        MATERIAL_EDITING.connect_material_expressions(coords, "", orm, "UVs")
        if roughness_scale != 1.0:
            scale = MATERIAL_EDITING.create_material_expression(
                material, unreal.MaterialExpressionMultiply, -380, 280)
            safe_set(scale, "const_b", roughness_scale)
            MATERIAL_EDITING.connect_material_expressions(orm, "G", scale, "A")
            MATERIAL_EDITING.connect_material_property(scale, "", unreal.MaterialProperty.MP_ROUGHNESS)
        else:
            MATERIAL_EDITING.connect_material_property(orm, "G", unreal.MaterialProperty.MP_ROUGHNESS)

    MATERIAL_EDITING.recompile_material(material)
    EDITOR_ASSETS.save_asset(path)
    log("megascans tiled material built: " + path)
    return material


MEGASCANS_TEXTURES = {
    "roof": ("/Game/Fab/Megascans/Surfaces/Roof_Tiles_tk4gcgldy/Medium/tk4gcgldy_tier_2/Textures/"
             "T_tk4gcgldy_2K_B", "/Game/Fab/Megascans/Surfaces/Roof_Tiles_tk4gcgldy/Medium/"
             "tk4gcgldy_tier_2/Textures/T_tk4gcgldy_2K_N",
             "/Game/Fab/Megascans/Surfaces/Roof_Tiles_tk4gcgldy/Medium/"
             "tk4gcgldy_tier_2/Textures/T_tk4gcgldy_2K_ORM"),
    "wood": ("/Game/Fab/Megascans/Surfaces/Wood_Planks_throbglfw/Medium/throbglfw_tier_2/Textures/"
             "T_throbglfw_2K_B", "/Game/Fab/Megascans/Surfaces/Wood_Planks_throbglfw/Medium/"
             "throbglfw_tier_2/Textures/T_throbglfw_2K_N",
             "/Game/Fab/Megascans/Surfaces/Wood_Planks_throbglfw/Medium/"
             "throbglfw_tier_2/Textures/T_throbglfw_2K_ORM"),
}

# Fab hands some Megascans surfaces out as a plain texture payload (PNG maps, no MI_* instance),
# so the paving keeps its sources in Assets/Megascans and gets imported into the same Fab folder
# shape the packaged surfaces use. 2K on purpose: the 4K set was a 44 MB download whose extra
# detail a 1080p target throws away anyway (the device profile caps textures at 2048).
MEGASCANS_STONE_DIR = ("/Game/Fab/Megascans/Surfaces/Mossy_Stone_Walkway_ue4rcgxg/Medium/"
                       "ue4rcgxg_tier_2/Textures")
MEGASCANS_STONE_SRC = os.path.join("Assets", "Megascans", "mossy_stone_walkway_2k", "Textures")


def ensure_megascans_texture(asset_name, source_name, is_normal=False, is_linear=False, masks=False):
    """Import one PNG of a Fab texture payload and return the Texture2D (or None)."""
    path = MEGASCANS_STONE_DIR + "/" + asset_name
    if EDITOR_ASSETS.does_asset_exist(path):
        existing = unreal.load_asset(path)
        # Same reasoning as ensure_texture(): re-apply, so a wrong sRGB guess is repaired.
        apply_texture_flags(existing, is_normal, is_linear)
        return existing

    source = os.path.join(unreal.Paths.project_dir(), MEGASCANS_STONE_SRC, source_name)
    if not os.path.isfile(source):
        log("missing megascans texture source: " + source)
        return None

    task = unreal.AssetImportTask()
    task.filename = source
    task.destination_path = MEGASCANS_STONE_DIR
    task.destination_name = asset_name
    task.automated = True
    task.replace_existing = True
    task.save = True

    # sRGB is import-time only (gotcha #38). UE 5.8 moved it from a `srgb` bool to the factory's
    # ColorSpaceMode enum, but that UPROPERTY(Transient) is not exposed to Python (every spelling
    # fails with "Failed to find property"), so we set the flag on the Texture2D and save: the flag
    # is persisted, and the next load builds the shader resource view with the right colour space.
    factory = unreal.TextureFactory()
    if is_normal:
        safe_set(factory, "compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
    elif masks:
        # Fab imports ORM sets as "Masks"; BC1 would block up the roughness channel.
        safe_set(factory, "compression_settings", unreal.TextureCompressionSettings.TC_MASKS)
    task.factory = factory

    ASSET_TOOLS.import_asset_tasks([task])

    texture = unreal.load_asset(path)
    if texture is None:
        log("megascans texture import produced nothing: " + path)
        return None

    apply_texture_flags(texture, is_normal, is_linear)
    return texture


def megascans_stone_paths():
    """(base, normal, orm) asset paths for the 2K mossy stone, importing them on first use."""
    base = ensure_megascans_texture("T_ue4rcgxg_2K_B", "T_ue4rcgxg_2K_B.png")
    normal = ensure_megascans_texture("T_ue4rcgxg_2K_N", "T_ue4rcgxg_2K_N.png",
                                      is_normal=True, is_linear=True)
    orm = ensure_megascans_texture("T_ue4rcgxg_2K_ORM", "T_ue4rcgxg_2K_ORM.png",
                                   is_linear=True, masks=True)
    if base is None:
        return None
    return (MEGASCANS_STONE_DIR + "/T_ue4rcgxg_2K_B",
            MEGASCANS_STONE_DIR + "/T_ue4rcgxg_2K_N" if normal else None,
            MEGASCANS_STONE_DIR + "/T_ue4rcgxg_2K_ORM" if orm else None)


MEGASCANS_TEXTURE_IMPORTERS = {
    # key -> callable returning (base, normal, orm) for surfaces that ship as a raw payload
    "stone": megascans_stone_paths,
}


def tiled_megascans(key, material_name, tiling, rebuild=False):
    """Build (or reuse) a tiled material for a Megascans surface, falling back to the MI."""
    importer = MEGASCANS_TEXTURE_IMPORTERS.get(key)
    paths = importer() if importer is not None else MEGASCANS_TEXTURES.get(key)
    if paths and paths[0]:
        material = make_megascans_tiled(material_name, paths[0], paths[1], paths[2], tiling, rebuild=rebuild)
        if material is not None:
            return material
    return load_megascans(key)


def hex_to_linear(value):
    """'#956c42' -> unreal.LinearColor (sRGB-ish; good enough for flat low-poly props)."""
    text = value.lstrip("#")
    r = int(text[0:2], 16) / 255.0
    g = int(text[2:4], 16) / 255.0
    b = int(text[4:6], 16) / 255.0
    return unreal.LinearColor(r, g, b, 1.0)


# --- Village zone (south of the plaza, along the road the player starts on) -----------
# Tiles are small meshes, so their placements are generated instead of hand-listed.
STREET_TILES = [((0.0, -5300.0 + index * 400.0, 0.0), 0.0) for index in range(7)]

PADDY_TILES = []
for column in (-1700.0, -1300.0, -900.0, 1000.0, 1400.0, 1800.0):
    for row in (-4900.0, -4550.0):
        PADDY_TILES.append(((column, row, 0.0), 0.0))

FENCE_RUNS = [((760.0, y, 0.0), 90.0) for y in (-4750.0, -4350.0)] + \
             [((-760.0, y, 0.0), 90.0) for y in (-4750.0, -4350.0)]

# A side lane leaves the main street eastwards towards the well and the farmhouses, so the
# village is a T-junction instead of one straight avenue.
LANE_TILES = [((500.0 + index * 400.0, -4300.0, 0.0), 90.0) for index in range(4)]

# Rocks and bushes placed on the paved square's edge to break its hard rectangle: a paved
# patch with a clean border reads as a card laid on the grass.
SQUARE_EDGE_ROCKS = [((-400.0, -3650.0, 0.0), 10.0), ((1000.0, -3650.0, 0.0), 80.0),
                     ((-400.0, -4950.0, 0.0), 130.0), ((1000.0, -4950.0, 0.0), 200.0),
                     ((300.0, -3650.0, 0.0), 45.0), ((300.0, -4950.0, 0.0), 160.0)]

SQUARE_EDGE_BUSHES = [((-500.0, -4300.0, 0.0), 25.0), ((1100.0, -4300.0, 0.0), 205.0),
                      ((-450.0, -3900.0, 0.0), 95.0), ((1050.0, -4700.0, 0.0), 285.0)]

# --- Shrine zone (north of the plaza) -------------------------------------------------
# The stone path and the retaining walls are 2 m modular pieces, so they are generated.
SHRINE_PATH = [((0.0, 1800.0 + index * 200.0, 0.0), 0.0) for index in range(16)]

# Low retaining walls only along the sides: a wall across the path just fences the player in.
SHRINE_WALLS = [((-1300.0, 3600.0 + index * 200.0, 0.0), 0.0) for index in range(5)] + \
               [((1300.0, 3600.0 + index * 200.0, 0.0), 0.0) for index in range(5)]


# Polyfork props (licence: CC BY 4.0, credit in Docs/Polyfork-CREDITS.md).
# The GLB files live in Assets/Polyfork; they carry vertex colours which Interchange drops,
# so each prop gets a material built from the palette in its params.json (or from a Poly
# Haven PBR set when we have one).
# (id, label, colour, roughness, metallic, texture_set, tiling, placements)
PROPS = (
    ("stone-guardian-beast-663ee9", "GuardianBeast", "#8a8886", 0.90, 0.0, "precast_stone_paving", 2.0,
     [((-520.0, -1620.0, 0.0), -90.0), ((520.0, -1620.0, 0.0), 90.0)]),
    ("stone-lantern-d56d0a", "StoneLantern", "#c7cbcc", 0.85, 0.0, "precast_stone_paving", 1.0,
     [((-420.0, -2320.0, 0.0), 0.0), ((420.0, -2320.0, 0.0), 0.0),
      ((-1180.0, -300.0, 80.0), 0.0), ((1180.0, -300.0, 80.0), 0.0)]),
    ("tiered-pagoda-f4ade0", "Pagoda", "#8a7a5c", 0.80, 0.0, "wood_planks", 3.0,
     [((3000.0, 900.0, 0.0), 15.0)]),
    ("courtyard-residence-342ac2", "Courtyard", "#9a7f5c", 0.85, 0.0, "clay_plaster", 2.0,
     [((-2750.0, 150.0, 0.0), 90.0)]),
    ("bronze-tripod-cauldron-7ee4ba", "Cauldron", "#956c42", 0.45, 0.6, None, 1.0,
     [((0.0, 1320.0, 80.0), 0.0)]),
    # Scatter detail: the biggest cheap win. A dozen rocks/shrubs break up the empty ground
    # so the eye reads "place" instead of "two flat planes".
    ("river-stone-cluster-0b55bc", "Rocks", "#8a8886", 0.90, 0.0, "precast_stone_paving", 2.0,
     [((1350.0, -1450.0, 0.0), 20.0), ((-1500.0, -1200.0, 0.0), 75.0), ((1600.0, -500.0, 0.0), 130.0),
      ((-1650.0, 250.0, 0.0), 45.0), ((-420.0, -2380.0, 0.0), 100.0), ((520.0, -2450.0, 0.0), 60.0)]
     + SQUARE_EDGE_ROCKS),
    # The mountain gate itself: a real city gate (12 x 13.9 x 8 m) with two wall runs,
    # replacing the three jade boxes the blockout used.
    ("city-gate-77d012", "CityGate", "#8a8886", 0.85, 0.0, "precast_stone_paving", 3.0,
     [((3400.0, -1500.0, 0.0), 200.0)]),
    # ---- village zone (south of the plaza, along the road the player starts on) ----
    ("packed-earth-street-tile-dc6251", "Street", "#a08a66", 0.90, 0.0, "clay_plaster", 1.0,
     STREET_TILES),
    ("packed-earth-street-tile-dc6251", "Lane", "#a08a66", 0.90, 0.0, "clay_plaster", 1.0,
     LANE_TILES),
    ("rice-paddy-tile-dc727e", "Paddy", "#5f7a3a", 0.85, 0.0, "grass_ground", 1.0,
     PADDY_TILES),
    ("rammed-earth-farmhouse-6432fc", "Farmhouse_A", "#a08a66", 0.85, 0.0, "clay_plaster", 2.0,
     [((-2350.0, -4350.0, 0.0), 90.0)]),
    ("rammed-earth-farmhouse-6432fc", "Farmhouse_B", "#a08a66", 0.85, 0.0, "clay_plaster", 2.0,
     [((2400.0, -4550.0, 0.0), 270.0)]),
    ("rammed-earth-farmhouse-6432fc", "Farmhouse_C", "#a08a66", 0.85, 0.0, "clay_plaster", 2.0,
     [((2250.0, -3500.0, 0.0), 180.0)]),
    ("wine-inn-a41b12", "WineInn", "#8a6a45", 0.85, 0.0, "wood_planks", 2.0,
     [((-2350.0, -3350.0, 0.0), 90.0)]),
    ("village-well-f8e361", "Well", "#a8a49a", 0.85, 0.0, "precast_stone_paving", 1.0,
     [((420.0, -4250.0, 0.0), 15.0)]),
    ("stake-palisade-run-548617", "Fence", "#7a6446", 0.90, 0.0, "wood_planks", 1.0,
     FENCE_RUNS),
    # ---- shrine zone (north of the plaza) ----
    ("cleared-stone-path-tile-7e92bc", "ShrinePath", "#9a9890", 0.90, 0.0, "precast_stone_paving", 1.0,
     SHRINE_PATH),
    ("ishigaki-stone-wall-255b7e", "ShrineWall", "#8f8b82", 0.90, 0.0, "precast_stone_paving", 1.0,
     SHRINE_WALLS),
    ("stone-altar-8f3a0a", "Altar", "#8f8b82", 0.85, 0.0, "precast_stone_paving", 1.0,
     [((0.0, 4750.0, 0.0), 0.0), ((-260.0, 4770.0, 0.0), 15.0), ((260.0, 4770.0, 0.0), -15.0)]),
    ("tiered-bell-tower-e1b706", "BellTower", "#8a7a5c", 0.85, 0.0, "wood_planks", 2.0,
     [((-2300.0, 5250.0, 0.0), 30.0)]),
    ("grave-mound-169ec3", "Grave", "#7f7a70", 0.95, 0.0, "precast_stone_paving", 1.0,
     [((-700.0, 3650.0, 0.0), 12.0), ((780.0, 3720.0, 0.0), 132.0),
      ((-1150.0, 5050.0, 0.0), 75.0), ((1150.0, 5000.0, 0.0), 205.0)]),
    # ---- dressing pass: the difference between "models placed" and "somebody lives here" ----
    ("clay-wine-jar-8eea26", "Jar", "#8a5a3a", 0.80, 0.0, "clay_plaster", 1.0,
     [((-2000.0, -4300.0, 0.0), 20.0), ((-1900.0, -4380.0, 0.0), 75.0),
      ((-1980.0, -4450.0, 0.0), 140.0), ((2050.0, -3600.0, 0.0), 30.0)]),
    ("wooden-barrel-6afab0", "Barrel", "#6b4a2e", 0.85, 0.0, "wood_planks", 1.0,
     [((-2050.0, -3350.0, 0.0), 10.0), ((-1950.0, -3300.0, 0.0), 65.0),
      ((2100.0, -4500.0, 0.0), 35.0)]),
    ("fish-crate-3c3f7b", "Crate", "#7a5a38", 0.85, 0.0, "wood_planks", 1.0,
     [((1980.0, -4420.0, 0.0), 15.0), ((2040.0, -4580.0, 0.0), 100.0)]),
    ("basket-of-produce-7420cf", "Basket", "#8a7440", 0.90, 0.0, None, 1.0,
     [((-2150.0, -3400.0, 0.0), 40.0), ((1900.0, -4380.0, 0.0), 120.0)]),
    ("ox-cart-c12bca", "OxCart", "#6b4a2e", 0.85, 0.0, "wood_planks", 2.0,
     [((1850.0, -3950.0, 0.0), 200.0)]),
    ("firewood-stack-810f49", "Firewood", "#6b4a2e", 0.90, 0.0, "wood_planks", 1.0,
     [((-2250.0, -4480.0, 0.0), 85.0), ((2280.0, -3600.0, 0.0), 5.0)]),
    ("hemp-grain-sack-f91edc", "Sack", "#9a8452", 0.90, 0.0, None, 1.0,
     [((-1980.0, -4180.0, 0.0), 25.0), ((-1880.0, -4220.0, 0.0), 150.0),
      ((2000.0, -3520.0, 0.0), 70.0)]),
    ("nobori-banner-ae4d88", "Banner", "#8a3a2e", 0.85, 0.0, None, 1.0,
     [((-2150.0, -3250.0, 0.0), 20.0), ((60.0, 4620.0, 0.0), 175.0)]),
    ("signpost-0bf523", "Signpost", "#6b4a2e", 0.85, 0.0, "wood_planks", 1.0,
     [((520.0, -5050.0, 0.0), 200.0)]),
    # vegetation: the three zones were reading as bare ground

)

PROP_SOURCE_DIR = os.path.join("Assets", "Polyfork")
PROP_ASSET_DIR = "/Game/Props"


def ensure_prop_material(prop_id, color, roughness, metallic, texture_set=None, tiling=1.0):
    """Creates (once) a material for a prop: PBR textures when we have a set, flat colour otherwise."""
    suffix = "_Tex" if texture_set else ""
    path = "/Game/Materials/M_Prop_" + prop_id + suffix
    if EDITOR_ASSETS.does_asset_exist(path):
        existing = unreal.load_asset(path)
        MATERIAL_EDITING.recompile_material(existing)
        return existing

    if texture_set:
        textured = make_textured_material("M_Prop_" + prop_id + suffix, texture_set, tiling,
                                          roughness_scale=roughness)
        if textured is not None:
            return textured

    material = ASSET_TOOLS.create_asset(
        "M_Prop_" + prop_id + suffix, MATERIAL_DIR, unreal.Material, unreal.MaterialFactoryNew())
    if material is None:
        log("could not create material for " + prop_id)
        return None

    base = MATERIAL_EDITING.create_material_expression(
        material, unreal.MaterialExpressionConstant3Vector, -420, -120)
    base.set_editor_property("constant", color)

    roughness_expr = MATERIAL_EDITING.create_material_expression(
        material, unreal.MaterialExpressionConstant, -420, 60)
    roughness_expr.set_editor_property("r", roughness)

    metallic_expr = MATERIAL_EDITING.create_material_expression(
        material, unreal.MaterialExpressionConstant, -420, 190)
    metallic_expr.set_editor_property("r", metallic)

    MATERIAL_EDITING.connect_material_property(base, "", unreal.MaterialProperty.MP_BASE_COLOR)
    MATERIAL_EDITING.connect_material_property(roughness_expr, "", unreal.MaterialProperty.MP_ROUGHNESS)
    MATERIAL_EDITING.connect_material_property(metallic_expr, "", unreal.MaterialProperty.MP_METALLIC)
    MATERIAL_EDITING.recompile_material(material)
    EDITOR_ASSETS.save_asset(path)
    log("prop material ready: " + path)
    return material


def assign_material(mesh, material):
    """Points every material slot of a static mesh at the given material."""
    slots = mesh.get_editor_property("static_materials")
    if not slots:
        return False

    updated = []
    for slot in slots:
        slot.set_editor_property("material_interface", material)
        updated.append(slot)
    mesh.set_editor_property("static_materials", updated)
    EDITOR_ASSETS.save_asset(mesh.get_path_name().split(".")[0])
    return True


def ensure_prop_meshes(prop_id, material):
    """Imports the GLB once and returns the static meshes it produced."""
    folder = PROP_ASSET_DIR + "/" + prop_id

    # Interchange also imports skinned parts (tree foliage etc.) as skeletal meshes. This
    # project only uses the static geometry, and those extras are megabytes of dead weight.
    junk_dir = folder + "/SkeletalMeshes"
    if EDITOR_ASSETS.does_directory_exist(junk_dir):
        EDITOR_ASSETS.delete_directory(junk_dir)
        log("dropped unused SkeletalMeshes from %s" % prop_id)

    meshes = []
    for path in EDITOR_ASSETS.list_assets(folder, recursive=True, include_folder=False):
        asset = unreal.load_asset(path)
        if isinstance(asset, unreal.StaticMesh):
            meshes.append(asset)

    if meshes:
        return meshes

    source = os.path.join(unreal.Paths.project_dir(), PROP_SOURCE_DIR, prop_id + ".glb")
    if not os.path.isfile(source):
        log("missing prop source: " + source)
        return []

    task = unreal.AssetImportTask()
    task.filename = source
    task.destination_path = PROP_ASSET_DIR
    task.destination_name = prop_id
    task.automated = True
    task.replace_existing = True
    task.save = True
    ASSET_TOOLS.import_asset_tasks([task])

    for path in EDITOR_ASSETS.list_assets(folder, recursive=True, include_folder=False):
        asset = unreal.load_asset(path)
        if isinstance(asset, unreal.StaticMesh):
            if material is not None:
                assign_material(asset, material)
            meshes.append(asset)

    # Interchange also imports skinned parts (tree foliage etc.) as skeletal meshes. This
    # project only uses the static geometry, and those extras are megabytes of dead weight.
    for junk in ("SkeletalMeshes",):
        junk_dir = folder + "/" + junk
        if EDITOR_ASSETS.does_directory_exist(junk_dir):
            EDITOR_ASSETS.delete_directory(junk_dir)
            log("dropped unused %s from %s" % (junk, prop_id))

    # Interchange also imports skinned parts (tree foliage etc.) as skeletal meshes. This
    # project only uses the static geometry, and those extras are megabytes of dead weight.
    for junk in ("SkeletalMeshes",):
        junk_dir = folder + "/" + junk
        if EDITOR_ASSETS.does_directory_exist(junk_dir):
            EDITOR_ASSETS.delete_directory(junk_dir)
            log("dropped unused %s from %s" % (junk, prop_id))

    log("imported prop %s -> %d mesh(es)" % (prop_id, len(meshes)))
    return meshes


USE_POLYFORK_PROPS = False  # official-assets-only pass: keep the table for reference, do not spawn


def build_props():
    if not USE_POLYFORK_PROPS:
        log("polyfork props disabled (official assets only)")
        return
    """Dresses the level with the archived Polyfork props (idempotent: the level is wiped first)."""
    spawned = 0
    for prop_id, label, color_hex, roughness, metallic, texture_set, tiling, placements in PROPS:
        material = ensure_prop_material(prop_id, hex_to_linear(color_hex), roughness, metallic,
                                        texture_set, tiling)
        meshes = ensure_prop_meshes(prop_id, material)
        if not meshes:
            continue

        for index, (location, yaw) in enumerate(placements):
            for part_index, mesh in enumerate(meshes):
                suffix = "" if len(meshes) == 1 else "_%d" % part_index
                actor = spawn(unreal.StaticMeshActor, location, rotation=(0.0, 0.0, yaw),
                              label="PROP_%s_%d%s" % (label, index, suffix))
                if actor is None:
                    continue
                component = actor.static_mesh_component
                safe_set(component, "mobility", unreal.ComponentMobility.STATIC)
                component.set_static_mesh(mesh)
                if material is not None:
                    component.set_material(0, material)
                spawned += 1

    log("props spawned: %d" % spawned)


def load_p0_world():
    """Pull the P0 map data and use it for the flat playable areas."""
    global TERRAIN_FLAT_AREAS
    import sys
    tools_dir = os.path.join(unreal.Paths.project_dir(), "Tools")
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)
    # RebuildInEditor runs this file again inside the same editor, where sys.modules already holds
    # the previous import of our own modules - edits to build_world.py / village_house.py /
    # chinese_house.py would be silently ignored. Drop everything that came from Tools/.
    for name in [name for name, module in list(sys.modules.items())
                 if getattr(module, "__file__", None)
                 and os.path.dirname(os.path.abspath(module.__file__)) == os.path.abspath(tools_dir)]:
        sys.modules.pop(name, None)
    try:
        from build_world import build_world as _build_world, flat_areas as _flat, load_world as _load
    except Exception as error:  # noqa: BLE001
        log("world data skipped (%s)" % error)
        return None
    world = _load()
    TERRAIN_FLAT_AREAS = _flat(world)
    log("world data: %d zones, %d roads" % (len(world["zones"]), len(world["roads"])))
    return (_build_world, world)


def main():
    if not ensure_empty_level():
        raise RuntimeError("Could not create or load " + LEVEL_PATH)

    materials = make_materials()
    # 2026-11-26: the level is now a reconstruction of a real 墨香 map rather than the hand-built
    # P0 sandbox. The sky is kept exactly as it was - atmosphere, sky light, clouds and sun - and
    # everything else comes from the client's own data. The hand-built world is reproducible from
    # Assets/Map/p0_world.json if it is ever wanted back; it is not built any more.
    build_lighting()
    placed = build_moxiang_map.build()
    log("moxiang map rebuilt from the client data: %d surfaces" % placed)
    saved = LEVELS.save_current_level()
    log("save_current_level -> %s" % saved)
    log("Done. %d actors in %s" % (len(ACTORS.get_all_level_actors()), LEVEL_PATH))
    return

    build_monsters()
    build_props()
    build_ground_patches(materials)
    build_gate()
    build_decals(materials)
    build_foliage()
    build_ferns()
    build_bamboo()
    build_grass()
    build_terrain(materials)
    build_houses(materials)
    log("unreachable: kept for reference while the village is rebuilt")
    # Pond: reverted. A flat plane with no water shader read as a blue plastic sheet.

    saved = LEVELS.save_current_level()
    log("save_current_level -> %s" % saved)
    log("Done. %d actors in %s" % (len(ACTORS.get_all_level_actors()), LEVEL_PATH))


try:
    main()
except Exception:
    unreal.log_error("[LingXuJie] level generation failed:\n" + traceback.format_exc())
    raise
