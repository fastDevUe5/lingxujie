"""Find the evaluation-type enum get_anim_pose_at_time expects.

The call reports a missing evaluation_type, so the enum has to exist somewhere in the reflected API.
Listing candidates is faster than guessing names one at a time.

    py "Tools/probe_eval_type.py"
"""

import unreal


def log(text):
    unreal.log("[LingXuJie] EV: %s" % text)


try:
    # Anything in the module whose name mentions pose or evaluation.
    names = [n for n in dir(unreal) if not n.startswith("_")]
    candidates = [n for n in names
                  if ("evaluation" in n.lower() or "evaltype" in n.lower()
                      or n.lower().startswith("animpose"))]
    log("candidate enums/classes: %s" % candidates)

    for name in candidates:
        obj = getattr(unreal, name)
        try:
            members = [m for m in dir(obj) if not m.startswith("_")]
        except Exception:  # noqa: BLE001
            continue
        log("%s: %s" % (name, members[:14]))

    # The enum may live on the extension class or under a different name.
    extensions = unreal.AnimPoseExtensions
    for member in [m for m in dir(extensions) if not m.startswith("_")]:
        if "eval" in member.lower() or "pose" in member.lower():
            log("extension member: %s" % member)

    # Sometimes the enum value is reachable as a plain integer constant.
    for name in ("ANIM_POSE_EVALUATION_TYPE_NORMAL", "AnimPoseEvaluationType",
                 "AnimPoseEvaluationType.NORMAL"):
        target = unreal
        found = True
        for part in name.split("."):
            target = getattr(target, part, None)
            if target is None:
                found = False
                break
        log("%-42s %s" % (name, target if found else "no"))
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())

log("done")
