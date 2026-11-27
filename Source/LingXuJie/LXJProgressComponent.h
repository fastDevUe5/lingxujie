// Cultivation progress: experience, level ups and the stat rewards they hand out.
// Kept free of world/HUD lookups so the whole curve is unit-testable.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "LXJProgressComponent.generated.h"

class ULXJCombatComponent;
class ULXJHealthComponent;

DECLARE_MULTICAST_DELEGATE_TwoParams(FOnLXJLevelUp, int32 /*NewLevel*/, AActor* /*Owner*/);

UCLASS(ClassGroup = (LingXuJie), meta = (BlueprintSpawnableComponent))
class LINGXUJIE_API ULXJProgressComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	ULXJProgressComponent();

	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	/** Adds experience and rolls any level ups it earns. Returns the number of levels gained. */
	int32 AddExperience(float Amount);

	/** Gives kill experience to the actor that landed the killing blow. */
	static void GrantKillReward(AActor* Killer, float Amount);

	/**
	 * Binds the components that level ups buff. Owners that build their components in C++
	 * (the player character) call this once; the owner lookup below is just a safety net.
	 */
	void SetStatTargets(ULXJHealthComponent* InHealth, ULXJCombatComponent* InCombat);

	/** Advances the level-up banner flash. Public so tests can drive it without a world. */
	void AdvanceLevelUpFlash(float DeltaSeconds);

	/** Experience needed to go from Level to Level + 1. Static so the curve is easy to test. */
	static float ExperienceRequiredForLevel(int32 InLevel);

	static constexpr int32 LevelCap = 60;

	UFUNCTION(BlueprintPure, Category = "LingXuJie|Progress")
	int32 GetLevel() const { return Level; }

	UFUNCTION(BlueprintPure, Category = "LingXuJie|Progress")
	float GetExperience() const { return Experience; }

	UFUNCTION(BlueprintPure, Category = "LingXuJie|Progress")
	float GetExperienceToNextLevel() const { return ExperienceRequiredForLevel(Level); }

	UFUNCTION(BlueprintPure, Category = "LingXuJie|Progress")
	float GetExperiencePercent() const;

	UFUNCTION(BlueprintPure, Category = "LingXuJie|Progress")
	bool IsMaxLevel() const { return Level >= LevelCap; }

	/** 1.0 right after a level up, fading to 0.0 - the HUD uses it for the level banner. */
	UFUNCTION(BlueprintPure, Category = "LingXuJie|Progress")
	float GetLevelUpFlashPercent() const { return LevelUpFlashDuration > 0.f ? LevelUpFlash / LevelUpFlashDuration : 0.f; }

	FOnLXJLevelUp OnLevelUp;

	UPROPERTY(EditAnywhere, Category = "LingXuJie|Progress")
	float MaxHealthPerLevel = 18.f;

	UPROPERTY(EditAnywhere, Category = "LingXuJie|Progress")
	float AttackPercentPerLevel = 0.04f;

private:
	/** Applies one level's stat rewards to the bound (or owner-found) health/combat components. */
	void ApplyLevelUp(int32 NewLevel);

	UPROPERTY()
	TObjectPtr<ULXJHealthComponent> HealthTarget;

	UPROPERTY()
	TObjectPtr<ULXJCombatComponent> CombatTarget;

	UPROPERTY(EditAnywhere, Category = "LingXuJie|Progress")
	int32 Level = 1;

	UPROPERTY(EditAnywhere, Category = "LingXuJie|Progress")
	float Experience = 0.f;

	float LevelUpFlash = 0.f;
	float LevelUpFlashDuration = 1.6f;
};
