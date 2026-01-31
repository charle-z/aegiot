import csv
import io
from pathlib import Path


FALSE_VALUE = "false"
TRUE_VALUE = "true"


def _detect_dialect(text: str) -> csv.Dialect:
    try:
        return csv.Sniffer().sniff(text[:4096])
    except Exception:
        return csv.excel


def _action_for_column(name: str) -> str | None:
    col = name.lower()
    if col in ("device_id", "vendor", "model"):
        return None
    if "cve" in col or "vuln" in col:
        return "zero"
    if "default" in col and ("cred" in col or "password" in col):
        return "false"
    if any(k in col for k in ["exposed", "internet", "public", "wan"]):
        return "false"
    if any(k in col for k in ["telnet", "upnp", "ssh", "ftp"]):
        return "false"
    if any(k in col for k in ["eol", "unsupported"]):
        return "false"
    if any(k in col for k in ["tls", "https", "encryption"]):
        return "true"
    return None


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    input_csv = repo_root / "sample_devices.csv"
    out_dir = repo_root / "docs" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    output_csv = out_dir / "hardened_devices.csv"

    text = input_csv.read_text(encoding="utf-8")
    dialect = _detect_dialect(text)

    reader = csv.DictReader(io.StringIO(text), dialect=dialect)
    fieldnames = reader.fieldnames or []

    rows = []
    for row in reader:
        updated = dict(row)
        for name in fieldnames:
            action = _action_for_column(name)
            if action == "false":
                updated[name] = FALSE_VALUE
            elif action == "true":
                updated[name] = TRUE_VALUE
            elif action == "zero":
                updated[name] = "0"
        rows.append(updated)

    with output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, dialect=dialect)
        writer.writeheader()
        writer.writerows(rows)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
