import tkinter as tk
from tkinter import ttk, messagebox
from db.models import QuanLyPhongKham, PhieuKhamBenh


class MedicalServiceView(tk.Frame):
    def __init__(self, parent, role="admin"):
        super().__init__(parent, bg="#FFFFFF")
        self.quan_ly = QuanLyPhongKham()
        self.role = role
        self.dich_vu_da_chon = []

        self.setup_ui()

    def setup_ui(self):
        # Header Tiêu đề chính
        header = tk.Frame(self, bg="#FFFFFF")
        header.pack(fill="x", pady=(0, 10))

        role_text = f" (Quyền: {str(self.role).upper()})" if self.role else ""
        tk.Label(
            header,
            text=f"Khám bệnh & Chỉ định dịch vụ{role_text}",
            bg="#FFFFFF", fg="#1C1917",
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Ghi nhận chẩn đoán, dịch vụ và thanh toán",
            bg="#FFFFFF", fg="#78716C",
            font=("Segoe UI", 9)
        ).pack(anchor="w")

        # Khung chọn Bệnh nhân & Chẩn đoán
        box_top = tk.LabelFrame(self, text="", bg="#FFFFFF", bd=1, relief="solid")
        box_top.pack(fill="x", pady=(0, 10), ipady=6, ipadx=10)

        grid_top = tk.Frame(box_top, bg="#FFFFFF")
        grid_top.pack(fill="x", padx=10, pady=5)

        tk.Label(grid_top, text="Bệnh nhân:", bg="#FFFFFF", font=("Segoe UI", 9, "bold")).grid(row=0, column=0,
                                                                                               sticky="w", padx=(0, 5))
        self.cbo_benh_nhan = ttk.Combobox(grid_top, width=35, state="readonly")
        self.cbo_benh_nhan.grid(row=0, column=1, sticky="w", padx=(0, 30))

        tk.Label(grid_top, text="Chẩn đoán:", bg="#FFFFFF", font=("Segoe UI", 9, "bold")).grid(row=0, column=2,
                                                                                               sticky="w", padx=(0, 5))
        self.ent_chan_doan = ttk.Entry(grid_top, width=55)
        self.ent_chan_doan.grid(row=0, column=3, sticky="w")

        # Khung Chi tiết khám bệnh
        box_main = tk.LabelFrame(self, text=" Chi tiết khám bệnh ", bg="#FFFFFF", fg="#1C1917",
                                 font=("Segoe UI", 9, "bold"), bd=1, relief="solid")
        box_main.pack(fill="both", expand=True, ipadx=10, ipady=10)

        main_inner = tk.Frame(box_main, bg="#FFFFFF")
        main_inner.pack(fill="both", expand=True, padx=10, pady=8)

        # Ô Nhập Nội dung / Tiền sử khám bệnh
        tk.Label(main_inner, text="Nội dung / Tiền sử khám bệnh:", bg="#FFFFFF", font=("Segoe UI", 9, "bold")).pack(
            anchor="w", pady=(0, 4))
        self.txt_noidung = tk.Text(main_inner, height=3, font=("Segoe UI", 10), bd=1, relief="solid")
        self.txt_noidung.pack(fill="x", pady=(0, 10))

        # Khung chọn Dịch vụ (Đã loại bỏ nút Crawl API và phần Kê thuốc)
        dv_bar = tk.Frame(main_inner, bg="#FFFFFF")
        dv_bar.pack(fill="x", pady=(0, 10))

        tk.Label(dv_bar, text="Dịch vụ:", bg="#FFFFFF", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 5))

        self.cbo_dich_vu = ttk.Combobox(dv_bar, width=35, state="readonly")
        self.cbo_dich_vu.pack(side="left", padx=(0, 8))

        btn_them_dv = tk.Button(
            dv_bar, text="+ Dịch vụ", command=self.add_service,
            bg="#FFFFFF", fg="#1C1917", font=("Segoe UI", 9), bd=1, relief="solid", padx=10, pady=2, cursor="hand2"
        )
        btn_them_dv.pack(side="left", padx=(0, 5))

        btn_xoa_dv = tk.Button(
            dv_bar, text="Xóa dịch vụ", command=self.remove_service,
            bg="#FFFFFF", fg="#1C1917", font=("Segoe UI", 9), bd=1, relief="solid", padx=10, pady=2, cursor="hand2"
        )
        btn_xoa_dv.pack(side="left")

        # Bảng Treeview hiển thị Danh sách dịch vụ chỉ định
        style = ttk.Style()
        style.configure("CustomDV.Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#FEF08A",
                        foreground="#000000")

        self.tree = ttk.Treeview(main_inner, columns=("TenDV", "SoLuong", "DonGia", "ThanhTien"), show="headings",
                                 style="CustomDV.Treeview")
        self.tree.heading("TenDV", text="Tên Dịch Vụ")
        self.tree.heading("SoLuong", text="Số Lượng")
        self.tree.heading("DonGia", text="Đơn Giá")
        self.tree.heading("ThanhTien", text="Thành Tiền (VNĐ)")

        self.tree.column("TenDV", anchor="w", width=380)
        self.tree.column("SoLuong", anchor="center", width=90)
        self.tree.column("DonGia", anchor="e", width=120)
        self.tree.column("ThanhTien", anchor="e", width=150)
        self.tree.pack(fill="both", expand=True, pady=(0, 10))

        # Bottom Bar: Tổng chi phí & Nút Lưu phiếu
        bottom_bar = tk.Frame(main_inner, bg="#FFFFFF")
        bottom_bar.pack(fill="x")

        self.lbl_tong_tien = tk.Label(bottom_bar, text="TỔNG CHI PHÍ HÓA ĐƠN: 0 VNĐ", bg="#FFFFFF", fg="#EAB308",
                                      font=("Segoe UI", 11, "bold"))
        self.lbl_tong_tien.pack(side="left")

        btn_luu = tk.Button(
            bottom_bar, text="💾 Lưu phiếu & Xuất hóa đơn", command=self.save_and_pay,
            bg="#EAB308", fg="#FFFFFF", activebackground="#CA8A04", activeforeground="#FFFFFF",
            font=("Segoe UI", 10, "bold"), bd=0, relief="flat", padx=15, pady=6, cursor="hand2"
        )
        btn_luu.pack(side="right")

        # Khung Danh Sách Phiếu Khám & Duyệt Thanh Toán (Cho Admin)
        if str(self.role).lower() == "admin":
            self.setup_admin_payment_section()

        self.load_initial_data()

    def setup_admin_payment_section(self):
        box_admin = tk.LabelFrame(self, text=" Danh Sách Phiếu Khám & Duyệt Thanh Toán ", bg="#FFFFFF", fg="#1C1917",
                                  font=("Segoe UI", 9, "bold"), bd=1, relief="solid")
        box_admin.pack(fill="x", pady=(10, 0), ipadx=10, ipady=5)

        btn_duyet = tk.Button(
            box_admin, text="✅ Admin Duyệt & Thanh Toán", command=self.approve_payment,
            bg="#22C55E", fg="#FFFFFF", font=("Segoe UI", 9, "bold"), bd=0, relief="flat", padx=10, pady=4,
            cursor="hand2"
        )
        btn_duyet.pack(anchor="w", padx=10, pady=5)

        self.tree_admin = ttk.Treeview(box_admin,
                                       columns=("MaPK", "BenhNhan", "NgayKham", "ChanDoan", "TongTien", "TrangThai"),
                                       show="headings", height=3)
        self.tree_admin.heading("MaPK", text="Mã PK")
        self.tree_admin.heading("BenhNhan", text="Bệnh Nhân")
        self.tree_admin.heading("NgayKham", text="Ngày Khám")
        self.tree_admin.heading("ChanDoan", text="Chẩn Đoán")
        self.tree_admin.heading("TongTien", text="Tổng Tiền (VNĐ)")
        self.tree_admin.heading("TrangThai", text="Trạng Thái")

        self.tree_admin.column("MaPK", anchor="center", width=80)
        self.tree_admin.column("BenhNhan", anchor="w", width=160)
        self.tree_admin.column("NgayKham", anchor="center", width=100)
        self.tree_admin.column("ChanDoan", anchor="w", width=220)
        self.tree_admin.column("TongTien", anchor="e", width=120)
        self.tree_admin.column("TrangThai", anchor="center", width=110)

        self.tree_admin.pack(fill="x", padx=10, pady=(0, 5))

    def load_initial_data(self):
        try:
            self.quan_ly.load_from_json()
        except Exception:
            pass

        # Load danh sách bệnh nhân
        list_bn = []
        if hasattr(self.quan_ly, 'danh_sach_benh_nhan') and self.quan_ly.danh_sach_benh_nhan:
            list_bn = [f"{bn.ma_id} - {bn.ho_ten}" for bn in self.quan_ly.danh_sach_benh_nhan]
        if not list_bn:
            list_bn = ["BN001 - Nguyễn Văn An", "BN002 - Trần Thị Bích"]
        self.cbo_benh_nhan["values"] = list_bn
        self.cbo_benh_nhan.set(list_bn[0])

        # Load danh sách dịch vụ
        list_dv = [
            "Khám Nội Tổng Quát - 150,000đ",
            "Xét Nghiệm Máu - 100,000đ",
            "Siêu Âm Tổng Quát - 200,000đ",
            "Chụp X-Quang - 180,000đ"
        ]
        self.cbo_dich_vu["values"] = list_dv
        self.cbo_dich_vu.set(list_dv[0])

    def add_service(self):
        val = self.cbo_dich_vu.get()
        if not val:
            return
        parts = val.split(" - ")
        ten_dv = parts[0]
        gia_str = parts[1].replace(",", "").replace("đ", "").strip()
        gia = int(gia_str)

        self.dich_vu_da_chon.append({"ten_dv": ten_dv, "gia": gia, "so_luong": 1})
        self.tree.insert("", "end", values=(ten_dv, 1, f"{gia:,}", f"{gia:,}"))
        self.update_total()

    def remove_service(self):
        selected = self.tree.selection()
        if selected:
            idx = self.tree.index(selected[0])
            self.tree.delete(selected[0])
            self.dich_vu_da_chon.pop(idx)
            self.update_total()

    def update_total(self):
        tong = sum(item["gia"] * item["so_luong"] for item in self.dich_vu_da_chon)
        self.lbl_tong_tien.config(text=f"TỔNG CHI PHÍ HÓA ĐƠN: {tong:,} VNĐ")

    def save_and_pay(self):
        bn_str = self.cbo_benh_nhan.get()
        chan_doan = self.ent_chan_doan.get().strip()

        if not chan_doan:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập chẩn đoán bệnh!", parent=self)
            return

        tong_tien = sum(item["gia"] * item["so_luong"] for item in self.dich_vu_da_chon)
        ma_pk = f"PK{len(self.dich_vu_da_chon) + 1:03d}"

        if hasattr(self, 'tree_admin'):
            self.tree_admin.insert("", "end",
                                   values=(ma_pk, bn_str, "2026-10-27", chan_doan, f"{tong_tien:,}", "Chờ duyệt"))

        messagebox.showinfo("Thành công", f"Đã tạo phiếu khám {ma_pk} thành công!", parent=self)
        self.ent_chan_doan.delete(0, tk.END)
        self.txt_noidung.delete("1.0", tk.END)
        self.dich_vu_da_chon.clear()
        self.tree.delete(*self.tree.get_children())
        self.update_total()

    def approve_payment(self):
        if hasattr(self, 'tree_admin'):
            selected = self.tree_admin.selection()
            if not selected:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn phiếu khám cần duyệt!", parent=self)
                return
            vals = list(self.tree_admin.item(selected[0], "values"))
            vals[5] = "Đã thanh toán"
            self.tree_admin.item(selected[0], values=vals)
            messagebox.showinfo("Thành công", f"Đã duyệt thanh toán cho phiếu {vals[0]}!", parent=self)