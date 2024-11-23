#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "Violett_Simphoni_MVPCharacter.generated.h"

UCLASS(config=Game)
class AViolett_Simphoni_MVPCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AViolett_Simphoni_MVPCharacter();

    // Input mapping context
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
    class UInputMappingContext* DefaultMappingContext;

    // Input actions
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
    class UInputAction* MoveAction;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
    class UInputAction* LookAction;

protected:
    virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;

    // Movement and looking functions
    void Move(const FInputActionValue& Value);
    void Look(const FInputActionValue& Value);
};
