// 邪修 (evil cultivator): ranged caster that keeps its distance and fires qi bolts.

#pragma once

#include "CoreMinimal.h"
#include "LXJMonster.h"
#include "LXJEvilCultivator.generated.h"

UCLASS()
class LINGXUJIE_API ALXJEvilCultivator : public ALXJMonster
{
	GENERATED_BODY()

public:
	ALXJEvilCultivator();

protected:
	virtual void PerformAttack(AActor* Target) override;

	/** Wants to fight from 800 units away (roadmap spec). */
	virtual float GetPreferredRange() const override { return PreferredRange; }

	/** Cultivators carry the richer drop table. */
	virtual bool IsRangedCaster() const override { return true; }

private:
	float PreferredRange = 800.f;
};
