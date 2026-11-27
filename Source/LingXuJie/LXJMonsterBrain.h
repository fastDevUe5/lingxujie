// Monster state machine, kept as a pure function so the whole brain is unit-testable
// without spawning actors, controllers or a world.

#pragma once

#include "CoreMinimal.h"

namespace LXJMonsterBrain
{
	enum class EState : uint8
	{
		/** Wandering around the spawn point. */
		Patrol,
		/** Running at the target (or kiting to preferred range). */
		Chase,
		/** Standing still and swinging/casting. */
		Attack,
		/** Walking back to the spawn point after losing aggro. */
		Return,
	};

	/** Everything the decision needs; the actor fills this in each tick. */
	struct FInput
	{
		bool bHasTarget = false;
		bool bAggro = false;
		/** Distance to the target, only meaningful when bHasTarget. */
		float DistanceToTarget = 0.f;
		float DistanceFromHome = 0.f;
		float AggroRadius = 1200.f;
		float AttackRange = 200.f;
		/** Beyond this distance from home the monster gives up and walks back. */
		float LeashRadius = 2400.f;
		bool bAttackReady = false;
		/** Distance considered "home" for the Return state. */
		float HomeTolerance = 180.f;
	};

	/** Next state for the brain. Pure: same inputs, same output. */
	inline EState NextState(EState Current, const FInput& In)
	{
		const bool bHome = In.DistanceFromHome <= In.HomeTolerance;

		// Hard leash: dragged this far from home, the monster gives up even mid-fight.
		if (In.DistanceFromHome > In.LeashRadius)
		{
			return EState::Return;
		}

		if (In.bHasTarget)
		{
			// Aggro is sticky: the monster keeps chasing until the leash or the player dies.
			// While walking home, proximity alone is not enough - it would turn around every
			// frame at the leash edge. Only an explicit aggro (e.g. being hit) can pull it back.
			const bool bEngaged = In.bAggro
				|| (Current != EState::Return && In.DistanceToTarget <= In.AggroRadius);
			if (bEngaged)
			{
				if (In.DistanceToTarget <= In.AttackRange && In.bAttackReady)
				{
					return EState::Attack;
				}
				return EState::Chase;
			}
		}

		// Nothing to fight. A patrolling monster keeps wandering (it is allowed to leave
		// home for a waypoint); one that just lost its target walks back first.
		if (Current == EState::Chase || Current == EState::Attack)
		{
			return EState::Return;
		}
		if (Current == EState::Return)
		{
			return bHome ? EState::Patrol : EState::Return;
		}
		return EState::Patrol;
	}

	/** True when the brain wants to drop aggro (leash or target gone). */
	inline bool ShouldDropAggro(const FInput& In)
	{
		return In.DistanceFromHome > In.LeashRadius || !In.bHasTarget;
	}

	inline const TCHAR* ToString(EState State)
	{
		switch (State)
		{
		case EState::Patrol: return TEXT("Patrol");
		case EState::Chase: return TEXT("Chase");
		case EState::Attack: return TEXT("Attack");
		case EState::Return: return TEXT("Return");
		default: return TEXT("?");
		}
	}
}
