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
    before_csv = repo_root / "sample_devices.csv"
    after_csv = repo_root / "docs" / "reports" / "hardened_devices.csv"
    out_path = repo_root / "docs" / "reports" / "diff.md"

    before_devices = _load_and_score(before_csv)
    after_devices = _load_and_score(after_csv)

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

    out_path.write_text("\n".join(lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
