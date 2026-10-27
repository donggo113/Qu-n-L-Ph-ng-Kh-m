"""Tài khoản: mật khẩu băm PBKDF2 + salt, phân quyền theo role."""
import hashlib
import hmac
import os

from config import ROLE_ADMIN, ROLE_STAFF
from models.simple_models import User
from services.base_manager import BaseManager

ITERATIONS = 120_000


def hash_password(password: str, salt_hex: str = None):
    salt = bytes.fromhex(salt_hex) if salt_hex else os.urandom(16)
    h = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    return h.hex(), salt.hex()


class AuthManager(BaseManager):
    PREFIX, MODEL = "US", User

    def find(self, username):
        return next((u for u in self.items if u.username == username), None)

    def register(self, username, password, role=ROLE_STAFF):
        if not username or len(password) < 6:
            raise ValueError("Tên đăng nhập trống hoặc mật khẩu dưới 6 ký tự")
        if role not in (ROLE_ADMIN, ROLE_STAFF):
            raise ValueError("Vai trò không hợp lệ")
        if self.find(username):
            raise ValueError("Tên đăng nhập đã tồn tại")
        pw_hash, salt = hash_password(password)
        return self.add(User(None, username, pw_hash, salt, role))

    def login(self, username, password):
        """Trả về User nếu đúng, None nếu sai."""
        u = self.find(username)
        if not u:
            return None
        pw_hash, _ = hash_password(password, u.salt)
        return u if hmac.compare_digest(pw_hash, u.password_hash) else None

    def ensure_default_admin(self):
        if not self.items:
            self.register("admin", "admin123", ROLE_ADMIN)  # đổi mật khẩu khi demo!

    @staticmethod
    def can_delete(user) -> bool:
        return user.role == ROLE_ADMIN

    @staticmethod
    def can_view_stats(user) -> bool:
        return user.role == ROLE_ADMIN
