// LingXuJie - cultivation (xiuxian) 3D MMO prototype.
// Phase 0 is a single-player vertical slice; module is kept engine-light on purpose.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "LXJGameMode.generated.h"

/**
 * Sandbox game mode: lets us fly around a generated level and validate the build/cook/run loop
 * before any gameplay systems exist.
 */
UCLASS()
class LINGXUJIE_API ALXJGameMode : public AGameModeBase
{
	GENERATED_BODY()

public:
	ALXJGameMode();
};
