"""Turn one recovered map into geometry the editor can import.

Everything from the client is already in world centimetres: the height field covers a fifty-one thousand two hundred
centimetre square, and the static meshes were exported at the positions they occupy in that square. So the two can be
written straight out as OBJ, with one axis swap to match the engine - the client is Y up, the engine is Z up - and no
scaling at all, since a centimetre there is a centimetre here.

The height field is a 513 by 513 grid, which as raw triangles is half a million of them; that is a lot for one mesh but
it is the honest shape of the land, so it is written as a single grid and the engine can be told to build it once.

The architecture is split by texture rather than merged into one mesh. The research workspace's exact parser already
writes a `usemtl` group per face group into every `stm_exact` OBJ, and `<map>.mtl` names the texture behind each group,
so grouping the triangles by texture here is all that is needed to give the city its own materials back. The result is
one OBJ per texture plus `17_arch.json` listing them, and a PNG copy of every texture the map uses, converted from the
client's DDS/TIF/TGA because the engine will not read the client's DDS header.

    python Tools/build_map_obj.py --map 17
"""

import argparse
import json
import os

STUDY = "C:/Users/tk/Desktop/moxiang-study"
TERRAIN = os.path.join(STUDY, "terrain")
MESHES = os.path.join(STUDY, "stm_exact")
# The OBJs are engine import sources rather than research output, so they are written into the
# project's own assets where build_moxiang_map expects to find them.
OUT = "C:/Users/tk/Desktop/lingxujie/Assets/Moxiang/ue_import"
PNG_DIR = "C:/Users/tk/Desktop/lingxujie/Assets/Moxiang/textures"

# Where the client keeps its textures, in the order they are preferred. The DDS copies are the
# ones the game itself loads; TIF/TGA are the odd few that were only recovered in that format.
TEXTURE_DIRS = [os.path.join(STUDY, "resources", "dds"),
                os.path.join(STUDY, "resources", "tif"),
                os.path.join(STUDY, "resources", "tga")]
TEXTURE_EXTENSIONS = (".dds", ".tif", ".tga")

WORLD = 51200.0
MAX_TEXTURE = 2048
DEFAULT_TEXTURE = "untextured"


def terrain_obj(name, source, out_path, step=1):
    rows = []
    with open(source, encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            rows.append([float(value) for value in line.split(",")])
    height = len(rows)
    width = len(rows[0]) if rows else 0
    if not width:
        return None

    lines = ["# terrain from %s" % os.path.basename(source)]
    cell = WORLD / (width - 1)
    for z in range(0, height, step):
        for x in range(0, width, step):
            wx = x * cell
            wy = z * cell
            lines.append("v %.3f %.3f %.3f" % (wx, wy, rows[z][x]))
    # The importer requires a texture coordinate per vertex; without one it discards the whole
    # mesh, which showed up as a static mesh with zero triangles. A planar mapping is enough.
    span = float(max(width - 1, 1))
    for z in range(0, height, step):
        for x in range(0, width, step):
            lines.append("vt %.5f %.5f" % (x / span, z / span))
    columns = (width + step - 1) // step
    for z in range(0, (height - step) // step):
        for x in range(0, (width - step) // step):
            a = z * columns + x + 1
            b = a + 1
            c = a + columns
            d = c + 1
            # Wound counter-clockwise as seen from above. The other order faces down, and the
            # engine culls it, which tears the land into floating patches.
            lines.append("f %d/%d %d/%d %d/%d" % (a, a, b, b, c, c))
            lines.append("f %d/%d %d/%d %d/%d" % (b, b, d, d, c, c))

    with open(out_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    return width, height, len(lines)


def safe_name(text):
    """An asset-safe form of a texture name: lower case, letters/digits/underscore only."""
    cleaned = "".join(char if (char.isalnum() or char == "_") else "_"
                      for char in (text or "").lower())
    return cleaned.strip("_") or DEFAULT_TEXTURE


def texture_stem(texture):
    """The file stem of a material's texture, without its extension."""
    return os.path.splitext(os.path.basename((texture or "").strip()))[0]


def read_mtl(path):
    """Return {material name: texture file name} from the OBJ's own material library."""
    textures = {}
    current = None
    if not os.path.exists(path):
        return textures
    with open(path, encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if line.startswith("newmtl "):
                current = line.split(None, 1)[1]
            elif current and line.lower().startswith("map_kd "):
                textures[current] = line.split(None, 1)[1].strip()
    return textures


def texture_index():
    """{lower-case stem: path} over the client's texture folders."""
    index = {}
    for folder in TEXTURE_DIRS:
        if not os.path.isdir(folder):
            continue
        for name in sorted(os.listdir(folder)):
            stem, extension = os.path.splitext(name)
            if extension.lower() not in TEXTURE_EXTENSIONS:
                continue
            index.setdefault(stem.lower(), os.path.join(folder, name))
    return index


def convert_texture(stem, source, out_dir):
    """Copy one client texture out as PNG. Returns (path, masked) or (None, False)."""
    try:
        from PIL import Image
    except ImportError:
        return None, False
    try:
        image = Image.open(source)
        has_alpha = (image.mode in ("RGBA", "LA")
                     or (image.mode == "P" and "transparency" in image.info))
        if has_alpha:
            image = image.convert("RGBA")
            low = image.getchannel("A").getextrema()[0]
            masked = low < 128
        else:
            image = image.convert("RGB")
            masked = False
        if max(image.size) > MAX_TEXTURE:
            scale = float(MAX_TEXTURE) / max(image.size)
            image = image.resize((max(1, int(image.width * scale)),
                                  max(1, int(image.height * scale))))
        target = os.path.join(out_dir, stem + ".png")
        image.save(target, "PNG", optimize=True)
        return target, masked
    except Exception as error:  # noqa: BLE001
        print("  texture %-24s FAILED: %s" % (stem, error))
        return None, False


def merge_architecture(prefix, mesh_dir, out_dir):
    """Split the map's meshes by texture and write one OBJ per texture.

    The importer drops any mesh whose faces reference no texture coordinate, so both arrays are
    carried across and the face lines keep the v/vt form the source files already use. OBJ requires
    every v and vt to appear before the faces that reference them, so each texture's arrays are
    collected first and written in that order.

    Returns a list of group records, one per texture, for the engine-side manifest.
    """
    materials = read_mtl(os.path.join(mesh_dir, prefix + ".mtl"))
    names = sorted(name for name in os.listdir(mesh_dir)
                   if name.startswith(prefix + "_") and name.endswith(".obj"))
    buckets = {}
    for name in names:
        vertices = []
        texcoords = []
        faces_by_material = {}
        current = None
        with open(os.path.join(mesh_dir, name), encoding="utf-8",
                  errors="replace") as handle:
            for line in handle:
                if line.startswith("v "):
                    vertices.append(line[2:].strip())
                elif line.startswith("vt "):
                    texcoords.append(line[3:].strip())
                elif line.startswith("usemtl "):
                    current = line.split(None, 1)[1].strip()
                elif line.startswith("f "):
                    triangle = []
                    for part in line[2:].split():
                        pieces = part.split("/")
                        vertex = int(pieces[0])
                        texcoord = int(pieces[1]) if len(pieces) > 1 and pieces[1] else vertex
                        triangle.append((vertex, texcoord))
                    key = current or DEFAULT_TEXTURE
                    if key not in faces_by_material:
                        faces_by_material[key] = []
                    faces_by_material[key].append(triangle)

        for material, triangles in faces_by_material.items():
            texture = materials.get(material, "")
            raw = texture_stem(texture) or DEFAULT_TEXTURE
            stem = safe_name(raw)
            bucket = buckets.get(stem)
            if bucket is None:
                # The raw name is kept for finding the file on disk; the sanitised stem names the
                # OBJ and the engine assets, because a client texture called jp_wall00-2 is not a
                # valid asset name.
                bucket = buckets[stem] = {"texture": raw, "vertices": [], "texcoords": [],
                                          "faces": [], "meshes": 0}
            # A fresh source mesh starts a fresh local index space, so the map is new per mesh.
            mapping = {}
            bucket["meshes"] += 1
            for triangle in triangles:
                face = []
                for vertex, texcoord in triangle:
                    if vertex not in mapping:
                        mapping[vertex] = len(bucket["vertices"]) + 1
                        x, y, z = vertices[vertex - 1].split()
                        bucket["vertices"].append("%s %s %s" % (x, z, y))
                        if 0 < texcoord <= len(texcoords):
                            bucket["texcoords"].append(texcoords[texcoord - 1])
                        else:
                            bucket["texcoords"].append("0.00000 0.00000")
                    face.append(mapping[vertex])
                bucket["faces"].append(face)

    records = []
    for stem in sorted(buckets):
        bucket = buckets[stem]
        if not bucket["faces"]:
            continue
        target = "%s_arch_%s.obj" % (prefix, stem)
        with open(os.path.join(out_dir, target), "w", encoding="utf-8") as handle:
            handle.write("# %s architecture, texture %s, %d meshes\n"
                         % (prefix, bucket["texture"] or stem, bucket["meshes"]))
            for vertex in bucket["vertices"]:
                handle.write("v " + vertex + "\n")
            for texcoord in bucket["texcoords"]:
                handle.write("vt " + texcoord + "\n")
            for face in bucket["faces"]:
                handle.write("f " + " ".join("%d/%d" % (index, index) for index in face) + "\n")
        records.append({
            "texture": bucket["texture"],
            "slug": stem,
            "obj": target,
            "mesh": "SM_LZ_" + stem.upper(),
            "material": "M_LZ_" + stem.upper(),
            "label": "MX_LZ_" + stem.upper(),
            "vertices": len(bucket["vertices"]),
            "triangles": len(bucket["faces"]),
            "meshes": bucket["meshes"],
        })
    return records, materials


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--map", default="22")
    parser.add_argument("--step", type=int, default=1)
    args = parser.parse_args()

    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PNG_DIR, exist_ok=True)

    terrain_source = os.path.join(TERRAIN, "%s.hfl.csv" % args.map)
    if os.path.exists(terrain_source):
        result = terrain_obj(args.map, terrain_source,
                             os.path.join(OUT, "%s_terrain.obj" % args.map),
                             args.step)
        if result:
            print("terrain: %d x %d grid, %d lines" % result)

    records, materials = merge_architecture(args.map, MESHES, OUT)

    index = texture_index()
    found = 0
    missing = []
    masked = 0
    for record in records:
        stem = record["texture"].lower()
        source = index.get(stem)
        if source is None:
            record["png"] = None
            record["masked"] = False
            missing.append(record["texture"])
            continue
        target, is_masked = convert_texture(record["slug"], source, PNG_DIR)
        record["png"] = os.path.basename(target) if target else None
        record["masked"] = is_masked
        if target:
            found += 1
        if is_masked:
            masked += 1

    manifest = {"map": args.map,
                "terrain": "%s_terrain.obj" % args.map,
                "groups": records}
    with open(os.path.join(OUT, "%s_arch.json" % args.map), "w",
              encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=1, ensure_ascii=False)

    triangles = sum(record["triangles"] for record in records)
    vertices = sum(record["vertices"] for record in records)
    print("architecture: %d meshes, %d textures, %d vertices, %d triangles"
          % (sum(record["meshes"] for record in records), len(records),
             vertices, triangles))
    print("textures: %d converted, %d masked, %d missing" % (found, masked, len(missing)))
    for name in missing:
        print("  missing texture: %s" % name)

    for name in sorted(os.listdir(OUT)):
        path = os.path.join(OUT, name)
        print("  %-32s %8.1f MB" % (name, os.path.getsize(path) / 1024 / 1024))


if __name__ == "__main__":
    main()
