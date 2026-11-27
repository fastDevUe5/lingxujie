#include "LXJProgressComponent.h"

#include "GameFramework/Actor.h"
#include "LXJCombatComponent.h"
#include "LXJHealthComponent.h"

ULXJProgressComponent::ULXJProgressComponent()
{
	// Ticks only to fade the level-up banner; cheap enough to leave on.
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.bStartWithTickEnabled = false;
}

float ULXJProgressComponent::ExperienceRequiredForLevel(int32 InLevel)
{
	// Gentle linear ramp: 100 exp for level 1 -> 2, then +50 per level.
	// Tuned so one training dummy (45 exp) is a meaningful bite at level 1.
	const int32 SafeLevel = FMath::Clamp(InLevel, 1, LevelCap);
	return 50.f + 50.f * static_cast<float>(SafeLevel);
}

float ULXJProgressComponent::GetExperiencePercent() const
{
	if (IsMaxLevel())
	{
		return 1.f;
	}
	const float Required = ExperienceRequiredForLevel(Level);
	return Required > 0.f ? FMath::Clamp(Experience / Required, 0.f, 1.f) : 0.f;
}

int32 ULXJProgressComponent::AddExperience(float Amount)
{
	if (Amount <= 0.f || IsMaxLevel())
	{
		return 0;
	}

	Experience += Amount;

	int32 LevelsGained = 0;
	while (Level < LevelCap && Experience >= ExperienceRequiredForLevel(Level))
	{
		Experience -= ExperienceRequiredForLevel(Level);
		++Level;
		++LevelsGained;
		ApplyLevelUp(Level);
	}

	if (IsMaxLevel())
	{
		Experience = 0.f;
	}

	return LevelsGained;
}

void ULXJProgressComponent::GrantKillReward(AActor* Killer, float Amount)
{
	if (!Killer || Amount <= 0.f)
	{
		return;
	}

	// No cast to the player class on purpose: anything carrying a progress component
	// (player now, pets/parties later) earns the reward.
	if (ULXJProgressComponent* Target = Killer->FindComponentByClass<ULXJProgressComponent>())
	{
		Target->AddExperience(Amount);
	}
}

void ULXJProgressComponent::SetStatTargets(ULXJHealthComponent* InHealth, ULXJCombatComponent* InCombat)
{
	HealthTarget = InHealth;
	CombatTarget = InCombat;
}

void ULXJProgressComponent::ApplyLevelUp(int32 NewLevel)
{
	AActor* Owner = GetOwner();

	ULXJHealthComponent* Health = HealthTarget
		? HealthTarget.Get()
		: (Owner ? Owner->FindComponentByClass<ULXJHealthComponent>() : nullptr);
	if (Health)
	{
		// Level ups grow the bar and heal by the same amount: no free full heal every level.
		Health->AddMaxHealth(MaxHealthPerLevel, MaxHealthPerLevel);
	}

	ULXJCombatComponent* Combat = CombatTarget
		? CombatTarget.Get()
		: (Owner ? Owner->FindComponentByClass<ULXJCombatComponent>() : nullptr);
	if (Combat)
	{
		Combat->AddAttackPercent(AttackPercentPerLevel);
	}

	LevelUpFlash = LevelUpFlashDuration;
	PrimaryComponentTick.SetTickFunctionEnable(true);

	UE_LOG(LogTemp, Log, TEXT("[LingXuJie] %s reached level %d"), *GetNameSafe(Owner), NewLevel);
	OnLevelUp.Broadcast(NewLevel, Owner);
}

void ULXJProgressComponent::AdvanceLevelUpFlash(float DeltaSeconds)
{
	if (LevelUpFlash <= 0.f)
	{
		return;
	}

	LevelUpFlash = FMath::Max(0.f, LevelUpFlash - DeltaSeconds);
	if (LevelUpFlash <= 0.f)
	{
		// Nothing left to animate: stop ticking until the next level up.
		PrimaryComponentTick.SetTickFunctionEnable(false);
	}
}

void ULXJProgressComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	AdvanceLevelUpFlash(DeltaTime);
}
