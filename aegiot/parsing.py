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