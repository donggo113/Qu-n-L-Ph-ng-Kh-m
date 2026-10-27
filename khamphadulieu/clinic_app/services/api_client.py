"""Phần API bắt buộc. Ví dụ: lấy danh mục tỉnh/thành làm Combobox địa chỉ.
TODO nhóm: kiểm tra API còn hoạt động + điều khoản sử dụng, ghi nguồn trong báo cáo."""
import json
from pathlib import Path

import requests

from config import DATA_DIR

API_URL = "https://provinces.open-api.vn/api/p/"   # kiểm tra lại trước khi dùng
CACHE = Path(DATA_DIR) / "provinces.json"
FALLBACK = ["Hà Nội", "TP. Hồ Chí Minh", "Đà Nẵng", "Cần Thơ", "Hải Phòng"]


def fetch_provinces() -> list:
    """Gọi API, làm sạch, lưu cache JSON; mất mạng thì dùng cache, rồi dự phòng."""
    try:
        r = requests.get(API_URL, timeout=5)
        r.raise_for_status()
        names = sorted({p["name"].strip() for p in r.json() if p.get("name")})
        if names:
            CACHE.write_text(json.dumps(names, ensure_ascii=False, indent=2), encoding="utf-8")
            return names
    except (requests.RequestException, ValueError, KeyError):
        pass
    try:
        return json.loads(CACHE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return list(FALLBACK)
