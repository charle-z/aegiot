$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

Write-Host "== git status =="
git status

Write-Host "== git log -5 --oneline =="
git log -5 --oneline

Write-Host "== python --version =="
python --version 2>&1

Write-Host "== run cli =="
python -m aegiot --input sample_devices.csv --output report_check.md

Write-Host "== pytest -q =="
pytest -q
