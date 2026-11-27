#include "LXJGameMode.h"

#include "LXJCharacter.h"
#include "LXJHUD.h"

ALXJGameMode::ALXJGameMode()
{
	// Cultivation prototype uses the third-person player character (sprint / dash / glide).
	DefaultPawnClass = ALXJCharacter::StaticClass();
	HUDClass = ALXJHUD::StaticClass();
}
