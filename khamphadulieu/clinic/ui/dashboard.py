import tkinter as tk
from tkinter import ttk
from .theme import BG, PANEL, TEXT, MUTED, ACCENT, SUCCESS, WARNING, DANGER, BORDER
from .demo_data import dashboard


class DashboardView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        s = dashboard()
        cards = [
            ("Bệnh nhân", s["patients"], ACCENT), ("Bác sĩ đang làm", s["doctors"], SUCCESS),
            ("Lịch khám hôm nay", s["today"], ACCENT), ("Đang chờ khám", s["waiting"], WARNING),
            ("HĐ chưa thanh toán", s["unpaid"], DANGER),
            ("Doanh thu", f"{s['revenue']:,}".replace(",", ".") + " đ", SUCCESS),
        ]
        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", pady=(0, 14))
        for i, (title, value, color) in enumerate(cards):
            row.columnconfigure(i, weight=1, uniform="c")
            c = tk.Frame(row, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
            c.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))
            tk.Frame(c, bg=color, height=4).pack(fill="x")
            tk.Label(c, text=title, bg=PANEL, fg=MUTED, font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=14, pady=(10, 2))
            tk.Label(c, text=str(value), bg=PANEL, fg=TEXT, font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=14, pady=(0, 12))

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        self._table(body, 0, "Lịch khám hôm nay",
                    ("MaLH", "MaBN", "MaBS", "Gio", "TrangThai"),
                    ("Mã lịch", "Mã BN", "Mã BS", "Giờ", "Trạng thái"),
                    [(a[0], a[1], a[2], a[4], a[6]) for a in s["appointments"]])
        self._table(body, 1, "Thuốc sắp hết (tồn < 50)",
                    ("MaThuoc", "TenThuoc", "SoLuongTon"),
                    ("Mã thuốc", "Tên thuốc", "Tồn kho"),
                    [(m[0], m[1], m[3]) for m in s["low_stock"]])

    def _table(self, parent, col, title, cols, heads, rows):
        box = tk.Frame(parent, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        box.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else 8, 0))
        tk.Label(box, text=title, bg=PANEL, fg=TEXT, font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=14, pady=(12, 6))
        tree = ttk.Treeview(box, columns=cols, show="headings", height=8)
        for c, h in zip(cols, heads):
            tree.heading(c, text=h)
            tree.column(c, width=90, anchor="center", stretch=True)
        for r in rows:
            tree.insert("", "end", values=r)
        tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))
