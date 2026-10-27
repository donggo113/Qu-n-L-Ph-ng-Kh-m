"""Specialty, Service, Appointment, Visit, User."""
from config import STATUS_SCHEDULED


class _Base:
    FIELDS = ()

    def to_dict(self) -> dict:
        return {f: getattr(self, f) for f in self.FIELDS}

    @classmethod
    def from_dict(cls, d: dict):
        return cls(**{f: d.get(f) for f in cls.FIELDS})


class Specialty(_Base):
    FIELDS = ("id", "name")

    def __init__(self, id, name):
        self.id, self.name = id, name


class Service(_Base):
    FIELDS = ("id", "name", "price")

    def __init__(self, id, name, price):
        self.id, self.name, self.price = id, name, price


class Appointment(_Base):
    FIELDS = ("id", "patient_id", "doctor_id", "date", "start", "end", "status", "note")

    def __init__(self, id, patient_id, doctor_id, date, start, end,
                 status=STATUS_SCHEDULED, note=""):
        self.id, self.patient_id, self.doctor_id = id, patient_id, doctor_id
        self.date, self.start, self.end = date, start, end
        self.status, self.note = status or STATUS_SCHEDULED, note or ""


class Visit(_Base):
    """Phiếu khám: chứa danh sách mã dịch vụ và tổng tiền."""
    FIELDS = ("id", "appointment_id", "diagnosis", "service_ids", "total", "date")

    def __init__(self, id, appointment_id, diagnosis, service_ids=None, total=0, date=""):
        self.id, self.appointment_id, self.diagnosis = id, appointment_id, diagnosis
        self.service_ids = list(service_ids or [])
        self.total, self.date = total or 0, date


class User(_Base):
    FIELDS = ("id", "username", "password_hash", "salt", "role")

    def __init__(self, id, username, password_hash, salt, role):
        self.id, self.username = id, username
        self.password_hash, self.salt, self.role = password_hash, salt, role
