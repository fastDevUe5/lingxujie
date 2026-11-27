#include "LXJTrainingDummy.h"

#include "Components/StaticMeshComponent.h"
#include "Engine/CollisionProfile.h"
#include "LXJHealthComponent.h"
#include "LXJProgressComponent.h"
#include "Materials/MaterialInterface.h"
#include "TimerManager.h"
#include "UObject/ConstructorHelpers.h"

ALXJTrainingDummy::ALXJTrainingDummy()
{
	PrimaryActorTick.bCanEverTick = true;

	Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
	SetRootComponent(Mesh);
	Mesh->SetCollisionProfileName(UCollisionProfile::Pawn_ProfileName);
	Mesh->SetMobility(EComponentMobility::Movable);

	static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderMesh(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	if (CylinderMesh.Succeeded())
	{
		Mesh->SetStaticMesh(CylinderMesh.Object);
	}
	Mesh->SetRelativeScale3D(FVector(0.7f, 0.7f, 1.8f));

	Health = CreateDefaultSubobject<ULXJHealthComponent>(TEXT("Health"));
	Health->MaxHealth = 220.f;
}

void ALXJTrainingDummy::BeginPlay()
{
	Super::BeginPlay();

	if (UMaterialInterface* Material = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/Materials/M_Gold.M_Gold")))
	{
		Mesh->SetMaterial(0, Material);
	}

	Health->OnDeath.AddUObject(this, &ALXJTrainingDummy::HandleDeath);
}

void ALXJTrainingDummy::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	// Small scale pop when hit: readable feedback without any animation assets.
	HitFlash = FMath::Max(0.f, HitFlash - DeltaSeconds * 4.f);
	const float Pop = 1.f + 0.08f * FMath::Sin(HitFlash * 18.f) * HitFlash;
	SetActorScale3D(FVector(Pop));
}

void ALXJTrainingDummy::HandleDeath(AActor* DeadActor, AActor* Killer)
{
	UE_LOG(LogTemp, Log, TEXT("[LingXuJie] Training dummy destroyed by %s"), *GetNameSafe(Killer));
	ULXJProgressComponent::GrantKillReward(Killer, ExperienceReward);

	SetActorHiddenInGame(true);
	SetActorEnableCollision(false);

	GetWorldTimerManager().SetTimer(RespawnTimer, this, &ALXJTrainingDummy::Respawn, 6.f, false);
}

void ALXJTrainingDummy::Respawn()
{
	Health->ResetHealth();
	SetActorHiddenInGame(false);
	SetActorEnableCollision(true);
	UE_LOG(LogTemp, Log, TEXT("[LingXuJie] Training dummy respawned"));
}
