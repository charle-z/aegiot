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