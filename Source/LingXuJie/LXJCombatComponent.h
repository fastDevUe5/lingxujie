// Lightweight ability system for the P0 prototype: three abilities, qi resource, cooldowns.
// Deliberately not GAS - it is a few hundred lines and can be replaced later if needed.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "LXJCombatComponent.generated.h"

UCLASS(ClassGroup = (LingXuJie), meta = (BlueprintSpawnableComponent))
class LINGXUJIE_API ULXJCombatComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	ULXJCombatComponent();

	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	/** Slot 0 = basic attack (LMB), 1 = single-target sword art (1), 2 = AOE (2). */
	bool TryUse(int32 Slot);

	UFUNCTION(BlueprintPure, Category = "LingXuJie")
	float GetQi() const { return Qi; }

	UFUNCTION(BlueprintPure, Category = "LingXuJie")
	float GetMaxQi() const { return MaxQi; }

	UFUNCTION(BlueprintPure, Category = "LingXuJie")
	float GetCooldownRemaining(int32 Slot) const { return Slot >= 0 && Slot < 3 ? Cooldowns[Slot] : 0.f; }

	UFUNCTION(BlueprintPure, Category = "LingXuJie")
	float GetCooldownDuration(int32 Slot) const { return Slot >= 0 && Slot < 3 ? CooldownDurations[Slot] : 0.f; }

	UFUNCTION(BlueprintPure, Category = "LingXuJie")
	int32 GetQiCost(int32 Slot) const { return Slot >= 0 && Slot < 3 ? FMath::RoundToInt(QiCosts[Slot]) : 0; }

	UFUNCTION(BlueprintPure, Category = "LingXuJie")
	static FString GetSlotName(int32 Slot);

	/** Permanent percentage damage bonus (level ups, weapons). 0.10 == +10% damage. */
	void AddAttackPercent(float Percent);

	/**
	 * Where the owner is aiming (camera yaw for the player). Attack sweeps use this instead
	 * of the actor's forward vector, which goes stale when standing still.
	 */
	void SetAimDirection(const FVector& InAim) { AimDirection = InAim.GetSafeNormal2D(); }

	UFUNCTION(BlueprintPure, Category = "LingXuJie")
	float GetAttackPercent() const { return AttackPercent; }

	UFUNCTION(BlueprintPure, Category = "LingXuJie")
	float GetDamageMultiplier() const { return 1.f + AttackPercent; }

private:
	void BasicAttack();
	void SingleTargetSkill();
	void AreaSkill();

	/** Sphere sweep in front of the owner, applying damage to every health component hit. */
	int32 SweepDamage(float Range, float Radius, float Damage);

	/** Sphere overlap around the owner (AOE). */
	int32 OverlapDamage(float Radius, float Damage);

	/** Skill base damage scaled by the accumulated attack bonus. */
	float ScaleDamage(float BaseDamage) const { return BaseDamage * GetDamageMultiplier(); }

	/** Aim first, actor facing second. */
	FVector GetAimForward() const;

	float AttackPercent = 0.f;
	FVector AimDirection = FVector::ZeroVector;

	float Qi = 100.f;
	float MaxQi = 100.f;
	float QiRegenPerSecond = 16.f;

	float Cooldowns[3] = { 0.f, 0.f, 0.f };
	float CooldownDurations[3] = { 0.45f, 4.f, 8.f };
	float QiCosts[3] = { 0.f, 30.f, 60.f };
	bool bBasicWasDown = false;
};
