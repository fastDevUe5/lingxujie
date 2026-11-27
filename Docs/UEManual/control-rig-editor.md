# control-rig-editor-in-unreal-engine

Source: https://dev.epicgames.com/documentation/en-us/unreal-engine/control-rig-editor-in-unreal-engine

## Control Rig Editor Learn about the various tools and areas in the Control Rig Editor. On this pageThis page outlines the user interface, tools, and features contained within the Control Rig Editor.

- Toolbar
 
- Viewport
 
- Rig Hierarchy
 
- Rig Graph
 
- Details

## Toolbar

The Control Rig toolbar contains buttons and settings for previewing behavior and Control Rig construction. The buttons with specific Control Rig functionality are as follows:

 | 

 | Name
 | Image
 | Description

 | Compile
 | 
 | 
Similar to Blueprints, Control Rigs must be compiled in order to fully save and begin executing their logic. Clicking this button will compile your rig, as well as visually provide feedback on whether or not your rig needs to be compiled.

You are required to compile whenever changes are made within the Rig Hierarchy. This can include adding, removing, reparenting, or renaming Controls, Bones or spaces. Recompiling is also required when creating variables.

The Compile button also resets your controls after you manipulate them in the viewport.

 | Solve Direction
 | 
 | 
The Solve Direction button switches between different Solver event chains. Use this to preview different Solve Directions. Each option is associated with a Rig Graph solve direction event node. Selecting an option will begin previewing that solve chain.

Clicking the main button will swap the mode between the current mode and the previously selected mode.

 | Auto Compile
 | 
 | Enable Auto Compile to set compiling to automatically occur when you make changes in the Rig Graph. This includes actions like creating and linking nodes. All other changes mentioned above will still require you to manually compile.

 | Debug Object
 | 
 | This drop-down menu links the Control Rig viewport to an active Control Rig in a simulating or playing session. This previews the current Control Rig animation from that session in the Control Rig viewport.

 | Class Settings
 | 
 | 
The Class Settings button toggles Blueprint class settings to be visible in the Details panel. The Shape Libraries property is located here, which can be used to change the control shapes available to you when rigging. Visit the Control Shapes and Control Shape Library page to learn more about this feature.

You can also access Control Rig Python commands such as Python Context and Copy Python Script.

## Viewport

From the Viewport, you can:

- Preview interaction with your Control Rig nodes.
 
- Set different display modes and debug displays.
 
- Select and manipulate controls.
 
- Change the preview mode using the top toolbar.

The View Options menu has the following Control Rig settings:

 | 

 | Name
 | Description

 | Display Nulls
 | 
Displays a selectable axis of Nulls in the viewport.

 | Display Axes On Selection
 | 
Displays a local axis when you select any rig element.

 | Axes Scale
 | 
The size of the axis display when drawing axes from either the Display Nulls or Display Axes On Selection options.

 | Bone Radius
 | 
The size of the Bones when Bones are visible by either selecting them or by showing Bones from the Character > Bones menu.

 | Pin Control Space
 | When controlling a pin value, you can select an element from this to offset the manipulator to be relative to a different element.

## Rig Hierarchy

The Rig Hierarchy panel is used to view and select your control hierarchy in an outliner-type view. This is also the primary area to create new Controls, Bones, and Nulls.

Create these elements by right-clicking in the panel and selecting New > Control, Bone, or Null. Your selection determines the location where these elements are created. If nothing is selected, then new elements will be created at the origin (0,0,0).

The context menu contains the following commands:

 | 

 | Name
 | Description

 | New
 | Creation menu for creating new Controls, Bones, or Nulls.

 | Delete
 | Deletes the current selection.

 | Duplicate
 | Duplicates the current selection.

 | Rename
 | Renames the current selection.

 | Mirror
 | 
Copies your currently selected elements and mirrors the copy along an axis. When clicked, a dialog window will appear where you can specify how you want the mirror action to function.

- Mirror Axis is the axis to mirror against. For characters that face Y-Forward in Unreal, you can keep this at the default value of X.
 
- Axis to Flip is the axis to rotate 180 degrees in order for rotations to be properly mirrored. For characters that face Y-Forward in Unreal, you can keep this at the default value of Z.
 
- Search is where you specify a keyword or letter to search for to be replaced. If you are mirroring a control with the postfix "_left", then you will want to write "left" here.
 
- Replace is where you specify a keyword or letter to replace the text used in Search. If you are mirroring a control with the postfix "_left", then you will want to write "right" here.

 | Test Space Switching
 | 
Opens a dialog window for previewing Space Switching behavior for your controls.

- Parent is the default behavior, where the control will follow any space changes by the parent.
 
- World will detach the control from any parent influence and attach it to the world.
 
- Click the Add (+) button to add any other control to parent to.

 | Copy
 | Copies the current selection, including the local and global transform, which can be used in conjunction with Paste Local / Global Transform.

 | Paste
 | Pastes the current selection.

 | Paste Local Transform
 | Pastes the currently copied control's local transform.

 | Paste Global Transform
 | Pastes the currently copied control's world transform

 | Reset Transform
 | Resets the currently selected control back to its initial transform.

 | Reset All Transforms
 | Resets all controls back to their initial transform.

 | Set Initial Transform from Current
 | After moving a transform in the viewport, clicking this will set the new location as the new initial transform.

 | Set Initial Transform from Closest Bone
 | Using this command will snap your selected Control to the nearest Bone and set that location as the Initial Transform. This is useful for aligning your controls to Bones.

 | Set Shape Transform From Current
 | If you are transforming your control, performing this command will reset the control's pivot point back to its initial transform, but maintain the current visual position of the control shape. This is useful if you want to customize your control's visual position while keeping the pivot the same.

 | Unparent
 | Moves the currently selected element to the top of the hierarchy.

 | Import
 | Imports a skeleton hierarchy to the current rig.

 | Refresh
 | Refreshes the existing initial transform from the selected mesh. This only updates if the node is found.

## My Blueprint

The My Blueprint panel, similar to that found in Blueprints, contains your various Control Rig Functions and Variables. Variables in Control Rig are meant to be used within your Rig Graph as a way to drive logic, rather than being exposed directly to an instance in a Level.

## Execution Stack

The Execution Stack panel previews the order of operations within your graph. Use this to debug your nodes and evaluate the sequence of events.

Right-clicking on an execution node and selecting Focus on Selection will frame that current node in the Rig Graph. You can also double-click a node to focus it.

## Curve Container

The Curve Container panel displays the list of Anim Curves from your Skeleton, and provides functionality to control them in the Rig Graph.

Curves can be referenced in the Rig Graph by using the Get Curve Value and Set Curve Value nodes.

## Rig Graph

The Rig Graph is where you script the Control Rig's behavior.

Hierarchy nodes can be referenced into the graph by dragging and dropping them from the Rig Hierarchy panel into the graph and selecting your desired reference type.

You can also create nodes by right-clicking. Search or navigate the context menu for your desired node.

Similar to Blueprints, multiple nodes can be collapsed into groups or Functions by right clicking on your selected nodes and selecting either Collapse Nodes or Collapse to Function.

Your functions are accessible from the My Blueprint panel in the Functions category. With functions, you can better organize large graphs, repeat logic, and easily share functionality across Control Rigs.

## Details

The Details panel contains information for your selected elements within the Control Rig Editor. These can include elements such as Controls, Bones, and rig graph nodes. Selecting Controls will reveal the following properties:

 | 

 | Name
 | Description

 | Name
 | The name of the selected rig element.

 | Display Name
 | The name of the Control as it will appear in Sequencer and the Anim Outliner. If not used, then the name will fallback to what is specified in Name.

 | Control Type
 | The type of Control to use. This is used to limit or change the Control's data if you intend the Control to only affect certain values, such as a Control that only rotates, translates, or provides a single property.

 | Animatable
 | Determines whether or not the Control will be animatable in Sequencer. This is useful if your rig has Controls that are visual-only.

 | Available Spaces
 | An array where you can add predefined custom spaces for your Controls, which are used for space switching.

 | Draw Limits
 | 
Draws a debug line if transform limits are being used on the selected Control.

 | Transform
 | Displays the different transform types for the selected rig element. Bones and Nulls will only display Initial and Current, while Controls will display Initial, Current, Offset, and Min/Max limits.

 | Shape
 | The Shape category contains properties for customizing the shape of the selected Control.

## Preview Scene Settings

The Preview Scene Settings panel contains properties that control your Skeletal Mesh, animation, and viewport environment settings.

The following properties can be used to affect the Control Rig viewport:

 | 

 | Name
 | Description

 | Preview Controller
 | 
Use the Preview Controller to play back animations in the viewport. This can be useful when testing how your Controls behave when animation is playing on your character, or for testing Backwards Solve behavior.

 | Preview Mesh
 | The Skeletal Mesh to use for your character in the viewport. You can change this to any other meshe with a compatible skeleton.

 | Clothing Simulation Factory
 | The cloth simulation to use in the viewport.

 | Allow Different Skeletons
 | If enabled, you can select Skeletal Meshes with incompatible skeletons in the Preview Mesh or Skeletal Meshes properties.

 | Allow Custom AnimBP Override
 | When using Preview Collections, enable Animation Blueprints to override from those collections.

 | Additional Meshes
 | Specify a Preview Collection here.

 | Skeletal Meshes
 | Additional meshes to add to the viewport. This can be useful if you are using Modular Characters.

- editor
- animation
- control rig