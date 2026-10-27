# db/models.py
import json
import urllib.request
from config import DATA_FILE, JSONBIN_API_KEY, JSONBIN_BIN_ID


class BenhNhan:
    def __init__(self, ma_id, ho_ten, tuoi, gioi_tinh, sdt, dia_chi, tien_su="Không", bhyt=""):
        self.ma_id = ma_id
        self.ho_ten = ho_ten
        self.tuoi = tuoi
        self.gioi_tinh = gioi_tinh
        self.sdt = sdt
        self.dia_chi = dia_chi
        self.tien_su = tien_su
        self.bhyt = bhyt

    def to_dict(self):
        return {
            "ma_id": self.ma_id,
            "ho_ten": self.ho_ten,
            "tuoi": self.tuoi,
            "gioi_tinh": self.gioi_tinh,
            "sdt": self.sdt,
            "dia_chi": self.dia_chi,
            "tien_su": self.tien_su,
            "bhyt": self.bhyt
        }


class BacSi:
    def __init__(self, ma_bs, ho_ten, chuyen_khoa, sdt):
        self.ma_bs = ma_bs
        self.ho_ten = ho_ten
        self.chuyen_khoa = chuyen_khoa
        self.sdt = sdt

    def to_dict(self):
        return {
            "ma_bs": self.ma_bs,
            "ho_ten": self.ho_ten,
            "chuyen_khoa": self.chuyen_khoa,
            "sdt": self.sdt
        }


class LichLamViec:
    def __init__(self, ma_ca, ten_nv, ngay, ca_lam, vai_tro="Nhân viên"):
        self.ma_ca = ma_ca
        self.ten_nv = ten_nv
        self.ngay = ngay
        self.ca_lam = ca_lam
        self.vai_tro = vai_tro

    def to_dict(self):
        return {
            "ma_ca": self.ma_ca,
            "ten_nv": self.ten_nv,
            "ngay": self.ngay,
            "ca_lam": self.ca_lam,
            "vai_tro": self.vai_tro
        }


class PhieuKhamBenh:
    def __init__(self, ma_pk, ma_bn, ho_ten_bn, bac_si, ngay_kham, trieu_chung, chan_doan, dich_vu=None, don_thuoc=None,
                 tong_tien=0, trang_thai_tt="Chờ thanh toán"):
        self.ma_pk = ma_pk
        self.ma_bn = ma_bn
        self.ho_ten_bn = ho_ten_bn
        self.bac_si = bac_si
        self.ngay_kham = ngay_kham
        self.trieu_chung = trieu_chung
        self.chan_doan = chan_doan
        self.dich_vu = dich_vu or []
        self.don_thuoc = don_thuoc or []
        self.tong_tien = tong_tien
        self.trang_thai_tt = trang_thai_tt

    def to_dict(self):
        return self.__dict__


class QuanLyPhongKham:
    def __init__(self):
        self.danh_sach_benh_nhan = []
        self.danh_sach_bac_si = []
        self.danh_sach_dich_vu = []
        self.danh_sach_phieu_kham = []
        self.danh_sach_lich_kham = []
        self.danh_sach_thuoc = []
        self.danh_sach_lich_lam = []
        self.load_from_json()

    def kiem_tra_trung_lich_bac_si(self, ma_bs, ngay_kham, gio_kham):
        """Thuật toán tự động chặn nếu Bác sĩ đã có lịch trùng giờ và ngày"""
        for lk in self.danh_sach_lich_kham:
            lk_ma_bs = lk.get("ma_bs") if isinstance(lk, dict) else getattr(lk, 'ma_bs', '')
            lk_ngay = lk.get("ngay_kham") if isinstance(lk, dict) else getattr(lk, 'ngay_kham', '')
            lk_gio = lk.get("gio_kham") if isinstance(lk, dict) else getattr(lk, 'gio_kham', '')

            if lk_ma_bs == ma_bs and lk_ngay == ngay_kham and lk_gio == gio_kham:
                return True
        return False

    def luu_phieu_kham(self, phieu_kham):
        self.danh_sach_phieu_kham.append(phieu_kham)
        # Trừ kho thuốc khi kê đơn
        if hasattr(phieu_kham, 'don_thuoc') and phieu_kham.don_thuoc:
            for item in phieu_kham.don_thuoc:
                ma_t = item.get("ma_thuoc")
                sl_ke = item.get("so_luong", 0)
                for t in self.danh_sach_thuoc:
                    ma_curr = t.get("ma_thuoc") if isinstance(t, dict) else getattr(t, 'ma_thuoc', None)
                    if ma_curr == ma_t:
                        if isinstance(t, dict):
                            t["so_luong"] = max(0, t.get("so_luong", 0) - sl_ke)
                        else:
                            t.so_luong = max(0, getattr(t, 'so_luong', 0) - sl_ke)
                        break
        self.save_to_json()

    def save_to_json(self):
        data = {
            "benh_nhan": [bn.to_dict() if hasattr(bn, 'to_dict') else bn for bn in self.danh_sach_benh_nhan],
            "bac_si": [bs.to_dict() if hasattr(bs, 'to_dict') else bs for bs in self.danh_sach_bac_si],
            "dich_vu": [dv.to_dict() if hasattr(dv, 'to_dict') else dv for dv in self.danh_sach_dich_vu],
            "phieu_kham": [pk.to_dict() if hasattr(pk, 'to_dict') else pk for pk in self.danh_sach_phieu_kham],
            "lich_kham": [lk.to_dict() if hasattr(lk, 'to_dict') else lk for lk in self.danh_sach_lich_kham],
            "thuoc": [t.to_dict() if hasattr(t, 'to_dict') else t for t in self.danh_sach_thuoc],
            "lich_lam": [ll.to_dict() if hasattr(ll, 'to_dict') else ll for ll in self.danh_sach_lich_lam]
        }
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print("[SAVE JSON ERROR]:", e)

    def load_from_json(self):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

                # Nạp và ép kiểu tự động Bệnh nhân thành BenhNhan Object
                self.danh_sach_benh_nhan = []
                for bn in data.get("benh_nhan", []):
                    if isinstance(bn, dict):
                        self.danh_sach_benh_nhan.append(BenhNhan(
                            ma_id=bn.get("ma_id", ""),
                            ho_ten=bn.get("ho_ten", ""),
                            tuoi=bn.get("tuoi", 0),
                            gioi_tinh=bn.get("gioi_tinh", "Nam"),
                            sdt=bn.get("sdt", ""),
                            dia_chi=bn.get("dia_chi", ""),
                            tien_su=bn.get("tien_su", "Không"),
                            bhyt=bn.get("bhyt", "")
                        ))
                    else:
                        self.danh_sach_benh_nhan.append(bn)

                self.danh_sach_bac_si = data.get("bac_si", [
                    {"ma_bs": "BS001", "ho_ten": "BS. Nguyễn Văn A", "chuyen_khoa": "Nội Khoa", "sdt": "0912345678"},
                    {"ma_bs": "BS002", "ho_ten": "BS. Trần Thị B", "chuyen_khoa": "Tai Mũi Họng", "sdt": "0987654321"}
                ])
                self.danh_sach_dich_vu = data.get("dich_vu", [])

                # Nạp Phiếu khám
                self.danh_sach_phieu_kham = []
                for pk in data.get("phieu_kham", []):
                    if isinstance(pk, dict):
                        self.danh_sach_phieu_kham.append(PhieuKhamBenh(**pk))
                    else:
                        self.danh_sach_phieu_kham.append(pk)

                self.danh_sach_lich_kham = data.get("lich_kham", [])
                self.danh_sach_thuoc = data.get("thuoc", [])
                self.danh_sach_lich_lam = data.get("lich_lam", [])
        except Exception as e:
            print("[LOAD JSON LOG]: Khởi tạo hoặc đọc dữ liệu mặc định:", e)