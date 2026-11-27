#include "LXJItems.h"

namespace
{
	/** The whole P0 catalog. Add entries here; the HUD and drop tables pick them up. */
	const TArray<FLXJItemDef>& Catalog()
	{
		static const TArray<FLXJItemDef> Items = {
			{ TEXT("spirit_stone"), TEXT("LING SHI"), ELXJItemType::Material, 0.f, 0.f, FLinearColor(0.75f, 0.95f, 1.0f) },
			{ TEXT("iron_sword"), TEXT("XUAN TIE JIAN"), ELXJItemType::Weapon, 0.12f, 0.f, FLinearColor(0.70f, 0.74f, 0.82f) },
			{ TEXT("jade_armor"), TEXT("YU LING JIA"), ELXJItemType::Armor, 0.f, 60.f, FLinearColor(0.35f, 0.85f, 0.70f) },
			{ TEXT("spirit_blade"), TEXT("LING XU JIAN"), ELXJItemType::Weapon, 0.22f, 0.f, FLinearColor(0.55f, 0.80f, 1.0f) },
			{ TEXT("cloud_robe"), TEXT("LIU YUN PAO"), ELXJItemType::Armor, 0.f, 120.f, FLinearColor(0.80f, 0.72f, 1.0f) },
		};
		return Items;
	}
}

const TArray<FLXJItemDef>& LXJItems::All()
{
	return Catalog();
}

const FLXJItemDef* LXJItems::Find(FName ItemId)
{
	for (const FLXJItemDef& Item : Catalog())
	{
		if (Item.Id == ItemId)
		{
			return &Item;
		}
	}
	return nullptr;
}

FName LXJItems::SpiritStoneId()
{
	return FName(TEXT("spirit_stone"));
}

bool LXJItems::IsEquipment(FName ItemId)
{
	const FLXJItemDef* Item = Find(ItemId);
	return Item && Item->Type != ELXJItemType::Material;
}

TArray<FLXJDrop> LXJItems::RollDrops(bool bRangedCaster, FRandomStream& Stream)
{
	TArray<FLXJDrop> Drops;

	// Spirit stones are the guaranteed part: casters carry a richer purse.
	const int32 MinStones = bRangedCaster ? 6 : 4;
	const int32 MaxStones = bRangedCaster ? 12 : 8;
	Drops.Add({ SpiritStoneId(), Stream.RandRange(MinStones, MaxStones) });

	// Equipment is the interesting part; melee brutes drop the cheap set, casters the good one.
	const float EquipmentChance = bRangedCaster ? 0.35f : 0.25f;
	if (Stream.FRand() <= EquipmentChance)
	{
		const FName EquipmentId = bRangedCaster
			? FName(TEXT("spirit_blade"))
			: FName(TEXT("iron_sword"));
		Drops.Add({ EquipmentId, 1 });

		// A rarer armour drop on top of the weapon, so pickups are not all swords.
		if (Stream.FRand() <= 0.5f)
		{
			const FName ArmorId = bRangedCaster ? FName(TEXT("cloud_robe")) : FName(TEXT("jade_armor"));
			Drops.Add({ ArmorId, 1 });
		}
	}

	return Drops;
}
