from __future__ import annotations
from dataclasses import dataclass, field
from typing import List

@dataclass
class Device:
    device_id: str
    vendor: str
    model: str
    firmware_version: str
    exposed_to_internet: bool

    device_type: str = "other"
    score: int = 0
    risk_level: str = "LOW"
    reasons: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)