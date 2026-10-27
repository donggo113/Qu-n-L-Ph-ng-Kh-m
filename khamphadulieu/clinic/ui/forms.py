import tkinter as tk
from tkinter import ttk, messagebox
from .theme import BG, PANEL, TEXT, MUTED


class FormDialog(tk.Toplevel):
    """Hộp thoại nhập và chỉnh sửa dữ liệu dùng chung cho giao diện."""
    def __init__(self, parent, title, fields, values=None, on_submit=None, submit_text="Lưu",
                 optional_fields=None):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=BG)
        self.geometry("520x620")
        self.minsize(480, 500)
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        self.on_submit = on_submit
        self.vars = {}
        self.optional_fields = set(optional_fields or [])
        self.readonly_fields = {f[1] for f in fields if f[2] == "readonly"}
        values = values or {}

        outer = tk.Frame(self, bg=PANEL, highlightbackground="#D9E2EF", highlightthickness=1)
        outer.pack(fill="both", expand=True, padx=12, pady=12)
        tk.Label(outer, text=title, bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=22, pady=(18, 2))
        tk.Label(outer, text="Nhập thông tin theo các trường của cơ sở dữ liệu.",
                 bg=PANEL, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=22, pady=(0, 10))

        # Dành chỗ cho hàng nút Thêm/Hủy TRƯỚC khi đặt khung cuộn, để khung cuộn
        # (có expand=True) không chiếm hết toàn bộ chiều cao và đẩy mất các nút.
        actions = tk.Frame(outer, bg=PANEL)
        actions.pack(side="bottom", fill="x", padx=22, pady=(12, 18))

        # Scrollable form body for tables with many fields.
        canvas = tk.Canvas(outer, bg=PANEL, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        body = tk.Frame(canvas, bg=PANEL)
        window_id = canvas.create_window((0, 0), window=body, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=(22, 0), pady=2)
        scrollbar.pack(side="right", fill="y", padx=(0, 18), pady=2)

        def resize_body(event):
            canvas.itemconfigure(window_id, width=event.width)
        body.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", resize_body)

        for field in fields:
            label, key, kind = field[:3]
            tk.Label(body, text=label, bg=PANEL, fg=TEXT,
                     font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(7, 4))
            var = tk.StringVar(value=str(values.get(key, "")))
            self.vars[key] = var
            if kind == "readonly":
                widget = ttk.Entry(body, textvariable=var, state="readonly")
            elif kind == "combo":
                options = field[3] if len(field) > 3 else []
                widget = ttk.Combobox(body, textvariable=var, values=options, state="readonly")
                if not var.get() and options:
                    widget.set(options[0])
            else:
                widget = ttk.Entry(body, textvariable=var)
            widget.pack(fill="x", ipady=4, padx=(0, 8))

        ttk.Button(actions, text="Hủy", command=self.destroy).pack(side="right")
        ttk.Button(actions, text=submit_text, style="Primary.TButton", command=self.submit).pack(side="right", padx=8)

    def submit(self):
        data = {key: var.get().strip() for key, var in self.vars.items()}
        missing = [
            key for key, value in data.items()
            if not value and key not in self.optional_fields and key not in self.readonly_fields
        ]
        if missing:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ các trường bắt buộc.", parent=self)
            return
        if self.on_submit:
            try:
                self.on_submit(data)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu dữ liệu vào SQL Server.\n\n{e}", parent=self)
                return
        else:
            messagebox.showinfo(
                "Work in progress",
                "Work in progress.\n\nChức năng đang được phát triển.",
                parent=self,
            )
        self.destroy()


def confirm_delete(parent, item_name="bản ghi"):
    return messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc muốn xóa {item_name} không?", parent=parent)


def integration_notice(parent, action):
    messagebox.showinfo(
        "Work in progress",
        f"Work in progress.\n\nChức năng: {action}.\n\nGiao diện đã được thiết kế sẵn. Chức năng xử lý dữ liệu đang được hoàn thiện.",
        parent=parent,
    )
