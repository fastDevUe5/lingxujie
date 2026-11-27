#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "LXJCombatComponent.h"
#include "LXJHealthComponent.h"
#include "LXJProgressComponent.h"

namespace
{
	/** A bare progress component with no owner: the stat rewards are then no-ops. */
	ULXJProgressComponent* MakeProgress()
	{
		return NewObject<ULXJProgressComponent>(GetTransientPackage());
	}
}

// The curve itself: every level must cost more than the one before, and stay finite.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FLXJProgressCurveTest, "LingXuJie.Progress.ExperienceCurve",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FLXJProgressCurveTest::RunTest(const FString& Parameters)
{
	TestTrue(TEXT("level 1 needs positive exp"), ULXJProgressComponent::ExperienceRequiredForLevel(1) > 0.f);

	// Level 1 -> 2 is the tuning anchor (one dummy is 45 exp).
	TestEqual(TEXT("level 1 -> 2 costs 100"),
		ULXJProgressComponent::ExperienceRequiredForLevel(1), 100.f);

	for (int32 Level = 1; Level < ULXJProgressComponent::LevelCap; ++Level)
	{
		const float Current = ULXJProgressComponent::ExperienceRequiredForLevel(Level);
		const float Next = ULXJProgressComponent::ExperienceRequiredForLevel(Level + 1);
		if (!TestTrue(FString::Printf(TEXT("level %d cost grows (%.0f -> %.0f)"), Level, Current, Next), Next > Current))
		{
			break;
		}
	}

	// Out-of-range levels are clamped instead of reading garbage.
	TestEqual(TEXT("level 0 clamps to level 1 cost"),
		ULXJProgressComponent::ExperienceRequiredForLevel(0), ULXJProgressComponent::ExperienceRequiredForLevel(1));
	TestEqual(TEXT("above cap clamps to cap cost"),
		ULXJProgressComponent::ExperienceRequiredForLevel(999), ULXJProgressComponent::ExperienceRequiredForLevel(ULXJProgressComponent::LevelCap));

	return true;
}

// Adding experience rolls level ups and keeps the remainder.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FLXJProgressLevelUpTest, "LingXuJie.Progress.AddExperienceLevelsUp",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FLXJProgressLevelUpTest::RunTest(const FString& Parameters)
{
	ULXJProgressComponent* Progress = MakeProgress();

	TestEqual(TEXT("starts at level 1"), Progress->GetLevel(), 1);
	TestEqual(TEXT("starts with 0 exp"), Progress->GetExperience(), 0.f);

	TestEqual(TEXT("45 exp is not a level"), Progress->AddExperience(45.f), 0);
	TestEqual(TEXT("level unchanged"), Progress->GetLevel(), 1);
	TestEqual(TEXT("exp banked"), Progress->GetExperience(), 45.f);

	// 45 + 60 = 105 crosses the 100 needed for level 2, keeping 5 exp.
	TestEqual(TEXT("one level gained"), Progress->AddExperience(60.f), 1);
	TestEqual(TEXT("now level 2"), Progress->GetLevel(), 2);
	TestEqual(TEXT("remainder carried over"), Progress->GetExperience(), 5.f);
	TestEqual(TEXT("next level costs 150"), Progress->GetExperienceToNextLevel(), 150.f);

	// A single fat reward must chain several level ups (150 for L3, 200 for L4 => 5 + 400 - 350 = 55).
	const int32 BigLevels = Progress->AddExperience(400.f);
	TestEqual(TEXT("two more levels in one grant"), BigLevels, 2);
	TestEqual(TEXT("now level 4"), Progress->GetLevel(), 4);
	TestEqual(TEXT("55 exp left over"), Progress->GetExperience(), 55.f);

	// Negative/zero rewards are ignored rather than eating bar progress.
	TestEqual(TEXT("zero exp gains nothing"), Progress->AddExperience(0.f), 0);
	TestEqual(TEXT("negative exp gains nothing"), Progress->AddExperience(-500.f), 0);
	TestEqual(TEXT("level survived bad input"), Progress->GetLevel(), 4);

	return true;
}

// The level cap is a hard stop: no overflow exp, no runaway levels.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FLXJProgressCapTest, "LingXuJie.Progress.LevelCap",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FLXJProgressCapTest::RunTest(const FString& Parameters)
{
	ULXJProgressComponent* Progress = MakeProgress();

	// One huge reward should stop exactly at the cap.
	Progress->AddExperience(10000000.f);
	TestEqual(TEXT("stopped at the cap"), Progress->GetLevel(), ULXJProgressComponent::LevelCap);
	TestTrue(TEXT("reports max level"), Progress->IsMaxLevel());
	TestEqual(TEXT("no exp banked once capped"), Progress->GetExperience(), 0.f);
	TestEqual(TEXT("bar reads full"), Progress->GetExperiencePercent(), 1.f);
	TestEqual(TEXT("further exp is discarded"), Progress->AddExperience(500.f), 0);
	TestEqual(TEXT("level stays capped"), Progress->GetLevel(), ULXJProgressComponent::LevelCap);

	return true;
}

// Level-up flash drives the HUD banner and must not stick around.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FLXJProgressFlashTest, "LingXuJie.Progress.LevelUpFlash",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FLXJProgressFlashTest::RunTest(const FString& Parameters)
{
	ULXJProgressComponent* Progress = MakeProgress();
	TestEqual(TEXT("no flash before a level up"), Progress->GetLevelUpFlashPercent(), 0.f);

	Progress->AddExperience(100.f);
	TestTrue(TEXT("flash starts after level up"), Progress->GetLevelUpFlashPercent() > 0.9f);

	Progress->AdvanceLevelUpFlash(0.8f);
	const float Halfway = Progress->GetLevelUpFlashPercent();
	TestTrue(TEXT("flash decays"), Halfway < 0.9f && Halfway > 0.f);

	Progress->AdvanceLevelUpFlash(5.f);
	TestEqual(TEXT("flash expires"), Progress->GetLevelUpFlashPercent(), 0.f);

	return true;
}

// A kill reward only lands when the killer can actually gain experience.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FLXJProgressKillRewardTest, "LingXuJie.Progress.KillReward",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FLXJProgressKillRewardTest::RunTest(const FString& Parameters)
{
	// No killer (environmental damage) and no reward must both be silent no-ops.
	ULXJProgressComponent::GrantKillReward(nullptr, 50.f);
	ULXJProgressComponent::GrantKillReward(nullptr, 0.f);

	TestTrue(TEXT("null killer did not crash"), true);
	return true;
}

// Level ups must move the real stats: health bar grows and damage multiplier rises.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FLXJProgressStatRewardTest, "LingXuJie.Progress.StatRewards",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FLXJProgressStatRewardTest::RunTest(const FString& Parameters)
{
	// Components are bound explicitly (like the player character does in its constructor),
	// so the test needs no world, no actor and no registered component.
	ULXJHealthComponent* Health = NewObject<ULXJHealthComponent>(GetTransientPackage());
	ULXJCombatComponent* Combat = NewObject<ULXJCombatComponent>(GetTransientPackage());
	ULXJProgressComponent* Progress = NewObject<ULXJProgressComponent>(GetTransientPackage());
	Progress->SetStatTargets(Health, Combat);

	Health->MaxHealth = 300.f;
	Health->ResetHealth();

	const float BaseMultiplier = Combat->GetDamageMultiplier();
	TestEqual(TEXT("starts at x1 damage"), BaseMultiplier, 1.f);
	TestEqual(TEXT("starts at full health"), Health->GetHealth(), 300.f);

	Progress->AddExperience(100.f);

	TestEqual(TEXT("level 2"), Progress->GetLevel(), 2);
	TestEqual(TEXT("max health grew by the per-level amount"), Health->GetMaxHealth(), 300.f + Progress->MaxHealthPerLevel);
	TestEqual(TEXT("current health healed by the same amount"), Health->GetHealth(), 300.f + Progress->MaxHealthPerLevel);
	TestTrue(TEXT("attack bonus applied"), Combat->GetAttackPercent() > 0.f);
	TestTrue(TEXT("damage multiplier above 1"), Combat->GetDamageMultiplier() > 1.f);

	// Two levels later the buffs must stack, not replace each other.
	Progress->AddExperience(150.f + 200.f);
	TestEqual(TEXT("level 4"), Progress->GetLevel(), 4);
	TestEqual(TEXT("max health stacks"), Health->GetMaxHealth(), 300.f + Progress->MaxHealthPerLevel * 3.f);
	TestEqual(TEXT("attack bonus stacks"), Combat->GetAttackPercent(), Progress->AttackPercentPerLevel * 3.f);

	return true;
}

#endif // WITH_DEV_AUTOMATION_TESTS
