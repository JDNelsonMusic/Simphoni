// Copyright Epic Games, Inc. All Rights Reserved.

#include "ViolettFreshGameMode.h"
#include "ViolettFreshCharacter.h"
#include "UObject/ConstructorHelpers.h"

AViolettFreshGameMode::AViolettFreshGameMode()
{
	// set default pawn class to our Blueprinted character
	static ConstructorHelpers::FClassFinder<APawn> PlayerPawnBPClass(TEXT("/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter"));
	if (PlayerPawnBPClass.Class != NULL)
	{
		DefaultPawnClass = PlayerPawnBPClass.Class;
	}
}
