"""Case 002, step one: measure the bad normals and tangents on the imported boss mesh.

The import warnings claim NaN tangents and near-zero normals. Before deciding what that means for
rendering, count them: how many vertices are affected, how many are exactly zero, and whether the
tangent data is genuinely non-finite.

    py "Tools/diag_normals_step1.py"
"""

import math

import unreal


def log(text):
    unreal.log("[LingXuJie] N1: %s" % text)


def main():
    reg = unreal.AssetRegistryHelpers.get_asset_registry()
    mesh = None
    for asset in reg.get_assets_by_path("/Game/Moxiang/Static", True, False):
        if str(asset.asset_class_path.asset_name) == "StaticMesh":
            full = "%s.%s" % (asset.package_name, asset.asset_name)
            log("found static mesh: %s" % full)
            mesh = unreal.load_asset(full)
            break

    if mesh is None:
        log("no static mesh under /Game/Moxiang/Static")
        return

    log("mesh: %s" % mesh.get_path_name())
    log("num lod levels: %r" % mesh.get_num_lod_levels())
    for lod in range(mesh.get_num_lod_levels()):
        log("  LOD %d: %d vert(s), %d tri(s)"
            % (lod, mesh.get_num_vertices(lod), mesh.get_num_triangles(lod)))

    # Read the render data. Normals live in the position vertex buffer, tangents in a separate one.
    try:
        render_data = mesh.get_render_data()
        log("render_data acquired: %r" % (render_data is not None))
    except Exception as error:  # noqa: BLE001
        log("get_render_data raised: %r" % error)
        render_data = None

    if render_data is None:
        log("cannot read render data from Python; falling back to a source-side check")
        return

    try:
        vertex_buffer = render_data.get_vertex_buffer()
        log("vertex buffer: %r" % (vertex_buffer is not None))
        if vertex_buffer:
            positions = vertex_buffer.get_vertex_positions()
            log("positions: %d" % len(positions))
    except Exception as error:  # noqa: BLE001
        log("vertex buffer access raised: %r" % error)

    # Count normals that are zero or near zero, straight from the asset's own data.
    try:
        normals = render_data.get_normals()
    except Exception:  # noqa: BLE001
        normals = None

    if normals is None:
        log("no normals accessor on render data; listing what it does expose:")
        for name in sorted(dir(render_data)):
            if not name.startswith("_"):
                log("    %s" % name)
        return

    zero = 0
    near = 0
    bad = 0
    total = len(normals)
    for n in normals:
        length = math.sqrt(n.x * n.x + n.y * n.y + n.z * n.z)
        if not math.isfinite(length):
            bad += 1
        elif length == 0.0:
            zero += 1
        elif abs(length - 1.0) > 1e-3:
            near += 1

    log("normals: %d total, %d exactly zero, %d not unit length, %d non-finite"
        % (total, zero, near, bad))

    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
