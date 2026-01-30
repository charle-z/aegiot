# AegIoT - IoT Firmware Risk Mapper (CLI)

AegIoT reads a simple inventory CSV and generates a defensive risk report (0-100) per device.

## Quickstart (Windows)
`powershell
cd C:\aegiot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m aegiot --input sample_devices.csv --output report.md
`

## Input CSV format
Columns:
- device_id,vendor,model,firmware_version,exposed_to_internet

## Output
- report.md (Markdown): summary + device table + per-device sections + 7/30/90 plan + disclaimer.

## License
MIT (see LICENSE).

## Disclaimer
Educational and defensive only. Use fake/local data. No exploitation.