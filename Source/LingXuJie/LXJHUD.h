// Minimal Canvas HUD for the P0 prototype: health, qi, skill slots, crosshair.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "LXJHUD.generated.h"

UCLASS()
class LINGXUJIE_API ALXJHUD : public AHUD
{
	GENERATED_BODY()

public:
	virtual void DrawHUD() override;

	/** Queues a floating damage number at a world location (drawn in screen space). */
	void AddDamageNumber(const FVector& WorldLocation, float Amount);

	/** Queues a short "+3 LING SHI" style line in the loot feed. */
	void AddPickupToast(const FString& Text);

private:
	struct FDamagePopup
	{
		FVector World = FVector::ZeroVector;
		FString Text;
		float Age = 0.f;
		float Life = 1.4f;
	};

	struct FToast
	{
		FString Text;
		float Age = 0.f;
		float Life = 3.f;
	};

	TArray<FDamagePopup> DamagePopups;
	TArray<FToast> Toasts;

	void DrawBar(float X, float Y, float Width, float Height, float Percent, const FLinearColor& Fill, const FLinearColor& Back);
	void DrawSlot(float X, float Y, float W, float H, int32 SlotIndex, const FString& KeyLabel, const FString& Name, float CooldownPercent, int32 QiCost);
	void DrawLabel(const FString& Text, float X, float Y, const FLinearColor& Color, float Scale);
	void DrawLabelCentered(const FString& Text, float CenterX, float Y, const FLinearColor& Color, float Scale);
	void DrawLootFeed(float DeltaSeconds, float ScreenWidth);
};
