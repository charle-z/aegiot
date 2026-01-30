# C:\aegiot\init-aegiot.ps1
# AegIoT scaffold (ASCII-only content + UTF-8 no-BOM writer)
# Run:
#   powershell -ExecutionPolicy Bypass -File C:\aegiot\init-aegiot.ps1 -Force -Author "charle-z"

param(
  [string]$Root = "C:\aegiot",
  [string]$Author = "charle-z",
  [string]$Project = "AegIoT",
  [string]$Version = "0.1.0",
  [switch]$Force
)

$ErrorActionPreference = 'Stop'

function Ensure-Dir([string]$Path) {
  if (!(Test-Path -LiteralPath $Path)) { New-Item -ItemType Directory -Path $Path | Out-Null }
}

function Write-Text([string]$Path, [string]$Content) {
  if ((Test-Path -LiteralPath $Path) -and (-not $Force)) {
    Write-Host "SKIP (exists): $Path"
    return
  }
  $dir = Split-Path -Parent $Path
  Ensure-Dir $dir

  # Write UTF-8 without BOM to avoid weird characters in some Windows viewers
  $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($Path, $Content, $utf8NoBom)

  Write-Host "WRITE: $Path"
}

# 0) Structure
Ensure-Dir $Root
Ensure-Dir (Join-Path $Root "aegiot")
Ensure-Dir (Join-Path $Root "docs")
Ensure-Dir (Join-Path $Root "lab")
Ensure-Dir (Join-Path $Root "tests")
Ensure-Dir (Join-Path $Root "scripts")

# 1) .gitignore
Write-Text (Join-Path $Root ".gitignore") @"
.venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.pytest_cache/
dist/
build/
*.egg-info/
.env
report*.md
report*.html
*.log
.DS_Store
"@

# 2) README (ASCII only)
Write-Text (Join-Path $Root "README.md") @"
# $Project - IoT Firmware Risk Mapper (CLI)

$Project reads a simple inventory CSV and generates a defensive risk report (0-100) per device.

## Quickstart (Windows)
```powershell
cd $Root
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m aegiot --input sample_devices.csv --output report.md
```

## Input CSV format
Columns:
- device_id,vendor,model,firmware_version,exposed_to_internet

## Output
- report.md (Markdown): summary + device table + per-device sections + 7/30/90 plan + disclaimer.

## License
MIT (see LICENSE).

## Disclaimer
Educational and defensive only. Use fake/local data. No exploitation.
"@

# 3) LICENSE (MIT) - author is your handle
$year = (Get-Date).Year
Write-Text (Join-Path $Root "LICENSE") @"
MIT License

Copyright (c) $year $Author

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"@

# 4) NOTICE + CITATION.cff
Write-Text (Join-Path $Root "NOTICE") @"
$Project - IoT Firmware Risk Mapper
(c) $year $Author. MIT Licensed.
"@

Write-Text (Join-Path $Root "CITATION.cff") @"
cff-version: 1.2.0
title: "$Project - IoT Firmware Risk Mapper"
message: "If you use this project, please cite it."
type: software
authors:
  - name: "$Author"
version: "$Version"
date-released: "$(Get-Date -Format 'yyyy-MM-dd')"
license: MIT
"@

# 5) requirements.txt (stdlib-only)
Write-Text (Join-Path $Root "requirements.txt") @"
# stdlib-only MVP (no dependencies)
"@

# 6) sample_devices.csv
Write-Text (Join-Path $Root "sample_devices.csv") @"
device_id,vendor,model,firmware_version,exposed_to_internet
cam-001,Hikvision,DS-2CD2043G0-I,5.5.82_2021,true
cam-002,Dahua,IPC-HFW1230S,2.622.0000000.7.R_2020,true
rtr-001,TP-Link,Archer C7,v2_2019,true
rtr-002,Ubiquiti,EdgeRouter X,2.0.9-hotfix.6_2022,false
nas-001,QNAP,TS-231P,4.5.4_2021,true
nas-002,Synology,DS220+,DSM 7.2_2023,false
dvr-001,Hikvision,DS-7608NI,UNKNOWN,true
dvr-002,Dahua,NVR4108,3.210_2018,true
iot-001,Xiaomi,Mi Camera 2K,1.3.6_2022,false
iot-002,Reolink,RLC-520A,v3.0.0_2021,true
ap-001,MikroTik,hAP ac2,7.12_2024,false
oth-001,Generic,SmartPlug X1,UNKNOWN,true
"@

# 7) Python package
Write-Text (Join-Path $Root "aegiot\__init__.py") @"
__version__ = "$Version"
"@

Write-Text (Join-Path $Root "aegiot\__main__.py") @"
from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
"@

Write-Text (Join-Path $Root "aegiot\models.py") @"
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List

@dataclass
class Device:
    device_id: str
    vendor: str
    model: str
    firmware_version: str
    exposed_to_internet: bool

    device_type: str = "other"
    score: int = 0
    risk_level: str = "LOW"
    reasons: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
"@

Write-Text (Join-Path $Root "aegiot\parsing.py") @"
from __future__ import annotations
import csv
from pathlib import Path
from .models import Device

REQUIRED_COLS = ["device_id", "vendor", "model", "firmware_version", "exposed_to_internet"]

def _parse_bool(v: str) -> bool:
    s = (v or "").strip().lower()
    if s in ("1", "true", "yes", "y", "on"):
        return True
    if s in ("0", "false", "no", "n", "off"):
        return False
    if s == "":
        return False
    raise ValueError(f"Invalid boolean for exposed_to_internet: '{v}'")

def load_devices(csv_path: str) -> list[Device]:
    p = Path(csv_path)
    if not p.exists():
        raise FileNotFoundError(f"Input CSV not found: {csv_path}")

    with p.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames or []
        missing = [c for c in REQUIRED_COLS if c not in cols]
        if missing:
            raise ValueError(f"Missing required columns: {missing}. Found: {cols}")

        devices: list[Device] = []
        for i, row in enumerate(reader, start=2):
            def norm(x: str) -> str:
                return " ".join((x or "").strip().split())

            dev_id = norm(row.get("device_id", ""))
            vendor = norm(row.get("vendor", "")) or "UnknownVendor"
            model = norm(row.get("model", "")) or "UnknownModel"
            fw = norm(row.get("firmware_version", "")) or "UNKNOWN"
            exp_raw = row.get("exposed_to_internet", "")

            try:
                exp = _parse_bool(exp_raw)
            except Exception as e:
                raise ValueError(f"Row {i}: {e}")

            if not dev_id:
                raise ValueError(f"Row {i}: device_id is empty")

            devices.append(Device(
                device_id=dev_id,
                vendor=vendor,
                model=model,
                firmware_version=fw,
                exposed_to_internet=exp,
            ))

    return devices
"@

Write-Text (Join-Path $Root "aegiot\classify.py") @"
from __future__ import annotations

def classify_device_type(vendor: str, model: str) -> str:
    v = (vendor or "").lower()
    m = (model or "").lower()
    text = f"{v} {m}"

    if any(k in text for k in ["hikvision", "dahua", "reolink", "ipc-", "ds-2cd", "rlc-", "camera", "cam"]):
        return "camera"
    if any(k in text for k in ["router", "archer", "edgerouter", "hap", "mikrotik", "ubiquiti", "access point", "ap "]):
        return "router"
    if any(k in text for k in ["qnap", "synology", "nas", "ds220", "ts-"]):
        return "nas"
    if any(k in text for k in ["dvr", "nvr", "ds-76", "nvr4", "video recorder"]):
        return "dvr"
    return "other"
"@

Write-Text (Join-Path $Root "aegiot\scoring.py") @"
from __future__ import annotations
import re
from datetime import datetime
from .models import Device
from .classify import classify_device_type

VENDOR_RISK = {
    "ubiquiti": "low",
    "mikrotik": "low",
    "synology": "low",
    "qnap": "medium",
    "tp-link": "medium",
    "xiaomi": "medium",
    "reolink": "medium",
    "hikvision": "high",
    "dahua": "high",
    "generic": "high",
}

def _vendor_level(vendor: str) -> str:
    key = (vendor or "").strip().lower()
    return VENDOR_RISK.get(key, "medium")

def extract_firmware_year(fw: str) -> int | None:
    s = (fw or "").strip()
    m = re.search(r"(19\d{2}|20\d{2})", s)
    if not m:
        return None
    y = int(m.group(1))
    if y < 1990 or y > (datetime.now().year + 1):
        return None
    return y

def _level_from_score(score: int) -> str:
    if score <= 25: return "LOW"
    if score <= 50: return "MEDIUM"
    if score <= 75: return "HIGH"
    return "CRITICAL"

def compute_score(device: Device) -> None:
    reasons: list[str] = []
    recs: list[str] = []

    device.device_type = classify_device_type(device.vendor, device.model)

    score = 0

    vlevel = _vendor_level(device.vendor)
    if vlevel == "low":
        score += 10; reasons.append("Vendor base risk: LOW (+10)")
    elif vlevel == "medium":
        score += 20; reasons.append("Vendor base risk: MEDIUM (+20)")
    else:
        score += 30; reasons.append("Vendor base risk: HIGH (+30)")

    if device.exposed_to_internet:
        score += 25
        reasons.append("Exposed to internet: YES (+25)")
    else:
        reasons.append("Exposed to internet: NO (+0)")

    dtype = device.device_type
    if dtype in ("nas", "dvr"):
        score += 15; reasons.append(f"Device type '{dtype}' higher impact (+15)")
    elif dtype in ("camera", "router"):
        score += 10; reasons.append(f"Device type '{dtype}' common attack surface (+10)")
    else:
        score += 5; reasons.append("Device type 'other' (+5)")

    fw = (device.firmware_version or "").strip()
    if fw.upper() == "UNKNOWN" or fw == "":
        score += 15
        reasons.append("Firmware version: UNKNOWN (+15)")
    else:
        y = extract_firmware_year(fw)
        if y is None:
            score += 10
            reasons.append("Firmware version: odd format (+10)")
        else:
            now = datetime.now().year
            age = now - y
            if age > 3:
                score += 20
                reasons.append(f"Firmware appears old ({y}) (+20)")
            else:
                reasons.append(f"Firmware appears recent ({y}) (+0)")

    score = max(0, min(100, int(score)))
    device.score = score
    device.risk_level = _level_from_score(score)
    device.reasons = reasons

    lvl = device.risk_level
    if lvl in ("HIGH", "CRITICAL"):
        recs.append("Remove direct internet exposure (VPN/allowlist) or place behind firewall.")
        recs.append("Update firmware to latest stable and document versions.")
        recs.append("Enforce strong auth: unique credentials, MFA where possible.")
        if dtype in ("router", "nas"):
            recs.append("Review admin services (SSH/Telnet/HTTP) and close unused ports.")
    elif lvl == "MEDIUM":
        recs.append("Schedule firmware updates and enable auto-update if supported.")
        recs.append("Rotate credentials and disable default accounts.")
        recs.append("Restrict management interfaces to internal networks only.")
    else:
        recs.append("Keep inventory and a patch cadence (monthly/quarterly).")
        recs.append("Keep behind NAT/firewall; avoid direct exposure.")
        recs.append("Document baseline config and monitor changes.")

    device.recommendations = recs[:4]
"@

Write-Text (Join-Path $Root "aegiot\report.py") @"
from __future__ import annotations
from datetime import datetime
from .models import Device

def render_report(devices: list[Device], title: str = "AegIoT Risk Report") -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for d in devices:
        counts[d.risk_level] = counts.get(d.risk_level, 0) + 1

    top5 = sorted(devices, key=lambda x: x.score, reverse=True)[:5]

    lines: list[str] = []
    lines.append(f"# {title}")
    lines.append(f"- Generated: **{ts}**")
    lines.append("")

    lines.append("## Executive summary")
    lines.append(
        f"- LOW: {counts.get('LOW',0)} | MEDIUM: {counts.get('MEDIUM',0)} | HIGH: {counts.get('HIGH',0)} | CRITICAL: {counts.get('CRITICAL',0)}"
    )
    lines.append("")

    lines.append("Top 5 by score:")
    for d in top5:
        lines.append(f"- {d.device_id} - {d.vendor} {d.model} - {d.score} ({d.risk_level})")
    lines.append("")

    lines.append("## Devices")
    lines.append("| device_id | vendor | model | type | firmware | exposed | score | level |")
    lines.append("|---|---|---|---|---|---:|---:|---|")
    for d in devices:
        exp = "yes" if d.exposed_to_internet else "no"
        lines.append(f"| {d.device_id} | {d.vendor} | {d.model} | {d.device_type} | {d.firmware_version} | {exp} | {d.score} | {d.risk_level} |")
    lines.append("")

    for d in sorted(devices, key=lambda x: x.score, reverse=True):
        lines.append(f"## {d.device_id} - {d.vendor} {d.model}")
        lines.append(f"- Type: **{d.device_type}**")
        lines.append(f"- Firmware: **{d.firmware_version}**")
        lines.append(f"- Exposed: **{'YES' if d.exposed_to_internet else 'NO'}**")
        lines.append(f"- Score: **{d.score}** ({d.risk_level})")
        lines.append("")

        lines.append("Reasons:")
        for r in d.reasons:
            lines.append(f"- {r}")
        lines.append("")

        lines.append("Recommended actions (2-4):")
        for a in d.recommendations:
            lines.append(f"- {a}")
        lines.append("")

    lines.append("## 7 / 30 / 90 day plan")
    lines.append("- 7 days: fix CRITICAL/HIGH first, remove exposure, rotate creds, patch what exists.")
    lines.append("- 30 days: inventory accuracy, standard configs, segmentation, basic monitoring.")
    lines.append("- 90 days: policy/compliance mapping, continuous scanning, change mgmt, playbooks.")
    lines.append("")

    lines.append("## Disclaimer")
    lines.append("Defensive triage tool. Local/fake data. No exploitation.")
    lines.append("")

    return "\n".join(lines)
"@

Write-Text (Join-Path $Root "aegiot\cli.py") @"
from __future__ import annotations
import argparse
from pathlib import Path
from .parsing import load_devices
from .scoring import compute_score
from .report import render_report

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="aegiot", description="AegIoT - IoT Firmware Risk Mapper (CLI)")
    p.add_argument("--input", required=True, help="Input CSV path")
    p.add_argument("--output", required=True, help="Output report path (Markdown)")
    args = p.parse_args(argv)

    devices = load_devices(args.input)
    for d in devices:
        compute_score(d)

    md = render_report(devices, title="AegIoT - IoT Firmware Risk Mapper")
    outp = Path(args.output)
    outp.write_text(md, encoding="utf-8")

    print(f"OK: wrote report -> {outp}")
    return 0
"@

# 8) Init git (optional)
$git = Get-Command git -ErrorAction SilentlyContinue
if ($git) {
  Push-Location $Root
  if (!(Test-Path (Join-Path $Root ".git"))) {
    git init | Out-Null
    git branch -m main 2>$null | Out-Null
  }
  Pop-Location
}

Write-Host ""
Write-Host "OK: project generated at $Root"
Write-Host "Next commands:"
Write-Host "  cd $Root"
Write-Host "  python -m venv .venv"
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host "  python -m aegiot --input sample_devices.csv --output report.md"
