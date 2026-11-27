"""Move the actual editor viewport camera, not just the frame that gets captured.

CaptureViewport's captureTransform renders from a temporary transform and leaves the editor
camera where it was, which is why the screenshots looked right while the editor window stayed
buried inside a building. This uses the editor subsystem that really owns the viewport.

    python Tools/reset_view.py [x y z yaw pitch]
"""

import unreal

# The plaza facing the red archway - see AGENTS.md rule 3b.
DEFAULT = (8950.0, -6200.0, 3900.0, 0.0, -2.0)


def main():
    args = unreal.SystemLibrary.get_command_line().split()
    x, y, z, yaw, pitch = DEFAULT

    subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    if subsystem is None:
        unreal.log_error("[LingXuJie] VIEW: no editor subsystem")
        return

    location = unreal.Vector(x, y, z)
    rotation = unreal.Rotator(pitch=0.0, yaw=0.0, roll=0.0)
    rotation.pitch = pitch
    rotation.yaw = yaw
    subsystem.set_level_viewport_camera_info(location, rotation)

    current_location, current_rotation = subsystem.get_level_viewport_camera_info()
    unreal.log("[LingXuJie] VIEW: camera now at %.0f, %.0f, %.0f yaw %.0f pitch %.0f"
               % (current_location.x, current_location.y, current_location.z,
                  current_rotation.yaw, current_rotation.pitch))


main()
