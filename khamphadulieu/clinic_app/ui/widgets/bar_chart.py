"""Biểu đồ cột vẽ bằng Canvas. data: dict {nhãn: giá trị}."""
import tkinter as tk


class BarChart(tk.Canvas):
    def __init__(self, master, width=600, height=300, **kw):
        super().__init__(master, width=width, height=height, bg="white", **kw)
        self.w, self.h = width, height

    def draw(self, data: dict, title=""):
        self.delete("all")
        self.create_text(self.w / 2, 14, text=title, font=("Arial", 12, "bold"))
        if not data:
            self.create_text(self.w / 2, self.h / 2, text="Chưa có dữ liệu")
            return
        left, bottom, top = 50, self.h - 40, 40
        mx = max(data.values()) or 1
        slot = (self.w - left - 20) / len(data)
        self.create_line(left, top, left, bottom)
        self.create_line(left, bottom, self.w - 10, bottom)
        for i, (label, val) in enumerate(data.items()):
            x0 = left + i * slot + slot * 0.15
            x1 = left + (i + 1) * slot - slot * 0.15
            y = bottom - (val / mx) * (bottom - top)
            self.create_rectangle(x0, y, x1, bottom, fill="#3b82f6")
            self.create_text((x0 + x1) / 2, y - 8, text=f"{val:g}")
            self.create_text((x0 + x1) / 2, bottom + 12, text=label, font=("Arial", 8))
