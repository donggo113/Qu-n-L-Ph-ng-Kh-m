import tkinter as tk
from tkinter import ttk
from config import COLOR_ACCENT, COLOR_ACCENT_HOVER

class PastelButton(tk.Button):
    """Custom Button được kế thừa từ tk.Button với hiệu ứng hover màu vàng chanh (Yêu cầu 8)"""
    def __init__(self, master=None, **kw):
        kw.setdefault("bg", COLOR_ACCENT)
        kw.setdefault("fg", "#FFFFFF")
        kw.setdefault("activebackground", COLOR_ACCENT_HOVER)
        kw.setdefault("activeforeground", "#FFFFFF")
        kw.setdefault("relief", "flat")
        kw.setdefault("bd", 0)
        kw.setdefault("font", ("Segoe UI", 9, "bold"))
        kw.setdefault("cursor", "hand2")
        super().__init__(master, **kw)