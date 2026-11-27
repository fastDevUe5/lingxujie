"""Point the viewport at MX_BOSS001_STATIC so its material state can be photographed.

The camera is set to a position that frames the untethered actor, and the position is recorded so the
after-shot lands on identical framing. Nothing about the actor is changed here.

    py "Tools/point_at_static_boss.py"
"""

import unreal

# In front of MX_BOSS001_STATIC, which sits at (9550, -6200, 3740).
LOCATION = (9550.0, -6900.0, 3800.0)
YAW = 90.0
PITCH = -5.0


def main():
    subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    if subsystem is None:
        unreal.log_error("[LingXuJie] CAM: no editor subsystem")
        return
    location = unreal.Vector(LOCATION[0], LOCATION[1], LOCATION[2])
    rotation = unreal.Rotator(pitch=0.0, yaw=0.0, roll=0.0)
    rotation.yaw = YAW
    rotation.pitch = PITCH
    subsystem.set_level_viewport_camera_info(location, rotation)
    unreal.log("[LingXuJie] CAM: camera now at %.0f, %.0f, %.0f yaw %.0f pitch %.0f"
               % (LOCATION[0], LOCATION[1], LOCATION[2], YAW, PITCH))


try:
    main()
except Exception as error:  # noqa: BLE001
    unreal.log_error("[LingXuJie] CAM: FATAL %r" % error)
