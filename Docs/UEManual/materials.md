# unreal-engine-materials

Source: https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-engine-materials

## Materials Controlling the appearance of surfaces in the world using shaders. On this pageMaterials in Unreal Engine define the surface properties of the objects in your scene. In the broadest sense, you can think of a Material as the "paint" that is applied to a mesh to control its visual appearance.In more technical terms, Materials tell the render engine exactly how a surface should interact with the light in your scene. Materials define every aspect of the surface including color, reflectivity, bumpiness, transparency, and so on. These calculations are done using data that is input to the Material from a variety of images (textures) and node-based Material expressions, as well as from various property settings inherent to the Material itself.

## Getting Started Material creation is a broad topic, and the node-based workflow allows you to create an almost infinite variety of surface types. Beginners are recommended to start with with the pages linked in this section. The Essential Material Concepts and Physically Based Materials pages introduce the theory and ideas that form the foundation of Material creation in Unreal. The Material Editor User Guide is a set of tool-based documentation that teaches practical aspects of using the Material Editor.
- Essential Material ConceptsAn introductory document on Materials in Unreal Engine.
- Designing Visuals, Rendering, and GraphicsRendering subsystem including lighting and shadowing, materials and textures, visual effects, and post processing.
- Physically Based MaterialsAn overview of the primary physically based Material inputs and how best to use them.
- Material Editor GuideLearn about Unreal Engine's node-based material editor to create materials which define the appearance and surface properties of objects in your scene.
- Material PropertiesAn introductory document on Material Properties in Unreal Engine.
- Material InputsAn in-depth look at the various inputs available on a Material and how they are used.
- Material Data TypesAn introduction to the four types of float data in the Material Editor

## Substrate Material Framework 
- Substrate MaterialsTopics and reference about using the Substrate Materials framework.
- Substrate MaterialsTopics and reference about using the Substrate Materials framework.
- Substrate MaterialsTopics and reference about using the Substrate Materials framework.

## Material Workflow Concepts Once you understand the basic principles behind Material creation, the documents in this section are strongly recommended as a next step. Material Instances and Material Functions are foundational topics in Material creation, and help you optimize your workflow to save time and avoid doing the same work twice. Material Instances allow you or other artists on your team to quickly and easily customize Materials to produce multiple variations (or instances) from a single parent Material. Material Functions allow you to package parts of a Material graph into a single node, and share it to a common library for reuse in other Materials.
- Material InstancesHierarchical Material relationships help you alter the behavior and appearance of child Materials without recompiling the shader.
- Material FunctionsSnippets of Material that you can save in packages and reuse across multiple Materials.
- Layered MaterialsTwo methods for layering Materials to create complex, unique surfaces.

## Tutorials Index The pages in this section are step-by-step, project based documents that walk you through some specific aspect of Material creation in Unreal. For example: Animating UV Coordinates, or Using Texture Masks.
- Materials TutorialsTutorials demonstrating various aspects of Material creation in Unreal Engine.

## Material Reference Pages The Material Editor provides dozens of Material Expressions and Functions, each meant to perform some specific task in your Material graph. If you are looking for information about how and when to use a specific node, start with the pages linked below. The Material Expression and Function reference pages are organized according to their categories in the Materials palette — for example, Blends, Gradients, Math, Coordinates, and so on.
- Material Expressions ReferenceReference for all Material expressions available for use in the Material Editor.
- Material Functions ReferenceReference pages for each of the default Material Functions, organized by category.
- Material Editor UIA breakdown of the Material Editor user interface.
- Material Instance Editor UIGuide to using the Material Instance Editor for modifying MaterialInstanceConstants.

## Additional Concepts and Tools Materials pages that do not fit more precisely into another category are found below. Many of these are intermediate to advanced topics that allow you to progress beyond the basics of Material creation and begin to develop more sophisticated Materials for your projects.
- Bent Normal MapsAn overview of using Bent Normal maps in Unreal Engine.
- Bump Mapping Without Tangent SpaceHow to achieve bump mapping from 3D procedural shaders where classic tangent space does not work.
- Curve Atlases in MaterialsCurve Atlases store a combination of Curve assets that enables you to access Curve Linear Color data through your Materials.
- Customized UVsFeature that allows running calculations in the vertex shader to increase performance over running them per-pixel.
- Material AnalyzerThis page describes how to locate and use the Material Analyzer tool.
- Refraction Using Pixel Normal OffsetOverview of the Refraction Mode for Pixel Normal Offset in your Materials.
- Storing Custom Data in Materials Per-PrimitiveAn overview of the Custom Primitive Data workflow for storing custom data per primitive that's accessible through Blueprint.
- Lit TranslucencyExplanation of how translucent surfaces are lit and cast shadows including self-shadows.
- materials
- shaders