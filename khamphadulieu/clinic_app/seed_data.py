"""Tạo dữ liệu mẫu: python seed_data.py (chỉ chạy khi data còn trống)."""
from services.app_context import AppContext
from models.person import Patient, Doctor
from models.simple_models import Specialty, Service, Appointment, Visit


def main():
    ctx = AppContext()
    if ctx.patients.items:
        print("Đã có dữ liệu, bỏ qua.")
        return
    ck = ctx.specialties.add(Specialty(None, "Nội tổng quát"))
    ctx.specialties.add(Specialty(None, "Nhi"))
    ctx.doctors.add(Doctor(None, "Nguyễn Văn An", "0901234567", "1980-05-12", ck.id))
    ctx.patients.add(Patient(None, "Trần Thị Bình", "0912345678", "1995-03-20",
                             "HC4010000000001", "TP. Hồ Chí Minh"))
    s1 = ctx.services.add(Service(None, "Khám tổng quát", 150000))
    s2 = ctx.services.add(Service(None, "Xét nghiệm máu", 220000))
    ap = ctx.appointments.add(Appointment(None, "BN001", "BS001", "2026-10-26", "08:00", "08:30"))
    ctx.visits.add(Visit(None, ap.id, "Cảm cúm", [s1.id, s2.id], date="2026-10-26"))
    print("Đã tạo dữ liệu mẫu. Tài khoản: admin / admin123")


if __name__ == "__main__":
    main()
