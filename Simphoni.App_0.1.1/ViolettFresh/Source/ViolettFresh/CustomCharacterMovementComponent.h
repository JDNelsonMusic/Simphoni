// CustomCharacterMovementComponent.h

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "CustomCharacterMovementComponent.generated.h"

/**
 * Custom movement component to handle custom gravity.
 */
UCLASS()
class VIOLETTFRESH_API UCustomCharacterMovementComponent : public UCharacterMovementComponent
{
    GENERATED_BODY()

public:
    /** Constructor */
    UCustomCharacterMovementComponent();

    /** Override to apply custom gravity */
    virtual void PhysCustom(float deltaTime, int32 Iterations) override;

    /** Function to set the current gravity direction */
    void SetGravityDirection(const FVector& NewGravityDirection);

protected:
    /** Current gravity direction */
    FVector GravityDirection;
};