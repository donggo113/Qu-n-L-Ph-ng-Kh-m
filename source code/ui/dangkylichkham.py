# ui/dangkylichkham.py
import tkinter as tk
from tkinter import ttk, messagebox
from db.models import QuanLyPhongKham
from utils import export_to_csv


class AppointmentRegistrationView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#FFFFFF")
        self.quan_ly = QuanLyPhongKham()
        self.setup_ui()

    def setup_ui(self):
        tk.Label(self, text="📅 Đăng Ký & Đặt Lịch Khám", bg="#FFFFFF", fg="#1C1917",
                 font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 10))

        # Form đặt lịch
        form = tk.LabelFrame(self, text=" Thêm Lịch Hẹn Mới ", bg="#FFFFFF", bd=1, relief="solid")
        form.pack(fill="x", pady=(0, 10), ipady=5, ipadx=10)

        f_grid = tk.Frame(form, bg="#FFFFFF")
        f_grid.pack(fill="x", padx=10, pady=5)

        tk.Label(f_grid, text="Bệnh nhân:", bg="#FFFFFF").grid(row=0, column=0, sticky="w")
        self.cbo_bn = ttk.Combobox(f_grid, width=25, state="readonly")
        self.cbo_bn.grid(row=0, column=1, padx=(0, 15))

        tk.Label(f_grid, text="Bác sĩ khám:", bg="#FFFFFF").grid(row=0, column=2, sticky="w")
        self.cbo_bs = ttk.Combobox(f_grid, width=25, state="readonly")
        self.cbo_bs.grid(row=0, column=3, padx=(0, 15))

        tk.Label(f_grid, text="Ngày (YYYY-MM-DD):", bg="#FFFFFF").grid(row=1, column=0, sticky="w", pady=5)
        self.ent_ngay = ttk.Entry(f_grid, width=27)
        self.ent_ngay.insert(0, "2026-10-20")
        self.ent_ngay.grid(row=1, column=1, padx=(0, 15), pady=5)

        tk.Label(f_grid, text="Giờ khám:", bg="#FFFFFF").grid(row=1, column=2, sticky="w", pady=5)
        self.cbo_gio = ttk.Combobox(f_grid,
                                    values=["08:00", "08:30", "09:00", "09:30", "10:00", "14:00", "14:30", "15:00"],
                                    width=25, state="readonly")
        self.cbo_gio.set("09:00")
        self.cbo_gio.grid(row=1, column=3, padx=(0, 15), pady=5)

        btn_dat = tk.Button(f_grid, text="➕ Đặt Lịch", command=self.dat_lich, bg="#EAB308", fg="#FFFFFF",
                            font=("Segoe UI", 9, "bold"), bd=0, padx=12, pady=4, cursor="hand2")
        btn_dat.grid(row=1, column=4)

        # Toolbar
        tb = tk.Frame(self, bg="#FFFFFF")
        tb.pack(fill="x", pady=(0, 5))
        btn_export = tk.Button(tb, text="📄 Xuất Báo Cáo Lịch Hẹn (CSV)", command=self.xuat_csv, bg="#FEF08A",
                               fg="#854D0E", font=("Segoe UI", 9, "bold"), bd=1, relief="solid", padx=10, pady=3,
                               cursor="hand2")
        btn_export.pack(side="left")

        # Bảng lịch hẹn
        cols = ("MaBS", "BacSi", "BenhNhan", "NgayKham", "GioKham")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c, t in zip(cols, ["Mã BS", "Bác Sĩ Khám", "Bệnh Nhân", "Ngày Khám", "Giờ Khám"]):
            self.tree.heading(c, text=t)
            self.tree.column(c, anchor="center")
        self.tree.pack(fill="both", expand=True)

        self.load_data()

    def load_data(self):
        self.quan_ly.load_from_json()

        # Load danh sách BN & BS
        list_bn = [
            f"{bn.get('ma_id', '')} - {bn.get('ho_ten', '')}" if isinstance(bn, dict) else f"{bn.ma_id} - {bn.ho_ten}"
            for bn in self.quan_ly.danh_sach_benh_nhan]
        list_bs = [
            f"{bs.get('ma_bs', '')} - {bs.get('ho_ten', '')}" if isinstance(bs, dict) else f"{bs.ma_bs} - {bs.ho_ten}"
            for bs in self.quan_ly.danh_sach_bac_si]

        self.cbo_bn["values"] = list_bn or ["BN001 - Nguyễn Văn An"]
        if list_bn: self.cbo_bn.set(list_bn[0])

        self.cbo_bs["values"] = list_bs or ["BS001 - BS. Nguyễn Văn A"]
        if list_bs: self.cbo_bs.set(list_bs[0])

        # Render Treeview
        self.tree.delete(*self.tree.get_children())
        for lk in self.quan_ly.danh_sach_lich_kham:
            self.tree.insert("", "end",
                             values=(lk.get("ma_bs"), lk.get("ten_bs"), lk.get("ten_bn"), lk.get("ngay_kham"),
                                     lk.get("gio_kham")))

    def dat_lich(self):
        bs_str = self.cbo_bs.get()
        bn_str = self.cbo_bn.get()
        ngay = self.ent_ngay.get().strip()
        gio = self.cbo_gio.get().strip()

        ma_bs = bs_str.split(" - ")[0]
        ten_bs = bs_str.split(" - ")[1]
        ten_bn = bn_str.split(" - ")[1]

        # CHẶN TRÙNG LỊCH BÁC SĨ (Yêu cầu 4)
        if self.quan_ly.kiem_tra_trung_lich_bac_si(ma_bs, ngay, gio):
            messagebox.showerror("Trùng Lịch Khám!",
                                 f"⚠️ Bác sĩ [{ten_bs}] đã có lịch hẹn vào lúc {gio} ngày {ngay}!\nVui lòng chọn giờ hoặc bác sĩ khác.")
            return

        self.quan_ly.danh_sach_lich_kham.append({
            "ma_bs": ma_bs, "ten_bs": ten_bs, "ten_bn": ten_bn, "ngay_kham": ngay, "gio_kham": gio
        })
        self.quan_ly.save_to_json()
        self.load_data()
        messagebox.showinfo("Thành công", f"Đã đặt lịch thành công cho {ten_bn} với {ten_bs} lúc {gio} ngày {ngay}!")

    def xuat_csv(self):
        data_csv = []
        for child in self.tree.get_children():
            data_csv.append(self.tree.item(child)["values"])

        headers = ["Mã Bác Sĩ", "Tên Bác Sĩ", "Bệnh Nhân", "Ngày Khám", "Giờ Khám"]
        if export_to_csv("danh_sach_lich_hen.csv", headers, data_csv):
            messagebox.showinfo("Xuất Báo Cáo", "Đã xuất file báo cáo 'danh_sach_lich_hen.csv' thành công!")