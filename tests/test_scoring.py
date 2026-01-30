import pytest

from aegiot.models import Device
from aegiot.parsing import _parse_bool, load_devices
from aegiot.scoring import compute_score


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("true", True),
        ("FALSE", False),
        ("1", True),
        ("0", False),
        ("yes", True),
        ("No", False),
    ],
)
def test_parse_bool_accepts_common_variants(raw, expected):
    assert _parse_bool(raw) is expected


def test_missing_required_columns_raises_clear_error(tmp_path):
    csv_text = "device_id,vendor,model,firmware_version\n1,acme,widget,1.2.3\n"
    path = tmp_path / "missing.csv"
    path.write_text(csv_text, encoding="utf-8")

    with pytest.raises(ValueError) as excinfo:
        load_devices(str(path))

    msg = str(excinfo.value)
    assert "Missing required columns" in msg
    assert "exposed_to_internet" in msg


def test_exposed_to_internet_scores_higher():
    d_true = Device(
        device_id="1",
        vendor="acme",
        model="widget",
        firmware_version="1.2.3",
        exposed_to_internet=True,
    )
    d_false = Device(
        device_id="2",
        vendor="acme",
        model="widget",
        firmware_version="1.2.3",
        exposed_to_internet=False,
    )
    compute_score(d_true)
    compute_score(d_false)
    assert d_true.score > d_false.score


def test_firmware_unknown_or_empty_penalized_vs_normal():
    d_unknown = Device(
        device_id="1",
        vendor="acme",
        model="widget",
        firmware_version="UNKNOWN",
        exposed_to_internet=False,
    )
    d_empty = Device(
        device_id="2",
        vendor="acme",
        model="widget",
        firmware_version="",
        exposed_to_internet=False,
    )
    d_normal = Device(
        device_id="3",
        vendor="acme",
        model="widget",
        firmware_version="1.2.3",
        exposed_to_internet=False,
    )
    compute_score(d_unknown)
    compute_score(d_empty)
    compute_score(d_normal)
    assert d_unknown.score > d_normal.score
    assert d_empty.score > d_normal.score


def test_vendor_base_risk_high_beats_low():
    d_high = Device(
        device_id="1",
        vendor="hikvision",
        model="camera-x",
        firmware_version="1.2.3",
        exposed_to_internet=False,
    )
    d_low = Device(
        device_id="2",
        vendor="ubiquiti",
        model="camera-x",
        firmware_version="1.2.3",
        exposed_to_internet=False,
    )
    compute_score(d_high)
    compute_score(d_low)
    assert d_high.score > d_low.score
