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
# config.py
DATA_FILE = "data_phongkham.json"
REGEX_PHONE = r"^(0[3|5|7|8|9])+([0-9]{8})$"
REGEX_EMAIL = r"^[\w\.-]+@[\w\.-]+\.\w+$"

# Cấu hình Cloud JSONBin
JSONBIN_API_KEY = "$2a$10$YOUR_MASTER_KEY_HERE"  # Thay bằng Master Key của bạn
JSONBIN_BIN_ID = "YOUR_BIN_ID_HERE"            # Thay bằng Bin ID của bạn
# config.py
DATA_FILE = "data_phongkham.json"

# Regex kiểm tra SĐT Việt Nam (10 số) và BHYT (15 ký tự gồm 2 chữ cái đầu + 13 số/chữ)
REGEX_PHONE = r"^(0[3|5|7|8|9])+([0-9]{8})$"
REGEX_BHYT = r"^[A-Z]{2}[0-9]{13}$"
REGEX_EMAIL = r"^[\w\.-]+@[\w\.-]+\.\w+$"

# Cấu hình Cloud JSONBin (Tuỳ chọn)
JSONBIN_API_KEY = "$2a$10$YOUR_MASTER_KEY_HERE"
JSONBIN_BIN_ID = "YOUR_BIN_ID_HERE"