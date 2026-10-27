USE QLKyTucXa;
GO


SET TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- 7.1 LOST UPDATE (MẤT DỮ LIỆU CẬP NHẬT)
-- Thứ tự: A1 -> B1 -> A2 -> B2 -> KIỂM TRA
-- Kết quả sai: DonGia = 850000 (đúng phải là 900000)

-- [A1] Đọc giá phòng (chạy ĐẦU TIÊN)
DECLARE @GiaA DECIMAL(12,0);

SELECT @GiaA = DonGia
FROM LoaiPhong
WHERE MaLoaiPhong = 'LP01';

SELECT @GiaA AS Gia_Session_A;   -- 750000


-- [A2] Cập nhật tăng 50.000 (chạy SAU B1)
-- Dùng số cứng 750000 vì A1 và A2 là 2 lần chạy riêng nên biến @GiaA đã mất;
-- số cứng mô phỏng giá trị mà ứng dụng đã đọc ở A1.
UPDATE LoaiPhong
SET DonGia = 750000 + 50000
WHERE MaLoaiPhong = 'LP01';


-- KIỂM TRA (chạy sau B2)
SELECT MaLoaiPhong, DonGia
FROM LoaiPhong
WHERE MaLoaiPhong = 'LP01';


-- DỌN DỮ LIỆU 7.1
UPDATE LoaiPhong
SET DonGia = 750000
WHERE MaLoaiPhong = 'LP01';

-- 7.1 KHẮC PHỤC LOST UPDATE
-- Trước khi chạy: đảm bảo DonGia = 750000 (chạy khối DỌN DỮ LIỆU 7.1).
-- Thứ tự: chạy khối này ở A, rồi chạy NGAY khối khắc phục ở B (trong 10 giây).
-- B sẽ CHỜ ở câu SELECT cho tới khi A COMMIT.
-- Kết quả đúng: DonGia = 900000

BEGIN TRAN;

DECLARE @GiaCuA DECIMAL(12,0);

SELECT @GiaCuA = DonGia
FROM LoaiPhong WITH (UPDLOCK, HOLDLOCK)
WHERE MaLoaiPhong = 'LP01';

WAITFOR DELAY '00:00:10';   -- thời gian để sang Session B chạy

UPDATE LoaiPhong
SET DonGia = @GiaCuA + 50000
WHERE MaLoaiPhong = 'LP01';

COMMIT TRAN;


-- KIỂM TRA (sau khi cả A và B đã xong)
SELECT MaLoaiPhong, DonGia
FROM LoaiPhong
WHERE MaLoaiPhong = 'LP01';   -- 900000


-- DỌN DỮ LIỆU (sau khi cả A và B đã xong)
UPDATE LoaiPhong
SET DonGia = 750000
WHERE MaLoaiPhong = 'LP01';

-- 7.2 DIRTY READ (ĐỌC DỮ LIỆU RÁC)
-- Thứ tự: chạy [A1+A2] -> TRONG 10 GIÂY chạy B1 ở Session B
-- Kết quả sai: B đọc được 999999999 (rồi A ROLLBACK, giá trị thật là 750000)

-- [A1+A2] Sửa hóa đơn, chưa COMMIT, chờ 10 giây rồi ROLLBACK
BEGIN TRAN;

UPDATE HoaDon
SET TienPhong = 999999999
WHERE MaHoaDon = 'HO000001';

WAITFOR DELAY '00:00:10';

ROLLBACK TRAN;


-- KIỂM TRA (sau khi A xong)
SELECT MaHoaDon, TienPhong
FROM HoaDon
WHERE MaHoaDon = 'HO000001';   -- phải là 750000

-- 7.2 KHẮC PHỤC DIRTY READ
-- Thứ tự: chạy lại khối [A1+A2] ở trên, rồi TRONG 10 GIÂY chạy khối
-- khắc phục ở Session B (READ COMMITTED, không NOLOCK).
-- B sẽ CHỜ tới khi A ROLLBACK rồi đọc 750000.
-- (Phía A không cần đổi gì, việc khắc phục nằm ở Session B.)

-- DỌN DỮ LIỆU 7.2
-- A đã ROLLBACK nên dữ liệu không đổi, chỉ cần kiểm tra:
SELECT MaHoaDon, TienPhong
FROM HoaDon
WHERE MaHoaDon = 'HO000001';   -- 750000

-- 7.3 NON-REPEATABLE READ (KHÔNG ĐỌC LẠI ĐƯỢC DỮ LIỆU)
-- Thứ tự: chạy [A1+A2] -> TRONG 10 GIÂY chạy B1 ở Session B
-- Kết quả sai: Lan_1 = Đang hiệu lực, Lan_2 = Đã kết thúc

SET TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- [A1+A2]
BEGIN TRAN;

SELECT TrangThai AS Lan_1
FROM HopDong
WHERE MaHopDong = 'HD000001';

WAITFOR DELAY '00:00:10';

SELECT TrangThai AS Lan_2
FROM HopDong
WHERE MaHopDong = 'HD000001';

COMMIT TRAN;


-- KIỂM TRA
SELECT MaHopDong, TrangThai
FROM HopDong
WHERE MaHopDong = 'HD000001';


-- DỌN DỮ LIỆU 7.3 (sau khi B đã xong)
UPDATE HopDong
SET TrangThai = N'Đang hiệu lực'
WHERE MaHopDong = 'HD000001';

-- 7.3 KHẮC PHỤC NON-REPEATABLE READ
-- Trước khi chạy: HD000001 phải là 'Đang hiệu lực' (chạy DỌN DỮ LIỆU 7.3).
-- Thứ tự: chạy khối này ở A -> TRONG 10 GIÂY chạy khối khắc phục ở B.
-- B sẽ BỊ CHẶN tới khi A COMMIT.
-- Kết quả đúng: Lan_1 = Lan_2 = Đang hiệu lực

SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;

BEGIN TRAN;

SELECT TrangThai AS Lan_1
FROM HopDong
WHERE MaHopDong = 'HD000001';

WAITFOR DELAY '00:00:10';

SELECT TrangThai AS Lan_2
FROM HopDong
WHERE MaHopDong = 'HD000001';

COMMIT TRAN;

SET TRANSACTION ISOLATION LEVEL READ COMMITTED;   -- đặt lại mặc định


-- DỌN DỮ LIỆU (sau khi B đã xong)
UPDATE HopDong
SET TrangThai = N'Đang hiệu lực'
WHERE MaHopDong = 'HD000001';

-- 7.4 PHANTOM READ (BÓNG MA)
-- Thứ tự: chạy [A1+A2] -> TRONG 10 GIÂY chạy B1 ở Session B
-- Kết quả sai: Lan_1 = 5, Lan_2 = 6 (dù đang REPEATABLE READ)

-- [A1+A2]
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;

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

SET TRANSACTION ISOLATION LEVEL READ COMMITTED;   -- đặt lại mặc định


-- KIỂM TRA
SELECT *
FROM HopDong
WHERE MaHopDong = 'HD99999999';


-- DỌN DỮ LIỆU 7.4
DELETE FROM HopDong
WHERE MaHopDong = 'HD99999999';

-- 7.4 KHẮC PHỤC PHANTOM READ
-- Trước khi chạy: đảm bảo HD99999999 đã được xóa (DỌN DỮ LIỆU 7.4).
-- Thứ tự: chạy khối này ở A -> TRONG 10 GIÂY chạy INSERT khắc phục ở B.
-- B sẽ BỊ CHẶN (khóa phạm vi) tới khi A COMMIT.
-- Kết quả đúng: Lan_1 = Lan_2 = 5

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

SET TRANSACTION ISOLATION LEVEL READ COMMITTED;   -- đặt lại mặc định


-- DỌN DỮ LIỆU (sau khi B đã INSERT xong)
DELETE FROM HopDong
WHERE MaHopDong = 'HD99999999';

-- 7.5 DEADLOCK (BẾ TẮC)
-- Thứ tự: chạy [A1+A2] ở A -> NGAY LẬP TỨC (trong 5 giây) chạy [B1+B2] ở B
-- Kết quả sai: một session báo lỗi 1205 (deadlock victim)

SET TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- [A1+A2] Khóa HopDong trước, rồi cần HoaDon
BEGIN TRAN;

UPDATE HopDong
SET TrangThai = N'Đang hiệu lực'
WHERE MaHopDong = 'HD000001';

WAITFOR DELAY '00:00:05';

UPDATE HoaDon
SET TrangThai = N'Chưa thanh toán'
WHERE MaHoaDon = 'HO000001';

COMMIT TRAN;


-- KIỂM TRA
SELECT MaHopDong, TrangThai
FROM HopDong
WHERE MaHopDong = 'HD000001';

SELECT MaHoaDon, MaHopDong, TrangThai
FROM HoaDon
WHERE MaHoaDon = 'HO000001';

-- Nếu bị chọn làm victim mà còn transaction mở thì chạy:
-- IF @@TRANCOUNT > 0 ROLLBACK TRAN;


-- DỌN DỮ LIỆU 7.5
-- Trạng thái gốc: HopDong HD000001 = 'Đang hiệu lực', HoaDon HO000001 = 'Đã thanh toán'
UPDATE HopDong
SET TrangThai = N'Đang hiệu lực'
WHERE MaHopDong = 'HD000001';

UPDATE HoaDon
SET TrangThai = N'Đã thanh toán'
WHERE MaHoaDon = 'HO000001';

-- 7.5 KHẮC PHỤC DEADLOCK
-- Cả A và B cùng cập nhật theo THỨ TỰ: HopDong trước, HoaDon sau.
-- Thứ tự: chạy khối này ở A -> NGAY (trong 5 giây) chạy khối khắc phục ở B.
-- Kết quả đúng: không có lỗi 1205; B chờ A xong rồi mới chạy.

SET XACT_ABORT ON;

BEGIN TRY
    BEGIN TRAN;

    -- Luôn cập nhật HopDong trước
    UPDATE HopDong
    SET TrangThai = N'Đang hiệu lực'
    WHERE MaHopDong = 'HD000001';

    WAITFOR DELAY '00:00:05';   -- thời gian để sang Session B chạy

    -- Sau đó cập nhật HoaDon
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


-- DỌN DỮ LIỆU CUỐI (sau khi cả A và B đã xong)
UPDATE HopDong
SET TrangThai = N'Đang hiệu lực'
WHERE MaHopDong = 'HD000001';

UPDATE HoaDon
SET TrangThai = N'Đã thanh toán'
WHERE MaHoaDon = 'HO000001';