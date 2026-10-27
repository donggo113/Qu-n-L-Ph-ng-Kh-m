import importlib
import tkinter as tk
from tkinter import ttk, messagebox
from .theme import BG, SIDEBAR, TEXT, MUTED, configure_style

# (biểu tượng, tên menu, module, class, tiêu đề, mô tả)
PAGES = [
    ("⌂", "Tổng quan", "dashboard", "DashboardView", "Tổng quan", "Tình hình hoạt động của phòng khám"),
    ("♙", "Bệnh nhân", "views", "PatientsView", "Bệnh nhân", "Quản lý hồ sơ bệnh nhân"),
    ("✚", "Chuyên khoa", "views", "SpecialtiesView", "Chuyên khoa", "Danh mục các chuyên khoa"),
    ("♟", "Bác sĩ", "views", "DoctorsView", "Bác sĩ", "Quản lý đội ngũ bác sĩ"),
    ("▤", "Lịch khám", "views", "AppointmentsView", "Lịch khám", "Đặt lịch và theo dõi hàng chờ khám"),
    ("▣", "Phiếu khám", "views", "VisitsView", "Phiếu khám", "Chẩn đoán, lời dặn và hẹn tái khám"),
    ("◫", "Thuốc", "views", "MedicinesView", "Thuốc", "Danh mục thuốc và tồn kho"),
    ("℞", "Đơn thuốc", "views", "PrescriptionsView", "Đơn thuốc", "Thuốc kê theo từng phiếu khám"),
    ("₫", "Hóa đơn", "views", "InvoicesView", "Hóa đơn", "Viện phí, tiền thuốc và thanh toán"),
]


class AppShell:
    def __init__(self, root, username="admin"):
        self.root = root
        root.title("Quản lý Phòng khám")
        root.geometry("1250x760")
        root.minsize(1050, 680)
        root.configure(bg=BG)
        configure_style(root)

        self.sidebar = tk.Frame(root, bg=SIDEBAR, width=245)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        tk.Label(self.sidebar, text="✚ PHÒNG KHÁM", bg=SIDEBAR, fg="white",
                 font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=22, pady=(24, 2))
        tk.Label(self.sidebar, text="Hệ thống quản lý", bg=SIDEBAR, fg="#94A3B8",
                 font=("Segoe UI", 9)).pack(anchor="w", padx=22)
        tk.Frame(self.sidebar, bg="#24324A", height=1).pack(fill="x", padx=18, pady=14)
        tk.Label(self.sidebar, text="MENU CHÍNH", bg=SIDEBAR, fg="#64748B",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=22, pady=(0, 5))

        self.buttons = []
        for i, page in enumerate(PAGES):
            b = tk.Button(self.sidebar, text=f"  {page[0]}    {page[1]}", anchor="w", relief="flat", bd=0,
                          bg=SIDEBAR, fg="#CBD5E1", activebackground="#1E293B", activeforeground="white",
                          font=("Segoe UI", 10, "bold"), padx=12, pady=11, cursor="hand2",
                          command=lambda i=i: self.show(i))
            b.pack(fill="x", padx=9, pady=2)
            self.buttons.append(b)

        bottom = tk.Frame(self.sidebar, bg=SIDEBAR)
        bottom.pack(side="bottom", fill="x", pady=15)
        tk.Frame(bottom, bg="#24324A", height=1).pack(fill="x", padx=18, pady=(0, 10))
        tk.Label(bottom, text=f"●  {username}", bg=SIDEBAR, fg="#CBD5E1",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=22, pady=4)
        ttk.Button(bottom, text="Đăng xuất", command=self.logout).pack(fill="x", padx=18, pady=7)

        self.content = tk.Frame(root, bg=BG)
        self.content.pack(side="right", fill="both", expand=True)
        self.show(0)

    def show(self, index):
        icon, name, module, cls, title, subtitle = PAGES[index]
        for i, b in enumerate(self.buttons):   # tô sáng mục đang chọn
            b.configure(bg="#1E293B" if i == index else SIDEBAR, fg="white" if i == index else "#CBD5E1")
        for w in self.content.winfo_children():
            w.destroy()
        top = tk.Frame(self.content, bg=BG)
        top.pack(fill="x", padx=30, pady=(22, 8))
        tk.Label(top, text=title, bg=BG, fg=TEXT, font=("Segoe UI", 22, "bold")).pack(anchor="w")
        tk.Label(top, text=subtitle, bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", pady=(2, 0))
        view = getattr(importlib.import_module(f".{module}", __package__), cls)
        view(self.content).pack(fill="both", expand=True, padx=30, pady=4)

    def logout(self):
        if messagebox.askyesno("Đăng xuất", "Bạn có muốn đăng xuất không?"):
            from .login import LoginPage
            self.root.unbind("<Return>")
            for w in self.root.winfo_children():
                w.destroy()
            LoginPage(self.root)
