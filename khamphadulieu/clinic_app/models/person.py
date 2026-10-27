"""Lớp cha Person và hai lớp con Patient, Doctor (kế thừa + đa hình)."""


class Person:
    def __init__(self, id, name, phone, dob):
        self.id = id
        self.name = name
        self.phone = phone
        self.dob = dob  # YYYY-MM-DD

    def describe(self) -> str:
        return f"{self.name} - {self.phone}"

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "phone": self.phone, "dob": self.dob}


class Patient(Person):
    def __init__(self, id, name, phone, dob, insurance_code="", address=""):
        super().__init__(id, name, phone, dob)
        self.insurance_code = insurance_code
        self.address = address

    def describe(self) -> str:  # ghi đè (đa hình)
        bhyt = self.insurance_code or "không có BHYT"
        return f"Bệnh nhân {self.name} ({bhyt})"

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({"insurance_code": self.insurance_code, "address": self.address})
        return d

    @classmethod
    def from_dict(cls, d: dict):
        return cls(d["id"], d["name"], d["phone"], d["dob"],
                   d.get("insurance_code", ""), d.get("address", ""))


class Doctor(Person):
    def __init__(self, id, name, phone, dob, specialty_id=""):
        super().__init__(id, name, phone, dob)
        self.specialty_id = specialty_id

    def describe(self) -> str:  # ghi đè (đa hình)
        return f"BS. {self.name} (chuyên khoa {self.specialty_id})"

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["specialty_id"] = self.specialty_id
        return d

    @classmethod
    def from_dict(cls, d: dict):
        return cls(d["id"], d["name"], d["phone"], d["dob"], d.get("specialty_id", ""))
