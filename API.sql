-- =========================================================
-- FD GENERIC TOOL - API DON GIAN (phien ban nhap gon)
-- Chay file nay SAU KHI da chay 01_engine.sql va API.sql.
-- Muc dich: cho phep goi POST /rpc/nhap_bai_toan voi body GON HON:
--   {
--     "attrs": "ABCDE",
--     "fds":   ["A->B", "A->C", "CD->E", "B->D", "E->A"],
--     "tests": ["CD->AC", "BD->CD", "BC->CD", "AC->BC"]
--   }
-- Va tra ve KET QUA RUT GON (chi con nhung phan chinh, de doc hon).
-- Day la OVERLOAD (ham cung ten, khac tham so) nen KHONG anh huong
-- ham nhap_bai_toan(p_attrs, p_fds, p_tuples, ...) da co san.
-- =========================================================

SET search_path TO fd_tool;

-- =========================================================
-- SETUP QUYEN: role web_anon + GRANT tren schema/bang/function
-- QUAN TRONG: moi lan chay lai init.sql (DROP SCHEMA ... CASCADE),
-- toan bo GRANT cu se bi xoa theo vi schema bi xoa va tao lai.
-- Vi vay phai chay lai doan nay (API.sql) sau MOI LAN chay init.sql.
-- =========================================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'web_anon') THEN
        CREATE ROLE web_anon NOLOGIN;
    END IF;
END $$;

GRANT USAGE ON SCHEMA fd_tool TO web_anon;
GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON ALL TABLES IN SCHEMA fd_tool TO web_anon;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA fd_tool TO web_anon;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA fd_tool TO web_anon;

-- ---------------------------------------------------------
-- Ham phu: tach 1 ve (vi du "CD" hoac "C,D") thanh mang thuoc tinh
-- Neu co dau phay -> tach theo phay. Neu khong -> tach tung ky tu.
-- ---------------------------------------------------------
CREATE OR REPLACE FUNCTION parse_attr_side(s text)
RETURNS text[] AS $$
DECLARE
    s2 text := btrim(COALESCE(s, ''));
BEGIN
    IF s2 = '' THEN
        RETURN ARRAY[]::text[];
    ELSIF position(',' IN s2) > 0 THEN
        RETURN norm_text_array(string_to_array(s2, ','));
    ELSE
        RETURN norm_text_array(ARRAY(SELECT substr(s2, i, 1) FROM generate_series(1, length(s2)) AS i));
    END IF;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ---------------------------------------------------------
-- FUNCTION nhap_bai_toan BAN DON GIAN
-- attrs: "ABCDE"  (moi ky tu la 1 thuoc tinh; hoac dung "A,B,C" neu ten dai)
-- fds  : ["A->B","CD->E",...]
-- tests: ["CD->AC",...] (cac FD muon kiem tra co thuoc F+ khong, khong bat buoc)
-- ---------------------------------------------------------
CREATE OR REPLACE FUNCTION nhap_bai_toan(
    attrs text,
    fds text[],
    tests text[] DEFAULT ARRAY[]::text[]
)
RETURNS jsonb AS $$
DECLARE
    result jsonb;
    f text;
    lhs_txt text;
    rhs_txt text;
BEGIN
    -- Khong dung RESTART IDENTITY vi web_anon khong phai owner cua cac sequence
    -- (RESTART IDENTITY yeu cau quyen ALTER SEQUENCE, se gay loi 42501 khi goi qua PostgREST).
    -- fd_id/tuple_id/test_id se tang dan qua moi lan goi, khong anh huong ket qua tinh toan.
    TRUNCATE TABLE relation_attr, fd_set, relation_tuple, fd_membership_test, decomposition
        CASCADE;

    -- 1. Thuoc tinh
    INSERT INTO relation_attr(attr_name, ordinal)
    SELECT a, ord FROM unnest(parse_attr_side(attrs)) WITH ORDINALITY AS t(a, ord);

    -- 2. Tap phu thuoc ham F, tu chuoi "A->B"
    FOREACH f IN ARRAY COALESCE(fds, ARRAY[]::text[]) LOOP
        lhs_txt := btrim(split_part(f, '->', 1));
        rhs_txt := btrim(split_part(f, '->', 2));
        INSERT INTO fd_set(lhs, rhs, note)
        VALUES (parse_attr_side(lhs_txt), parse_attr_side(rhs_txt), f);
    END LOOP;

    -- 3. Cac FD muon kiem tra thanh vien F+ (neu co)
    FOREACH f IN ARRAY COALESCE(tests, ARRAY[]::text[]) LOOP
        lhs_txt := btrim(split_part(f, '->', 1));
        rhs_txt := btrim(split_part(f, '->', 2));
        INSERT INTO fd_membership_test(lhs, rhs, note)
        VALUES (parse_attr_side(lhs_txt), parse_attr_side(rhs_txt), f);
    END LOOP;

    -- 4. Ket qua rut gon
    SELECT jsonb_build_object(
        'luoc_do', 'R(' || attrs_to_csv(all_attrs()) || ')',
        'F', (SELECT jsonb_agg(attrs_to_text(lhs) || ' -> ' || attrs_to_text(rhs) ORDER BY fd_id) FROM fd_set),
        'minimal_cover', (SELECT jsonb_agg(fd ORDER BY stt) FROM v_minimal_cover),
        'candidate_key', (SELECT jsonb_agg(tap_thuoc_tinh) FROM v_candidate_keys),
        'thuoc_tinh', (SELECT jsonb_agg(jsonb_build_object('thuoc_tinh', attr_name, 'loai', loai_thuoc_tinh)) FROM v_prime_attributes),
        'kiem_tra_thanh_vien', (
            SELECT jsonb_agg(jsonb_build_object(
                'fd', note,
                'ket_qua', CASE WHEN fd_implied(lhs, rhs) THEN 'THUOC F+' ELSE 'KHONG THUOC F+' END
            ) ORDER BY test_id)
            FROM fd_membership_test
        ),
        'chuan', jsonb_build_object(
            '2NF', (SELECT ket_qua FROM v_check_2nf),
            '3NF', (SELECT ket_qua FROM v_check_3nf),
            'BCNF', (SELECT ket_qua FROM v_check_bcnf)
        )
    ) INTO result;

    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Cap lai quyen cho web_anon vi vua tao them ham/overload moi
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA fd_tool TO web_anon;

SELECT 'Da them phien ban nhap_bai_toan(attrs, fds, tests) don gian. Goi lai POST /rpc/nhap_bai_toan voi body gon.' AS thong_bao;

-- Bao PostgREST nap lai schema cache (quan trong sau khi doi function/grant)
NOTIFY pgrst, 'reload schema';