#include "LXJGround.h"

#include "ProceduralMeshComponent.h"

namespace
{
	/** cm per texture repeat on the ground material; matches the old Python TERRAIN_UV_SCALE. */
	constexpr float GroundUVScale = 250.0f;

	/** Distance over which the rolling hills fade out around a flat rectangle (cm). */
	constexpr float FlatFadeDistance = 1200.0f;
}

ALXJGround::ALXJGround()
{
	PrimaryActorTick.bCanEverTick = false;

	Mesh = CreateDefaultSubobject<UProceduralMeshComponent>(TEXT("Ground"));
	SetRootComponent(Mesh);

	// Movable: a Static component refuses section updates once it has been registered, and this
	// mesh is (re)built at load time rather than cooked into the level.
	Mesh->SetMobility(EComponentMobility::Movable);
	Mesh->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
	Mesh->SetCollisionProfileName(TEXT("BlockAll"));
	Mesh->SetCastShadow(true);
}

void ALXJGround::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);
	Rebuild();
}

void ALXJGround::PostRegisterAllComponents()
{
	Super::PostRegisterAllComponents();

	// Runs when the level is loaded as well as when the actor is spawned, which is exactly where
	// the serialised-empty ProceduralMesh needs to be filled back in.
	Rebuild();
}

void ALXJGround::BeginPlay()
{
	Super::BeginPlay();
	Rebuild();
}

float ALXJGround::HeightAt(float X, float Y) const
{
	// Three overlapping sine bands: long swells, medium rolls, short ripples. Same numbers the
	// level used to compute in Python, so the layout around the houses does not move.
	const float Hills =
		75.0f * FMath::Sin(X / 850.0f) * FMath::Cos(Y / 1000.0f) +
		38.0f * FMath::Sin(X / 380.0f + 1.7f) * FMath::Cos(Y / 430.0f + 0.4f) +
		18.0f * FMath::Sin(X / 160.0f + 2.9f) * FMath::Cos(Y / 190.0f + 1.1f);

	float Mask = 1.0f;
	for (const FVector4& Area : FlatAreas)
	{
		const float DeltaX = FMath::Max3(static_cast<float>(Area.X) - X, 0.0f, X - static_cast<float>(Area.Z));
		const float DeltaY = FMath::Max3(static_cast<float>(Area.Y) - Y, 0.0f, Y - static_cast<float>(Area.W));
		Mask = FMath::Min(Mask, FMath::Min(1.0f, FMath::Sqrt(DeltaX * DeltaX + DeltaY * DeltaY) / FlatFadeDistance));
	}

	return Hills * Mask;
}

void ALXJGround::Rebuild()
{
	if (Mesh == nullptr)
	{
		return;
	}

	const int32 Steps = FMath::Max(2, FMath::RoundToInt(Size / FMath::Max(50.0f, Step)));
	const float Half = Size * 0.5f;
	const float ActualStep = Size / Steps;
	const int32 Side = Steps + 1;

	TArray<FVector> Vertices;
	TArray<FVector> Normals;
	TArray<FVector2D> UVs;
	TArray<int32> Triangles;
	Vertices.Reserve(Side * Side);
	Normals.Reserve(Side * Side);
	UVs.Reserve(Side * Side);
	Triangles.Reserve(Steps * Steps * 6);

	for (int32 IndexY = 0; IndexY < Side; ++IndexY)
	{
		for (int32 IndexX = 0; IndexX < Side; ++IndexX)
		{
			const float LocalX = -Half + IndexX * ActualStep;
			const float LocalY = -Half + IndexY * ActualStep;
			const float WorldX = LocalX + static_cast<float>(Centre.X);
			const float WorldY = LocalY + static_cast<float>(Centre.Y);

			Vertices.Add(FVector(LocalX, LocalY, HeightAt(WorldX, WorldY)));

			// Normal from the height gradient: a section without normals renders black.
			const float DzDx = (HeightAt(WorldX + ActualStep, WorldY) - HeightAt(WorldX - ActualStep, WorldY)) /
				(2.0f * ActualStep);
			const float DzDy = (HeightAt(WorldX, WorldY + ActualStep) - HeightAt(WorldX, WorldY - ActualStep)) /
				(2.0f * ActualStep);
			const float Length = FMath::Sqrt(DzDx * DzDx + DzDy * DzDy + 1.0f);
			Normals.Add(FVector(-DzDx / Length, -DzDy / Length, 1.0f / Length));

			UVs.Add(FVector2D(LocalX / GroundUVScale, LocalY / GroundUVScale));
		}
	}

	for (int32 IndexY = 0; IndexY < Steps; ++IndexY)
	{
		for (int32 IndexX = 0; IndexX < Steps; ++IndexX)
		{
			const int32 A = IndexY * Side + IndexX;
			const int32 B = A + 1;
			const int32 C = A + Side;
			const int32 D = C + 1;
			// Counter-clockwise seen from above, so the surface faces up.
			Triangles.Append({ A, C, B, B, C, D });
		}
	}

	Mesh->ClearAllMeshSections();
	Mesh->CreateMeshSection_LinearColor(0, Vertices, Triangles, Normals, UVs,
		TArray<FLinearColor>(), TArray<FProcMeshTangent>(), true);
	if (GroundMaterial != nullptr)
	{
		Mesh->SetMaterial(0, GroundMaterial);
	}

	UE_LOG(LogTemp, Display, TEXT("[LingXuJie] ground rebuilt: %d verts, %d tris, %.0f cm across, %d flat areas"),
		Vertices.Num(), Triangles.Num() / 3, Size, FlatAreas.Num());
}
