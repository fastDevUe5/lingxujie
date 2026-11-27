# reflections-environment-in-unreal-engine

Source: https://dev.epicgames.com/documentation/en-us/unreal-engine/reflections-environment-in-unreal-engine

## Reflections Environment Systems for how reflections are captured and displayed on reflective surfaces. On this pageReflections are an important aspect of bringing environments to life by allowing light to ground objects in the scene. In real-time 3D, reflections start with how the Materials are set up. Materials with low roughness values make surfaces more or less reflective. This can be the difference between creating a mirror-like surface or like brushed metal.Unreal Engine provides several dedicated reflection systems to use for your projects. Some of these can be used in conjunction with one another or on their own, deprioritizing any other reflection methods. Choosing what types of reflections you enable for your project primarily comes down to the quality you want to achieve and the platforms you're targeting to release on. Some reflection systems may be too costly to performance, only supported on certain platforms, or may have hardware restrictions.

## Types of Reflections When developing your project, you'll want to consider whether your project needs dynamic reflections, the level of quality it should achieve, and if the target platform you want to release on supports them or not.For example, using a combination of static Reflection Captures with a dynamic Screen Space Reflections post process effect works well for most platforms and is fast to render but has rendering artifacts due to their nature. However, using Lumen Global Illumination and Reflections emulates light and reflections more accurately to ground objects in the scene, but comes at a higher rendering cost and is not supported on all platforms.The available reflection systems support the following types of reflections and platforms: | 
 | Reflection System | Type of Reflections | Supported Platforms 
 | Lumen Reflections | Dynamic | High-end Desktop PCs and Next-Gen Consoles
 | Screen Space Reflections | Dynamic | Desktop and Consoles
 | Reflection Captures | Static | All Platforms
 | Planar Reflections | Dynamic | All Platforms

## Lumen Reflections Lumen Reflections are part of the Lumen Global Illumination and Reflection system which uses either software or hardware-based ray tracing to generate reflections for the scene. Lumen uses a combination of methods to accurately represent the scene through screen traces when using software ray tracing mode. When hardware ray tracing mode is enabled, it will leverage the existing ray tracing architecture for reflections but requires a graphics card that supports hardware ray tracing.For more information, see Lumen Global Illumination and Reflections.

## Lumen Ray Traced Reflections To get hardware ray traced reflections, enable Support Hardware Ray Tracing and Use Hardware Ray Tracing when available in the Project Settings under Engine > Rendering. Lumen Reflections then trace against the hardware ray tracing scene. For the highest reflection quality, set Lumen's Ray Lighting Mode to Hit Lighting for Reflections, which evaluates the full material and lighting at each reflection hit.For more information, see Hardware Ray Tracing.

## Screen Space Reflections Screen Space Reflections (SSR) are a dynamic post process effect that is limited to only reflecting what is visible on the screen. Objects off screen or occluded by objects on screen are not able to be represented in screen space reflections, which can cause rendering artifacts in the reflections.When Lumen Reflections are enabled, which is the default for new projects, they replace SSR. SSR is used when the project's Reflection Method is set to Screen Space. It's also the fallback when scalability turns Lumen Reflections off, as the Medium reflection quality level does.For more information, see Screen Space Reflections.

## Reflection Capture Actors Reflection Capture Actors are a low-cost, static capture of the area the reflection probe is placed. Many of these can be placed around the Level with no performance impact since they are calculated before runtime.There are two types of Reflection Captures to choose from: a Box and a Sphere shape. They work by capturing an image of the surrounding environment from their center and then mapping that to the reflection capture shape. Reflection Captures can overlap and blend with one another and are often placed with a large one to encompass an area and smaller ones for more defined static reflections on surfaces.Reflection Captures are a fallback in projects that use Lumen. When Lumen Global Illumination is enabled, Lumen provides all of the indirect specular lighting, and Reflection Captures don't contribute. They're used when Lumen is off, for example at lower scalability settings or in projects that use static lighting.For more information, see Reflection Capture Actors.

## Planar Reflections Planar Reflections is an Actor that can be placed along surfaces to create accurate, dynamic reflections of the scene whereby it renders the level again from the direction of the reflection. This method of reflection can be costly, but provides accurate reflections and is supported on all platforms.Planar Reflections are composited in the same pass as Reflection Captures, which the renderer skips when Lumen Global Illumination and Reflections are enabled.For more information, see Planar Reflection.

## High Quality Reflections Default reflection quality settings strike a good balance between performance and visual quality. However, for projects that are less concerned about performance and want to push the quality of reflections even higher, you can use the High Precision Normals GBuffer to do so.An important factor in achieving high quality reflections is how accurately the vertex normal and tangent can be represented. High density meshes may lead to adjacent vertices quantizing to the same vertex normal and tangent values, which leads to blocky jumps in normal orientation. Encoding the normals and tangents as 16 bits per channel enables developers to make the trade off between higher quality and how much additional memory is used encoding vertex buffers.The following settings are required to enable High Precision Normals for reflections:
- In the Project Settings under Engine > Rendering > Optimizations change the GBuffer Format to High Precision Normals.
- Open any Static Mesh Asset and use the Details panel in the Static Mesh Editor, under LOD 0 > Build Settings enable Use High Precision Tangent Basis.
- rendering
- lighting
- reflections
- ray tracing
- planar reflections
- screen space reflections
- reflection probe
- reflection capture
- lumen