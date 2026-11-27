using UnrealBuildTool;

public class LingXuJie : ModuleRules
{
	public LingXuJie(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		// Sources live flat in the module root (no Public/Private split) so files under
		// Private/Tests can include headers by bare name, like CoinRush does.
		PublicIncludePaths.Add(ModuleDirectory);

		PublicDependencyModuleNames.AddRange(new string[]
		{
			"Core",
			"CoreUObject",
			"Engine",
			"InputCore",
			// LXJGround rebuilds the terrain section at load time instead of baking it into the
			// level, because procedural mesh sections are not serialised.
			"ProceduralMeshComponent"
		});

		// Server-authoritative features (replication, online subsystems) get added here when
		// the prototype moves to its networking phase.
	}
}
