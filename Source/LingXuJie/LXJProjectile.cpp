#include "LXJProjectile.h"

#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/ProjectileMovementComponent.h"
#include "LXJHealthComponent.h"
#include "LXJMonster.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"

ALXJProjectile::ALXJProjectile()
{
	// The movement component does the ticking; the actor does not need its own tick.
	PrimaryActorTick.bCanEverTick = false;

	// Blocking sphere (same idea as the engine's projectile template): the bolt stops on
	// whatever it reaches. A QueryOnly overlap sphere did NOT report swept overlaps here.
	Collision = CreateDefaultSubobject<USphereComponent>(TEXT("Collision"));
	SetRootComponent(Collision);
	Collision->InitSphereRadius(24.f);
	Collision->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
	Collision->SetCollisionObjectType(ECC_WorldDynamic);
	Collision->SetCollisionResponseToAllChannels(ECR_Block);
	Collision->SetGenerateOverlapEvents(true);
	Collision->SetNotifyRigidBodyCollision(true);
	Collision->CanCharacterStepUpOn = ECB_No;

	Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
	Mesh->SetupAttachment(Collision);
	Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Mesh->SetCanEverAffectNavigation(false);
	Mesh->SetRelativeScale3D(FVector(0.26f, 0.26f, 0.26f));

	static ConstructorHelpers::FObjectFinder<UStaticMesh> SphereMesh(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
	if (SphereMesh.Succeeded())
	{
		Mesh->SetStaticMesh(SphereMesh.Object);
	}

	Movement = CreateDefaultSubobject<UProjectileMovementComponent>(TEXT("Movement"));
	Movement->UpdatedComponent = Collision;
	Movement->InitialSpeed = Speed;
	Movement->MaxSpeed = Speed;
	Movement->bRotationFollowsVelocity = true;
	Movement->bInitialVelocityInLocalSpace = false;
	Movement->ProjectileGravityScale = 0.f;
	Movement->bShouldBounce = false;
	Movement->bSweepCollision = true;
}

void ALXJProjectile::InitProjectile(AActor* InSourceActor, const FVector& Direction, float InDamage)
{
	SourceActor = InSourceActor;
	Damage = InDamage;

	// Set the heading here instead of trusting the spawn transform: BeginPlay runs inside
	// SpawnActor, so InitialSpeed is applied before the spawn rotation lands (gotcha #33).
	const FVector Heading = Direction.GetSafeNormal();
	SetActorRotation(Heading.Rotation());
	if (Movement)
	{
		Movement->Velocity = Heading * Speed;
	}

	if (InSourceActor)
	{
		// Never stop on the caster on the way out.
		Collision->IgnoreActorWhenMoving(InSourceActor, true);
	}
}

void ALXJProjectile::BeginPlay()
{
	Super::BeginPlay();

	Collision->OnComponentHit.AddDynamic(this, &ALXJProjectile::HandleHit);

	if (UMaterialInterface* QiMaterial = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/Materials/M_Qi.M_Qi")))
	{
		Mesh->SetMaterial(0, QiMaterial);
	}

	SetLifeSpan(LifeSeconds);
}

void ALXJProjectile::HandleHit(UPrimitiveComponent* HitComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp,
	FVector NormalImpulse, const FHitResult& Hit)
{
	if (bConsumed || !OtherActor || OtherActor == this || OtherActor == SourceActor)
	{
		return;
	}

	// P0: monsters do not friendly-fire each other; the bolt just splashes on them.
	if (OtherActor->IsA<ALXJMonster>())
	{
		Destroy();
		return;
	}

	// Damage anything that can take it; walls just stop the bolt.
	if (ULXJHealthComponent* TargetHealth = OtherActor->FindComponentByClass<ULXJHealthComponent>())
	{
		if (!TargetHealth->IsDead())
		{
			bConsumed = true;
			TargetHealth->ApplyDamage(Damage, SourceActor);
			UE_LOG(LogTemp, Log, TEXT("[LingXuJie] Qi bolt hit %s for %.0f"), *GetNameSafe(OtherActor), Damage);
		}
	}

	Destroy();
}
