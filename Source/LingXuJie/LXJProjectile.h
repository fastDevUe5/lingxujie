// Simple qi bolt used by the ranged monster (閭慨): straight-line, damage on impact.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LXJProjectile.generated.h"

class UProjectileMovementComponent;
class USphereComponent;
class UStaticMeshComponent;

UCLASS()
class LINGXUJIE_API ALXJProjectile : public AActor
{
	GENERATED_BODY()

public:
	ALXJProjectile();

	/** Who fired it (for kill attribution), which way it flies and how hard it hits. */
	void InitProjectile(AActor* InSourceActor, const FVector& Direction, float InDamage);

protected:
	virtual void BeginPlay() override;

	UFUNCTION()
	void HandleHit(UPrimitiveComponent* HitComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp,
		FVector NormalImpulse, const FHitResult& Hit);

	UPROPERTY(VisibleAnywhere, Category = "LingXuJie|Projectile")
	TObjectPtr<USphereComponent> Collision;

	UPROPERTY(VisibleAnywhere, Category = "LingXuJie|Projectile")
	TObjectPtr<UStaticMeshComponent> Mesh;

	UPROPERTY(VisibleAnywhere, Category = "LingXuJie|Projectile")
	TObjectPtr<UProjectileMovementComponent> Movement;

	UPROPERTY(EditAnywhere, Category = "LingXuJie|Projectile")
	float Speed = 1900.f;

	UPROPERTY(EditAnywhere, Category = "LingXuJie|Projectile")
	float LifeSeconds = 4.f;

private:
	UPROPERTY()
	TObjectPtr<AActor> SourceActor;

	float Damage = 20.f;
	bool bConsumed = false;
};
