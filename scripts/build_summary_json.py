import json
import sys
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


def main() -> int:
    repo_root = REPO_ROOT
    input_csv = repo_root / "sample_devices.csv"
    hardened_csv = repo_root / "docs" / "reports" / "hardened_devices.csv"
    out_dir = repo_root / "docs" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "summary.json"

    before_devices = _load_and_score(input_csv)
    if hardened_csv.exists():
        after_devices = _load_and_score(hardened_csv)
    else:
        after_devices = list(before_devices)

    before_overall = _overall(before_devices)
    after_overall = _overall(after_devices)
    delta = round(after_overall - before_overall, 2)

    counts_before = _counts(before_devices)
    counts_after = _counts(after_devices)

    top = sorted(before_devices, key=lambda x: (-x.score, x.device_id))[:5]
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

    payload = {
        "overall_score": before_overall,
        "counts": counts_before,
        "before_overall_score": before_overall,
        "after_overall_score": after_overall,
        "delta": delta,
        "counts_before": counts_before,
        "counts_after": counts_after,
        "top5": top_items,
        "reports": {
            "before": "reports/before.md",
            "after": "reports/after.md",
            "diff": "reports/diff.md",
        },
    }

    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
