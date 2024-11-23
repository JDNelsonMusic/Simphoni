// IGravityObject.h

#pragma once

#include "CoreMinimal.h"
#include "UObject/Interface.h"
#include "IGravityObject.generated.h"

// This class does not need to be modified.
UINTERFACE(MinimalAPI)
class UGravityObject : public UInterface
{
    GENERATED_BODY()
};

/**
 * Interface for actors affected by custom gravity.
 */
class VIOLETTFRESH_API IGravityObject
{
    GENERATED_BODY()

public:
    /** Apply custom gravity to the implementing actor */
    virtual void ApplyCustomGravity(const FVector& GravityDirection, float GravityStrength) = 0;
};