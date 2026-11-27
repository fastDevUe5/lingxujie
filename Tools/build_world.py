"""Generate the P0 world from Assets/Map/p0_world.json.

The point of this module is that the whole map is data: change a number in the JSON and rebuild,
instead of editing Python and re-tuning by eye. It draws

  * flat ground for every zone,
  * the roads between zone centres,
  * the village's finished houses (assembled from the gate pack by Tools/village_house.py) and
    grey-box blocks everywhere else (replace those with real assets later),
  * spawn points for NPCs and monsters.

Called from build_level.py: `from build_world import build_world` then `build_world(materials)`.
"""

import json
import math
import os

import unreal

from chinese_house import build_cross_ridge_pavilion as build_chinese_pavilion
from chinese_house import build_house as build_chinese_house
from village_house import (BAY, build_courtyard, build_fence, build_gatehouse, build_house,
                           build_monster_slot, build_npc_slot, build_pavilion, build_stall,
                           build_well, build_woodpile)

WORLD_JSON = os.path.join("Assets", "Map", "p0_world.json")
GREYBOX_CUBE = "/Engine/BasicShapes/Cube.Cube"

# 桃源村 is the finished zone: real houses instead of blocks. The others keep their grey boxes
# until their own asset pass.
HOUSE_ZONE = "taoyuan"
# 兰州 (the city) is the second finished zone: same house assembly, but every block is the big
# 2 x 3 bay shopfront (4.9 x 7.4 m facade) and no courtyards - a city street has doors on the road.
CITY_ZONE = "lanzhou"
CITY_BAYS = (2, 3)
# POI ids that stand for a person in the city (the pond POI is scenery, not an NPC).
NPC_POI_IDS = ("shop", "quest", "elder", "healer")
# 敦煌 is wilderness: no buildings at all, a scatter of monster positions and one post station. Its
# POIs are read as data so the layout stays editable; ids starting with this prefix are monsters.
WILDERNESS_ZONE = "dunhuang"
MONSTER_POI_PREFIX = "mob"
# 桃源村 has 2 big and 2 small houses, expressed in wall bays (one bay = 2.46 m panel, see
# village_house.PIECES). The big ones are one bay wider along the street (7.4 m facade); the small
# ones stay square at two bays. Diagonally opposite plots get the big ones so each row mixes.
HOUSE_BAYS_BIG = (2, 3)
HOUSE_BAYS_SMALL = (2, 2)
BIG_HOUSE_INDICES = (0, 3)


def load_world():
    path = os.path.join(unreal.Paths.project_dir(), WORLD_JSON)
    with open(path, "r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def flat_areas(world):
    """Zone rectangles in the (x0, x1, y0, y1) form build_level._terrain_height expects."""
    areas = []
    for zone in world["zones"]:
        cx, cy = zone["centre"]
        sx, sy = zone["size"]
        areas.append((cx - sx / 2.0, cx + sx / 2.0, cy - sy / 2.0, cy + sy / 2.0))
    return areas


def _log(message):
    unreal.log("[LingXuJie] " + str(message))


def street_plot(cx, cy, count, index, spacing=1600.0, row_offset=1400.0):
    """Plot for building `index` of `count`, and the yaw that turns its door to the street.

    墨香-era towns read as a street with houses in two rows, so the road stays clear and every
    door faces it: the -X row looks east (+X, yaw 0), the +X row looks west (yaw 180).
    """
    side = -1.0 if index % 2 == 0 else 1.0
    row = index // 2
    x = cx + side * row_offset
    y = cy + (row - (count // 2 - 1) / 2.0) * spacing
    return (x, y), (0.0 if side < 0.0 else 180.0)


def build_world(materials, spawn, ground_patch, log):
    """Build terrain-adjacent scenery for every zone; terrain height comes from flat_areas()."""
    world = load_world()
    cube = unreal.load_asset(GREYBOX_CUBE)
    wall = materials.get("stone") or materials.get("wall")

    houses = 0
    yards = 0
    fillers = 0
    city = 0
    mobs = 0
    placed = 0
    for zone in world["zones"]:
        cx, cy = zone["centre"]
        count = int(zone.get("buildings", 0))
        for index in range(count):
            # Zones may tighten their plot spacing (兰州 packs its eight buildings so they stop
            # crowding the village's north row); the defaults are the 墨香 two-row street.
            (x, y), yaw = street_plot(cx, cy, count, index,
                                      spacing=float(zone.get("row_spacing", 1600.0)),
                                      row_offset=float(zone.get("row_offset", 1400.0)))
            if zone["id"] == HOUSE_ZONE:
                bays = HOUSE_BAYS_BIG if index in BIG_HOUSE_INDICES else HOUSE_BAYS_SMALL
                prefix = "%s_H%02d" % (zone["id"].upper(), index)
                houses += build_house(spawn, log, (x, y), yaw=yaw, bays=bays, material=wall,
                                      prefix=prefix, gable_material=materials.get("wood"))
                yards += build_courtyard(spawn, log, (x, y), yaw, bays[0] * BAY * 0.5, wall,
                                         prefix=prefix, gate_material=materials.get("wood"))
                continue
            if zone["id"] == CITY_ZONE:
                city += build_house(spawn, log, (x, y), yaw=yaw, bays=CITY_BAYS, material=wall,
                                    prefix="%s_BLD%02d" % (zone["id"].upper(), index),
                                    gable_material=materials.get("wood"))
                continue
            # plain boxes: 墨香-era buildings are simple blocks, not set pieces
            size = (700.0, 600.0, 380.0) if zone["ground"] != "sand" else (500.0, 400.0, 260.0)
            actor = spawn(unreal.StaticMeshActor, (x, y, size[2] / 2.0),
                          rotation=(0.0, 0.0, yaw),
                          label="%s_BLD_%02d" % (zone["id"].upper(), index))
            if actor is None:
                continue
            actor.static_mesh_component.set_static_mesh(cube)
            actor.set_actor_scale3d(unreal.Vector(size[0] / 100.0, size[1] / 100.0, size[2] / 100.0))
            if wall is not None:
                actor.static_mesh_component.set_material(0, wall)
            placed += 1

    # 桃源村's fillers and the village gate. Offsets are relative to the zone centre, so they
    # follow Assets/Map/p0_world.json instead of being pinned to absolute coordinates.
    village = next((zone for zone in world["zones"] if zone["id"] == HOUSE_ZONE), None)
    if village is not None:
        vx, vy = village["centre"]
        stone = materials.get("stone") or materials.get("wall")
        wood = materials.get("wood")
        fillers += build_gatehouse(spawn, log, (vx, vy - 2550.0), span=600.0, material=stone,
                                   prefix="TAOYUAN_GATE")
        fillers += build_well(spawn, log, (vx - 860.0, vy - 1000.0), material=stone, wood=wood,
                              prefix="TAOYUAN_WELL")
        fillers += build_fence(spawn, log, (vx + 880.0, vy - 850.0), yaw=90.0, length=500.0,
                               material=wood, prefix="TAOYUAN_FENCE")
        fillers += build_woodpile(spawn, log, (vx - 900.0, vy + 1000.0), material=wood,
                                  prefix="TAOYUAN_WOODPILE")

    # 敦煌: seven monster positions and one 驿亭, no buildings. The two kinds of POI are told apart
    # by id prefix, so adding a monster later is a JSON edit rather than a code change.
    wilderness = next((zone for zone in world["zones"] if zone["id"] == WILDERNESS_ZONE), None)
    if wilderness is not None:
        for poi in world.get("poi", []):
            if poi.get("zone") != WILDERNESS_ZONE:
                continue
            px, py = poi["at"]
            identifier = str(poi.get("id", ""))
            if identifier.startswith(MONSTER_POI_PREFIX):
                mobs += build_monster_slot(spawn, log, (px, py), stone, wood,
                                           prefix="DUNHUANG_%s" % identifier.upper())
            elif identifier == "camp":
                # The post station sits on the road at the zone centre, so the traveller meets it
                # walking north rather than having to look for it.
                fillers += build_pavilion(spawn, log, (px, py), span=420.0, material=stone,
                                          prefix="DUNHUANG_CAMP")

    # 兰州的 NPC 位与商店摊：坐标来自 p0_world.json 的 poi 表（T8 会把标记换成会说话的人）。
    # Only real NPC points get a slot - the pond POI belongs to the garden set that D8 keeps out of
    # the generation flow.
    for poi in world.get("poi", []):
        if poi.get("zone") != CITY_ZONE or poi.get("id") not in NPC_POI_IDS:
            continue
        px, py = poi["at"]
        fillers += build_npc_slot(spawn, log, (px, py), stone,
                                  prefix="LANZHOU_%s" % str(poi.get("id", "npc")).upper())
        if poi.get("id") == "shop":
            # The stall stands just behind the merchant, in front of the shopfront.
            side = 1.0 if px >= 0.0 else -1.0
            fillers += build_stall(spawn, log, (px + side * 250.0, py), yaw=180.0 if side > 0.0 else 0.0,
                                   material=stone, wood=wood, prefix="LANZHOU_SHOP_STALL")

    # TEMP: one procedural Chinese house east of the village, for the A/B look test against the
    # gate-pack assembly. It sits outside the street so nothing else moves; delete this block once
    # the direction is decided.
    fillers += build_chinese_house(spawn, log, (2600.0, -9400.0), yaw=180.0, materials=materials,
                                   prefix="SAMPLE")
    # TEMP: a 十字脊 pavilion beside it - 墨香 puts the X-shaped roof on gatehouses/shrines, not on
    # houses, so this is the test of that roof type.
    fillers += build_chinese_pavilion(spawn, log, (2600.0, -8400.0), yaw=180.0,
                                      materials=materials, prefix="SAMPLE_PAVILION")

    for road in world["roads"]:
        (x0, y0), (x1, y1) = road["from"], road["to"]
        length = math.hypot(x1 - x0, y1 - y0)
        yaw = math.degrees(math.atan2(y1 - y0, x1 - x0))
        material = materials.get(road.get("surface", "stone")) or materials.get("stone")
        if material is None:
            continue
        ground_patch("ROAD_%d" % placed, material, ((x0 + x1) / 2.0, (y0 + y1) / 2.0),
                     (length / 100.0, road.get("width", 1000.0) / 100.0),
                     z=60.0, yaw=yaw, thickness=0.02)
        placed += 1

    log("world: %d zones, %d roads, %d grey-box pieces, %d house pieces, %d courtyard pieces, "
        "%d village fillers, %d city buildings, %d wilderness monster pieces"
        % (len(world["zones"]), len(world["roads"]), placed, houses, yards, fillers, city, mobs))
    return world
