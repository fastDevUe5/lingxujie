# animation-editors-in-unreal-engine

Source: https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-editors-in-unreal-engine

## Animation Editors An overview of the Animation Editor modes in Unreal Engine. On this pageThe Skeletal Mesh Animation System in Unreal Engine is comprised of specialized animation asset editors that feature robust animation tools that you can use when working with Skeletal Meshes and other Animation Assets. With these animation editors, you can create character animations, interactions within the levels, and other procedural behaviors.

This document provides an overview of the specialized animation editors in Unreal.

## Overview

A character's skeletal mesh has many associated assets that can be opened through the Content Browser. These assets include a Skeleton, Skeletal Mesh, Animation Sequences, and Animation Blueprints. Depending on which asset is opened, the corresponding Editor Mode will open.

Here you will find an overview of an Animation Editor window with highlighted features, common across all of the Animation Editor Modes.

- 
 Toolbar

- 
 Viewport

- 
 Editor Modes

- 
 Preview Scene Settings

## Toolbar

The Toolbar, which is found in all of the Animation Editor modes, is similar to the Toolbar found across Unreal Engine's many editors and windows. For general Toolbar functions refer to the Main Toolbar, and for specific animation editor toolbar features, reference their respective pages for more information.

The following unique features are common across all of the Animation Editors:

 | 

 | Name
 | Icon
 | Description

 | Preview Mesh
 | 
 | Set a new preview Skeletal Mesh for the current asset (Stored per-animation or per-skeleton).

 | Preview Animation
 | 
 | Select a preview animation for playback with the current asset.

 | Create Asset
 | 
 | 

From this drop down menu, the following Animation Assets can be created:

- Create Animation creates a new Animation Sequence from either the current default Reference Pose, or from the displayed meshes Current Pose.
 
- Create Pose Asset creates a new Pose Asset from either the Current Pose displayed on the mesh, the Current Animation description, or the Insert Pose Description.
 
- Anim Blueprint creates a new Animation Blueprint for the current Skeletal Mesh.
 
- Anim Composite created a new AnimComposite using the selected Skeleton.
 
- Anim Montage creates a new AnimMontage using the selected skeleton.
 
- Blend Space creates a new Blend Space used for smoothly blending transitions between animations.
 
- Blend Space 1D creates a new 1D Blend Space using the selected Skeleton.
 
- Aim Offset creates a new Aim Offset Blend Space using the selected skeleton.
 
- Aim Offset 1D creates a new Aim Offset 1D Blend Space using the selected skeleton.

## Viewport

The Viewport window allows you to preview playback of animation assets on your selected Skeletal Mesh and provides information about your assets. Below you will find highlighted features relevant to the Animation Editors.

- Viewport Property Settings

Listed below are the viewport properties relevant to the Animation Sequence Editor Viewport.

 | 

 | Name
 | Description

 | Preview Animation
 | Lists the current selected animation sequence.

 | LOD (Level of Detail)
 | The current displayed LOD or Level of Detail assigned value of the character.

 | Current Screen Size
 | This is a value that represents how much of the viewport is occupied by the character's bounding box (By default, the bounding box is derived from the Physics Asset, if one is present, and Skeleton Asset if not.). Factors that affect this number are how large the animation's bounding box is (or the displacement in 3D space), how close the character is to the camera, and the amount of zoom applied to the camera. Based on this value you can assign when your LOD should switch between levels.

 | Triangles
 | Lists the number of triangles rendered that comprise the previewed mesh.

 | Vertices
 | Lists the number of vertices, or individual coordinate points, that comprise the previewed mesh.

 | UV Channels
 | Lists the current mesh's UV Channel.

 | Approximate Size
 | Dimensions of a bounding box containing the current animations displaced space, calculated by one of the animations assets. By default the physics asset will be used, and if no physics asset is present then the Skeleton asset will be referenced. Listed in Unreal Units (Centimeters).

 | Frame Rate
 | Lists the preview animations frame rate of playback.

- Debug Text

Here you the Animation Editor Debug Text can also be seen in the top right of the Viewport. Here you can find important reference information about the animation asset currently being used such as the name of the animation asset, the LOD mode, Current screen Size and display output of mesh properties such as displayed triangles and vertices.

## Editor Modes

Each Animation Editor Mode, can be opened with their respective buttons in the top right of your project window:

- 
 Skeleton Editor: This editor is used for working with Skeleton Rigs and provides visual control of bone and joint hierarchy associated with a Skeletal Mesh.

- 
 Skeletal Mesh Editor: The Skeletal Mesh Editor is where you can make edits to meshes, assign Materials, adjust Level of Detail (LOD), and test Morph Target functionality.

- 
 Animation Sequence Editor: If the Skeletal Mesh has associated Animation Sequences, you can edit and preview them, including augmentation tools such as, Blendspaces, Morph Targets and Animation Notifies here.

- 
 Animation Blueprint Editor: Similar to Unreal's Blueprint Editor, The Animation Blueprint editor is a visual scripting environment for directing animation functionality and behaviors within the level. You can access this Mode after an Animation Blueprint asset has been created for your mesh.

- 
 Physics Asset Editor: The Physics Asset Editor is a dedicated animation editor you can use to manipulate the Physics Asset assigned to your Skeletal Mesh.

After opening a Skeletal Mesh asset for the first time, the Skeletal Mesh Editor will be the default Editor Mode open. By clicking any of the other Editor Modes, a new window tab will open in your current editor window.

## Skeleton Editor

In the Skeleton Editor Mode you will find a hierarchy outline and visual preview of the Bone data found within your Skeleton Mesh. Here you can adjust bone placement, create Skeleton Sockets, and preview Animation Curves.

## Skeletal Mesh Editor

The Skeletal Mesh Editor Mode is where you can edit visual attributes of Skeletal Meshes. For instance, manipulating the polygonal structures of meshes, editing the associated Materials, and even assigning LODs.

## Animation Sequence Editor

With the Animation Sequencer Editor mode, you can perform animation focused editing, specific to any of your project's animation asset types. Examples include creating and managing Animation Sequences, Animation Notifies, Animation Montages, and more.

## Preview Scene Settings

The Preview Scene is the visual preview found in all of Unreal Engine's many project windows. With this window you can quickly see what your asset and animations will look like in different lighting environments and playback scenarios.

Below are a few features of the Preview Scene Settings window that are unique to the animation editors modes:

 | 

 | Name
 | Description

 | Preview Controller
 | 
Here you have control over which animation is previewed in the viewport.

- 
 Default will use the Animation tool's default settings. In most cases, this will cause the character to use the reference pose, except when an animation sequence is being viewed.

- 
 Reference Pose will use the Skeletal Mesh's Reference Pose.

- 
 Use Specific Animation will open an option to select a specific Animation Sequence associated with your skeletal mesh to preview.

- 
 Live Link Preview Controller will use preview using Live Link settings.

The selected mode will also be displayed on the first line of the Debug Text in the viewport.

 | Preview Mesh (Skeleton)
 | This property enables you to change the Skeletal Mesh used for previewing purposes. Only found in Skeleton Editor and Animation Editor.

 | Allow Different Skeletons
 | When this property is enabled you can select an additional mesh, even ones not associated with the current skeleton, to preview in the viewport. Only found in Skeleton Editor and Animation Editor.

 | Allow Custom AnimBP Override
 | If using a Preview Collection, you can enable this property to allow an override of custom Animation Blueprints. Only found in Skeleton Editor and Animation Editor

 | Additional Meshes
 | For use in instances of Mesh Collection implementation. View other meshes included in the current Mesh Collection for previewing purposes. Only found in Skeleton Editor and Animation Editor.

 | Skeletal Meshes
 | The Skeletal Mesh assets that are included in the specified Preview Mesh Collection. Only found in Skeleton Editor and Animation Editor.

 | Settings
 | General scene lighting and rendering settings.

- animation