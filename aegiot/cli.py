from __future__ import annotations
import argparse
from pathlib import Path
from .parsing import load_devices
from .scoring import compute_score
from .report import render_report

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="aegiot", description="AegIoT - IoT Firmware Risk Mapper (CLI)")
    p.add_argument("--input", required=True, help="Input CSV path")
    p.add_argument("--output", required=True, help="Output report path (Markdown)")
    args = p.parse_args(argv)

    devices = load_devices(args.input)
    for d in devices:
        compute_score(d)

    md = render_report(devices, title="AegIoT - IoT Firmware Risk Mapper")
    outp = Path(args.output)
    outp.write_text(md, encoding="utf-8")

    print(f"OK: wrote report -> {outp}")
    return 0