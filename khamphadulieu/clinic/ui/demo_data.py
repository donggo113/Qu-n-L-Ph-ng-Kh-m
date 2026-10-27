"""Dữ liệu mẫu để chạy giao diện. Khi nối SQL Server, thay bằng db.repository."""

PATIENTS = [
    ("BN0001", "Nguyễn Văn An", "1990-05-12", "Nam", "0901000001", "079090000001", "12 Quang Trung, Gò Vấp", "BHYT"),
    ("BN0002", "Trần Thị Bình", "1985-02-18", "Nữ", "0901000002", "079085000002", "45 Lê Lợi, Quận 1", "Không"),
    ("BN0003", "Lê Minh Khoa", "2015-09-27", "Nam", "0901000003", "", "88 Phan Văn Trị, Gò Vấp", "BHYT"),
    ("BN0004", "Phạm Ngọc Lan", "1978-06-09", "Nữ", "0901000004", "079078000004", "9 Nguyễn Kiệm, Phú Nhuận", "BHYT"),
]
SPECIALTIES = [
    ("CK01", "Nội tổng quát", "Khám và điều trị bệnh nội khoa"),
    ("CK02", "Nhi khoa", "Khám và điều trị trẻ em"),
    ("CK03", "Tai Mũi Họng", "Khám tai, mũi, họng"),
    ("CK04", "Da liễu", "Khám bệnh về da"),
]
DOCTORS = [
    ("BS001", "BS. Nguyễn Hoàng Nam", "CK01", "0908000001", "nam.bs@phongkham.vn", "Đang làm việc"),
    ("BS002", "BS. Trần Minh Huy", "CK02", "0908000002", "huy.bs@phongkham.vn", "Đang làm việc"),
    ("BS003", "BS. Lê Thu Hà", "CK03", "0908000003", "ha.bs@phongkham.vn", "Nghỉ phép"),
]
APPOINTMENTS = [
    ("LH0001", "BN0001", "BS001", "2026-10-26", "08:30", "Đau đầu, mệt mỏi", "Đã đến"),
    ("LH0002", "BN0002", "BS001", "2026-10-26", "09:00", "Tái khám", "Chờ khám"),
    ("LH0003", "BN0003", "BS002", "2026-10-26", "09:30", "Sốt, ho", "Chờ khám"),
    ("LH0004", "BN0004", "BS003", "2026-10-27", "14:00", "Viêm họng", "Đã đặt"),
]
VISITS = [
    ("PK0001", "LH0001", "BN0001", "BS001", "2026-10-26", "Căng thẳng thần kinh", "Nghỉ ngơi, uống đủ nước", "2026-11-02"),
    ("PK0002", "LH0002", "BN0002", "BS001", "2026-10-26", "Tăng huyết áp độ 1", "Theo dõi huyết áp tại nhà", "2026-11-09"),
]
MEDICINES = [
    ("T001", "Paracetamol 500mg", "Viên", "500", "1.000", "2027-12-31"),
    ("T002", "Amoxicillin 500mg", "Viên", "320", "2.500", "2027-06-30"),
    ("T003", "Vitamin C 1000mg", "Viên", "40", "3.000", "2026-12-15"),
    ("T004", "Siro ho Prospan", "Chai", "25", "85.000", "2027-03-01"),
]
PRESCRIPTIONS = [
    ("DT0001", "PK0001", "T001", "10", "2 viên/lần, 3 lần/ngày", "5 ngày"),
    ("DT0002", "PK0002", "T003", "30", "1 viên/ngày", "30 ngày"),
]
INVOICES = [
    ("HD0001", "PK0001", "2026-10-26", "150.000", "10.000", "160.000", "Tiền mặt", "Đã thanh toán"),
    ("HD0002", "PK0002", "2026-10-26", "150.000", "90.000", "240.000", "", "Chưa thanh toán"),
]

def dashboard():
    today = "2026-10-26"
    return {
        "patients": len(PATIENTS),
        "doctors": sum(d[-1] == "Đang làm việc" for d in DOCTORS),
        "today": sum(a[3] == today for a in APPOINTMENTS),
        "waiting": sum(a[-1] == "Chờ khám" for a in APPOINTMENTS),
        "unpaid": sum(i[-1] != "Đã thanh toán" for i in INVOICES),
        "revenue": sum(int(i[5].replace(".", "")) for i in INVOICES if i[-1] == "Đã thanh toán"),
        "low_stock": [m for m in MEDICINES if int(m[3]) < 50],
        "appointments": [a for a in APPOINTMENTS if a[3] == today],
    }
