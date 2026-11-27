#requires -Version 5.1
# Runs LingXuJie automation tests (pure logic, no editor UI needed).
# Usage:  powershell -ExecutionPolicy Bypass -File Tools\RunTests.ps1
# Exit code: 0 = all passed, 1 = failures or no tests ran.
# NOTE: keep this file ASCII-only. PowerShell 5.1 reads BOM-less files as ANSI.

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$UE = 'C:\Program Files\Epic Games\UE_5.8'
$Project = Join-Path $Root 'LingXuJie.uproject'
$Cmd = Join-Path $UE 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$LogDir = Join-Path $Root 'Saved\Logs'
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Log = Join-Path $LogDir 'tests.log'
$ReportDir = Join-Path $Root 'Saved\TestReports'

& $Cmd "$Project" `
    "-ExecCmds=Automation RunTests LingXuJie" `
    "-TestExit=Automation Test Queue Empty" `
    "-ReportExportPath=$ReportDir" `
    -unattended -nosplash -nop4 -stdout -FullStdOutLogOutput *>&1 |
    Out-File -FilePath $Log -Encoding utf8

$lines = Get-Content $Log
$completed = $lines | Select-String -Pattern 'Test Completed'
$failed = $lines | Select-String -Pattern 'Result=\{Fail\}|Result=\{Error\}'

$completed | ForEach-Object { $_.Line }
"----"
"completed=$($completed.Count) failed=$($failed.Count) log=$Log"

if ($completed.Count -eq 0) {
    Write-Host "No tests ran. Check that tests compile into the Editor target and the filter name is correct." -ForegroundColor Red
    exit 1
}
if ($failed.Count -gt 0) {
    $failed | ForEach-Object { Write-Host $_.Line -ForegroundColor Red }
    exit 1
}

Write-Host "ALL TESTS PASSED" -ForegroundColor Green
exit 0
