from .factory import make_view
from . import demo_data as D

PatientsView = make_view("Thêm bệnh nhân", D.PATIENTS, [
    ("MaBN", "Mã BN", 90, "text"), ("HoTen", "Họ tên", 170, "text"),
    ("NgaySinh", "Ngày sinh", 105, "text"), ("GioiTinh", "Giới tính", 90, "combo", ["Nam", "Nữ"]),
    ("SDT", "SĐT", 110, "text"), ("CCCD", "CCCD", 140, "text"),
    ("DiaChi", "Địa chỉ", 200, "text"), ("BaoHiem", "Bảo hiểm", 100, "combo", ["BHYT", "Không"]),
], optional={"CCCD", "DiaChi"})

SpecialtiesView = make_view("Thêm chuyên khoa", D.SPECIALTIES, [
    ("MaCK", "Mã CK", 90, "text"), ("TenCK", "Tên chuyên khoa", 200, "text"),
    ("MoTa", "Mô tả", 280, "text"),
], optional={"MoTa"})

DoctorsView = make_view("Thêm bác sĩ", D.DOCTORS, [
    ("MaBS", "Mã BS", 90, "text"), ("HoTen", "Họ tên", 180, "text"),
    ("MaCK", "Chuyên khoa", 110, "text"), ("SDT", "SĐT", 110, "text"),
    ("Email", "Email", 200, "text"),
    ("TrangThai", "Trạng thái", 130, "combo", ["Đang làm việc", "Nghỉ phép", "Đã nghỉ"]),
], optional={"SDT", "Email"})

AppointmentsView = make_view("Đặt lịch khám", D.APPOINTMENTS, [
    ("MaLH", "Mã lịch", 90, "readonly"), ("MaBN", "Mã BN", 90, "text"),
    ("MaBS", "Mã BS", 90, "text"), ("Ngay", "Ngày khám", 105, "text"),
    ("Gio", "Giờ", 70, "text"), ("LyDo", "Lý do khám", 200, "text"),
    ("TrangThai", "Trạng thái", 120, "combo", ["Đã đặt", "Chờ khám", "Đã đến", "Hủy"]),
], optional={"MaLH", "LyDo"})

VisitsView = make_view("Lập phiếu khám", D.VISITS, [
    ("MaPK", "Mã phiếu", 90, "readonly"), ("MaLH", "Mã lịch", 90, "text"),
    ("MaBN", "Mã BN", 90, "text"), ("MaBS", "Mã BS", 90, "text"),
    ("NgayKham", "Ngày khám", 105, "text"), ("ChanDoan", "Chẩn đoán", 200, "text"),
    ("LoiDan", "Lời dặn", 200, "text"), ("NgayTaiKham", "Ngày tái khám", 115, "text"),
], optional={"MaPK", "MaLH", "LoiDan", "NgayTaiKham"})

MedicinesView = make_view("Thêm thuốc", D.MEDICINES, [
    ("MaThuoc", "Mã thuốc", 90, "text"), ("TenThuoc", "Tên thuốc", 200, "text"),
    ("DonViTinh", "Đơn vị", 90, "text"), ("SoLuongTon", "Tồn kho", 90, "text"),
    ("DonGia", "Đơn giá", 100, "text"), ("HanDung", "Hạn dùng", 105, "text"),
])

PrescriptionsView = make_view("Kê đơn thuốc", D.PRESCRIPTIONS, [
    ("MaDT", "Mã đơn", 90, "readonly"), ("MaPK", "Mã phiếu", 90, "text"),
    ("MaThuoc", "Mã thuốc", 90, "text"), ("SoLuong", "Số lượng", 80, "text"),
    ("CachDung", "Cách dùng", 220, "text"), ("SoNgay", "Số ngày", 90, "text"),
], optional={"MaDT", "CachDung"})

InvoicesView = make_view("Lập hóa đơn", D.INVOICES, [
    ("MaHD", "Mã HĐ", 90, "readonly"), ("MaPK", "Mã phiếu", 90, "text"),
    ("NgayLap", "Ngày lập", 105, "text"), ("TienKham", "Tiền khám", 100, "text"),
    ("TienThuoc", "Tiền thuốc", 100, "text"), ("TongTien", "Tổng tiền", 110, "readonly"),
    ("HinhThucTT", "Hình thức", 110, "combo", ["Tiền mặt", "Chuyển khoản", "Ví điện tử"]),
    ("TrangThai", "Trạng thái", 130, "combo", ["Chưa thanh toán", "Đã thanh toán"]),
], optional={"MaHD", "TongTien", "NgayLap", "HinhThucTT"})
