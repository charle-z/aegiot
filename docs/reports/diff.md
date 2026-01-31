# AegIoT Demo Diff Report

## Overall scores
- Before overall score: 64.17
- After overall score: 47.5
- Delta (after - before): -16.67

## Severity counts
| Severity | Before | After |
|---|---:|---:|
| LOW | 2 | 2 |
| MEDIUM | 2 | 6 |
| HIGH | 4 | 4 |
| CRITICAL | 4 | 0 |

## Top 5 improvements
Improvement is (before_score - after_score).
- cam-001 - Hikvision DS-2CD2043G0-I - improvement 25 (85 -> 60)
- cam-002 - Dahua IPC-HFW1230S - improvement 25 (85 -> 60)
- dvr-001 - Hikvision DS-7608NI - improvement 25 (80 -> 55)
- dvr-002 - Dahua NVR4108 - improvement 25 (85 -> 60)
- iot-002 - Reolink RLC-520A - improvement 25 (75 -> 50)

## 7/30/90 hardening plan
- 7 days: remove internet exposure, disable legacy services, rotate credentials.
- 30 days: enforce TLS/HTTPS, update firmware, validate inventory accuracy.
- 90 days: continuous monitoring, vulnerability management, and policy reviews.
