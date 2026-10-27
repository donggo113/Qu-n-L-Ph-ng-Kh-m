import os
import re

# Đường dẫn file dữ liệu
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "db", "data_phongkham.json")
USERS_FILE = os.path.join(BASE_DIR, "db", "users.json")
BACKUP_FILE = os.path.join(BASE_DIR, "db", "data_phongkham.json.bak")
EXPORT_CSV = os.path.join(BASE_DIR, "bao_cao_lich_kham.csv")

# Regular Expressions (Yêu cầu 5)
REGEX_PHONE = r"^(0[3|5|7|8|9])+([0-9]{8})$"  # Kiểm tra SĐT Việt Nam
REGEX_EMAIL = r"^[\w\.-]+@[\w\.-]+\.\w+$"      # Kiểm tra Email

# Hằng số màu sắc Vàng Chanh Pastel (Yêu cầu 6 & 8)
COLOR_BG = "#FDFBF7"
COLOR_SIDEBAR = "#FEF9C3"
COLOR_PANEL = "#FFFFFF"
COLOR_TEXT = "#1C1917"
COLOR_MUTED = "#713F12"
COLOR_BORDER = "#FEF08A"
COLOR_ACCENT = "#EAB308"
COLOR_ACCENT_PASTEL = "#FEF08A"
COLOR_ACCENT_HOVER = "#CA8A04"