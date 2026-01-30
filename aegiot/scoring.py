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