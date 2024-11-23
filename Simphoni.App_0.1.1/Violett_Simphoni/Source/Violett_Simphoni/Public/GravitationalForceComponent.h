#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "GravitationalForceComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class SIMPHONI_API UGravitationalForceComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    // Constructor
    UGravitationalForceComponent();

    // Method to set gravitational center
    void SetGravitationalCenter(AActor* Center);

protected:
    // Called when the game starts
    virtual void BeginPlay() override;

private:
    AActor* GravitationalCenter; // Reference to the gravitational center
};