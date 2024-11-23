// CustomCharacterMovementComponent.cpp

#include "CustomCharacterMovementComponent.h"

UCustomCharacterMovementComponent::UCustomCharacterMovementComponent()
{
    // Initialize default gravity direction (downwards)
    GravityDirection = FVector(0.0f, 0.0f, -1.0f);
}

void UCustomCharacterMovementComponent::PhysCustom(float deltaTime, int32 Iterations)
{
    if (!CharacterOwner)
    {
        return;
    }

    // Apply custom gravity
    FVector Gravity = GravityDirection * GravityScale * GetGravityZ();
    Velocity += Gravity * deltaTime;

    // Call the default physics for walking
    Super::PhysWalking(deltaTime, Iterations);
}

void UCustomCharacterMovementComponent::SetGravityDirection(const FVector& NewGravityDirection)
{
    GravityDirection = NewGravityDirection;
    GravityDirection.Normalize();
}