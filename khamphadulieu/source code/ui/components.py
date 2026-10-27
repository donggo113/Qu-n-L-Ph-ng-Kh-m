# components.py
import tkinter as tk
from tkinter import ttk, messagebox
from .theme import BG, PANEL, ACCENT
from db.models import QuanLyPhongKham, BenhNhan
from utils import validate_phone, validate_email

class DataView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.quan_ly = QuanLyPhongKham()

        top_bar = tk.Frame(self, bg=PANEL, padx=10, pady=10)
        top_bar.pack(fill="x")

        tk.Label(top_bar, text="QUẢN LÝ DANH SÁCH BỆNH NHÂN", bg=PANEL, fg=ACCENT, font=("Segoe UI", 11, "bold")).pack(side="left")

        ttk.Button(top_bar, text="📜 Xem Lịch Sử Khám", command=self.xem_lich_su_kham).pack(side="right", padx=5)
        ttk.Button(top_bar, text="🔄 Tải lại", command=self.load_data).pack(side="right", padx=5)

        # KHU VỰC TÌM KIẾM THEO 2 TIÊU CHÍ (Mã / Tên / SĐT)
        search_frame = tk.Frame(self, bg=BG, padx=10, pady=8)
        search_frame.pack(fill="x")

        tk.Label(search_frame, text="🔍 Tìm kiếm (Mã/Tên/SĐT):", bg=BG, font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 5))
        self.ent_search = ttk.Entry(search_frame, width=30)
        self.ent_search.pack(side="left", padx=5)
        self.ent_search.bind("<KeyRelease>", self.thuc_hien_tim_kiem)

        ttk.Button(search_frame, text="Xóa tìm", command=self.xoa_tim_kiem).pack(side="left", padx=2)
        ttk.Button(search_frame, text="➕ Thêm BN", command=self.them_benh_nhan).pack(side="right", padx=3)
        ttk.Button(search_frame, text="🗑️ Xóa BN", command=self.xoa_benh_nhan).pack(side="right", padx=3)

        # Bảng hiển thị
        cols = ("Mã BN", "Họ tên", "Số điện thoại", "Giới tính", "Email", "Địa chỉ")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.load_data()

    def load_data(self):
        self.quan_ly.load_from_json()
        self.hien_thi_danh_sach(self.quan_ly.danh_sach_benh_nhan)

    def hien_thi_danh_sach(self, ds_benh_nhan):
        self.tree.delete(*self.tree.get_children())
        for bn in ds_benh_nhan:
            self.tree.insert("", "end", values=(bn.ma_id, bn.ho_ten, bn.sdt, bn.gioi_tinh, bn.email, bn.dia_chi))

    def thuc_hien_tim_kiem(self, event=None):
        tu_khoa = self.ent_search.get().strip().lower()
        if not tu_khoa:
            self.hien_thi_danh_sach(self.quan_ly.danh_sach_benh_nhan)
            return

        ds_ket_qua = [
            bn for bn in self.quan_ly.danh_sach_benh_nhan
            if tu_khoa in bn.ma_id.lower()
            or tu_khoa in bn.ho_ten.lower()
            or tu_khoa in bn.sdt.lower()
        ]
        self.hien_thi_danh_sach(ds_ket_qua)

    def xoa_tim_kiem(self):
        self.ent_search.delete(0, tk.END)
        self.hien_thi_danh_sach(self.quan_ly.danh_sach_benh_nhan)

    def them_benh_nhan(self):
        win = tk.Toplevel(self)
        win.title("Thêm Bệnh Nhân Mới")
        win.geometry("380x320")

        tk.Label(win, text="Mã BN:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ent_ma = ttk.Entry(win)
        ent_ma.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(win, text="Họ tên:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        ent_ten = ttk.Entry(win)
        ent_ten.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(win, text="SĐT:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        ent_sdt = ttk.Entry(win)
        ent_sdt.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(win, text="Email:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        ent_email = ttk.Entry(win)
        ent_email.grid(row=3, column=1, padx=10, pady=5)

        def luu():
            ma, ten, sdt, email = ent_ma.get().strip(), ent_ten.get().strip(), ent_sdt.get().strip(), ent_email.get().strip()
            if not ma or not ten:
                messagebox.showwarning("Lỗi", "Mã và Tên không được để trống!", parent=win)
                return
            if sdt and not validate_phone(sdt):
                messagebox.showwarning("Lỗi Regex", "Số điện thoại không đúng định dạng VN!", parent=win)
                return
            if email and not validate_email(email):
                messagebox.showwarning("Lỗi Regex", "Email không đúng định dạng!", parent=win)
                return

            bn = BenhNhan(ma, ten, sdt, "2000-01-01", "Nam", "Việt Nam", email)
            self.quan_ly.them_benh_nhan(bn)
            self.load_data()
            win.destroy()
            messagebox.showinfo("Thành công", f"Đã thêm bệnh nhân {ten}!")

        ttk.Button(win, text="Lưu Bệnh Nhân", command=luu).grid(row=4, column=0, columnspan=2, pady=15)

    def xoa_benh_nhan(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Chú ý", "Vui lòng chọn bệnh nhân cần xóa!")
            return
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa bệnh nhân này không?"):
            ma_bn = self.tree.item(selected[0])["values"][0]
            self.quan_ly.danh_sach_benh_nhan = [bn for bn in self.quan_ly.danh_sach_benh_nhan if bn.ma_id != ma_bn]
            self.quan_ly.save_to_json()
            self.load_data()

    def xem_lich_su_kham(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Chú ý", "Vui lòng chọn 1 bệnh nhân để xem lịch sử khám!")
            return

        item = self.tree.item(selected[0])["values"]
        ma_bn, ho_ten = item[0], item[1]
        history = self.quan_ly.lay_lich_su_kham(ma_bn)

        win = tk.Toplevel(self)
        win.title(f"Lịch sử khám - {ho_ten}")
        win.geometry("650x400")

        if not history:
            tk.Label(win, text="Chưa có lịch sử khám bệnh!", fg="gray").pack(pady=20)
            return

        text = tk.Text(win, padx=10, pady=10)
        text.pack(fill="both", expand=True)
        for pk in history:
            text.insert("end", f"Ngày: {pk.ngay_kham} | Bác sĩ: {pk.bac_si}\nChẩn đoán: {pk.chan_doan}\nTong tiền: {pk.tong_tien:,} VNĐ\n" + "-"*50 + "\n")
        text.config(state="disabled")