"""Export a batch of models, pairing each with whatever animation shares its name.

Doing one model at a time proved the pipeline; this makes it useful. The pairing rule is that a
model and its animation share a stem - `198_bobu.mod` and `198_bobu.anm` - which holds for the
character set. Where no animation exists the model is still exported, because a static pose is
worth having.

The point of a batch run is the report as much as the files: how many exported, and what the
failures have in common. A batch that quietly skips half its input is worse than one that fails
loudly on the first file.

    python Tools/batch_export.py [--limit N] [--pattern TEXT]
"""

import os
import sys
import traceback

import export_mod_anim_gltf as exporter
import parse_chx

MOD_FOLDER = "C:/Users/tk/Desktop/moxiang-study/resources/mod"
ANM_FOLDER = "C:/Users/tk/Desktop/moxiang-study/resources/anm"
OUT_FOLDER = "C:/Users/tk/Desktop/lingxujie/Assets/Moxiang/ue_import/batch"

# Built once: model stem -> list of animation stems, from the .chx containers. Name guessing works
# for some sets and fails badly for others, so the container is the authority where it exists.
CHX_MAP = {}


def log(text):
    print(text)


def build_chx_map():
    global CHX_MAP
    try:
        mapping, unparsed = parse_chx.build_map()
    except Exception as error:  # noqa: BLE001
        log("chx map unavailable (%s); falling back to name matching" % error)
        return
    CHX_MAP = mapping
    log("chx map: %d models, %d unparsed"
        % (len(mapping), len(unparsed)))


def resolve_animation(stem, model_bones=()):
    """Pick the animation that best matches this model's skeleton.

    A .chx entry lists everything the model needs, and that list mixes categories: one file drives
    the skeleton's bones, while others drive effect meshes - fireballs, smoke, fog planes - which
    animate scale only and whose track names are not bone names at all. Taking the first entry
    therefore sometimes picks an effect, and sometimes picks a skeleton file that animates only the
    tail because that is all that particular motion moves.

    Scoring each candidate by how many of its tracks name a bone in this model separates the two
    without needing to know which is which.
    """
    listed = CHX_MAP.get(stem.lower())
    if not listed:
        path = find_animation(stem)
        return path, ([os.path.splitext(os.path.basename(path))[0]] if path else []), 0

    bone_names = {name.lower() for name in model_bones}
    candidates = []
    for candidate in listed:
        path = None
        for variant in (candidate, candidate.lower(), candidate.upper()):
            probe = os.path.join(ANM_FOLDER, variant + ".anm")
            if os.path.exists(probe):
                path = probe
                break
        if path is None:
            # Case differs between the listing and disk; scan once.
            wanted = candidate.lower()
            for filename in os.listdir(ANM_FOLDER):
                if filename.lower() == wanted + ".anm":
                    path = os.path.join(ANM_FOLDER, filename)
                    break
        if path is None:
            continue
        candidates.append((candidate, path))

    if not candidates:
        return None, listed, 0

    best = None
    best_score = -1
    for candidate, path in candidates:
        tracks = exporter.parse_anm(path)
        score = sum(1 for name in tracks if name.lower() in bone_names)
        if score > best_score:
            best_score = score
            best = (candidate, path)

    if best_score <= 0:
        # Nothing matches the skeleton: fall back to the first entry so a static pose is still
        # exported, and report the score as zero so the run shows it.
        candidate, path = candidates[0]
        return path, listed, 0

    return best[1], listed, best_score


def find_animation(stem):
    """Animations are named either exactly after the model or with a short suffix.

    The suffix is appended without a separator for some sets - `108_bird` pairs with
    `108_birda.anm` - while other sets use an underscore. Both forms are tried.
    """
    candidates = [stem + ".anm"]
    for suffix in ("a", "b", "c", "_01", "_1", "_idle", "_a"):
        candidates.append(stem + suffix + ".anm")
    for candidate in candidates:
        path = os.path.join(ANM_FOLDER, candidate)
        if os.path.exists(path):
            return path
    return None


def export_one(mod_path, out_path):
    objects = exporter.parse_mod(mod_path)
    bones = [o for o in objects if o["marker"] == exporter.MOD_BONE_MARKER]
    meshes = [o for o in objects if o["marker"] == exporter.MOD_MESH_MARKER]
    if not meshes:
        return None, "no mesh blocks"

    stem = os.path.splitext(os.path.basename(mod_path))[0]
    animation, listed, matched = resolve_animation(
        stem, [bone["name"] for bone in bones])
    tracks = exporter.parse_anm(animation) if animation else {}

    gltf, blob = exporter.build(objects, tracks, stem)

    folder = os.path.dirname(out_path)
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)
    bin_path = os.path.splitext(out_path)[0] + ".bin"
    with open(bin_path, "wb") as handle:
        handle.write(blob)
    gltf["buffers"][0]["uri"] = os.path.basename(bin_path)

    import json
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(gltf, handle, indent=1)

    channels = len(gltf.get("animations", [{}])[0].get("channels", [])) if "animations" in gltf else 0
    return {
        "stem": stem,
        "bones": len(bones),
        "meshes": len(meshes),
        "animation": os.path.basename(animation) if animation else None,
        "available": len(listed),
        "matched": matched,
        "available": len(listed),
        "matched": matched,
        "channels": channels,
        "bytes": os.path.getsize(out_path),
    }, None


def main():
    limit = 40
    pattern = ""
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == "--limit" and i + 1 < len(args):
            limit = int(args[i + 1])
        if arg == "--pattern" and i + 1 < len(args):
            pattern = args[i + 1]

    build_chx_map()

    build_chx_map()

    names = sorted(n for n in os.listdir(MOD_FOLDER) if n.endswith(".mod"))
    if pattern:
        names = [n for n in names if pattern in n]
    log("candidate models: %d (limit %d, pattern %r)" % (len(names), limit, pattern))
    log("")

    ok = []
    skipped = []
    failed = []
    considered = 0

    for name in names:
        if len(ok) >= limit:
            break
        considered += 1
        path = os.path.join(MOD_FOLDER, name)
        out = os.path.join(OUT_FOLDER, os.path.splitext(name)[0] + ".gltf")
        try:
            result, reason = export_one(path, out)
        except Exception as error:  # noqa: BLE001
            failed.append((name, "%s: %s" % (type(error).__name__, error)))
            continue
        if result is None:
            skipped.append((name, reason))
            continue
        ok.append(result)

    log("")
    log("=" * 76)
    log("exported %d of %d considered" % (len(ok), considered))
    log("")
    log("%-22s %-6s %-7s %-8s %-20s %s"
        % ("model", "bones", "meshes", "channels", "animation", "gltf bytes"))
    log("-" * 88)
    for row in ok[:30]:
        log("%-22s %-6d %-7d %-8d %-20s %d"
            % (row["stem"][:22], row["bones"], row["meshes"], row["channels"],
               (row["animation"] or "-")[:20], row["bytes"]))

    if skipped:
        log("")
        log("skipped %d:" % len(skipped))
        reasons = {}
        for name, reason in skipped:
            reasons.setdefault(reason, []).append(name)
        for reason, group in reasons.items():
            log("  %-30s %d files (e.g. %s)" % (reason, len(group), group[0]))

    if failed:
        log("")
        log("failed %d:" % len(failed))
        for name, reason in failed[:10]:
            log("  %-30s %s" % (name, reason))

    animated = sum(1 for row in ok if row["channels"])
    log("")
    log("summary: %d exported, %d with animation, %d skipped, %d failed"
        % (len(ok), animated, len(skipped), len(failed)))
    if ok:
        log("total output %.1f MB" % (sum(r["bytes"] for r in ok) / (1024.0 * 1024.0)))


if __name__ == "__main__":
    main()
