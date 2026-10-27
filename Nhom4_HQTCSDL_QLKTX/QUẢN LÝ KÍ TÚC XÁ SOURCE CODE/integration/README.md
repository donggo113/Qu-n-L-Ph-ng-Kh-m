# Ghi chú cấu trúc dữ liệu và nghiệp vụ

Giao diện được tổ chức theo các bảng chính của cơ sở dữ liệu `QLKyTucXa`. Tên trường trên màn hình được chuẩn hóa để dễ đọc, đồng thời giữ quan hệ giữa các bảng.

## Sinh viên — `SinhVien`
`MaSV`, `HoTen`, `NgaySinh`, `GioiTinh`, `CCCD`, `SDT`, `Email`, `Lop`, `Khoa`, `DiaChiThuongTru`, `NgayNhapHoc`

## Tòa nhà — `ToaNha`
`MaToa`, `TenToa`, `SoTang`, `DiaChi`

## Phòng — `Phong`
`MaPhong`, `MaToa`, `MaLoaiPhong`, `SoPhong`, `Tang`, `GioiTinhPhong`, `TinhTrang`

Thông tin `SucChua` và `DonGia` thuộc `LoaiPhong` và được hiển thị trong phần chi tiết của phòng.

## Hợp đồng — `HopDong`
`MaHopDong`, `MaSV`, `MaPhong`, `MaNV`, `NgayBatDau`, `NgayKetThucDK`, `NgayTraThucTe`, `TrangThai`

## Dịch vụ — `DichVu`
`MaDV`, `TenDV`, `DonViTinh`, `DonGia`

## Chỉ số dịch vụ — `ChiSoDichVu`
`MaCS`, `MaPhong`, `MaDV`, `Thang`, `Nam`, `ChiSoDau`, `ChiSoCuoi`, `SoLuong`

## Hóa đơn — `HoaDon`
`MaHoaDon`, `MaHopDong`, `Thang`, `Nam`, `TienPhong`, `TienDichVu`, `TongTien`, `NgayLap`, `HanThanhToan`, `TrangThai`

Trong phần chi tiết hóa đơn có hai bảng phụ:
- `ChiTietHoaDon`: mã hóa đơn, mã dịch vụ, số lượng, đơn giá, thành tiền.
- `ThanhToan`: mã thanh toán, mã hóa đơn, ngày thanh toán, số tiền, hình thức thanh toán.

## Vi phạm — `ViPham`
`MaVP`, `MaSV`, `NgayVP`, `NoiDung`, `HinhThucXuLy`

## Nhân viên — `NhanVien`
`MaNV`, `HoTen`, `ChucVu`, `SDT`, `Email`

## Quy ước giao diện
- Các bảng chính dùng cùng kiểu tìm kiếm, nút thao tác và vùng hiển thị.
- Các bảng có nhiều trường sử dụng thanh cuộn để tránh làm giao diện quá dày.
- Bảng phụ được đặt trong cửa sổ chi tiết của đối tượng liên quan.
