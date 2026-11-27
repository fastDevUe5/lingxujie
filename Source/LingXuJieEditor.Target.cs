using UnrealBuildTool;
using System.Collections.Generic;

public class LingXuJieEditorTarget : TargetRules
{
	public LingXuJieEditorTarget(TargetInfo Target) : base(Target)
	{
		Type = TargetType.Editor;
		DefaultBuildSettings = BuildSettingsVersion.Latest;
		IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
		ExtraModuleNames.Add("LingXuJie");
	}
}
