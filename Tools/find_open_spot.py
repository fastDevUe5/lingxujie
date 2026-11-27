"""Find open space inside the city, and the ground height under it.

Placing a camera by guessing coordinates lands inside a wall, which is what the last few
screenshots were. This instead reads the city's own geometry: every group OBJ carries world
positions, so their footprints rasterise into an occupancy grid and the empty cells come out
as streets and plazas. The height field then supplies the ground level for whatever spot is
chosen.

The terrain is read once into a list - reading it per candidate cell made the first version of
this script take minutes rather than a second.

    python Tools/find_open_spot.py 17 [cell_cm]
"""

import os
import sys

ROOT = "C:/Users/tk/Desktop/lingxujie"
IMPORT_DIR = os.path.join(ROOT, "Assets", "Moxiang", "ue_import")
TERRAIN_CSV = "C:/Users/tk/Desktop/moxiang-study/terrain/%s.hfl.csv"

CELL_CM = 100.0


def load_terrain(map_id):
    rows = []
    with open(TERRAIN_CSV % map_id) as handle:
        for line in handle:
            if line.strip():
                rows.append([float(v) for v in line.split(",")])
    return rows


def height_at(rows, x, y):
    grid_x = int(round(x / CELL_CM))
    grid_z = int(round(-y / CELL_CM))
    if not (0 <= grid_z < len(rows)) or not (0 <= grid_x < len(rows[0])):
        return None
    return rows[grid_z][grid_x]


def occupied_cells(map_id, cell_cm):
    taken = set()
    vertices = 0
    for name in os.listdir(IMPORT_DIR):
        if not name.startswith("%s_arch_" % map_id) or not name.endswith(".obj"):
            continue
        with open(os.path.join(IMPORT_DIR, name), encoding="utf-8", errors="replace") as handle:
            for line in handle:
                if not line.startswith("v "):
                    continue
                parts = line.split()
                if len(parts) < 4:
                    continue
                taken.add((int(float(parts[1]) // cell_cm),
                           int(float(parts[2]) // cell_cm)))
                vertices += 1
    return taken, vertices


def main():
    map_id = sys.argv[1] if len(sys.argv) > 1 else "17"
    cell_cm = float(sys.argv[2]) if len(sys.argv) > 2 else 200.0

    taken, vertices = occupied_cells(map_id, cell_cm)
    print("map %s: %d vertices, %d occupied cells" % (map_id, vertices, len(taken)))

    rows = load_terrain(map_id)
    print("terrain: %dx%d" % (len(rows[0]), len(rows)))
    print("")

    best = []
    for gx in range(0, int(51800 / cell_cm)):
        for gy in range(int(-47000 / cell_cm), 1):
            if (gx, gy) in taken:
                continue
            open_count = 0
            for dx in (-2, -1, 0, 1, 2):
                for dy in (-2, -1, 0, 1, 2):
                    if (gx + dx, gy + dy) not in taken:
                        open_count += 1
            if open_count < 24:
                continue
            x = (gx + 0.5) * cell_cm
            y = (gy + 0.5) * cell_cm
            height = height_at(rows, x, y)
            if height is None:
                continue
            best.append((open_count, x, y, height))

    best.sort(reverse=True)
    print("most open spots (open_of_25, x, y, ground_z):")
    for open_count, x, y, height in best[:15]:
        print("  %2d  x=%6.0f  y=%7.0f  z=%5.0f" % (open_count, x, y, height))


if __name__ == "__main__":
    main()
