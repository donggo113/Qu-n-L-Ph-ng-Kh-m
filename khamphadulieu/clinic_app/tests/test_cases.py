"""Chạy: python -m unittest discover -s tests -v (từ thư mục clinic_app)."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models.person import Patient
from models.simple_models import Appointment, Service, Visit
from services.app_context import AppContext
from services.json_storage import JsonStorage
from utils import validators as v


class TestValidators(unittest.TestCase):
    def test_phone(self):
        self.assertTrue(v.is_valid_phone("0901234567"))       # hợp lệ
        self.assertTrue(v.is_valid_phone("+84901234567"))
        self.assertFalse(v.is_valid_phone("0101234567"))      # đầu số sai
        self.assertFalse(v.is_valid_phone("090123456"))       # thiếu số (biên)

    def test_insurance(self):
        self.assertTrue(v.is_valid_insurance("HC4010000000001"))
        self.assertFalse(v.is_valid_insurance("HC401"))

    def test_date(self):
        self.assertTrue(v.is_valid_date("2024-02-29"))
        self.assertFalse(v.is_valid_date("2025-02-30"))
        self.assertFalse(v.is_valid_date("30/02/2025"))


class TestStorage(unittest.TestCase):
    def test_missing_empty_corrupt(self):
        with tempfile.TemporaryDirectory() as d:
            s = JsonStorage("a.json", data_dir=d)
            self.assertEqual(s.load(), [])                    # file chưa có
            s.path.write_text("", encoding="utf-8")
            self.assertEqual(s.load(), [])                    # file rỗng
            s.path.write_text("{hỏng", encoding="utf-8")
            self.assertEqual(s.load(), [])                    # JSON sai


class TestManagers(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ctx = AppContext(data_dir=Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def test_patient_crud_search(self):
        p = self.ctx.patients.add(Patient(None, "Lê Văn Cường", "0912345678", "1990-01-01"))
        self.assertEqual(p.id, "BN001")
        self.assertEqual(len(self.ctx.patients.search("cường")), 1)
        self.assertTrue(self.ctx.patients.delete(p.id))
        with self.assertRaises(ValueError):
            self.ctx.patients.add(Patient(None, "Lê Văn Cường", "abc", "1990-01-01"))

    def test_conflict(self):
        am = self.ctx.appointments
        am.add(Appointment(None, "BN001", "BS001", "2026-10-26", "08:00", "09:00"))
        with self.assertRaises(ValueError):                   # giao nhau
            am.add(Appointment(None, "BN002", "BS001", "2026-10-26", "08:30", "09:30"))
        am.add(Appointment(None, "BN002", "BS001", "2026-10-26", "09:00", "10:00"))  # biên: liền kề OK
        am.add(Appointment(None, "BN002", "BS002", "2026-10-26", "08:30", "09:30"))  # bác sĩ khác OK

    def test_edit_self_not_conflict(self):
        am = self.ctx.appointments
        a = am.add(Appointment(None, "BN001", "BS001", "2026-10-26", "08:00", "09:00"))
        a.end = "09:30"
        am.update(a)                                          # không tự trùng chính mình

    def test_visit_total_and_auth(self):
        s = self.ctx.services.add(Service(None, "Khám", 100000))
        vs = self.ctx.visits.add(Visit(None, "LH001", "Ho", [s.id, s.id], date="2026-10-26"))
        self.assertEqual(vs.total, 200000)
        self.ctx.auth.register("le_tan", "matkhau1", "staff")
        self.assertIsNotNone(self.ctx.auth.login("le_tan", "matkhau1"))
        self.assertIsNone(self.ctx.auth.login("le_tan", "saimatkhau"))
        self.assertIsNotNone(self.ctx.auth.login("admin", "admin123"))


if __name__ == "__main__":
    unittest.main()
