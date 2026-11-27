// Item catalog + drop tables for the P0 slice.
// Kept in code (not a DataTable asset) so drops are unit-testable and the level generator
// does not have to author data.

#pragma once

#include "CoreMinimal.h"
#include "LXJItems.generated.h"

UENUM()
enum class ELXJItemType : uint8
{
	/** 灵石 and other stackable material. */
	Material,
	/** Goes into the weapon slot. */
	Weapon,
	/** Goes into the armour slot. */
	Armor,
};

/** One inventory line: an id plus how many of it. */
USTRUCT()
struct FLXJItemStack
{
	GENERATED_BODY()

	UPROPERTY()
	FName ItemId;

	UPROPERTY()
	int32 Count = 0;

	bool IsEmpty() const { return ItemId.IsNone() || Count <= 0; }
};

/** Static definition of an item (not reflected: only the stack is saved/exposed). */
struct FLXJItemDef
{
	FName Id;
	FString DisplayName;
	ELXJItemType Type = ELXJItemType::Material;
	/** Damage bonus while equipped, 0.12 == +12%. */
	float AttackPercent = 0.f;
	/** Flat max-health bonus while equipped. */
	float MaxHealth = 0.f;
	FLinearColor Color = FLinearColor::White;
};

/** One roll of a monster's drop table. */
struct FLXJDrop
{
	FName ItemId;
	int32 Count = 0;
};

namespace LXJItems
{
	/** Every item known to the game (static table). */
	const TArray<FLXJItemDef>& All();

	/** nullptr when the id is unknown. */
	const FLXJItemDef* Find(FName ItemId);

	/** 灵石, the currency-ish material every monster drops. */
	FName SpiritStoneId();

	/** True for ids that can be worn. */
	bool IsEquipment(FName ItemId);

	/**
	 * Rolls a monster's loot: spirit stones always, equipment sometimes.
	 * Pure (stream in, drops out) so the table can be tested without spawning anything.
	 */
	TArray<FLXJDrop> RollDrops(bool bRangedCaster, FRandomStream& Stream);
}
