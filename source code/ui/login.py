# ui/login.py
import tkinter as tk
from tkinter import ttk, messagebox
from ui.base import AppShell


class LoginPage:
    # Cơ sở dữ liệu tài khoản mẫu
    USERS_DB = {
        "admin": {"password": "admin", "role": "admin"},
        "bacti": {"password": "123456", "role": "user"}
    }

    def __init__(self, window):
        self.window = window
        self.window.title("Hệ Thống Quản Lý Phòng Khám - Đăng Nhập")
        self.window.geometry("450x580")
        self.window.resizable(False, False)

        # Tone màu chủ đạo Vàng Chanh Pastel
        self.BG_MAIN = "#FDFBF7"  # Nền ngoài kem nhạt
        self.BG_CARD = "#FFFFFF"  # Nền khung trắng
        self.COLOR_YELLOW = "#EAB308"  # Vàng chanh điểm nhấn
        self.COLOR_HOVER = "#CA8A04"  # Vàng chanh đậm khi di chuột
        self.COLOR_TEXT = "#1C1917"  # Chữ nâu đen đậm
        self.COLOR_MUTED = "#713F12"  # Chữ nâu vàng đậm
        self.COLOR_BORDER = "#FEF08A"  # Đường viền vàng pastel

        self.window.configure(bg=self.BG_MAIN)
        self.center_window()

        # Khung Card chính căn giữa
        card = tk.Frame(
            self.window, bg=self.BG_CARD,
            highlightbackground=self.COLOR_BORDER, highlightthickness=2
        )
        card.place(relx=0.5, rely=0.5, anchor="center", width=370, height=500)

        # 1. Avatar Icon Biểu tượng hình tròn
        lbl_avatar = tk.Label(
            card, text="🏥", font=("Segoe UI Emoji", 42),
            bg=self.BG_CARD, fg=self.COLOR_YELLOW
        )
        lbl_avatar.pack(pady=(20, 5))

        # 2. Khung nhập Username
        tk.Label(card, text="Tên đăng nhập", bg=self.BG_CARD, fg=self.COLOR_MUTED, font=("Segoe UI", 9, "bold")).pack(
            anchor="w", padx=35)

        frame_user = tk.Frame(card, bg=self.BG_CARD, highlightbackground=self.COLOR_BORDER, highlightthickness=1)
        frame_user.pack(fill="x", padx=35, pady=(3, 10), ipady=3)

        tk.Label(frame_user, text="👤 ", bg=self.BG_CARD, fg=self.COLOR_YELLOW, font=("Segoe UI", 10)).pack(side="left",
                                                                                                           padx=(5, 0))
        self.ent_user = tk.Entry(frame_user, bd=0, bg=self.BG_CARD, fg=self.COLOR_TEXT, font=("Segoe UI", 10))
        self.ent_user.pack(side="left", fill="x", expand=True, padx=5)
        self.ent_user.insert(0, "admin")

        # 3. Khung nhập Password
        tk.Label(card, text="Mật khẩu", bg=self.BG_CARD, fg=self.COLOR_MUTED, font=("Segoe UI", 9, "bold")).pack(
            anchor="w", padx=35)

        frame_pass = tk.Frame(card, bg=self.BG_CARD, highlightbackground=self.COLOR_BORDER, highlightthickness=1)
        frame_pass.pack(fill="x", padx=35, pady=(3, 8), ipady=3)

        tk.Label(frame_pass, text="🔒 ", bg=self.BG_CARD, fg=self.COLOR_YELLOW, font=("Segoe UI", 10)).pack(side="left",
                                                                                                           padx=(5, 0))
        self.ent_pass = tk.Entry(frame_pass, show="*", bd=0, bg=self.BG_CARD, fg=self.COLOR_TEXT, font=("Segoe UI", 10))
        self.ent_pass.pack(side="left", fill="x", expand=True, padx=5)
        self.ent_pass.insert(0, "admin")

        # Nút ẩn/hiện mật khẩu
        self.is_show_pass = False
        self.btn_eye = tk.Button(
            frame_pass, text="👁️", bd=0, bg=self.BG_CARD, activebackground=self.BG_CARD,
            cursor="hand2", command=self.toggle_password
        )
        self.btn_eye.pack(side="right", padx=5)

        # 4. Hàng tùy chọn: Ghi nhớ & Quên mật khẩu
        row_opt = tk.Frame(card, bg=self.BG_CARD)
        row_opt.pack(fill="x", padx=35, pady=(0, 15))

        self.var_remember = tk.BooleanVar(value=True)
        chk_remember = tk.Checkbutton(
            row_opt, text="Ghi nhớ", variable=self.var_remember,
            bg=self.BG_CARD, fg=self.COLOR_MUTED, activebackground=self.BG_CARD,
            font=("Segoe UI", 8, "bold")
        )
        chk_remember.pack(side="left")

        lbl_forgot = tk.Label(
            row_opt, text="Quên mật khẩu?", bg=self.BG_CARD, fg=self.COLOR_MUTED,
            font=("Segoe UI", 8, "underline"), cursor="hand2"
        )
        lbl_forgot.pack(side="right")
        lbl_forgot.bind("<Button-1>", lambda e: self.open_forgot_pwd())

        # 5. Nút ĐĂNG NHẬP (Chính - Màu vàng chanh)
        btn_login = tk.Button(
            card, text="ĐĂNG NHẬP", command=self.handle_login,
            font=("Segoe UI", 10, "bold"), bg=self.COLOR_YELLOW, fg="#FFFFFF",
            activebackground=self.COLOR_HOVER, activeforeground="#FFFFFF",
            relief="flat", bd=0, cursor="hand2"
        )
        btn_login.pack(fill="x", padx=35, ipady=7)

        # 6. Nút TẠO TÀI KHOẢN MỚI (Nền nhạt viền vàng)
        btn_register = tk.Button(
            card, text="TẠO TÀI KHOẢN", command=self.open_register,
            font=("Segoe UI", 9, "bold"), bg="#FEF9C3", fg=self.COLOR_MUTED,
            activebackground="#FEF08A", activeforeground=self.COLOR_MUTED,
            highlightbackground=self.COLOR_YELLOW, highlightthickness=1,
            relief="flat", bd=0, cursor="hand2"
        )
        btn_register.pack(fill="x", padx=35, pady=(10, 0), ipady=6)

        # Bắt sự kiện phím Enter
        self.window.bind("<Return>", lambda e: self.handle_login())

    def center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")

    def toggle_password(self):
        if self.is_show_pass:
            self.ent_pass.config(show="*")
            self.is_show_pass = False
        else:
            self.ent_pass.config(show="")
            self.is_show_pass = True

    def handle_login(self):
        user = self.ent_user.get().strip()
        pwd = self.ent_pass.get().strip()

        if user in self.USERS_DB and self.USERS_DB[user]["password"] == pwd:
            role = self.USERS_DB[user]["role"]

            for widget in self.window.winfo_children():
                widget.destroy()

            self.window.resizable(True, True)
            self.window.geometry("1100x680")
            self.window.minsize(980, 600)
            self.center_window()

            AppShell(self.window, username=user, role=role)
        else:
            messagebox.showerror("Lỗi đăng nhập", "Tên tài khoản hoặc mật khẩu không đúng!", parent=self.window)

    def open_register(self):
        win = tk.Toplevel(self.window)
        win.title("Đăng Ký Tài Khoản Mới")
        win.geometry("360x340")
        win.configure(bg=self.BG_MAIN)
        win.resizable(False, False)
        win.grab_set()

        tk.Label(win, text="✨ TẠO TÀI KHOẢN MỚI", bg=self.BG_MAIN, fg=self.COLOR_YELLOW,
                 font=("Segoe UI", 12, "bold")).pack(pady=(15, 10))

        tk.Label(win, text="Tên đăng nhập:", bg=self.BG_MAIN, fg=self.COLOR_MUTED, font=("Segoe UI", 9, "bold")).pack(
            anchor="w", padx=25)
        ent_u = ttk.Entry(win)
        ent_u.pack(fill="x", padx=25, pady=(2, 8))

        tk.Label(win, text="Mật khẩu:", bg=self.BG_MAIN, fg=self.COLOR_MUTED, font=("Segoe UI", 9, "bold")).pack(
            anchor="w", padx=25)
        ent_p = ttk.Entry(win, show="*")
        ent_p.pack(fill="x", padx=25, pady=(2, 8))

        tk.Label(win, text="Loại tài khoản:", bg=self.BG_MAIN, fg=self.COLOR_MUTED, font=("Segoe UI", 9, "bold")).pack(
            anchor="w", padx=25)
        cbo_r = ttk.Combobox(win, values=["Người dùng (Bác sĩ/Lễ tân)", "Quản trị viên (Admin)"], state="readonly")
        cbo_r.set("Người dùng (Bác sĩ/Lễ tân)")
        cbo_r.pack(fill="x", padx=25, pady=(2, 12))

        def save():
            u, p = ent_u.get().strip(), ent_p.get().strip()
            r = "admin" if "Admin" in cbo_r.get() else "user"
            if not u or not p:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ tên tài khoản và mật khẩu!", parent=win)
                return
            if u in self.USERS_DB:
                messagebox.showerror("Lỗi", "Tài khoản này đã tồn tại!", parent=win)
                return
            self.USERS_DB[u] = {"password": p, "role": r}
            messagebox.showinfo("Thành công", f"Đã đăng ký tài khoản '{u}' thành công!", parent=win)

            self.ent_user.delete(0, tk.END)
            self.ent_user.insert(0, u)
            self.ent_pass.delete(0, tk.END)
            win.destroy()

        tk.Button(
            win, text="XÁC NHẬN ĐĂNG KÝ", command=save,
            bg=self.COLOR_YELLOW, fg="#FFFFFF", font=("Segoe UI", 9, "bold"),
            relief="flat", bd=0, cursor="hand2"
        ).pack(fill="x", padx=25, ipady=6)

    def open_forgot_pwd(self):
        win = tk.Toplevel(self.window)
        win.title("Đổi Mật Khẩu")
        win.geometry("340x240")
        win.configure(bg=self.BG_MAIN)
        win.resizable(False, False)
        win.grab_set()

        tk.Label(win, text="🔒 ĐỔI MẬT KHẨU", bg=self.BG_MAIN, fg=self.COLOR_YELLOW, font=("Segoe UI", 12, "bold")).pack(
            pady=(15, 10))

        tk.Label(win, text="Tên tài khoản:", bg=self.BG_MAIN, fg=self.COLOR_MUTED, font=("Segoe UI", 9, "bold")).pack(
            anchor="w", padx=25)
        ent_u = ttk.Entry(win)
        ent_u.pack(fill="x", padx=25, pady=(2, 8))

        tk.Label(win, text="Mật khẩu mới:", bg=self.BG_MAIN, fg=self.COLOR_MUTED, font=("Segoe UI", 9, "bold")).pack(
            anchor="w", padx=25)
        ent_p = ttk.Entry(win, show="*")
        ent_p.pack(fill="x", padx=25, pady=(2, 12))

        def save():
            u, p = ent_u.get().strip(), ent_p.get().strip()
            if not u or not p:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin!", parent=win)
                return
            if u not in self.USERS_DB:
                messagebox.showerror("Lỗi", "Tài khoản không tồn tại trong hệ thống!", parent=win)
                return
            self.USERS_DB[u]["password"] = p
            messagebox.showinfo("Thành công", "Đã đổi mật khẩu thành công!", parent=win)
            win.destroy()

        tk.Button(
            win, text="LƯU MẬT KHẨU MỚI", command=save,
            bg=self.COLOR_YELLOW, fg="#FFFFFF", font=("Segoe UI", 9, "bold"),
            relief="flat", bd=0, cursor="hand2"
        ).pack(fill="x", padx=25, ipady=6)