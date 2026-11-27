// Training dummy: a static target that takes damage, shows hit feedback and respawns.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LXJTrainingDummy.generated.h"

class ULXJHealthComponent;
class UStaticMeshComponent;

UCLASS()
class LINGXUJIE_API ALXJTrainingDummy : public AActor
{
	GENERATED_BODY()

public:
	ALXJTrainingDummy();

	virtual void Tick(float DeltaSeconds) override;

protected:
	virtual void BeginPlay() override;

private:
	void HandleDeath(AActor* DeadActor, AActor* Killer);
	void Respawn();

	UPROPERTY(VisibleAnywhere, Category = "LingXuJie")
	TObjectPtr<UStaticMeshComponent> Mesh;

	UPROPERTY(VisibleAnywhere, Category = "LingXuJie")
	TObjectPtr<ULXJHealthComponent> Health;

	/** Experience handed to whoever lands the killing blow. Generous on purpose: a dummy is
	 *  the P0 sandbox's "level up once" button, real monsters (M0.3 step 2) will give 45-60. */
	UPROPERTY(EditAnywhere, Category = "LingXuJie")
	float ExperienceReward = 100.f;

	float HitFlash = 0.f;
	FTimerHandle RespawnTimer;
};
