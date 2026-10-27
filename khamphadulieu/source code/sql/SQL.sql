-- ĐỀ TÀI: QUẢN LÝ KÝ TÚC XÁ

IF DB_ID('QLKyTucXa') IS NOT NULL
    DROP DATABASE QLKyTucXa;
GO

CREATE DATABASE QLKyTucXa;
GO

USE QLKyTucXa;
GO
-- 1. THIẾT KẾ BẢNG

-- 1.1 Tòa nhà
CREATE TABLE ToaNha (
    MaToa       CHAR(5)         PRIMARY KEY,
    TenToa      NVARCHAR(50)    NOT NULL,
    SoTang      INT             NOT NULL CHECK (SoTang > 0),
    DiaChi      NVARCHAR(200)   NULL
);
GO

-- 1.2 Loại phòng
CREATE TABLE LoaiPhong (
    MaLoaiPhong     CHAR(5)         PRIMARY KEY,
    TenLoaiPhong    NVARCHAR(50)    NOT NULL,
    SucChua         INT             NOT NULL CHECK (SucChua > 0),
    DonGia          DECIMAL(12,0)   NOT NULL CHECK (DonGia >= 0) -- giá/tháng/phòng
);
GO

-- 1.3 Phòng
CREATE TABLE Phong (
    MaPhong         CHAR(6)         PRIMARY KEY,
    MaToa           CHAR(5)         NOT NULL REFERENCES ToaNha(MaToa),
    MaLoaiPhong     CHAR(5)         NOT NULL REFERENCES LoaiPhong(MaLoaiPhong),
    SoPhong         NVARCHAR(10)    NOT NULL,
    Tang            INT             NOT NULL CHECK (Tang > 0),
    GioiTinhPhong   NVARCHAR(5)     NOT NULL CHECK (GioiTinhPhong IN (N'Nam', N'Nữ')),
    TinhTrang       NVARCHAR(20)    NOT NULL DEFAULT N'Trống'
                        CHECK (TinhTrang IN (N'Trống', N'Đang sử dụng', N'Bảo trì')),
    CONSTRAINT UQ_Phong UNIQUE (MaToa, SoPhong)
);
GO

-- 1.4 Sinh viên
CREATE TABLE SinhVien (
    MaSV            CHAR(10)        PRIMARY KEY,
    HoTen           NVARCHAR(100)   NOT NULL,
    NgaySinh        DATE            NOT NULL,
    GioiTinh        NVARCHAR(5)     NOT NULL CHECK (GioiTinh IN (N'Nam', N'Nữ')),
    CCCD            CHAR(14)        NOT NULL UNIQUE,
    SDT             VARCHAR(15)     NULL,
    Email           VARCHAR(100)    NULL,
    Lop             NVARCHAR(20)    NULL,
    Khoa            NVARCHAR(50)    NULL,
    DiaChiThuongTru NVARCHAR(200)   NULL,
    NgayNhapHoc     DATE            NULL
);
GO

-- 1.5 Nhân viên quản lý KTX
CREATE TABLE NhanVien (
    MaNV        CHAR(6)         PRIMARY KEY,
    HoTen       NVARCHAR(100)   NOT NULL,
    ChucVu      NVARCHAR(50)    NULL,
    SDT         VARCHAR(15)     NULL,
    Email       VARCHAR(100)    NULL
);
GO

-- 1.6 Hợp đồng thuê phòng
CREATE TABLE HopDong (
    MaHopDong       CHAR(10)        PRIMARY KEY,
    MaSV            CHAR(10)        NOT NULL REFERENCES SinhVien(MaSV),
    MaPhong         CHAR(6)         NOT NULL REFERENCES Phong(MaPhong),
    MaNV            CHAR(6)         NULL REFERENCES NhanVien(MaNV),
    NgayBatDau      DATE            NOT NULL,
    NgayKetThucDK   DATE            NOT NULL,   -- ngày kết thúc dự kiến
    NgayTraThucTe   DATE            NULL,       -- ngày trả phòng thực tế
    TrangThai       NVARCHAR(20)    NOT NULL DEFAULT N'Đang hiệu lực'
                        CHECK (TrangThai IN (N'Đang hiệu lực', N'Đã kết thúc', N'Hủy')),
    CHECK (NgayKetThucDK > NgayBatDau)
);
GO

-- 1.7 Dịch vụ (điện, nước, wifi, gửi xe...)
CREATE TABLE DichVu (
    MaDV        CHAR(5)         PRIMARY KEY,
    TenDV       NVARCHAR(50)    NOT NULL,
    DonViTinh   NVARCHAR(20)    NOT NULL,       -- kWh, m3, tháng...
    DonGia      DECIMAL(12,0)   NOT NULL CHECK (DonGia >= 0)
);
GO

-- 1.8 mức sử dụng dịch vụ theo phòng - theo tháng
CREATE TABLE ChiSoDichVu (
    MaCS        INT IDENTITY(1,1) PRIMARY KEY,
    MaPhong     CHAR(6)         NOT NULL REFERENCES Phong(MaPhong),
    MaDV        CHAR(5)         NOT NULL REFERENCES DichVu(MaDV),
    Thang       INT             NOT NULL CHECK (Thang BETWEEN 1 AND 12),
    Nam         INT             NOT NULL,
    ChiSoDau    DECIMAL(10,2)   NULL,           -- dùng cho điện/nước
    ChiSoCuoi   DECIMAL(10,2)   NULL,
    SoLuong     DECIMAL(10,2)   NULL,           -- dùng cho dịch vụ tính theo lượt/tháng (wifi, xe)
    CONSTRAINT UQ_ChiSo UNIQUE (MaPhong, MaDV, Thang, Nam)
);
GO

-- 1.9 Hóa đơn 
CREATE TABLE HoaDon (
    MaHoaDon        CHAR(10)        PRIMARY KEY,
    MaHopDong       CHAR(10)        NOT NULL REFERENCES HopDong(MaHopDong),
    Thang           INT             NOT NULL CHECK (Thang BETWEEN 1 AND 12),
    Nam             INT             NOT NULL,
    TienPhong       DECIMAL(12,0)   NOT NULL DEFAULT 0,
    TienDichVu      DECIMAL(12,0)   NOT NULL DEFAULT 0,
    TongTien        AS (TienPhong + TienDichVu) PERSISTED,
    NgayLap         DATE            NOT NULL DEFAULT CAST(GETDATE() AS DATE),
    HanThanhToan    DATE            NULL,
    TrangThai       NVARCHAR(20)    NOT NULL DEFAULT N'Chưa thanh toán'
                        CHECK (TrangThai IN (N'Chưa thanh toán', N'Đã thanh toán', N'Quá hạn')),
    CONSTRAINT UQ_HoaDon UNIQUE (MaHopDong, Thang, Nam)
);
GO

-- 1.10 Chi tiết hóa đơn 
CREATE TABLE ChiTietHoaDon (
    MaHoaDon    CHAR(10)        NOT NULL REFERENCES HoaDon(MaHoaDon),
    MaDV        CHAR(5)         NOT NULL REFERENCES DichVu(MaDV),
    SoLuong     DECIMAL(10,2)   NOT NULL,
    DonGia      DECIMAL(12,0)   NOT NULL,
    ThanhTien   AS (SoLuong * DonGia) PERSISTED,
    PRIMARY KEY (MaHoaDon, MaDV)
);
GO

-- 1.11 Thanh toán
CREATE TABLE ThanhToan (
    MaTT            INT IDENTITY(1,1) PRIMARY KEY,
    MaHoaDon        CHAR(10)        NOT NULL REFERENCES HoaDon(MaHoaDon),
    NgayThanhToan   DATE            NOT NULL DEFAULT CAST(GETDATE() AS DATE),
    SoTien          DECIMAL(12,0)   NOT NULL CHECK (SoTien > 0),
    HinhThucTT      NVARCHAR(30)    NOT NULL DEFAULT N'Tiền mặt'
);
GO

-- 1.12 Vi phạm nội quy 
CREATE TABLE ViPham (
    MaVP        INT IDENTITY(1,1) PRIMARY KEY,
    MaSV        CHAR(10)        NOT NULL REFERENCES SinhVien(MaSV),
    NgayVP      DATE            NOT NULL DEFAULT CAST(GETDATE() AS DATE),
    NoiDung     NVARCHAR(200)   NOT NULL,
    HinhThucXuLy NVARCHAR(200)  NULL
);
GO


-- 2. DỮ LIỆU MẪU
  

INSERT INTO ToaNha (MaToa, TenToa, SoTang, DiaChi) VALUES
('T01', N'Tòa A', 5, N'123 Đường D5, Quận Bình Thanh'),
('T02', N'Tòa B', 5, N'456 Đường Võ Oanh, Quận Bình Thạnh'),
('T03', N'Tòa C', 4, N'789 Đường D3, Quận Bình Thạnh');
('T04', N'Tòa D', 4, N'789 Đường D6, Quận Bình Thạnh');
GO

INSERT INTO LoaiPhong (MaLoaiPhong, TenLoaiPhong, SucChua, DonGia) VALUES
('LP01', N'Phòng 4 người', 4, 750000),
('LP02', N'Phòng 6 người', 6, 600000),
('LP03', N'Phòng 8 người', 8, 500000);
GO

INSERT INTO Phong (MaPhong, MaToa, MaLoaiPhong, SoPhong, Tang, GioiTinhPhong, TinhTrang) VALUES
('P01101', 'T01', 'LP01', '101', 1, N'Nam', N'Bảo trì'),
('P01102', 'T01', 'LP02', '102', 1, N'Nam', N'Trống'),
('P01201', 'T01', 'LP03', '201', 2, N'Nữ', N'Trống'),
('P01202', 'T01', 'LP01', '202', 2, N'Nữ', N'Bảo trì'),
('P01301', 'T01', 'LP02', '301', 3, N'Nam', N'Trống'),
('P01302', 'T01', 'LP03', '302', 3, N'Nam', N'Trống'),
('P01401', 'T01', 'LP01', '401', 4, N'Nữ', N'Trống'),
('P01402', 'T01', 'LP02', '402', 4, N'Nữ', N'Trống'),
('P01501', 'T01', 'LP03', '501', 5, N'Nam', N'Trống'),
('P01502', 'T01', 'LP01', '502', 5, N'Nam', N'Trống'),
('P02101', 'T02', 'LP02', '101', 1, N'Nam', N'Trống'),
('P02102', 'T02', 'LP03', '102', 1, N'Nam', N'Trống'),
('P02201', 'T02', 'LP01', '201', 2, N'Nữ', N'Trống'),
('P02202', 'T02', 'LP02', '202', 2, N'Nữ', N'Trống'),
('P02301', 'T02', 'LP03', '301', 3, N'Nam', N'Trống'),
('P02302', 'T02', 'LP01', '302', 3, N'Nam', N'Trống'),
('P02401', 'T02', 'LP02', '401', 4, N'Nữ', N'Trống'),
('P02402', 'T02', 'LP03', '402', 4, N'Nữ', N'Trống'),
('P02501', 'T02', 'LP01', '501', 5, N'Nam', N'Trống'),
('P02502', 'T02', 'LP02', '502', 5, N'Nam', N'Trống'),
('P03101', 'T03', 'LP03', '101', 1, N'Nam', N'Bảo trì'),
('P03102', 'T03', 'LP01', '102', 1, N'Nam', N'Trống'),
('P03201', 'T03', 'LP02', '201', 2, N'Nữ', N'Trống'),
('P03202', 'T03', 'LP03', '202', 2, N'Nữ', N'Trống'),
('P03301', 'T03', 'LP01', '301', 3, N'Nam', N'Trống'),
('P03302', 'T03', 'LP02', '302', 3, N'Nam', N'Trống'),
('P03401', 'T03', 'LP03', '401', 4, N'Nữ', N'Trống'),
('P03402', 'T03', 'LP01', '402', 4, N'Nữ', N'Trống');
GO

INSERT INTO SinhVien (MaSV, HoTen, NgaySinh, GioiTinh, CCCD, SDT, Email, Lop, Khoa, DiaChiThuongTru, NgayNhapHoc) VALUES
('SV0001', N'Mai Kim Anh', '2003-12-14', N'Nữ', '07922003000002', '0955667651', 'sv0002@student.edu.vn', N'KT2', N'Kinh tế', N'Vĩnh Long', '2021-09-03'),
('SV0002', N'Phạm Ngọc My', '2002-06-28', N'Nữ', '07922002000003', '0956164955', 'sv0003@student.edu.vn', N'DL2', N'Du lịch', N'Kiên Giang', '2020-09-04'),
('SV0003', N'Đinh Ngọc My', '2002-09-10', N'Nữ', '07922002000004', '0994374605', 'sv0004@student.edu.vn', N'DL2', N'Du lịch', N'Bạc Liêu', '2020-09-01'),
('SV0004', N'Trần Minh Uyên', '2004-02-28', N'Nữ', '07922004000005', '0941244663', 'sv0005@student.edu.vn', N'CNTT2', N'CNTT', N'Cà Mau', '2023-09-04'),
('SV0005', N'Đỗ Minh Minh', '2004-04-22', N'Nam', '07922004000006', '0945833156', 'sv0006@student.edu.vn', N'CNTT2', N'CNTT', N'Hậu Giang', '2022-09-05'),
('SV0006', N'Vũ Minh Quân', '2005-05-21', N'Nam', '07922005000007', '0984752529', 'sv0007@student.edu.vn', N'KT1', N'Kinh tế', N'Tiền Giang', '2024-09-01'),
('SV0007', N'Vũ Văn Long', '2005-05-03', N'Nam', '07922005000008', '0938317637', 'sv0008@student.edu.vn', N'DL2', N'Du lịch', N'Bến Tre', '2024-09-02'),
('SV0008', N'Lý Xuân Đạt', '2005-03-09', N'Nam', '07922005000009', '0928740864', 'sv0009@student.edu.vn', N'KT1', N'Kinh tế', N'Bến Tre', '2024-09-05'),
('SV0009', N'Ngô Hoài My', '2004-04-05', N'Nữ', '07922004000010', '0978387461', 'sv0010@student.edu.vn', N'QTKD2', N'Quản trị kinh doanh', N'An Giang', '2022-09-01'),
('SV0010', N'Hoàng Thu Yến', '2005-10-03', N'Nữ', '07922005000011', '0961642594', 'sv0011@student.edu.vn', N'QTKD1', N'Quản trị kinh doanh', N'Hậu Giang', '2024-09-05'),
('SV0011', N'Võ Bích Anh', '2002-11-18', N'Nữ', '07922002000012', '0945812670', 'sv0012@student.edu.vn', N'KT3', N'Kinh tế', N'An Giang', '2021-09-04'),
('SV0012', N'Huỳnh Diệu Anh', '2004-09-25', N'Nữ', '07922004000013', '0933978249', 'sv0013@student.edu.vn', N'DL1', N'Du lịch', N'An Giang', '2023-09-05'),
('SV0013', N'Lương Minh Hà', '2004-03-18', N'Nữ', '07922004000014', '0981182864', 'sv0014@student.edu.vn', N'CNTT1', N'CNTT', N'Hậu Giang', '2023-09-04'),
('SV0014', N'Nguyễn Ngọc Mai', '2004-04-02', N'Nữ', '07922004000015', '0942329237', 'sv0015@student.edu.vn', N'DL2', N'Du lịch', N'An Giang', '2022-09-04'),
('SV0015', N'Lê Bích Uyên', '2003-03-22', N'Nữ', '07922003000016', '0973791320', 'sv0016@student.edu.vn', N'DL1', N'Du lịch', N'Vĩnh Long', '2022-09-05'),
('SV0016', N'Lương Thanh Hằng', '2003-12-10', N'Nữ', '07922003000017', '0963551839', 'sv0017@student.edu.vn', N'KT3', N'Kinh tế', N'Sóc Trăng', '2022-09-01'),
('SV0017', N'Vũ Đức Cường', '2004-01-19', N'Nam', '07922004000018', '0984346088', 'sv0018@student.edu.vn', N'KT1', N'Kinh tế', N'Hậu Giang', '2022-09-01'),
('SV0018', N'Lê Văn Hải', '2002-01-28', N'Nam', '07922002000019', '0954349361', 'sv0019@student.edu.vn', N'CNTT2', N'CNTT', N'Trà Vinh', '2020-09-03'),
('SV0019', N'Lý Đức Toàn', '2003-12-19', N'Nam', '07922003000020', '0987337818', 'sv0020@student.edu.vn', N'QTKD2', N'Quản trị kinh doanh', N'Đồng Tháp', '2022-09-04'),
('SV0020', N'Phan Hữu Dũng', '2005-06-14', N'Nam', '07922005000021', '0965177213', 'sv0021@student.edu.vn', N'QTKD2', N'Quản trị kinh doanh', N'Bến Tre', '2023-09-01'),
('SV0021', N'Trần Xuân Kiên', '2004-02-08', N'Nam', '07922004000022', '0935714784', 'sv0022@student.edu.vn', N'KT1', N'Kinh tế', N'Trà Vinh', '2023-09-02'),
('SV0022', N'Ngô Minh Huy', '2005-04-28', N'Nam', '07922005000023', '0920117988', 'sv0023@student.edu.vn', N'QTKD2', N'Quản trị kinh doanh', N'Long An', '2023-09-01'),
('SV0023', N'Đinh Văn Cường', '2003-03-14', N'Nam', '07922003000024', '0975181648', 'sv0024@student.edu.vn', N'QTKD2', N'Quản trị kinh doanh', N'Đồng Tháp', '2022-09-01'),
('SV0024', N'Huỳnh Xuân An', '2005-05-26', N'Nam', '07922005000025', '0971070189', 'sv0025@student.edu.vn', N'KT2', N'Kinh tế', N'Cà Mau', '2024-09-02'),
('SV0025', N'Phan Kim Hằng', '2002-10-24', N'Nữ', '07922002000026', '0982772208', 'sv0026@student.edu.vn', N'CNTT1', N'CNTT', N'Bến Tre', '2021-09-01'),
('SV0026', N'Trần Hoài Nhi', '2003-01-17', N'Nữ', '07922003000027', '0920752378', 'sv0027@student.edu.vn', N'CNTT3', N'CNTT', N'An Giang', '2021-09-02'),
('SV0027', N'Hồ Ngọc Thảo', '2003-10-20', N'Nữ', '07922003000028', '0915334035', 'sv0028@student.edu.vn', N'DL2', N'Du lịch', N'An Giang', '2022-09-05'),
('SV0028', N'Mai Bích Linh', '2004-04-22', N'Nữ', '07922004000029', '0952169044', 'sv0029@student.edu.vn', N'KT1', N'Kinh tế', N'Kiên Giang', '2023-09-02'),
('SV0029', N'Đặng Diệu Linh', '2002-01-15', N'Nữ', '07922002000030', '0993370583', 'sv0030@student.edu.vn', N'DL2', N'Du lịch', N'An Giang', '2020-09-05'),
('SV0030', N'Phan Bích Huyền', '2003-06-03', N'Nữ', '07922003000031', '0942787299', 'sv0031@student.edu.vn', N'KT3', N'Kinh tế', N'Kiên Giang', '2021-09-04'),
('SV0031', N'Đinh Kim Trang', '2002-11-27', N'Nữ', '07922002000032', '0984437458', 'sv0032@student.edu.vn', N'KT2', N'Kinh tế', N'Tiền Giang', '2020-09-02'),
('SV0032', N'Võ Ngọc Dung', '2003-05-10', N'Nữ', '07922003000033', '0991178885', 'sv0033@student.edu.vn', N'KT1', N'Kinh tế', N'Bến Tre', '2022-09-02'),
('SV0033', N'Võ Bích Nhi', '2004-01-03', N'Nữ', '07922004000034', '0995132217', 'sv0034@student.edu.vn', N'QTKD1', N'Quản trị kinh doanh', N'Kiên Giang', '2022-09-01'),
('SV0034', N'Bùi Thu Vy', '2004-03-24', N'Nữ', '07922004000035', '0969302158', 'sv0035@student.edu.vn', N'DL1', N'Du lịch', N'Bến Tre', '2023-09-05'),
('SV0035', N'Nguyễn Ngọc Chi', '2003-09-02', N'Nữ', '07922003000036', '0959555330', 'sv0036@student.edu.vn', N'DL2', N'Du lịch', N'Trà Vinh', '2021-09-04'),
('SV0036', N'Hoàng Thị Lan', '2004-01-12', N'Nữ', '07922004000037', '0938195995', 'sv0037@student.edu.vn', N'KT1', N'Kinh tế', N'Tiền Giang', '2022-09-03'),
('SV0037', N'Đinh Thanh Trang', '2003-04-28', N'Nữ', '07922003000038', '0931810617', 'sv0038@student.edu.vn', N'CNTT3', N'CNTT', N'Cà Mau', '2021-09-02'),
('SV0038', N'Bùi Thanh Yến', '2003-05-06', N'Nữ', '07922003000039', '0924508349', 'sv0039@student.edu.vn', N'QTKD1', N'Quản trị kinh doanh', N'Cần Thơ', '2022-09-02'),
('SV0039', N'Phan Diệu Mai', '2004-04-08', N'Nữ', '07922004000040', '0913176186', 'sv0040@student.edu.vn', N'KT1', N'Kinh tế', N'Cà Mau', '2023-09-03'),
('SV0040', N'Lê Kim Mai', '2005-11-27', N'Nữ', '07922005000041', '0981969657', 'sv0041@student.edu.vn', N'KT3', N'Kinh tế', N'Cần Thơ', '2023-09-03'),
('SV0041', N'Huỳnh Trọng Huy', '2002-02-20', N'Nam', '07922002000042', '0968326160', 'sv0042@student.edu.vn', N'KT3', N'Kinh tế', N'Bến Tre', '2021-09-04'),
('SV0042', N'Lương Anh Dũng', '2005-10-07', N'Nam', '07922005000043', '0944188276', 'sv0043@student.edu.vn', N'CNTT1', N'CNTT', N'Bến Tre', '2024-09-01'),
('SV0043', N'Trịnh Anh Tuấn', '2003-06-14', N'Nam', '07922003000044', '0919391725', 'sv0044@student.edu.vn', N'KT3', N'Kinh tế', N'Hậu Giang', '2022-09-01'),
('SV0044', N'Đặng Anh Khang', '2005-06-13', N'Nam', '07922005000045', '0949682169', 'sv0045@student.edu.vn', N'DL1', N'Du lịch', N'Vĩnh Long', '2023-09-04'),
('SV0045', N'Hồ Minh Vinh', '2004-07-18', N'Nam', '07922004000046', '0910054484', 'sv0046@student.edu.vn', N'KT2', N'Kinh tế', N'Kiên Giang', '2022-09-04'),
('SV0046', N'Mai Trọng Đạt', '2004-08-15', N'Nam', '07922004000047', '0969345683', 'sv0047@student.edu.vn', N'KT1', N'Kinh tế', N'Trà Vinh', '2023-09-02'),
('SV0047', N'Lê Quốc Tài', '2004-02-27', N'Nam', '07922004000048', '0941523529', 'sv0048@student.edu.vn', N'KT2', N'Kinh tế', N'Đồng Tháp', '2022-09-02'),
('SV0048', N'Nguyễn Thị Hoa', '2005-10-28', N'Nữ', '07922005000049', '0919774839', 'sv0049@student.edu.vn', N'QTKD2', N'Quản trị kinh doanh', N'Cà Mau', '2023-09-04'),
('SV0049', N'Lý Thanh Hoa', '2003-11-23', N'Nữ', '07922003000050', '0910744212', 'sv0050@student.edu.vn', N'CNTT2', N'CNTT', N'Long An', '2022-09-02'),
('SV0050', N'Huỳnh Bích Ngọc', '2002-09-08', N'Nữ', '07922002000051', '0926288475', 'sv0051@student.edu.vn', N'QTKD2', N'Quản trị kinh doanh', N'Vĩnh Long', '2021-09-05');

INSERT INTO SinhVien (MaSV, HoTen, NgaySinh, GioiTinh, CCCD, SDT, Email, Lop, Khoa, DiaChiThuongTru, NgayNhapHoc) VALUES
('SV0051', N'Đinh Trọng Long', '2005-10-27', N'Nam', '07922005000052', '0977750178', 'sv0052@student.edu.vn', N'QTKD1', N'Quản trị kinh doanh', N'Trà Vinh', '2024-09-02'),
('SV0052', N'Lý Công Huy', '2003-11-09', N'Nam', '07922003000053', '0979967676', 'sv0053@student.edu.vn', N'QTKD2', N'Quản trị kinh doanh', N'Tiền Giang', '2021-09-03'),
('SV0053', N'Dương Hữu Khoa', '2004-04-09', N'Nam', '07922004000054', '0955076693', 'sv0054@student.edu.vn', N'KT3', N'Kinh tế', N'Trà Vinh', '2022-09-02'),
('SV0054', N'Hoàng Đức Nam', '2003-12-07', N'Nam', '07922003000055', '0918620650', 'sv0055@student.edu.vn', N'QTKD1', N'Quản trị kinh doanh', N'Cà Mau', '2022-09-05'),
('SV0055', N'Dương Xuân Bình', '2003-07-13', N'Nam', '07922003000056', '0988393811', 'sv0056@student.edu.vn', N'CNTT1', N'CNTT', N'Long An', '2022-09-04'),
('SV0056', N'Nguyễn Thành Khang', '2005-07-18', N'Nam', '07922005000057', '0983300637', 'sv0057@student.edu.vn', N'DL2', N'Du lịch', N'Đồng Tháp', '2024-09-02'),
('SV0057', N'Võ Xuân Sơn', '2002-07-11', N'Nam', '07922002000058', '0999774697', 'sv0058@student.edu.vn', N'QTKD1', N'Quản trị kinh doanh', N'Bến Tre', '2020-09-04'),
('SV0058', N'Hoàng Hoài Quyên', '2002-07-19', N'Nữ', '07922002000059', '0985751409', 'sv0059@student.edu.vn', N'CNTT1', N'CNTT', N'An Giang', '2021-09-02'),
('SV0059', N'Dương Thu Bích', '2004-07-11', N'Nữ', '07922004000060', '0938408562', 'sv0060@student.edu.vn', N'QTKD2', N'Quản trị kinh doanh', N'Bạc Liêu', '2023-09-04'),
('SV0060', N'Võ Thanh Huyền', '2002-08-01', N'Nữ', '07922002000061', '0982399599', 'sv0061@student.edu.vn', N'CNTT1', N'CNTT', N'Bạc Liêu', '2020-09-01'),
('SV0061', N'Trần Thị Hoa', '2003-01-20', N'Nữ', '07922003000062', '0930452412', 'sv0062@student.edu.vn', N'KT1', N'Kinh tế', N'Vĩnh Long', '2022-09-01'),
('SV0062', N'Mai Minh Ngọc', '2004-06-06', N'Nữ', '07922004000063', '0991321540', 'sv0063@student.edu.vn', N'DL2', N'Du lịch', N'Bến Tre', '2022-09-02'),
('SV0063', N'Đặng Ngọc Thảo', '2002-05-19', N'Nữ', '07922002000064', '0960372847', 'sv0064@student.edu.vn', N'QTKD1', N'Quản trị kinh doanh', N'Bến Tre', '2020-09-01'),
('SV0064', N'Mai Minh Dung', '2004-11-20', N'Nữ', '07922004000065', '0926247735', 'sv0065@student.edu.vn', N'DL2', N'Du lịch', N'Long An', '2022-09-03'),
('SV0065', N'Đinh Thanh Yến', '2004-02-17', N'Nữ', '07922004000066', '0996911784', 'sv0066@student.edu.vn', N'KT3', N'Kinh tế', N'Cần Thơ', '2023-09-04'),
('SV0066', N'Phạm Thanh Mai', '2005-12-05', N'Nữ', '07922005000067', '0968450095', 'sv0067@student.edu.vn', N'CNTT3', N'CNTT', N'Bến Tre', '2024-09-05'),
('SV0067', N'Đinh Diệu Ngọc', '2005-12-19', N'Nữ', '07922005000068', '0946023439', 'sv0068@student.edu.vn', N'KT3', N'Kinh tế', N'Đồng Tháp', '2023-09-03'),
('SV0068', N'Dương Minh Uyên', '2005-10-20', N'Nữ', '07922005000069', '0999682738', 'sv0069@student.edu.vn', N'QTKD1', N'Quản trị kinh doanh', N'Bạc Liêu', '2023-09-04'),
('SV0069', N'Bùi Thu Nhi', '2003-06-26', N'Nữ', '07922003000070', '0944675473', 'sv0070@student.edu.vn', N'KT3', N'Kinh tế', N'Kiên Giang', '2022-09-05'),
('SV0070', N'Nguyễn Anh Giang', '2002-04-24', N'Nam', '07922002000071', '0964549859', 'sv0071@student.edu.vn', N'QTKD2', N'Quản trị kinh doanh', N'Trà Vinh', '2020-09-04'),
('SV0071', N'Lý Công An', '2002-05-08', N'Nam', '07922002000072', '0964277800', 'sv0072@student.edu.vn', N'KT1', N'Kinh tế', N'Kiên Giang', '2021-09-04'),
('SV0072', N'Đinh Anh Minh', '2005-12-18', N'Nam', '07922005000073', '0954398056', 'sv0073@student.edu.vn', N'KT3', N'Kinh tế', N'Bến Tre', '2024-09-03'),
('SV0073', N'Đặng Quốc Hải', '2002-12-07', N'Nam', '07922002000074', '0952352128', 'sv0074@student.edu.vn', N'CNTT2', N'CNTT', N'Bến Tre', '2020-09-02'),
('SV0074', N'Phan Công Huy', '2004-02-27', N'Nam', '07922004000075', '0936054020', 'sv0075@student.edu.vn', N'KT2', N'Kinh tế', N'Đồng Tháp', '2023-09-02'),
('SV0075', N'Đặng Thị Xuân', '2003-05-02', N'Nữ', '07922003000076', '0917318358', 'sv0076@student.edu.vn', N'DL1', N'Du lịch', N'Kiên Giang', '2021-09-04'),
('SV0076', N'Phạm Thị Thảo', '2004-08-16', N'Nữ', '07922004000077', '0969118721', 'sv0077@student.edu.vn', N'KT3', N'Kinh tế', N'Vĩnh Long', '2022-09-03'),
('SV0077', N'Lý Ngọc Chi', '2005-08-03', N'Nữ', '07922005000078', '0987446468', 'sv0078@student.edu.vn', N'CNTT1', N'CNTT', N'Vĩnh Long', '2023-09-05'),
('SV0078', N'Đặng Ngọc Hoa', '2002-09-25', N'Nữ', '07922002000079', '0965857931', 'sv0079@student.edu.vn', N'DL2', N'Du lịch', N'Hậu Giang', '2020-09-05'),
('SV0079', N'Hồ Diệu Ngọc', '2004-10-14', N'Nữ', '07922004000080', '0950987442', 'sv0080@student.edu.vn', N'DL2', N'Du lịch', N'Hậu Giang', '2022-09-05'),
('SV0080', N'Phạm Minh Vy', '2003-05-22', N'Nữ', '07922003000081', '0920896797', 'sv0081@student.edu.vn', N'CNTT3', N'CNTT', N'Đồng Tháp', '2021-09-05'),
('SV0081', N'Lê Thu Anh', '2005-08-23', N'Nữ', '07922005000082', '0989699989', 'sv0082@student.edu.vn', N'QTKD2', N'Quản trị kinh doanh', N'Kiên Giang', '2023-09-02'),
('SV0082', N'Đặng Quốc Khoa', '2005-02-22', N'Nam', '07922005000083', '0941329612', 'sv0083@student.edu.vn', N'KT2', N'Kinh tế', N'Long An', '2023-09-04'),
('SV0083', N'Phạm Anh Hải', '2003-05-27', N'Nam', '07922003000084', '0929090631', 'sv0084@student.edu.vn', N'CNTT2', N'CNTT', N'Cần Thơ', '2021-09-03'),
('SV0084', N'Lương Trọng Khang', '2005-02-15', N'Nam', '07922005000085', '0950814428', 'sv0085@student.edu.vn', N'QTKD1', N'Quản trị kinh doanh', N'Kiên Giang', '2024-09-04'),
('SV0085', N'Lê Trọng Bình', '2005-12-11', N'Nam', '07922005000086', '0991029073', 'sv0086@student.edu.vn', N'KT2', N'Kinh tế', N'Cần Thơ', '2023-09-02'),
('SV0086', N'Mai Trọng An', '2004-10-02', N'Nam', '07922004000087', '0933513701', 'sv0087@student.edu.vn', N'QTKD2', N'Quản trị kinh doanh', N'Trà Vinh', '2023-09-03'),
('SV0087', N'Huỳnh Trọng Phong', '2005-02-16', N'Nam', '07922005000088', '0956702542', 'sv0088@student.edu.vn', N'QTKD1', N'Quản trị kinh doanh', N'Bạc Liêu', '2024-09-01'),
('SV0088', N'Huỳnh Thành Phong', '2005-05-22', N'Nam', '07922005000089', '0963747791', 'sv0089@student.edu.vn', N'DL1', N'Du lịch', N'Cần Thơ', '2024-09-01'),
('SV0089', N'Bùi Quốc Long', '2002-07-28', N'Nam', '07922002000090', '0979067939', 'sv0090@student.edu.vn', N'CNTT1', N'CNTT', N'Tiền Giang', '2021-09-04'),
('SV0090', N'Trần Đức Tài', '2004-10-25', N'Nam', '07922004000091', '0976906611', 'sv0091@student.edu.vn', N'QTKD2', N'Quản trị kinh doanh', N'Long An', '2022-09-02'),
('SV0091', N'Võ Anh Em', '2004-08-23', N'Nam', '07922004000092', '0975056916', 'sv0092@student.edu.vn', N'CNTT2', N'CNTT', N'Cần Thơ', '2022-09-02'),
('SV0092', N'Đặng Anh An', '2005-02-08', N'Nam', '07922005000093', '0925228493', 'sv0093@student.edu.vn', N'QTKD2', N'Quản trị kinh doanh', N'An Giang', '2023-09-04'),
('SV0093', N'Đặng Anh Khoa', '2004-07-27', N'Nam', '07922004000094', '0974759996', 'sv0094@student.edu.vn', N'QTKD2', N'Quản trị kinh doanh', N'Đồng Tháp', '2023-09-05'),
('SV0094', N'Hoàng Xuân Giang', '2003-02-09', N'Nam', '07922003000095', '0965692629', 'sv0095@student.edu.vn', N'KT3', N'Kinh tế', N'Long An', '2022-09-01'),
('SV0095', N'Đặng Quốc Việt', '2005-03-15', N'Nam', '07922005000096', '0982287061', 'sv0096@student.edu.vn', N'QTKD2', N'Quản trị kinh doanh', N'Bạc Liêu', '2024-09-05'),
('SV0096', N'Đinh Xuân Quân', '2004-04-23', N'Nam', '07922004000097', '0942051937', 'sv0097@student.edu.vn', N'DL2', N'Du lịch', N'Cà Mau', '2022-09-04'),
('SV0097', N'Trần Thành Kiên', '2005-12-26', N'Nam', '07922005000098', '0961167978', 'sv0098@student.edu.vn', N'QTKD1', N'Quản trị kinh doanh', N'Tiền Giang', '2023-09-04'),
('SV0098', N'Trần Minh Tài', '2004-02-28', N'Nam', '07922004000099', '0969096899', 'sv0099@student.edu.vn', N'CNTT2', N'CNTT', N'Trà Vinh', '2023-09-01'),
('SV0099', N'Hoàng Xuân Đạt', '2003-02-16', N'Nam', '07922003000100', '0945570755', 'sv0100@student.edu.vn', N'KT3', N'Kinh tế', N'Hậu Giang', '2022-09-01'),
('SV0100', N'Bùi Anh Nam', '2004-11-23', N'Nam', '07922004000101', '0975491202', 'sv0101@student.edu.vn', N'DL1', N'Du lịch', N'Cần Thơ', '2022-09-02');

INSERT INTO SinhVien (MaSV, HoTen, NgaySinh, GioiTinh, CCCD, SDT, Email, Lop, Khoa, DiaChiThuongTru, NgayNhapHoc) VALUES
('SV0101', N'Đặng Đức Kiên', '2002-07-04', N'Nam', '07922002000102', '0995060193', 'sv0102@student.edu.vn', N'CNTT2', N'CNTT', N'Sóc Trăng', '2020-09-03'),
('SV0102', N'Nguyễn Thị Linh', '2002-05-12', N'Nữ', '07922002000103', '0960310319', 'sv0103@student.edu.vn', N'QTKD1', N'Quản trị kinh doanh', N'Vĩnh Long', '2020-09-05'),
('SV0103', N'Ngô Hoài Yến', '2003-03-06', N'Nữ', '07922003000104', '0920598952', 'sv0104@student.edu.vn', N'DL2', N'Du lịch', N'Cà Mau', '2021-09-04'),
('SV0104', N'Mai Thu Hoa', '2005-11-09', N'Nữ', '07922005000105', '0971682508', 'sv0105@student.edu.vn', N'KT2', N'Kinh tế', N'Tiền Giang', '2023-09-04'),
('SV0105', N'Đặng Anh Phát', '2002-08-12', N'Nam', '07922002000106', '0988862539', 'sv0106@student.edu.vn', N'KT2', N'Kinh tế', N'Tiền Giang', '2021-09-03'),
('SV0106', N'Dương Quốc Giang', '2005-08-04', N'Nam', '07922005000107', '0941837210', 'sv0107@student.edu.vn', N'QTKD1', N'Quản trị kinh doanh', N'Hậu Giang', '2024-09-05'),
('SV0107', N'Đặng Quốc An', '2005-05-01', N'Nam', '07922005000108', '0985957706', 'sv0108@student.edu.vn', N'CNTT1', N'CNTT', N'Hậu Giang', '2024-09-03'),
('SV0108', N'Vũ Trọng Minh', '2003-11-07', N'Nam', '07922003000109', '0993334601', 'sv0109@student.edu.vn', N'KT2', N'Kinh tế', N'Tiền Giang', '2021-09-01'),
('SV0109', N'Trần Quốc Quân', '2002-10-12', N'Nam', '07922002000110', '0927637794', 'sv0110@student.edu.vn', N'CNTT2', N'CNTT', N'Kiên Giang', '2021-09-04'),
('SV0110', N'Huỳnh Đức Em', '2004-09-17', N'Nam', '07922004000111', '0946578001', 'sv0111@student.edu.vn', N'CNTT3', N'CNTT', N'Kiên Giang', '2023-09-03'),
('SV0111', N'Bùi Hữu Quân', '2002-03-25', N'Nam', '07922002000112', '0940281491', 'sv0112@student.edu.vn', N'QTKD1', N'Quản trị kinh doanh', N'Long An', '2021-09-01'),
('SV0112', N'Hồ Văn Huy', '2002-08-12', N'Nam', '07922002000113', '0945186708', 'sv0113@student.edu.vn', N'DL2', N'Du lịch', N'Cà Mau', '2021-09-01'),
('SV0113', N'Vũ Công An', '2004-10-08', N'Nam', '07922004000114', '0996926431', 'sv0114@student.edu.vn', N'CNTT2', N'CNTT', N'Tiền Giang', '2023-09-03'),
('SV0114', N'Ngô Hữu Em', '2002-01-10', N'Nam', '07922002000115', '0976118957', 'sv0115@student.edu.vn', N'CNTT2', N'CNTT', N'An Giang', '2020-09-05'),
('SV0115', N'Hoàng Xuân Quân', '2004-11-24', N'Nam', '07922004000116', '0982503409', 'sv0116@student.edu.vn', N'QTKD1', N'Quản trị kinh doanh', N'Hậu Giang', '2022-09-04'),
('SV0116', N'Phạm Công Vinh', '2005-05-02', N'Nam', '07922005000117', '0959731689', 'sv0117@student.edu.vn', N'KT1', N'Kinh tế', N'Sóc Trăng', '2024-09-02'),
('SV0117', N'Đỗ Hữu Tuấn', '2004-09-21', N'Nam', '07922004000118', '0958140388', 'sv0118@student.edu.vn', N'CNTT1', N'CNTT', N'Cà Mau', '2023-09-02'),
('SV0118', N'Phạm Diệu Chi', '2003-11-21', N'Nữ', '07922003000119', '0990147573', 'sv0119@student.edu.vn', N'CNTT1', N'CNTT', N'Cần Thơ', '2022-09-02'),
('SV0119', N'Hoàng Hoài Hằng', '2002-09-07', N'Nữ', '07922002000120', '0988703005', 'sv0120@student.edu.vn', N'KT1', N'Kinh tế', N'Đồng Tháp', '2021-09-02'),
('SV0120', N'Lương Thị Huyền', '2003-03-18', N'Nữ', '07922003000121', '0943642236', 'sv0121@student.edu.vn', N'CNTT3', N'CNTT', N'An Giang', '2021-09-02'),
('SV0121', N'Nguyễn Hồng Hoa', '2004-01-06', N'Nữ', '07922004000122', '0945617024', 'sv0122@student.edu.vn', N'CNTT1', N'CNTT', N'Vĩnh Long', '2023-09-05'),
('SV0122', N'Phạm Ngọc Nhi', '2005-06-17', N'Nữ', '07922005000123', '0989680504', 'sv0123@student.edu.vn', N'CNTT2', N'CNTT', N'Sóc Trăng', '2023-09-05'),
('SV0123', N'Trần Bích Lan', '2005-11-01', N'Nữ', '07922005000124', '0918163847', 'sv0124@student.edu.vn', N'QTKD2', N'Quản trị kinh doanh', N'Cà Mau', '2024-09-01'),
('SV0124', N'Lý Diệu Chi', '2002-06-20', N'Nữ', '07922002000125', '0929909029', 'sv0125@student.edu.vn', N'CNTT2', N'CNTT', N'Vĩnh Long', '2021-09-05');
GO

INSERT INTO NhanVien (MaNV, HoTen, ChucVu, SDT, Email) VALUES
('NV001', N'Đỗ Văn Quản', N'Trưởng ban quản lý KTX', '0909111111', 'quan.dv@ktx.edu.vn'),
('NV002', N'Ngô Thị Lý', N'Nhân viên quản lý', '0909111112', 'ly.nt@ktx.edu.vn'),
('NV003', N'Trần Văn Hòa', N'Nhân viên quản lý', '0909111113', 'hoa.tv@ktx.edu.vn'),
('NV004', N'Lê Thị Sương', N'Kế toán KTX', '0909111114', 'suong.lt@ktx.edu.vn'),
('NV005', N'Phạm Văn Tâm', N'Bảo vệ', '0909111115', 'tam.pv@ktx.edu.vn'),
('NV006', N'Nguyễn Thị Yến', N'Nhân viên quản lý', '0909111116', 'yen.nt@ktx.edu.vn');
GO

INSERT INTO DichVu (MaDV, TenDV, DonViTinh, DonGia) VALUES
('DV01', N'Điện', N'kWh', 3500),
('DV02', N'Nước', N'm3', 15000),
('DV03', N'Wifi', N'tháng', 50000),
('DV04', N'Gửi xe', N'tháng', 100000);
GO

INSERT INTO HopDong (MaHopDong, MaSV, MaPhong, MaNV, NgayBatDau, NgayKetThucDK, TrangThai, NgayTraThucTe) VALUES
('HD000001', 'SV0001', 'P02201', 'NV006', '2021-09-03', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000002', 'SV0002', 'P02201', 'NV005', '2020-09-04', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000003', 'SV0003', 'P02201', 'NV005', '2020-09-01', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000004', 'SV0004', 'P02201', 'NV006', '2023-09-04', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000005', 'SV0005', 'P03301', 'NV003', '2022-09-05', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000006', 'SV0006', 'P03301', 'NV004', '2024-09-01', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000007', 'SV0007', 'P03301', 'NV005', '2024-09-02', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000008', 'SV0008', 'P03301', 'NV005', '2024-09-05', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000009', 'SV0009', 'P03202', 'NV003', '2022-09-01', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000010', 'SV0010', 'P03202', 'NV004', '2024-09-05', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000011', 'SV0011', 'P03202', 'NV005', '2021-09-04', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000012', 'SV0012', 'P03202', 'NV005', '2023-09-05', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000013', 'SV0013', 'P03202', 'NV004', '2023-09-04', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000014', 'SV0014', 'P03202', 'NV001', '2022-09-04', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000015', 'SV0015', 'P03202', 'NV006', '2022-09-05', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000016', 'SV0016', 'P03202', 'NV001', '2022-09-01', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000017', 'SV0017', 'P01501', 'NV006', '2022-09-01', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000018', 'SV0018', 'P01501', 'NV006', '2020-09-03', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000019', 'SV0019', 'P01501', 'NV005', '2022-09-04', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000020', 'SV0020', 'P01501', 'NV006', '2023-09-01', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000021', 'SV0021', 'P01501', 'NV002', '2023-09-02', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000022', 'SV0022', 'P01501', 'NV004', '2023-09-01', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000023', 'SV0023', 'P01501', 'NV004', '2022-09-01', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000024', 'SV0024', 'P01501', 'NV002', '2024-09-02', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000025', 'SV0025', 'P01402', 'NV004', '2021-09-01', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000026', 'SV0026', 'P01402', 'NV003', '2021-09-02', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000027', 'SV0027', 'P01402', 'NV004', '2022-09-05', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000028', 'SV0028', 'P01402', 'NV004', '2023-09-02', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000029', 'SV0029', 'P01402', 'NV004', '2020-09-05', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000030', 'SV0030', 'P01402', 'NV006', '2021-09-04', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000031', 'SV0031', 'P02202', 'NV001', '2020-09-02', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000032', 'SV0032', 'P02202', 'NV003', '2022-09-02', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000033', 'SV0033', 'P02202', 'NV004', '2022-09-01', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000034', 'SV0034', 'P02202', 'NV003', '2023-09-05', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000035', 'SV0035', 'P02202', 'NV006', '2021-09-04', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000036', 'SV0036', 'P02401', 'NV003', '2022-09-03', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000037', 'SV0037', 'P02401', 'NV003', '2021-09-02', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000038', 'SV0038', 'P02401', 'NV002', '2022-09-02', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000039', 'SV0039', 'P02401', 'NV006', '2023-09-03', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000040', 'SV0040', 'P02401', 'NV004', '2023-09-03', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000041', 'SV0041', 'P02102', 'NV001', '2021-09-04', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000042', 'SV0042', 'P02102', 'NV001', '2024-09-01', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000043', 'SV0043', 'P02102', 'NV001', '2022-09-01', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000044', 'SV0044', 'P02102', 'NV001', '2023-09-04', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000045', 'SV0045', 'P02102', 'NV004', '2022-09-04', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000046', 'SV0046', 'P02102', 'NV001', '2023-09-02', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000047', 'SV0047', 'P02102', 'NV006', '2022-09-02', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000048', 'SV0048', 'P03402', 'NV006', '2023-09-04', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000049', 'SV0049', 'P03402', 'NV003', '2022-09-02', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000050', 'SV0050', 'P03402', 'NV002', '2021-09-05', '2027-06-30', N'Đang hiệu lực', NULL);

INSERT INTO HopDong (MaHopDong, MaSV, MaPhong, MaNV, NgayBatDau, NgayKetThucDK, TrangThai, NgayTraThucTe) VALUES
('HD000051', 'SV0051', 'P02301', 'NV005', '2024-09-02', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000052', 'SV0052', 'P02301', 'NV001', '2021-09-03', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000053', 'SV0053', 'P02301', 'NV005', '2022-09-02', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000054', 'SV0054', 'P02301', 'NV005', '2022-09-05', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000055', 'SV0055', 'P02301', 'NV005', '2022-09-04', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000056', 'SV0056', 'P02301', 'NV003', '2024-09-02', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000057', 'SV0057', 'P02301', 'NV006', '2020-09-04', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000058', 'SV0058', 'P03201', 'NV001', '2021-09-02', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000059', 'SV0059', 'P03201', 'NV004', '2023-09-04', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000060', 'SV0060', 'P03201', 'NV003', '2020-09-01', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000061', 'SV0061', 'P03201', 'NV006', '2022-09-01', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000062', 'SV0062', 'P03201', 'NV004', '2022-09-02', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000063', 'SV0063', 'P02402', 'NV006', '2020-09-01', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000064', 'SV0064', 'P02402', 'NV001', '2022-09-03', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000065', 'SV0065', 'P02402', 'NV003', '2023-09-04', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000066', 'SV0066', 'P02402', 'NV005', '2024-09-05', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000067', 'SV0067', 'P02402', 'NV003', '2023-09-03', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000068', 'SV0068', 'P02402', 'NV003', '2023-09-04', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000069', 'SV0069', 'P02402', 'NV001', '2022-09-05', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000070', 'SV0070', 'P01102', 'NV005', '2020-09-04', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000071', 'SV0071', 'P01102', 'NV005', '2021-09-04', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000072', 'SV0072', 'P01102', 'NV002', '2024-09-03', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000073', 'SV0073', 'P01102', 'NV002', '2020-09-02', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000074', 'SV0074', 'P01102', 'NV006', '2023-09-02', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000075', 'SV0075', 'P01201', 'NV004', '2021-09-04', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000076', 'SV0076', 'P01201', 'NV002', '2022-09-03', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000077', 'SV0077', 'P01201', 'NV001', '2023-09-05', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000078', 'SV0078', 'P01201', 'NV003', '2020-09-05', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000079', 'SV0079', 'P01201', 'NV005', '2022-09-05', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000080', 'SV0080', 'P01201', 'NV003', '2021-09-05', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000081', 'SV0081', 'P01201', 'NV001', '2023-09-02', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000082', 'SV0082', 'P02302', 'NV003', '2023-09-04', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000083', 'SV0083', 'P02302', 'NV005', '2021-09-03', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000084', 'SV0084', 'P02302', 'NV002', '2024-09-04', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000085', 'SV0085', 'P01301', 'NV004', '2023-09-02', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000086', 'SV0086', 'P01301', 'NV005', '2023-09-03', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000087', 'SV0087', 'P01301', 'NV005', '2024-09-01', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000088', 'SV0088', 'P01301', 'NV005', '2024-09-01', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000089', 'SV0089', 'P01301', 'NV006', '2021-09-04', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000090', 'SV0090', 'P02502', 'NV006', '2022-09-02', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000091', 'SV0091', 'P02502', 'NV005', '2022-09-02', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000092', 'SV0092', 'P02502', 'NV001', '2023-09-04', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000093', 'SV0093', 'P02502', 'NV005', '2023-09-05', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000094', 'SV0094', 'P02502', 'NV006', '2022-09-01', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000095', 'SV0095', 'P01302', 'NV006', '2024-09-05', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000096', 'SV0096', 'P01302', 'NV003', '2022-09-04', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000097', 'SV0097', 'P01302', 'NV001', '2023-09-04', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000098', 'SV0098', 'P01302', 'NV002', '2023-09-01', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000099', 'SV0099', 'P01302', 'NV003', '2022-09-01', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000100', 'SV0100', 'P01302', 'NV006', '2022-09-02', '2027-06-30', N'Đang hiệu lực', NULL);

INSERT INTO HopDong (MaHopDong, MaSV, MaPhong, MaNV, NgayBatDau, NgayKetThucDK, TrangThai, NgayTraThucTe) VALUES
('HD000101', 'SV0101', 'P01302', 'NV003', '2020-09-03', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000102', 'SV0102', 'P01401', 'NV003', '2020-09-05', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000103', 'SV0103', 'P01401', 'NV003', '2021-09-04', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000104', 'SV0104', 'P01401', 'NV001', '2023-09-04', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000105', 'SV0105', 'P03302', 'NV002', '2021-09-03', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000106', 'SV0106', 'P03302', 'NV002', '2024-09-05', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000107', 'SV0107', 'P03302', 'NV005', '2024-09-03', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000108', 'SV0108', 'P03302', 'NV006', '2021-09-01', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000109', 'SV0109', 'P03302', 'NV004', '2021-09-04', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000110', 'SV0110', 'P01502', 'NV001', '2023-09-03', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000111', 'SV0111', 'P01502', 'NV002', '2021-09-01', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000112', 'SV0112', 'P01502', 'NV006', '2021-09-01', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000113', 'SV0113', 'P02101', 'NV006', '2023-09-03', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000114', 'SV0114', 'P02101', 'NV001', '2020-09-05', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000115', 'SV0115', 'P02101', 'NV001', '2022-09-04', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000116', 'SV0116', 'P02101', 'NV006', '2024-09-02', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000117', 'SV0117', 'P02101', 'NV005', '2023-09-02', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000118', 'SV0118', 'P03401', 'NV002', '2022-09-02', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000119', 'SV0119', 'P03401', 'NV004', '2021-09-02', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000120', 'SV0120', 'P03401', 'NV004', '2021-09-02', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000121', 'SV0121', 'P03401', 'NV004', '2023-09-05', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000122', 'SV0122', 'P03401', 'NV003', '2023-09-05', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000123', 'SV0123', 'P03401', 'NV002', '2024-09-01', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000124', 'SV0124', 'P03401', 'NV003', '2021-09-05', '2027-06-30', N'Đang hiệu lực', NULL),
('HD000125', 'SV0040', 'P01402', 'NV001', '2022-09-05', '2023-06-30', N'Đã kết thúc', '2023-06-25'),
('HD000126', 'SV0093', 'P03302', 'NV002', '2022-09-05', '2023-06-30', N'Đã kết thúc', '2023-06-25'),
('HD000127', 'SV0042', 'P01502', 'NV001', '2022-09-05', '2023-06-30', N'Đã kết thúc', '2023-06-25'),
('HD000128', 'SV0100', 'P01102', 'NV001', '2022-09-05', '2023-06-30', N'Đã kết thúc', '2023-06-25'),
('HD000129', 'SV0121', 'P03401', 'NV004', '2022-09-05', '2023-06-30', N'Đã kết thúc', '2023-06-25'),
('HD000130', 'SV0073', 'P02502', 'NV004', '2022-09-05', '2023-06-30', N'Đã kết thúc', '2023-06-25'),
('HD000131', 'SV0077', 'P02402', 'NV005', '2022-09-05', '2023-06-30', N'Đã kết thúc', '2023-06-25'),
('HD000132', 'SV0011', 'P02401', 'NV004', '2022-09-05', '2023-06-30', N'Đã kết thúc', '2023-06-25');
GO

INSERT INTO ChiSoDichVu (MaPhong, MaDV, Thang, Nam, ChiSoDau, ChiSoCuoi, SoLuong) VALUES
('P02201', 'DV01', 6, 2026, 77, 190, NULL),
('P02201', 'DV02', 6, 2026, 13, 22, NULL),
('P02201', 'DV03', 6, 2026, NULL, NULL, 1),
('P03301', 'DV01', 6, 2026, 94, 205, NULL),
('P03301', 'DV02', 6, 2026, 23, 28, NULL),
('P03301', 'DV03', 6, 2026, NULL, NULL, 1),
('P03301', 'DV04', 6, 2026, NULL, NULL, 1),
('P03202', 'DV01', 6, 2026, 64, 145, NULL),
('P03202', 'DV02', 6, 2026, 19, 31, NULL),
('P03202', 'DV03', 6, 2026, NULL, NULL, 1),
('P03202', 'DV04', 6, 2026, NULL, NULL, 2),
('P01501', 'DV01', 6, 2026, 136, 242, NULL),
('P01501', 'DV02', 6, 2026, 25, 31, NULL),
('P01501', 'DV03', 6, 2026, NULL, NULL, 1),
('P01501', 'DV04', 6, 2026, NULL, NULL, 1),
('P01402', 'DV01', 6, 2026, 117, 190, NULL),
('P01402', 'DV02', 6, 2026, 19, 27, NULL),
('P01402', 'DV03', 6, 2026, NULL, NULL, 1),
('P01402', 'DV04', 6, 2026, NULL, NULL, 1),
('P02202', 'DV01', 6, 2026, 55, 166, NULL),
('P02202', 'DV02', 6, 2026, 17, 23, NULL),
('P02202', 'DV03', 6, 2026, NULL, NULL, 1),
('P02202', 'DV04', 6, 2026, NULL, NULL, 1),
('P02401', 'DV01', 6, 2026, 100, 199, NULL),
('P02401', 'DV02', 6, 2026, 11, 21, NULL),
('P02401', 'DV03', 6, 2026, NULL, NULL, 1),
('P02102', 'DV01', 6, 2026, 50, 152, NULL),
('P02102', 'DV02', 6, 2026, 16, 23, NULL),
('P02102', 'DV03', 6, 2026, NULL, NULL, 1),
('P03402', 'DV01', 6, 2026, 88, 213, NULL),
('P03402', 'DV02', 6, 2026, 16, 22, NULL),
('P03402', 'DV03', 6, 2026, NULL, NULL, 1),
('P03402', 'DV04', 6, 2026, NULL, NULL, 2),
('P02301', 'DV01', 6, 2026, 148, 273, NULL),
('P02301', 'DV02', 6, 2026, 14, 22, NULL),
('P02301', 'DV03', 6, 2026, NULL, NULL, 1),
('P02301', 'DV04', 6, 2026, NULL, NULL, 1),
('P03201', 'DV01', 6, 2026, 147, 251, NULL),
('P03201', 'DV02', 6, 2026, 18, 25, NULL),
('P03201', 'DV03', 6, 2026, NULL, NULL, 1),
('P02402', 'DV01', 6, 2026, 87, 160, NULL),
('P02402', 'DV02', 6, 2026, 20, 27, NULL),
('P02402', 'DV03', 6, 2026, NULL, NULL, 1),
('P02402', 'DV04', 6, 2026, NULL, NULL, 1),
('P01102', 'DV01', 6, 2026, 65, 150, NULL),
('P01102', 'DV02', 6, 2026, 10, 17, NULL),
('P01102', 'DV03', 6, 2026, NULL, NULL, 1),
('P01102', 'DV04', 6, 2026, NULL, NULL, 2),
('P01201', 'DV01', 6, 2026, 113, 192, NULL),
('P01201', 'DV02', 6, 2026, 23, 29, NULL),
('P01201', 'DV03', 6, 2026, NULL, NULL, 1),
('P02302', 'DV01', 6, 2026, 72, 195, NULL),
('P02302', 'DV02', 6, 2026, 14, 26, NULL),
('P02302', 'DV03', 6, 2026, NULL, NULL, 1),
('P02302', 'DV04', 6, 2026, NULL, NULL, 2),
('P01301', 'DV01', 6, 2026, 98, 215, NULL),
('P01301', 'DV02', 6, 2026, 17, 27, NULL),
('P01301', 'DV03', 6, 2026, NULL, NULL, 1),
('P01301', 'DV04', 6, 2026, NULL, NULL, 2),
('P02502', 'DV01', 6, 2026, 114, 214, NULL),
('P02502', 'DV02', 6, 2026, 21, 28, NULL),
('P02502', 'DV03', 6, 2026, NULL, NULL, 1),
('P02502', 'DV04', 6, 2026, NULL, NULL, 1),
('P01302', 'DV01', 6, 2026, 59, 127, NULL),
('P01302', 'DV02', 6, 2026, 22, 34, NULL),
('P01302', 'DV03', 6, 2026, NULL, NULL, 1),
('P01302', 'DV04', 6, 2026, NULL, NULL, 1),
('P01401', 'DV01', 6, 2026, 144, 242, NULL),
('P01401', 'DV02', 6, 2026, 11, 20, NULL),
('P01401', 'DV03', 6, 2026, NULL, NULL, 1),
('P01401', 'DV04', 6, 2026, NULL, NULL, 2),
('P03302', 'DV01', 6, 2026, 105, 172, NULL),
('P03302', 'DV02', 6, 2026, 10, 20, NULL),
('P03302', 'DV03', 6, 2026, NULL, NULL, 1),
('P03302', 'DV04', 6, 2026, NULL, NULL, 2),
('P01502', 'DV01', 6, 2026, 108, 177, NULL),
('P01502', 'DV02', 6, 2026, 12, 21, NULL),
('P01502', 'DV03', 6, 2026, NULL, NULL, 1),
('P01502', 'DV04', 6, 2026, NULL, NULL, 1),
('P02101', 'DV01', 6, 2026, 90, 207, NULL);

INSERT INTO ChiSoDichVu (MaPhong, MaDV, Thang, Nam, ChiSoDau, ChiSoCuoi, SoLuong) VALUES
('P02101', 'DV02', 6, 2026, 23, 28, NULL),
('P02101', 'DV03', 6, 2026, NULL, NULL, 1),
('P03401', 'DV01', 6, 2026, 123, 230, NULL),
('P03401', 'DV02', 6, 2026, 22, 31, NULL),
('P03401', 'DV03', 6, 2026, NULL, NULL, 1),
('P02201', 'DV01', 7, 2026, 190, 261, NULL),
('P02201', 'DV02', 7, 2026, 22, 33, NULL),
('P02201', 'DV03', 7, 2026, NULL, NULL, 1),
('P02201', 'DV04', 7, 2026, NULL, NULL, 1),
('P03301', 'DV01', 7, 2026, 205, 335, NULL),
('P03301', 'DV02', 7, 2026, 28, 33, NULL),
('P03301', 'DV03', 7, 2026, NULL, NULL, 1),
('P03301', 'DV04', 7, 2026, NULL, NULL, 1),
('P03202', 'DV01', 7, 2026, 145, 229, NULL),
('P03202', 'DV02', 7, 2026, 31, 41, NULL),
('P03202', 'DV03', 7, 2026, NULL, NULL, 1),
('P03202', 'DV04', 7, 2026, NULL, NULL, 2),
('P01501', 'DV01', 7, 2026, 242, 362, NULL),
('P01501', 'DV02', 7, 2026, 31, 38, NULL),
('P01501', 'DV03', 7, 2026, NULL, NULL, 1),
('P01402', 'DV01', 7, 2026, 190, 307, NULL),
('P01402', 'DV02', 7, 2026, 27, 33, NULL),
('P01402', 'DV03', 7, 2026, NULL, NULL, 1),
('P01402', 'DV04', 7, 2026, NULL, NULL, 1),
('P02202', 'DV01', 7, 2026, 166, 236, NULL),
('P02202', 'DV02', 7, 2026, 23, 30, NULL),
('P02202', 'DV03', 7, 2026, NULL, NULL, 1),
('P02401', 'DV01', 7, 2026, 199, 290, NULL),
('P02401', 'DV02', 7, 2026, 21, 33, NULL),
('P02401', 'DV03', 7, 2026, NULL, NULL, 1),
('P02401', 'DV04', 7, 2026, NULL, NULL, 1),
('P02102', 'DV01', 7, 2026, 152, 279, NULL),
('P02102', 'DV02', 7, 2026, 23, 30, NULL),
('P02102', 'DV03', 7, 2026, NULL, NULL, 1),
('P02102', 'DV04', 7, 2026, NULL, NULL, 1),
('P03402', 'DV01', 7, 2026, 213, 320, NULL),
('P03402', 'DV02', 7, 2026, 22, 31, NULL),
('P03402', 'DV03', 7, 2026, NULL, NULL, 1),
('P03402', 'DV04', 7, 2026, NULL, NULL, 1),
('P02301', 'DV01', 7, 2026, 273, 385, NULL),
('P02301', 'DV02', 7, 2026, 22, 32, NULL),
('P02301', 'DV03', 7, 2026, NULL, NULL, 1),
('P02301', 'DV04', 7, 2026, NULL, NULL, 2),
('P03201', 'DV01', 7, 2026, 251, 317, NULL),
('P03201', 'DV02', 7, 2026, 25, 35, NULL),
('P03201', 'DV03', 7, 2026, NULL, NULL, 1),
('P02402', 'DV01', 7, 2026, 160, 262, NULL),
('P02402', 'DV02', 7, 2026, 27, 33, NULL),
('P02402', 'DV03', 7, 2026, NULL, NULL, 1),
('P02402', 'DV04', 7, 2026, NULL, NULL, 2),
('P01102', 'DV01', 7, 2026, 150, 259, NULL),
('P01102', 'DV02', 7, 2026, 17, 26, NULL),
('P01102', 'DV03', 7, 2026, NULL, NULL, 1),
('P01102', 'DV04', 7, 2026, NULL, NULL, 1),
('P01201', 'DV01', 7, 2026, 192, 271, NULL),
('P01201', 'DV02', 7, 2026, 29, 39, NULL),
('P01201', 'DV03', 7, 2026, NULL, NULL, 1),
('P02302', 'DV01', 7, 2026, 195, 273, NULL),
('P02302', 'DV02', 7, 2026, 26, 36, NULL),
('P02302', 'DV03', 7, 2026, NULL, NULL, 1),
('P02302', 'DV04', 7, 2026, NULL, NULL, 1),
('P01301', 'DV01', 7, 2026, 215, 325, NULL),
('P01301', 'DV02', 7, 2026, 27, 34, NULL),
('P01301', 'DV03', 7, 2026, NULL, NULL, 1),
('P01301', 'DV04', 7, 2026, NULL, NULL, 2),
('P02502', 'DV01', 7, 2026, 214, 284, NULL),
('P02502', 'DV02', 7, 2026, 28, 37, NULL),
('P02502', 'DV03', 7, 2026, NULL, NULL, 1),
('P02502', 'DV04', 7, 2026, NULL, NULL, 2),
('P01302', 'DV01', 7, 2026, 127, 235, NULL),
('P01302', 'DV02', 7, 2026, 34, 44, NULL),
('P01302', 'DV03', 7, 2026, NULL, NULL, 1),
('P01401', 'DV01', 7, 2026, 242, 369, NULL),
('P01401', 'DV02', 7, 2026, 20, 26, NULL),
('P01401', 'DV03', 7, 2026, NULL, NULL, 1),
('P01401', 'DV04', 7, 2026, NULL, NULL, 2),
('P03302', 'DV01', 7, 2026, 172, 286, NULL),
('P03302', 'DV02', 7, 2026, 20, 30, NULL),
('P03302', 'DV03', 7, 2026, NULL, NULL, 1),
('P01502', 'DV01', 7, 2026, 177, 283, NULL);

INSERT INTO ChiSoDichVu (MaPhong, MaDV, Thang, Nam, ChiSoDau, ChiSoCuoi, SoLuong) VALUES
('P01502', 'DV02', 7, 2026, 21, 30, NULL),
('P01502', 'DV03', 7, 2026, NULL, NULL, 1),
('P02101', 'DV01', 7, 2026, 207, 294, NULL),
('P02101', 'DV02', 7, 2026, 28, 38, NULL),
('P02101', 'DV03', 7, 2026, NULL, NULL, 1),
('P02101', 'DV04', 7, 2026, NULL, NULL, 1),
('P03401', 'DV01', 7, 2026, 230, 314, NULL),
('P03401', 'DV02', 7, 2026, 31, 39, NULL),
('P03401', 'DV03', 7, 2026, NULL, NULL, 1),
('P02201', 'DV01', 8, 2026, 261, 340, NULL),
('P02201', 'DV02', 8, 2026, 33, 39, NULL),
('P02201', 'DV03', 8, 2026, NULL, NULL, 1),
('P02201', 'DV04', 8, 2026, NULL, NULL, 1),
('P03301', 'DV01', 8, 2026, 335, 407, NULL),
('P03301', 'DV02', 8, 2026, 33, 38, NULL),
('P03301', 'DV03', 8, 2026, NULL, NULL, 1),
('P03301', 'DV04', 8, 2026, NULL, NULL, 2),
('P03202', 'DV01', 8, 2026, 229, 332, NULL),
('P03202', 'DV02', 8, 2026, 41, 48, NULL),
('P03202', 'DV03', 8, 2026, NULL, NULL, 1),
('P03202', 'DV04', 8, 2026, NULL, NULL, 2),
('P01501', 'DV01', 8, 2026, 362, 470, NULL),
('P01501', 'DV02', 8, 2026, 38, 45, NULL),
('P01501', 'DV03', 8, 2026, NULL, NULL, 1),
('P01402', 'DV01', 8, 2026, 307, 390, NULL),
('P01402', 'DV02', 8, 2026, 33, 40, NULL),
('P01402', 'DV03', 8, 2026, NULL, NULL, 1),
('P01402', 'DV04', 8, 2026, NULL, NULL, 2),
('P02202', 'DV01', 8, 2026, 236, 352, NULL),
('P02202', 'DV02', 8, 2026, 30, 35, NULL),
('P02202', 'DV03', 8, 2026, NULL, NULL, 1),
('P02202', 'DV04', 8, 2026, NULL, NULL, 1),
('P02401', 'DV01', 8, 2026, 290, 396, NULL),
('P02401', 'DV02', 8, 2026, 33, 41, NULL),
('P02401', 'DV03', 8, 2026, NULL, NULL, 1),
('P02401', 'DV04', 8, 2026, NULL, NULL, 1),
('P02102', 'DV01', 8, 2026, 279, 375, NULL),
('P02102', 'DV02', 8, 2026, 30, 42, NULL),
('P02102', 'DV03', 8, 2026, NULL, NULL, 1),
('P03402', 'DV01', 8, 2026, 320, 448, NULL),
('P03402', 'DV02', 8, 2026, 31, 39, NULL),
('P03402', 'DV03', 8, 2026, NULL, NULL, 1),
('P03402', 'DV04', 8, 2026, NULL, NULL, 1),
('P02301', 'DV01', 8, 2026, 385, 505, NULL),
('P02301', 'DV02', 8, 2026, 32, 40, NULL),
('P02301', 'DV03', 8, 2026, NULL, NULL, 1),
('P02301', 'DV04', 8, 2026, NULL, NULL, 1),
('P03201', 'DV01', 8, 2026, 317, 433, NULL),
('P03201', 'DV02', 8, 2026, 35, 47, NULL),
('P03201', 'DV03', 8, 2026, NULL, NULL, 1),
('P03201', 'DV04', 8, 2026, NULL, NULL, 1),
('P02402', 'DV01', 8, 2026, 262, 370, NULL),
('P02402', 'DV02', 8, 2026, 33, 44, NULL),
('P02402', 'DV03', 8, 2026, NULL, NULL, 1),
('P01102', 'DV01', 8, 2026, 259, 344, NULL),
('P01102', 'DV02', 8, 2026, 26, 33, NULL),
('P01102', 'DV03', 8, 2026, NULL, NULL, 1),
('P01102', 'DV04', 8, 2026, NULL, NULL, 1),
('P01201', 'DV01', 8, 2026, 271, 337, NULL),
('P01201', 'DV02', 8, 2026, 39, 51, NULL),
('P01201', 'DV03', 8, 2026, NULL, NULL, 1),
('P01201', 'DV04', 8, 2026, NULL, NULL, 1),
('P02302', 'DV01', 8, 2026, 273, 403, NULL),
('P02302', 'DV02', 8, 2026, 36, 42, NULL),
('P02302', 'DV03', 8, 2026, NULL, NULL, 1),
('P02302', 'DV04', 8, 2026, NULL, NULL, 2),
('P01301', 'DV01', 8, 2026, 325, 451, NULL),
('P01301', 'DV02', 8, 2026, 34, 40, NULL),
('P01301', 'DV03', 8, 2026, NULL, NULL, 1),
('P01301', 'DV04', 8, 2026, NULL, NULL, 1),
('P02502', 'DV01', 8, 2026, 284, 354, NULL),
('P02502', 'DV02', 8, 2026, 37, 44, NULL),
('P02502', 'DV03', 8, 2026, NULL, NULL, 1),
('P02502', 'DV04', 8, 2026, NULL, NULL, 1),
('P01302', 'DV01', 8, 2026, 235, 352, NULL),
('P01302', 'DV02', 8, 2026, 44, 51, NULL),
('P01302', 'DV03', 8, 2026, NULL, NULL, 1),
('P01302', 'DV04', 8, 2026, NULL, NULL, 1),
('P01401', 'DV01', 8, 2026, 369, 440, NULL),
('P01401', 'DV02', 8, 2026, 26, 34, NULL);

INSERT INTO ChiSoDichVu (MaPhong, MaDV, Thang, Nam, ChiSoDau, ChiSoCuoi, SoLuong) VALUES
('P01401', 'DV03', 8, 2026, NULL, NULL, 1),
('P01401', 'DV04', 8, 2026, NULL, NULL, 1),
('P03302', 'DV01', 8, 2026, 286, 390, NULL),
('P03302', 'DV02', 8, 2026, 30, 35, NULL),
('P03302', 'DV03', 8, 2026, NULL, NULL, 1),
('P03302', 'DV04', 8, 2026, NULL, NULL, 1),
('P01502', 'DV01', 8, 2026, 283, 349, NULL),
('P01502', 'DV02', 8, 2026, 30, 41, NULL),
('P01502', 'DV03', 8, 2026, NULL, NULL, 1),
('P01502', 'DV04', 8, 2026, NULL, NULL, 2),
('P02101', 'DV01', 8, 2026, 294, 401, NULL),
('P02101', 'DV02', 8, 2026, 38, 46, NULL),
('P02101', 'DV03', 8, 2026, NULL, NULL, 1),
('P02101', 'DV04', 8, 2026, NULL, NULL, 1),
('P03401', 'DV01', 8, 2026, 314, 384, NULL),
('P03401', 'DV02', 8, 2026, 39, 49, NULL),
('P03401', 'DV03', 8, 2026, NULL, NULL, 1);
GO

INSERT INTO HoaDon (MaHoaDon, MaHopDong, Thang, Nam, TienPhong, TienDichVu, HanThanhToan, TrangThai) VALUES
('HO000001', 'HD000001', 6, 2026, 750000, 580500, '2026-07-10', N'Đã thanh toán'),
('HO000002', 'HD000001', 7, 2026, 750000, 563500, '2026-08-10', N'Chưa thanh toán'),
('HO000003', 'HD000005', 6, 2026, 750000, 613500, '2026-07-10', N'Đã thanh toán'),
('HO000004', 'HD000005', 7, 2026, 750000, 680000, '2026-08-10', N'Quá hạn'),
('HO000005', 'HD000009', 6, 2026, 500000, 713500, '2026-07-10', N'Đã thanh toán'),
('HO000006', 'HD000009', 7, 2026, 500000, 694000, '2026-08-10', N'Chưa thanh toán'),
('HO000007', 'HD000017', 6, 2026, 500000, 611000, '2026-07-10', N'Đã thanh toán'),
('HO000008', 'HD000017', 7, 2026, 500000, 575000, '2026-08-10', N'Chưa thanh toán'),
('HO000009', 'HD000025', 6, 2026, 600000, 525500, '2026-07-10', N'Đã thanh toán'),
('HO000010', 'HD000025', 7, 2026, 600000, 649500, '2026-08-10', N'Chưa thanh toán'),
('HO000011', 'HD000031', 6, 2026, 600000, 628500, '2026-07-10', N'Đã thanh toán'),
('HO000012', 'HD000031', 7, 2026, 600000, 400000, '2026-08-10', N'Quá hạn'),
('HO000013', 'HD000036', 6, 2026, 600000, 546500, '2026-07-10', N'Đã thanh toán'),
('HO000014', 'HD000036', 7, 2026, 600000, 648500, '2026-08-10', N'Chưa thanh toán'),
('HO000015', 'HD000041', 6, 2026, 500000, 512000, '2026-07-10', N'Đã thanh toán'),
('HO000016', 'HD000041', 7, 2026, 500000, 699500, '2026-08-10', N'Chưa thanh toán'),
('HO000017', 'HD000048', 6, 2026, 750000, 777500, '2026-07-10', N'Đã thanh toán'),
('HO000018', 'HD000048', 7, 2026, 750000, 659500, '2026-08-10', N'Chưa thanh toán'),
('HO000019', 'HD000051', 6, 2026, 500000, 707500, '2026-07-10', N'Đã thanh toán'),
('HO000020', 'HD000051', 7, 2026, 500000, 792000, '2026-08-10', N'Chưa thanh toán'),
('HO000021', 'HD000058', 6, 2026, 600000, 519000, '2026-07-10', N'Đã thanh toán'),
('HO000022', 'HD000058', 7, 2026, 600000, 431000, '2026-08-10', N'Chưa thanh toán'),
('HO000023', 'HD000063', 6, 2026, 500000, 510500, '2026-07-10', N'Đã thanh toán'),
('HO000024', 'HD000063', 7, 2026, 500000, 697000, '2026-08-10', N'Chưa thanh toán'),
('HO000025', 'HD000070', 6, 2026, 600000, 652500, '2026-07-10', N'Đã thanh toán'),
('HO000026', 'HD000070', 7, 2026, 600000, 666500, '2026-08-10', N'Chưa thanh toán'),
('HO000027', 'HD000075', 6, 2026, 500000, 416500, '2026-07-10', N'Đã thanh toán'),
('HO000028', 'HD000075', 7, 2026, 500000, 476500, '2026-08-10', N'Chưa thanh toán'),
('HO000029', 'HD000082', 6, 2026, 750000, 860500, '2026-07-10', N'Đã thanh toán'),
('HO000030', 'HD000082', 7, 2026, 750000, 573000, '2026-08-10', N'Quá hạn'),
('HO000031', 'HD000085', 6, 2026, 600000, 809500, '2026-07-10', N'Đã thanh toán'),
('HO000032', 'HD000085', 7, 2026, 600000, 740000, '2026-08-10', N'Chưa thanh toán'),
('HO000033', 'HD000090', 6, 2026, 600000, 605000, '2026-07-10', N'Đã thanh toán'),
('HO000034', 'HD000090', 7, 2026, 600000, 630000, '2026-08-10', N'Chưa thanh toán'),
('HO000035', 'HD000095', 6, 2026, 500000, 568000, '2026-07-10', N'Đã thanh toán'),
('HO000036', 'HD000095', 7, 2026, 500000, 578000, '2026-08-10', N'Quá hạn'),
('HO000037', 'HD000102', 6, 2026, 750000, 728000, '2026-07-10', N'Đã thanh toán'),
('HO000038', 'HD000102', 7, 2026, 750000, 784500, '2026-08-10', N'Quá hạn'),
('HO000039', 'HD000105', 6, 2026, 600000, 634500, '2026-07-10', N'Đã thanh toán'),
('HO000040', 'HD000105', 7, 2026, 600000, 599000, '2026-08-10', N'Chưa thanh toán'),
('HO000041', 'HD000110', 6, 2026, 750000, 526500, '2026-07-10', N'Đã thanh toán'),
('HO000042', 'HD000110', 7, 2026, 750000, 556000, '2026-08-10', N'Chưa thanh toán'),
('HO000043', 'HD000113', 6, 2026, 600000, 534500, '2026-07-10', N'Đã thanh toán'),
('HO000044', 'HD000113', 7, 2026, 600000, 604500, '2026-08-10', N'Chưa thanh toán'),
('HO000045', 'HD000118', 6, 2026, 500000, 559500, '2026-07-10', N'Đã thanh toán'),
('HO000046', 'HD000118', 7, 2026, 500000, 464000, '2026-08-10', N'Chưa thanh toán');
GO

INSERT INTO ChiTietHoaDon (MaHoaDon, MaDV, SoLuong, DonGia) VALUES
('HO000001', 'DV01', 113, 3500),
('HO000001', 'DV02', 9, 15000),
('HO000001', 'DV03', 1, 50000),
('HO000002', 'DV01', 71, 3500),
('HO000002', 'DV02', 11, 15000),
('HO000002', 'DV03', 1, 50000),
('HO000002', 'DV04', 1, 100000),
('HO000003', 'DV01', 111, 3500),
('HO000003', 'DV02', 5, 15000),
('HO000003', 'DV03', 1, 50000),
('HO000003', 'DV04', 1, 100000),
('HO000004', 'DV01', 130, 3500),
('HO000004', 'DV02', 5, 15000),
('HO000004', 'DV03', 1, 50000),
('HO000004', 'DV04', 1, 100000),
('HO000005', 'DV01', 81, 3500),
('HO000005', 'DV02', 12, 15000),
('HO000005', 'DV03', 1, 50000),
('HO000005', 'DV04', 2, 100000),
('HO000006', 'DV01', 84, 3500),
('HO000006', 'DV02', 10, 15000),
('HO000006', 'DV03', 1, 50000),
('HO000006', 'DV04', 2, 100000),
('HO000007', 'DV01', 106, 3500),
('HO000007', 'DV02', 6, 15000),
('HO000007', 'DV03', 1, 50000),
('HO000007', 'DV04', 1, 100000),
('HO000008', 'DV01', 120, 3500),
('HO000008', 'DV02', 7, 15000),
('HO000008', 'DV03', 1, 50000),
('HO000009', 'DV01', 73, 3500),
('HO000009', 'DV02', 8, 15000),
('HO000009', 'DV03', 1, 50000),
('HO000009', 'DV04', 1, 100000),
('HO000010', 'DV01', 117, 3500),
('HO000010', 'DV02', 6, 15000),
('HO000010', 'DV03', 1, 50000),
('HO000010', 'DV04', 1, 100000),
('HO000011', 'DV01', 111, 3500),
('HO000011', 'DV02', 6, 15000),
('HO000011', 'DV03', 1, 50000),
('HO000011', 'DV04', 1, 100000),
('HO000012', 'DV01', 70, 3500),
('HO000012', 'DV02', 7, 15000),
('HO000012', 'DV03', 1, 50000),
('HO000013', 'DV01', 99, 3500),
('HO000013', 'DV02', 10, 15000),
('HO000013', 'DV03', 1, 50000),
('HO000014', 'DV01', 91, 3500),
('HO000014', 'DV02', 12, 15000),
('HO000014', 'DV03', 1, 50000),
('HO000014', 'DV04', 1, 100000),
('HO000015', 'DV01', 102, 3500),
('HO000015', 'DV02', 7, 15000),
('HO000015', 'DV03', 1, 50000),
('HO000016', 'DV01', 127, 3500),
('HO000016', 'DV02', 7, 15000),
('HO000016', 'DV03', 1, 50000),
('HO000016', 'DV04', 1, 100000),
('HO000017', 'DV01', 125, 3500),
('HO000017', 'DV02', 6, 15000),
('HO000017', 'DV03', 1, 50000),
('HO000017', 'DV04', 2, 100000),
('HO000018', 'DV01', 107, 3500),
('HO000018', 'DV02', 9, 15000),
('HO000018', 'DV03', 1, 50000),
('HO000018', 'DV04', 1, 100000),
('HO000019', 'DV01', 125, 3500),
('HO000019', 'DV02', 8, 15000),
('HO000019', 'DV03', 1, 50000),
('HO000019', 'DV04', 1, 100000),
('HO000020', 'DV01', 112, 3500),
('HO000020', 'DV02', 10, 15000),
('HO000020', 'DV03', 1, 50000),
('HO000020', 'DV04', 2, 100000),
('HO000021', 'DV01', 104, 3500),
('HO000021', 'DV02', 7, 15000),
('HO000021', 'DV03', 1, 50000),
('HO000022', 'DV01', 66, 3500),
('HO000022', 'DV02', 10, 15000);

INSERT INTO ChiTietHoaDon (MaHoaDon, MaDV, SoLuong, DonGia) VALUES
('HO000022', 'DV03', 1, 50000),
('HO000023', 'DV01', 73, 3500),
('HO000023', 'DV02', 7, 15000),
('HO000023', 'DV03', 1, 50000),
('HO000023', 'DV04', 1, 100000),
('HO000024', 'DV01', 102, 3500),
('HO000024', 'DV02', 6, 15000),
('HO000024', 'DV03', 1, 50000),
('HO000024', 'DV04', 2, 100000),
('HO000025', 'DV01', 85, 3500),
('HO000025', 'DV02', 7, 15000),
('HO000025', 'DV03', 1, 50000),
('HO000025', 'DV04', 2, 100000),
('HO000026', 'DV01', 109, 3500),
('HO000026', 'DV02', 9, 15000),
('HO000026', 'DV03', 1, 50000),
('HO000026', 'DV04', 1, 100000),
('HO000027', 'DV01', 79, 3500),
('HO000027', 'DV02', 6, 15000),
('HO000027', 'DV03', 1, 50000),
('HO000028', 'DV01', 79, 3500),
('HO000028', 'DV02', 10, 15000),
('HO000028', 'DV03', 1, 50000),
('HO000029', 'DV01', 123, 3500),
('HO000029', 'DV02', 12, 15000),
('HO000029', 'DV03', 1, 50000),
('HO000029', 'DV04', 2, 100000),
('HO000030', 'DV01', 78, 3500),
('HO000030', 'DV02', 10, 15000),
('HO000030', 'DV03', 1, 50000),
('HO000030', 'DV04', 1, 100000),
('HO000031', 'DV01', 117, 3500),
('HO000031', 'DV02', 10, 15000),
('HO000031', 'DV03', 1, 50000),
('HO000031', 'DV04', 2, 100000),
('HO000032', 'DV01', 110, 3500),
('HO000032', 'DV02', 7, 15000),
('HO000032', 'DV03', 1, 50000),
('HO000032', 'DV04', 2, 100000),
('HO000033', 'DV01', 100, 3500),
('HO000033', 'DV02', 7, 15000),
('HO000033', 'DV03', 1, 50000),
('HO000033', 'DV04', 1, 100000),
('HO000034', 'DV01', 70, 3500),
('HO000034', 'DV02', 9, 15000),
('HO000034', 'DV03', 1, 50000),
('HO000034', 'DV04', 2, 100000),
('HO000035', 'DV01', 68, 3500),
('HO000035', 'DV02', 12, 15000),
('HO000035', 'DV03', 1, 50000),
('HO000035', 'DV04', 1, 100000),
('HO000036', 'DV01', 108, 3500),
('HO000036', 'DV02', 10, 15000),
('HO000036', 'DV03', 1, 50000),
('HO000037', 'DV01', 98, 3500),
('HO000037', 'DV02', 9, 15000),
('HO000037', 'DV03', 1, 50000),
('HO000037', 'DV04', 2, 100000),
('HO000038', 'DV01', 127, 3500),
('HO000038', 'DV02', 6, 15000),
('HO000038', 'DV03', 1, 50000),
('HO000038', 'DV04', 2, 100000),
('HO000039', 'DV01', 67, 3500),
('HO000039', 'DV02', 10, 15000),
('HO000039', 'DV03', 1, 50000),
('HO000039', 'DV04', 2, 100000),
('HO000040', 'DV01', 114, 3500),
('HO000040', 'DV02', 10, 15000),
('HO000040', 'DV03', 1, 50000),
('HO000041', 'DV01', 69, 3500),
('HO000041', 'DV02', 9, 15000),
('HO000041', 'DV03', 1, 50000),
('HO000041', 'DV04', 1, 100000),
('HO000042', 'DV01', 106, 3500),
('HO000042', 'DV02', 9, 15000),
('HO000042', 'DV03', 1, 50000),
('HO000043', 'DV01', 117, 3500),
('HO000043', 'DV02', 5, 15000),
('HO000043', 'DV03', 1, 50000),
('HO000044', 'DV01', 87, 3500);

INSERT INTO ChiTietHoaDon (MaHoaDon, MaDV, SoLuong, DonGia) VALUES
('HO000044', 'DV02', 10, 15000),
('HO000044', 'DV03', 1, 50000),
('HO000044', 'DV04', 1, 100000),
('HO000045', 'DV01', 107, 3500),
('HO000045', 'DV02', 9, 15000),
('HO000045', 'DV03', 1, 50000),
('HO000046', 'DV01', 84, 3500),
('HO000046', 'DV02', 8, 15000),
('HO000046', 'DV03', 1, 50000);
GO

INSERT INTO ThanhToan (MaHoaDon, NgayThanhToan, SoTien, HinhThucTT) VALUES
('HO000001', '2026-07-05', 1330500, N'Tiền mặt'),
('HO000003', '2026-07-05', 1363500, N'Tiền mặt'),
('HO000005', '2026-07-05', 1213500, N'Chuyển khoản'),
('HO000007', '2026-07-05', 1111000, N'Tiền mặt'),
('HO000009', '2026-07-05', 1125500, N'Chuyển khoản'),
('HO000011', '2026-07-05', 1228500, N'Tiền mặt'),
('HO000013', '2026-07-05', 1146500, N'Chuyển khoản'),
('HO000015', '2026-07-05', 1012000, N'Tiền mặt'),
('HO000017', '2026-07-05', 1527500, N'Tiền mặt'),
('HO000019', '2026-07-05', 1207500, N'Tiền mặt'),
('HO000021', '2026-07-05', 1119000, N'Chuyển khoản'),
('HO000023', '2026-07-05', 1010500, N'Chuyển khoản'),
('HO000025', '2026-07-05', 1252500, N'Chuyển khoản'),
('HO000027', '2026-07-05', 916500, N'Tiền mặt'),
('HO000029', '2026-07-05', 1610500, N'Chuyển khoản'),
('HO000031', '2026-07-05', 1409500, N'Chuyển khoản'),
('HO000033', '2026-07-05', 1205000, N'Tiền mặt'),
('HO000035', '2026-07-05', 1068000, N'Tiền mặt'),
('HO000037', '2026-07-05', 1478000, N'Tiền mặt'),
('HO000039', '2026-07-05', 1234500, N'Tiền mặt'),
('HO000041', '2026-07-05', 1276500, N'Chuyển khoản'),
('HO000043', '2026-07-05', 1134500, N'Chuyển khoản'),
('HO000045', '2026-07-05', 1059500, N'Chuyển khoản');
GO

-- 3. VIEW BÁO CÁO
    

-- 3.1 Danh sách phòng còn trống
CREATE VIEW vw_PhongTrong AS
SELECT  p.MaPhong, tn.TenToa, p.SoPhong, p.Tang, p.GioiTinhPhong,
        lp.TenLoaiPhong, lp.SucChua, lp.DonGia
FROM    Phong p
JOIN    ToaNha tn   ON p.MaToa = tn.MaToa
JOIN    LoaiPhong lp ON p.MaLoaiPhong = lp.MaLoaiPhong
WHERE   p.TinhTrang = N'Trống';
GO

-- 3.2 Danh sách sinh viên đang ở KTX
CREATE VIEW vw_SinhVienDangO AS
SELECT  sv.MaSV, sv.HoTen, sv.GioiTinh, sv.Lop, sv.Khoa,
        hd.MaHopDong, p.MaPhong, tn.TenToa, p.SoPhong,
        hd.NgayBatDau, hd.NgayKetThucDK
FROM    HopDong hd
JOIN    SinhVien sv ON hd.MaSV = sv.MaSV
JOIN    Phong p     ON hd.MaPhong = p.MaPhong
JOIN    ToaNha tn   ON p.MaToa = tn.MaToa
WHERE   hd.TrangThai = N'Đang hiệu lực';
GO

-- 3.3 Hóa đơn chưa thanh toán / quá hạn
CREATE VIEW vw_HoaDonChuaThanhToan AS
SELECT  hdon.MaHoaDon, sv.MaSV, sv.HoTen, p.MaPhong,
        hdon.Thang, hdon.Nam, hdon.TongTien, hdon.HanThanhToan, hdon.TrangThai
FROM    HoaDon hdon
JOIN    HopDong hd ON hdon.MaHopDong = hd.MaHopDong
JOIN    SinhVien sv ON hd.MaSV = sv.MaSV
JOIN    Phong p ON hd.MaPhong = p.MaPhong
WHERE   hdon.TrangThai IN (N'Chưa thanh toán', N'Quá hạn');
GO

-- 3.4 Doanh thu theo tháng (chỉ tính hóa đơn đã thanh toán)
CREATE VIEW vw_DoanhThuTheoThang AS
SELECT  Nam, Thang, SUM(TongTien) AS DoanhThu, COUNT(*) AS SoHoaDon
FROM    HoaDon
WHERE   TrangThai = N'Đã thanh toán'
GROUP BY Nam, Thang;
GO

/* =====================================================================
   4. FUNCTION
   ===================================================================== */

-- 4.1 Số ngày sinh viên đã / đang ở theo hợp đồng
CREATE FUNCTION fn_SoNgayO (@MaHopDong CHAR(10))
RETURNS INT
AS
BEGIN
    DECLARE @SoNgay INT;
    SELECT @SoNgay = DATEDIFF(DAY, NgayBatDau,
                        COALESCE(NgayTraThucTe, CAST(GETDATE() AS DATE)))
    FROM HopDong
    WHERE MaHopDong = @MaHopDong;
    RETURN @SoNgay;
END;
GO

-- 4.2 Đếm số phòng còn trống trong 1 tòa
CREATE FUNCTION fn_SoPhongTrongTheoToa (@MaToa CHAR(5))
RETURNS INT
AS
BEGIN
    DECLARE @SoPhong INT;
    SELECT @SoPhong = COUNT(*)
    FROM Phong
    WHERE MaToa = @MaToa AND TinhTrang = N'Trống';
    RETURN @SoPhong;
END;
GO


-- 5. STORED PROCEDURE - CÁC NGHIỆP VỤ CHÍNH

-- 5.1 Lập hợp đồng thuê phòng mới (kèm sinh mã tự động)
CREATE PROCEDURE sp_ThemHopDong
    @MaSV           CHAR(10),
    @MaPhong        CHAR(6),
    @MaNV           CHAR(6),
    @NgayBatDau     DATE,
    @NgayKetThucDK  DATE
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        IF NOT EXISTS (SELECT 1 FROM Phong WHERE MaPhong = @MaPhong AND TinhTrang <> N'Bảo trì')
        BEGIN
            RAISERROR(N'Phòng không tồn tại hoặc đang bảo trì.', 16, 1);
            RETURN;
        END

        DECLARE @MaHopDongMoi CHAR(10);
        SELECT @MaHopDongMoi = 'HD' + RIGHT('000000' +
                CAST(ISNULL(MAX(CAST(SUBSTRING(MaHopDong,3,8) AS INT)),0) + 1 AS VARCHAR), 8)
        FROM HopDong;

        BEGIN TRAN;
            INSERT INTO HopDong (MaHopDong, MaSV, MaPhong, MaNV, NgayBatDau, NgayKetThucDK)
            VALUES (@MaHopDongMoi, @MaSV, @MaPhong, @MaNV, @NgayBatDau, @NgayKetThucDK);
        COMMIT TRAN;

        PRINT N'Lập hợp đồng thành công: ' + @MaHopDongMoi;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRAN;
        THROW;
    END CATCH
END;
GO

-- 5.2 Trả phòng / kết thúc hợp đồng
CREATE PROCEDURE sp_TraPhong
    @MaHopDong      CHAR(10),
    @NgayTraThucTe  DATE = NULL
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        IF NOT EXISTS (SELECT 1 FROM HopDong WHERE MaHopDong = @MaHopDong AND TrangThai = N'Đang hiệu lực')
        BEGIN
            RAISERROR(N'Hợp đồng không tồn tại hoặc đã kết thúc.', 16, 1);
            RETURN;
        END

        UPDATE HopDong
        SET NgayTraThucTe = ISNULL(@NgayTraThucTe, CAST(GETDATE() AS DATE)),
            TrangThai = N'Đã kết thúc'
        WHERE MaHopDong = @MaHopDong;

        PRINT N'Đã cập nhật trả phòng cho hợp đồng ' + @MaHopDong;
    END TRY
    BEGIN CATCH
        THROW;
    END CATCH
END;
GO

-- 5.3 Lập hóa đơn tháng cho 1 hợp đồng (tự tính tiền phòng + tiền dịch vụ)
CREATE PROCEDURE sp_LapHoaDon
    @MaHopDong  CHAR(10),
    @Thang      INT,
    @Nam        INT,
    @HanThanhToan DATE = NULL
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        IF EXISTS (SELECT 1 FROM HoaDon WHERE MaHopDong = @MaHopDong AND Thang = @Thang AND Nam = @Nam)
        BEGIN
            RAISERROR(N'Hóa đơn tháng này đã tồn tại.', 16, 1);
            RETURN;
        END

        DECLARE @MaPhong CHAR(6), @TienPhong DECIMAL(12,0);
        SELECT @MaPhong = hd.MaPhong, @TienPhong = lp.DonGia
        FROM HopDong hd
        JOIN Phong p ON hd.MaPhong = p.MaPhong
        JOIN LoaiPhong lp ON p.MaLoaiPhong = lp.MaLoaiPhong
        WHERE hd.MaHopDong = @MaHopDong;

        DECLARE @MaHoaDonMoi CHAR(10);
        SELECT @MaHoaDonMoi = 'HO' + RIGHT('000000' +
                CAST(ISNULL(MAX(CAST(SUBSTRING(MaHoaDon,3,8) AS INT)),0) + 1 AS VARCHAR), 8)
        FROM HoaDon;

        BEGIN TRAN;
            -- Tạo hóa đơn (tiền dịch vụ tạm 0, cập nhật sau khi chèn chi tiết)
            INSERT INTO HoaDon (MaHoaDon, MaHopDong, Thang, Nam, TienPhong, TienDichVu, HanThanhToan)
            VALUES (@MaHoaDonMoi, @MaHopDong, @Thang, @Nam, @TienPhong, 0,
                    ISNULL(@HanThanhToan, DATEADD(DAY, 40, DATEFROMPARTS(@Nam, @Thang, 1))) -- hạn TT: ~10 ngày của tháng sau
                    );

            -- Chèn chi tiết từ ChiSoDichVu (điện/nước tính theo chỉ số, còn lại theo SoLuong)
            INSERT INTO ChiTietHoaDon (MaHoaDon, MaDV, SoLuong, DonGia)
            SELECT  @MaHoaDonMoi,
                    cs.MaDV,
                    CASE WHEN cs.ChiSoCuoi IS NOT NULL THEN cs.ChiSoCuoi - cs.ChiSoDau
                         ELSE cs.SoLuong END,
                    dv.DonGia
            FROM ChiSoDichVu cs
            JOIN DichVu dv ON cs.MaDV = dv.MaDV
            WHERE cs.MaPhong = @MaPhong AND cs.Thang = @Thang AND cs.Nam = @Nam;

            -- Cập nhật lại tổng tiền dịch vụ trên hóa đơn
            UPDATE HoaDon
            SET TienDichVu = ISNULL((SELECT SUM(ThanhTien) FROM ChiTietHoaDon WHERE MaHoaDon = @MaHoaDonMoi), 0)
            WHERE MaHoaDon = @MaHoaDonMoi;
        COMMIT TRAN;

        PRINT N'Đã lập hóa đơn: ' + @MaHoaDonMoi;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRAN;
        THROW;
    END CATCH
END;
GO

-- 5.4 Ghi nhận thanh toán hóa đơn
CREATE PROCEDURE sp_ThanhToanHoaDon
    @MaHoaDon   CHAR(10),
    @SoTien     DECIMAL(12,0),
    @HinhThucTT NVARCHAR(30) = N'Tiền mặt'
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        BEGIN TRAN;
            INSERT INTO ThanhToan (MaHoaDon, SoTien, HinhThucTT)
            VALUES (@MaHoaDon, @SoTien, @HinhThucTT);

            DECLARE @TongTien DECIMAL(12,0), @DaThanhToan DECIMAL(12,0);
            SELECT @TongTien = TongTien FROM HoaDon WHERE MaHoaDon = @MaHoaDon;
            SELECT @DaThanhToan = ISNULL(SUM(SoTien),0) FROM ThanhToan WHERE MaHoaDon = @MaHoaDon;

            IF @DaThanhToan >= @TongTien
                UPDATE HoaDon SET TrangThai = N'Đã thanh toán' WHERE MaHoaDon = @MaHoaDon;
        COMMIT TRAN;

        PRINT N'Đã ghi nhận thanh toán cho hóa đơn ' + @MaHoaDon;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRAN;
        THROW;
    END CATCH
END;
GO

-- 6. TRIGGER - RÀNG BUỘC NGHIỆP VỤ

-- 6.1 Khi thêm/sửa hợp đồng: kiểm tra sức chứa phòng & giới tính phù hợp
CREATE TRIGGER trg_KiemTraHopDong
ON HopDong
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    -- Kiểm tra giới tính sinh viên khớp giới tính phòng
    IF EXISTS (
        SELECT 1
        FROM inserted i
        JOIN SinhVien sv ON i.MaSV = sv.MaSV
        JOIN Phong p ON i.MaPhong = p.MaPhong
        WHERE i.TrangThai = N'Đang hiệu lực' AND sv.GioiTinh <> p.GioiTinhPhong
    )
    BEGIN
        RAISERROR(N'Giới tính sinh viên không phù hợp với phòng.', 16, 1);
        ROLLBACK TRAN;
        RETURN;
    END

    -- Kiểm tra sức chứa: số hợp đồng đang hiệu lực trong phòng không vượt SucChua
    IF EXISTS (
        SELECT p.MaPhong
        FROM Phong p
        JOIN LoaiPhong lp ON p.MaLoaiPhong = lp.MaLoaiPhong
        WHERE p.MaPhong IN (SELECT MaPhong FROM inserted)
        GROUP BY p.MaPhong, lp.SucChua
        HAVING (SELECT COUNT(*) FROM HopDong h
                WHERE h.MaPhong = p.MaPhong AND h.TrangThai = N'Đang hiệu lực') > lp.SucChua
    )
    BEGIN
        RAISERROR(N'Phòng đã đủ sức chứa, không thể thêm hợp đồng.', 16, 1);
        ROLLBACK TRAN;
        RETURN;
    END
END;
GO

-- 6.2 Tự động cập nhật tình trạng phòng khi hợp đồng thay đổi
CREATE TRIGGER trg_CapNhatTinhTrangPhong
ON HopDong
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    UPDATE p
    SET p.TinhTrang = CASE
            WHEN EXISTS (SELECT 1 FROM HopDong h WHERE h.MaPhong = p.MaPhong AND h.TrangThai = N'Đang hiệu lực')
            THEN N'Đang sử dụng'
            ELSE N'Trống'
        END
    FROM Phong p
    WHERE p.MaPhong IN (SELECT MaPhong FROM inserted)
      AND p.TinhTrang <> N'Bảo trì';
END;
GO