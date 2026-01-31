# AegIoT - IoT Firmware Risk Mapper (CLI)

AegIoT reads a simple inventory CSV and generates a defensive risk report (0-100) per device.

## Demo publica (GitHub Pages)
URL esperada:
https://<owner>.github.io/<repo>/

## Quickstart (Windows)
```powershell
cd C:\aegiot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m aegiot --input sample_devices.csv --output report.md
```

## Run the CLI
```powershell
python -m aegiot --input sample_devices.csv --output report.md
```

## Generate demo reports locally
```powershell
python -m aegiot --input sample_devices.csv --output docs\reports\before.md
python scripts\make_hardened_csv.py
python -m aegiot --input docs\reports\hardened_devices.csv --output docs\reports\after.md
python scripts\build_diff_md.py
python scripts\build_summary_json.py
```

## Package info
aegiot is a package folder at .\aegiot.
python -c "import aegiot; print(aegiot.__file__)" prints:
C:\aegiot\aegiot\__init__.py

## Run tests
```powershell
pytest -q
```

## Run status script
```powershell
.\scripts\status.ps1
```

## Enable GitHub Pages from /docs
1. Open the repo on GitHub and go to Settings.
2. Open Pages.
3. Source: Deploy from a branch.
4. Branch: main (or your default branch) and folder /docs.
5. Save.

## Input CSV format
Columns:
- device_id,vendor,model,firmware_version,exposed_to_internet

## Output
- report.md (Markdown): summary + device table + per-device sections + 7/30/90 plan + disclaimer.

## License
MIT (see LICENSE).

## Disclaimer
Educational and defensive only. Use fake/local data. No exploitation.
