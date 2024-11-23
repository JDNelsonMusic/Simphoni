#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "Camera/CameraComponent.h"               // Include for UCameraComponent
#include "GameFramework/SpringArmComponent.h"     // Include for USpringArmComponent
#include "CustomGravityCharacter.generated.h"

/**
 * A character class with custom gravity functionality.
 * Allows for movement and orientation relative to a specified gravity source actor.
 */
UCLASS(Blueprintable)
class VIOLETT_SIMPHONI_MVP_API ACustomGravityCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    // Constructor
    ACustomGravityCharacter();

    // Called every frame
    virtual void Tick(float DeltaTime) override;

    /** Custom gravity strength, configurable in the editor */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Custom Gravity")
    float CustomGravityStrength;

    /** Reference to the actor serving as the gravity source */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Custom Gravity")
    AActor* GravitySourceActor;

protected:
    // Called when the game starts or when spawned
    virtual void BeginPlay() override;

    // Binds input actions
    virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;

private:
    /** Handles forward/backward movement */
    void MoveForward(float Value);

    /** Handles right/left movement */
    void MoveRight(float Value);

    /** Spring arm component for the camera */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Camera", meta = (AllowPrivateAccess = "true"))
    USpringArmComponent* CameraBoom;

    /** Follow camera component */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Camera", meta = (AllowPrivateAccess = "true"))
    UCameraComponent* FollowCamera;
};
