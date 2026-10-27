USE QLKyTucXa;
GO

SET TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- 7.1 LOST UPDATE (MẤT DỮ LIỆU CẬP NHẬT)
-- Thứ tự: A1 -> B1 -> A2 -> B2 -> KIỂM TRA

-- [B1] Đọc giá phòng (chạy SAU A1)
DECLARE @GiaB DECIMAL(12,0);

SELECT @GiaB = DonGia
FROM LoaiPhong
WHERE MaLoaiPhong = 'LP01';

SELECT @GiaB AS Gia_Session_B;   -- 750000


-- [B2] Cập nhật tăng 100.000 (chạy SAU A2)
-- Dùng số cứng 750000 để mô phỏng giá trị đã đọc ở B1 (biến mất sau khi batch kết thúc).
UPDATE LoaiPhong
SET DonGia = 750000 + 100000
WHERE MaLoaiPhong = 'LP01';


-- KIỂM TRA
SELECT MaLoaiPhong, DonGia
FROM LoaiPhong
WHERE MaLoaiPhong = 'LP01';   -- 850000 (sai, đúng phải 900000)

-- 7.1 KHẮC PHỤC LOST UPDATE
-- Chạy NGAY sau khi Session A bắt đầu khối khắc phục (trong 10 giây).
-- B sẽ CHỜ ở câu SELECT tới khi A COMMIT, rồi đọc 800000 và cộng thành 900000.

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
WHERE MaLoaiPhong = 'LP01';   -- 900000


-- DỌN DỮ LIỆU
UPDATE LoaiPhong
SET DonGia = 750000
WHERE MaLoaiPhong = 'LP01';

-- 7.2 DIRTY READ (ĐỌC DỮ LIỆU RÁC)
-- Chạy TRONG 10 GIÂY sau khi Session A bắt đầu khối [A1+A2] của 7.2


-- [B1] Đọc dữ liệu chưa COMMIT
SELECT TienPhong
FROM HoaDon WITH (NOLOCK)
WHERE MaHoaDon = 'HO000001';   -- thấy 999999999 (dữ liệu rác)

-- Chờ A xong (ROLLBACK) rồi chạy lại: sẽ thấy 750000.


-- 7.2 KHẮC PHỤC DIRTY READ
-- Chạy TRONG 10 GIÂY sau khi Session A bắt đầu lại khối [A1+A2] của 7.2.
-- B sẽ CHỜ tới khi A ROLLBACK rồi trả về 750000.

SET TRANSACTION ISOLATION LEVEL READ COMMITTED;

SELECT TienPhong
FROM HoaDon
WHERE MaHoaDon = 'HO000001';   -- 750000

-- 7.3 NON-REPEATABLE READ (KHÔNG ĐỌC LẠI ĐƯỢC DỮ LIỆU)
-- Chạy TRONG 10 GIÂY sau khi Session A bắt đầu khối [A1+A2] của 7.3

-- [B1] Cập nhật trạng thái và COMMIT
UPDATE HopDong
SET TrangThai = N'Đã kết thúc'
WHERE MaHopDong = 'HD000001';


-- KIỂM TRA
SELECT MaHopDong, TrangThai
FROM HopDong
WHERE MaHopDong = 'HD000001';

-- 7.3 KHẮC PHỤC NON-REPEATABLE READ
-- Chạy sau khi Session A đã đọc lần 1 (trong REPEATABLE READ).
-- B sẽ BỊ CHẶN tới khi A COMMIT.

UPDATE HopDong
SET TrangThai = N'Đã kết thúc'
WHERE MaHopDong = 'HD000001';


-- DỌN DỮ LIỆU
UPDATE HopDong
SET TrangThai = N'Đang hiệu lực'
WHERE MaHopDong = 'HD000001';

-- 7.4 PHANTOM READ (BÓNG MA)
-- Chạy TRONG 10 GIÂY sau khi Session A bắt đầu khối [A1+A2] của 7.4
-- (phòng P01102 đang có 5 hợp đồng, sức chứa 6 nên INSERT hợp lệ)

-- [B1] Thêm hợp đồng mới
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
    'SV0005',
    'P01102',
    NULL,
    GETDATE(),
    DATEADD(MONTH, 6, GETDATE())
);


-- KIỂM TRA
SELECT *
FROM HopDong
WHERE MaHopDong = 'HD99999999';


-- DỌN DỮ LIỆU
DELETE FROM HopDong
WHERE MaHopDong = 'HD99999999';

-- 7.4 KHẮC PHỤC PHANTOM READ
-- Khi Session A đang SERIALIZABLE, câu INSERT này sẽ CHỜ khóa phạm vi
-- tới khi A COMMIT (A đếm 2 lần đều ra 5).

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
    'SV0005',
    'P01102',
    NULL,
    GETDATE(),
    DATEADD(MONTH, 6, GETDATE())
);


-- DỌN DỮ LIỆU
DELETE FROM HopDong
WHERE MaHopDong = 'HD99999999';

-- 7.5 DEADLOCK (BẾ TẮC)
-- Chạy NGAY LẬP TỨC (trong 5 giây) sau khi Session A bắt đầu [A1+A2] của 7.5
-- Kết quả sai: một trong hai session báo lỗi 1205

SET TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- [B1+B2] Khóa HoaDon trước, rồi cần HopDong
BEGIN TRAN;

UPDATE HoaDon
SET TienDichVu = TienDichVu + 0
WHERE MaHoaDon = 'HO000001';

WAITFOR DELAY '00:00:05';

UPDATE HopDong
SET TrangThai = N'Đang hiệu lực'
WHERE MaHopDong = 'HD000001';

COMMIT TRAN;


-- KIỂM TRA
SELECT MaHoaDon, MaHopDong, TrangThai
FROM HoaDon
WHERE MaHoaDon = 'HO000001';

SELECT MaHopDong, TrangThai
FROM HopDong
WHERE MaHopDong = 'HD000001';

-- Nếu bị chọn làm victim mà còn transaction mở thì chạy:
-- IF @@TRANCOUNT > 0 ROLLBACK TRAN;


-- DỌN DỮ LIỆU
-- Trạng thái gốc: HopDong HD000001 = 'Đang hiệu lực', HoaDon HO000001 = 'Đã thanh toán'
UPDATE HopDong
SET TrangThai = N'Đang hiệu lực'
WHERE MaHopDong = 'HD000001';

UPDATE HoaDon
SET TrangThai = N'Đã thanh toán'
WHERE MaHoaDon = 'HO000001';

-- 7.5 KHẮC PHỤC DEADLOCK
-- Cập nhật CÙNG THỨ TỰ với Session A: HopDong trước, HoaDon sau.
-- Chạy NGAY (trong 5 giây) sau khi Session A bắt đầu khối khắc phục.
-- B sẽ chờ A xong rồi mới chạy, không có lỗi 1205.
SET XACT_ABORT ON;

BEGIN TRY
    BEGIN TRAN;

    UPDATE HopDong
    SET TrangThai = N'Đang hiệu lực'
    WHERE MaHopDong = 'HD000001';

    WAITFOR DELAY '00:00:05';

    UPDATE HoaDon
    SET TrangThai = N'Chưa thanh toán'
    WHERE MaHoaDon = 'HO000001';

    COMMIT TRAN;
END TRY
BEGIN CATCH
    IF XACT_STATE() <> 0
        ROLLBACK TRAN;

    THROW;
END CATCH;

SET XACT_ABORT OFF;   -- đặt lại mặc định


-- KIỂM TRA
SELECT *
FROM HopDong
WHERE MaHopDong = 'HD000001';

SELECT *
FROM HoaDon
WHERE MaHoaDon = 'HO000001';


-- DỌN DỮ LIỆU CUỐI
UPDATE HopDong
SET TrangThai = N'Đang hiệu lực'
WHERE MaHopDong = 'HD000001';

UPDATE HoaDon
SET TrangThai = N'Đã thanh toán'
WHERE MaHoaDon = 'HO000001';