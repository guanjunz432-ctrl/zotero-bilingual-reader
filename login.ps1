param([switch]$Status, [switch]$Logout)
$ErrorActionPreference = 'Stop'
$taskPython = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
$taskArgs = @((Join-Path $PSScriptRoot 'scripts/account.py'))
if ($Status) { $taskArgs += '--status' }
if ($Logout) { $taskArgs += '--logout' }
& $taskPython @taskArgs
exit $LASTEXITCODE
