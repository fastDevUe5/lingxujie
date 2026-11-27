#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "LXJCombatComponent.h"
#include "LXJHealthComponent.h"
#include "LXJInventoryComponent.h"
#include "LXJItems.h"

namespace
{
	const TCHAR* SwordId = TEXT("iron_sword");
	const TCHAR* BetterSwordId = TEXT("spirit_blade");
	const TCHAR* ArmorId = TEXT("jade_armor");
}

// The catalog is the single source of truth for ids, names and equipment stats.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FLXJItemCatalogTest, "LingXuJie.Items.Catalog",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FLXJItemCatalogTest::RunTest(const FString& Parameters)
{
	TestTrue(TEXT("catalog is not empty"), LXJItems::All().Num() > 0);

	TSet<FName> SeenIds;
	for (const FLXJItemDef& Item : LXJItems::All())
	{
		TestFalse(TEXT("item id is set"), Item.Id.IsNone());
		TestFalse(TEXT("item name is set"), Item.DisplayName.IsEmpty());
		if (!TestFalse(FString::Printf(TEXT("item id '%s' is unique"), *Item.Id.ToString()), SeenIds.Contains(Item.Id)))
		{
			continue;
		}
		SeenIds.Add(Item.Id);
	}

	const FLXJItemDef* Stone = LXJItems::Find(LXJItems::SpiritStoneId());
	TestNotNull(TEXT("spirit stone exists"), Stone);
	if (Stone)
	{
		TestEqual(TEXT("spirit stone is a material"), Stone->Type, ELXJItemType::Material);
		TestFalse(TEXT("spirit stone is not equipment"), LXJItems::IsEquipment(Stone->Id));
	}

	const FLXJItemDef* Sword = LXJItems::Find(FName(SwordId));
	TestNotNull(TEXT("iron sword exists"), Sword);
	if (Sword)
	{
		TestEqual(TEXT("iron sword is a weapon"), Sword->Type, ELXJItemType::Weapon);
		TestTrue(TEXT("iron sword adds damage"), Sword->AttackPercent > 0.f);
		TestTrue(TEXT("iron sword counts as equipment"), LXJItems::IsEquipment(Sword->Id));
	}

	const FLXJItemDef* Armor = LXJItems::Find(FName(ArmorId));
	TestNotNull(TEXT("jade armor exists"), Armor);
	if (Armor)
	{
		TestEqual(TEXT("jade armor is armour"), Armor->Type, ELXJItemType::Armor);
		TestTrue(TEXT("jade armor adds health"), Armor->MaxHealth > 0.f);
	}

	TestNull(TEXT("unknown ids return null"), LXJItems::Find(FName(TEXT("no_such_item"))));

	return true;
}

// Drops: spirit stones always, equipment sometimes, casters pay better.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FLXJItemDropTableTest, "LingXuJie.Items.DropTable",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FLXJItemDropTableTest::RunTest(const FString& Parameters)
{
	FRandomStream Stream(1337);
	const FName Stone = LXJItems::SpiritStoneId();

	int32 RollsWithEquipment = 0;
	int32 MinMeleeStones = MAX_int32;
	int32 MinCasterStones = MAX_int32;

	for (int32 Roll = 0; Roll < 200; ++Roll)
	{
		const bool bCaster = (Roll % 2) == 0;
		const TArray<FLXJDrop> Drops = LXJItems::RollDrops(bCaster, Stream);

		if (!TestTrue(TEXT("every roll has drops"), Drops.Num() > 0))
		{
			return false;
		}

		bool bHasStones = false;
		bool bHasEquipment = false;
		for (const FLXJDrop& Drop : Drops)
		{
			TestNotNull(FString::Printf(TEXT("drop id '%s' is in the catalog"), *Drop.ItemId.ToString()), LXJItems::Find(Drop.ItemId));
			TestTrue(TEXT("drop count is positive"), Drop.Count > 0);

			if (Drop.ItemId == Stone)
			{
				bHasStones = true;
				if (bCaster)
				{
					MinCasterStones = FMath::Min(MinCasterStones, Drop.Count);
				}
				else
				{
					MinMeleeStones = FMath::Min(MinMeleeStones, Drop.Count);
				}
			}
			else if (LXJItems::IsEquipment(Drop.ItemId))
			{
				bHasEquipment = true;
			}
		}

		if (!TestTrue(TEXT("spirit stones are guaranteed"), bHasStones))
		{
			return false;
		}
		if (bHasEquipment)
		{
			++RollsWithEquipment;
		}
	}

	// The table must not be all-or-nothing: over 200 rolls equipment shows up, but not always.
	TestTrue(TEXT("equipment drops sometimes"), RollsWithEquipment > 0);
	TestTrue(TEXT("equipment is not guaranteed"), RollsWithEquipment < 200);
	TestTrue(TEXT("casters carry at least 6 stones"), MinCasterStones >= 6);
	TestTrue(TEXT("melee carries at least 4 stones"), MinMeleeStones >= 4);

	return true;
}

// Bag: stacking into one line, spilling into the next, and refusing when full.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FLXJInventoryStackingTest, "LingXuJie.Inventory.Stacking",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FLXJInventoryStackingTest::RunTest(const FString& Parameters)
{
	const FName Stone = LXJItems::SpiritStoneId();
	ULXJInventoryComponent* Bag = NewObject<ULXJInventoryComponent>(GetTransientPackage());

	TestEqual(TEXT("starts empty"), Bag->GetUsedSlots(), 0);

	TestTrue(TEXT("adding works"), Bag->AddItem(Stone, 5));
	TestEqual(TEXT("five in one stack"), Bag->GetItemCount(Stone), 5);
	TestEqual(TEXT("one slot used"), Bag->GetUsedSlots(), 1);
	TestEqual(TEXT("stack count readable"), Bag->GetStack(0).Count, 5);

	// Crossing the stack cap spills into a second slot instead of overflowing.
	TestTrue(TEXT("bulk add works"), Bag->AddItem(Stone, ULXJInventoryComponent::MaxStack));
	TestEqual(TEXT("total is stacked"), Bag->GetItemCount(Stone), 5 + ULXJInventoryComponent::MaxStack);
	TestEqual(TEXT("two slots used"), Bag->GetUsedSlots(), 2);

	// A second item type gets its own line.
	TestTrue(TEXT("equipment add works"), Bag->AddItem(FName(SwordId), 1));
	TestEqual(TEXT("three slots used"), Bag->GetUsedSlots(), 3);

	// Unknown ids are rejected instead of making junk entries.
	TestFalse(TEXT("unknown item rejected"), Bag->AddItem(FName(TEXT("ghost_item")), 1));

	// Fill the bag completely and check the refusal is clean.
	for (int32 Index = Bag->GetUsedSlots(); Index < ULXJInventoryComponent::MaxSlots; ++Index)
	{
		Bag->AddItem(Stone, ULXJInventoryComponent::MaxStack);
	}
	TestEqual(TEXT("bag is full"), Bag->GetUsedSlots(), ULXJInventoryComponent::MaxSlots);
	TestFalse(TEXT("full bag refuses a new item"), Bag->AddItem(FName(BetterSwordId), 1));

	return true;
}

// Equipment: wearing pushes the delta into health/combat, unwearing takes it back.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FLXJInventoryEquipTest, "LingXuJie.Inventory.Equip",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FLXJInventoryEquipTest::RunTest(const FString& Parameters)
{
	ULXJHealthComponent* Health = NewObject<ULXJHealthComponent>(GetTransientPackage());
	ULXJCombatComponent* Combat = NewObject<ULXJCombatComponent>(GetTransientPackage());
	ULXJInventoryComponent* Bag = NewObject<ULXJInventoryComponent>(GetTransientPackage());
	Health->MaxHealth = 300.f;
	Health->ResetHealth();
	Bag->SetStatTargets(Health, Combat);

	Bag->AddItem(FName(SwordId), 1);
	const int32 SwordSlot = 0;
	TestTrue(TEXT("equipping the sword works"), Bag->EquipFromSlot(SwordSlot));
	TestEqual(TEXT("sword is worn"), Bag->GetEquippedId(ELXJItemType::Weapon), FName(SwordId));
	TestEqual(TEXT("sword left the bag"), Bag->GetItemCount(FName(SwordId)), 0);
	TestTrue(TEXT("damage bonus applied"), Combat->GetAttackPercent() > 0.f);
	TestEqual(TEXT("health untouched by a weapon"), Health->GetMaxHealth(), 300.f);

	// Wearing armour raises the health cap and tops up by the same amount.
	Bag->AddItem(FName(ArmorId), 1);
	const int32 ArmorSlot = Bag->GetUsedSlots() - 1;
	TestTrue(TEXT("equipping the armour works"), Bag->EquipFromSlot(ArmorSlot));
	TestEqual(TEXT("armour is worn"), Bag->GetEquippedId(ELXJItemType::Armor), FName(ArmorId));
	TestEqual(TEXT("health cap grew"), Health->GetMaxHealth(), 360.f);
	TestEqual(TEXT("current health followed the cap"), Health->GetHealth(), 300.f);

	// Upgrading swaps the pieces: the old sword goes back into the bag.
	const float AttackWithSword = Combat->GetAttackPercent();
	Bag->AddItem(FName(BetterSwordId), 1);
	const int32 BetterSlot = Bag->GetUsedSlots() - 1;
	TestTrue(TEXT("upgrade works"), Bag->EquipFromSlot(BetterSlot));
	TestEqual(TEXT("better sword worn"), Bag->GetEquippedId(ELXJItemType::Weapon), FName(BetterSwordId));
	TestEqual(TEXT("old sword returned to the bag"), Bag->GetItemCount(FName(SwordId)), 1);
	TestTrue(TEXT("attack grew with the upgrade"), Combat->GetAttackPercent() > AttackWithSword);

	// Unequipping removes the bonus again (and keeps the item).
	Bag->Unequip(ELXJItemType::Armor);
	TestTrue(TEXT("armour removed"), Bag->GetEquippedId(ELXJItemType::Armor).IsNone());
	TestEqual(TEXT("health cap back to base"), Health->GetMaxHealth(), 300.f);
	TestEqual(TEXT("armour is in the bag"), Bag->GetItemCount(FName(ArmorId)), 1);

	Bag->Unequip(ELXJItemType::Weapon);
	TestEqual(TEXT("attack bonus gone"), Combat->GetAttackPercent(), 0.f);
	TestEqual(TEXT("sword is back"), Bag->GetItemCount(FName(BetterSwordId)), 1);

	return true;
}

// Auto-equip (the stand-in for a bag UI) only upgrades, never downgrades.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FLXJInventoryAutoEquipTest, "LingXuJie.Inventory.AutoEquip",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FLXJInventoryAutoEquipTest::RunTest(const FString& Parameters)
{
	ULXJHealthComponent* Health = NewObject<ULXJHealthComponent>(GetTransientPackage());
	ULXJCombatComponent* Combat = NewObject<ULXJCombatComponent>(GetTransientPackage());
	ULXJInventoryComponent* Bag = NewObject<ULXJInventoryComponent>(GetTransientPackage());
	Health->MaxHealth = 300.f;
	Health->ResetHealth();
	Bag->SetStatTargets(Health, Combat);

	Bag->AddItem(FName(SwordId), 1);
	TestTrue(TEXT("wears an empty weapon slot"), Bag->TryAutoEquip(FName(SwordId)));

	Bag->AddItem(FName(BetterSwordId), 1);
	TestTrue(TEXT("upgrades to the better sword"), Bag->TryAutoEquip(FName(BetterSwordId)));

	Bag->AddItem(FName(SwordId), 1);
	TestFalse(TEXT("refuses to downgrade"), Bag->TryAutoEquip(FName(SwordId)));
	TestEqual(TEXT("better sword still worn"), Bag->GetEquippedId(ELXJItemType::Weapon), FName(BetterSwordId));

	TestFalse(TEXT("materials are never worn"), Bag->TryAutoEquip(LXJItems::SpiritStoneId()));
	TestFalse(TEXT("unknown ids are refused"), Bag->TryAutoEquip(FName(TEXT("ghost_item"))));

	return true;
}

#endif // WITH_DEV_AUTOMATION_TESTS
