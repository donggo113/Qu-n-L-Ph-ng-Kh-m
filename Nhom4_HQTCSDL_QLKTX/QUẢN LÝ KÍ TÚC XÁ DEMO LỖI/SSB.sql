
USE QLKyTucXa;
GO

-- =====================================================
-- SESSION B
-- DEMO LỖI + KHẮC PHỤC + DỌN DỮ LIỆU
-- =====================================================


-- =====================================================
-- 7.1 LOST UPDATE
-- =====================================================

-- B1: Đọc giá phòng
DECLARE @GiaB DECIMAL(12,0);

SELECT @GiaB = DonGia
FROM LoaiPhong
WHERE MaLoaiPhong = 'LP01';

SELECT @GiaB AS Gia_Session_B;


-- B2: Cập nhật tăng 100.000
-- Chạy sau A1

UPDATE LoaiPhong
SET DonGia = 750000 + 100000
WHERE MaLoaiPhong = 'LP01';


-- KIỂM TRA

SELECT MaLoaiPhong, DonGia
FROM LoaiPhong
WHERE MaLoaiPhong = 'LP01';


-- =====================================================
-- 7.1 KHẮC PHỤC LOST UPDATE
-- =====================================================

BEGIN TRAN;

DECLARE @GiaCuB DECIMAL(12,0);

SELECT @GiaCuB = DonGia
FROM LoaiPhong WITH (UPDLOCK, HOLDLOCK)
WHERE MaLoaiPhong = 'LP01';

UPDATE LoaiPhong
SET DonGia = @GiaCuB + 100000
WHERE MaLoaiPhong = 'LP01';

COMMIT TRAN;


-- KIỂM TRA

SELECT MaLoaiPhong, DonGia
FROM LoaiPhong
WHERE MaLoaiPhong = 'LP01';


-- DỌN DỮ LIỆU

UPDATE LoaiPhong
SET DonGia = 750000
WHERE MaLoaiPhong = 'LP01';


-- =====================================================
-- 7.2 DIRTY READ
-- =====================================================

-- B1: Đọc dữ liệu chưa COMMIT

SELECT TienPhong
FROM HoaDon WITH (NOLOCK)
WHERE MaHoaDon = 'HO00000001';


-- =====================================================
-- 7.2 KHẮC PHỤC DIRTY READ
-- =====================================================

SET TRANSACTION ISOLATION LEVEL READ COMMITTED;

SELECT TienPhong
FROM HoaDon
WHERE MaHoaDon = 'HO00000001';


-- =====================================================
-- 7.3 NON-REPEATABLE READ
-- =====================================================

-- B1: Cập nhật trạng thái và COMMIT

UPDATE HopDong
SET TrangThai = N'Đã kết thúc'
WHERE MaHopDong = 'HD00000001';


-- KIỂM TRA

SELECT MaHopDong, TrangThai
FROM HopDong
WHERE MaHopDong = 'HD00000001';


-- =====================================================
-- 7.3 KHẮC PHỤC NON-REPEATABLE READ
-- =====================================================

-- Chạy sau khi Session A đã đọc lần 1.
-- Session B sẽ phải chờ khóa của Session A.

UPDATE HopDong
SET TrangThai = N'Đã kết thúc'
WHERE MaHopDong = 'HD00000001';


-- DỌN DỮ LIỆU

UPDATE HopDong
SET TrangThai = N'Đang hiệu lực'
WHERE MaHopDong = 'HD00000001';


-- =====================================================
-- 7.4 PHANTOM READ
-- =====================================================

-- B1: Thêm hợp đồng mới

INSERT INTO HopDong
(
    MaHopDong,
    MaSV,
    MaPhong,
    MaNV,
    NgayBatDau,
    NgayKetThucDK
)
VALUES
(
    'HD99999999',
    'SV0001',
    'P01102',
    NULL,
    GETDATE(),
    DATEADD(MONTH,6,GETDATE())
);


-- KIỂM TRA

SELECT *
FROM HopDong
WHERE MaHopDong = 'HD99999999';


-- DỌN DỮ LIỆU

DELETE FROM HopDong
WHERE MaHopDong = 'HD99999999';


-- =====================================================
-- 7.4 KHẮC PHỤC PHANTOM READ
-- =====================================================

-- Khi Session A đang SERIALIZABLE,
-- câu INSERT này sẽ chờ khóa phạm vi.

INSERT INTO HopDong
(
    MaHopDong,
    MaSV,
    MaPhong,
    MaNV,
    NgayBatDau,
    NgayKetThucDK
)
VALUES
(
    'HD99999999',
    'SV0001',
    'P01102',
    NULL,
    GETDATE(),
    DATEADD(MONTH,6,GETDATE())
);


-- DỌN DỮ LIỆU

DELETE FROM HopDong
WHERE MaHopDong = 'HD99999999';


-- =====================================================
-- 7.5 DEADLOCK
-- =====================================================

-- B1: Khóa HoaDon trước

BEGIN TRAN;

UPDATE HoaDon
SET TienDichVu = TienDichVu + 0
WHERE MaHoaDon = 'HO00000001';

WAITFOR DELAY '00:00:05';


-- B2: Cập nhật HopDong
-- Chạy sau A1

UPDATE HopDong
SET TrangThai = N'Đang hiệu lực'
WHERE MaHopDong =
(
    SELECT MaHopDong
    FROM HoaDon
    WHERE MaHoaDon = 'HO00000001'
);

COMMIT TRAN;


-- KIỂM TRA

SELECT MaHoaDon, TrangThai
FROM HoaDon
WHERE MaHoaDon = 'HO00000001';

SELECT MaHopDong, TrangThai
FROM HopDong
WHERE MaHopDong = 'HD00000001';


-- DỌN DỮ LIỆU

UPDATE HopDong
SET TrangThai = N'Đang hiệu lực'
WHERE MaHopDong = 'HD00000001';

UPDATE HoaDon
SET TrangThai = N'Chưa thanh toán'
WHERE MaHoaDon = 'HO00000001';


-- =====================================================
-- 7.5 KHẮC PHỤC DEADLOCK
-- =====================================================

SET XACT_ABORT ON;

BEGIN TRY
    BEGIN TRAN;

    -- Cập nhật cùng thứ tự với Session A
    UPDATE HopDong
    SET TrangThai = N'Đang hiệu lực'
    WHERE MaHopDong = 'HD00000001';

    UPDATE HoaDon
    SET TrangThai = N'Chưa thanh toán'
    WHERE MaHopDong = 'HD00000001';

    COMMIT TRAN;
END TRY
BEGIN CATCH
    IF XACT_STATE() <> 0
        ROLLBACK TRAN;

    THROW;
END CATCH;


-- KIỂM TRA

SELECT *
FROM HopDong
WHERE MaHopDong = 'HD00000001';

SELECT *
FROM HoaDon
WHERE MaHoaDon = 'HO00000001';


-- DỌN DỮ LIỆU CUỐI

UPDATE HopDong
SET TrangThai = N'Đang hiệu lực'
WHERE MaHopDong = 'HD00000001';

UPDATE HoaDon
SET TrangThai = N'Chưa thanh toán'
WHERE MaHoaDon = 'HO00000001';