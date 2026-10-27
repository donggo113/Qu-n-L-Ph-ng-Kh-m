"""Custom widget: kế thừa tk.Frame, hiển thị thẻ lịch hẹn theo màu trạng thái."""
import tkinter as tk

COLORS = {"scheduled": "#dbeafe", "done": "#dcfce7", "cancelled": "#fee2e2"}


class AppointmentCard(tk.Frame):
    def __init__(self, master, appointment, patient_name="", doctor_name="", **kw):
        super().__init__(master, bg=COLORS.get(appointment.status, "#eeeeee"),
                         bd=1, relief="solid", padx=8, pady=6, **kw)
        tk.Label(self, text=f"{appointment.start} - {appointment.end}",
                 font=("Arial", 11, "bold"), bg=self["bg"]).pack(anchor="w")
        tk.Label(self, text=f"BN: {patient_name}", bg=self["bg"]).pack(anchor="w")
        tk.Label(self, text=f"BS: {doctor_name}", bg=self["bg"]).pack(anchor="w")
