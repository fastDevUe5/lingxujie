// Base monster: patrol / chase / attack / return state machine driven by LXJMonsterBrain.
// Subclasses only change the attack payload and the kiting distance (beast vs cultivator).

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "LXJMonsterBrain.h"
#include "LXJMonster.generated.h"

class ULXJHealthComponent;
class UStaticMeshComponent;

UCLASS()
class LINGXUJIE_API ALXJMonster : public ACharacter
{
	GENERATED_BODY()

public:
	ALXJMonster();

	virtual void Tick(float DeltaSeconds) override;

	/** Plain C++ accessor: the brain enum is not reflected, so no UFUNCTION here. */
	LXJMonsterBrain::EState GetBrainState() const { return State; }

	UFUNCTION(BlueprintPure, Category = "LingXuJie|Monster")
	bool HasAggro() const { return bAggro; }

	ULXJHealthComponent* GetHealthComponent() const { return Health; }

protected:
	virtual void BeginPlay() override;

	/** One swing / cast at the target. The base implementation is a melee hit. */
	virtual void PerformAttack(AActor* Target);

	/** Distance the monster tries to keep: small = charges in, large = kites. */
	virtual float GetPreferredRange() const { return AttackRange * 0.6f; }

	/** Casters drop the richer loot table. */
	virtual bool IsRangedCaster() const { return false; }

	virtual void HandleDeath(AActor* DeadActor, AActor* Killer);
	virtual void HandleDamaged(AActor* DamagedActor, float Amount, float RemainingHealth, AActor* Source);

	void Respawn();

	/** Moves along a flat direction to a world point (no controller needed). */
	void MoveTowards(const FVector& WorldTarget, float Speed);

	AActor* FindTarget() const;

	UPROPERTY(VisibleAnywhere, Category = "LingXuJie|Monster")
	TObjectPtr<UStaticMeshComponent> BodyMesh;

	UPROPERTY(VisibleAnywhere, Category = "LingXuJie|Monster")
	TObjectPtr<UStaticMeshComponent> HeadMesh;

	UPROPERTY(VisibleAnywhere, Category = "LingXuJie|Monster")
	TObjectPtr<ULXJHealthComponent> Health;

	UPROPERTY(EditAnywhere, Category = "LingXuJie|Monster")
	FString BodyMaterialPath = TEXT("/Game/Materials/M_Moss.M_Moss");

	UPROPERTY(EditAnywhere, Category = "LingXuJie|Monster")
	FString HeadMaterialPath = TEXT("/Game/Materials/M_Stone.M_Stone");

	UPROPERTY(EditAnywhere, Category = "LingXuJie|Monster")
	float AggroRadius = 1200.f;

	UPROPERTY(EditAnywhere, Category = "LingXuJie|Monster")
	float LeashRadius = 2400.f;

	UPROPERTY(EditAnywhere, Category = "LingXuJie|Monster")
	float AttackRange = 200.f;

	UPROPERTY(EditAnywhere, Category = "LingXuJie|Monster")
	float AttackInterval = 1.8f;

	UPROPERTY(EditAnywhere, Category = "LingXuJie|Monster")
	float AttackDamage = 18.f;

	UPROPERTY(EditAnywhere, Category = "LingXuJie|Monster")
	float PatrolSpeed = 200.f;

	UPROPERTY(EditAnywhere, Category = "LingXuJie|Monster")
	float ChaseSpeed = 480.f;

	UPROPERTY(EditAnywhere, Category = "LingXuJie|Monster")
	float PatrolRadius = 700.f;

	UPROPERTY(EditAnywhere, Category = "LingXuJie|Monster")
	float ExperienceReward = 55.f;

	UPROPERTY(EditAnywhere, Category = "LingXuJie|Monster")
	float RespawnDelay = 14.f;

private:
	void UpdatePatrol(float DeltaSeconds);
	void UpdateChase(AActor* Target, float DistanceToTarget);
	void UpdateReturn();
	void PickPatrolTarget();

	LXJMonsterBrain::EState State = LXJMonsterBrain::EState::Patrol;

	FVector HomeLocation = FVector::ZeroVector;
	FVector PatrolTarget = FVector::ZeroVector;

	float AttackCooldownLeft = 0.f;
	float PatrolWaitLeft = 0.f;
	float StrafeSign = 1.f;

	/** Seeded in BeginPlay; drives the drop table. */
	FRandomStream LootStream;

	bool bAggro = false;
	FTimerHandle RespawnTimer;
};
