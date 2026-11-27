#include "LXJCombatComponent.h"

#include "LXJHealthComponent.h"
#include "CollisionQueryParams.h"
#include "Components/PrimitiveComponent.h"
#include "Engine/OverlapResult.h"
#include "Engine/World.h"
#include "GameFramework/Actor.h"
#include "GameFramework/PlayerController.h"

ULXJCombatComponent::ULXJCombatComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
}

void ULXJCombatComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	for (int32 Index = 0; Index < 3; ++Index)
	{
		Cooldowns[Index] = FMath::Max(0.f, Cooldowns[Index] - DeltaTime);
	}

	Qi = FMath::Min(MaxQi, Qi + QiRegenPerSecond * DeltaTime);
}

FString ULXJCombatComponent::GetSlotName(int32 Slot)
{
	switch (Slot)
	{
	case 0: return TEXT("JIAN JI");
	case 1: return TEXT("SWORD ART");
	case 2: return TEXT("QI BURST");
	default: return TEXT("?");
	}
}

bool ULXJCombatComponent::TryUse(int32 Slot)
{
	if (Slot < 0 || Slot > 2 || Cooldowns[Slot] > 0.f)
	{
		return false;
	}

	if (Qi < QiCosts[Slot])
	{
		UE_LOG(LogTemp, Log, TEXT("[LingXuJie] %s: not enough qi (%.0f/%.0f)"), *GetSlotName(Slot), Qi, QiCosts[Slot]);
		return false;
	}

	Qi -= QiCosts[Slot];
	Cooldowns[Slot] = CooldownDurations[Slot];

	switch (Slot)
	{
	case 0: BasicAttack(); break;
	case 1: SingleTargetSkill(); break;
	case 2: AreaSkill(); break;
	default: break;
	}
	return true;
}

void ULXJCombatComponent::BasicAttack()
{
	const int32 Hits = SweepDamage(320.f, 150.f, ScaleDamage(24.f));
	UE_LOG(LogTemp, Log, TEXT("[LingXuJie] Basic attack hits=%d dmg=%.0f"), Hits, ScaleDamage(24.f));
}

void ULXJCombatComponent::SingleTargetSkill()
{
	const int32 Hits = SweepDamage(1500.f, 200.f, ScaleDamage(120.f));
	UE_LOG(LogTemp, Log, TEXT("[LingXuJie] Sword art hits=%d dmg=%.0f"), Hits, ScaleDamage(120.f));
}

void ULXJCombatComponent::AreaSkill()
{
	const int32 Hits = OverlapDamage(750.f, ScaleDamage(70.f));
	UE_LOG(LogTemp, Log, TEXT("[LingXuJie] Qi burst hits=%d dmg=%.0f"), Hits, ScaleDamage(70.f));
}

void ULXJCombatComponent::AddAttackPercent(float Percent)
{
	// Negative deltas are legal: taking gear off removes its bonus. Keep the multiplier sane.
	if (FMath::IsNearlyZero(Percent))
	{
		return;
	}

	AttackPercent = FMath::Max(-0.9f, AttackPercent + Percent);
	UE_LOG(LogTemp, Log, TEXT("[LingXuJie] Attack bonus %+.0f%% (total x%.2f)"), Percent * 100.f, GetDamageMultiplier());
}

FVector ULXJCombatComponent::GetAimForward() const
{
	if (!AimDirection.IsNearlyZero())
	{
		return AimDirection;
	}
	const AActor* Owner = GetOwner();
	return Owner ? Owner->GetActorForwardVector().GetSafeNormal2D() : FVector::ForwardVector;
}

int32 ULXJCombatComponent::SweepDamage(float Range, float Radius, float Damage)
{
	AActor* Owner = GetOwner();
	UWorld* World = GetWorld();
	if (!Owner || !World)
	{
		return 0;
	}

	const FVector Start = Owner->GetActorLocation() + FVector(0.f, 0.f, 60.f);
	const FVector End = Start + GetAimForward() * Range;

	FCollisionQueryParams Params(SCENE_QUERY_STAT(LXJAbilitySweep), false, Owner);

	// Multi-sweep, not single: a single sweep stops at the first blocking thing (a decorative
	// stone, a qi node) and the monster standing behind it never takes the hit.
	TArray<FHitResult> Hits;
	World->SweepMultiByChannel(Hits, Start, End, FQuat::Identity, ECC_Pawn, FCollisionShape::MakeSphere(Radius), Params);

	const FVector Forward = GetAimForward();
	int32 Damaged = 0;
	TSet<AActor*> AlreadyHit;
	for (const FHitResult& Hit : Hits)
	{
		AActor* Other = Hit.GetActor();
		if (!Other || Other == Owner || AlreadyHit.Contains(Other))
		{
			continue;
		}

		// Scenery stops the swing visually but is not damageable.
		ULXJHealthComponent* OtherHealth = Other->FindComponentByClass<ULXJHealthComponent>();
		if (!OtherHealth)
		{
			continue;
		}

		// Only things in front of the aim count, except point-blank: a monster hugging the
		// player from behind must still be hit, otherwise every melee trade is a whiff.
		const FVector ToOther = (Other->GetActorLocation() - Owner->GetActorLocation()).GetSafeNormal2D();
		const float DistanceToOwner = FVector::Dist2D(Other->GetActorLocation(), Owner->GetActorLocation());
		const bool bInFront = FVector::DotProduct(ToOther, Forward) >= 0.f;
		const bool bPointBlank = DistanceToOwner <= Radius + 150.f;
		if (!bInFront && !bPointBlank)
		{
			continue;
		}

		OtherHealth->ApplyDamage(Damage, Owner);
		AlreadyHit.Add(Other);
		++Damaged;
	}

	UE_LOG(LogTemp, Verbose, TEXT("[LingXuJie] sweep owner=%s start=%s end=%s hits=%d"),
		*GetNameSafe(Owner), *Start.ToCompactString(), *End.ToCompactString(), Damaged);
	return Damaged;
}

int32 ULXJCombatComponent::OverlapDamage(float Radius, float Damage)
{
	AActor* Owner = GetOwner();
	UWorld* World = GetWorld();
	if (!Owner || !World)
	{
		return 0;
	}

	const FVector Center = Owner->GetActorLocation() + FVector(0.f, 0.f, 60.f);
	TArray<FOverlapResult> Overlaps;
	FCollisionQueryParams Params(SCENE_QUERY_STAT(LXJAbilityBurst), false, Owner);
	World->OverlapMultiByChannel(Overlaps, Center, FQuat::Identity, ECC_Pawn, FCollisionShape::MakeSphere(Radius), Params);

	int32 Hits = 0;
	TSet<AActor*> Damaged;
	for (const FOverlapResult& Overlap : Overlaps)
	{
		AActor* Other = Overlap.GetActor();
		if (!Other || Other == Owner || Damaged.Contains(Other))
		{
			continue;
		}

		if (ULXJHealthComponent* Health = Other->FindComponentByClass<ULXJHealthComponent>())
		{
			Health->ApplyDamage(Damage, Owner);
			Damaged.Add(Other);
			++Hits;
		}
	}
	return Hits;
}
