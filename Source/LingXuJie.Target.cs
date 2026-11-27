using UnrealBuildTool;
using System.Collections.Generic;

public class LingXuJieTarget : TargetRules
{
	public LingXuJieTarget(TargetInfo Target) : base(Target)
	{
		Type = TargetType.Game;
		DefaultBuildSettings = BuildSettingsVersion.Latest;
		IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
		ExtraModuleNames.Add("LingXuJie");
	}
}
