// Backpack + equipment for the P0 slice: stacked slots, a weapon slot and an armour slot,
// and the stat totals those two slots add up to.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "LXJItems.h"
#include "LXJInventoryComponent.generated.h"

class ULXJCombatComponent;
class ULXJHealthComponent;

DECLARE_MULTICAST_DELEGATE_TwoParams(FOnLXJItemPicked, FName /*ItemId*/, int32 /*Count*/);

UCLASS(ClassGroup = (LingXuJie), meta = (BlueprintSpawnableComponent))
class LINGXUJIE_API ULXJInventoryComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	ULXJInventoryComponent();

	static constexpr int32 MaxSlots = 12;
	static constexpr int32 MaxStack = 99;

	/** Stores items, stacking into existing lines. Returns false when the bag is full. */
	bool AddItem(FName ItemId, int32 Count);

	int32 GetItemCount(FName ItemId) const;
	const FLXJItemStack& GetStack(int32 Index) const;
	int32 GetUsedSlots() const;

	/** Wears one item from an inventory line. Returns true when it ended up in a slot. */
	bool EquipFromSlot(int32 Index);

	/** P0 convenience (there is no bag UI yet): wear it when the slot is empty or it is better. */
	bool TryAutoEquip(FName ItemId);

	void Unequip(ELXJItemType SlotType);

	FName GetEquippedId(ELXJItemType SlotType) const;

	/** Sum of the equipped items' bonuses (level ups use the same health/combat components). */
	float GetAttackBonus() const;
	float GetMaxHealthBonus() const;

	/** Who receives the equipment bonuses (the player character wires these up in its constructor). */
	void SetStatTargets(ULXJHealthComponent* InHealth, ULXJCombatComponent* InCombat);

	FOnLXJItemPicked OnItemPicked;

private:
	int32 FindStack(FName ItemId) const;
	int32 FindEmptySlot() const;
	void RemoveFromStack(int32 Index, int32 Count);
	const FLXJItemStack& GetSlotStack(ELXJItemType SlotType) const;

	/** Pushes the *delta* of the equipment bonuses into health/combat so level ups stay additive. */
	void ApplyEquipmentStats();

	UPROPERTY()
	TArray<FLXJItemStack> Slots;

	UPROPERTY()
	FLXJItemStack WeaponSlot;

	UPROPERTY()
	FLXJItemStack ArmorSlot;

	UPROPERTY()
	TObjectPtr<ULXJHealthComponent> HealthTarget;

	UPROPERTY()
	TObjectPtr<ULXJCombatComponent> CombatTarget;

	float AppliedAttackBonus = 0.f;
	float AppliedHealthBonus = 0.f;
};
