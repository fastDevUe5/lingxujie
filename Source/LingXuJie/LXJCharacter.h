// LingXuJie player character: third-person over-shoulder camera, sprint, air glide and a dash.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "LXJCharacter.generated.h"

class UCameraComponent;
class USpringArmComponent;
class UStaticMeshComponent;
class ULXJCombatComponent;
class ULXJHealthComponent;
class ULXJProgressComponent;
class ULXJInventoryComponent;

UCLASS()
class LINGXUJIE_API ALXJCharacter : public ACharacter
{
	GENERATED_BODY()

public:
	ALXJCharacter();

	virtual void Tick(float DeltaSeconds) override;

	/** True while Shift is held and the character is moving (exposed for HUD/UI later). */
	UFUNCTION(BlueprintPure, Category = "LingXuJie")
	bool IsSprinting() const { return bSprinting; }

	/** True during the dash window (used later for i-frames). */
	UFUNCTION(BlueprintPure, Category = "LingXuJie")
	bool IsDashing() const { return DashTimeLeft > 0.f; }

	/** True while gliding (holding jump in the air). */
	UFUNCTION(BlueprintPure, Category = "LingXuJie")
	bool IsGliding() const { return bGliding; }

	ULXJCombatComponent* GetCombatComponent() const { return Combat; }

	ULXJHealthComponent* GetHealthComponent() const { return Health; }

	ULXJProgressComponent* GetProgressComponent() const { return Progress; }

	ULXJInventoryComponent* GetInventoryComponent() const { return Inventory; }

protected:
	virtual void BeginPlay() override;
	virtual void Landed(const FHitResult& Hit) override;

private:
	void UpdateLook(float DeltaSeconds);
	void UpdateMove(float DeltaSeconds);
	void UpdateJumpAndGlide(float DeltaSeconds);
	void UpdateDash(float DeltaSeconds);
	void UpdateLandShake(float DeltaSeconds);
	void ReadDebugShortcuts();
	void UpdateCombatInput();
	void HandleDeath(AActor* DeadActor, AActor* Killer);

	UPROPERTY(VisibleAnywhere, Category = "LingXuJie")
	TObjectPtr<USpringArmComponent> CameraBoom;

	UPROPERTY(VisibleAnywhere, Category = "LingXuJie")
	TObjectPtr<UCameraComponent> FollowCamera;

	UPROPERTY(VisibleAnywhere, Category = "LingXuJie")
	TObjectPtr<UStaticMeshComponent> BodyMesh;

	UPROPERTY(VisibleAnywhere, Category = "LingXuJie")
	TObjectPtr<UStaticMeshComponent> HeadMesh;

	UPROPERTY(VisibleAnywhere, Category = "LingXuJie")
	TObjectPtr<UStaticMeshComponent> SwordMesh;

	UPROPERTY(VisibleAnywhere, Category = "LingXuJie")
	TObjectPtr<ULXJCombatComponent> Combat;

	UPROPERTY(VisibleAnywhere, Category = "LingXuJie")
	TObjectPtr<ULXJHealthComponent> Health;

	UPROPERTY(VisibleAnywhere, Category = "LingXuJie")
	TObjectPtr<ULXJProgressComponent> Progress;

	UPROPERTY(VisibleAnywhere, Category = "LingXuJie")
	TObjectPtr<ULXJInventoryComponent> Inventory;

	UPROPERTY(EditAnywhere, Category = "LingXuJie|Movement")
	float WalkSpeed = 520.f;

	UPROPERTY(EditAnywhere, Category = "LingXuJie|Movement")
	float SprintSpeed = 880.f;

	UPROPERTY(EditAnywhere, Category = "LingXuJie|Movement")
	float DashSpeed = 1850.f;

	UPROPERTY(EditAnywhere, Category = "LingXuJie|Movement")
	float DashDuration = 0.18f;

	UPROPERTY(EditAnywhere, Category = "LingXuJie|Movement")
	float DashCooldown = 0.75f;

	UPROPERTY(EditAnywhere, Category = "LingXuJie|Glide")
	float GlideGravityScale = 0.22f;

	UPROPERTY(EditAnywhere, Category = "LingXuJie|Glide")
	float GlideFallSpeedCap = 240.f;

	UPROPERTY(EditAnywhere, Category = "LingXuJie|Glide")
	float GlideForwardPush = 520.f;

	UPROPERTY(EditAnywhere, Category = "LingXuJie|Camera")
	float CameraYawRate = 110.f;

	UPROPERTY(EditAnywhere, Category = "LingXuJie|Camera")
	float CameraPitchRate = 75.f;

	UPROPERTY(EditAnywhere, Category = "LingXuJie|Camera")
	float MouseSensitivity = 0.6f;

	UPROPERTY(EditAnywhere, Category = "LingXuJie|Camera")
	float DefaultFieldOfView = 90.f;

	UPROPERTY(EditAnywhere, Category = "LingXuJie|Camera")
	float SprintFieldOfView = 100.f;

	float CameraYaw = 0.f;
	float CameraPitch = -14.f;
	float LandShakeTime = 0.f;
	float LandShakeDuration = 0.2f;
	float DashTimeLeft = 0.f;
	float DashCooldownLeft = 0.f;
	bool bSprinting = false;
	bool bGliding = false;
	bool bJumpKeyHeld = false;
	bool bDashKeyHeld = false;
	bool bGravityWasGlide = false;
	bool bSkillKeysHeld[3] = { false, false, false };
	FVector SpawnLocation = FVector::ZeroVector;
};
