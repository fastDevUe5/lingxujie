# Stop any leftover debug host and the suspended debuggee.
Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -and ($_.CommandLine -match 'live_debug' -or $_.Name -eq 'MHClient-Connect.exe')
} | ForEach-Object {
    if ($_.ProcessId -ne $PID) {
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }
}
Start-Sleep -Seconds 2
$left = Get-Process -Name MHClient-Connect -ErrorAction SilentlyContinue
if ($left) { $left | Select-Object Id, @{n='MB';e={[math]::Round($_.WorkingSet64/1MB)}} | Format-Table -AutoSize }
else { 'no client processes remain' }
