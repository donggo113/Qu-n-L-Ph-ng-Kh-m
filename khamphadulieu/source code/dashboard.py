import tkinter as tk
from .theme import BG, PANEL, TEXT, MUTED, ACCENT, SUCCESS, WARNING, DANGER, BORDER

class DashboardView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)

        data = {
            "total_patients": 142,
            "today_appointments": 18,
            "completed_exams": 12,
            "total_revenue": 15400000,
            "monthly_visits": [("T1", 85), ("T2", 92), ("T3", 110), ("T4", 98), ("T5", 130), ("T6", 142)],
            "monthly_revenue": [("T1", 9.5), ("T2", 10.2), ("T3", 12.0), ("T4", 11.5), ("T5", 14.2), ("T6", 15.4)] # Triệu VNĐ
        }

        stats_frame = tk.Frame(self, bg=BG)
        stats_frame.pack(fill="x", pady=(0, 15))

        cards = [
            ("TỔNG BỆNH NHÂN", data["total_patients"], "Hồ sơ", ACCENT),
            ("LỊCH KHÁM HÔM NAY", data["today_appointments"], "Lượt hẹn", WARNING),
            ("ĐÃ KHÁM HÔM NAY", data["completed_exams"], "Hoàn thành", SUCCESS),
            ("DOANH THU THÁNG", f"{data['total_revenue']:,} đ", "VND", DANGER),
        ]

        for i, (title, val, unit, color) in enumerate(cards):
            card = tk.Frame(stats_frame, bg=PANEL, highlightbackground=BORDER, highlightthickness=1, height=85)
            card.pack(side="left", fill="both", expand=True, padx=(0 if i==0 else 5, 0))
            card.pack_propagate(False)

            tk.Frame(card, bg=color, width=5).pack(side="left", fill="y")
            tk.Label(card, text=title, bg=PANEL, fg=MUTED, font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=12, pady=(10, 0))

            row = tk.Frame(card, bg=PANEL)
            row.pack(anchor="w", padx=12)
            tk.Label(row, text=str(val), bg=PANEL, fg=TEXT, font=("Segoe UI", 16, "bold")).pack(side="left")
            tk.Label(row, text=f" {unit}", bg=PANEL, fg=MUTED, font=("Segoe UI", 8)).pack(side="left", pady=(5, 0))

        charts_frame = tk.Frame(self, bg=BG)
        charts_frame.pack(fill="both", expand=True)

        self.create_bar_chart(charts_frame, "THỐNG KÊ LƯỢT KHÁM THEO THÁNG", data["monthly_visits"], ACCENT, col=0)
        self.create_bar_chart(charts_frame, "DOANH THU THEO THÁNG (Triệu VNĐ)", data["monthly_revenue"], SUCCESS, col=1)

    def create_bar_chart(self, parent, title, chart_data, bar_color, col):
        box = tk.Frame(parent, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        box.pack(side="left", fill="both", expand=True, padx=(0 if col==0 else 8, 0))

        tk.Label(box, text=title, bg=PANEL, fg=TEXT, font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=15, pady=12)

        canvas = tk.Canvas(box, bg=PANEL, highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        def draw(event):
            canvas.delete("all")
            w, h = event.width, event.height
            padding_bottom, padding_top = 30, 20
            chart_h = h - padding_bottom - padding_top

            max_val = max(v for _, v in chart_data) * 1.2 or 1
            num_bars = len(chart_data)
            bar_width = (w / num_bars) * 0.45
            spacing = w / num_bars

            canvas.create_line(10, h - padding_bottom, w - 10, h - padding_bottom, fill=BORDER, width=2)

            for i, (label, val) in enumerate(chart_data):
                x0 = i * spacing + (spacing - bar_width) / 2
                y0 = h - padding_bottom - (val / max_val * chart_h)
                x1 = x0 + bar_width
                y1 = h - padding_bottom

                canvas.create_rectangle(x0, y0, x1, y1, fill=bar_color, outline="")
                canvas.create_text((x0 + x1) / 2, y0 - 10, text=str(val), fill=TEXT, font=("Segoe UI", 8, "bold"))
                canvas.create_text((x0 + x1) / 2, h - 12, text=label, fill=MUTED, font=("Segoe UI", 9))

        canvas.bind("<Configure>", draw)