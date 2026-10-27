"""Điểm khởi động: python main.py"""
import tkinter as tk
from tkinter import ttk, messagebox

from config import APP_TITLE
from services.app_context import AppContext
from services.stats_service import visits_by_day, revenue_by_month
from ui.widgets.bar_chart import BarChart


class LoginWindow(tk.Tk):
    def __init__(self, ctx):
        super().__init__()
        self.ctx, self.user = ctx, None
        self.title(f"{APP_TITLE} - Đăng nhập")
        frm = ttk.Frame(self, padding=20)
        frm.grid()
        ttk.Label(frm, text="Tên đăng nhập").grid(row=0, column=0, sticky="w")
        self.e_user = ttk.Entry(frm)
        self.e_user.grid(row=0, column=1, pady=4)
        ttk.Label(frm, text="Mật khẩu").grid(row=1, column=0, sticky="w")
        self.e_pw = ttk.Entry(frm, show="*")
        self.e_pw.grid(row=1, column=1, pady=4)
        ttk.Button(frm, text="Đăng nhập", command=self.do_login).grid(row=2, column=0, columnspan=2, pady=8)
        self.bind("<Return>", lambda e: self.do_login())

    def do_login(self):
        u = self.ctx.auth.login(self.e_user.get().strip(), self.e_pw.get())
        if u:
            self.user = u
            self.destroy()
        else:
            messagebox.showerror("Lỗi", "Sai tên đăng nhập hoặc mật khẩu")


class MainWindow(tk.Tk):
    def __init__(self, ctx, user):
        super().__init__()
        self.ctx, self.user = ctx, user
        self.title(f"{APP_TITLE} - {user.username} ({user.role})")
        self.geometry("900x560")
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        # TODO nhóm: tách mỗi tab thành file riêng trong ui/tabs/
        t_patient = ttk.Frame(nb)
        nb.add(t_patient, text="Bệnh nhân")
        cols = ("id", "name", "phone", "dob", "insurance_code")
        self.tree = ttk.Treeview(t_patient, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
        self.tree.pack(fill="both", expand=True)
        for p in ctx.patients.get_all():
            self.tree.insert("", "end", values=tuple(p.to_dict()[c] for c in cols))

        if ctx.auth.can_view_stats(user):
            t_stats = ttk.Frame(nb)
            nb.add(t_stats, text="Thống kê")
            chart = BarChart(t_stats)
            chart.pack(padx=10, pady=10)
            chart.draw(revenue_by_month(ctx.visits.get_all()), "Doanh thu theo tháng")
            chart2 = BarChart(t_stats)
            chart2.pack(padx=10, pady=10)
            chart2.draw(visits_by_day(ctx.visits.get_all()), "Lượt khám theo ngày")

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        if messagebox.askyesno("Thoát", "Bạn có chắc muốn thoát?"):
            self.destroy()


def main():
    ctx = AppContext()
    login = LoginWindow(ctx)
    login.mainloop()
    if login.user:
        MainWindow(ctx, login.user).mainloop()


if __name__ == "__main__":
    main()
