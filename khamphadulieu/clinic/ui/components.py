import tkinter as tk
from tkinter import ttk, messagebox
from .theme import BG, PANEL, TEXT, MUTED
from .forms import FormDialog, confirm_delete, integration_notice


class DataView(tk.Frame):
    def __init__(self, parent, data, columns, title_add="Thêm", status_col=None,
                 column_widths=None, form_fields=None, detail_fields=None, extra_actions=None, column_labels=None, detail_sections=None,
                 on_add=None, on_edit=None, on_delete=None, optional_fields=None):
        super().__init__(parent, bg=parent.cget("bg"))
        self.data = data
        self.columns = columns
        self.status_col = status_col
        self.column_widths = column_widths or {}
        self.form_fields = form_fields or [(c, c, "text") for c in columns]
        self.detail_fields = detail_fields or self.form_fields
        self.title_add = title_add
        self.extra_actions = extra_actions or []
        self.column_labels = column_labels or {}
        self.detail_sections = detail_sections or []
        # Các callback thao tác với SQL Server. Nếu để trống, thao tác sẽ chỉ
        # hiện thông báo "Work in progress" (chưa nối với cơ sở dữ liệu).
        self.on_add = on_add
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.optional_fields = set(optional_fields or [])

        bar = tk.Frame(self, bg=BG)
        bar.pack(fill="x", pady=(0, 12))
        self.search = ttk.Entry(bar, width=38)
        self.search.pack(side="left", ipady=3)
        self.search.insert(0, "")
        self.search.bind("<KeyRelease>", lambda e: self.refresh())
        ttk.Button(bar, text="Làm mới", command=self.refresh).pack(side="left", padx=8)
        ttk.Button(bar, text=title_add, style="Primary.TButton", command=self.add_record).pack(side="right")

        box = tk.Frame(self, bg=PANEL, highlightbackground="#D9E2EF", highlightthickness=1)
        box.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(box, columns=columns, show="headings", selectmode="browse")
        vs = ttk.Scrollbar(box, orient="vertical", command=self.tree.yview)
        hs = ttk.Scrollbar(box, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        vs.pack(side="right", fill="y", pady=10)
        hs.pack(side="bottom", fill="x", padx=10)

        for col in columns:
            self.tree.heading(col, text=self.column_labels.get(col, col))
            hinted = self.column_widths.get(col, max(110, len(self.column_labels.get(col, col)) * 12))
            width = max(100, min(180, hinted))
            self.tree.column(col, width=width, minwidth=90, anchor="center", stretch=True)
        self.tree.tag_configure("odd", background="#F8FAFC")
        self.tree.tag_configure("even", background="white")
        self.tree.bind("<Double-1>", lambda e: self.view_record())

        actions = tk.Frame(self, bg=BG)
        actions.pack(fill="x", pady=(10, 0))
        ttk.Button(actions, text="Sửa", command=self.edit_record).pack(side="left")
        ttk.Button(actions, text="Xóa", style="Danger.TButton", command=self.delete_record).pack(side="left", padx=8)
        ttk.Button(actions, text="Xem chi tiết", command=self.view_record).pack(side="left")
        for text, command in self.extra_actions:
            ttk.Button(actions, text=text, command=command).pack(side="left", padx=(8, 0))
        self.refresh()

    def refresh(self):
        q = self.search.get().strip().lower()
        self.tree.delete(*self.tree.get_children())
        idx = 0
        for row in self.data:
            if not q or any(q in str(v).lower() for v in row):
                self.tree.insert("", "end", values=row, tags=("even" if idx % 2 == 0 else "odd",))
                idx += 1

    def selected(self):
        s = self.tree.selection()
        if not s:
            messagebox.showwarning("Chưa chọn", "Hãy chọn một dòng trước.")
            return None
        return self.tree.item(s[0], "values")

    def _values_dict(self, values):
        return {col: values[i] for i, col in enumerate(self.columns) if i < len(values)}

    def add_record(self):
        def handle(data):
            if self.on_add:
                self.on_add(data)
                self.refresh()
                messagebox.showinfo("Thành công", "Đã thêm bản ghi vào SQL Server.", parent=self)
            else:
                integration_notice(self, "Thêm bản ghi")

        FormDialog(self, self.title_add, self.form_fields, on_submit=handle,
                   submit_text="Thêm", optional_fields=self.optional_fields)

    def edit_record(self):
        values = self.selected()
        if not values:
            return
        original = self._values_dict(values)

        def handle(data):
            if self.on_edit:
                self.on_edit(original, data)
                self.refresh()
                messagebox.showinfo("Thành công", "Đã cập nhật bản ghi trong SQL Server.", parent=self)
            else:
                integration_notice(self, "Cập nhật bản ghi")

        FormDialog(self, "Sửa thông tin", self.form_fields, values=original, on_submit=handle,
                   submit_text="Cập nhật", optional_fields=self.optional_fields)

    def delete_record(self):
        values = self.selected()
        if not values or not confirm_delete(self, "bản ghi"):
            return
        original = self._values_dict(values)
        if self.on_delete:
            try:
                self.on_delete(original)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa bản ghi trong SQL Server.\n\n{e}", parent=self)
                return
            self.refresh()
            messagebox.showinfo("Thành công", "Đã xóa bản ghi khỏi SQL Server.", parent=self)
        else:
            integration_notice(self, "Xóa bản ghi")

    def view_record(self):
        values = self.selected()
        if not values:
            return
        d = self._values_dict(values)
        dialog = tk.Toplevel(self)
        dialog.title("Chi tiết")
        dialog.configure(bg=PANEL)
        dialog.geometry("560x620")
        dialog.minsize(500, 450)

        tk.Label(dialog, text="Chi tiết bản ghi", bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=22, pady=(18, 4))
        tk.Label(dialog, text="Các trường hiển thị bám theo cấu trúc database.",
                 bg=PANEL, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=22, pady=(0, 10))

        # Dành chỗ cho nút Đóng ở đáy TRƯỚC khi đặt khung cuộn (area/canvas),
        # để khung cuộn không chiếm hết chỗ và đẩy mất nút.
        ttk.Button(dialog, text="Đóng", command=dialog.destroy).pack(side="bottom", anchor="e", padx=22, pady=(10, 18))

        area = tk.Frame(dialog, bg=PANEL)
        area.pack(fill="both", expand=True, padx=22)
        canvas = tk.Canvas(area, bg=PANEL, highlightthickness=0)
        scrollbar = ttk.Scrollbar(area, orient="vertical", command=canvas.yview)
        body = tk.Frame(canvas, bg=PANEL)
        window_id = canvas.create_window((0, 0), window=body, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        body.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(window_id, width=e.width))

        for label, key, *_ in self.detail_fields:
            row = tk.Frame(body, bg="#F8FAFC")
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label, bg="#F8FAFC", fg=MUTED,
                     font=("Segoe UI", 9, "bold"), anchor="w", width=22).pack(side="left", padx=10, pady=8)
            tk.Label(row, text=d.get(key, "") or "—", bg="#F8FAFC", fg=TEXT,
                     font=("Segoe UI", 10), anchor="w", justify="left", wraplength=300).pack(side="left", fill="x", expand=True, padx=8, pady=8)

        for section in self.detail_sections:
            section_title, columns, rows_fn, labels = section[:4]
            edit_fields = section[4] if len(section) > 4 else None
            child_callbacks = section[5] if len(section) > 5 else {}
            on_add_child = child_callbacks.get('add')
            on_edit_child = child_callbacks.get('edit')

            tk.Label(body, text=section_title, bg=PANEL, fg=TEXT,
                     font=("Segoe UI", 11, "bold"), anchor="w").pack(fill="x", pady=(16, 7))
            rows = rows_fn(d) if callable(rows_fn) else rows_fn
            frame = tk.Frame(body, bg=PANEL, highlightbackground="#D9E2EF", highlightthickness=1)
            frame.pack(fill="x", pady=(0, 6))
            tree_height = min(5, max(2, len(rows))) if rows else 2
            tree = ttk.Treeview(frame, columns=columns, show="headings", height=tree_height)
            for col in columns:
                tree.heading(col, text=labels.get(col, col))
                label = labels.get(col, col)
                tree.column(col, width=max(95, min(150, len(label) * 12)), minwidth=80, anchor="center", stretch=True)
            for row in rows:
                tree.insert("", "end", values=row)
            tree.pack(fill="x", padx=5, pady=5)
            empty_label = None
            if not rows:
                empty_label = tk.Label(frame, text="Chưa có dữ liệu", bg="#F8FAFC", fg=MUTED,
                                        font=("Segoe UI", 9, "italic"))
                empty_label.place(relx=0.5, rely=0.5, anchor="center")

            def refresh_child_tree(tree=tree, rows_fn=rows_fn, empty_label=empty_label):
                tree.delete(*tree.get_children())
                new_rows = rows_fn(d) if callable(rows_fn) else rows_fn
                for row in new_rows:
                    tree.insert("", "end", values=row)
                if empty_label is not None:
                    if new_rows:
                        empty_label.place_forget()
                    else:
                        empty_label.place(relx=0.5, rely=0.5, anchor="center")

            if edit_fields:
                child_actions = tk.Frame(body, bg=PANEL)
                child_actions.pack(fill="x", pady=(0, 8))

                def add_child(fields=edit_fields, cb=on_add_child, refresh=refresh_child_tree):
                    def handle(data):
                        if cb:
                            cb(data)
                            refresh()
                            messagebox.showinfo("Thành công", "Đã thêm bản ghi vào SQL Server.", parent=dialog)
                        else:
                            integration_notice(dialog, "Thêm bản ghi")
                    FormDialog(dialog, "Thêm", fields, on_submit=handle, submit_text="Thêm")

                def edit_child(fields=edit_fields, child_tree=tree, cb=on_edit_child, refresh=refresh_child_tree):
                    selected = child_tree.selection()
                    if not selected:
                        messagebox.showwarning("Chưa chọn", "Hãy chọn một dòng trước.", parent=dialog)
                        return
                    vals = child_tree.item(selected[0], "values")
                    mapping = {c: vals[i] for i, c in enumerate(columns) if i < len(vals)}

                    def handle(data, original=mapping):
                        if cb:
                            cb(original, data)
                            refresh()
                            messagebox.showinfo("Thành công", "Đã cập nhật bản ghi trong SQL Server.", parent=dialog)
                        else:
                            integration_notice(dialog, "Cập nhật bản ghi")
                    FormDialog(dialog, "Sửa", fields, values=mapping, on_submit=handle, submit_text="Cập nhật")

                ttk.Button(child_actions, text="Thêm", command=add_child).pack(side="left")
                ttk.Button(child_actions, text="Sửa", command=edit_child).pack(side="left", padx=8)
