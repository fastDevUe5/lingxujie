# unreal-engine-material-expressions-reference

Source: https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-engine-material-expressions-reference

## Material Expressions Reference Reference for all Material expressions available for use in the Material Editor. On this pageThis page is a reference index for all Material expression nodes available in the Material Editor. Material Expressions are the building blocks for creating fully functional Materials in Unreal Engine.Each Material expression is a self-contained black box that either outputs a set of one or more specific values, or performs a single operation on one or more inputs and then outputs the results of that operation.

## Parameters Certain Material expressions are parameters, meaning you can modify their values (dynamically during runtime in some cases) in a Material Instance of the base material containing the parameter.You should assign all parameters a unique name using the Parameter Name details property. This name is used to identify each specific parameter when you edit an instance in the Material Instance Editor.If two parameters of the same type have the same name within a Material, they are treated as the same parameter. Changing the value of one parameter in the Material Instance would change the value of both parameter expressions in the Material. You can set a default value for your parameters in the Details Panel. This default value is used in the Material Instance unless it is overridden and modified there.

## Material Expression Properties All Material Expression nodes contain the same properties that provide different kinds of information. Below, we use a Texture Sample node to highlight these
on properties. | 
 | Number | Property Name | Description 
 | 1 | Description | All materials expressions have a common Desc (Description) property, which is accessible from the Details Panel. Any text entered into this in this property displays in the Material Editor just above the expression in the workspace. It can be used for any purpose, but usually serves as a good way to leave short notes about the purpose or function of the expression.
 | 2 | Title bar | Displays the name and/or pertinent information about the the Material Expression.
 | 3 | Inputs | Links to any values used by the Material Expression.
 | 4 | Outputs | Links that output the results of the Material Expression operation.
 | 5 | Preview | Displays a preview of the values that are output by the Material Expression. This updates automatically when realtime update is enabled and can be manually updated using the Spacebar.

## Material Expression Types These reference pages are organized according to the categories in the Material Editor palette.
- Atmosphere Material ExpressionsMaterial Expressions that affect fog and other atmospheric level effects.
- Color Material ExpressionsMaterial expressions that perform actions on color inputs.
- Constant Material ExpressionsMaterial Expressions whose outputs generally do not change once set in the Editor or when play begins.
- Coordinates Material ExpressionsExpressions that perform actions on texture coordinates or output values that can be used as, or to modify, texture coordinates.
- Custom Material ExpressionsMaterial expressions that allow the use of custom, plain shader code.
- Depth Material ExpressionsMaterial expressions that deal with depth of the pixel being rendered.
- Font Material ExpressionsMaterial Expressions that sample and output font assets.
- Material Function ExpressionsMaterial expressions that are used to create or execute Materials Functions.
- Landscape Material ExpressionsMaterial expressions for creating Materials apply to Landscape terrains.
- Material Attributes ExpressionsThese expression nodes serve as a way to separate or combine various Material attributes, which is particularly useful when creating Layered Materials.
- Math Material ExpressionsExpressions that perform mathematical operations on one or more inputs.
- Material Parameter ExpressionsExpressions that expose properties to Material Instances to be overridden in child instances or modified at runtime.
- Particle Material ExpressionsExpressions used for creating Materials for emitters in Particle Systems.
- Texture Material ExpressionsExpressions that sample and output textures.
- Utility Material ExpressionsMaterial expressions that perform various utility operations on one or more inputs.
- Vector Material ExpressionsMaterial expressions that output a vector value, such as a position or normal.
- Vector Operation Material ExpressionsMaterial Expressions that perform operations on vector input values.

## Expression Index This is a reference list of many, but not all, Material Expressions. All links shown here can also be accessed through the Expression Types pages listed above.
Additionally, you can use Ctrl+F to find the expression node you need and follow the link to its description.Atmosphere
- AtmosphericFogColorColor
- DesaturationConstants
- Constant
- Constant2Vector
- Constant3Vector
- Constant4Vector
- DistanceCullFade
- PerInstanceFadeAmount
- PerInstanceRandom
- Time
- TwoSidedSign
- VertexColorCoordinates
- ActorPositionWS
- CameraPositionWS
- LightmapUVs
- 
ObjectOrientation
 
- 
ObjectPositionWS
 
- 
ObjectRadius
 
- Panner
- ParticlePositionWS
- PixelNormalWS
- Rotator
- SceneTexelSize
- ScreenPosition
- TextureCoordinate
- VertexNormalWS
- ViewSize
- WorldPositionCustom
- CustomDepth
- DepthFade
- PixelDepth
- SceneDepthFont
- FontSample
- FontSampleParameterFunctions
- FunctionInput
- FunctionOutput
- MaterialFunctionCall
- StaticBool
- StaticSwitch
- TextureObjectMaterialAttributes
- BreakMaterialAttributes
- MakeMaterialAttributesMath
- Abs
- Add
- AppendVector
- Ceil
- Clamp
- ComponentMask
- Cosine
- CrossProduct
- Divide
- DotProduct
- Floor
- Fmod
- Frac
- If
- LinearInterpolate
- Multiply
- Normalize
- OneMinus
- Power
- Sine
- SquareRoot
- SubtractParameters
- CollectionParameters
- DynamicParameter
- FontSampleParameter
- ScalarParameter
- StaticBoolParameter
- StaticSwitchParameter
- StaticComponentMaskParameter
- VectorParameter
- TextureObjectParameter
- TextureSampleParameter2D
- TextureSampleParameterSubUV
- TextureSampleParameterCube
- TextureSampleParameterMovieParticles
- DynamicParameter
- ParticleColor
- ParticleDirection
- ParticleMacroUV
- ParticleMotionBlurFade
- ParticlePositionWS
- ParticleRadius
- ParticleRelativeTime
- ParticleSize
- ParticleSpeed
- SphericalParticleOpacity
- ParticleSubUV
- TextureSampleParameterSubUVTerrain
- LandscapeLayerBlend
- LandscapeLayerCoords
- LandscapeLayerSwitchTexture
- FontSample
- FontSampleParameter
- SceneColor
- TextureObject
- TextureSampleUtility
- AntialiasedTextureMask
- BlackBody
- BumpOffset
- ConstantBiasScale
- DDX
- DDY
- DepthFade
- DepthOfFieldFunction
- Desaturation
- Distance
- DistanceFieldGradient
- DistanceToNearestSurface
- FeatureLevelSwitch
- Fresnel
- LightmassReplace
- LinearInterpolate
- Noise
- Previous Frame Switch
- QualitySwitch
- RotateAboutAxis
- SphereMask

- 
Thin Translucent

- Vector NoiseVectorOps
- AppendVector
- ComponentMask
- CrossProduct
- DeriveNormalZ
- DotProduct
- Normalize
- Transform
- TransformPositionVectors
- ActorPositionWS
- CameraPositionWS
- CameraVectorWS
- Constant2Vector
- Constant3Vector
- Constant4Vector
- LightVector
- 
ObjectBounds
 
- 
ObjectOrientation
 
- 
ObjectPositionWS
 
- ParticlePositionWS
- PixelNormalWS
- ReflectionVectorWS
- VertexNormalWS
- materials
- shaders
- material expressions