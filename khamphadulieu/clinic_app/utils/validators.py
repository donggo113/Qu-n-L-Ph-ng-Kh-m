"""Kiểm tra dữ liệu đầu vào bằng Regex."""
import re
from datetime import datetime

PHONE_RE = re.compile(r"^(0|\+84)(3|5|7|8|9)\d{8}$")
# Quy ước nhóm: 2 chữ cái + 13 chữ số (ghi rõ quy ước này trong báo cáo)
INSURANCE_RE = re.compile(r"^[A-Z]{2}\d{13}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIME_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
NAME_RE = re.compile(r"^[^\W\d_]+(?:[ '\-][^\W\d_]+)*$", re.UNICODE)


def is_valid_phone(value: str) -> bool:
    return bool(PHONE_RE.match((value or "").strip()))


def is_valid_insurance(value: str) -> bool:
    return bool(INSURANCE_RE.match((value or "").strip().upper()))


def is_valid_name(value: str) -> bool:
    return bool(NAME_RE.match((value or "").strip()))


def is_valid_date(value: str) -> bool:
    """Định dạng YYYY-MM-DD và là ngày có thật (không có 2025-02-30)."""
    value = (value or "").strip()
    if not DATE_RE.match(value):
        return False
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_valid_time(value: str) -> bool:
    return bool(TIME_RE.match((value or "").strip()))


def time_to_minutes(value: str) -> int:
    h, m = value.split(":")
    return int(h) * 60 + int(m)
