# directional-lights-in-unreal-engine

Source: https://dev.epicgames.com/documentation/en-us/unreal-engine/directional-lights-in-unreal-engine

## Directional Lights The basics of understanding directional lights. On this pageThe Directional Light simulates light that is being emitted from a source that is infinitely far away. This means that all shadows cast by this light will be parallel, making this the ideal choice for simulating sunlight. The Directional Light when placed can be set to one of three Mobility settings:
- Static - (pictured left) which means that the light cannot be changed in game. This is the fastest method for rendering and allows for baked lighting.
- Stationary - (also pictured left) which means the light will only have its shadowing and bounced lighting from static geometry baked by Lightmass, all other lighting will be dynamic. This setting also allows for the light to change color and intensity in game, but, it does not move and allows partial baked lighting.
- Moveable - (pictured left) which means the light is totally dynamic and allows for dynamic shadowing. This is the slowest in terms of rendering but allows for the most flexibility during gameplay.Below you will see a representation of sunlight being cast through an opening in a roof.The left image shows just the light, the right image has its Shadow Frustum enabled in order to see that the Directional Light is casting parallel light rays.Light Direction (pictured left) is indicated by an arrow that points in the direction the light will emit which is useful for placing and orientating your light as needed.

## Directional Light Properties The properties of a Directional Light are broken up into the following categories: Light, Light Shafts, Lightmass, Light Function, Cascaded Shadow Maps, Distance Field Shadows, Atmosphere and Cloud, and Ray Tracing:

## Light The Light category holds the settings you'll change most: how bright the light is, its color, and the size of the sun disk it simulates. It also controls how the light casts shadows and how it contributes to features such as volumetric fog, translucency, and ray tracing. Many of these are in the category's advanced section, which you can expand at the bottom of the category. | 
 |  Property | Description 
 | Intensity | Maximum illumination from the light, in lux. For more information, see Physical Lighting Units.
 | Light Color | The color that the light emits.
 | Source Angle | Angle subtended by a light source in degrees. Defaults to 0.5357, which is the angle for our sun. Larger values give softer shadows and broader specular highlights.
 | Source Soft Angle | Angle subtended by a soft light source in degrees.
 | Use Temperature | When disabled, use white as an illuminant.
 | Temperature | Color temperature in Kelvin of the blackbody illuminant. White is 6500K.
 | Affects World | Disables the light completely. Cannot be set at run time. To disable a light's effect during runtime, change its Visibility property.
 | Cast Shadows | If the light casts shadows.
 | Indirect Lighting Intensity | Scales the indirect lighting contribution from the light.
 | Volumetric Scattering Intensity | Intensity of the volumetric scattering from this light.
 | Shadow Cascade Bias Distribution | Controls the depth bias across cascades. Use this to mitigate the shadow acne difference on shadow cascades transition.
 | Forward Shading Priority | Forward lighting priority for the single directional light that will be used for forward shading, translucent, single layer water and volumetric fog. When two lights have equal priorities, the selection will be based on their overall brightness as a fallback.
 | Cast Modulated Shadows | Whether to cast modulated shadows from dynamic objects (mobile only). Requires a Stationary light with Inset Shadows For Movable Objects enabled.
 | Modulated Shadow Color | Color to modulate against the scene color when rendering modulated shadows (mobile only).
 | Shadow Amount | The amount of shadow occlusion. A value of 0 means no occlusion and no shadow.
 | Specular Scale | The multiplier on specular highlights. Use with care. Any values besides 1 are not physical.
 | Diffuse Scale | Multiplier on diffuse lighting. Use only with great care! Any value besides 1 is not physical!
 | Shadow Resolution Scale | Scales the resolution of shadow maps used to shadow this light.
 | Shadow Bias | Controls how accurate the shadows from this light are.
 | Shadow Slope Bias | Controls how accurate the self-shadowing of whole scene shadows from this light is. This contributes to Shadow Bias by increasing the amount of bias depending on the slope of a surface.
 | Shadow Filter Sharpen | How much to sharpen shadow filtering for this light.
 | Contact Shadow Length | Length of screen space ray trace for sharp contact shadows.
 | Contact Shadow Length in World Space Units | Whether to use world space units for the Contact Shadow Length.
 | Contact Shadow Casting Intensity | Intensity of the contact shadows cast by primitives with Contact Shadow enabled. A value of 0 casts no shadow.
 | Contact Shadow Non Casting Intensity | Intensity of the contact shadows cast by primitives with Contact Shadow disabled. A value of 0 casts no shadow.
 | Cast Translucent Shadows | Whether to cast dynamic shadows through translucent objects.
 | Cast Shadows from Cinematic Objects Only | Whether the light should only cast shadows from components with Cast Cinematic Shadow enabled. This can be useful for setting up cinematic Movable spotlights aimed at characters and avoiding the shadow depth costs of the background.This option only works with dynamic shadow maps, not with static shadowing or Ray Traced Distance Field shadows.
 | Force Cached Shadows for Movable Primitives | Enables cached shadows for movable primitives.
 | Lighting Channels | Channels that this light should affect.
 | View Lighting Channels | Controls which views this light affects.
 | Cast Static Shadows | Whether this light casts static shadows.
 | Cast Dynamic Shadows | Whether this light casts dynamic shadows.
 | Affect Translucent Lighting | Whether the light affects translucency or not.
 | Transmission | Whether to transmit through surfaces with subsurface scattering profiles.
 | Cast Volumetric Shadow | Whether to shadow volumetric fog.
 | Cast Deep Shadow | Whether to cast high-quality hair strands self-shadowing.
 | Deep Shadow Layer Distribution | How the deep shadow layers used for hair strands are spread out, from 0 (evenly spaced) to 1 (exponential, which gives more detail on small nearby features).
 | Cast Ray Traced Shadows | Sets whether to enable ray traced shadows for this light. The options are:
- Disabled
- Use Project Setting
- Enabled
 | Affect Ray Tracing Reflections | Whether to affect objects in reflections when ray-traced reflection is enabled.
 | Affect Ray Tracing Global Illumination | Whether to affect global illumination when ray-traced global illumination is enabled.
 | Allow MegaLights | Whether this light can use MegaLights when MegaLights is enabled in the project settings or a Post Process Volume. By default, MegaLights doesn't render directional lights, so this setting has no effect unless your project turns on MegaLights support for directional lights.
 | MegaLights Shadow Method | The shadowing method MegaLights uses for this light. Ray Tracing gives a fixed cost and correct area shadows. Virtual Shadow Map has a higher cost per light, but casts shadows directly from Nanite geometry.
 | Override Ray End Bias | Whether to use the Ray End Bias value on this light.
 | Ray End Bias | Bias for the end of a shadow ray. Use it to fix self-occlusion artifacts between the light and nearby geometry, such as an enclosure mesh.

## Light Shafts Light shafts, sometimes called god rays, add screen-space rays around the light's direction through fog and atmosphere. For more information, see Light Shafts. | 
 | Property | Description 
 | Light Shaft Occlusion | Whether to occlude fog and atmosphere inter scattering with the screen space blurred occlusion from this light.
 | Occlusion Mask Darkness | How dark the occlusion masking is, a value of 1 is no darkening. Requires Light Shaft Occlusion.
 | Occlusion Depth Range | Everything closer to the camera than this distance will occlude the light shafts. Requires Light Shaft Occlusion.
 | Light Shaft Bloom | Whether to render light shaft bloom for this light.
 | Bloom Scale | Scales the additive bloom color.
 | Bloom Threshold | Scene color must be larger than this to create bloom in the light shafts.
 | Bloom Max Brightness | When exposure is applied, this value constrains scene color brightness.
 | Bloom Tint | Sets the color to tint the bloom coming from the light shafts.
 | Light Shaft Override Direction | Can be used to make the light shafts come from somewhere other than the light's actual direction.

## Lightmass These settings control how Lightmass treats this light when you build lighting. They affect only the precomputed lighting from Static and Stationary lights. | 
 | Property | Description 
 | Light Source Angle | Angle that the directional light's emissive surface extends relative to a receiver, affects penumbra sizes.
 | Indirect Lighting Saturation | A value of 0 will completely desaturate this light in Lightmass, 1 will be unchanged.
 | Shadow Exponent | Controls the falloff of shadow penumbras.
 | Use Area Shadows for Stationary Light | Whether to use area shadows for stationary light precomputed shadow maps.

## Light Function A light function uses a material to filter the light's intensity, for example to project the shadows of moving clouds across a level. For more information, see Light Functions. | 
 | Property | Description 
 | Light Function Material | The light function material to be applied to this light.
 | Light Function Scale | Scales the light function projection.
 | Fade Distance | The distance at which the light function should be completely faded to the value in Disabled Brightness.
 | Disabled Brightness | Brightness factor applied to the light when the light function is specified but disabled, for example, beyond the Fade Distance.

## Cascaded Shadow Maps Cascaded shadow maps (CSMs) split the view into several shadow maps, with the most detail close to the camera. The light uses them when the project's Shadow Map Method is set to Shadow Maps. With Virtual Shadow Maps, the default for new UE5 projects, the light doesn't render cascades, so most of these settings have no effect. The dynamic shadow distance still matters, though: beyond it, only objects with Far Shadow enabled cast shadows. | 
 | Property | Description 
 | Dynamic Shadow Distance MovableLight | How far Cascaded Shadow Map dynamic shadows will cover for a movable light, measured from the camera. A value of 0 disables dynamic shadows. If Allow Static Lighting is disabled in the project settings, this is labeled Dynamic Shadow Distance and applies to Stationary lights too.
 | Dynamic Shadow Distance StationaryLight | How far Cascaded Shadow Map dynamic shadows will cover for a stationary light, measured from the camera. A value of 0 disables dynamic shadows. Hidden if Allow Static Lighting is disabled in the project settings.
 | Num Dynamic Shadow Cascades | Number of cascades to split the view frustum into for the whole scene. More cascades give better shadow resolution, but add significant rendering cost.
 | Distribution Exponent | Controls whether the cascades are distributed closer to the camera (larger exponent) or further from the camera (smaller exponent).
 | Transition Fraction | Proportion of the fade region between cascades.
 | Distance Fadeout Fraction | Controls the size of the fade out region at the far extent of the dynamic shadow's influence.
 | Inset Shadows for Movable Objects | (Stationary lights only) Whether to use per-object inset shadows for movable components, even though cascaded shadow maps are enabled.
 | Far Shadow Cascade Count | The number of cascades between the dynamic shadow distance and Far Shadow Distance. Only objects with Far Shadow enabled render into them. A value of 0 means no far shadow cascades.
 | Far Shadow Distance | Distance at which the far shadow cascade should end.

## Reusing Cascade Depths Between Frames By default, the light renders the shadow depths for every cascade every frame. Cascades can instead reuse their depths from an earlier frame and re-render only every few frames, with the cascades staggered so they don't all update on the same frame. This lowers the cost of shadow depth rendering in projects that use Shadow Maps rather than Virtual Shadow Maps, such as projects for mobile or lower-end hardware, especially when the sun and most shadow casters don't move. The trade-off is that shadows update less often.This option is off by default, and there's no setting for it in the Details panel or Project Settings. You control it with console variables:
- r.Shadow.CSMShadowDepthReuse turns depth reuse on.
- r.Shadow.CSMShadowDepthReuse.Interval sets how many frames each cascade waits before it re-renders. r.Shadow.CSMShadowDepthReuse.FarInterval sets a separate interval for the far shadow cascades.
- r.Shadow.CSMShadowDepthReuse.SeparateDynamic and r.Shadow.CSMShadowDepthReuse.DynamicCascadeMask render movable objects into their own part of the shadow map for the cascades you choose, so that their shadows can update more often (r.Shadow.CSMShadowDepthReuse.DynamicInterval) than the static scene.
- r.Shadow.VisualizeCSMOverlay tints the scene by cascade, which helps you see which cascade covers which part of the view while you tune these values.

## Distance Field Shadows These settings control ray traced distance field shadows, which use Mesh Distance Fields to cast soft area shadows with sharp contacts. On a directional light, they cover the distance beyond the dynamic shadow distance, which gives you cheaper shadows in the distance. | 
 | Property | Description 
 | Distance Field Shadows | Whether to use ray traced distance field area shadows. Requires Generate Mesh Distance Fields to be enabled in the project settings. Enabled by default on new directional lights.
 | Ray Start Offset Depth Scale | Controls how far ray traced shadows are offset from the receiving surface as the camera gets farther away. Larger values reduce self-shadowing artifacts on low-resolution distance fields.
 | DistanceField Shadow Distance | The distance at which distance field shadows end. They cover the range between the dynamic shadow distance and this distance.
 | DistanceField Trace Distance | How far shadows can be cast, in world units. Larger values increase the shadowing cost.

## Atmosphere and Cloud Directional Lights support the Sky Atmosphere and the Volumetric Clouds features of Unreal Engine.Additional information and demonstration can be found in the Volumetric Clouds page under the Directional Light Interactions and Shadowing section. | 
 |  Property | Description 
 | Atmosphere and Cloud |   
 | Atmosphere Sun Light | Whether the Directional Light can interact with the atmosphere, clouds and generate a visual sun disk, all of which compose the visual sky. Enabled by default. With a Sky Atmosphere in the level, Intensity and Light Color describe the sunlight above the atmosphere, and the atmosphere dims and tints the light that reaches the ground, for example toward orange at sunset. Most of the other settings in this category require this option.
 | Cast Shadows on Clouds | Whether the light should cast any shadows from opaque meshes onto clouds. This is disabled for any secondary Directional Lights that have Atmosphere Sun Light enabled and set to Atmosphere Sun Light Index of 1, such as another sun or as a moon light.
 | Cast Shadows on Atmosphere | Whether the light should cast any shadows from opaque meshes into the atmosphere when a SkyAtmosphere is used.
 | Cast Cloud Shadows | Whether the light should cast any shadows from the clouds onto the atmosphere and other scene elements. The cloud shadow settings in the advanced section require this.
 | Cloud Scattered Luminance Scale | Scales the light contribution when scattered in cloud participating media. This can help counter balance the fact that our current multiple scattering solution is only an approximation. | 
 | Advanced Properties |   
 | Atmosphere Sun Light Index | Two atmosphere lights are supported at any time to represent the sun and moon, or two suns. Use this index to set the primary and secondary light source. For example, the sun would be 0 and the moon would be 1.
 | Atmosphere Sun Disk Color Scale | A color multiplied with the sun disk luminance.
 | Per Pixel Atmosphere Transmittance | Whether to apply atmosphere transmittance per pixel on opaque meshes instead of using the light's global transmittance.
 | Cloud Shadow Strength | The strength of the shadow. Higher values will block more light.
 | Cloud Shadow on Atmosphere Strength | The strength of shadows on the atmosphere. When set to 0, shadows on the atmosphere is disabled.
 | Cloud Shadow on Surface Strength | The strength of shadows on opaque and transparent meshes. When set to 0, shadows on opaque and translucent surfaces is disabled.
 | Cloud Shadow Depth Bias | Controls the bias applied to the front shadow depth of the volumetric cloud shadow map.
 | Cloud Shadow Extent | The world space radius of the cloud shadow map around the camera. Measured in kilometers (km).
 | Cloud Shadow Map Resolution Scale | Scales the cloud shadow map resolution. The resolution is clamped by r.VolumetricCloud.ShadowMap.MaxResolution.
 | Cloud Shadow Ray Sample Count Scale | Scales the number of samples used for shadow map tracing. The sample count resolution is clamped with r.VolumetricCloud.ShadowMap.RaySampleMaxCount.

## Ray Tracing These settings apply when the light casts ray traced shadows. | 
 | Property | Description 
 | Samples Per Pixel | The number of rays traced for each pixel when this light casts ray traced shadows. Higher values give smoother soft shadows at a higher cost.
 | Shadow Source Angle Factor | Scales the source angle used for shadows, relative to Source Angle. The default of 1.0 matches Source Angle.
- rendering
- lighting
- mobility
- light type