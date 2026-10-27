"""Các manager cụ thể + kiểm tra trùng lịch."""
from config import STATUS_CANCELLED
from models.person import Patient, Doctor
from models.simple_models import Specialty, Service, Appointment, Visit
from services.base_manager import BaseManager
from utils import validators as v


class PatientManager(BaseManager):
    PREFIX, MODEL = "BN", Patient

    def validate(self, p):
        if not v.is_valid_name(p.name):
            raise ValueError("Họ tên không hợp lệ")
        if not v.is_valid_phone(p.phone):
            raise ValueError("Số điện thoại không hợp lệ")
        if not v.is_valid_date(p.dob):
            raise ValueError("Ngày sinh không hợp lệ (YYYY-MM-DD)")
        if p.insurance_code and not v.is_valid_insurance(p.insurance_code):
            raise ValueError("Mã BHYT không hợp lệ")


class DoctorManager(BaseManager):
    PREFIX, MODEL = "BS", Doctor

    def validate(self, d):
        if not v.is_valid_name(d.name):
            raise ValueError("Họ tên không hợp lệ")
        if not v.is_valid_phone(d.phone):
            raise ValueError("Số điện thoại không hợp lệ")
        if not v.is_valid_date(d.dob):
            raise ValueError("Ngày sinh không hợp lệ (YYYY-MM-DD)")


class SpecialtyManager(BaseManager):
    PREFIX, MODEL = "CK", Specialty


class ServiceManager(BaseManager):
    PREFIX, MODEL = "DV", Service

    def validate(self, s):
        if not str(s.name).strip():
            raise ValueError("Tên dịch vụ không được trống")
        if not isinstance(s.price, (int, float)) or s.price < 0:
            raise ValueError("Giá dịch vụ phải là số không âm")


class AppointmentManager(BaseManager):
    PREFIX, MODEL = "LH", Appointment

    def validate(self, a):
        if not v.is_valid_date(a.date):
            raise ValueError("Ngày hẹn không hợp lệ")
        if not (v.is_valid_time(a.start) and v.is_valid_time(a.end)):
            raise ValueError("Giờ không hợp lệ (HH:MM)")
        if v.time_to_minutes(a.start) >= v.time_to_minutes(a.end):
            raise ValueError("Giờ bắt đầu phải trước giờ kết thúc")
        if self.has_conflict(a):
            raise ValueError("Bác sĩ đã có lịch trùng khung giờ này")

    def has_conflict(self, a) -> bool:
        """Trùng khi cùng bác sĩ, cùng ngày, và start1 < end2 and start2 < end1.
        Bỏ qua lịch đã hủy và chính lịch đang sửa."""
        if a.status == STATUS_CANCELLED:
            return False
        s1, e1 = v.time_to_minutes(a.start), v.time_to_minutes(a.end)
        for o in self.items:
            if o.id == a.id or o.status == STATUS_CANCELLED:
                continue
            if o.doctor_id != a.doctor_id or o.date != a.date:
                continue
            s2, e2 = v.time_to_minutes(o.start), v.time_to_minutes(o.end)
            if s1 < e2 and s2 < e1:
                return True
        return False


class VisitManager(BaseManager):
    PREFIX, MODEL = "PK", Visit

    def __init__(self, storage, service_manager: ServiceManager):
        super().__init__(storage)
        self.service_manager = service_manager

    def calc_total(self, service_ids) -> float:
        total = 0
        for sid in service_ids:
            s = self.service_manager.get(sid)
            if s:
                total += s.price
        return total

    def validate(self, visit):
        visit.total = self.calc_total(visit.service_ids)
