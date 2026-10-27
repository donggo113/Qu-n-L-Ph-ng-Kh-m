# ui/base.py
import tkinter as tk
from tkinter import ttk, messagebox
from .theme import BG, PANEL, TEXT, ACCENT, MUTED
from .dashboard import DashboardView


class AppShell(tk.Frame):
    def __init__(self, parent, username="admin", role="admin", **kwargs):
        super().__init__(parent, bg="#FAF8F5")
        self.parent = parent
        self.username = username
        self.role = role
        self.pack(fill="both", expand=True)

        self.setup_sidebar()

        self.content = tk.Frame(self, bg="#FAF8F5")
        self.content.pack(side="right", fill="both", expand=True, padx=20, pady=15)

        # Mặc định hiển thị Bảng điều khiển (Dashboard)
        self.show_dashboard()

    def setup_sidebar(self):
        sidebar = tk.Frame(self, bg="#FEF9C3", width=230)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        header_frame = tk.Frame(sidebar, bg="#FEF9C3", pady=20, padx=15)
        header_frame.pack(fill="x")

        lbl_icon = tk.Label(header_frame, text="🏥 PHÒNG KHÁM", bg="#FEF9C3", fg="#854D0E",
                            font=("Segoe UI", 14, "bold"))
        lbl_icon.pack(anchor="w")

        tk.Frame(header_frame, bg="#EAB308", height=1).pack(fill="x", pady=(10, 0))

        tk.Label(sidebar, text="MENU QUẢN LÝ", bg="#FEF9C3", fg="#A16207", font=("Segoe UI", 8, "bold")).pack(
            anchor="w", padx=15, pady=(10, 10))

        btn_style = {
            "bg": "#FEF9C3",
            "fg": "#713F12",
            "activebackground": "#FEF08A",
            "activeforeground": "#854D0E",
            "font": ("Segoe UI", 10, "bold"),
            "anchor": "w",
            "relief": "flat",
            "bd": 0,
            "padx": 15,
            "pady": 8,
            "cursor": "hand2"
        }

        self.btn_dash = tk.Button(sidebar, text="📊 Tổng Quan ", command=self.show_dashboard, **btn_style)
        self.btn_dash.pack(fill="x", pady=2)

        self.btn_app = tk.Button(sidebar, text="📑 Đăng ký & Đặt lịch", command=self.show_appointments, **btn_style)
        self.btn_app.pack(fill="x", pady=2)

        self.btn_med = tk.Button(sidebar, text="🩺 Khám bệnh & Dịch vụ", command=self.show_medical_records, **btn_style)
        self.btn_med.pack(fill="x", pady=2)

        self.btn_pat = tk.Button(sidebar, text="👤 Quản lý Bệnh nhân", command=self.show_patients, **btn_style)
        self.btn_pat.pack(fill="x", pady=2)

        # Nút Quản lý Kho Thuốc
        self.btn_med_store = tk.Button(sidebar, text="💊 Quản lý Kho Thuốc", command=self.show_medicines, **btn_style)
        self.btn_med_store.pack(fill="x", pady=2)

        # Nút Đăng ký & Xếp Lịch Làm
        self.btn_shifts = tk.Button(sidebar, text="📅 Đăng ký & Xếp lịch làm", command=self.show_shifts, **btn_style)
        self.btn_shifts.pack(fill="x", pady=2)

        # Thông tin user ở góc dưới
        bottom_frame = tk.Frame(sidebar, bg="#FEF9C3", pady=15, padx=15)
        bottom_frame.pack(side="bottom", fill="x")

        lbl_user = tk.Label(bottom_frame, text=f"• {self.username}\n ({self.role.upper()})", bg="#FEF9C3", fg="#854D0E",
                            font=("Segoe UI", 9, "bold"), justify="left")
        lbl_user.pack(anchor="w", pady=(0, 10))

        btn_logout = tk.Button(
            bottom_frame, text="Đăng xuất", command=self.handle_logout,
            bg="#FEF08A", fg="#854D0E", font=("Segoe UI", 9, "bold"),
            relief="flat", bd=0, pady=6, cursor="hand2"
        )
        btn_logout.pack(fill="x")

    def clear_content(self):
        for child in self.content.winfo_children():
            child.destroy()

    def show_dashboard(self):
        self.clear_content()
        view = DashboardView(self.content)
        view.pack(fill="both", expand=True)

    def show_appointments(self):
        self.clear_content()
        from .dangkylichkham import AppointmentRegistrationView
        view = AppointmentRegistrationView(self.content)
        view.pack(fill="both", expand=True)

    def show_medical_records(self):
        self.clear_content()
        from .khambenh_dichvu import MedicalServiceView
        # Truyền role tài khoản hiện tại vào view để phân quyền Admin Duyệt Thanh Toán
        view = MedicalServiceView(self.content, role=self.role)
        view.pack(fill="both", expand=True)

    def show_patients(self):
        self.clear_content()
        from .components import DataView
        view = DataView(self.content)
        view.pack(fill="both", expand=True)

    def show_medicines(self):
        self.clear_content()
        from .quanlythuoc import MedicineManagementView
        view = MedicineManagementView(self.content)
        view.pack(fill="both", expand=True)

    def show_shifts(self):
        self.clear_content()
        from .phanlichlam import ShiftManagementView
        view = ShiftManagementView(self.content, username=self.username, role=self.role)
        view.pack(fill="both", expand=True)

    def handle_logout(self):
        if messagebox.askyesno("Đăng xuất", "Bạn có chắc chắn muốn đăng xuất không?", parent=self.parent):
            for widget in self.parent.winfo_children():
                widget.destroy()
            from .login import LoginPage
            LoginPage(self.parent)


BaseLayout = AppShell