#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "Violetta.generated.h"

UCLASS()
class SIMPHONI_API AVioletta : public ACharacter
{
    GENERATED_BODY()

public:
    AVioletta();

    virtual void Tick(float DeltaTime) override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gravity")
    AActor* GravitySource;

protected:
    virtual void BeginPlay() override;
};