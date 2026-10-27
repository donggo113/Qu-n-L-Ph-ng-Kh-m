"""Đọc/ghi JSON an toàn: file thiếu/rỗng/hỏng, ghi nguyên tử, sao lưu."""
import json
import os
import shutil
from datetime import datetime
from pathlib import Path

from config import DATA_DIR, BACKUP_DIR, MAX_BACKUPS


class JsonStorage:
    def __init__(self, filename: str, data_dir: Path = DATA_DIR, backup_dir: Path = None):
        self.path = Path(data_dir) / filename
        self.backup_dir = Path(backup_dir) if backup_dir else Path(data_dir) / "backups"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> list:
        if not self.path.exists():
            return []
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                text = f.read().strip()
            if not text:
                return []
            data = json.loads(text)
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            # File hỏng: giữ lại để kiểm tra, trả về danh sách rỗng
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.move(str(self.path), str(self.path.with_suffix(f".corrupt_{stamp}")))
            return []
        except OSError:
            return []

    def save(self, items: list) -> None:
        self._backup()
        tmp = self.path.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.path)  # ghi nguyên tử, lỗi giữa chừng không mất file cũ

    def _backup(self) -> None:
        if not self.path.exists():
            return
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        shutil.copy2(self.path, self.backup_dir / f"{self.path.stem}_{stamp}.json")
        olds = sorted(self.backup_dir.glob(f"{self.path.stem}_*.json"))
        for old in olds[:-MAX_BACKUPS]:
            old.unlink(missing_ok=True)
