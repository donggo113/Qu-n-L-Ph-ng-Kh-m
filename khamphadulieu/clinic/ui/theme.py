import tkinter as tk
from tkinter import ttk

BG = "#F3F6FA"
SIDEBAR = "#0F172A"
PANEL = "#FFFFFF"
PANEL_2 = "#E8EEF7"
TEXT = "#172033"
MUTED = "#64748B"
ACCENT = "#2563EB"
ACCENT_2 = "#1D4ED8"
DANGER = "#DC2626"
SUCCESS = "#16A34A"
WARNING = "#D97706"
BORDER = "#D9E2EF"

def configure_style(root):
    style=ttk.Style(root); style.theme_use("clam")
    style.configure("TButton",font=("Segoe UI",10,"bold"),padding=(12,8),borderwidth=0)
    style.configure("Primary.TButton",background=ACCENT,foreground="white")
    style.map("Primary.TButton",background=[("active",ACCENT_2)])
    style.configure("Danger.TButton",background=DANGER,foreground="white")
    style.map("Danger.TButton",background=[("active","#B91C1C")])
    style.configure("TEntry",fieldbackground="white",foreground=TEXT,padding=8)
    style.configure("TCombobox",fieldbackground="white",foreground=TEXT,padding=7)
    style.configure("Treeview",background="white",fieldbackground="white",foreground=TEXT,rowheight=34,font=("Segoe UI",9))
    style.configure("Treeview.Heading",background="#E8EEF7",foreground=TEXT,font=("Segoe UI",9,"bold"),padding=9)
    style.map("Treeview",background=[("selected",ACCENT)],foreground=[("selected","white")])

def label(parent,text,size=10,bold=False,color=TEXT):
    return tk.Label(parent,text=text,bg=parent.cget("bg"),fg=color,font=("Segoe UI",size,"bold" if bold else "normal"))
