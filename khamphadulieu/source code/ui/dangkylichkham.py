# dangkylichkham.py
import tkinter as tk
from tkinter import ttk, messagebox
from db.models import QuanLyPhongKham, LichKham, BenhNhan


class AppointmentRegistrationView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#FFFFFF")
        self.quan_ly = QuanLyPhongKham()
        self.setup_ui()

    def setup_ui(self):
        header = tk.Frame(self, bg="#FFFFFF")
        header.pack(fill="x", pady=(0, 15))

        tk.Label(header, text="Đăng ký & Đặt lịch khám", bg="#FFFFFF", fg="#1C1917",
                 font=("Segoe UI", 16, "bold")).pack(anchor="w")
        tk.Label(header, text="Quản lý tiếp nhận và đặt lịch hẹn khám bệnh", bg="#FFFFFF", fg="#78716C",
                 font=("Segoe UI", 9)).pack(anchor="w")

        box_form = tk.LabelFrame(self, text=" Thêm lịch khám mới ", bg="#FFFFFF", fg="#854D0E",
                                 font=("Segoe UI", 10, "bold"), bd=1, relief="solid")
        box_form.pack(fill="x", pady=(0, 15), ipadx=10, ipady=10)

        grid = tk.Frame(box_form, bg="#FFFFFF")
        grid.pack(fill="x", padx=10, pady=5)

        tk.Label(grid, text="Mã bệnh nhân:", bg="#FFFFFF", font=("Segoe UI", 9, "bold")).grid(row=0, column=0,
                                                                                              sticky="w", pady=5)
        self.ent_ma_bn = ttk.Entry(grid, width=25)
        self.ent_ma_bn.grid(row=0, column=1, sticky="w", padx=(5, 20), pady=5)

        tk.Label(grid, text="Họ và tên:", bg="#FFFFFF", font=("Segoe UI", 9, "bold")).grid(row=0, column=2, sticky="w",
                                                                                           pady=5)
        self.ent_ho_ten = ttk.Entry(grid, width=35)
        self.ent_ho_ten.grid(row=0, column=3, sticky="w", padx=(5, 0), pady=5)

        tk.Label(grid, text="Ngày khám (YYYY-MM-DD):", bg="#FFFFFF", font=("Segoe UI", 9, "bold")).grid(row=1, column=0,
                                                                                                        sticky="w",
                                                                                                        pady=5)
        self.ent_ngay = ttk.Entry(grid, width=25)
        self.ent_ngay.insert(0, "2026-10-27")
        self.ent_ngay.grid(row=1, column=1, sticky="w", padx=(5, 20), pady=5)

        tk.Label(grid, text="Giờ khám:", bg="#FFFFFF", font=("Segoe UI", 9, "bold")).grid(row=1, column=2, sticky="w",
                                                                                          pady=5)
        self.cbo_gio = ttk.Combobox(grid, width=33,
                                    values=["08:00", "08:30", "09:00", "09:30", "10:00", "14:00", "14:30", "15:00"],
                                    state="readonly")
        self.cbo_gio.set("08:00")
        self.cbo_gio.grid(row=1, column=3, sticky="w", padx=(5, 0), pady=5)

        tk.Label(grid, text="Lý do khám:", bg="#FFFFFF", font=("Segoe UI", 9, "bold")).grid(row=2, column=0, sticky="w",
                                                                                            pady=5)
        self.ent_ly_do = ttk.Entry(grid, width=70)
        self.ent_ly_do.grid(row=2, column=1, columnspan=3, sticky="w", padx=(5, 0), pady=5)

        btn_dat_lich = tk.Button(
            box_form, text="➕ Tạo Lịch Khám Mới", command=self.add_appointment,
            bg="#EAB308", fg="#FFFFFF", activebackground="#CA8A04", activeforeground="#FFFFFF",
            font=("Segoe UI", 10, "bold"), bd=0, relief="flat", padx=15, pady=6, cursor="hand2"
        )
        btn_dat_lich.pack(anchor="e", padx=10, pady=(5, 0))

        box_table = tk.LabelFrame(self, text=" Danh sách lịch hẹn ", bg="#FFFFFF", fg="#854D0E",
                                  font=("Segoe UI", 10, "bold"), bd=1, relief="solid")
        box_table.pack(fill="both", expand=True, ipadx=10, ipady=10)

        style = ttk.Style()
        style.configure("CustomApp.Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#FEF08A",
                        foreground="#000000")

        self.tree = ttk.Treeview(box_table, columns=("MaLK", "MaBN", "HoTen", "Ngay", "Gio", "LyDo", "TrangThai"),
                                 show="headings", style="CustomApp.Treeview")
        self.tree.heading("MaLK", text="Mã Lịch")
        self.tree.heading("MaBN", text="Mã BN")
        self.tree.heading("HoTen", text="Họ và Tên")
        self.tree.heading("Ngay", text="Ngày Khám")
        self.tree.heading("Gio", text="Giờ Khám")
        self.tree.heading("LyDo", text="Lý Do Khám")
        self.tree.heading("TrangThai", text="Trạng Thái")

        self.tree.column("MaLK", width=80, anchor="center")
        self.tree.column("MaBN", width=90, anchor="center")
        self.tree.column("HoTen", width=180, anchor="w")
        self.tree.column("Ngay", width=100, anchor="center")
        self.tree.column("Gio", width=80, anchor="center")
        self.tree.column("LyDo", width=250, anchor="w")
        self.tree.column("TrangThai", width=110, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.load_data()

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        self.quan_ly.load_from_json()

        for lk in self.quan_ly.danh_sach_lich_kham:
            self.tree.insert("", "end", values=(lk.ma_lich, lk.ma_bn, lk.ho_ten_bn, lk.ngay_kham, lk.gio_kham, lk.ly_do,
                                                lk.trang_thai))

    def add_appointment(self):
        ma_bn = self.ent_ma_bn.get().strip()
        ho_ten = self.ent_ho_ten.get().strip()
        ngay = self.ent_ngay.get().strip()
        gio = self.cbo_gio.get().strip()
        ly_do = self.ent_ly_do.get().strip()

        if not ma_bn or not ho_ten or not ly_do:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ Mã BN, Họ tên và Lý do khám!")
            return

        ma_lk = f"LK{len(self.quan_ly.danh_sach_lich_kham) + 1:03d}"

        # Tạo đối tượng lịch khám và lưu vào cơ sở dữ liệu JSON
        moi_lk = LichKham(ma_lk, ma_bn, ho_ten, "BS. Nguyễn Văn A", ngay, gio, ly_do, "Chờ khám")
        self.quan_ly.dat_lich_kham(moi_lk)

        # Thêm bệnh nhân mới vào danh sách nếu chưa có
        self.quan_ly.them_benh_nhan(BenhNhan(ma_bn, ho_ten, "0900000000", "2000-01-01", "Nam"))

        self.load_data()
        messagebox.showinfo("Thành công", f"Đã đăng ký lịch khám thành công cho bệnh nhân {ho_ten}!")

        self.ent_ma_bn.delete(0, tk.END)
        self.ent_ho_ten.delete(0, tk.END)
        self.ent_ly_do.delete(0, tk.END)