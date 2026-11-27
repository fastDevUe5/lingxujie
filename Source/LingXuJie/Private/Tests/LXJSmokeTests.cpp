#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

// Smoke test: proves the LingXuJie module is compiled into the editor and the automation
// pipeline works, so tools/RunTests.ps1 has something to verify from day one.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FLXJSmokeTest, "LingXuJie.Smoke.ModuleLoaded",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FLXJSmokeTest::RunTest(const FString& Parameters)
{
	TestTrue(TEXT("module is running"), true);
	return true;
}

#endif // WITH_DEV_AUTOMATION_TESTS
