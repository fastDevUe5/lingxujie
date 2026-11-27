"""Assemble one village house from the Geonchunmun modular pieces.

The pack has no ready-made farmhouse, but it does have building-scale parts (the SM_GSB / SM_SMJC
sets that ship beside the gate): a 2.46 m wall bay, a 2.88 m timber post, a 0.77 m door leaf and a
2.35 m x 6.88 m half roof. A house is therefore a small layout table of those parts at *native*
size - scaling a gate-sized wall down to farmhouse size would stretch every tile and beam.

Every number below is the mesh's own bounding box in cm, measured by Tools/probe_pack.py, so the
pieces line up without guessing. The house faces +X (door side) unless the yaw says otherwise.

Size is expressed in *bays*: a bay is one 2.46 m wall panel, so 桃源村's houses are 2 bays deep
(4.9 m) and either 2 or 3 bays wide along the street (4.9 m / 7.4 m). The half roof's ridge only
covers 6.88 m, so a 3-bay house stretches the roof along the ridge by ~7 % - a stretch that the
tiles absorb invisibly, while the alternative (a second roof pair) would double the ridge line.
"""

import math

import unreal

PACK = "/Game/GeonchunmunComplex/Meshes/Buildings/"

# key: (mesh name, (size x, y, z), (bbox centre x, y, z)) - straight from probe_pack.py output.
PIECES = {
    "wall":   ("SM_GSB_WallB",      (245.8, 24.8, 292.4), (122.9, 12.4, 146.2)),
    "post":   ("SM_SMJC_Pillar",    (21.7, 21.7, 287.8),  (0.0, 0.0, 143.9)),
    "door":   ("SM_SMJC_Door01A",   (77.0, 18.7, 247.3),  (37.0, -6.35, 123.65)),
    "roof":   ("SM_GSB_Roof01A",    (235.3, 688.0, 260.7), (117.65, 1.2, -111.3)),
}

BAY = 245.8               # one wall panel, cm; natives so no tile stretching
WALL_H = 292.4
PLINTH_H = 30.0
ROOF_EAVE_OVERLAP = 15.0
ROOF_RIDGE_LENGTH = 688.0  # the half roof's own ridge length, cm

_MESH_CACHE = {}


def _mesh(key):
    if key not in _MESH_CACHE:
        name = PIECES[key][0]
        _MESH_CACHE[key] = unreal.load_asset(PACK + name + "." + name)
    return _MESH_CACHE[key]


def _rot(dx, dy, yaw):
    rad = math.radians(yaw)
    return dx * math.cos(rad) - dy * math.sin(rad), dx * math.sin(rad) + dy * math.cos(rad)


def _spawn_piece(spawn, key, centre_xy, centre_z, yaw, label, material=None):
    """Place a piece so its bounding-box centre lands on (centre_xy, centre_z).

    The pack's pivots sit at odd corners (a wall bay's pivot is its bottom-left corner), so the
    bbox centre is what the layout table positions; the actor is offset by the rotated centre.
    """
    mesh = _mesh(key)
    if mesh is None:
        return None
    local = PIECES[key][2]
    rx, ry = _rot(local[0], local[1], yaw)
    actor = spawn(unreal.StaticMeshActor,
                  (centre_xy[0] - rx, centre_xy[1] - ry, centre_z - local[2]),
                  rotation=(0.0, 0.0, yaw), label=label)
    if actor is None:
        return None
    component = actor.static_mesh_component
    try:
        component.set_mobility(unreal.ComponentMobility.STATIC)
    except Exception:  # noqa: BLE001 - older builds only expose the editor property
        pass
    component.set_static_mesh(mesh)
    if material is not None:
        component.set_material(0, material)
    return actor


def _spawn_roof_half(spawn, centre_xy, ridge_z, yaw, label, ridge_scale=1.0):
    """Roof halves pivot on the ridge: local origin is on the ridge line, geometry hangs off +X.

    The ridge runs along the piece's local Y, so the actor's Y scale is what lengthens the ridge
    over a 3-bay house; X (the slope) and Z stay untouched so the pitch keeps its proportions.
    """
    mesh = _mesh("roof")
    if mesh is None:
        return None
    actor = spawn(unreal.StaticMeshActor, (centre_xy[0], centre_xy[1], ridge_z),
                  rotation=(0.0, 0.0, yaw), label=label)
    if actor is None:
        return None
    component = actor.static_mesh_component
    try:
        component.set_mobility(unreal.ComponentMobility.STATIC)
    except Exception:  # noqa: BLE001
        pass
    component.set_static_mesh(mesh)
    if abs(ridge_scale - 1.0) > 0.001:
        actor.set_actor_scale3d(unreal.Vector(1.0, ridge_scale, 1.0))
    return actor


def _box(spawn, centre, size, material, label, rotation=(0.0, 0.0, 0.0)):
    """A scaled engine cube: plinths, thresholds, fence rails, stacked firewood."""
    actor = spawn(unreal.StaticMeshActor, (centre[0], centre[1], centre[2]),
                  rotation=rotation, label=label)
    if actor is None:
        return 0
    cube = unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
    component = actor.static_mesh_component
    try:
        component.set_mobility(unreal.ComponentMobility.STATIC)
    except Exception:  # noqa: BLE001
        pass
    component.set_static_mesh(cube)
    if material is not None:
        component.set_material(0, material)
    actor.set_actor_scale3d(unreal.Vector(size[0] / 100.0, size[1] / 100.0, size[2] / 100.0))
    return 1


def _plinth(spawn, centre, size, material, label):
    return _box(spawn, (centre[0], centre[1], PLINTH_H * 0.5),
                (size[0], size[1], PLINTH_H), material, label)


# 院墙: the pack's own 2.46 m stone wall panel, 2.05 m tall, used at native size where it fits.
COURTYARD_PIECE = "SM_SMJC_StoneWall01A"
COURTYARD_PIECE_LEN = 245.8
COURTYARD_PIECE_SIZE = (245.8, 17.0, 205.0)
COURTYARD_PIECE_CENTRE = (122.9, 8.5, 102.5)
COURTYARD_DEPTH = 500.0          # how far the walled yard reaches out from the house front
COURTYARD_HALF_WIDTH = 450.0     # half of the yard's width along the street
GATE_WIDTH = 150.0               # 柴门 opening in the street-side wall


def _wall_run(spawn, start, end, material, label):
    """Fill a straight run with stone wall panels, scaled only along their own length."""
    mesh = unreal.load_asset(PACK + COURTYARD_PIECE + "." + COURTYARD_PIECE)
    if mesh is None:
        return 0
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length = math.hypot(dx, dy)
    if length < 30.0:
        return 0
    yaw = math.degrees(math.atan2(dy, dx))
    pieces = max(1, int(round(length / COURTYARD_PIECE_LEN)))
    segment = length / pieces
    scale = segment / COURTYARD_PIECE_LEN
    placed = 0
    for index in range(pieces):
        t = (index + 0.5) / pieces
        px = start[0] + dx * t
        py = start[1] + dy * t
        rx, ry = _rot(COURTYARD_PIECE_CENTRE[0] * scale, COURTYARD_PIECE_CENTRE[1], yaw)
        actor = spawn(unreal.StaticMeshActor,
                      (px - rx, py - ry, COURTYARD_PIECE_CENTRE[2]),
                      rotation=(0.0, 0.0, yaw), label="%s_%d" % (label, index))
        if actor is None:
            continue
        component = actor.static_mesh_component
        try:
            component.set_mobility(unreal.ComponentMobility.STATIC)
        except Exception:  # noqa: BLE001
            pass
        component.set_static_mesh(mesh)
        if material is not None:
            component.set_material(0, material)
        if abs(scale - 1.0) > 0.001:
            actor.set_actor_scale3d(unreal.Vector(scale, 1.0, 1.0))
        placed += 1
    return placed


def build_courtyard(spawn, log, centre, yaw, house_half_width, material, prefix=None,
                    gate_material=None):
    """A walled yard in front of the house, with a brushwood gate in the street-side wall.

    front_sign follows the door: the row at -X faces +X (sign +1), the row at +X faces -X (-1).
    """
    cx, cy = centre
    front_sign = 1.0 if abs(yaw) < 90.0 else -1.0
    house_front = cx + front_sign * (house_half_width + 40.0)
    wall_x = house_front + front_sign * COURTYARD_DEPTH
    tag = (prefix or "VIL_%d_%d" % (int(cx), int(cy))) + "_YARD"

    count = 0
    # Side walls, from the house front out to the street-side wall.
    for side in (1.0, -1.0):
        y = cy + side * COURTYARD_HALF_WIDTH
        count += _wall_run(spawn, (house_front, y), (wall_x, y), material,
                           "%s_SIDE_%d" % (tag, int(side)))
    # Street-side wall, split around the gate opening.
    for side in (1.0, -1.0):
        y_edge = cy + side * COURTYARD_HALF_WIDTH
        y_gate = cy + side * (GATE_WIDTH * 0.5)
        count += _wall_run(spawn, (wall_x, y_gate), (wall_x, y_edge), material,
                           "%s_FRONT_%d" % (tag, int(side)))

    # 柴门: two posts, a timber lintel and a plank leaf, all native-scale.
    post_z = PLINTH_H + PIECES["post"][1][2] * 0.5
    for side in (1.0, -1.0):
        count += 1 if _spawn_piece(spawn, "post", (wall_x, cy + side * GATE_WIDTH * 0.5),
                                   post_z, 0.0, "%s_GATEPOST_%d" % (tag, int(side))) else 0
    lintel_z = PLINTH_H + PIECES["post"][1][2] + 7.5
    count += _box(spawn, (wall_x, cy, lintel_z), (30.0, GATE_WIDTH + 60.0, 15.0),
                  gate_material, tag + "_LINTEL")
    count += _box(spawn, (wall_x + front_sign * 14.0, cy, PLINTH_H + 90.0),
                  (8.0, GATE_WIDTH - 10.0, 180.0), gate_material, tag + "_GATE")

    log("courtyard at %d, %d: %d pieces" % (int(cx), int(cy), count))
    return count


def build_house(spawn, log, centre, yaw=0.0, bays=(2, 2), material=None,
                roof=True, prefix=None, gable_material=None):
    """One house: stone plinth, wall bays, corner posts, gable roof and a door.

    bays = (bays across the depth, bays across the facade). The facade faces +X, so the second
    number is the width the street sees. The roof's two halves leave a triangular opening at each
    gable end, so a backing panel sits 30 cm inboard: the roof hides its corners from outside and
    the opening reads as a boarded gable instead of a hole you can see through.
    """
    cx, cy = centre
    width = bays[0] * BAY            # along X: how deep the house is
    depth = bays[1] * BAY            # along Y: how wide it looks from the street
    half_w, half_d = width * 0.5, depth * 0.5
    tag = prefix or "VIL_%d_%d" % (int(cx), int(cy))

    def to_world(dx, dy):
        rx, ry = _rot(dx, dy, yaw)
        return (cx + rx, cy + ry)

    count = _plinth(spawn, (cx, cy), (width + 70.0, depth + 70.0), material, tag + "_BASE")

    # Walls: one 2.46 m panel per bay. Piece yaw 0 spans X (north/south walls), 90 spans Y.
    wall_z = PLINTH_H + WALL_H * 0.5
    for index in range(bays[0]):
        bay_x = -half_w + (index + 0.5) * BAY
        for dy in (half_d, -half_d):
            point = to_world(bay_x, dy)
            count += 1 if _spawn_piece(spawn, "wall", point, wall_z, yaw,
                                       "%s_WX%d_%d" % (tag, index, int(dy))) else 0
    for index in range(bays[1]):
        bay_y = -half_d + (index + 0.5) * BAY
        for dx in (half_w, -half_w):
            point = to_world(dx, bay_y)
            count += 1 if _spawn_piece(spawn, "wall", point, wall_z, yaw + 90.0,
                                       "%s_WY%d_%d" % (tag, index, int(dx))) else 0

    # Corner posts stand just proud of the wall junctions, as the pack's gate does.
    post_z = PLINTH_H + PIECES["post"][1][2] * 0.5
    for dx in (-half_w, half_w):
        for dy in (-half_d, half_d):
            point = to_world(dx, dy)
            count += 1 if _spawn_piece(spawn, "post", point, post_z, yaw,
                                       "%s_P%s_%s" % (tag, int(dx), int(dy))) else 0

    # Door leaf on the +X facade, a little proud of the wall.
    door_z = PLINTH_H + PIECES["door"][1][2] * 0.5
    door_point = to_world(half_w + 24.0, 0.0)
    count += 1 if _spawn_piece(spawn, "door", door_point, door_z, yaw + 90.0,
                               tag + "_DOOR") else 0

    # Threshold slab in front of the door.
    count += _plinth(spawn, to_world(half_w + 40.0, 0.0), (160.0, 60.0), material,
                     tag + "_STEP")

    # Roof: two halves pivoting on the ridge, eaves landing on the wall top. The ridge covers
    # the facade width (depth); a 3-bay facade is 7.4 m against the roof's 6.88 m.
    if roof:
        ridge_z = PLINTH_H + WALL_H + 241.6 - ROOF_EAVE_OVERLAP
        ridge_scale = max(1.0, depth / ROOF_RIDGE_LENGTH)
        for half_yaw in (0.0, 180.0):
            count += 1 if _spawn_roof_half(spawn, (cx, cy), ridge_z, yaw + half_yaw,
                                           "%s_ROOF_%d" % (tag, int(half_yaw)),
                                           ridge_scale=ridge_scale) else 0

        # Gable ends are left open on purpose for now. The two roof halves leave a triangle above
        # the wall top (227 cm) and the pack has no gable triangle piece; a rectangular panel is
        # wider than the roof at its top edge and pokes out, and stepped panels only hide the
        # middle. Recorded as an open item instead of faking it with boxes.
        pass

    log("house at %d, %d: %d pieces (%d x %d bays, %.0f x %.0f cm)" % (
        int(cx), int(cy), count, bays[0], bays[1], width, depth))
    return count


def build_gatehouse(spawn, log, centre, yaw=0.0, span=600.0, material=None, prefix=None):
    """村口小门楼: two pillars, a stone footing under each, and one roof pair across the road.

    span is the distance between the pillars; the roof is 6.88 m across its ridge, so a 6 m span
    leaves ~40 cm of eave on each side - the village gate reads as a gate, not as a hall.
    """
    cx, cy = centre
    tag = prefix or "GATE"
    count = 0
    post_h = PIECES["post"][1][2]
    for side in (1.0, -1.0):
        offset = side * span * 0.5
        point = _rot(offset, 0.0, yaw)
        count += _plinth(spawn, (cx + point[0], cy + point[1]), (70.0, 70.0), material,
                         "%s_FOOT_%d" % (tag, int(side)))
        count += 1 if _spawn_piece(spawn, "post", (cx + point[0], cy + point[1]),
                                   PLINTH_H + post_h * 0.5, yaw,
                                   "%s_POST_%d" % (tag, int(side))) else 0

    # Ridge across the road: the roof's long axis (6.88 m) runs along X, so the slopes face the
    # traveller. 90 degrees turns the pair, whose ridge otherwise runs along Y.
    ridge_z = PLINTH_H + post_h + 241.6 - ROOF_EAVE_OVERLAP
    for half_yaw in (0.0, 180.0):
        count += 1 if _spawn_roof_half(spawn, (cx, cy), ridge_z, yaw + 90.0 + half_yaw,
                                       "%s_ROOF_%d" % (tag, int(half_yaw))) else 0

    log("gatehouse at %d, %d: %d pieces, %.0f cm span" % (int(cx), int(cy), count, span))
    return count


def build_well(spawn, log, centre, material=None, wood=None, prefix=None):
    """井: a stone ring with a dark opening, plus a timber frame over it."""
    cx, cy = centre
    tag = prefix or "WELL"
    cylinder = unreal.load_asset("/Engine/BasicShapes/Cylinder.Cylinder")
    count = 0

    if cylinder is not None:
        ring = spawn(unreal.StaticMeshActor, (cx, cy, 36.0), label=tag + "_RING")
        if ring is not None:
            ring.static_mesh_component.set_static_mesh(cylinder)
            if material is not None:
                ring.static_mesh_component.set_material(0, material)
            ring.set_actor_scale3d(unreal.Vector(1.4, 1.4, 0.72))
            count += 1
        # The dark plug reads as the shaft; without it the well is a stone drum.
        hole = spawn(unreal.StaticMeshActor, (cx, cy, 68.0), label=tag + "_MOUTH")
        if hole is not None:
            hole.static_mesh_component.set_static_mesh(cylinder)
            hole.set_actor_scale3d(unreal.Vector(1.1, 1.1, 0.06))
            count += 1

    # Two uprights and a crossbar: the bucket frame every 墨香-era village well has.
    for side in (1.0, -1.0):
        count += _box(spawn, (cx, cy + side * 70.0, 90.0), (14.0, 14.0, 180.0), wood,
                      "%s_POST_%d" % (tag, int(side)))
    count += _box(spawn, (cx, cy, 176.0), (14.0, 170.0, 12.0), wood, tag + "_BAR")

    log("well at %d, %d: %d pieces" % (int(cx), int(cy), count))
    return count


def build_fence(spawn, log, centre, yaw=0.0, length=600.0, material=None, prefix=None):
    """栅栏: posts with two rails, the way a village yard keeps chickens in."""
    cx, cy = centre
    tag = prefix or "FENCE"
    count = 0
    posts = max(2, int(round(length / 150.0)) + 1)
    for index in range(posts):
        t = index / float(posts - 1)
        local = (-length * 0.5) + length * t
        dx, dy = _rot(local, 0.0, yaw)
        count += _box(spawn, (cx + dx, cy + dy, 45.0), (12.0, 12.0, 90.0), material,
                      "%s_POST_%d" % (tag, index))
    for height in (35.0, 70.0):
        count += _box(spawn, (cx, cy, height), (length, 8.0, 10.0), material,
                      "%s_RAIL_%d" % (tag, int(height)), rotation=(0.0, 0.0, yaw))
    log("fence at %d, %d: %d pieces" % (int(cx), int(cy), count))
    return count


def build_woodpile(spawn, log, centre, yaw=0.0, material=None, prefix=None):
    """柴堆: three split logs stacked, enough to read as firewood at village scale."""
    cx, cy = centre
    tag = prefix or "WOODPILE"
    count = 0
    rows = ((0.0, 40.0, 3), (0.0, 76.0, 2), (0.0, 112.0, 1))
    for row_index, (_, z, logs) in enumerate(rows):
        for log_index in range(logs):
            offset = (log_index - (logs - 1) * 0.5) * 46.0
            dx, dy = _rot(offset, 0.0, yaw)
            count += _box(spawn, (cx + dx, cy + dy, z), (220.0, 40.0, 34.0), material,
                          "%s_%d_%d" % (tag, row_index, log_index))
    log("woodpile at %d, %d: %d pieces" % (int(cx), int(cy), count))
    return count


def build_stall(spawn, log, centre, yaw=0.0, material=None, wood=None, prefix=None):
    """商店摊: four timber posts, a counter and a flat board canopy - 墨香's market stalls read
    the same way, and the trade UI itself is a later task (T8)."""
    cx, cy = centre
    tag = prefix or "STALL"
    count = 0
    for dx in (-110.0, 110.0):
        for dy in (-90.0, 90.0):
            offset = _rot(dx, dy, yaw)
            count += _box(spawn, (cx + offset[0], cy + offset[1], 120.0),
                          (14.0, 14.0, 240.0), wood, "%s_POST_%s_%s" % (tag, int(dx), int(dy)))
    count += _box(spawn, (cx, cy, 45.0), (200.0, 80.0, 90.0), wood, tag + "_COUNTER",
                  rotation=(0.0, 0.0, yaw))
    count += _box(spawn, (cx, cy, 250.0), (260.0, 190.0, 12.0), wood, tag + "_CANOPY",
                  rotation=(0.0, 0.0, yaw))
    log("stall at %d, %d: %d pieces" % (int(cx), int(cy), count))
    return count


def build_npc_slot(spawn, log, centre, material=None, prefix=None):
    """NPC 位: a flagstone marker on the pavement. T8 replaces it with the actual NPC; until then
    the level shows where the four city NPCs stand."""
    cx, cy = centre
    tag = prefix or "NPC"
    count = _box(spawn, (cx, cy, 5.0), (80.0, 80.0, 10.0), material, tag + "_MARKER")
    log("npc slot at %d, %d: %d pieces" % (int(cx), int(cy), count))
    return count


def build_monster_slot(spawn, log, centre, material=None, wood=None, prefix=None):
    """怪位: a flat base with an upright stake on it.

    Deliberately unlike the NPC slab - a slab lying flat reads the same at a distance, and the
    wilderness needs the two kinds of marker to be tellable apart from the road. T7 puts real
    monsters on these.
    """
    cx, cy = centre
    tag = prefix or "MONSTER"
    count = _box(spawn, (cx, cy, 5.0), (90.0, 90.0, 10.0), material, tag + "_BASE")
    count += _box(spawn, (cx, cy, 55.0), (22.0, 22.0, 90.0), wood, tag + "_STAKE")
    log("monster slot at %d, %d: %d pieces" % (int(cx), int(cy), count))
    return count


def build_pavilion(spawn, log, centre, yaw=0.0, span=420.0, material=None, prefix=None):
    """驿亭: four pillars on stone footings under one gable roof, with no walls.

    A post station is a roof and a bench - shade and a place to stop, nothing to go inside. The span
    is wider than the village gate's so the eaves hang out past the posts, which is what separates a
    rest shelter from an entrance. One base slab keeps it off the sand.
    """
    cx, cy = centre
    tag = prefix or "PAVILION"
    count = _box(spawn, (cx, cy, 6.0), (span + 120.0, span + 120.0, 12.0), material, tag + "_BASE")

    post_h = PIECES["post"][1][2]
    for sx in (1.0, -1.0):
        for sy in (1.0, -1.0):
            point = _rot(sx * span * 0.5, sy * span * 0.5, yaw)
            label = "%s_POST_%d_%d" % (tag, int(sx), int(sy))
            count += _plinth(spawn, (cx + point[0], cy + point[1]), (70.0, 70.0), material,
                             label + "_FOOT")
            count += 1 if _spawn_piece(spawn, "post", (cx + point[0], cy + point[1]),
                                       PLINTH_H + post_h * 0.5, yaw, label) else 0

    ridge_z = PLINTH_H + post_h + 241.6 - ROOF_EAVE_OVERLAP
    for half_yaw in (0.0, 180.0):
        count += 1 if _spawn_roof_half(spawn, (cx, cy), ridge_z, yaw + 90.0 + half_yaw,
                                       "%s_ROOF_%d" % (tag, int(half_yaw))) else 0

    log("pavilion at %d, %d: %d pieces, %.0f cm span" % (int(cx), int(cy), count, span))
    return count
