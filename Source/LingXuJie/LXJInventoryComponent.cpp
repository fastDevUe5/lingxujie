#include "LXJInventoryComponent.h"

#include "LXJCombatComponent.h"
#include "LXJHealthComponent.h"

ULXJInventoryComponent::ULXJInventoryComponent()
{
	PrimaryComponentTick.bCanEverTick = false;
	Slots.SetNum(MaxSlots);
}

int32 ULXJInventoryComponent::FindStack(FName ItemId) const
{
	for (int32 Index = 0; Index < Slots.Num(); ++Index)
	{
		if (Slots[Index].ItemId == ItemId && Slots[Index].Count > 0)
		{
			return Index;
		}
	}
	return INDEX_NONE;
}

int32 ULXJInventoryComponent::FindEmptySlot() const
{
	for (int32 Index = 0; Index < MaxSlots; ++Index)
	{
		const bool bFree = !Slots.IsValidIndex(Index) || Slots[Index].IsEmpty();
		if (bFree)
		{
			return Index;
		}
	}
	return INDEX_NONE;
}

bool ULXJInventoryComponent::AddItem(FName ItemId, int32 Count)
{
	if (ItemId.IsNone() || Count <= 0)
	{
		return false;
	}

	// Unknown ids would silently rot in the bag; reject them at the door.
	if (!LXJItems::Find(ItemId))
	{
		UE_LOG(LogTemp, Warning, TEXT("[LingXuJie] AddItem: unknown item id '%s'"), *ItemId.ToString());
		return false;
	}

	if (Slots.Num() < MaxSlots)
	{
		Slots.SetNum(MaxSlots);
	}

	bool bAdded = false;
	int32 Taken = 0;

	// Top up existing lines first (stacking).
	const int32 Existing = FindStack(ItemId);
	if (Existing != INDEX_NONE)
	{
		const int32 Room = MaxStack - Slots[Existing].Count;
		const int32 Stacked = FMath::Min(Room, Count);
		if (Stacked > 0)
		{
			Slots[Existing].Count += Stacked;
			Count -= Stacked;
			Taken += Stacked;
			bAdded = true;
		}
	}

	// Then spill into empty slots, one stack at a time.
	while (Count > 0)
	{
		const int32 Empty = FindEmptySlot();
		if (Empty == INDEX_NONE)
		{
			break;
		}
		const int32 Spilled = FMath::Min(MaxStack, Count);
		Slots[Empty].ItemId = ItemId;
		Slots[Empty].Count = Spilled;
		Count -= Spilled;
		Taken += Spilled;
		bAdded = true;
	}

	if (bAdded)
	{
		OnItemPicked.Broadcast(ItemId, Taken);
	}
	else
	{
		UE_LOG(LogTemp, Log, TEXT("[LingXuJie] Bag full, could not store %s"), *ItemId.ToString());
	}

	return bAdded && Count <= 0;
}

int32 ULXJInventoryComponent::GetItemCount(FName ItemId) const
{
	int32 Total = 0;
	for (const FLXJItemStack& Stack : Slots)
	{
		if (Stack.ItemId == ItemId)
		{
			Total += Stack.Count;
		}
	}
	return Total;
}

const FLXJItemStack& ULXJInventoryComponent::GetStack(int32 Index) const
{
	static const FLXJItemStack Empty;
	return Slots.IsValidIndex(Index) ? Slots[Index] : Empty;
}

int32 ULXJInventoryComponent::GetUsedSlots() const
{
	int32 Used = 0;
	for (const FLXJItemStack& Stack : Slots)
	{
		if (!Stack.IsEmpty())
		{
			++Used;
		}
	}
	return Used;
}

const FLXJItemStack& ULXJInventoryComponent::GetSlotStack(ELXJItemType SlotType) const
{
	return SlotType == ELXJItemType::Armor ? ArmorSlot : WeaponSlot;
}

FName ULXJInventoryComponent::GetEquippedId(ELXJItemType SlotType) const
{
	return GetSlotStack(SlotType).ItemId;
}

void ULXJInventoryComponent::RemoveFromStack(int32 Index, int32 Count)
{
	if (!Slots.IsValidIndex(Index) || Count <= 0)
	{
		return;
	}

	Slots[Index].Count = FMath::Max(0, Slots[Index].Count - Count);
	if (Slots[Index].Count <= 0)
	{
		Slots[Index] = FLXJItemStack();
	}
}

bool ULXJInventoryComponent::EquipFromSlot(int32 Index)
{
	if (!Slots.IsValidIndex(Index) || Slots[Index].IsEmpty())
	{
		return false;
	}

	const FLXJItemDef* Item = LXJItems::Find(Slots[Index].ItemId);
	if (!Item || Item->Type == ELXJItemType::Material)
	{
		return false;
	}

	const FName NewItemId = Slots[Index].ItemId;
	RemoveFromStack(Index, 1);

	// Whatever was worn goes back into the bag (we just freed a slot, so it fits).
	FLXJItemStack& Target = Item->Type == ELXJItemType::Armor ? ArmorSlot : WeaponSlot;
	const FName OldItemId = Target.ItemId;
	if (!OldItemId.IsNone())
	{
		AddItem(OldItemId, 1);
	}

	Target.ItemId = NewItemId;
	Target.Count = 1;

	ApplyEquipmentStats();
	UE_LOG(LogTemp, Log, TEXT("[LingXuJie] Equipped %s (was %s)"),
		*Item->DisplayName, OldItemId.IsNone() ? TEXT("nothing") : *OldItemId.ToString());
	return true;
}

bool ULXJInventoryComponent::TryAutoEquip(FName ItemId)
{
	const FLXJItemDef* Item = LXJItems::Find(ItemId);
	if (!Item || Item->Type == ELXJItemType::Material)
	{
		return false;
	}

	const FLXJItemStack& Equipped = GetSlotStack(Item->Type);
	if (!Equipped.ItemId.IsNone())
	{
		const FLXJItemDef* Current = LXJItems::Find(Equipped.ItemId);
		const float NewScore = Item->AttackPercent + Item->MaxHealth;
		const float CurrentScore = Current ? Current->AttackPercent + Current->MaxHealth : 0.f;
		if (NewScore <= CurrentScore)
		{
			return false;
		}
	}

	const int32 Index = FindStack(ItemId);
	return Index != INDEX_NONE && EquipFromSlot(Index);
}

void ULXJInventoryComponent::Unequip(ELXJItemType SlotType)
{
	FLXJItemStack& Slot = SlotType == ELXJItemType::Armor ? ArmorSlot : WeaponSlot;
	if (Slot.ItemId.IsNone())
	{
		return;
	}

	const FName ItemId = Slot.ItemId;
	Slot = FLXJItemStack();

	if (AddItem(ItemId, 1))
	{
		ApplyEquipmentStats();
		UE_LOG(LogTemp, Log, TEXT("[LingXuJie] Unequipped %s"), *ItemId.ToString());
	}
	else
	{
		// No room: keep wearing it rather than deleting the item.
		Slot.ItemId = ItemId;
		Slot.Count = 1;
		UE_LOG(LogTemp, Log, TEXT("[LingXuJie] Bag full, keeping %s equipped"), *ItemId.ToString());
	}
}

float ULXJInventoryComponent::GetAttackBonus() const
{
	float Total = 0.f;
	if (const FLXJItemDef* Weapon = LXJItems::Find(WeaponSlot.ItemId))
	{
		Total += Weapon->AttackPercent;
	}
	if (const FLXJItemDef* Armor = LXJItems::Find(ArmorSlot.ItemId))
	{
		Total += Armor->AttackPercent;
	}
	return Total;
}

float ULXJInventoryComponent::GetMaxHealthBonus() const
{
	float Total = 0.f;
	if (const FLXJItemDef* Weapon = LXJItems::Find(WeaponSlot.ItemId))
	{
		Total += Weapon->MaxHealth;
	}
	if (const FLXJItemDef* Armor = LXJItems::Find(ArmorSlot.ItemId))
	{
		Total += Armor->MaxHealth;
	}
	return Total;
}

void ULXJInventoryComponent::SetStatTargets(ULXJHealthComponent* InHealth, ULXJCombatComponent* InCombat)
{
	HealthTarget = InHealth;
	CombatTarget = InCombat;
	ApplyEquipmentStats();
}

void ULXJInventoryComponent::ApplyEquipmentStats()
{
	const float NewAttack = GetAttackBonus();
	const float NewHealth = GetMaxHealthBonus();

	// Only push the difference: level ups already added their own bonuses to the same components.
	if (CombatTarget && !FMath::IsNearlyEqual(NewAttack, AppliedAttackBonus))
	{
		CombatTarget->AddAttackPercent(NewAttack - AppliedAttackBonus);
	}
	if (HealthTarget && !FMath::IsNearlyEqual(NewHealth, AppliedHealthBonus))
	{
		HealthTarget->AddMaxHealth(NewHealth - AppliedHealthBonus, 0.f);
	}

	AppliedAttackBonus = NewAttack;
	AppliedHealthBonus = NewHealth;
}
