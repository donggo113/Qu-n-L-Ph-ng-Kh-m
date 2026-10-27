
USE QLKyTucXa;
GO

-- =====================================================
-- SESSION A
-- DEMO LỖI + KHẮC PHỤC + DỌN DỮ LIỆU
-- =====================================================


-- =====================================================
-- 7.1 LOST UPDATE
-- =====================================================

-- A1: Đọc giá phòng
DECLARE @GiaA DECIMAL(12,0);

SELECT @GiaA = DonGia
FROM LoaiPhong
WHERE MaLoaiPhong = 'LP01';

SELECT @GiaA AS Gia_Session_A;


-- A2: Cập nhật tăng 50.000
-- Chạy sau B1

UPDATE LoaiPhong
SET DonGia = 750000 + 50000
WHERE MaLoaiPhong = 'LP01';


-- KIỂM TRA

SELECT MaLoaiPhong, DonGia
FROM LoaiPhong
WHERE MaLoaiPhong = 'LP01';


-- DỌN DỮ LIỆU 7.1

UPDATE LoaiPhong
SET DonGia = 750000
WHERE MaLoaiPhong = 'LP01';


-- =====================================================
-- 7.1 KHẮC PHỤC LOST UPDATE
-- =====================================================

-- Chạy riêng, thay cho phần UPDATE demo ở trên

BEGIN TRAN;

DECLARE @GiaCuA DECIMAL(12,0);

SELECT @GiaCuA = DonGia
FROM LoaiPhong WITH (UPDLOCK, HOLDLOCK)
WHERE MaLoaiPhong = 'LP01';

UPDATE LoaiPhong
SET DonGia = @GiaCuA + 50000
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

-- A1: Sửa hóa đơn nhưng chưa COMMIT

BEGIN TRAN;

UPDATE HoaDon
SET TienPhong = 999999999
WHERE MaHoaDon = 'HO00000001';

WAITFOR DELAY '00:00:10';


-- A2: Hoàn tác
-- Chạy sau B1

ROLLBACK TRAN;


-- KIỂM TRA

SELECT MaHoaDon, TienPhong
FROM HoaDon
WHERE MaHoaDon = 'HO00000001';


-- =====================================================
-- 7.2 KHẮC PHỤC DIRTY READ
-- =====================================================

SET TRANSACTION ISOLATION LEVEL READ COMMITTED;

SELECT TienPhong
FROM HoaDon
WHERE MaHoaDon = 'HO00000001';


-- =====================================================
-- DỌN DỮ LIỆU 7.2
-- =====================================================

-- Nếu A đã ROLLBACK thì không cần UPDATE lại.
-- Kiểm tra giá trị gốc trước khi khôi phục thủ công.

SELECT *
FROM HoaDon
WHERE MaHoaDon = 'HO00000001';


-- =====================================================
-- 7.3 NON-REPEATABLE READ
-- =====================================================

-- A1: Đọc lần 1

BEGIN TRAN;

SELECT TrangThai AS Lan_1
FROM HopDong
WHERE MaHopDong = 'HD00000001';

WAITFOR DELAY '00:00:10';


-- A2: Đọc lần 2
-- Chạy sau B1

SELECT TrangThai AS Lan_2
FROM HopDong
WHERE MaHopDong = 'HD00000001';

COMMIT TRAN;


-- KIỂM TRA

SELECT MaHopDong, TrangThai
FROM HopDong
WHERE MaHopDong = 'HD00000001';


-- DỌN DỮ LIỆU 7.3

UPDATE HopDong
SET TrangThai = N'Đang hiệu lực'
WHERE MaHopDong = 'HD00000001';


-- =====================================================
-- 7.3 KHẮC PHỤC NON-REPEATABLE READ
-- =====================================================

SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;

BEGIN TRAN;

SELECT TrangThai AS Lan_1
FROM HopDong
WHERE MaHopDong = 'HD00000001';

WAITFOR DELAY '00:00:10';

SELECT TrangThai AS Lan_2
FROM HopDong
WHERE MaHopDong = 'HD00000001';

COMMIT TRAN;


-- DỌN DỮ LIỆU

UPDATE HopDong
SET TrangThai = N'Đang hiệu lực'
WHERE MaHopDong = 'HD00000001';


-- =====================================================
-- 7.4 PHANTOM READ
-- =====================================================

-- A1: Đếm lần 1

SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;

BEGIN TRAN;

SELECT COUNT(*) AS SoHopDong_Lan_1
FROM HopDong
WHERE MaPhong = 'P01102'
  AND TrangThai = N'Đang hiệu lực';

WAITFOR DELAY '00:00:10';


-- A2: Đếm lần 2
-- Chạy sau B1

SELECT COUNT(*) AS SoHopDong_Lan_2
FROM HopDong
WHERE MaPhong = 'P01102'
  AND TrangThai = N'Đang hiệu lực';

COMMIT TRAN;


-- KIỂM TRA

SELECT *
FROM HopDong
WHERE MaHopDong = 'HD99999999';


-- DỌN DỮ LIỆU 7.4

DELETE FROM HopDong
WHERE MaHopDong = 'HD99999999';


-- =====================================================
-- 7.4 KHẮC PHỤC PHANTOM READ
-- =====================================================

SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

BEGIN TRAN;

SELECT COUNT(*) AS SoHopDong_Lan_1
FROM HopDong
WHERE MaPhong = 'P01102'
  AND TrangThai = N'Đang hiệu lực';

WAITFOR DELAY '00:00:10';

SELECT COUNT(*) AS SoHopDong_Lan_2
FROM HopDong
WHERE MaPhong = 'P01102'
  AND TrangThai = N'Đang hiệu lực';

COMMIT TRAN;


-- =====================================================
-- 7.5 DEADLOCK
-- =====================================================

-- A1: Khóa HopDong trước

BEGIN TRAN;

UPDATE HopDong
SET TrangThai = N'Đang hiệu lực'
WHERE MaHopDong = 'HD00000001';

WAITFOR DELAY '00:00:05';


-- A2: Cập nhật HoaDon
-- Chạy sau B1

UPDATE HoaDon
SET TrangThai = N'Chưa thanh toán'
WHERE MaHopDong = 'HD00000001';

COMMIT TRAN;


-- KIỂM TRA

SELECT MaHopDong, TrangThai
FROM HopDong
WHERE MaHopDong = 'HD00000001';

SELECT MaHoaDon, TrangThai
FROM HoaDon
WHERE MaHoaDon = 'HO00000001';


-- DỌN DỮ LIỆU 7.5

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

    -- Luôn cập nhật HopDong trước
    UPDATE HopDong
    SET TrangThai = N'Đang hiệu lực'
    WHERE MaHopDong = 'HD00000001';

    -- Sau đó cập nhật HoaDon
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