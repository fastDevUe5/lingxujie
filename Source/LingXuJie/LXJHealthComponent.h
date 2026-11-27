// Reusable health container: works for the player, training dummies and (later) monsters.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "LXJHealthComponent.generated.h"

DECLARE_MULTICAST_DELEGATE_TwoParams(FOnLXJDeath, AActor* /*Owner*/, AActor* /*Killer*/);
DECLARE_MULTICAST_DELEGATE_FourParams(FOnLXJDamaged, AActor* /*Owner*/, float /*Amount*/, float /*Health*/, AActor* /*Source*/);

UCLASS(ClassGroup = (LingXuJie), meta = (BlueprintSpawnableComponent))
class LINGXUJIE_API ULXJHealthComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	ULXJHealthComponent();

	virtual void BeginPlay() override;

	/** Applies damage and spawns a floating damage number above the owner. */
	void ApplyDamage(float Amount, AActor* Source);

	void ResetHealth();

	/**
	 * Grows the health bar (level ups, gear). HealAmount restores that much current health,
	 * clamped to the new maximum, so a level up can refill the room it just added.
	 */
	void AddMaxHealth(float Amount, float HealAmount = 0.f);

	/** Direct heal, clamped to the current maximum. Used by consumables/level ups. */
	void Heal(float Amount);

	UFUNCTION(BlueprintPure, Category = "LingXuJie")
	float GetHealth() const { return Health; }

	UFUNCTION(BlueprintPure, Category = "LingXuJie")
	float GetMaxHealth() const { return MaxHealth; }

	UFUNCTION(BlueprintPure, Category = "LingXuJie")
	bool IsDead() const { return bDead; }

	UFUNCTION(BlueprintPure, Category = "LingXuJie")
	float GetHealthPercent() const { return MaxHealth > 0.f ? Health / MaxHealth : 0.f; }

	FOnLXJDeath OnDeath;
	FOnLXJDamaged OnDamaged;

	UPROPERTY(EditAnywhere, Category = "LingXuJie")
	float MaxHealth = 100.f;

private:
	float Health = 0.f;
	bool bDead = false;
};
