#include "LXJHealthComponent.h"

#include "Components/ActorComponent.h"
#include "Engine/World.h"
#include "GameFramework/Actor.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"
#include "LXJHUD.h"

ULXJHealthComponent::ULXJHealthComponent()
{
	PrimaryComponentTick.bCanEverTick = false;
}

void ULXJHealthComponent::BeginPlay()
{
	Super::BeginPlay();
	Health = MaxHealth;
}

void ULXJHealthComponent::ResetHealth()
{
	Health = MaxHealth;
	bDead = false;
}

void ULXJHealthComponent::AddMaxHealth(float Amount, float HealAmount)
{
	// Negative amounts are legal: taking gear off shrinks the bar again.
	if (FMath::IsNearlyZero(Amount))
	{
		return;
	}

	MaxHealth = FMath::Max(1.f, MaxHealth + Amount);
	if (HealAmount > 0.f && !bDead)
	{
		Heal(HealAmount);
	}
	Health = FMath::Min(Health, MaxHealth);
}

void ULXJHealthComponent::Heal(float Amount)
{
	if (Amount <= 0.f || bDead)
	{
		return;
	}

	Health = FMath::Min(MaxHealth, Health + Amount);
}

void ULXJHealthComponent::ApplyDamage(float Amount, AActor* Source)
{
	if (bDead || Amount <= 0.f)
	{
		return;
	}

	Health = FMath::Max(0.f, Health - Amount);

	if (AActor* Owner = GetOwner())
	{
		const FVector NumberLocation = Owner->GetActorLocation() + FVector(0.f, 0.f, 120.f);
		if (APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0))
		{
			if (ALXJHUD* HUD = Cast<ALXJHUD>(PC->GetHUD()))
			{
				HUD->AddDamageNumber(NumberLocation, Amount);
			}
		}
	}

	OnDamaged.Broadcast(GetOwner(), Amount, Health, Source);
	UE_LOG(LogTemp, Log, TEXT("[LingXuJie] %s took %.0f damage -> %.0f hp"),
		*GetNameSafe(GetOwner()), Amount, Health);

	if (Health <= 0.f)
	{
		bDead = true;
		OnDeath.Broadcast(GetOwner(), Source);
	}
}
