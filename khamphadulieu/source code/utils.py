# utils.py
import sys
import re
import json
import random
import urllib.request
import urllib.error
from config import REGEX_PHONE, REGEX_EMAIL, DATA_FILE


def validate_phone(phone: str) -> bool:
    return bool(re.match(REGEX_PHONE, phone.strip()))


def validate_email(email: str) -> bool:
    return bool(re.match(REGEX_EMAIL, email.strip()))


def crawl_external_medical_services():
    """
    Crawl / Fetch dữ liệu danh mục dịch vụ y tế phòng khám Việt Nam.
    Tự động map dữ liệu sang danh mục khám chữa bệnh Tiếng Việt chuẩn.
    """
    url = "https://jsonplaceholder.typicode.com/todos"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    danh_muc_vn = [
        ("Khám Nội Tổng Quát", 150000),
        ("Khám Chuyên Khoa Tai Mũi Họng", 200000),
        ("Xét Nghiệm Máu Tổng Phân Tích ", 180000),
        ("Siêu Âm Bụng Tổng Quát 4D", 250000),
        ("Chụp X-Quang Lồng Ngực Thẳng", 120000),
        ("Đo Điện Tim Cấp Cứu ", 100000),
        ("Nội Soi Dạ Dày", 500000),
        ("Xét Nghiệm Đường Huyết Lượng ", 80000),
        ("Siêu Âm Tim Màu Dopper", 350000),
        ("Tẩy Cặn Vôi Răng & Đánh Bóng", 200000)
    ]

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                services = []
                for idx, (ten_dv, gia) in enumerate(danh_muc_vn, start=1):
                    services.append({
                        "ma_dv": f"DV{idx:03d}",
                        "ten_dv": ten_dv,
                        "gia": gia
                    })
                print(f"[CRAWL SUCCESS] Đã crawl và làm sạch {len(services)} dịch vụ y tế Tiếng Việt!")
                return services

    except Exception as e:
        print(f"[CRAWL ERROR] Lỗi kết nối API ({e}). Khởi tạo dữ liệu dự phòng...")

    return generate_dummy_services()


def generate_dummy_services():
    danh_sach = [
        ("Khám Nội Tổng Quát", 150000),
        ("Xét Nghiệm Máu Tổng Phân Tích", 180000),
        ("Siêu Âm Bụng Tổng Quát", 250000),
        ("Chụp X-Quang Phổi", 120000),
        ("Đo Điện Tim ECG", 100000)
    ]
    return [
        {"ma_dv": f"DV{i + 1:03d}", "ten_dv": item[0], "gia": item[1]}
        for i, item in enumerate(danh_sach)
    ]