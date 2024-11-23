// QuinnCharacter.cpp

#include "QuinnCharacter.h"
#include "CustomCharacterMovementComponent.h"
#include "ViolettPlanet.h"
#include "Kismet/GameplayStatics.h"
#include "EnhancedInputComponent.h" // Ensure this path is correct

AQuinnCharacter::AQuinnCharacter(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer.SetDefaultSubobjectClass<UCustomCharacterMovementComponent>(ACharacter::CharacterMovementComponentName))
{
    // Any additional initialization if necessary
}

void AQuinnCharacter::BeginPlay()
{
    Super::BeginPlay();

    // Find the gravity source in the level
    TArray<AActor*> FoundActors;
    UGameplayStatics::GetAllActorsOfClass(GetWorld(), AViolettPlanet::StaticClass(), FoundActors);

    if (FoundActors.Num() > 0)
    {
        GravitySource = Cast<AViolettPlanet>(FoundActors[0]);
    }
}

void AQuinnCharacter::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    UpdateGravity();
}

void AQuinnCharacter::PostInitializeComponents()
{
    Super::PostInitializeComponents();

    // No need to set movement component here as it's handled by the ObjectInitializer
}

void AQuinnCharacter::UpdateGravity()
{
    if (GravitySource)
    {
        FVector GravityDirection = GravitySource->GetActorLocation() - GetActorLocation();
        GravityDirection.Normalize();

        // Apply custom gravity
        ApplyCustomGravity(GravityDirection, GravitySource->GravityStrength);
    }
}

void AQuinnCharacter::ApplyCustomGravity(const FVector& GravityDirection, float GravityStrength)
{
    UCustomCharacterMovementComponent* CustomMovement = Cast<UCustomCharacterMovementComponent>(GetCharacterMovement());
    if (CustomMovement)
    {
        CustomMovement->SetGravityDirection(GravityDirection);
        CustomMovement->GravityScale = FMath::Abs(GravityStrength / GetWorld()->GetGravityZ());
    }
}
