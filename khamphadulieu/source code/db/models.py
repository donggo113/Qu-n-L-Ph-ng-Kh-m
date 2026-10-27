# db/models.py
from abc import ABC, abstractmethod
import json
import os
import shutil
import csv
from config import DATA_FILE, BACKUP_FILE, EXPORT_CSV
from utils import crawl_external_medical_services

class Nguoi(ABC):
    def __init__(self, ma_id: str, ho_ten: str, sdt: str):
        self._ma_id = ma_id
        self._ho_ten = ho_ten
        self.__sdt = sdt

    @property
    def ma_id(self): return self._ma_id
    @property
    def ho_ten(self): return self._ho_ten
    @property
    def sdt(self): return self.__sdt

    @abstractmethod
    def lay_thong_tin(self) -> str: pass

class BenhNhan(Nguoi):
    def __init__(self, ma_bn: str, ho_ten: str, sdt: str, ngay_sinh: str, gioi_tinh: str, dia_chi: str = "", email: str = ""):
        super().__init__(ma_bn, ho_ten, sdt)
        self.ngay_sinh = ngay_sinh
        self.gioi_tinh = gioi_tinh
        self.dia_chi = dia_chi
        self.email = email

    def lay_thong_tin(self) -> str:
        return f"Bệnh nhân [{self.ma_id}] {self.ho_ten} - SĐT: {self.sdt}"

    def to_dict(self) -> dict:
        return {
            "ma_bn": self.ma_id, "ho_ten": self.ho_ten, "sdt": self.sdt,
            "ngay_sinh": self.ngay_sinh, "gioi_tinh": self.gioi_tinh,
            "dia_chi": self.dia_chi, "email": self.email
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            ma_bn=data.get("ma_bn", ""), ho_ten=data.get("ho_ten", ""), sdt=data.get("sdt", ""),
            ngay_sinh=data.get("ngay_sinh", ""), gioi_tinh=data.get("gioi_tinh", "Nam"),
            dia_chi=data.get("dia_chi", ""), email=data.get("email", "")
        )

class LichKham:
    def __init__(self, ma_lich: str, ma_bn: str, ho_ten_bn: str, bac_si: str, ngay_kham: str, gio_kham: str, ly_do: str = "Khám bệnh", trang_thai: str = "Chờ khám"):
        self.ma_lich = ma_lich
        self.ma_bn = ma_bn
        self.ho_ten_bn = ho_ten_bn
        self.bac_si = bac_si
        self.ngay_kham = ngay_kham
        self.gio_kham = gio_kham
        self.ly_do = ly_do
        self.trang_thai = trang_thai

    def to_dict(self) -> dict:
        return {
            "ma_lich": self.ma_lich, "ma_bn": self.ma_bn, "ho_ten_bn": self.ho_ten_bn,
            "bac_si": self.bac_si, "ngay_kham": self.ngay_kham, "gio_kham": self.gio_kham,
            "ly_do": self.ly_do, "trang_thai": self.trang_thai
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            ma_lich=data.get("ma_lich", ""), ma_bn=data.get("ma_bn", ""),
            ho_ten_bn=data.get("ho_ten_bn", ""), bac_si=data.get("bac_si", "BS. Nguyễn Văn A"),
            ngay_kham=data.get("ngay_kham", ""), gio_kham=data.get("gio_kham", ""),
            ly_do=data.get("ly_do", "Khám bệnh"), trang_thai=data.get("trang_thai", "Chờ khám")
        )

class PhieuKhamBenh:
    def __init__(self, ma_pk: str, ma_bn: str, ho_ten_bn: str, bac_si: str, ngay_kham: str,
                 trieu_chung: str, chan_doan: str, dich_vu: list, don_thuoc: list,
                 tong_tien: float, trang_thai_tt: str = "Đã thanh toán"):
        self.ma_pk = ma_pk
        self.ma_bn = ma_bn
        self.ho_ten_bn = ho_ten_bn
        self.bac_si = bac_si
        self.ngay_kham = ngay_kham
        self.trieu_chung = trieu_chung
        self.chan_doan = chan_doan
        self.dich_vu = dich_vu
        self.don_thuoc = don_thuoc
        self.tong_tien = tong_tien
        self.trang_thai_tt = trang_thai_tt

    def to_dict(self) -> dict:
        return {
            "ma_pk": self.ma_pk, "ma_bn": self.ma_bn, "ho_ten_bn": self.ho_ten_bn,
            "bac_si": self.bac_si, "ngay_kham": self.ngay_kham, "trieu_chung": self.trieu_chung,
            "chan_doan": self.chan_doan, "dich_vu": self.dich_vu, "don_thuoc": self.don_thuoc,
            "tong_tien": self.tong_tien, "trang_thai_tt": self.trang_thai_tt
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            ma_pk=data.get("ma_pk", ""), ma_bn=data.get("ma_bn", ""),
            ho_ten_bn=data.get("ho_ten_bn", ""), bac_si=data.get("bac_si", ""),
            ngay_kham=data.get("ngay_kham", ""), trieu_chung=data.get("trieu_chung", ""),
            chan_doan=data.get("chan_doan", ""), dich_vu=data.get("dich_vu", []),
            don_thuoc=data.get("don_thuoc", []), tong_tien=data.get("tong_tien", 0),
            trang_thai_tt=data.get("trang_thai_tt", "Đã thanh toán")
        )

class Thuoc:
    def __init__(self, ma_thuoc: str, ten_thuoc: str, don_vi: str, don_gia: float, so_luong_ton: int):
        self.ma_thuoc = ma_thuoc
        self.ten_thuoc = ten_thuoc
        self.don_vi = don_vi
        self.don_gia = don_gia
        self.so_luong_ton = so_luong_ton

    def to_dict(self):
        return {
            "ma_thuoc": self.ma_thuoc, "ten_thuoc": self.ten_thuoc,
            "don_vi": self.don_vi, "don_gia": self.don_gia, "so_luong_ton": self.so_luong_ton
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            ma_thuoc=data.get("ma_thuoc", ""), ten_thuoc=data.get("ten_thuoc", ""),
            don_vi=data.get("don_vi", "Hộp"), don_gia=data.get("don_gia", 0),
            so_luong_ton=data.get("so_luong_ton", 0)
        )

class LichLamViec:
    def __init__(self, ma_nv: str, ten_nv: str, ngay: str, ca_lam: str, trang_thai: str = "Chờ duyệt"):
        self.ma_nv = ma_nv
        self.ten_nv = ten_nv
        self.ngay = ngay
        self.ca_lam = ca_lam
        self.trang_thai = trang_thai

    def to_dict(self):
        return {
            "ma_nv": self.ma_nv, "ten_nv": self.ten_nv,
            "ngay": self.ngay, "ca_lam": self.ca_lam, "trang_thai": self.trang_thai
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            ma_nv=data.get("ma_nv", ""), ten_nv=data.get("ten_nv", ""),
            ngay=data.get("ngay", ""), ca_lam=data.get("ca_lam", "Sáng"),
            trang_thai=data.get("trang_thai", "Chờ duyệt")
        )

class QuanLyPhongKham:
    def __init__(self, data_file: str = DATA_FILE):
        self.data_file = data_file
        self.danh_sach_benh_nhan: list[BenhNhan] = []
        self.danh_sach_lich_kham: list[LichKham] = []
        self.danh_sach_phieu_kham: list[PhieuKhamBenh] = []
        self.danh_sach_dich_vu: list[dict] = []
        self.danh_sach_thuoc: list[Thuoc] = []
        self.danh_sach_lich_lam: list[LichLamViec] = []
        self.load_from_json()

    def save_to_json(self):
        dir_name = os.path.dirname(self.data_file)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        if os.path.exists(self.data_file):
            shutil.copy(self.data_file, BACKUP_FILE)

        payload = {
            "benh_nhan": [bn.to_dict() for bn in self.danh_sach_benh_nhan],
            "lich_kham": [lk.to_dict() for lk in self.danh_sach_lich_kham],
            "phieu_kham": [pk.to_dict() for pk in self.danh_sach_phieu_kham],
            "dich_vu": self.danh_sach_dich_vu,
            "thuoc": [t.to_dict() for t in self.danh_sach_thuoc],
            "lich_lam": [l.to_dict() for l in self.danh_sach_lich_lam]
        }
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=4)

    def load_from_json(self):
        if not os.path.exists(self.data_file):
            self._init_default_data()
            self.save_to_json()
            return

        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    raise ValueError("File rỗng!")
                data = json.loads(content)
                self.danh_sach_benh_nhan = [BenhNhan.from_dict(d) for d in data.get("benh_nhan", [])]
                self.danh_sach_lich_kham = [LichKham.from_dict(d) for d in data.get("lich_kham", [])]
                self.danh_sach_phieu_kham = [PhieuKhamBenh.from_dict(d) for d in data.get("phieu_kham", [])]
                self.danh_sach_dich_vu = data.get("dich_vu", [])
                self.danh_sach_thuoc = [Thuoc.from_dict(d) for d in data.get("thuoc", [])]
                self.danh_sach_lich_lam = [LichLamViec.from_dict(d) for d in data.get("lich_lam", [])]
                if not self.danh_sach_dich_vu:
                    self.fetch_and_save_services()
        except Exception:
            self._init_default_data()

    def fetch_and_save_services(self):
        self.danh_sach_dich_vu = crawl_external_medical_services()
        self.save_to_json()

    def _init_default_data(self):
        self.danh_sach_benh_nhan = [
            BenhNhan("BN001", "Nguyễn Văn An", "0901234567", "1990-05-12", "Nam", "TP. Hồ Chí Minh", "an.nguyen@gmail.com"),
            BenhNhan("BN002", "Trần Thị Bích", "0987654321", "1995-08-20", "Nữ", "Hà Nội", "bich.tran@gmail.com")
        ]
        self.danh_sach_lich_kham = [
            LichKham("LK001", "BN001", "Nguyễn Văn An", "BS. Nguyễn Văn A", "2026-10-27", "08:00", "Khám định kỳ", "Chờ khám"),
            LichKham("LK002", "BN002", "Trần Thị Bích", "BS. Trần Thị B", "2026-10-27", "09:30", "Đau dạ dày", "Chờ khám")
        ]
        self.danh_sach_thuoc = [
            Thuoc("T001", "Paracetamol 500mg", "Hộp", 35000, 100),
            Thuoc("T002", "Amoxicillin 500mg", "Vỉ", 25000, 50)
        ]
        self.danh_sach_lich_lam = [
            LichLamViec("admin", "Admin", "2026-10-28", "Sáng (07:30 - 11:30)", "Đã duyệt")
        ]

    def dat_lich_kham(self, lk: LichKham):
        self.danh_sach_lich_kham.append(lk)
        self.save_to_json()

    def them_benh_nhan(self, bn: BenhNhan):
        for item in self.danh_sach_benh_nhan:
            if item.ma_id == bn.ma_id:
                return
        self.danh_sach_benh_nhan.append(bn)
        self.save_to_json()

    def luu_phieu_kham(self, pk: PhieuKhamBenh):
        self.danh_sach_phieu_kham.append(pk)
        for lk in self.danh_sach_lich_kham:
            if lk.ma_bn == pk.ma_bn and lk.ngay_kham == pk.ngay_kham:
                lk.trang_thai = "Đã khám"
        self.save_to_json()

    def lay_lich_su_kham(self, ma_bn: str) -> list[PhieuKhamBenh]:
        return [pk for pk in self.danh_sach_phieu_kham if pk.ma_bn == ma_bn]