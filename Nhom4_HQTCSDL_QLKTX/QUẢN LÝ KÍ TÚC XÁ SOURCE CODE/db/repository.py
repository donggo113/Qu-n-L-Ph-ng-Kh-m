from db.connection import get_connection


def _execute(query, params=()):
    """Chạy câu lệnh INSERT/UPDATE/DELETE và commit."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
    finally:
        conn.close()


def _execute_identity(query, params=()):
    """Chạy INSERT vào bảng có cột IDENTITY và trả về id vừa tạo."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        cursor.execute("SELECT SCOPE_IDENTITY()")
        new_id = cursor.fetchone()[0]
        conn.commit()
        return int(new_id) if new_id is not None else None
    finally:
        conn.close()


def _blank_to_none(value):
    if value is None:
        return None
    value = str(value).strip()
    return value if value else None


# ---------------------------------------------------------------------------
# Sinh viên
# ---------------------------------------------------------------------------

def insert_sinh_vien(d):
    _execute("""
        INSERT INTO SinhVien
            (MaSV, HoTen, NgaySinh, GioiTinh, CCCD, SDT, Email, Lop, Khoa, DiaChiThuongTru, NgayNhapHoc)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        d['MaSV'], d['HoTen'], d['NgaySinh'], d['GioiTinh'], d['CCCD'],
        _blank_to_none(d.get('SDT')), _blank_to_none(d.get('Email')),
        _blank_to_none(d.get('Lop')), _blank_to_none(d.get('Khoa')),
        _blank_to_none(d.get('DiaChiThuongTru')), _blank_to_none(d.get('NgayNhapHoc'))
    ))


def update_sinh_vien(ma_sv, d):
    _execute("""
        UPDATE SinhVien
        SET HoTen=?, NgaySinh=?, GioiTinh=?, CCCD=?, SDT=?, Email=?, Lop=?, Khoa=?,
            DiaChiThuongTru=?, NgayNhapHoc=?
        WHERE MaSV=?
    """, (
        d['HoTen'], d['NgaySinh'], d['GioiTinh'], d['CCCD'],
        _blank_to_none(d.get('SDT')), _blank_to_none(d.get('Email')),
        _blank_to_none(d.get('Lop')), _blank_to_none(d.get('Khoa')),
        _blank_to_none(d.get('DiaChiThuongTru')), _blank_to_none(d.get('NgayNhapHoc')),
        ma_sv
    ))


def delete_sinh_vien(ma_sv):
    _execute("DELETE FROM SinhVien WHERE MaSV=?", (ma_sv,))


# ---------------------------------------------------------------------------
# Tòa nhà
# ---------------------------------------------------------------------------

def insert_toa_nha(d):
    _execute("""
        INSERT INTO ToaNha (MaToa, TenToa, SoTang, DiaChi)
        VALUES (?, ?, ?, ?)
    """, (d['MaToa'], d['TenToa'], d['SoTang'], _blank_to_none(d.get('DiaChi'))))


def update_toa_nha(ma_toa, d):
    _execute("""
        UPDATE ToaNha SET TenToa=?, SoTang=?, DiaChi=? WHERE MaToa=?
    """, (d['TenToa'], d['SoTang'], _blank_to_none(d.get('DiaChi')), ma_toa))


def delete_toa_nha(ma_toa):
    _execute("DELETE FROM ToaNha WHERE MaToa=?", (ma_toa,))


# ---------------------------------------------------------------------------
# Loại phòng
# ---------------------------------------------------------------------------

def get_all_loai_phong():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT MaLoaiPhong, TenLoaiPhong, SucChua, DonGia
            FROM LoaiPhong
            ORDER BY MaLoaiPhong
        """)
        return [tuple(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def insert_loai_phong(d):
    _execute("""
        INSERT INTO LoaiPhong (MaLoaiPhong, TenLoaiPhong, SucChua, DonGia)
        VALUES (?, ?, ?, ?)
    """, (d['MaLoaiPhong'], d['TenLoaiPhong'], d['SucChua'], d['DonGia']))


def update_loai_phong(ma_loai_phong, d):
    _execute("""
        UPDATE LoaiPhong SET TenLoaiPhong=?, SucChua=?, DonGia=? WHERE MaLoaiPhong=?
    """, (d['TenLoaiPhong'], d['SucChua'], d['DonGia'], ma_loai_phong))


def delete_loai_phong(ma_loai_phong):
    _execute("DELETE FROM LoaiPhong WHERE MaLoaiPhong=?", (ma_loai_phong,))


# ---------------------------------------------------------------------------
# Phòng
# ---------------------------------------------------------------------------

def insert_phong(d):
    _execute("""
        INSERT INTO Phong (MaPhong, MaToa, MaLoaiPhong, SoPhong, Tang, GioiTinhPhong, TinhTrang)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        d['MaPhong'], d['MaToa'], d['MaLoaiPhong'], d['SoPhong'], d['Tang'],
        d['GioiTinhPhong'], d.get('TinhTrang') or 'Trống'
    ))


def update_phong(ma_phong, d):
    _execute("""
        UPDATE Phong
        SET MaToa=?, MaLoaiPhong=?, SoPhong=?, Tang=?, GioiTinhPhong=?, TinhTrang=?
        WHERE MaPhong=?
    """, (
        d['MaToa'], d['MaLoaiPhong'], d['SoPhong'], d['Tang'],
        d['GioiTinhPhong'], d.get('TinhTrang') or 'Trống', ma_phong
    ))


def delete_phong(ma_phong):
    _execute("DELETE FROM Phong WHERE MaPhong=?", (ma_phong,))


# ---------------------------------------------------------------------------
# Nhân viên
# ---------------------------------------------------------------------------

def insert_nhan_vien(d):
    _execute("""
        INSERT INTO NhanVien (MaNV, HoTen, ChucVu, SDT, Email)
        VALUES (?, ?, ?, ?, ?)
    """, (
        d['MaNV'], d['HoTen'], _blank_to_none(d.get('ChucVu')),
        _blank_to_none(d.get('SDT')), _blank_to_none(d.get('Email'))
    ))


def update_nhan_vien(ma_nv, d):
    _execute("""
        UPDATE NhanVien SET HoTen=?, ChucVu=?, SDT=?, Email=? WHERE MaNV=?
    """, (
        d['HoTen'], _blank_to_none(d.get('ChucVu')),
        _blank_to_none(d.get('SDT')), _blank_to_none(d.get('Email')), ma_nv
    ))


def delete_nhan_vien(ma_nv):
    _execute("DELETE FROM NhanVien WHERE MaNV=?", (ma_nv,))


# ---------------------------------------------------------------------------
# Hợp đồng
# ---------------------------------------------------------------------------

def insert_hop_dong(d):
    _execute("""
        INSERT INTO HopDong
            (MaHopDong, MaSV, MaPhong, MaNV, NgayBatDau, NgayKetThucDK, NgayTraThucTe, TrangThai)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        d['MaHopDong'], d['MaSV'], d['MaPhong'], _blank_to_none(d.get('MaNV')),
        d['NgayBatDau'], d['NgayKetThucDK'], _blank_to_none(d.get('NgayTraThucTe')),
        d.get('TrangThai') or 'Đang hiệu lực'
    ))


def update_hop_dong(ma_hop_dong, d):
    _execute("""
        UPDATE HopDong
        SET MaSV=?, MaPhong=?, MaNV=?, NgayBatDau=?, NgayKetThucDK=?, NgayTraThucTe=?, TrangThai=?
        WHERE MaHopDong=?
    """, (
        d['MaSV'], d['MaPhong'], _blank_to_none(d.get('MaNV')),
        d['NgayBatDau'], d['NgayKetThucDK'], _blank_to_none(d.get('NgayTraThucTe')),
        d.get('TrangThai') or 'Đang hiệu lực', ma_hop_dong
    ))


def delete_hop_dong(ma_hop_dong):
    _execute("DELETE FROM HopDong WHERE MaHopDong=?", (ma_hop_dong,))


def tra_phong_hop_dong(ma_hop_dong, ngay_tra_thuc_te):
    """Đóng hợp đồng: cập nhật ngày trả phòng thực tế và trạng thái."""
    _execute("""
        UPDATE HopDong SET NgayTraThucTe=?, TrangThai=N'Đã kết thúc' WHERE MaHopDong=?
    """, (ngay_tra_thuc_te, ma_hop_dong))


# ---------------------------------------------------------------------------
# Dịch vụ
# ---------------------------------------------------------------------------

def insert_dich_vu(d):
    _execute("""
        INSERT INTO DichVu (MaDV, TenDV, DonViTinh, DonGia)
        VALUES (?, ?, ?, ?)
    """, (d['MaDV'], d['TenDV'], d['DonViTinh'], d['DonGia']))


def update_dich_vu(ma_dv, d):
    _execute("""
        UPDATE DichVu SET TenDV=?, DonViTinh=?, DonGia=? WHERE MaDV=?
    """, (d['TenDV'], d['DonViTinh'], d['DonGia'], ma_dv))


def delete_dich_vu(ma_dv):
    _execute("DELETE FROM DichVu WHERE MaDV=?", (ma_dv,))


# ---------------------------------------------------------------------------
# Chỉ số dịch vụ
# ---------------------------------------------------------------------------

def insert_chi_so_dich_vu(d):
    return _execute_identity("""
        INSERT INTO ChiSoDichVu (MaPhong, MaDV, Thang, Nam, ChiSoDau, ChiSoCuoi, SoLuong)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        d['MaPhong'], d['MaDV'], d['Thang'], d['Nam'],
        _blank_to_none(d.get('ChiSoDau')), _blank_to_none(d.get('ChiSoCuoi')),
        _blank_to_none(d.get('SoLuong'))
    ))


def update_chi_so_dich_vu(ma_cs, d):
    _execute("""
        UPDATE ChiSoDichVu
        SET MaPhong=?, MaDV=?, Thang=?, Nam=?, ChiSoDau=?, ChiSoCuoi=?, SoLuong=?
        WHERE MaCS=?
    """, (
        d['MaPhong'], d['MaDV'], d['Thang'], d['Nam'],
        _blank_to_none(d.get('ChiSoDau')), _blank_to_none(d.get('ChiSoCuoi')),
        _blank_to_none(d.get('SoLuong')), ma_cs
    ))


def delete_chi_so_dich_vu(ma_cs):
    _execute("DELETE FROM ChiSoDichVu WHERE MaCS=?", (ma_cs,))


# ---------------------------------------------------------------------------
# Hóa đơn (TongTien là cột tính toán -> không insert/update trực tiếp)
# ---------------------------------------------------------------------------

def insert_hoa_don(d):
    _execute("""
        INSERT INTO HoaDon
            (MaHoaDon, MaHopDong, Thang, Nam, TienPhong, TienDichVu, NgayLap, HanThanhToan, TrangThai)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        d['MaHoaDon'], d['MaHopDong'], d['Thang'], d['Nam'],
        d.get('TienPhong') or 0, d.get('TienDichVu') or 0,
        _blank_to_none(d.get('NgayLap')), _blank_to_none(d.get('HanThanhToan')),
        d.get('TrangThai') or 'Chưa thanh toán'
    ))


def update_hoa_don(ma_hoa_don, d):
    _execute("""
        UPDATE HoaDon
        SET MaHopDong=?, Thang=?, Nam=?, TienPhong=?, TienDichVu=?, NgayLap=?, HanThanhToan=?, TrangThai=?
        WHERE MaHoaDon=?
    """, (
        d['MaHopDong'], d['Thang'], d['Nam'],
        d.get('TienPhong') or 0, d.get('TienDichVu') or 0,
        _blank_to_none(d.get('NgayLap')), _blank_to_none(d.get('HanThanhToan')),
        d.get('TrangThai') or 'Chưa thanh toán', ma_hoa_don
    ))


def delete_hoa_don(ma_hoa_don):
    _execute("DELETE FROM HoaDon WHERE MaHoaDon=?", (ma_hoa_don,))


# ---------------------------------------------------------------------------
# Chi tiết hóa đơn (ThanhTien là cột tính toán)
# ---------------------------------------------------------------------------

def insert_chi_tiet_hoa_don(d):
    _execute("""
        INSERT INTO ChiTietHoaDon (MaHoaDon, MaDV, SoLuong, DonGia)
        VALUES (?, ?, ?, ?)
    """, (d['MaHoaDon'], d['MaDV'], d['SoLuong'], d['DonGia']))


def update_chi_tiet_hoa_don(ma_hoa_don, ma_dv, d):
    _execute("""
        UPDATE ChiTietHoaDon SET SoLuong=?, DonGia=? WHERE MaHoaDon=? AND MaDV=?
    """, (d['SoLuong'], d['DonGia'], ma_hoa_don, ma_dv))


def delete_chi_tiet_hoa_don(ma_hoa_don, ma_dv):
    _execute("DELETE FROM ChiTietHoaDon WHERE MaHoaDon=? AND MaDV=?", (ma_hoa_don, ma_dv))


# ---------------------------------------------------------------------------
# Thanh toán
# ---------------------------------------------------------------------------

def insert_thanh_toan(d):
    return _execute_identity("""
        INSERT INTO ThanhToan (MaHoaDon, NgayThanhToan, SoTien, HinhThucTT)
        VALUES (?, ?, ?, ?)
    """, (
        d['MaHoaDon'], _blank_to_none(d.get('NgayThanhToan')), d['SoTien'],
        d.get('HinhThucTT') or 'Tiền mặt'
    ))


def update_thanh_toan(ma_tt, d):
    _execute("""
        UPDATE ThanhToan SET MaHoaDon=?, NgayThanhToan=?, SoTien=?, HinhThucTT=? WHERE MaTT=?
    """, (
        d['MaHoaDon'], _blank_to_none(d.get('NgayThanhToan')), d['SoTien'],
        d.get('HinhThucTT') or 'Tiền mặt', ma_tt
    ))


def delete_thanh_toan(ma_tt):
    _execute("DELETE FROM ThanhToan WHERE MaTT=?", (ma_tt,))


def danh_dau_hoa_don_da_thanh_toan(ma_hoa_don):
    _execute("UPDATE HoaDon SET TrangThai=N'Đã thanh toán' WHERE MaHoaDon=?", (ma_hoa_don,))


# ---------------------------------------------------------------------------
# Vi phạm
# ---------------------------------------------------------------------------

def insert_vi_pham(d):
    return _execute_identity("""
        INSERT INTO ViPham (MaSV, NgayVP, NoiDung, HinhThucXuLy)
        VALUES (?, ?, ?, ?)
    """, (
        d['MaSV'], _blank_to_none(d.get('NgayVP')), d['NoiDung'],
        _blank_to_none(d.get('HinhThucXuLy'))
    ))


def update_vi_pham(ma_vp, d):
    _execute("""
        UPDATE ViPham SET MaSV=?, NgayVP=?, NoiDung=?, HinhThucXuLy=? WHERE MaVP=?
    """, (
        d['MaSV'], _blank_to_none(d.get('NgayVP')), d['NoiDung'],
        _blank_to_none(d.get('HinhThucXuLy')), ma_vp
    ))


def delete_vi_pham(ma_vp):
    _execute("DELETE FROM ViPham WHERE MaVP=?", (ma_vp,))


def get_all_sinh_vien():
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                MaSV,
                HoTen,
                NgaySinh,
                GioiTinh,
                CCCD,
                SDT,
                Email,
                Lop,
                Khoa,
                DiaChiThuongTru,
                NgayNhapHoc
            FROM SinhVien
            ORDER BY MaSV
        """)

        rows = cursor.fetchall()

        # Chuyển pyodbc.Row thành tuple Python thông thường
        return [tuple(row) for row in rows]

    finally:
        conn.close()
def get_all_toa_nha():
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                MaToa,
                TenToa,
                SoTang,
                DiaChi
            FROM ToaNha
            ORDER BY MaToa
        """)

        rows = cursor.fetchall()

        return [tuple(row) for row in rows]

    finally:
        conn.close()
def get_all_nhan_vien():
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                MaNV,
                HoTen,
                ChucVu,
                SDT,
                Email
            FROM NhanVien
            ORDER BY MaNV
        """)

        rows = cursor.fetchall()

        return [tuple(row) for row in rows]

    finally:
        conn.close()
def get_all_dich_vu():
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                MaDV,
                TenDV,
                DonViTinh,
                DonGia
            FROM DichVu
            ORDER BY MaDV
        """)

        rows = cursor.fetchall()

        return [tuple(row) for row in rows]

    finally:
        conn.close()
def get_all_chi_so_dich_vu():
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                MaCS,
                MaPhong,
                MaDV,
                Thang,
                Nam,
                ChiSoDau,
                ChiSoCuoi,
                SoLuong
            FROM ChiSoDichVu
            ORDER BY Nam, Thang, MaPhong, MaDV
        """)

        rows = cursor.fetchall()

        return [tuple(row) for row in rows]

    finally:
        conn.close()
def get_all_vi_pham():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                MaVP,
                MaSV,
                NgayVP,
                NoiDung,
                HinhThucXuLy
            FROM ViPham
            ORDER BY MaVP
        """)
        rows = cursor.fetchall()
        return [tuple(row) for row in rows]
    finally:
        conn.close()
def get_all_phong():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                MaPhong,
                MaToa,
                MaLoaiPhong,
                SoPhong,
                Tang,
                GioiTinhPhong,
                TinhTrang
            FROM Phong
            ORDER BY MaPhong
        """)
        rows = cursor.fetchall()
        return [tuple(row) for row in rows]
    finally:
        conn.close()


def get_loai_phong_by_ma(ma_loai_phong):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                MaLoaiPhong,
                TenLoaiPhong,
                SucChua,
                DonGia
            FROM LoaiPhong
            WHERE MaLoaiPhong = ?
        """, ma_loai_phong)

        rows = cursor.fetchall()
        return [tuple(row) for row in rows]
    finally:
        conn.close()
def get_all_hop_dong():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                MaHopDong,
                MaSV,
                MaPhong,
                MaNV,
                NgayBatDau,
                NgayKetThucDK,
                NgayTraThucTe,
                TrangThai
            FROM HopDong
            ORDER BY MaHopDong
        """)
        rows = cursor.fetchall()
        return [tuple(row) for row in rows]
    finally:
        conn.close()
def get_all_hoa_don():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                MaHoaDon,
                MaHopDong,
                Thang,
                Nam,
                TienPhong,
                TienDichVu,
                TongTien,
                NgayLap,
                HanThanhToan,
                TrangThai
            FROM HoaDon
            ORDER BY MaHoaDon
        """)
        rows = cursor.fetchall()
        return [tuple(row) for row in rows]
    finally:
        conn.close()


def get_chi_tiet_hoa_don(ma_hoa_don):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                MaHoaDon,
                MaDV,
                SoLuong,
                DonGia,
                ThanhTien
            FROM ChiTietHoaDon
            WHERE MaHoaDon = ?
            ORDER BY MaDV
        """, ma_hoa_don)

        rows = cursor.fetchall()
        return [tuple(row) for row in rows]
    finally:
        conn.close()


def get_thanh_toan_hoa_don(ma_hoa_don):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                MaTT,
                MaHoaDon,
                NgayThanhToan,
                SoTien,
                HinhThucTT
            FROM ThanhToan
            WHERE MaHoaDon = ?
            ORDER BY MaTT
        """, ma_hoa_don)

        rows = cursor.fetchall()
        return [tuple(row) for row in rows]
    finally:
        conn.close()
def get_dashboard_data():
    conn = get_connection()

    try:
        cursor = conn.cursor()

        # Thống kê tổng quan
        cursor.execute("""
            SELECT COUNT(*)
            FROM SinhVien
        """)
        students = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM Phong
        """)
        rooms = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM Phong
            WHERE TinhTrang = N'Trống'
        """)
        available_rooms = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM Phong
            WHERE TinhTrang = N'Đang sử dụng'
        """)
        occupied_rooms = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM Phong
            WHERE TinhTrang = N'Bảo trì'
        """)
        maintenance_rooms = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM HoaDon
            WHERE TrangThai = N'Chưa thanh toán'
        """)
        unpaid = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM ViPham
        """)
        violations = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM HopDong
            WHERE TrangThai = N'Đang hiệu lực'
        """)
        active_contracts = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COALESCE(SUM(lp.SucChua), 0)
            FROM Phong p
            JOIN LoaiPhong lp
                ON p.MaLoaiPhong = lp.MaLoaiPhong
        """)
        capacity = cursor.fetchone()[0]

        occupancy = round(
            (occupied_rooms / rooms * 100) if rooms else 0,
            1
        )

        cursor.execute("""
            SELECT COALESCE(SUM(SoTien), 0)
            FROM ThanhToan
        """)
        revenue = cursor.fetchone()[0]

        # Số hóa đơn theo trạng thái
        cursor.execute("""
            SELECT COUNT(*)
            FROM HoaDon
            WHERE TrangThai = N'Đã thanh toán'
        """)
        paid = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM HoaDon
            WHERE TrangThai = N'Quá hạn'
        """)
        overdue = cursor.fetchone()[0]

        # Hóa đơn chưa thanh toán để hiển thị mục "Cần theo dõi"
        cursor.execute("""
            SELECT
                MaHoaDon,
                MaHopDong,
                Thang,
                Nam,
                TienPhong,
                TienDichVu,
                TongTien,
                NgayLap,
                HanThanhToan,
                TrangThai
            FROM HoaDon
            WHERE TrangThai <> N'Đã thanh toán'
            ORDER BY MaHoaDon
        """)
        unpaid_invoices = [tuple(row) for row in cursor.fetchall()]

        # Phòng bảo trì
        cursor.execute("""
            SELECT
                MaPhong,
                MaToa,
                MaLoaiPhong,
                SoPhong,
                Tang,
                GioiTinhPhong,
                TinhTrang
            FROM Phong
            WHERE TinhTrang = N'Bảo trì'
            ORDER BY MaPhong
        """)
        maintenance = [tuple(row) for row in cursor.fetchall()]

        # Vi phạm
        cursor.execute("""
            SELECT
                MaVP,
                MaSV,
                NgayVP,
                NoiDung,
                HinhThucXuLy
            FROM ViPham
            ORDER BY MaVP
        """)
        violations_data = [tuple(row) for row in cursor.fetchall()]

        # Thanh toán gần nhất
        cursor.execute("""
            SELECT
                MaTT,
                MaHoaDon,
                NgayThanhToan,
                SoTien,
                HinhThucTT
            FROM ThanhToan
            ORDER BY MaTT DESC
        """)
        payments = [tuple(row) for row in cursor.fetchall()]

        return {
            "students": students,
            "rooms": rooms,
            "available_rooms": available_rooms,
            "occupied_rooms": occupied_rooms,
            "maintenance_rooms": maintenance_rooms,
            "unpaid": unpaid,
            "violations": violations,
            "active_contracts": active_contracts,
            "capacity": capacity,
            "occupancy": occupancy,
            "revenue": revenue,
            "paid": paid,
            "overdue": overdue,
            "unpaid_invoices": unpaid_invoices,
            "maintenance": maintenance,
            "violations_data": violations_data,
            "payments": payments,
        }

    finally:
        conn.close()
