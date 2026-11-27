"""Find the Python API that reports a skeleton's bone transforms.

Reading the pose back is the whole point of the experiment, so guessing method names is wasted time.
This lists what the reflection system actually exposes on the relevant classes.

    py "Tools/find_bone_api.py"
"""

import unreal


def log(text):
    unreal.log("[LingXuJie] BONEAPI: %s" % text)


def describe(class_name):
    cls = getattr(unreal, class_name, None)
    if cls is None:
        log("%s: not exported to Python" % class_name)
        return
    names = [name for name in dir(cls) if not name.startswith("_")]
    interesting = [name for name in names
                   if any(word in name.lower()
                          for word in ("bone", "pose", "transform", "socket", "matrix",
                                       "reference", "ref_pose", "skeleton"))]
    log("%s: %d members, %d bone/pose related" % (class_name, len(names), len(interesting)))
    for name in sorted(interesting)[:24]:
        log("    %s" % name)


def main():
    for class_name in ("SkeletalMeshComponent", "SkeletalMesh", "Skeleton",
                       "AnimationLibrary", "SkeletalMeshEditorSubsystem",
                       "AnimationBlueprintLibrary", "AnimPoseExtensions"):
        describe(class_name)
        log("")

    log("also checking whether these exist at all:")
    for name in ("SkeletonUtilitiesLibrary", "AnimPoseExtensions", "AnimationLibrary",
                 "SkeletalMeshEditorSubsystem", "AnimationBlueprintLibrary"):
        log("  %-30s %s" % (name, "yes" if hasattr(unreal, name) else "no"))


main()
