#include "LXJSpiritBeast.h"

#include "LXJHealthComponent.h"

ALXJSpiritBeast::ALXJSpiritBeast()
{
	// Melee bruiser: sees you from 1200, sticks to you at ~150, hits hard but slowly.
	AggroRadius = 1200.f;
	LeashRadius = 2600.f;
	AttackRange = 200.f;
	AttackInterval = 1.4f;
	AttackDamage = 22.f;
	PatrolSpeed = 220.f;
	ChaseSpeed = 620.f;
	PatrolRadius = 800.f;
	ExperienceReward = 55.f;
	RespawnDelay = 14.f;

	BodyMaterialPath = TEXT("/Game/Materials/M_Moss.M_Moss");
	HeadMaterialPath = TEXT("/Game/Materials/M_Jade.M_Jade");

	BodyMesh->SetRelativeScale3D(FVector(0.62f, 0.62f, 0.72f));
	HeadMesh->SetRelativeLocation(FVector(0.f, 30.f, 52.f));
	HeadMesh->SetRelativeScale3D(FVector(0.34f, 0.34f, 0.34f));

	Health->MaxHealth = 240.f;
}
