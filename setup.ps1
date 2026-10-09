param([string]$Python = 'python', [string]$Npm = 'npm.cmd')
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if ($env:OS -ne 'Windows_NT') { throw 'This preview supports Windows only.' }
$taskNode = (Get-Command node -ErrorAction Stop).Source
& $Python -c 'import sys; assert sys.version_info >= (3,11), "Python 3.11+ required"'
if ($LASTEXITCODE -ne 0) { throw 'Python 3.11+ is required.' }
& $Python -m venv .venv
if ($LASTEXITCODE -ne 0) { throw 'Could not create Python environment.' }
$taskPython = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
& $taskPython -m pip install --disable-pip-version-check -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Python dependency installation failed.' }
& $Npm ci --ignore-scripts --no-audit --no-fund
if ($LASTEXITCODE -ne 0) { throw 'Node dependency installation failed. Install Node.js LTS including npm.' }
& $taskPython scripts/configure.py --node $taskNode
if ($LASTEXITCODE -ne 0) { throw 'Backend configuration failed.' }
& $taskPython scripts/doctor.py
if ($LASTEXITCODE -ne 0) { throw 'Environment checks failed.' }
& $taskPython scripts/build.py
if ($LASTEXITCODE -ne 0) { throw 'Plugin build failed.' }
Write-Host 'Setup complete. Run .\login.ps1, then install the XPI from dist in Zotero.'
