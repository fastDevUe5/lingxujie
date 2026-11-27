#requires -Version 5.1
# Prints native sizes of the Geonchunmun modular meshes (editor must be closed).
$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $PSScriptRoot
$UE = 'C:\Program Files\Epic Games\UE_5.8'
$Project = Join-Path $Root 'LingXuJie.uproject'
$LogDir = Join-Path $Root 'Saved\Logs'
$Cmd = Join-Path $UE 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$log = Join-Path $LogDir 'probe_pack.log'
& $Cmd "$Project" -run=pythonscript -script="$(Join-Path $Root 'Tools\probe_pack.py')" -unattended -nosplash -nop4 -stdout -FullStdOutLogOutput *>&1 | Out-File -FilePath $log -Encoding utf8
Select-String -Path $log -Pattern '\[LingXuJie\]|Exception|Error:' | ForEach-Object { $_.Line }
