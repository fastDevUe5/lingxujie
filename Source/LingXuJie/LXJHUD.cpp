#include "LXJHUD.h"

#include "Engine/Canvas.h"
#include "Engine/Engine.h"
#include "Engine/Font.h"
#include "LXJCharacter.h"
#include "LXJCombatComponent.h"
#include "LXJHealthComponent.h"
#include "LXJInventoryComponent.h"
#include "LXJItems.h"
#include "LXJProgressComponent.h"
#include "GameFramework/PlayerController.h"

namespace
{
	const FLinearColor Paper(0.92f, 0.95f, 1.0f, 1.f);
	const FLinearColor Dim(0.60f, 0.66f, 0.76f, 1.f);
	const FLinearColor Gold(1.0f, 0.80f, 0.32f, 1.f);
	const FLinearColor Jade(0.35f, 0.90f, 0.72f, 1.f);
	const FLinearColor QiBlue(0.38f, 0.70f, 1.0f, 1.f);
	const FLinearColor HpRed(0.92f, 0.30f, 0.28f, 1.f);
	const FLinearColor ExpViolet(0.72f, 0.52f, 1.0f, 1.f);
	const FLinearColor Back(0.02f, 0.03f, 0.05f, 0.72f);
}

void ALXJHUD::AddDamageNumber(const FVector& WorldLocation, float Amount)
{
	FDamagePopup Popup;
	Popup.World = WorldLocation;
	Popup.Text = FString::Printf(TEXT("%d"), FMath::RoundToInt(Amount));
	DamagePopups.Add(Popup);
}

void ALXJHUD::AddPickupToast(const FString& Text)
{
	FToast Toast;
	Toast.Text = Text;
	Toasts.Add(Toast);

	// Keep the feed short: five lines is plenty for a prototype.
	while (Toasts.Num() > 5)
	{
		Toasts.RemoveAt(0);
	}
}

void ALXJHUD::DrawLootFeed(float DeltaSeconds, float ScreenWidth)
{
	for (int32 Index = Toasts.Num() - 1; Index >= 0; --Index)
	{
		FToast& Toast = Toasts[Index];
		Toast.Age += DeltaSeconds;
		if (Toast.Age >= Toast.Life)
		{
			Toasts.RemoveAt(Index);
			continue;
		}
	}

	// Newest last, scrolling up from the bottom of the feed block.
	float Y = 150.f;
	for (int32 Index = 0; Index < Toasts.Num(); ++Index)
	{
		const FToast& Toast = Toasts[Index];
		const float Alpha = FMath::Clamp(1.f - (Toast.Age / Toast.Life), 0.f, 1.f);
		DrawLabel(Toast.Text, ScreenWidth - 250.f, Y, FLinearColor(0.85f, 0.95f, 1.0f, Alpha), 0.95f);
		Y += 22.f;
	}
}

void ALXJHUD::DrawHUD()
{
	Super::DrawHUD();

	if (!Canvas)
	{
		return;
	}

	const float DeltaSeconds = GetWorld() ? GetWorld()->GetDeltaSeconds() : 0.f;

	// Floating damage numbers: project their world position to the screen every frame.
	for (int32 Index = DamagePopups.Num() - 1; Index >= 0; --Index)
	{
		FDamagePopup& Popup = DamagePopups[Index];
		Popup.Age += DeltaSeconds;
		if (Popup.Age >= Popup.Life)
		{
			DamagePopups.RemoveAt(Index);
			continue;
		}

		const FVector World = Popup.World + FVector(0.f, 0.f, 70.f * (Popup.Age / Popup.Life));
		const FVector Screen = Canvas->Project(World);
		if (Screen.Z <= 0.f)
		{
			continue;
		}

		const float Alpha = 1.f - (Popup.Age / Popup.Life);
		const float Scale = 1.6f * (0.6f + 0.4f * Alpha);
		DrawLabelCentered(Popup.Text, Screen.X, Screen.Y, FLinearColor(1.f, 0.84f, 0.32f, Alpha), Scale);
	}

	const ALXJCharacter* Character = Cast<ALXJCharacter>(GetOwningPawn());
	if (!Character)
	{
		return;
	}

	const float W = Canvas->ClipX;
	const float H = Canvas->ClipY;

	DrawLabel(TEXT("LINGXUJIE  -  P0 COMBAT TEST"), 36.f, 30.f, Gold, 1.25f);

	const ULXJProgressComponent* Progress = Character->GetProgressComponent();
	if (Progress)
	{
		DrawLabel(FString::Printf(TEXT("Lv.%d"), Progress->GetLevel()), 36.f, 62.f, Gold, 1.15f);
		if (Progress->IsMaxLevel())
		{
			DrawLabel(TEXT("EXP   MAX"), 118.f, 64.f, ExpViolet, 1.0f);
		}
		else
		{
			DrawLabel(FString::Printf(TEXT("EXP   %d / %d"),
				FMath::RoundToInt(Progress->GetExperience()),
				FMath::RoundToInt(Progress->GetExperienceToNextLevel())), 118.f, 64.f, ExpViolet, 1.0f);
		}
		DrawBar(118.f, 88.f, 226.f, 10.f, Progress->GetExperiencePercent(), ExpViolet, Back);
	}

	// Level up banner: fades from the progress component's flash timer.
	if (Progress && Progress->GetLevelUpFlashPercent() > 0.f)
	{
		const float Flash = Progress->GetLevelUpFlashPercent();
		const float Alpha = FMath::Min(1.f, Flash * 2.f);
		const FString Banner = FString::Printf(TEXT("LEVEL UP   Lv.%d"), Progress->GetLevel());
		DrawLabelCentered(Banner, W * 0.5f, H * 0.24f - 24.f * Flash, FLinearColor(1.f, 0.86f, 0.36f, Alpha), 2.0f);
	}

	DrawLootFeed(DeltaSeconds, W);

	// Bag + equipment readout. No bag UI yet: auto-equip keeps the best piece worn.
	if (const ULXJInventoryComponent* Inventory = Character->GetInventoryComponent())
	{
		const int32 Stones = Inventory->GetItemCount(LXJItems::SpiritStoneId());
		DrawLabel(FString::Printf(TEXT("LING SHI  %d"), Stones), 44.f, H - 166.f, Gold, 1.0f);
		DrawLabel(FString::Printf(TEXT("BAG  %d / %d"), Inventory->GetUsedSlots(), ULXJInventoryComponent::MaxSlots),
			190.f, H - 166.f, Dim, 1.0f);

		auto SlotName = [](FName ItemId) -> FString
		{
			if (ItemId.IsNone())
			{
				return TEXT("--");
			}
			const FLXJItemDef* Item = LXJItems::Find(ItemId);
			return Item ? Item->DisplayName : ItemId.ToString();
		};

		DrawLabel(FString::Printf(TEXT("W: %s"), *SlotName(Inventory->GetEquippedId(ELXJItemType::Weapon))),
			44.f, H - 188.f, Jade, 0.9f);
		DrawLabel(FString::Printf(TEXT("A: %s"), *SlotName(Inventory->GetEquippedId(ELXJItemType::Armor))),
			264.f, H - 188.f, Jade, 0.9f);
	}

	const ULXJHealthComponent* Health = Character->GetHealthComponent();
	if (Health)
	{
		DrawLabel(FString::Printf(TEXT("HP   %d / %d"), FMath::RoundToInt(Health->GetHealth()), FMath::RoundToInt(Health->GetMaxHealth())),
			44.f, H - 116.f, Paper, 1.0f);
		DrawBar(44.f, H - 96.f, 320.f, 18.f, Health->GetHealthPercent(), HpRed, Back);
	}

	if (const ULXJCombatComponent* Combat = Character->GetCombatComponent())
	{
		DrawLabel(FString::Printf(TEXT("QI   %d / %d"), FMath::RoundToInt(Combat->GetQi()), FMath::RoundToInt(Combat->GetMaxQi())),
			44.f, H - 66.f, Paper, 1.0f);
		DrawBar(44.f, H - 46.f, 320.f, 18.f, Combat->GetQi() / FMath::Max(Combat->GetMaxQi(), 1.f), QiBlue, Back);

		const float SlotW = 132.f;
		const float SlotH = 66.f;
		const float Gap = 14.f;
		const float TotalW = SlotW * 3.f + Gap * 2.f;
		float X = (W - TotalW) * 0.5f;
		const float Y = H - SlotH - 40.f;

		for (int32 Slot = 0; Slot < 3; ++Slot)
		{
			const float Remaining = Combat->GetCooldownRemaining(Slot);
			const float Duration = FMath::Max(Combat->GetCooldownDuration(Slot), 0.01f);
			const float Percent = Remaining > 0.f ? 1.f - (Remaining / Duration) : 1.f;
			const FString KeyLabel = Slot == 0 ? TEXT("LMB/J") : FString::Printf(TEXT("%d"), Slot);
			DrawSlot(X, Y, SlotW, SlotH, Slot, KeyLabel, ULXJCombatComponent::GetSlotName(Slot), Percent, Combat->GetQiCost(Slot));
			X += SlotW + Gap;
		}
	}

	// Crosshair.
	DrawLabelCentered(TEXT("+"), W * 0.5f, H * 0.5f - 14.f, Paper, 1.2f);
}

void ALXJHUD::DrawBar(float X, float Y, float Width, float Height, float Percent, const FLinearColor& Fill, const FLinearColor& BackColor)
{
	DrawRect(BackColor, X, Y, Width, Height);
	DrawRect(Fill, X, Y, Width * FMath::Clamp(Percent, 0.f, 1.f), Height);
}

void ALXJHUD::DrawSlot(float X, float Y, float W, float H, int32 SlotIndex, const FString& KeyLabel, const FString& Name, float CooldownPercent, int32 QiCost)
{
	DrawRect(Back, X, Y, W, H);
	DrawRect(FLinearColor(0.10f, 0.12f, 0.16f, 0.9f), X, Y, W, 20.f);

	// Cooldown sweep: remaining time darkens the lower part of the slot.
	if (CooldownPercent < 1.f)
	{
		DrawRect(FLinearColor(0.f, 0.f, 0.f, 0.55f), X, Y + H * CooldownPercent, W, H * (1.f - CooldownPercent));
	}

	DrawLabel(KeyLabel, X + 8.f, Y + 2.f, Gold, 0.9f);
	DrawLabel(Name, X + 8.f, Y + 26.f, Paper, 0.95f);
	DrawLabel(FString::Printf(TEXT("QI %d"), QiCost), X + 8.f, Y + 46.f, Dim, 0.8f);
}

void ALXJHUD::DrawLabel(const FString& TextValue, float X, float Y, const FLinearColor& Color, float Scale)
{
	UFont* Font = GEngine ? GEngine->GetSmallFont() : nullptr;
	if (!Font || !Canvas)
	{
		return;
	}
	FCanvasTextItem Item(FVector2D(X, Y), FText::FromString(TextValue), Font, Color);
	Item.Scale = FVector2D(Scale, Scale);
	Canvas->DrawItem(Item);
}

void ALXJHUD::DrawLabelCentered(const FString& TextValue, float CenterX, float Y, const FLinearColor& Color, float Scale)
{
	UFont* Font = GEngine ? GEngine->GetSmallFont() : nullptr;
	if (!Font || !Canvas)
	{
		return;
	}
	FCanvasTextItem Item(FVector2D(CenterX - TextValue.Len() * 3.2f * Scale, Y), FText::FromString(TextValue), Font, Color);
	Item.Scale = FVector2D(Scale, Scale);
	Canvas->DrawItem(Item);
}
