# AegIoT

AegIoT is a defensive IoT inventory risk mapper (CLI).  
It reads a CSV inventory and generates a Markdown risk report (0-100).

## Try it (60s)
- View example report: [report_example.md](../report_example.md)
- Sample input CSV: [sample_devices.csv](../sample_devices.csv)

## Run locally
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m aegiot --input sample_devices.csv --output report.md
