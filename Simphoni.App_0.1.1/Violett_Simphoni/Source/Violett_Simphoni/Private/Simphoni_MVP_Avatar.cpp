// Fill out your copyright notice in the Description page of Project Settings.


#include "Simphoni_MVP_Avatar.h"

// Sets default values
ASimphoni_MVP_Avatar::ASimphoni_MVP_Avatar()
{
 	// Set this character to call Tick() every frame.  You can turn this off to improve performance if you don't need it.
	PrimaryActorTick.bCanEverTick = true;

}

// Called when the game starts or when spawned
void ASimphoni_MVP_Avatar::BeginPlay()
{
	Super::BeginPlay();
	
}

// Called every frame
void ASimphoni_MVP_Avatar::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

}

// Called to bind functionality to input
void ASimphoni_MVP_Avatar::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);

}

