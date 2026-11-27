#include "LXJEvilCultivator.h"

#include "Engine/World.h"
#include "LXJHealthComponent.h"
#include "LXJProjectile.h"

ALXJEvilCultivator::ALXJEvilCultivator()
{
	// Ranged harasser: engages from 1200, wants 800 of air between you and it.
	AggroRadius = 1200.f;
	LeashRadius = 3000.f;
	AttackRange = 1000.f;
	AttackInterval = 2.4f;
	AttackDamage = 16.f;
	PatrolSpeed = 180.f;
	ChaseSpeed = 430.f;
	PatrolRadius = 600.f;
	ExperienceReward = 70.f;
	RespawnDelay = 16.f;

	BodyMaterialPath = TEXT("/Game/Materials/M_Stone.M_Stone");
	HeadMaterialPath = TEXT("/Game/Materials/M_Gold.M_Gold");

	BodyMesh->SetRelativeScale3D(FVector(0.5f, 0.5f, 1.0f));
	HeadMesh->SetRelativeLocation(FVector(0.f, 0.f, 70.f));
	HeadMesh->SetRelativeScale3D(FVector(0.36f, 0.36f, 0.36f));

	Health->MaxHealth = 190.f;
}

void ALXJEvilCultivator::PerformAttack(AActor* Target)
{
	UWorld* World = GetWorld();
	if (!World || !Target)
	{
		return;
	}

	if (ULXJHealthComponent* TargetHealth = Target->FindComponentByClass<ULXJHealthComponent>())
	{
		if (TargetHealth->IsDead())
		{
			return;
		}
	}

	const FVector MuzzleLocation = GetActorLocation() + FVector(0.f, 0.f, 70.f) + GetActorForwardVector() * 110.f;
	const FVector AimLocation = Target->GetActorLocation() + FVector(0.f, 0.f, 40.f);
	const FVector Direction = (AimLocation - MuzzleLocation).GetSafeNormal();

	FActorSpawnParameters SpawnParams;
	SpawnParams.Owner = this;
	SpawnParams.Instigator = this;
	SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

	ALXJProjectile* Bolt = World->SpawnActor<ALXJProjectile>(
		ALXJProjectile::StaticClass(), MuzzleLocation, Direction.Rotation(), SpawnParams);
	if (!Bolt)
	{
		return;
	}

	Bolt->InitProjectile(this, Direction, AttackDamage);
	UE_LOG(LogTemp, Log, TEXT("[LingXuJie] %s casts qi bolt at %s"), *GetNameSafe(this), *GetNameSafe(Target));
}
