import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure repo root is on sys.path for direct script execution.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from aegiot.parsing import load_devices
from aegiot.scoring import compute_score


def _load_and_score(path: Path):
    devices = load_devices(str(path))
    for d in devices:
        compute_score(d)
    return devices


def _counts(devices):
    out = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for d in devices:
        out[d.risk_level] = out.get(d.risk_level, 0) + 1
    return out


def _overall(devices):
    if not devices:
        return 0
    return round(sum(d.score for d in devices) / len(devices), 2)


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


def _fingerprint(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha256(data).hexdigest()


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


def _sort_devices(devices):
    return sorted(devices, key=lambda x: (-x.score, x.device_id))


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


def main() -> int:
    repo_root = REPO_ROOT
    input_csv = repo_root / "sample_devices.csv"
    hardened_csv = repo_root / "docs" / "reports" / "hardened_devices.csv"
    out_dir = repo_root / "docs" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)

    before_devices = _load_and_score(input_csv)
    if hardened_csv.exists():
        after_devices = _load_and_score(hardened_csv)
    else:
        after_devices = list(before_devices)

    before_overall = _overall(before_devices)
    after_overall = _overall(after_devices)
    delta = round(after_overall - before_overall, 2)
    risk_reduction = round(before_overall - after_overall, 2)

    counts_before = _counts(before_devices)
    counts_after = _counts(after_devices)

    before_sorted = _sort_devices(before_devices)
    after_sorted = _sort_devices(after_devices)

    before_payload = [_device_payload(d) for d in before_sorted]
    after_payload = [_device_payload(d) for d in after_sorted]

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

    top = before_sorted[:5]
    top_items = [
        {
            "device_id": d.device_id,
            "vendor": d.vendor,
            "model": d.model,
            "score": d.score,
            "risk_level": d.risk_level,
        }
        for d in top
    ]

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    git_sha = _git_sha()
    run_id = "{0}-{1}".format(generated_at, git_sha)
    input_fingerprint = _fingerprint(input_csv)

    summary_payload = {
        "overall_score": before_overall,
        "counts": counts_before,
        "before_overall_score": before_overall,
        "after_overall_score": after_overall,
        "delta": delta,
        "risk_reduction": risk_reduction,
        "counts_before": counts_before,
        "counts_after": counts_after,
        "top5": top_items,
        "generated_at": generated_at,
        "git_sha": git_sha,
        "run_id": run_id,
        "input_fingerprint": input_fingerprint,
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

    (out_dir / "summary.json").write_text(
        json.dumps(summary_payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (out_dir / "devices_before.json").write_text(
        json.dumps(before_payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (out_dir / "devices_after.json").write_text(
        json.dumps(after_payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (out_dir / "devices_diff.json").write_text(
        json.dumps(diff_items, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
