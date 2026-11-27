"""A Chinese village house generated from primitives, painted with our own texture sheets.

The reference study (Docs/Reference/MoXiang/) splits the look in two:
  * village houses: whitewashed walls, a dark timber frame, a STEEP brown thatch/shingle roof,
    small windows and one little gable dormer;
  * towns, gates and shrines: glazed tile (green or grey), 歇山/十字脊 roofs, upturned corners.

墨香 is a 2007 low-poly game, so its detail lives in the textures, not the meshes: tile courses,
straw, lime-wash stains and lattice windows are all painted sheets (Tools/paint_textures.py). This
file builds the simple geometry those sheets need - slabs, boards and posts - and closes the gable
with two boards laid flat against the roof's underside.
"""

import math

import unreal

CUBE = "/Engine/BasicShapes/Cube.Cube"
PLANE = "/Engine/BasicShapes/Plane.Plane"

# Proportions in cm: a village house is wider along the street than it is deep, with a steep pitch
# and deep eaves - the overhang is what reads as 古风 rather than as a shed.
DEFAULT_WIDTH = 620.0      # along X (how far it sets back from the street)
DEFAULT_DEPTH = 660.0      # along Y (the facade the street sees)
DEFAULT_WALL_H = 290.0
DEFAULT_PITCH = 30.0       # degrees; the Lanzhou screenshots measure about 30, not the 38 of thatch
EAVE_Y = 95.0              # roof overhang past the facade
EAVE_X = 75.0              # roof overhang past the gable ends
PLINTH_H = 40.0
WALL_T = 26.0
FRAME = 28.0


def _spawn_mesh(spawn, mesh_path, centre, size, material, label, rotation=(0.0, 0.0, 0.0)):
    actor = spawn(unreal.StaticMeshActor, centre, rotation=rotation, label=label)
    if actor is None:
        return None
    component = actor.static_mesh_component
    try:
        component.set_mobility(unreal.ComponentMobility.STATIC)
    except Exception:  # noqa: BLE001
        pass
    component.set_static_mesh(unreal.load_asset(mesh_path))
    if material is not None:
        component.set_material(0, material)
    actor.set_actor_scale3d(unreal.Vector(size[0] / 100.0, size[1] / 100.0, size[2] / 100.0))
    return actor


def build_house(spawn, log, centre, yaw=0.0, width=DEFAULT_WIDTH, depth=DEFAULT_DEPTH,
                wall_h=DEFAULT_WALL_H, pitch=DEFAULT_PITCH, materials=None, prefix=None):
    """One house. The door faces +X in local space, rotated by yaw."""
    cx, cy = centre
    materials = materials or {}
    stone = materials.get("stone")
    plaster = materials.get("paint_wall") or materials.get("plaster_white") or materials.get("wall")
    wood = materials.get("paint_wood") or materials.get("wood_dark") or materials.get("wood")
    brace = materials.get("paint_wood_tan") or wood
    roof = materials.get("paint_tile_red") or materials.get("paint_tile_grey") or materials.get("roof")
    ridge_tile = materials.get("paint_ridge") or materials.get("paint_tile_grey") or roof
    soffit = materials.get("paint_soffit") or wood
    lattice = materials.get("paint_lattice")
    lantern = materials.get("paint_lantern")
    tag = prefix or "SAMPLE_%d_%d" % (int(cx), int(cy))
    count = 0

    def to_world(dx, dy):
        rad = math.radians(yaw)
        return (cx + dx * math.cos(rad) - dy * math.sin(rad),
                cy + dx * math.sin(rad) + dy * math.cos(rad))

    def at(dx, dy, z, size, material, label, rotation=(0.0, 0.0, 0.0), mesh_path=CUBE):
        point = to_world(dx, dy)
        actor = _spawn_mesh(spawn, mesh_path, (point[0], point[1], z), size, material, label,
                            rotation=(rotation[0], rotation[1], yaw + rotation[2]))
        return 1 if actor is not None else 0

    half_w, half_d = width * 0.5, depth * 0.5
    wall_base = PLINTH_H
    wall_top = wall_base + wall_h

    # Stone plinth and the doorstep.
    count += at(0.0, 0.0, PLINTH_H * 0.5, (width + 90.0, depth + 90.0, PLINTH_H), stone, tag + "_PLINTH")
    count += at(half_w + 45.0, 0.0, 10.0, (110.0, 120.0, 20.0), stone, tag + "_STEP")

    # Four wall panels.
    count += at(0.0, half_d, wall_base + wall_h * 0.5, (width, WALL_T, wall_h), plaster, tag + "_WALL_F")
    count += at(0.0, -half_d, wall_base + wall_h * 0.5, (width, WALL_T, wall_h), plaster, tag + "_WALL_B")
    count += at(half_w, 0.0, wall_base + wall_h * 0.5, (WALL_T, depth, wall_h), plaster, tag + "_WALL_R")
    count += at(-half_w, 0.0, wall_base + wall_h * 0.5, (WALL_T, depth, wall_h), plaster, tag + "_WALL_L")

    # Timber frame: corner posts, a top beam (檐枋) and a mid rail (腰枋).
    for index, (px, py) in enumerate(((half_w, half_d), (half_w, -half_d),
                                      (-half_w, half_d), (-half_w, -half_d))):
        count += at(px, py, wall_base + wall_h * 0.5, (FRAME, FRAME, wall_h + 40.0), wood,
                    "%s_POST%d" % (tag, index))
    # 木构分格: intermediate posts along both long facades, so the wall reads as framed panels
    # instead of one flat slab (the Lanzhou screenshots show blue-grey posts dividing the plaster).
    for index in range(1, 4):
        offset = -half_d + depth * index / 4.0
        for facade in (1.0, -1.0):
            count += at(facade * half_w, offset, wall_base + wall_h * 0.5,
                        (FRAME * 0.8, FRAME * 0.8, wall_h), wood,
                        "%s_MPOST%d%d" % (tag, int(facade), index))
    for side in (1.0, -1.0):
        count += at(0.0, side * half_d, wall_top - 10.0, (width + 30.0, FRAME, 26.0), wood,
                    "%s_BEAM%d" % (tag, int(side)))
        count += at(0.0, side * half_d, wall_base + wall_h * 0.52, (width + 30.0, FRAME * 0.7, 18.0),
                    wood, "%s_RAIL%d" % (tag, int(side)))
        count += at(side * half_w, 0.0, wall_top - 10.0, (FRAME, depth + 30.0, 26.0), wood,
                    "%s_SBEAM%d" % (tag, int(side)))

    # Door on the +X facade.
    count += at(half_w + 14.0, 0.0, wall_base + 105.0, (16.0, 130.0, 210.0), wood, tag + "_DOOR")
    count += at(half_w + 8.0, 0.0, wall_base + 110.0, (14.0, 172.0, 220.0), wood, tag + "_DOORFRAME")

    # Lattice windows: one masked plane each, so the sheet's alpha cuts the grid.
    if lattice is not None:
        for facade in (1.0, -1.0):
            for side in (1.0, -1.0):
                count += at(facade * (half_w + 12.0), side * 195.0, wall_base + 180.0,
                            (96.0, 96.0, 1.0), lattice,
                            "%s_WIN%s%s" % (tag, int(facade), int(side)),
                            rotation=(0.0, 90.0 * facade, 0.0), mesh_path=PLANE)
                # A timber surround so the lattice does not float on the plaster.
                count += at(facade * (half_w + 10.0), side * 195.0, wall_base + 180.0,
                            (10.0, 112.0, 112.0), wood, "%s_WINFRAME%s%s" % (tag, int(facade), int(side)))

    # Gable roof: two steep slabs, a ridge cap, dark eave boards.
    theta = math.radians(pitch)
    tan_theta = math.tan(theta)
    half_span = half_d + EAVE_Y
    drop = half_span * tan_theta
    ridge_z = wall_top + drop
    slab_len = half_span / math.cos(theta)
    slab_width = width + EAVE_X * 2.0
    for side in (1.0, -1.0):
        count += at(0.0, side * half_span * 0.5, ridge_z - drop * 0.5,
                    (slab_width, slab_len, 14.0), roof,
                    "%s_ROOF%d" % (tag, int(side)), rotation=(side * pitch, 0.0, 0.0))
        count += at(0.0, side * (half_span - 16.0), ridge_z - drop - 18.0,
                    (slab_width, 26.0, 22.0), wood, "%s_EAVE%d" % (tag, int(side)))
    count += at(0.0, 0.0, ridge_z + 12.0, (slab_width, 44.0, 32.0), ridge_tile, tag + "_RIDGE")

    # Close the gable ends with an alpha-cut triangle: the sheet's opaque triangle is exactly the
    # roof's cross-section, so one plane per end closes it with no boxes poking through the thatch.
    # A plane rotated to face +X maps its U axis to world Z, hence the U-oriented sheet.
    gable = materials.get("paint_gable")
    if gable is not None:
        for side_x in (1.0, -1.0):
            count += at(side_x * (half_w + 4.0), 0.0, wall_top + drop * 0.5,
                        (drop, depth - 6.0, 1.0), gable,
                        "%s_GABLE%d" % (tag, int(side_x)),
                        rotation=(0.0, 90.0, 180.0 if side_x < 0.0 else 0.0), mesh_path=PLANE)

    # 博风板: a fascia board along each gable edge, so the roof does not read as a bare slab edge.
    for side_x in (1.0, -1.0):
        for side_y in (1.0, -1.0):
            count += at(side_x * (half_w + EAVE_X - 10.0), side_y * half_span * 0.5,
                        ridge_z - drop * 0.5, (20.0, slab_len * 1.02, 54.0), brace,
                        "%s_BOFENG%s%s" % (tag, int(side_x), int(side_y)),
                        rotation=(side_y * pitch, 0.0, 0.0))

    # 檐底彩画: a green painted board under each eave - the most recognisable 墨香 eave detail.
    for side in (1.0, -1.0):
        count += at(0.0, side * (half_span - 44.0), ridge_z - drop - 4.0,
                    (slab_width, 110.0, 6.0), soffit, "%s_SOFFIT%d" % (tag, int(side)))

    # 翘角: four upturned tips at the roof corners (the "beak" that reads as 古风 at a glance).
    for side_x in (1.0, -1.0):
        for side_y in (1.0, -1.0):
            corner = to_world(side_x * (half_w + EAVE_X - 30.0),
                              side_y * (half_span - 30.0))
            _spawn_mesh(spawn, CUBE, (corner[0], corner[1], ridge_z - drop + 26.0),
                        (92.0, 22.0, 14.0), roof,
                        "%s_WING%s%s" % (tag, int(side_x), int(side_y)),
                        rotation=(0.0, -side_y * 30.0, yaw + 40.0 * side_x * side_y))
            count += 1

    # 匾额: white board with a dark frame over the door, hung under the eave.
    count += at(half_w + 10.0, 0.0, wall_top + 44.0, (14.0, 190.0, 62.0), wood, tag + "_PLAQUE_FRAME")
    count += at(half_w + 20.0, 0.0, wall_top + 44.0, (8.0, 168.0, 46.0), plaster, tag + "_PLAQUE")

    # 太极灯笼: a pair of alpha lanterns either side of the door.
    if lantern is not None:
        for side in (1.0, -1.0):
            count += at(half_w + 40.0, side * 150.0, wall_top - 6.0,
                        (48.0, 48.0, 48.0), lantern,
                        "%s_LANTERN%d" % (tag, int(side)),
                        rotation=(90.0, 0.0, 0.0), mesh_path=PLANE)

    log("chinese house at %d, %d: %d pieces (%.0f x %.0f cm, %.0f deg)"
        % (int(cx), int(cy), count, width, depth, pitch))
    return count


def build_cross_ridge_pavilion(spawn, log, centre, yaw=0.0, width=620.0, depth=620.0,
                               pillar_h=280.0, pitch=30.0, materials=None, prefix=None):
    """十字脊 pavilion: two gable roofs crossing at 90 degrees plus four upturned corners."""
    cx, cy = centre
    materials = materials or {}
    stone = materials.get("stone")
    wood = materials.get("paint_wood") or materials.get("wood_dark") or materials.get("wood")
    roof = materials.get("paint_tile_red") or materials.get("paint_tile_grey") or materials.get("roof")
    tag = prefix or "PAVILION"
    count = 0
    theta = math.radians(pitch)

    def to_world(dx, dy):
        rad = math.radians(yaw)
        return (cx + dx * math.cos(rad) - dy * math.sin(rad),
                cy + dx * math.sin(rad) + dy * math.cos(rad))

    def at(dx, dy, z, size, material, label, rotation=(0.0, 0.0, 0.0)):
        point = to_world(dx, dy)
        actor = _spawn_mesh(spawn, CUBE, (point[0], point[1], z), size, material, label,
                            rotation=(rotation[0], rotation[1], yaw + rotation[2]))
        return 1 if actor is not None else 0

    count += at(0.0, 0.0, 20.0, (width + 90.0, depth + 90.0, 40.0), stone, tag + "_BASE")
    for index, (px, py) in enumerate(((width * 0.4, depth * 0.4), (width * 0.4, -depth * 0.4),
                                      (-width * 0.4, depth * 0.4), (-width * 0.4, -depth * 0.4))):
        count += at(px, py, 40.0 + pillar_h * 0.5, (30.0, 30.0, pillar_h), wood,
                    "%s_POST%d" % (tag, index))

    base_z = 40.0 + pillar_h
    half = min(width, depth) * 0.5 + 70.0
    drop = half * math.tan(theta)
    top_z = base_z + drop
    slab_len = half / math.cos(theta)

    for side in (1.0, -1.0):
        count += at(0.0, side * half * 0.5, top_z - drop * 0.5,
                    (width + 220.0, slab_len, 14.0), roof,
                    "%s_ROOFY%d" % (tag, int(side)), rotation=(side * pitch, 0.0, 0.0))
        count += at(side * half * 0.5, 0.0, top_z - drop * 0.5,
                    (slab_len, depth + 220.0, 14.0), roof,
                    "%s_ROOFX%d" % (tag, int(side)), rotation=(0.0, -side * pitch, 0.0))
    count += at(0.0, 0.0, top_z + 14.0, (width + 260.0, 46.0, 34.0), roof, tag + "_RIDGE_X")
    count += at(0.0, 0.0, top_z + 30.0, (46.0, depth + 260.0, 34.0), roof, tag + "_RIDGE_Y")

    for side_x in (1.0, -1.0):
        for side_y in (1.0, -1.0):
            corner = to_world(side_x * half * 0.92, side_y * half * 0.92)
            _spawn_mesh(spawn, CUBE, (corner[0], corner[1], top_z - drop + 40.0),
                        (150.0, 30.0, 18.0), roof,
                        "%s_UPTURN%d%d" % (tag, int(side_x), int(side_y)),
                        rotation=(0.0, -side_x * 22.0, yaw + 45.0))
            count += 1

    log("cross-ridge pavilion at %d, %d: %d pieces" % (int(cx), int(cy), count))
    return count
