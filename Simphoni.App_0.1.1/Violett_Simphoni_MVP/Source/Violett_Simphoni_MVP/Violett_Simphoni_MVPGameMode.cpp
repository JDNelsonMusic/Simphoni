// Copyright Epic Games, Inc. All Rights Reserved.

#include "Violett_Simphoni_MVPGameMode.h"
#include "Violett_Simphoni_MVPCharacter.h"
#include "UObject/ConstructorHelpers.h"

AViolett_Simphoni_MVPGameMode::AViolett_Simphoni_MVPGameMode()
{
	// set default pawn class to our Blueprinted character
	static ConstructorHelpers::FClassFinder<APawn> PlayerPawnBPClass(TEXT("/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter"));
	if (PlayerPawnBPClass.Class != NULL)
	{
		DefaultPawnClass = PlayerPawnBPClass.Class;
	}
}
