# ui/quanlythuoc.py
import tkinter as tk
from tkinter import ttk, messagebox
from .theme import BG, PANEL, ACCENT
from db.models import QuanLyPhongKham, Thuoc

class MedicineManagementView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.quan_ly = QuanLyPhongKham()
        self.setup_ui()

    def setup_ui(self):
        # Header
        top_bar = tk.Frame(self, bg=PANEL, padx=10, pady=10)
        top_bar.pack(fill="x")
        tk.Label(top_bar, text="QUẢN LÝ KHO THUỐC", bg=PANEL, fg=ACCENT, font=("Segoe UI", 12, "bold")).pack(side="left")

        # Form nhập liệu
        box_form = tk.LabelFrame(self, text=" Thông tin thuốc ", bg=PANEL, fg="#854D0E", font=("Segoe UI", 9, "bold"))
        box_form.pack(fill="x", padx=10, pady=10, ipadx=5, ipady=5)

        grid = tk.Frame(box_form, bg=PANEL)
        grid.pack(fill="x", padx=5, pady=5)

        tk.Label(grid, text="Mã thuốc:", bg=PANEL).grid(row=0, column=0, sticky="w")
        self.ent_ma = ttk.Entry(grid, width=15)
        self.ent_ma.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(grid, text="Tên thuốc:", bg=PANEL).grid(row=0, column=2, sticky="w")
        self.ent_ten = ttk.Entry(grid, width=25)
        self.ent_ten.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(grid, text="Đơn vị tính:", bg=PANEL).grid(row=1, column=0, sticky="w")
        self.cbo_donvi = ttk.Combobox(grid, values=["Vỉ", "Hộp", "Chai", "Viên", "Gói"], width=13, state="readonly")
        self.cbo_donvi.set("Hộp")
        self.cbo_donvi.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(grid, text="Đơn giá (VNĐ):", bg=PANEL).grid(row=1, column=2, sticky="w")
        self.ent_gia = ttk.Entry(grid, width=15)
        self.ent_gia.grid(row=1, column=3, padx=5, pady=5)

        tk.Label(grid, text="Số lượng tồn:", bg=PANEL).grid(row=1, column=4, sticky="w")
        self.ent_ton = ttk.Entry(grid, width=10)
        self.ent_ton.grid(row=1, column=5, padx=5, pady=5)

        btn_box = tk.Frame(box_form, bg=PANEL)
        btn_box.pack(anchor="e", padx=5, pady=5)
        ttk.Button(btn_box, text="➕ Thêm Thuốc", command=self.add_medicine).pack(side="left", padx=3)
        ttk.Button(btn_box, text="🗑️ Xóa Thuốc", command=self.delete_medicine).pack(side="left", padx=3)

        # Thanh Tìm kiếm
        search_frame = tk.Frame(self, bg=BG, padx=10, pady=5)
        search_frame.pack(fill="x")
        tk.Label(search_frame, text="🔍 Tìm thuốc:", bg=BG, font=("Segoe UI", 9, "bold")).pack(side="left")
        self.ent_search = ttk.Entry(search_frame, width=25)
        self.ent_search.pack(side="left", padx=5)
        self.ent_search.bind("<KeyRelease>", self.search_medicine)

        # Bảng Treeview
        cols = ("Mã Thuốc", "Tên Thuốc", "Đơn Vị", "Đơn Giá (VNĐ)", "Số Lượng Tồn")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.load_data()

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        ds_thuoc = getattr(self.quan_ly, 'danh_sach_thuoc', [])
        for t in ds_thuoc:
            self.tree.insert("", "end", values=(t.ma_thuoc, t.ten_thuoc, t.don_vi, f"{t.don_gia:,}", t.so_luong_ton))

    def add_medicine(self):
        ma = self.ent_ma.get().strip()
        ten = self.ent_ten.get().strip()
        try:
            gia = float(self.ent_gia.get().strip())
            ton = int(self.ent_ton.get().strip())
        except ValueError:
            messagebox.showwarning("Cảnh báo", "Đơn giá và Số lượng tồn phải là số!")
            return

        if not ma or not ten:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ mã và tên thuốc!")
            return

        moi = Thuoc(ma, ten, self.cbo_donvi.get(), gia, ton)
        if not hasattr(self.quan_ly, 'danh_sach_thuoc'):
            self.quan_ly.danh_sach_thuoc = []
        self.quan_ly.danh_sach_thuoc.append(moi)
        self.quan_ly.save_to_json()
        self.load_data()
        messagebox.showinfo("Thành công", f"Đã thêm thuốc {ten} vào kho!")

    def delete_medicine(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Chú ý", "Vui lòng chọn thuốc cần xóa!")
            return
        ma_thuoc = self.tree.item(selected[0])["values"][0]
        self.quan_ly.danh_sach_thuoc = [t for t in self.quan_ly.danh_sach_thuoc if t.ma_thuoc != ma_thuoc]
        self.quan_ly.save_to_json()
        self.load_data()

    def search_medicine(self, event=None):
        kw = self.ent_search.get().strip().lower()
        self.tree.delete(*self.tree.get_children())
        for t in getattr(self.quan_ly, 'danh_sach_thuoc', []):
            if kw in t.ma_thuoc.lower() or kw in t.ten_thuoc.lower():
                self.tree.insert("", "end", values=(t.ma_thuoc, t.ten_thuoc, t.don_vi, f"{t.don_gia:,}", t.so_luong_ton))