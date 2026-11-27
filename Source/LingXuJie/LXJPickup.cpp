#include "LXJPickup.h"

#include "Components/StaticMeshComponent.h"
#include "Engine/World.h"
#include "GameFramework/Pawn.h"
#include "Kismet/GameplayStatics.h"
#include "LXJHUD.h"
#include "LXJInventoryComponent.h"
#include "LXJItems.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"

ALXJPickup::ALXJPickup()
{
	PrimaryActorTick.bCanEverTick = true;

	Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
	SetRootComponent(Mesh);
	Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Mesh->SetCanEverAffectNavigation(false);
	Mesh->SetRelativeScale3D(FVector(0.3f, 0.3f, 0.3f));

	static ConstructorHelpers::FObjectFinder<UStaticMesh> SphereMesh(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
	if (SphereMesh.Succeeded())
	{
		Mesh->SetStaticMesh(SphereMesh.Object);
	}
}

void ALXJPickup::InitPickup(FName InItemId, int32 InCount)
{
	ItemId = InItemId;
	Count = FMath::Max(1, InCount);

	const FLXJItemDef* Item = LXJItems::Find(ItemId);
	if (!Item)
	{
		UE_LOG(LogTemp, Warning, TEXT("[LingXuJie] pickup with unknown item '%s'"), *ItemId.ToString());
		return;
	}

	// Shape and material tell the item type apart without needing per-item assets.
	UStaticMesh* Shape = nullptr;
	const TCHAR* MaterialPath = TEXT("/Game/Materials/M_Qi.M_Qi");
	FVector Scale(0.3f);

	switch (Item->Type)
	{
	case ELXJItemType::Weapon:
		Shape = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"));
		MaterialPath = TEXT("/Game/Materials/M_Gold.M_Gold");
		Scale = FVector(0.08f, 0.08f, 0.7f);
		break;

	case ELXJItemType::Armor:
		Shape = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
		MaterialPath = TEXT("/Game/Materials/M_Jade.M_Jade");
		Scale = FVector(0.35f, 0.35f, 0.55f);
		break;

	case ELXJItemType::Material:
	default:
		Shape = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Sphere.Sphere"));
		MaterialPath = TEXT("/Game/Materials/M_Qi.M_Qi");
		Scale = FVector(0.28f);
		break;
	}

	if (Shape)
	{
		Mesh->SetStaticMesh(Shape);
	}
	if (UMaterialInterface* Material = LoadObject<UMaterialInterface>(nullptr, MaterialPath))
	{
		Mesh->SetMaterial(0, Material);
	}
	SetActorScale3D(Scale);
}

ALXJPickup* ALXJPickup::SpawnAt(UWorld* World, const FVector& Location, FName ItemId, int32 Count)
{
	if (!World)
	{
		return nullptr;
	}

	FActorSpawnParameters Params;
	Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

	ALXJPickup* Pickup = World->SpawnActor<ALXJPickup>(
		ALXJPickup::StaticClass(), Location + FVector(0.f, 0.f, 40.f), FRotator::ZeroRotator, Params);
	if (Pickup)
	{
		Pickup->InitPickup(ItemId, Count);
	}
	return Pickup;
}

void ALXJPickup::BeginPlay()
{
	Super::BeginPlay();

	SpawnLocation = GetActorLocation();
	SetLifeSpan(LifeSeconds);
}

void ALXJPickup::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	APawn* Player = UGameplayStatics::GetPlayerPawn(this, 0);
	if (!Player)
	{
		return;
	}

	const float Distance = FVector::Dist(GetActorLocation(), Player->GetActorLocation() + FVector(0.f, 0.f, 40.f));

	if (!bFlying && Distance <= CollectRadius)
	{
		bFlying = true;
	}

	if (bFlying)
	{
		const FVector Target = Player->GetActorLocation() + FVector(0.f, 0.f, 40.f);
		const FVector Direction = (Target - GetActorLocation()).GetSafeNormal();
		SetActorLocation(GetActorLocation() + Direction * FlySpeed * DeltaSeconds);

		if (Distance <= 90.f && TryCollect(Player))
		{
			return;
		}
		return;
	}

	// Idle drift so the loot reads as loot instead of scenery.
	BobTime += DeltaSeconds;
	SetActorLocation(SpawnLocation + FVector(0.f, 0.f, FMath::Sin(BobTime * 2.2f) * 14.f));
	AddActorLocalRotation(FRotator(0.f, 90.f * DeltaSeconds, 0.f));
}

bool ALXJPickup::TryCollect(AActor* Collector)
{
	ULXJInventoryComponent* Inventory = Collector ? Collector->FindComponentByClass<ULXJInventoryComponent>() : nullptr;
	if (!Inventory)
	{
		return false;
	}

	const FName PickedId = ItemId;
	const int32 PickedCount = Count;

	if (!Inventory->AddItem(PickedId, PickedCount))
	{
		// Bag full: drop the magnet and let the player make room.
		bFlying = false;
		SpawnLocation = GetActorLocation();
		return false;
	}

	Inventory->TryAutoEquip(PickedId);

	const FLXJItemDef* Item = LXJItems::Find(PickedId);
	const FString Label = Item ? Item->DisplayName : PickedId.ToString();

	if (const APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0))
	{
		if (ALXJHUD* HUD = Cast<ALXJHUD>(PC->GetHUD()))
		{
			HUD->AddPickupToast(FString::Printf(TEXT("+%d %s"), PickedCount, *Label));
		}
	}

	UE_LOG(LogTemp, Log, TEXT("[LingXuJie] Picked up %s x%d"), *Label, PickedCount);
	Destroy();
	return true;
}
