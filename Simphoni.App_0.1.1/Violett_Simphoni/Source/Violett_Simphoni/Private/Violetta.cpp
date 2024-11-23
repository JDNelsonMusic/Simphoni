#include "Violetta.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/KismetMathLibrary.h"
#include "DrawDebugHelpers.h"

AVioletta::AVioletta()
{
    PrimaryActorTick.bCanEverTick = true;

    GetCharacterMovement()->GravityScale = 0.0f; // Disable default gravity
    GetCharacterMovement()->SetWalkableFloorAngle(180.0f); // Allow walking on any surface angle
}

void AVioletta::BeginPlay()
{
    Super::BeginPlay();
}

void AVioletta::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (GravitySource)
    {
        // Calculate gravity direction
        FVector GravityDirection = (GravitySource->GetActorLocation() - GetActorLocation()).GetSafeNormal();

        // Apply gravity force
        FVector GravityForce = GravityDirection * 980.0f; // Custom gravity strength
        GetCharacterMovement()->AddForce(GravityForce);

        // Align character rotation with the sphere surface
        FRotator DesiredRotation = UKismetMathLibrary::MakeRotFromZX(-GravityDirection, GetActorForwardVector());
        SetActorRotation(DesiredRotation);

        // Debug gravity direction
        DrawDebugLine(GetWorld(), GetActorLocation(), GravitySource->GetActorLocation(), FColor::Green, false, -1, 0, 2.0f);
    }
}