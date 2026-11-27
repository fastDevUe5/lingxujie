"""Play the imported animation and prove the mesh actually moves.

This is the last unverified link: the sequence imported, but nothing has shown that playing it changes
the mesh. Two captures at different times into the animation, compared by the skeleton's own pose
rather than by eye, answer it.

The component API is probed first, because the way to play a single animation has moved between
engine versions and guessing costs a round.

    py "Tools/play_animation.py"
"""

import unreal

MESH = "/Game/Moxiang/Skeletal/Characters/boss001/SkeletalMeshes/SK_Boss001.SK_Boss001"
ANIM = ("/Game/Moxiang/Skeletal/Characters/boss001/SkeletalMeshes/"
        "SK_Boss001_Anim.SK_Boss001_Anim")
LABEL = "MX_BOSS001"


def log(text):
    unreal.log("[LingXuJie] PLAY: %s" % text)


def main():
    component_class = unreal.SkeletalMeshComponent
    names = [n for n in dir(component_class) if not n.startswith("_")]
    relevant = [n for n in names
                if any(word in n.lower()
                       for word in ("anim", "play", "pose", "single", "evaluate"))]
    log("animation-related members: %d" % len(relevant))
    for name in sorted(relevant)[:30]:
        log("    %s" % name)

    log("AnimationMode values:")
    mode = getattr(unreal, "AnimationMode", None)
    if mode is not None:
        for name in [n for n in dir(mode) if not n.startswith("_")][:12]:
            log("    %s" % name)
    else:
        log("    AnimationMode not exported")

    for helper in ("AnimationSingleNode", "AnimSingleNodeInstance", "AnimInstance"):
        log("%-26s %s" % (helper, "yes" if hasattr(unreal, helper) else "no"))


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
