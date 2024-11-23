// ViolettPlanet.h

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "IGravityObject.h"
#include "ViolettPlanet.generated.h"

UCLASS()
class VIOLETTFRESH_API AViolettPlanet : public AActor
{
    GENERATED_BODY()

public:
    /** Constructor */
    AViolettPlanet();

protected:
    /** Called when the game starts or when spawned */
    virtual void BeginPlay() override;

public:
    /** Called every frame */
    virtual void Tick(float DeltaTime) override;

    /** Gravity strength variable */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gravity")
    float GravityStrength;

    /** Sphere component to represent the planet's gravity field */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    class USphereComponent* GravitySphere;

    /** Static mesh for visual representation */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    class UStaticMeshComponent* PlanetMesh;

    /** Applies gravity to actors implementing IGravityObject */
    void ApplyGravity();
};