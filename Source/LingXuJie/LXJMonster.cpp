#include "LXJMonster.h"

#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "LXJHealthComponent.h"
#include "LXJItems.h"
#include "LXJPickup.h"
#include "LXJProgressComponent.h"
#include "Materials/MaterialInterface.h"
#include "TimerManager.h"
#include "UObject/ConstructorHelpers.h"

ALXJMonster::ALXJMonster()
{
	PrimaryActorTick.bCanEverTick = true;

	GetCapsuleComponent()->InitCapsuleSize(44.f, 88.f);

	bUseControllerRotationPitch = false;
	bUseControllerRotationYaw = false;
	bUseControllerRotationRoll = false;

	UCharacterMovementComponent* Move = GetCharacterMovement();
	Move->bOrientRotationToMovement = true;
	Move->RotationRate = FRotator(0.f, 300.f, 0.f);
	Move->MaxWalkSpeed = PatrolSpeed;
	Move->BrakingDecelerationWalking = 1800.f;
	Move->GroundFriction = 7.f;
	Move->MaxStepHeight = 60.f;

	BodyMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("BodyMesh"));
	BodyMesh->SetupAttachment(GetCapsuleComponent());
	BodyMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	BodyMesh->SetCanEverAffectNavigation(false);
	BodyMesh->SetRelativeLocation(FVector(0.f, 0.f, -30.f));
	BodyMesh->SetRelativeScale3D(FVector(0.55f, 0.55f, 0.85f));

	HeadMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("HeadMesh"));
	HeadMesh->SetupAttachment(GetCapsuleComponent());
	HeadMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	HeadMesh->SetCanEverAffectNavigation(false);
	HeadMesh->SetRelativeLocation(FVector(0.f, 0.f, 66.f));
	HeadMesh->SetRelativeScale3D(FVector(0.38f, 0.38f, 0.38f));

	static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderMesh(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> SphereMesh(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
	if (CylinderMesh.Succeeded())
	{
		BodyMesh->SetStaticMesh(CylinderMesh.Object);
	}
	if (SphereMesh.Succeeded())
	{
		HeadMesh->SetStaticMesh(SphereMesh.Object);
	}

	Health = CreateDefaultSubobject<ULXJHealthComponent>(TEXT("Health"));
	Health->MaxHealth = 240.f;
}

void ALXJMonster::BeginPlay()
{
	Super::BeginPlay();

	if (UMaterialInterface* BodyMaterial = LoadObject<UMaterialInterface>(nullptr, *BodyMaterialPath))
	{
		BodyMesh->SetMaterial(0, BodyMaterial);
	}
	if (UMaterialInterface* HeadMaterial = LoadObject<UMaterialInterface>(nullptr, *HeadMaterialPath))
	{
		HeadMesh->SetMaterial(0, HeadMaterial);
	}

	HomeLocation = GetActorLocation();
	PickPatrolTarget();
	LootStream.Initialize(FMath::Rand());

	Health->OnDeath.AddUObject(this, &ALXJMonster::HandleDeath);
	Health->OnDamaged.AddUObject(this, &ALXJMonster::HandleDamaged);

	UE_LOG(LogTemp, Log, TEXT("[LingXuJie] %s spawned at %s (hp %.0f)"),
		*GetNameSafe(this), *HomeLocation.ToCompactString(), Health->GetMaxHealth());
}

AActor* ALXJMonster::FindTarget() const
{
	APawn* Pawn = UGameplayStatics::GetPlayerPawn(this, 0);
	if (!Pawn)
	{
		return nullptr;
	}

	// The player is "targetable" only while alive; a dead player is ignored, not chased.
	if (const ULXJHealthComponent* PawnHealth = Pawn->FindComponentByClass<ULXJHealthComponent>())
	{
		if (PawnHealth->IsDead())
		{
			return nullptr;
		}
	}
	return Pawn;
}

void ALXJMonster::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	if (!Health || Health->IsDead())
	{
		return;
	}

	AttackCooldownLeft = FMath::Max(0.f, AttackCooldownLeft - DeltaSeconds);

	AActor* Target = FindTarget();
	const float DistanceToTarget = Target
		? FVector::Dist2D(GetActorLocation(), Target->GetActorLocation())
		: 0.f;

	// Getting hit (or spotting the player) flips aggro on; the leash turns it off again.
	// A monster walking home ignores targets on the way: otherwise "beyond the leash" and
	// "player in range" fight each other and it re-aggros every single frame.
	const bool bCanAggro = State != LXJMonsterBrain::EState::Return;
	if (Target && !bAggro && bCanAggro && DistanceToTarget <= AggroRadius)
	{
		bAggro = true;
		UE_LOG(LogTemp, Log, TEXT("[LingXuJie] %s aggro on %s (%.0f away)"), *GetNameSafe(this), *GetNameSafe(Target), DistanceToTarget);
	}

	LXJMonsterBrain::FInput In;
	In.bHasTarget = Target != nullptr;
	In.bAggro = bAggro;
	In.DistanceToTarget = DistanceToTarget;
	In.DistanceFromHome = FVector::Dist2D(GetActorLocation(), HomeLocation);
	In.AggroRadius = AggroRadius;
	In.AttackRange = AttackRange;
	In.LeashRadius = LeashRadius;
	In.bAttackReady = AttackCooldownLeft <= 0.f;

	const LXJMonsterBrain::EState PreviousState = State;
	State = LXJMonsterBrain::NextState(State, In);

	if (State != PreviousState)
	{
		UE_LOG(LogTemp, Log, TEXT("[LingXuJie] %s state %s -> %s"), *GetNameSafe(this),
			LXJMonsterBrain::ToString(PreviousState), LXJMonsterBrain::ToString(State));
	}

	if (bAggro && LXJMonsterBrain::ShouldDropAggro(In))
	{
		bAggro = false;
		UE_LOG(LogTemp, Log, TEXT("[LingXuJie] %s drops aggro"), *GetNameSafe(this));
	}

	switch (State)
	{
	case LXJMonsterBrain::EState::Patrol:
		UpdatePatrol(DeltaSeconds);
		break;

	case LXJMonsterBrain::EState::Chase:
		UpdateChase(Target, DistanceToTarget);
		break;

	case LXJMonsterBrain::EState::Attack:
		if (Target)
		{
			// Face the target so the melee sweep / bolt leaves in the right direction.
			FRotator Facing = (Target->GetActorLocation() - GetActorLocation()).Rotation();
			Facing.Pitch = 0.f;
			Facing.Roll = 0.f;
			SetActorRotation(Facing);
		}
		if (AttackCooldownLeft <= 0.f)
		{
			AttackCooldownLeft = AttackInterval;
			PerformAttack(Target);
		}
		break;

	case LXJMonsterBrain::EState::Return:
	default:
		UpdateReturn();
		break;
	}
}

void ALXJMonster::MoveTowards(const FVector& WorldTarget, float Speed)
{
	const FVector Direction = (WorldTarget - GetActorLocation()).GetSafeNormal2D();
	if (Direction.IsNearlyZero())
	{
		return;
	}

	GetCharacterMovement()->MaxWalkSpeed = Speed;
	AddMovementInput(Direction, 1.f);
}

void ALXJMonster::PickPatrolTarget()
{
	const FVector2D Offset = FMath::RandPointInCircle(PatrolRadius);
	PatrolTarget = HomeLocation + FVector(Offset.X, Offset.Y, 0.f);
	PatrolWaitLeft = 0.f;
}

void ALXJMonster::UpdatePatrol(float DeltaSeconds)
{
	if (PatrolWaitLeft > 0.f)
	{
		PatrolWaitLeft = FMath::Max(0.f, PatrolWaitLeft - DeltaSeconds);
		return;
	}

	if (FVector::Dist2D(GetActorLocation(), PatrolTarget) <= 140.f)
	{
		// Reached the waypoint: idle a moment, then wander somewhere else.
		PatrolWaitLeft = FMath::FRandRange(1.f, 2.5f);
		PickPatrolTarget();
		return;
	}

	MoveTowards(PatrolTarget, PatrolSpeed);
}

void ALXJMonster::UpdateChase(AActor* Target, float DistanceToTarget)
{
	if (!Target)
	{
		return;
	}

	// Already in attack range: plant your feet. Strafing here made melee monsters circle
	// behind the player, and every player swing (aimed where the camera looks) whiffed.
	if (DistanceToTarget <= AttackRange * 0.95f)
	{
		GetCharacterMovement()->StopMovementImmediately();
		return;
	}

	const FVector TargetLocation = Target->GetActorLocation();
	const float PreferredRange = FMath::Max(GetPreferredRange(), 60.f);

	// Kiting: approach when too far, back off when too close, otherwise circle the target.
	if (DistanceToTarget > PreferredRange * 1.15f)
	{
		MoveTowards(TargetLocation, ChaseSpeed);
	}
	else if (DistanceToTarget < PreferredRange * 0.75f)
	{
		const FVector Away = (GetActorLocation() - TargetLocation).GetSafeNormal2D();
		MoveTowards(GetActorLocation() + Away * 400.f, PatrolSpeed);
	}
	else
	{
		if (FMath::FRand() < 0.002f)
		{
			StrafeSign *= -1.f;
		}
		const FVector ToTarget = (TargetLocation - GetActorLocation()).GetSafeNormal2D();
		const FVector Side = FVector::CrossProduct(FVector::UpVector, ToTarget) * StrafeSign;
		MoveTowards(GetActorLocation() + Side * 400.f, PatrolSpeed);
	}
}

void ALXJMonster::UpdateReturn()
{
	if (FVector::Dist2D(GetActorLocation(), HomeLocation) <= 180.f)
	{
		State = LXJMonsterBrain::EState::Patrol;
		PickPatrolTarget();
		return;
	}

	MoveTowards(HomeLocation, PatrolSpeed);
}

void ALXJMonster::PerformAttack(AActor* Target)
{
	if (!Target)
	{
		return;
	}

	// Melee: only connects when the target is actually in reach (the state machine
	// already checked, this is the second guard for a target that stepped away).
	const float Distance = FVector::Dist2D(GetActorLocation(), Target->GetActorLocation());
	if (Distance > AttackRange + 80.f)
	{
		UE_LOG(LogTemp, Verbose, TEXT("[LingXuJie] %s swing missed (%s is %.0f away)"), *GetNameSafe(this), *GetNameSafe(Target), Distance);
		return;
	}

	if (ULXJHealthComponent* TargetHealth = Target->FindComponentByClass<ULXJHealthComponent>())
	{
		TargetHealth->ApplyDamage(AttackDamage, this);
	}
}

void ALXJMonster::HandleDamaged(AActor* DamagedActor, float Amount, float RemainingHealth, AActor* Source)
{
	// Being hit pulls the monster off its patrol even from outside the aggro radius.
	if (Source && !bAggro)
	{
		if (Source->FindComponentByClass<ULXJProgressComponent>())
		{
			bAggro = true;
			UE_LOG(LogTemp, Log, TEXT("[LingXuJie] %s aggro from %s damage"), *GetNameSafe(this), *GetNameSafe(Source));
		}
	}
}

void ALXJMonster::HandleDeath(AActor* DeadActor, AActor* Killer)
{
	UE_LOG(LogTemp, Log, TEXT("[LingXuJie] %s slain by %s (+%.0f exp)"), *GetNameSafe(this), *GetNameSafe(Killer), ExperienceReward);
	ULXJProgressComponent::GrantKillReward(Killer, ExperienceReward);

	// Loot: every monster pays spirit stones, casters sometimes part with gear.
	if (UWorld* World = GetWorld())
	{
		const TArray<FLXJDrop> Drops = LXJItems::RollDrops(IsRangedCaster(), LootStream);
		for (const FLXJDrop& Drop : Drops)
		{
			ALXJPickup::SpawnAt(World, GetActorLocation(), Drop.ItemId, Drop.Count);
			UE_LOG(LogTemp, Log, TEXT("[LingXuJie] %s dropped %s x%d"),
				*GetNameSafe(this), *Drop.ItemId.ToString(), Drop.Count);
		}
	}

	bAggro = false;
	State = LXJMonsterBrain::EState::Patrol;
	AttackCooldownLeft = 0.f;
	GetCharacterMovement()->StopMovementImmediately();
	SetActorHiddenInGame(true);
	SetActorEnableCollision(false);

	GetWorldTimerManager().SetTimer(RespawnTimer, this, &ALXJMonster::Respawn, RespawnDelay, false);
}

void ALXJMonster::Respawn()
{
	Health->ResetHealth();
	SetActorLocation(HomeLocation);
	SetActorHiddenInGame(false);
	SetActorEnableCollision(true);
	State = LXJMonsterBrain::EState::Patrol;
	bAggro = false;
	PickPatrolTarget();
	UE_LOG(LogTemp, Log, TEXT("[LingXuJie] %s respawned"), *GetNameSafe(this));
}
