"""The Python API classes this project actually reaches for.

Mirroring the whole reference is not worth it: the index lists 11,675 classes and the
documentation server answers one page roughly every nine seconds, so the full set would take a
day of continuous fetching, most of it for animation graph nodes and camera rig types this
project will never touch.

This list covers the editor scripting surface - subsystems, actors, assets, materials, meshes,
blueprints, levels, maths types and the toolset classes. It is deliberately short enough to
re-fetch quickly after an engine upgrade.

Used by Tools/mirror_python_api_list.py.
"""

CLASSES = [
    # --- Subsystems: what the editor exposes to scripts ---
    "UnrealEditorSubsystem",
    "LevelEditorSubsystem",
    "EditorActorSubsystem",
    "EditorAssetSubsystem",
    "EditorSubsystem",
    "StaticMeshEditorSubsystem",
    "MaterialEditorSubsystem",
    "AssetEditorSubsystem",
    "EditorUtilitySubsystem",
    "LevelSequenceEditorSubsystem",

    # --- Editor objects ---
    "EditorActorSubsystem",
    "EditorLevelLibrary",
    "EditorAssetLibrary",
    "LevelEditorViewportClient",
    "EditorViewportClient",
    "UnrealEdEngine",
    "EditorEngine",
    "EditorWorld",

    # --- Assets ---
    "AssetTools",
    "AssetImportTask",
    "AssetRegistryHelpers",
    "AssetRegistry",
    "AssetData",
    "Object",
    "Package",
    "AssetManager",

    # --- Meshes ---
    "StaticMesh",
    "StaticMeshComponent",
    "StaticMeshSourceModel",
    "MeshDescription",
    "SkeletalMesh",
    "SkeletalMeshComponent",
    "SkeletalMeshSocket",
    "Skeleton",
    "BoneNode",
    "BodySetup",
    "MeshBuildSettings",
    "NaniteSettings",
    "MeshNaniteSettings",

    # --- Materials ---
    "MaterialEditingLibrary",
    "Material",
    "MaterialInstance",
    "MaterialInstanceConstant",
    "MaterialInstanceDynamic",
    "MaterialExpression",
    "MaterialExpressionTextureSample",
    "MaterialExpressionTextureCoordinate",
    "MaterialFactoryNew",
    "MaterialInstanceConstantFactoryNew",
    "Texture",
    "Texture2D",
    "MaterialProperty",

    # --- Actors and worlds ---
    "Actor",
    "Pawn",
    "Character",
    "PlayerStart",
    "PlayerController",
    "World",
    "Level",
    "SceneComponent",
    "PrimitiveComponent",
    "Component",

    # --- Blueprints ---
    "Blueprint",
    "BlueprintEditorLibrary",
    "BlueprintFactory",
    "BlueprintGeneratedClass",
    "KismetSystemLibrary",
    "KismetMathLibrary",

    # --- Maths and containers ---
    "Vector",
    "Vector2D",
    "Vector4",
    "Rotator",
    "Quat",
    "Transform",
    "Matrix",
    "LinearColor",
    "Color",
    "Box",
    "Box2D",
    "Sphere",
    "IntPoint",
    "IntVector",
    "Array",
    "Map",
    "Set",
    "Name",
    "Text",
    "StringLibrary",
    "MathLibrary",

    # --- Lighting ---
    "Light",
    "DirectionalLight",
    "PointLight",
    "SpotLight",
    "SkyLight",
    "SkyAtmosphere",
    "ExponentialHeightFog",

    # --- Toolset registry: writing MCP tools in Python ---
    "ToolsetDefinition",
    "ToolAccessMode",
    "AgentSkill",
    "StructBase",
    "ObjectBase",
    "EnumBase",

    # --- Editor utilities ---
    "EditorDialog",
    "ScopedSlowTask",
    "ScopedEditorTransaction",
    "EditorLoadingAndSavingUtils",
    "EditorFilterLibrary",
    "EditorLevelUtils",
    "LevelEditorSubsystem",
    "ProjectSettings",
]
