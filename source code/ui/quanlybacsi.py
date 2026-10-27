# ui/quanlybacsi.py
import tkinter as tk
from tkinter import ttk, messagebox
from db.models import QuanLyPhongKham, BacSi


class DoctorManagementView(tk.Frame):
    def __init__(self, parent, role="admin"):
        super().__init__(parent, bg="#FFFFFF")
        self.quan_ly = QuanLyPhongKham()
        self.role = role
        self.setup_ui()

    def setup_ui(self):
        tk.Label(self, text="👨‍⚕️ Quản Lý Bác Sĩ Phòng Khám", bg="#FFFFFF", fg="#1C1917",
                 font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 10))

        # Form CRUD
        form = tk.LabelFrame(self, text=" Thông Tin Bác Sĩ ", bg="#FFFFFF", bd=1, relief="solid")
        form.pack(fill="x", pady=(0, 10), ipady=5, ipadx=10)

        fg = tk.Frame(form, bg="#FFFFFF")
        fg.pack(fill="x", padx=10, pady=5)

        tk.Label(fg, text="Mã BS:", bg="#FFFFFF").grid(row=0, column=0)
        self.ent_ma = ttk.Entry(fg, width=15)
        self.ent_ma.grid(row=0, column=1, padx=5)

        tk.Label(fg, text="Họ Tên:", bg="#FFFFFF").grid(row=0, column=2)
        self.ent_ten = ttk.Entry(fg, width=25)
        self.ent_ten.grid(row=0, column=3, padx=5)

        tk.Label(fg, text="Chuyên Khoa:", bg="#FFFFFF").grid(row=0, column=4)
        self.cbo_khoa = ttk.Combobox(fg, values=["Nội Khoa", "Ngoại Khoa", "Tai Mũi Họng", "Nhi Khoa", "Mắt",
                                                 "Răng Hàm Mặt"], width=18)
        self.cbo_khoa.grid(row=0, column=5, padx=5)

        tk.Label(fg, text="SĐT:", bg="#FFFFFF").grid(row=0, column=6)
        self.ent_sdt = ttk.Entry(fg, width=15)
        self.ent_sdt.grid(row=0, column=7, padx=5)

        # Buttons
        btn_frame = tk.Frame(self, bg="#FFFFFF")
        btn_frame.pack(fill="x", pady=(0, 10))

        tk.Button(btn_frame, text="➕ Thêm Bác Sĩ", command=self.them_bs, bg="#EAB308", fg="#FFFFFF",
                  font=("Segoe UI", 9, "bold"), bd=0, padx=10, pady=3, cursor="hand2").pack(side="left", padx=2)

        # PHÂN QUYỀN: CHỈ ADMIN MỚI CÓ QUYỀN XÓA (Yêu cầu 1)
        if self.role == "admin":
            tk.Button(btn_frame, text="❌ Xóa Bác Sĩ", command=self.xoa_bs, bg="#EF4444", fg="#FFFFFF",
                      font=("Segoe UI", 9, "bold"), bd=0, padx=10, pady=3, cursor="hand2").pack(side="left", padx=2)

        tk.Label(btn_frame, text=" 🔍 Lọc theo Chuyên Khoa: ", bg="#FFFFFF", font=("Segoe UI", 9, "bold")).pack(
            side="left", padx=(20, 2))
        self.cbo_filter = ttk.Combobox(btn_frame,
                                       values=["Tất cả", "Nội Khoa", "Ngoại Khoa", "Tai Mũi Họng", "Nhi Khoa"],
                                       state="readonly", width=18)
        self.cbo_filter.set("Tất cả")
        self.cbo_filter.pack(side="left")
        self.cbo_filter.bind("<<ComboboxSelected>>", self.loc_theo_khoa)

        # Bảng
        cols = ("MaBS", "HoTen", "ChuyenKhoa", "SDT")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c, t in zip(cols, ["Mã Bác Sĩ", "Họ & Tên Bác Sĩ", "Chuyên Khoa", "Số Điện Thoại"]):
            self.tree.heading(c, text=t)
            self.tree.column(c, anchor="center" if c != "HoTen" else "w")
        self.tree.pack(fill="both", expand=True)

        self.load_data()

    def load_data(self, filter_khoa="Tất cả"):
        self.quan_ly.load_from_json()
        self.tree.delete(*self.tree.get_children())
        for bs in self.quan_ly.danh_sach_bac_si:
            m = bs.get("ma_bs") if isinstance(bs, dict) else bs.ma_bs
            t = bs.get("ho_ten") if isinstance(bs, dict) else bs.ho_ten
            k = bs.get("chuyen_khoa") if isinstance(bs, dict) else bs.chuyen_khoa
            s = bs.get("sdt") if isinstance(bs, dict) else bs.sdt

            if filter_khoa == "Tất cả" or k == filter_khoa:
                self.tree.insert("", "end", values=(m, t, k, s))

    def them_bs(self):
        m, t, k, s = self.ent_ma.get().strip(), self.ent_ten.get().strip(), self.cbo_khoa.get().strip(), self.ent_sdt.get().strip()
        if not m or not t or not k:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng điền đủ Mã, Tên và Chuyên khoa!")
            return
        self.quan_ly.danh_sach_bac_si.append({"ma_bs": m, "ho_ten": t, "chuyen_khoa": k, "sdt": s})
        self.quan_ly.save_to_json()
        self.load_data()
        messagebox.showinfo("Thành công", f"Đã thêm Bác sĩ [{t}] thành công!")

    def xoa_bs(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Chú ý", "Vui lòng chọn 1 bác sĩ để xóa!")
            return
        m = self.tree.item(selected[0])["values"][0]
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa Bác sĩ [{m}]?"):
            self.quan_ly.danh_sach_bac_si = [b for b in self.quan_ly.danh_sach_bac_si if
                                             (b.get("ma_bs") if isinstance(b, dict) else b.ma_bs) != m]
            self.quan_ly.save_to_json()
            self.load_data()

    def loc_theo_khoa(self, event):
        self.load_data(self.cbo_filter.get())