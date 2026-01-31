# AegIoT - IoT Firmware Risk Mapper
- Generated: **2026-01-31 13:40:42**

## Executive summary
- LOW: 2 | MEDIUM: 2 | HIGH: 4 | CRITICAL: 4

Top 5 by score:
- cam-001 - Hikvision DS-2CD2043G0-I - 85 (CRITICAL)
- cam-002 - Dahua IPC-HFW1230S - 85 (CRITICAL)
- dvr-002 - Dahua NVR4108 - 85 (CRITICAL)
- dvr-001 - Hikvision DS-7608NI - 80 (CRITICAL)
- rtr-001 - TP-Link Archer C7 - 75 (HIGH)

## Devices
| device_id | vendor | model | type | firmware | exposed | score | level |
|---|---|---|---|---|---:|---:|---|
| cam-001 | Hikvision | DS-2CD2043G0-I | camera | 5.5.82_2021 | yes | 85 | CRITICAL |
| cam-002 | Dahua | IPC-HFW1230S | camera | 2.622.0000000.7.R_2020 | yes | 85 | CRITICAL |
| rtr-001 | TP-Link | Archer C7 | router | v2_2019 | yes | 75 | HIGH |
| rtr-002 | Ubiquiti | EdgeRouter X | router | 2.0.9-hotfix.6_2022 | no | 40 | MEDIUM |
| nas-001 | QNAP | TS-231P | router | 4.5.4_2021 | yes | 75 | HIGH |
| nas-002 | Synology | DS220+ | nas | DSM 7.2_2023 | no | 25 | LOW |
| dvr-001 | Hikvision | DS-7608NI | camera | UNKNOWN | yes | 80 | CRITICAL |
| dvr-002 | Dahua | NVR4108 | camera | 3.210_2018 | yes | 85 | CRITICAL |
| iot-001 | Xiaomi | Mi Camera 2K | camera | 1.3.6_2022 | no | 50 | MEDIUM |
| iot-002 | Reolink | RLC-520A | camera | v3.0.0_2021 | yes | 75 | HIGH |
| ap-001 | MikroTik | hAP ac2 | router | 7.12_2024 | no | 20 | LOW |
| oth-001 | Generic | SmartPlug X1 | other | UNKNOWN | yes | 75 | HIGH |

## cam-001 - Hikvision DS-2CD2043G0-I
- Type: **camera**
- Firmware: **5.5.82_2021**
- Exposed: **YES**
- Score: **85** (CRITICAL)

Reasons:
- Vendor base risk: HIGH (+30)
- Exposed to internet: YES (+25)
- Device type 'camera' common attack surface (+10)
- Firmware appears old (2021) (+20)

Recommended actions (2-4):
- Remove direct internet exposure (VPN/allowlist) or place behind firewall.
- Update firmware to latest stable and document versions.
- Enforce strong auth: unique credentials, MFA where possible.

## cam-002 - Dahua IPC-HFW1230S
- Type: **camera**
- Firmware: **2.622.0000000.7.R_2020**
- Exposed: **YES**
- Score: **85** (CRITICAL)

Reasons:
- Vendor base risk: HIGH (+30)
- Exposed to internet: YES (+25)
- Device type 'camera' common attack surface (+10)
- Firmware appears old (2020) (+20)

Recommended actions (2-4):
- Remove direct internet exposure (VPN/allowlist) or place behind firewall.
- Update firmware to latest stable and document versions.
- Enforce strong auth: unique credentials, MFA where possible.

## dvr-002 - Dahua NVR4108
- Type: **camera**
- Firmware: **3.210_2018**
- Exposed: **YES**
- Score: **85** (CRITICAL)

Reasons:
- Vendor base risk: HIGH (+30)
- Exposed to internet: YES (+25)
- Device type 'camera' common attack surface (+10)
- Firmware appears old (2018) (+20)

Recommended actions (2-4):
- Remove direct internet exposure (VPN/allowlist) or place behind firewall.
- Update firmware to latest stable and document versions.
- Enforce strong auth: unique credentials, MFA where possible.

## dvr-001 - Hikvision DS-7608NI
- Type: **camera**
- Firmware: **UNKNOWN**
- Exposed: **YES**
- Score: **80** (CRITICAL)

Reasons:
- Vendor base risk: HIGH (+30)
- Exposed to internet: YES (+25)
- Device type 'camera' common attack surface (+10)
- Firmware version: UNKNOWN (+15)

Recommended actions (2-4):
- Remove direct internet exposure (VPN/allowlist) or place behind firewall.
- Update firmware to latest stable and document versions.
- Enforce strong auth: unique credentials, MFA where possible.

## rtr-001 - TP-Link Archer C7
- Type: **router**
- Firmware: **v2_2019**
- Exposed: **YES**
- Score: **75** (HIGH)

Reasons:
- Vendor base risk: MEDIUM (+20)
- Exposed to internet: YES (+25)
- Device type 'router' common attack surface (+10)
- Firmware appears old (2019) (+20)

Recommended actions (2-4):
- Remove direct internet exposure (VPN/allowlist) or place behind firewall.
- Update firmware to latest stable and document versions.
- Enforce strong auth: unique credentials, MFA where possible.
- Review admin services (SSH/Telnet/HTTP) and close unused ports.

## nas-001 - QNAP TS-231P
- Type: **router**
- Firmware: **4.5.4_2021**
- Exposed: **YES**
- Score: **75** (HIGH)

Reasons:
- Vendor base risk: MEDIUM (+20)
- Exposed to internet: YES (+25)
- Device type 'router' common attack surface (+10)
- Firmware appears old (2021) (+20)

Recommended actions (2-4):
- Remove direct internet exposure (VPN/allowlist) or place behind firewall.
- Update firmware to latest stable and document versions.
- Enforce strong auth: unique credentials, MFA where possible.
- Review admin services (SSH/Telnet/HTTP) and close unused ports.

## iot-002 - Reolink RLC-520A
- Type: **camera**
- Firmware: **v3.0.0_2021**
- Exposed: **YES**
- Score: **75** (HIGH)

Reasons:
- Vendor base risk: MEDIUM (+20)
- Exposed to internet: YES (+25)
- Device type 'camera' common attack surface (+10)
- Firmware appears old (2021) (+20)

Recommended actions (2-4):
- Remove direct internet exposure (VPN/allowlist) or place behind firewall.
- Update firmware to latest stable and document versions.
- Enforce strong auth: unique credentials, MFA where possible.

## oth-001 - Generic SmartPlug X1
- Type: **other**
- Firmware: **UNKNOWN**
- Exposed: **YES**
- Score: **75** (HIGH)

Reasons:
- Vendor base risk: HIGH (+30)
- Exposed to internet: YES (+25)
- Device type 'other' (+5)
- Firmware version: UNKNOWN (+15)

Recommended actions (2-4):
- Remove direct internet exposure (VPN/allowlist) or place behind firewall.
- Update firmware to latest stable and document versions.
- Enforce strong auth: unique credentials, MFA where possible.

## iot-001 - Xiaomi Mi Camera 2K
- Type: **camera**
- Firmware: **1.3.6_2022**
- Exposed: **NO**
- Score: **50** (MEDIUM)

Reasons:
- Vendor base risk: MEDIUM (+20)
- Exposed to internet: NO (+0)
- Device type 'camera' common attack surface (+10)
- Firmware appears old (2022) (+20)

Recommended actions (2-4):
- Schedule firmware updates and enable auto-update if supported.
- Rotate credentials and disable default accounts.
- Restrict management interfaces to internal networks only.

## rtr-002 - Ubiquiti EdgeRouter X
- Type: **router**
- Firmware: **2.0.9-hotfix.6_2022**
- Exposed: **NO**
- Score: **40** (MEDIUM)

Reasons:
- Vendor base risk: LOW (+10)
- Exposed to internet: NO (+0)
- Device type 'router' common attack surface (+10)
- Firmware appears old (2022) (+20)

Recommended actions (2-4):
- Schedule firmware updates and enable auto-update if supported.
- Rotate credentials and disable default accounts.
- Restrict management interfaces to internal networks only.

## nas-002 - Synology DS220+
- Type: **nas**
- Firmware: **DSM 7.2_2023**
- Exposed: **NO**
- Score: **25** (LOW)

Reasons:
- Vendor base risk: LOW (+10)
- Exposed to internet: NO (+0)
- Device type 'nas' higher impact (+15)
- Firmware appears recent (2023) (+0)

Recommended actions (2-4):
- Keep inventory and a patch cadence (monthly/quarterly).
- Keep behind NAT/firewall; avoid direct exposure.
- Document baseline config and monitor changes.

## ap-001 - MikroTik hAP ac2
- Type: **router**
- Firmware: **7.12_2024**
- Exposed: **NO**
- Score: **20** (LOW)

Reasons:
- Vendor base risk: LOW (+10)
- Exposed to internet: NO (+0)
- Device type 'router' common attack surface (+10)
- Firmware appears recent (2024) (+0)

Recommended actions (2-4):
- Keep inventory and a patch cadence (monthly/quarterly).
- Keep behind NAT/firewall; avoid direct exposure.
- Document baseline config and monitor changes.

## 7 / 30 / 90 day plan
- 7 days: fix CRITICAL/HIGH first, remove exposure, rotate creds, patch what exists.
- 30 days: inventory accuracy, standard configs, segmentation, basic monitoring.
- 90 days: policy/compliance mapping, continuous scanning, change mgmt, playbooks.

## Disclaimer
Defensive triage tool. Local/fake data. No exploitation.
