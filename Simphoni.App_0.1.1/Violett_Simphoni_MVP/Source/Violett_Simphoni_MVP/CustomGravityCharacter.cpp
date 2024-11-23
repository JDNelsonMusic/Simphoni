#include "CustomGravityCharacter.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/KismetMathLibrary.h"
#include "Components/InputComponent.h"
#include "Engine/World.h" // For GetWorld()

// Constructor
ACustomGravityCharacter::ACustomGravityCharacter()
{
    // Set default gravity strength
    CustomGravityStrength = 980.0f; // Earth's gravity in cm/s^2

    // Enable ticking every frame
    PrimaryActorTick.bCanEverTick = true;

    // Disable default character rotation
    bUseControllerRotationPitch = false;
    bUseControllerRotationYaw = false;
    bUseControllerRotationRoll = false;

    // Configure character movement
    if (UCharacterMovementComponent* MovementComponent = GetCharacterMovement())
    {
        MovementComponent->bOrientRotationToMovement = true; // Move in input direction
        MovementComponent->RotationRate = FRotator(0.0f, 540.0f, 0.0f); // Rotation speed
        MovementComponent->GravityScale = 0.0f; // Disable default gravity
    }

    // Create camera boom
    CameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));
    if (CameraBoom)
    {
        CameraBoom->SetupAttachment(RootComponent);
        CameraBoom->TargetArmLength = 400.0f; // Camera distance
        CameraBoom->bUsePawnControlRotation = true; // Rotate based on controller
    }

    // Create follow camera
    FollowCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera"));
    if (FollowCamera)
    {
        FollowCamera->SetupAttachment(CameraBoom, USpringArmComponent::SocketName);
        FollowCamera->bUsePawnControlRotation = false; // No relative rotation
    }
}

// Called when the game starts
void ACustomGravityCharacter::BeginPlay()
{
    Super::BeginPlay();

    if (!GravitySourceActor)
    {
        UE_LOG(LogTemp, Warning, TEXT("GravitySourceActor is not assigned for %s"), *GetActorNameOrLabel());
    }
}

// Called every frame
void ACustomGravityCharacter::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (GravitySourceActor)
    {
        // Calculate gravity direction
        FVector GravityDirection = (GravitySourceActor->GetActorLocation() - GetActorLocation()).GetSafeNormal();

        // Apply gravity force
        FVector GravityForce = GravityDirection * CustomGravityStrength;
        if (UCharacterMovementComponent* MovementComponent = GetCharacterMovement())
        {
            MovementComponent->AddForce(GravityForce);
        }

        // Align character with gravity source
        FRotator DesiredRotation = UKismetMathLibrary::MakeRotFromXZ(GetActorForwardVector(), -GravityDirection);
        SetActorRotation(DesiredRotation);
    }
}

// Binds input actions
void ACustomGravityCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);

    if (PlayerInputComponent)
    {
        PlayerInputComponent->BindAxis("MoveForward", this, &ACustomGravityCharacter::MoveForward);
        PlayerInputComponent->BindAxis("MoveRight", this, &ACustomGravityCharacter::MoveRight);

        PlayerInputComponent->BindAxis("Turn", this, &ACustomGravityCharacter::AddControllerYawInput);
        PlayerInputComponent->BindAxis("LookUp", this, &ACustomGravityCharacter::AddControllerPitchInput);
    }
}

// Move forward/backward
void ACustomGravityCharacter::MoveForward(float Value)
{
    if (Controller && Value != 0.0f)
    {
        AddMovementInput(GetActorForwardVector(), Value);
    }
}

// Move right/left
void ACustomGravityCharacter::MoveRight(float Value)
{
    if (Controller && Value != 0.0f)
    {
        AddMovementInput(GetActorRightVector(), Value);
    }
}
