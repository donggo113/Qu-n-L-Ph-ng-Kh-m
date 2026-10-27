# ui/components.py
import tkinter as tk
from tkinter import ttk, messagebox
from db.models import QuanLyPhongKham, BenhNhan
from utils import validate_phone, validate_bhyt


class DataView(tk.Frame):
    def __init__(self, parent, role="admin"):
        super().__init__(parent, bg="#FFFFFF")
        self.quan_ly = QuanLyPhongKham()
        self.role = role
        self.setup_ui()

    def setup_ui(self):
        # Header
        header = tk.Frame(self, bg="#FFFFFF")
        header.pack(fill="x", pady=(0, 10))

        tk.Label(header, text="👤 Quản Lý Hồ Sơ Bệnh Nhân", bg="#FFFFFF", fg="#1C1917",
                 font=("Segoe UI", 16, "bold")).pack(anchor="w")
        tk.Label(header, text="Khai báo thông tin, kiểm tra Regex SĐT & Thẻ BHYT", bg="#FFFFFF", fg="#78716C",
                 font=("Segoe UI", 9)).pack(anchor="w")

        # Form Khai Báo Hồ Sơ
        form = tk.LabelFrame(self, text=" Khai Báo Hồ Sơ Bệnh Nhân Mới ", bg="#FFFFFF", bd=1, relief="solid")
        form.pack(fill="x", pady=(0, 10), ipady=5, ipadx=10)

        fg = tk.Frame(form, bg="#FFFFFF")
        fg.pack(fill="x", padx=10, pady=5)

        tk.Label(fg, text="Mã BN:", bg="#FFFFFF", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w")
        self.ent_ma = ttk.Entry(fg, width=12)
        self.ent_ma.grid(row=0, column=1, padx=(0, 10))

        tk.Label(fg, text="Họ Tên:", bg="#FFFFFF", font=("Segoe UI", 9, "bold")).grid(row=0, column=2, sticky="w")
        self.ent_ten = ttk.Entry(fg, width=22)
        self.ent_ten.grid(row=0, column=3, padx=(0, 10))

        tk.Label(fg, text="Tuổi:", bg="#FFFFFF").grid(row=0, column=4, sticky="w")
        self.ent_tuoi = ttk.Entry(fg, width=8)
        self.ent_tuoi.grid(row=0, column=5, padx=(0, 10))

        tk.Label(fg, text="Giới Tính:", bg="#FFFFFF").grid(row=0, column=6, sticky="w")
        self.cbo_gioi = ttk.Combobox(fg, values=["Nam", "Nữ"], width=8, state="readonly")
        self.cbo_gioi.set("Nam")
        self.cbo_gioi.grid(row=0, column=7)

        # Hàng 2
        tk.Label(fg, text="SĐT (Regex):", bg="#FFFFFF", font=("Segoe UI", 9, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        self.ent_sdt = ttk.Entry(fg, width=12)
        self.ent_sdt.grid(row=1, column=1, padx=(0, 10), pady=5)

        tk.Label(fg, text="BHYT (Regex):", bg="#FFFFFF", font=("Segoe UI", 9, "bold")).grid(row=1, column=2, sticky="w", pady=5)
        self.ent_bhyt = ttk.Entry(fg, width=22)
        self.ent_bhyt.grid(row=1, column=3, padx=(0, 10), pady=5)

        tk.Label(fg, text="Địa Chỉ:", bg="#FFFFFF").grid(row=1, column=4, sticky="w", pady=5)
        self.ent_diachi = ttk.Entry(fg, width=30)
        self.ent_diachi.grid(row=1, column=5, columnspan=3, sticky="w", pady=5)

        # Thanh công cụ Nút Bấm
        tb = tk.Frame(self, bg="#FFFFFF")
        tb.pack(fill="x", pady=(0, 10))

        btn_them = tk.Button(tb, text="➕ Thêm Hồ Sơ", command=self.them_benh_nhan, bg="#EAB308", fg="#FFFFFF",
                             font=("Segoe UI", 9, "bold"), bd=0, padx=10, pady=3, cursor="hand2")
        btn_them.pack(side="left", padx=(0, 5))

        if self.role == "admin":
            btn_xoa = tk.Button(tb, text="❌ Xóa Bệnh Nhân", command=self.xoa_benh_nhan, bg="#EF4444", fg="#FFFFFF",
                                font=("Segoe UI", 9, "bold"), bd=0, padx=10, pady=3, cursor="hand2")
            btn_xoa.pack(side="left", padx=(0, 5))

        btn_crawl = tk.Button(tb, text="🌐 Crawl 50 Bệnh Nhân", command=self.thuc_hien_crawl_benh_nhan,
                              bg="#FEF08A", fg="#854D0E", font=("Segoe UI", 9, "bold"), bd=1, relief="solid", padx=10, pady=3, cursor="hand2")
        btn_crawl.pack(side="left")

        # Bảng danh sách Bệnh Nhân
        style = ttk.Style()
        style.configure("Custom.Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#FEF08A", foreground="#000000")

        cols = ("MaBN", "HoTen", "Tuoi", "GioiTinh", "SDT", "BHYT", "DiaChi")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", style="Custom.Treeview")

        for c, t in zip(cols, ["Mã BN", "Họ & Tên", "Tuổi", "Giới Tính", "Số ĐT", "Thẻ BHYT", "Địa Chỉ"]):
            self.tree.heading(c, text=t)
            self.tree.column(c, anchor="center" if c not in ["HoTen", "DiaChi"] else "w")

        self.tree.pack(fill="both", expand=True)

        self.load_data()

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        try:
            self.quan_ly.load_from_json()
        except Exception as e:
            print("[BENH NHAN] Lỗi đọc JSON:", e)

        for bn in getattr(self.quan_ly, 'danh_sach_benh_nhan', []):
            m = bn.get("ma_id", "") if isinstance(bn, dict) else getattr(bn, 'ma_id', '')
            t = bn.get("ho_ten", "") if isinstance(bn, dict) else getattr(bn, 'ho_ten', '')
            tuoi = bn.get("tuoi", 0) if isinstance(bn, dict) else getattr(bn, 'tuoi', 0)
            g = bn.get("gioi_tinh", "") if isinstance(bn, dict) else getattr(bn, 'gioi_tinh', '')
            s = bn.get("sdt", "") if isinstance(bn, dict) else getattr(bn, 'sdt', '')
            b = bn.get("bhyt", "") if isinstance(bn, dict) else getattr(bn, 'bhyt', '')
            d = bn.get("dia_chi", "") if isinstance(bn, dict) else getattr(bn, 'dia_chi', '')

            self.tree.insert("", "end", values=(m, t, tuoi, g, s, b, d))

    def them_benh_nhan(self):
        m = self.ent_ma.get().strip()
        t = self.ent_ten.get().strip()
        sdt = self.ent_sdt.get().strip()
        bhyt = self.ent_bhyt.get().strip()
        diachi = self.ent_diachi.get().strip()

        if not m or not t:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập Mã BN và Họ tên!")
            return

        # KIỂM TRA REGEX SĐT VÀ BHYT
        if sdt and not validate_phone(sdt):
            messagebox.showerror("Lỗi Regex SĐT", "⚠️ Số điện thoại không hợp lệ! (Phải là 10 số, bắt đầu bằng 03, 05, 07, 08, 09)")
            return

        if bhyt and not validate_bhyt(bhyt):
            messagebox.showerror("Lỗi Regex BHYT", "⚠️ Mã BHYT không hợp lệ! (Phải gồm 15 ký tự, ví dụ: DN4010123456789)")
            return

        bn_new = BenhNhan(
            ma_id=m, ho_ten=t, tuoi=int(self.ent_tuoi.get() or 0),
            gioi_tinh=self.cbo_gioi.get(), sdt=sdt, dia_chi=diachi, bhyt=bhyt
        )

        self.quan_ly.danh_sach_benh_nhan.append(bn_new)
        self.quan_ly.save_to_json()
        self.load_data()
        messagebox.showinfo("Thành công", f"Đã thêm thành công bệnh nhân [{t}]!")

    def xoa_benh_nhan(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Chú ý", "Vui lòng chọn 1 bệnh nhân để xóa!")
            return

        m = self.tree.item(selected[0])["values"][0]
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa bệnh nhân [{m}]?"):
            self.quan_ly.danh_sach_benh_nhan = [
                b for b in self.quan_ly.danh_sach_benh_nhan
                if (b.get("ma_id") if isinstance(b, dict) else getattr(b, 'ma_id', '')) != m
            ]
            self.quan_ly.save_to_json()
            self.load_data()

    def thuc_hien_crawl_benh_nhan(self):
        from utils import crawl_external_patients
        ds_moi = crawl_external_patients(50)
        self.quan_ly.danh_sach_benh_nhan = ds_moi
        self.quan_ly.save_to_json()
        self.load_data()
        messagebox.showinfo("Thành công", "Đã crawl và nạp thành công 50 hồ sơ bệnh nhân!")