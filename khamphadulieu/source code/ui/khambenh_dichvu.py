# ui/khambenh_dichvu.py
import tkinter as tk
from tkinter import ttk, messagebox
from db.models import QuanLyPhongKham, PhieuKhamBenh


class MedicalServiceView(tk.Frame):
    def __init__(self, parent, role="user"):
        super().__init__(parent, bg="#FFFFFF")
        self.quan_ly = QuanLyPhongKham()
        self.role = role  # Nhận vai trò người dùng ("admin" hoặc "user")
        self.dich_vu_da_chon = []

        self.setup_ui()

    def setup_ui(self):
        # Header Tiêu đề chính
        header = tk.Frame(self, bg="#FFFFFF")
        header.pack(fill="x", pady=(0, 10))

        tk.Label(header, text="Khám bệnh & Chỉ định dịch vụ", bg="#FFFFFF", fg="#1C1917",
                 font=("Segoe UI", 16, "bold")).pack(anchor="w")
        tk.Label(header, text=f"Ghi nhận chẩn đoán và quản lý duyệt thanh toán (Quyền: {self.role.upper()})",
                 bg="#FFFFFF", fg="#78716C", font=("Segoe UI", 9)).pack(anchor="w")

        # Khung chọn Bệnh nhân & Chẩn đoán
        box_top = tk.LabelFrame(self, text="", bg="#FFFFFF", bd=1, relief="solid")
        box_top.pack(fill="x", pady=(0, 10), ipady=5, ipadx=10)

        grid_top = tk.Frame(box_top, bg="#FFFFFF")
        grid_top.pack(fill="x", padx=10, pady=5)

        tk.Label(grid_top, text="Bệnh nhân:", bg="#FFFFFF", font=("Segoe UI", 9, "bold")).grid(row=0, column=0,
                                                                                               sticky="w", padx=(0, 5))
        self.cbo_benh_nhan = ttk.Combobox(grid_top, width=30, state="readonly")
        self.cbo_benh_nhan.grid(row=0, column=1, sticky="w", padx=(0, 20))

        tk.Label(grid_top, text="Chẩn đoán:", bg="#FFFFFF", font=("Segoe UI", 9, "bold")).grid(row=0, column=2,
                                                                                               sticky="w", padx=(0, 5))
        self.ent_chan_doan = ttk.Entry(grid_top, width=45)
        self.ent_chan_doan.grid(row=0, column=3, sticky="w")

        # Khung Nội dung & Chỉ định Dịch vụ
        box_main = tk.LabelFrame(self, text="Chi tiết khám bệnh", bg="#FFFFFF", bd=1, relief="solid",
                                 font=("Segoe UI", 9, "bold"))
        box_main.pack(fill="x", ipadx=10, ipady=5, pady=(0, 10))

        main_inner = tk.Frame(box_main, bg="#FFFFFF")
        main_inner.pack(fill="x", padx=10, pady=5)

        # Ô Nhập Nội dung / Tiền sử
        tk.Label(main_inner, text="Nội dung / Tiền sử khám bệnh:", bg="#FFFFFF", font=("Segoe UI", 9, "bold")).pack(
            anchor="w", pady=(0, 2))
        self.txt_noidung = tk.Text(main_inner, height=3, font=("Segoe UI", 9), bd=1, relief="solid")
        self.txt_noidung.pack(fill="x", pady=(0, 8))

        # Thanh chọn Dịch vụ & Nút bấm
        dv_bar = tk.Frame(main_inner, bg="#FFFFFF")
        dv_bar.pack(fill="x", pady=(0, 8))

        tk.Label(dv_bar, text="Chọn dịch vụ:", bg="#FFFFFF", font=("Segoe UI", 9, "bold")).pack(side="left",
                                                                                                padx=(0, 5))
        self.cbo_dich_vu = ttk.Combobox(dv_bar, width=35, state="readonly")
        self.cbo_dich_vu.pack(side="left", padx=(0, 8))

        btn_them = tk.Button(
            dv_bar, text="Thêm dịch vụ", command=self.add_service,
            bg="#FFFFFF", fg="#1C1917", font=("Segoe UI", 9), bd=1, relief="solid", padx=8, pady=2, cursor="hand2"
        )
        btn_them.pack(side="left", padx=(0, 5))

        btn_xoa = tk.Button(
            dv_bar, text="Xóa dịch vụ chọn", command=self.remove_service,
            bg="#FFFFFF", fg="#1C1917", font=("Segoe UI", 9), bd=1, relief="solid", padx=8, pady=2, cursor="hand2"
        )
        btn_xoa.pack(side="left", padx=(0, 5))

        btn_crawl = tk.Button(
            dv_bar, text="🌐 Crawl Dữ Liệu API", command=self.thuc_hien_crawl,
            bg="#FEF08A", fg="#854D0E", font=("Segoe UI", 9, "bold"), bd=1, relief="solid", padx=8, pady=2,
            cursor="hand2"
        )
        btn_crawl.pack(side="left")

        # Bảng hiển thị dịch vụ đã chọn
        style = ttk.Style()
        style.configure("Custom.Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#FEF08A",
                        foreground="#000000")

        self.tree_dv = ttk.Treeview(main_inner, columns=("TenDV", "DonGia"), show="headings", height=3,
                                    style="Custom.Treeview")
        self.tree_dv.heading("TenDV", text="Tên dịch vụ / Chi tiết")
        self.tree_dv.heading("DonGia", text="Đơn giá (VNĐ)")
        self.tree_dv.column("TenDV", anchor="w", width=400)
        self.tree_dv.column("DonGia", anchor="center", width=150)
        self.tree_dv.pack(fill="x", pady=(0, 8))

        # Bottom Bar: Tổng chi phí & Nút Tạo phiếu (Chờ thanh toán)
        bottom_bar = tk.Frame(main_inner, bg="#FFFFFF")
        bottom_bar.pack(fill="x")

        self.lbl_tong_tien = tk.Label(bottom_bar, text="TỔNG CHI PHÍ: 0 VNĐ", bg="#FFFFFF", fg="#EAB308",
                                      font=("Segoe UI", 11, "bold"))
        self.lbl_tong_tien.pack(side="left")

        btn_luu = tk.Button(
            bottom_bar, text="💾 Lưu phiếu (Chờ thanh toán)", command=self.save_and_pay,
            bg="#EAB308", fg="#FFFFFF", activebackground="#CA8A04", activeforeground="#FFFFFF",
            font=("Segoe UI", 9, "bold"), bd=0, relief="flat", padx=12, pady=5, cursor="hand2"
        )
        btn_luu.pack(side="right")

        # =====================================================================
        # BẢNG DANH SÁCH PHIẾU KHÁM & DUYỆT THANH TOÁN
        # =====================================================================
        box_history = tk.LabelFrame(self, text="📋 Danh Sách Phiếu Khám & Duyệt Thanh Toán", bg="#FFFFFF", bd=1,
                                    relief="solid", font=("Segoe UI", 9, "bold"))
        box_history.pack(fill="both", expand=True, ipadx=10, ipady=5)

        # Thanh công cụ Admin Duyệt
        action_bar = tk.Frame(box_history, bg="#FFFFFF")
        action_bar.pack(fill="x", padx=10, pady=(5, 0))

        if self.role == "admin":
            btn_duyet = tk.Button(
                action_bar, text="✅ Admin Duyệt & Thanh Toán", command=self.duyet_thanh_toan,
                bg="#22C55E", fg="#FFFFFF", font=("Segoe UI", 9, "bold"), bd=0, relief="flat", padx=10, pady=3,
                cursor="hand2"
            )
            btn_duyet.pack(side="left")

        cols = ("MaPK", "HoTenBN", "NgayKham", "ChanDoan", "TongTien", "TrangThai")
        self.tree_pk = ttk.Treeview(box_history, columns=cols, show="headings", style="Custom.Treeview")

        self.tree_pk.heading("MaPK", text="Mã PK")
        self.tree_pk.heading("HoTenBN", text="Bệnh Nhân")
        self.tree_pk.heading("NgayKham", text="Ngày Khám")
        self.tree_pk.heading("ChanDoan", text="Chẩn Đoán")
        self.tree_pk.heading("TongTien", text="Tổng Tiền (VNĐ)")
        self.tree_pk.heading("TrangThai", text="Trạng Thái")

        self.tree_pk.column("MaPK", anchor="center", width=80)
        self.tree_pk.column("HoTenBN", anchor="w", width=150)
        self.tree_pk.column("NgayKham", anchor="center", width=100)
        self.tree_pk.column("ChanDoan", anchor="w", width=200)
        self.tree_pk.column("TongTien", anchor="center", width=120)
        self.tree_pk.column("TrangThai", anchor="center", width=130)

        self.tree_pk.pack(fill="both", expand=True, padx=10, pady=5)

        self.load_initial_data()
        self.load_history_phieu_kham()

    def duyet_thanh_toan(self):
        """Chức năng dành riêng cho Admin để duyệt phiếu chờ thanh toán"""
        selected = self.tree_pk.selection()
        if not selected:
            messagebox.showwarning("Chú ý", "Vui lòng chọn 1 phiếu khám cần duyệt!")
            return

        item = self.tree_pk.item(selected[0])["values"]
        ma_pk, trang_thai = item[0], item[5]

        if trang_thai == "Đã thanh toán":
            messagebox.showinfo("Thông báo", f"Phiếu [{ma_pk}] này đã được thanh toán trước đó!")
            return

        if messagebox.askyesno("Xác nhận", f"Duyệt thanh toán cho phiếu khám [{ma_pk}]?"):
            for pk in self.quan_ly.danh_sach_phieu_kham:
                if pk.ma_pk == ma_pk:
                    pk.trang_thai_tt = "Đã thanh toán"
                    break
            self.quan_ly.save_to_json()
            self.load_history_phieu_kham()
            messagebox.showinfo("Thành công", f"Đã duyệt thanh toán thành công cho phiếu [{ma_pk}]!")

    def thuc_hien_crawl(self):
        from utils import crawl_external_medical_services
        ds_moi = crawl_external_medical_services()
        self.quan_ly.danh_sach_dich_vu = ds_moi
        self.quan_ly.save_to_json()
        self.load_initial_data()
        messagebox.showinfo("Thành công", f"Đã crawl thành công {len(ds_moi)} dịch vụ y tế từ API!")

    def load_initial_data(self):
        try:
            self.quan_ly.load_from_json()
        except Exception as e:
            print("Chưa có file JSON hoặc lỗi nạp DB:", e)

        list_bn = []
        if hasattr(self.quan_ly, 'danh_sach_benh_nhan') and self.quan_ly.danh_sach_benh_nhan:
            list_bn = [f"{bn.ma_id} - {bn.ho_ten}" for bn in self.quan_ly.danh_sach_benh_nhan]

        if not list_bn:
            list_bn = ["BN001 - Nguyễn Văn An", "BN002 - Trần Thị Bích", "BN003 - Lê Hoàng Nam"]

        self.cbo_benh_nhan["values"] = list_bn
        self.cbo_benh_nhan.set(list_bn[0])

        list_dv = []
        if hasattr(self.quan_ly, 'danh_sach_dich_vu') and self.quan_ly.danh_sach_dich_vu:
            list_dv = [f"{dv['ten_dv']} - {dv['gia']:,}đ" for dv in self.quan_ly.danh_sach_dich_vu]

        if not list_dv:
            list_dv = [
                "Khám bệnh nội khoa - 150.000đ",
                "Xét nghiệm máu tổng phân tích - 100.000đ",
                "Siêu âm tổng quát - 200.000đ",
                "Kê đơn thuốc điều trị - 50.000đ"
            ]

        self.cbo_dich_vu["values"] = list_dv
        self.cbo_dich_vu.set(list_dv[0])

    def load_history_phieu_kham(self):
        self.tree_pk.delete(*self.tree_pk.get_children())
        if hasattr(self.quan_ly, 'danh_sach_phieu_kham'):
            for pk in self.quan_ly.danh_sach_phieu_kham:
                self.tree_pk.insert(
                    "", "end",
                    values=(pk.ma_pk, pk.ho_ten_bn, pk.ngay_kham, pk.chan_doan, f"{pk.tong_tien:,}", pk.trang_thai_tt)
                )

    def add_service(self):
        val = self.cbo_dich_vu.get()
        if not val:
            return

        try:
            parts = val.split(" - ")
            ten_dv = parts[0]
            gia_clean = parts[1].replace(".", "").replace(",", "").replace("đ", "").replace("VNĐ", "").strip()
            gia = int(gia_clean)

            self.dich_vu_da_chon.append({"ten_dv": ten_dv, "gia": gia})
            self.tree_dv.insert("", "end", values=(ten_dv, f"{gia:,}"))
            self.update_total()
        except Exception as e:
            messagebox.showerror("Lỗi dữ liệu", f"Không thể lấy giá dịch vụ: {e}")

    def remove_service(self):
        selected = self.tree_dv.selection()
        if selected:
            idx = self.tree_dv.index(selected[0])
            self.tree_dv.delete(selected[0])
            self.dich_vu_da_chon.pop(idx)
            self.update_total()

    def update_total(self):
        tong = sum(item["gia"] for item in self.dich_vu_da_chon)
        self.lbl_tong_tien.config(text=f"TỔNG CHI PHÍ: {tong:,} VNĐ")

    def save_and_pay(self):
        bn_str = self.cbo_benh_nhan.get()
        chan_doan = self.ent_chan_doan.get().strip()

        if not bn_str:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn bệnh nhân!")
            return

        if not chan_doan:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập chẩn đoán!")
            return

        ma_bn = bn_str.split(" - ")[0]
        ho_ten = bn_str.split(" - ")[1]
        tong_tien = sum(item["gia"] for item in self.dich_vu_da_chon)

        ma_pk = f"PK{len(self.quan_ly.danh_sach_phieu_kham) + 1:03d}"

        # Mặc định tạo phiếu ở trạng thái "Chờ thanh toán"
        pk = PhieuKhamBenh(
            ma_pk=ma_pk, ma_bn=ma_bn, ho_ten_bn=ho_ten, bac_si="BS. Nguyễn Văn A",
            ngay_kham="2026-10-27", trieu_chung=self.txt_noidung.get("1.0", "end-1c").strip(),
            chan_doan=chan_doan, dich_vu=self.dich_vu_da_chon, don_thuoc=[], tong_tien=tong_tien,
            trang_thai_tt="Chờ thanh toán"
        )

        self.quan_ly.luu_phieu_kham(pk)
        messagebox.showinfo("Thành công", f"Đã lưu phiếu khám [{ma_pk}]! Trạng thái: CHỜ THANH TOÁN (Chờ Admin duyệt)")

        self.ent_chan_doan.delete(0, tk.END)
        self.txt_noidung.delete("1.0", tk.END)
        self.dich_vu_da_chon.clear()
        self.tree_dv.delete(*self.tree_dv.get_children())
        self.update_total()
        self.load_history_phieu_kham()