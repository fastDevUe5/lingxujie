// 掉落物: a bobbing item that flies to the player and lands in the bag.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LXJPickup.generated.h"

class UStaticMeshComponent;

UCLASS()
class LINGXUJIE_API ALXJPickup : public AActor
{
	GENERATED_BODY()

public:
	ALXJPickup();

	virtual void Tick(float DeltaSeconds) override;

	/** Configures what this pickup gives (mesh/material are picked from the item type). */
	void InitPickup(FName InItemId, int32 InCount);

	/** Spawns a pickup just above a world location (monster death uses this). */
	static ALXJPickup* SpawnAt(UWorld* World, const FVector& Location, FName ItemId, int32 Count);

protected:
	virtual void BeginPlay() override;

private:
	/** Hands the item to the collector's bag. False when the bag is full. */
	bool TryCollect(AActor* Collector);

	UPROPERTY(VisibleAnywhere, Category = "LingXuJie|Pickup")
	TObjectPtr<UStaticMeshComponent> Mesh;

	FName ItemId;
	int32 Count = 1;

	FVector SpawnLocation = FVector::ZeroVector;
	float BobTime = 0.f;
	bool bFlying = false;

	/** Players closer than this scoop the item up automatically. */
	static constexpr float CollectRadius = 220.f;
	/** Once magnetised, the item closes this fast. */
	static constexpr float FlySpeed = 900.f;
	/** Uncollected loot eventually rots away so the level does not fill up. */
	static constexpr float LifeSeconds = 90.f;
};
