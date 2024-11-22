#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "CustomGravityCharacter.generated.h"

UCLASS()
class YOURPROJECT_API ACustomGravityCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    ACustomGravityCharacter();

    virtual void Tick(float DeltaTime) override;

    /** Custom gravity strength */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Custom Gravity")
    float CustomGravityStrength;

    /** The actor representing the gravity source (the sphere) */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Custom Gravity")
    AActor* GravitySourceActor;

protected:
    virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;

    /** Movement functions */
    void MoveForward(float Value);
    void MoveRight(float Value);
};
