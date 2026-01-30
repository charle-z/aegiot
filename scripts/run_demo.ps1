$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

$venvPython = Join-Path $repoRoot ".venv\\Scripts\\python.exe"
if (Test-Path $venvPython) {
    $python = $venvPython
} else {
    $python = "python"
}

Write-Host "== run demo report =="
& $python -m aegiot --input sample_devices.csv --output report_demo.md

Write-Host "== summary =="
@'
from collections import Counter
from aegiot.parsing import load_devices
from aegiot.scoring import compute_score

devices = load_devices("sample_devices.csv")
for d in devices:
    compute_score(d)

counts = Counter(d.risk_level for d in devices)
print("Summary")
print("LOW: {0} | MEDIUM: {1} | HIGH: {2} | CRITICAL: {3}".format(
    counts.get("LOW", 0),
    counts.get("MEDIUM", 0),
    counts.get("HIGH", 0),
    counts.get("CRITICAL", 0),
))
print("")
print("Top 5 by score:")
for d in sorted(devices, key=lambda x: x.score, reverse=True)[:5]:
    print("- {0} - {1} {2} - {3} ({4})".format(
        d.device_id, d.vendor, d.model, d.score, d.risk_level
    ))
'@ | & $python -
