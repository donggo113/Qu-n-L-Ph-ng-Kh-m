# ui/phanlichlam.py
import tkinter as tk
from tkinter import ttk, messagebox
from .theme import BG, PANEL, ACCENT
from db.models import QuanLyPhongKham, LichLamViec

class ShiftManagementView(tk.Frame):
    def __init__(self, parent, username="admin", role="admin"):
        super().__init__(parent, bg=BG)
        self.quan_ly = QuanLyPhongKham()
        self.username = username
        self.role = role
        self.setup_ui()

    def setup_ui(self):
        top_bar = tk.Frame(self, bg=PANEL, padx=10, pady=10)
        top_bar.pack(fill="x")
        title = "XẾP LỊCH LÀM VIỆC (QUẢN TRỊ)" if self.role == "admin" else "ĐĂNG KÝ CA LÀM VIỆC"
        tk.Label(top_bar, text=title, bg=PANEL, fg=ACCENT, font=("Segoe UI", 12, "bold")).pack(side="left")

        # Form Đăng ký cho Nhân viên
        box_form = tk.LabelFrame(self, text=" Đăng ký ca làm ", bg=PANEL, fg="#854D0E", font=("Segoe UI", 9, "bold"))
        box_form.pack(fill="x", padx=10, pady=10, ipadx=5, ipady=5)

        grid = tk.Frame(box_form, bg=PANEL)
        grid.pack(fill="x", padx=5, pady=5)

        tk.Label(grid, text="Mã NV/Tên:", bg=PANEL).grid(row=0, column=0, sticky="w")
        self.ent_nv = ttk.Entry(grid, width=20)
        self.ent_nv.insert(0, self.username)
        self.ent_nv.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(grid, text="Ngày làm (YYYY-MM-DD):", bg=PANEL).grid(row=0, column=2, sticky="w")
        self.ent_ngay = ttk.Entry(grid, width=15)
        self.ent_ngay.insert(0, "2026-10-28")
        self.ent_ngay.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(grid, text="Ca làm:", bg=PANEL).grid(row=0, column=4, sticky="w")
        self.cbo_ca = ttk.Combobox(grid, values=["Sáng (07:30 - 11:30)", "Chiều (13:00 - 17:00)", "Tối (17:00 - 21:00)"], width=22, state="readonly")
        self.cbo_ca.set("Sáng (07:30 - 11:30)")
        self.cbo_ca.grid(row=0, column=5, padx=5, pady=5)

        ttk.Button(box_form, text="📝 Đăng ký ca", command=self.dang_ky_ca).pack(anchor="e", padx=10, pady=5)

        # Bảng danh sách Ca làm
        cols = ("Mã NV", "Ngày", "Ca Làm", "Trạng Thái")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        # Nút chức năng dành riêng cho Admin
        if self.role == "admin":
            admin_bar = tk.Frame(self, bg=BG, padx=10, pady=5)
            admin_bar.pack(fill="x")
            ttk.Button(admin_bar, text="✅ Duyệt ca chọn", command=lambda: self.duyet_ca("Đã duyệt")).pack(side="left", padx=5)
            ttk.Button(admin_bar, text="❌ Từ chối ca chọn", command=lambda: self.duyet_ca("Từ chối")).pack(side="left", padx=5)

        self.load_data()

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        ds_lich = getattr(self.quan_ly, 'danh_sach_lich_lam', [])
        for l in ds_lich:
            # Nếu là User bình thường thì chỉ xem lịch của chính mình
            if self.role != "admin" and l.ma_nv != self.username:
                continue
            self.tree.insert("", "end", values=(l.ma_nv, l.ngay, l.ca_lam, l.trang_thai))

    def dang_ky_ca(self):
        nv = self.ent_nv.get().strip()
        ngay = self.ent_ngay.get().strip()
        ca = self.cbo_ca.get()

        if not nv or not ngay:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên nhân viên và ngày làm!")
            return

        moi = LichLamViec(nv, nv, ngay, ca, "Chờ duyệt")
        if not hasattr(self.quan_ly, 'danh_sach_lich_lam'):
            self.quan_ly.danh_sach_lich_lam = []
        self.quan_ly.danh_sach_lich_lam.append(moi)
        self.quan_ly.save_to_json()
        self.load_data()
        messagebox.showinfo("Thành công", "Đăng ký ca làm thành công, vui lòng chờ Admin duyệt!")

    def duyet_ca(self, trang_thai_moi):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Chú ý", "Vui lòng chọn ca làm cần duyệt!")
            return
        vals = self.tree.item(selected[0])["values"]
        ma_nv, ngay, ca = vals[0], vals[1], vals[2]

        for l in getattr(self.quan_ly, 'danh_sach_lich_lam', []):
            if l.ma_nv == ma_nv and l.ngay == ngay and l.ca_lam == ca:
                l.trang_thai = trang_thai_moi
                break
        self.quan_ly.save_to_json()
        self.load_data()
        messagebox.showinfo("Thành công", f"Đã chuyển trạng thái ca làm thành '{trang_thai_moi}'!")