using UnrealBuildTool;

public class Violett_Simphoni : ModuleRules
{
    public Violett_Simphoni(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[] {
            "Core",
            "CoreUObject",
            "Engine",
            "InputCore"
        });

        PrivateDependencyModuleNames.AddRange(new string[] {
            // Add your private dependencies here
        });
    }
}