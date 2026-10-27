import tkinter as tk
from tkinter import ttk, messagebox
from .theme import BG, PANEL, TEXT, MUTED, configure_style

DARK = "#0F172A"


class LoginPage:
    def __init__(self, root):
        self.root = root
        root.title("Đăng nhập - Quản lý Phòng khám")
        root.geometry("1120x680")
        root.minsize(980, 620)
        root.configure(bg=BG)
        configure_style(root)
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.build()
        root.bind("<Return>", lambda e: self.check_login())

    def build(self):
        left = tk.Frame(self.root, bg=DARK, width=610)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)
        tk.Label(left, text="✚ PHÒNG KHÁM", bg=DARK, fg="white", font=("Segoe UI", 26, "bold")).pack(anchor="w", padx=44, pady=(60, 8))
        tk.Label(left, text="Quản lý bệnh nhân, lịch khám, đơn thuốc\nvà thanh toán trong một nơi.",
                 bg=DARK, fg="#CBD5E1", font=("Segoe UI", 15), justify="left").pack(anchor="w", padx=44, pady=10)
        tk.Label(left, text="BỆNH NHÂN • LỊCH KHÁM • ĐƠN THUỐC • HÓA ĐƠN",
                 bg=DARK, fg="#64748B", font=("Segoe UI", 9, "bold")).pack(side="bottom", pady=30)

        right = tk.Frame(self.root, bg=BG)
        right.pack(side="right", fill="both", expand=True)
        card = tk.Frame(right, bg=PANEL, highlightbackground="#D9E2EF", highlightthickness=1, width=410, height=455)
        card.place(relx=.5, rely=.5, anchor="center")
        card.pack_propagate(False)
        tk.Label(card, text="Chào mừng trở lại", bg=PANEL, fg=TEXT, font=("Segoe UI", 22, "bold")).pack(pady=(48, 5))
        tk.Label(card, text="Đăng nhập hệ thống phòng khám", bg=PANEL, fg=MUTED, font=("Segoe UI", 10)).pack(pady=(0, 28))
        tk.Label(card, text="Tài khoản", bg=PANEL, fg=TEXT, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=48)
        e1 = ttk.Entry(card, textvariable=self.username)
        e1.pack(fill="x", padx=48, pady=(6, 18), ipady=5)
        tk.Label(card, text="Mật khẩu", bg=PANEL, fg=TEXT, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=48)
        ttk.Entry(card, textvariable=self.password, show="•").pack(fill="x", padx=48, pady=(6, 24), ipady=5)
        ttk.Button(card, text="ĐĂNG NHẬP", style="Primary.TButton", command=self.check_login).pack(fill="x", padx=48, ipady=5)
        tk.Label(card, text="Tài khoản demo: admin / admin", bg=PANEL, fg=MUTED, font=("Segoe UI", 9)).pack(pady=22)
        e1.focus_set()

    def check_login(self):
        if self.username.get().strip() == "admin" and self.password.get() == "admin":
            from .base import AppShell
            name = self.username.get().strip()
            self.root.unbind("<Return>")
            for w in self.root.winfo_children():
                w.destroy()
            AppShell(self.root, name)
        else:
            messagebox.showerror("Đăng nhập thất bại", "Sai tài khoản hoặc mật khẩu.")
