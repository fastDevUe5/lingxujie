#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "LXJMonsterBrain.h"

namespace
{
	using LXJMonsterBrain::EState;
	using LXJMonsterBrain::FInput;

	/** Baseline: a monster sitting at home with nothing to do. */
	FInput MakeInput()
	{
		FInput In;
		In.bHasTarget = false;
		In.bAggro = false;
		In.DistanceToTarget = 0.f;
		In.DistanceFromHome = 0.f;
		In.AggroRadius = 1200.f;
		In.AttackRange = 200.f;
		In.LeashRadius = 2400.f;
		In.bAttackReady = false;
		return In;
	}
}

// Patrol only happens at home: wandering back is the Return state's job.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FLXJMonsterBrainPatrolTest, "LingXuJie.MonsterBrain.PatrolAndReturn",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FLXJMonsterBrainPatrolTest::RunTest(const FString& Parameters)
{
	FInput In = MakeInput();
	TestEqual(TEXT("idle at home patrols"), LXJMonsterBrain::NextState(EState::Patrol, In), EState::Patrol);

	// Patrolling may wander away from home without triggering a walk-back (bug found in game:
	// otherwise the monster yo-yos Patrol <-> Return every frame at the edge of the patrol radius).
	In.DistanceFromHome = 900.f;
	TestEqual(TEXT("a wandering patrol keeps patrolling"), LXJMonsterBrain::NextState(EState::Patrol, In), EState::Patrol);

	// Losing a target is what sends it home.
	In.DistanceFromHome = 900.f;
	TestEqual(TEXT("chase without a target walks home"), LXJMonsterBrain::NextState(EState::Chase, In), EState::Return);
	TestEqual(TEXT("attack without a target walks home"), LXJMonsterBrain::NextState(EState::Attack, In), EState::Return);

	// Return reaches home and hands back to patrol.
	In.DistanceFromHome = 900.f;
	TestEqual(TEXT("still far from home keeps returning"), LXJMonsterBrain::NextState(EState::Return, In), EState::Return);

	In.DistanceFromHome = 100.f;
	TestEqual(TEXT("back home switches to patrol"), LXJMonsterBrain::NextState(EState::Return, In), EState::Patrol);

	// Regression: a monster walking home must not turn around just because the player stands
	// nearby (that ping-pongs "aggro / drops aggro" every frame at the leash edge).
	FInput NearPlayerWhileReturning = MakeInput();
	NearPlayerWhileReturning.bHasTarget = true;
	NearPlayerWhileReturning.DistanceToTarget = 300.f;
	NearPlayerWhileReturning.DistanceFromHome = 2000.f;
	NearPlayerWhileReturning.bAttackReady = true;
	TestEqual(TEXT("returning ignores a nearby player"),
		LXJMonsterBrain::NextState(EState::Return, NearPlayerWhileReturning), EState::Return);

	// ...unless it gets hit, which sets aggro and pulls it back into the fight.
	NearPlayerWhileReturning.bAggro = true;
	TestEqual(TEXT("being hit pulls it back"), LXJMonsterBrain::NextState(EState::Return, NearPlayerWhileReturning), EState::Chase);

	return true;
}

// Aggro: spotted inside the radius, sticky afterwards, and attacking only when in range and ready.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FLXJMonsterBrainAggroTest, "LingXuJie.MonsterBrain.AggroAndAttack",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FLXJMonsterBrainAggroTest::RunTest(const FString& Parameters)
{
	FInput In = MakeInput();
	In.bHasTarget = true;

	In.DistanceToTarget = 1500.f;
	TestEqual(TEXT("target outside aggro radius is ignored"), LXJMonsterBrain::NextState(EState::Patrol, In), EState::Patrol);

	In.DistanceToTarget = 900.f;
	TestEqual(TEXT("target inside aggro radius starts a chase"), LXJMonsterBrain::NextState(EState::Patrol, In), EState::Chase);

	// Aggro keeps the chase going past the perception radius.
	In.bAggro = true;
	In.DistanceToTarget = 1100.f;
	TestEqual(TEXT("already aggroed keeps chasing"), LXJMonsterBrain::NextState(EState::Chase, In), EState::Chase);

	In.DistanceToTarget = 150.f;
	In.bAttackReady = true;
	TestEqual(TEXT("in range and ready attacks"), LXJMonsterBrain::NextState(EState::Chase, In), EState::Attack);

	In.bAttackReady = false;
	TestEqual(TEXT("in range on cooldown keeps chasing"), LXJMonsterBrain::NextState(EState::Attack, In), EState::Chase);

	// Melee range boundary: 201 units means "not in range" for a 200 range monster.
	In.bAttackReady = true;
	In.DistanceToTarget = 201.f;
	TestEqual(TEXT("just outside range does not attack"), LXJMonsterBrain::NextState(EState::Chase, In), EState::Chase);

	return true;
}

// The leash beats everything: no target, however close, can hold a monster too far from home.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FLXJMonsterBrainLeashTest, "LingXuJie.MonsterBrain.Leash",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FLXJMonsterBrainLeashTest::RunTest(const FString& Parameters)
{
	FInput In = MakeInput();
	In.bHasTarget = true;
	In.bAggro = true;
	In.DistanceToTarget = 50.f;
	In.bAttackReady = true;
	In.DistanceFromHome = 2500.f;

	TestEqual(TEXT("dragged past the leash goes home"), LXJMonsterBrain::NextState(EState::Attack, In), EState::Return);
	TestTrue(TEXT("and drops aggro"), LXJMonsterBrain::ShouldDropAggro(In));

	// Inside the leash the same target is still worth fighting.
	In.DistanceFromHome = 2000.f;
	TestEqual(TEXT("inside the leash still attacks"), LXJMonsterBrain::NextState(EState::Return, In), EState::Attack);
	TestFalse(TEXT("and keeps aggro"), LXJMonsterBrain::ShouldDropAggro(In));

	// Losing the target (player death / despawn) also drops aggro.
	FInput NoTarget = MakeInput();
	NoTarget.DistanceFromHome = 300.f;
	TestTrue(TEXT("a missing target drops aggro"), LXJMonsterBrain::ShouldDropAggro(NoTarget));
	TestEqual(TEXT("and the monster walks home"), LXJMonsterBrain::NextState(EState::Chase, NoTarget), EState::Return);

	return true;
}

#endif // WITH_DEV_AUTOMATION_TESTS
