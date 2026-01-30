from __future__ import annotations
from datetime import datetime
from .models import Device

def render_report(devices: list[Device], title: str = "AegIoT Risk Report") -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for d in devices:
        counts[d.risk_level] = counts.get(d.risk_level, 0) + 1

    top5 = sorted(devices, key=lambda x: x.score, reverse=True)[:5]

    lines: list[str] = []
    lines.append(f"# {title}")
    lines.append(f"- Generated: **{ts}**")
    lines.append("")

    lines.append("## Executive summary")
    lines.append(
        f"- LOW: {counts.get('LOW',0)} | MEDIUM: {counts.get('MEDIUM',0)} | HIGH: {counts.get('HIGH',0)} | CRITICAL: {counts.get('CRITICAL',0)}"
    )
    lines.append("")

    lines.append("Top 5 by score:")
    for d in top5:
        lines.append(f"- {d.device_id} - {d.vendor} {d.model} - {d.score} ({d.risk_level})")
    lines.append("")

    lines.append("## Devices")
    lines.append("| device_id | vendor | model | type | firmware | exposed | score | level |")
    lines.append("|---|---|---|---|---|---:|---:|---|")
    for d in devices:
        exp = "yes" if d.exposed_to_internet else "no"
        lines.append(f"| {d.device_id} | {d.vendor} | {d.model} | {d.device_type} | {d.firmware_version} | {exp} | {d.score} | {d.risk_level} |")
    lines.append("")

    for d in sorted(devices, key=lambda x: x.score, reverse=True):
        lines.append(f"## {d.device_id} - {d.vendor} {d.model}")
        lines.append(f"- Type: **{d.device_type}**")
        lines.append(f"- Firmware: **{d.firmware_version}**")
        lines.append(f"- Exposed: **{'YES' if d.exposed_to_internet else 'NO'}**")
        lines.append(f"- Score: **{d.score}** ({d.risk_level})")
        lines.append("")

        lines.append("Reasons:")
        for r in d.reasons:
            lines.append(f"- {r}")
        lines.append("")

        lines.append("Recommended actions (2-4):")
        for a in d.recommendations:
            lines.append(f"- {a}")
        lines.append("")

    lines.append("## 7 / 30 / 90 day plan")
    lines.append("- 7 days: fix CRITICAL/HIGH first, remove exposure, rotate creds, patch what exists.")
    lines.append("- 30 days: inventory accuracy, standard configs, segmentation, basic monitoring.")
    lines.append("- 90 days: policy/compliance mapping, continuous scanning, change mgmt, playbooks.")
    lines.append("")

    lines.append("## Disclaimer")
    lines.append("Defensive triage tool. Local/fake data. No exploitation.")
    lines.append("")

    return "\n".join(lines)