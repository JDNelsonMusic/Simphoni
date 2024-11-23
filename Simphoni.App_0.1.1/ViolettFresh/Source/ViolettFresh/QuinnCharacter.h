// QuinnCharacter.h

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "IGravityObject.h"
#include "ViolettPlanet.h"
#include "QuinnCharacter.generated.h"

UCLASS()
class VIOLETTFRESH_API AQuinnCharacter : public ACharacter, public IGravityObject
{
    GENERATED_BODY()

public:
    /** Constructor */
    AQuinnCharacter(const FObjectInitializer& ObjectInitializer = FObjectInitializer::Get());

protected:
    /** Called when the game starts or when spawned */
    virtual void BeginPlay() override;

public:
    /** Called every frame */
    virtual void Tick(float DeltaTime) override;

    /** Override to use custom movement component */
    virtual void PostInitializeComponents() override;

    /** Gravity source actor */
    UPROPERTY()
    AViolettPlanet* GravitySource;

    /** Function to update gravity direction */
    void UpdateGravity();

    /** Implement ApplyCustomGravity from IGravityObject */
    virtual void ApplyCustomGravity(const FVector& GravityDirection, float GravityStrength) override;
};
