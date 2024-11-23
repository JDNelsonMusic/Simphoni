// ViolettPlanet.cpp

#include "ViolettPlanet.h"
#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "IGravityObject.h"
#include "Kismet/GameplayStatics.h"

AViolettPlanet::AViolettPlanet()
{
    PrimaryActorTick.bCanEverTick = true;

    GravityStrength = -980.f; // Negative value to attract towards the center

    // Initialize the Gravity Sphere Component
    GravitySphere = CreateDefaultSubobject<USphereComponent>(TEXT("GravitySphere"));
    RootComponent = GravitySphere;
    GravitySphere->InitSphereRadius(5000.f); // Adjust as needed

    // Initialize the Planet Mesh Component
    PlanetMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PlanetMesh"));
    PlanetMesh->SetupAttachment(GravitySphere);

    // Assign a purple material in the editor or dynamically
}

void AViolettPlanet::BeginPlay()
{
    Super::BeginPlay();
}

void AViolettPlanet::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    ApplyGravity();
}

void AViolettPlanet::ApplyGravity()
{
    // Get all overlapping actors
    TArray<AActor*> OverlappingActors;
    GravitySphere->GetOverlappingActors(OverlappingActors);

    for (AActor* Actor : OverlappingActors)
    {
        if (Actor->GetClass()->ImplementsInterface(UGravityObject::StaticClass()))
        {
            IGravityObject* GravityActor = Cast<IGravityObject>(Actor);
            if (GravityActor)
            {
                FVector Direction = GetActorLocation() - Actor->GetActorLocation();
                Direction.Normalize();

                GravityActor->ApplyCustomGravity(Direction, GravityStrength);
            }
        }
    }
}