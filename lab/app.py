from flask import Flask, jsonify, request
from datetime import datetime, timezone
from pathlib import Path
import csv
import json
import hashlib
import os
import subprocess

from aegiot.models import Device
from aegiot.scoring import compute_score, extract_firmware_year
from aegiot.report import render_report

REPO_ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = REPO_ROOT / "docs" / "reports"

app = Flask(__name__)


def _parse_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    s = str(value or "").strip().lower()
    if s in ("1", "true", "yes", "y", "on"):
        return True
    if s in ("0", "false", "no", "n", "off", ""):
        return False
    return False


def _device_from_payload(item: dict, idx: int) -> Device:
    dev_id = str(item.get("device_id") or f"device-{idx:03d}").strip()
    vendor = str(item.get("vendor") or "UnknownVendor").strip()
    model = str(item.get("model") or "UnknownModel").strip()
    fw = str(item.get("firmware_version") or "UNKNOWN").strip()
    exposed = _parse_bool(item.get("exposed_to_internet"))
    return Device(
        device_id=dev_id,
        vendor=vendor,
        model=model,
        firmware_version=fw,
        exposed_to_internet=exposed,
    )


def _harden_device(device: Device) -> Device:
    now_year = datetime.now().year
    fw = device.firmware_version or ""
    year = extract_firmware_year(fw)

    updated_fw = fw
    if fw.strip() == "" or fw.upper() == "UNKNOWN":
        updated_fw = f"fw_{now_year}"
    elif year is not None and (now_year - year) > 2:
        updated_fw = f"fw_{now_year}"

    return Device(
        device_id=device.device_id,
        vendor=device.vendor,
        model=device.model,
        firmware_version=updated_fw,
        exposed_to_internet=False,
    )


def _counts(devices):
    out = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for d in devices:
        out[d.risk_level] = out.get(d.risk_level, 0) + 1
    return out


def _overall(devices):
    if not devices:
        return 0
    return round(sum(d.score for d in devices) / len(devices), 2)


def _device_payload(device):
    return {
        "device_id": device.device_id,
        "vendor": device.vendor,
        "model": device.model,
        "device_type": device.device_type,
        "firmware_version": device.firmware_version,
        "exposed_to_internet": device.exposed_to_internet,
        "score": device.score,
        "risk_level": device.risk_level,
        "reasons": list(device.reasons),
        "recommendations": list(device.recommendations),
    }


def _by_key(devices, key):
    out = {}
    for d in devices:
        k = getattr(d, key) or "unknown"
        bucket = out.get(k)
        if not bucket:
            bucket = {
                "counts": {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0},
                "avg_score": 0,
                "exposed_count": 0,
                "total": 0,
            }
            out[k] = bucket
        bucket["counts"][d.risk_level] = bucket["counts"].get(d.risk_level, 0) + 1
        bucket["total"] += 1
        bucket["exposed_count"] += 1 if d.exposed_to_internet else 0
        bucket["avg_score"] = round(
            (bucket["avg_score"] * (bucket["total"] - 1) + d.score) / bucket["total"],
            2,
        )
    return out


def _exposure_counts(devices):
    exposed_yes = sum(1 for d in devices if d.exposed_to_internet)
    exposed_no = len(devices) - exposed_yes
    return {"exposed_yes": exposed_yes, "exposed_no": exposed_no}


def _git_sha() -> str:
    env_sha = os.getenv("GITHUB_SHA")
    if env_sha:
        return env_sha[:7]
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(REPO_ROOT),
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return out or "n/a"
    except Exception:
        return "n/a"


def _write_csv(path: Path, devices) -> str:
    headers = ["device_id", "vendor", "model", "firmware_version", "exposed_to_internet"]
    rows = []
    for d in devices:
        rows.append({
            "device_id": d.device_id,
            "vendor": d.vendor,
            "model": d.model,
            "firmware_version": d.firmware_version,
            "exposed_to_internet": "true" if d.exposed_to_internet else "false",
        })

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    return path.read_text(encoding="utf-8")


def _write_diff_md(before_devices, after_devices, path: Path) -> None:
    before_score = _overall(before_devices)
    after_score = _overall(after_devices)
    delta = round(after_score - before_score, 2)

    counts_before = _counts(before_devices)
    counts_after = _counts(after_devices)

    before_map = {d.device_id: d for d in before_devices}
    after_map = {d.device_id: d for d in after_devices}

    improvements = []
    for device_id in sorted(set(before_map) & set(after_map)):
        b = before_map[device_id]
        a = after_map[device_id]
        improvement = b.score - a.score
        improvements.append((improvement, b, a))

    improvements.sort(key=lambda x: (-x[0], x[1].device_id))

    lines = []
    lines.append("# AegIoT Demo Diff Report")
    lines.append("")
    lines.append("## Overall scores")
    lines.append("- Before overall score: {0}".format(before_score))
    lines.append("- After overall score: {0}".format(after_score))
    lines.append("- Delta (after - before): {0}".format(delta))
    lines.append("")

    lines.append("## Severity counts")
    lines.append("| Severity | Before | After |")
    lines.append("|---|---:|---:|")
    for level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
        lines.append("| {0} | {1} | {2} |".format(
            level,
            counts_before.get(level, 0),
            counts_after.get(level, 0),
        ))
    lines.append("")

    lines.append("## Top 5 improvements")
    lines.append("Improvement is (before_score - after_score).")
    if not improvements:
        lines.append("- No comparable devices found.")
    else:
        for improvement, b, a in improvements[:5]:
            label = "{0} - {1} {2}".format(b.device_id, b.vendor, b.model).strip()
            lines.append("- {0} - improvement {1} ({2} -> {3})".format(
                label,
                improvement,
                b.score,
                a.score,
            ))
    lines.append("")

    lines.append("## 7/30/90 hardening plan")
    lines.append("- 7 days: remove internet exposure, disable legacy services, rotate credentials.")
    lines.append("- 30 days: enforce TLS/HTTPS, update firmware, validate inventory accuracy.")
    lines.append("- 90 days: continuous monitoring, vulnerability management, and policy reviews.")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


@app.route("/run", methods=["POST"])
def run_simulation():
    payload = request.get_json(force=True, silent=True) or {}
    devices_payload = payload.get("devices") or []
    seed = payload.get("seed")

    if not isinstance(devices_payload, list) or not devices_payload:
        return jsonify({"error": "devices list is required"}), 400

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    before_devices = []
    for idx, item in enumerate(devices_payload, start=1):
        device = _device_from_payload(item or {}, idx)
        compute_score(device)
        before_devices.append(device)

    after_devices = []
    for device in before_devices:
        hardened = _harden_device(device)
        compute_score(hardened)
        after_devices.append(hardened)

    before_md = render_report(before_devices, "AegIoT - IoT Firmware Risk Mapper")
    after_md = render_report(after_devices, "AegIoT - IoT Firmware Risk Mapper")

    (REPORTS_DIR / "before.md").write_text(before_md, encoding="utf-8")
    (REPORTS_DIR / "after.md").write_text(after_md, encoding="utf-8")

    _write_diff_md(before_devices, after_devices, REPORTS_DIR / "diff.md")

    before_csv_text = _write_csv(REPORTS_DIR / "input_devices.csv", before_devices)

    before_payload = [_device_payload(d) for d in sorted(before_devices, key=lambda x: (-x.score, x.device_id))]
    after_payload = [_device_payload(d) for d in sorted(after_devices, key=lambda x: (-x.score, x.device_id))]

    before_map = {d.device_id: d for d in before_devices}
    after_map = {d.device_id: d for d in after_devices}

    diff_items = []
    for device_id in sorted(set(before_map) & set(after_map)):
        b = before_map[device_id]
        a = after_map[device_id]
        diff_items.append({
            "device_id": device_id,
            "vendor": b.vendor,
            "model": b.model,
            "device_type": b.device_type,
            "before_score": b.score,
            "after_score": a.score,
            "delta": round(a.score - b.score, 2),
            "risk_level_before": b.risk_level,
            "risk_level_after": a.risk_level,
            "exposed_before": b.exposed_to_internet,
            "exposed_after": a.exposed_to_internet,
        })

    diff_items.sort(key=lambda x: (x["delta"], x["device_id"]))

    top_improvements = [x for x in diff_items if x["delta"] < 0][:10]
    top_regressions = [x for x in reversed(diff_items) if x["delta"] > 0][:10]

    before_overall = _overall(before_devices)
    after_overall = _overall(after_devices)
    delta = round(after_overall - before_overall, 2)
    risk_reduction = round(before_overall - after_overall, 2)

    top5 = sorted(before_devices, key=lambda x: (-x.score, x.device_id))[:5]
    top_items = [
        {
            "device_id": d.device_id,
            "vendor": d.vendor,
            "model": d.model,
            "score": d.score,
            "risk_level": d.risk_level,
        }
        for d in top5
    ]

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    git_sha = _git_sha()
    run_id = "{0}-{1}".format(generated_at, git_sha)
    fingerprint = hashlib.sha256(before_csv_text.encode("utf-8")).hexdigest()

    summary_payload = {
        "overall_score": before_overall,
        "counts": _counts(before_devices),
        "before_overall_score": before_overall,
        "after_overall_score": after_overall,
        "delta": delta,
        "risk_reduction": risk_reduction,
        "counts_before": _counts(before_devices),
        "counts_after": _counts(after_devices),
        "top5": top_items,
        "generated_at": generated_at,
        "git_sha": git_sha,
        "run_id": run_id,
        "input_fingerprint": fingerprint,
        "by_vendor": _by_key(before_devices, "vendor"),
        "by_type": _by_key(before_devices, "device_type"),
        "exposure": _exposure_counts(before_devices),
        "top_improvements": top_improvements,
        "top_regressions": top_regressions,
        "reports": {
            "before": "reports/before.md",
            "after": "reports/after.md",
            "diff": "reports/diff.md",
            "devices_before": "reports/devices_before.json",
            "devices_after": "reports/devices_after.json",
            "devices_diff": "reports/devices_diff.json",
        },
    }

    (REPORTS_DIR / "summary.json").write_text(
        json.dumps(summary_payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (REPORTS_DIR / "devices_before.json").write_text(
        json.dumps(before_payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (REPORTS_DIR / "devices_after.json").write_text(
        json.dumps(after_payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (REPORTS_DIR / "devices_diff.json").write_text(
        json.dumps(diff_items, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    return jsonify({
        "run_id": run_id,
        "reports": summary_payload["reports"],
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)