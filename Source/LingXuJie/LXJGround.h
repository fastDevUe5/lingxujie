// Procedural ground that survives a level reload.
//
// A ProceduralMeshComponent's section data is not serialised, so a plain procedural mesh saved
// into a level comes back empty - which is why the ground used to disappear whenever the editor
// was reopened or the game was launched straight from disk. This actor owns the height field
// parameters and rebuilds its own section whenever its components register, so the level stays
// small and the ground is always there: editor viewport, PIE and cooked game alike.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LXJGround.generated.h"

class UMaterialInterface;
class UProceduralMeshComponent;

UCLASS()
class LINGXUJIE_API ALXJGround : public AActor
{
	GENERATED_BODY()

public:
	ALXJGround();

	/**
	 * Rectangles the ground is flat inside, in world cm: X,Y is the min corner and Z,W the max
	 * corner. Villages, cities and roads need level ground; outside them the land rolls.
	 */
	UPROPERTY(EditAnywhere, Category = "Ground")
	TArray<FVector4> FlatAreas;

	/** Centre of the height field in world XY (cm). */
	UPROPERTY(EditAnywhere, Category = "Ground")
	FVector2D Centre = FVector2D(0.0, -500.0);

	/** Side length of the height field (cm). */
	UPROPERTY(EditAnywhere, Category = "Ground")
	float Size = 25000.0f;

	/** Grid spacing of the height field (cm). */
	UPROPERTY(EditAnywhere, Category = "Ground")
	float Step = 250.0f;

	/** Material for section 0; the level builder passes the grass surface in. */
	UPROPERTY(EditAnywhere, Category = "Ground")
	TObjectPtr<UMaterialInterface> GroundMaterial = nullptr;

	/**
	 * Rebuild the section from the parameters above. The level builder calls this once it has
	 * written them; the actor also rebuilds on construction and whenever components register.
	 */
	UFUNCTION(BlueprintCallable, Category = "Ground")
	void Rebuild();

	virtual void OnConstruction(const FTransform& Transform) override;

protected:
	virtual void PostRegisterAllComponents() override;
	virtual void BeginPlay() override;

	UPROPERTY(VisibleAnywhere, Category = "Ground")
	TObjectPtr<UProceduralMeshComponent> Mesh;

	/** Rolling ground at world XY in cm, faded to zero inside FlatAreas. */
	float HeightAt(float X, float Y) const;
};
