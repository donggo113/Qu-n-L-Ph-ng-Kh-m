"""Cấu hình chung. Dùng đường dẫn tương đối tính từ vị trí file này."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = DATA_DIR / "backups"
MAX_BACKUPS = 5

APP_TITLE = "Quản lý phòng khám"
ROLE_ADMIN = "admin"
ROLE_STAFF = "staff"

STATUS_SCHEDULED = "scheduled"
STATUS_DONE = "done"
STATUS_CANCELLED = "cancelled"
