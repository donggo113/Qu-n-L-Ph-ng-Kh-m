"""Khởi tạo tất cả manager một chỗ để UI dùng chung."""
from services.json_storage import JsonStorage as S
from services.managers import (PatientManager, DoctorManager, SpecialtyManager,
                               ServiceManager, AppointmentManager, VisitManager)
from services.auth_manager import AuthManager


class AppContext:
    def __init__(self, data_dir=None):
        kw = {"data_dir": data_dir} if data_dir else {}
        self.patients = PatientManager(S("patients.json", **kw))
        self.doctors = DoctorManager(S("doctors.json", **kw))
        self.specialties = SpecialtyManager(S("specialties.json", **kw))
        self.services = ServiceManager(S("services.json", **kw))
        self.appointments = AppointmentManager(S("appointments.json", **kw))
        self.visits = VisitManager(S("visits.json", **kw), self.services)
        self.auth = AuthManager(S("users.json", **kw))
        self.auth.ensure_default_admin()
