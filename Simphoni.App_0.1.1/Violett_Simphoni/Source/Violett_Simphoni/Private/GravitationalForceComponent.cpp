#include "GravitationalForceComponent.h"
#include "GameFramework/Actor.h"

UGravitationalForceComponent::UGravitationalForceComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
    GravitationalCenter = nullptr;
}

void UGravitationalForceComponent::BeginPlay()
{
    Super::BeginPlay();
    // Initialization logic here
}

void UGravitationalForceComponent::SetGravitationalCenter(AActor* Center)
{
    GravitationalCenter = Center;
}