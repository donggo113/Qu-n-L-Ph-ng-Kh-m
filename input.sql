-- =========================================================
-- FD GENERIC TOOL - INPUT (chay moi lan doi bai toan)
-- Dieu kien: da chay file 01_engine.sql truoc do (it nhat 1 lan).
-- File nay: xoa du lieu bai toan cu -> nhap bai toan moi -> hien ket qua.
-- Chi can sua vung "NHAP BAI TOAN" ben duoi roi F5 toan bo file.
-- =========================================================

SET search_path TO fd_tool;

-- Xoa sach du lieu bai toan cu (khong dung DROP nen khong anh huong function/view)
TRUNCATE TABLE relation_attr, fd_set, relation_tuple, fd_membership_test, decomposition
    RESTART IDENTITY CASCADE;

-- =========================================================
-- NHAP BAI TOAN
-- Vi du mac dinh: R(A,B,C,D), F = {A->B, B->C, A->D}
-- =========================================================

-- 1. Luoc do quan he R
INSERT INTO relation_attr(attr_name, ordinal) VALUES
('A',1),
('B',2),
('C',3),
('D',4);

-- 2. Tap phu thuoc ham F
INSERT INTO fd_set(lhs, rhs, note) VALUES
(ARRAY['A'],ARRAY['B'],'A -> B'),
(ARRAY['B'],ARRAY['C'],'B -> C'),
(ARRAY['A'],ARRAY['D'],'A -> D');

-- 2b. Cac FD muon kiem tra co thuoc F+ hay khong
INSERT INTO fd_membership_test(lhs, rhs, note) VALUES
(ARRAY['A'],ARRAY['C'],'A -> C ?'),
(ARRAY['B'],ARRAY['D'],'B -> D ?');

-- 3. Du lieu demo de kiem tra co thoa F hay khong
INSERT INTO relation_tuple(vals) VALUES
('{"A":"1","B":"10","C":"100","D":"1000"}'),
('{"A":"2","B":"20","C":"200","D":"2000"}'),
('{"A":"3","B":"30","C":"300","D":"3000"}');
-- Muon test du lieu VI PHAM thi bo comment dong duoi:
-- INSERT INTO relation_tuple(vals) VALUES ('{"A":"1","B":"99","C":"999"}');

-- Quan he con de kiem tra projection, lossless join, dependency preservation
INSERT INTO decomposition(rel_name, attrs) VALUES
('R1',ARRAY['A','B']),
('R2',ARRAY['B','C']),
('R3',ARRAY['A','D']);

-- =========================================================
-- KET QUA (20 buoc) - khong can sua gi o duoi, chi doc ket qua
-- =========================================================

SELECT '01. Luoc do quan he R' AS buoc;
SELECT attrs_to_text(all_attrs()) AS R, attrs_to_csv(all_attrs()) AS danh_sach_thuoc_tinh;

SELECT '02. Tap phu thuoc ham F' AS buoc;
SELECT fd_id, attrs_to_text(lhs) || ' -> ' || attrs_to_text(rhs) AS fd, note FROM fd_set ORDER BY fd_id;

SELECT '03. Kiem tra du lieu co thoa cac FD hay khong' AS buoc;
SELECT * FROM v_fd_data_check;

SELECT '04. Tinh bao dong cua moi tap thuoc tinh' AS buoc;
SELECT tap_thuoc_tinh, bao_dong FROM v_all_closures ORDER BY cardinality(attrs), tap_thuoc_tinh;

SELECT '05. Kiem tra FD co thuoc F+ hay khong' AS buoc;
SELECT
    test_id,
    attrs_to_text(lhs) || ' -> ' || attrs_to_text(rhs) AS fd_can_kiem_tra,
    attrs_to_text(fd_closure(lhs)) AS lhs_closure,
    CASE WHEN fd_implied(lhs, rhs) THEN 'THUOC F+' ELSE 'KHONG THUOC F+' END AS ket_qua,
    note
FROM fd_membership_test
ORDER BY test_id;

SELECT '06. Super Key' AS buoc;
SELECT tap_thuoc_tinh, bao_dong, giai_thich FROM v_super_keys;

SELECT '07. Candidate Key' AS buoc;
SELECT tap_thuoc_tinh, bao_dong, giai_thich FROM v_candidate_keys;

SELECT '08. Prime Attribute va Non-prime Attribute' AS buoc;
SELECT * FROM v_prime_attributes;

SELECT '09. Minimal Cover' AS buoc;
SELECT stt, fd FROM v_minimal_cover;

SELECT '10. Tap FD chieu tren tung quan he con' AS buoc;
SELECT rel_name, relation_attrs, projected_fd FROM v_projected_fds;

SELECT '11. Kiem tra 1NF' AS buoc;
SELECT * FROM v_check_1nf;

SELECT '12. Kiem tra 2NF' AS buoc;
SELECT * FROM v_check_2nf;

SELECT '13. Kiem tra 3NF' AS buoc;
SELECT * FROM v_check_3nf;

SELECT '14. Kiem tra BCNF' AS buoc;
SELECT * FROM v_check_bcnf;

SELECT '15. Phan ra quan he sang 3NF' AS buoc;
SELECT rel_name, relation_scheme, giai_thich FROM v_decompose_3nf;

SELECT '16. Phan ra quan he sang BCNF' AS buoc;
SELECT rel_name, relation_scheme, giai_thich FROM v_decompose_bcnf;

SELECT '17. Tableau' AS buoc;
SELECT * FROM v_tableau;

SELECT '18. Kiem tra Lossless Join' AS buoc;
SELECT * FROM v_check_lossless_join;

SELECT '19. Kiem tra Dependency Preservation' AS buoc;
SELECT * FROM v_check_dependency_preservation;
SELECT * FROM v_dependency_preservation_detail;

SELECT '20. Hoan tat' AS buoc;
SELECT 'Da nhap bai toan moi va tinh xong ket qua.' AS thong_bao;
