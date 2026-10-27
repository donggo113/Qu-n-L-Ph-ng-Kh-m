-- =========================================================
-- FD GENERIC TOOL - ENGINE (chay 1 lan duy nhat)
-- File nay CHI chua: schema, cau truc bang rong, function, view.
-- KHONG chua du lieu bai toan.
-- Sau khi chay file nay xong, moi lan doi bai toan chi can chay
-- file 02_input.sql (khong can chay lai file nay).
-- Neu ban sua/them thuat toan (function/view) thi chay lai file nay.
-- =========================================================

DROP SCHEMA IF EXISTS fd_tool CASCADE;
CREATE SCHEMA fd_tool;
SET search_path TO fd_tool;

-- =========================================================
-- CAU TRUC BANG (RONG - chua nhap du lieu o day)
-- =========================================================

CREATE TABLE relation_attr (
    attr_name text PRIMARY KEY,
    ordinal int NOT NULL
);

CREATE TABLE fd_set (
    fd_id serial PRIMARY KEY,
    lhs text[] NOT NULL,
    rhs text[] NOT NULL,
    note text
);

CREATE TABLE relation_tuple (
    tuple_id serial PRIMARY KEY,
    vals jsonb NOT NULL
);

CREATE TABLE fd_membership_test (
    test_id serial PRIMARY KEY,
    lhs text[] NOT NULL,
    rhs text[] NOT NULL,
    note text
);

CREATE TABLE decomposition (
    rel_name text PRIMARY KEY,
    attrs text[] NOT NULL
);

-- =========================================================
-- HAM TIEN ICH TAP THUOC TINH
-- =========================================================

CREATE OR REPLACE FUNCTION norm_text_array(items text[])
RETURNS text[] AS $$
    SELECT COALESCE(array_agg(DISTINCT btrim(item) ORDER BY btrim(item)), ARRAY[]::text[])
    FROM unnest(COALESCE(items, ARRAY[]::text[])) AS item
    WHERE item IS NOT NULL AND btrim(item) <> '';
$$ LANGUAGE sql IMMUTABLE;

CREATE OR REPLACE FUNCTION attrs_to_text(attrs text[])
RETURNS text AS $$
    SELECT COALESCE(string_agg(attr, '' ORDER BY attr), '')
    FROM unnest(norm_text_array(attrs)) AS attr;
$$ LANGUAGE sql IMMUTABLE;

CREATE OR REPLACE FUNCTION attrs_to_csv(attrs text[])
RETURNS text AS $$
    SELECT COALESCE(string_agg(attr, ', ' ORDER BY attr), '')
    FROM unnest(norm_text_array(attrs)) AS attr;
$$ LANGUAGE sql IMMUTABLE;

CREATE OR REPLACE FUNCTION array_contains_all(container text[], needed text[])
RETURNS boolean AS $$
    SELECT NOT EXISTS (
        SELECT 1
        FROM unnest(norm_text_array(needed)) AS n
        WHERE NOT n = ANY(norm_text_array(container))
    );
$$ LANGUAGE sql IMMUTABLE;

CREATE OR REPLACE FUNCTION array_equal_set(a text[], b text[])
RETURNS boolean AS $$
    SELECT array_contains_all(a, b) AND array_contains_all(b, a);
$$ LANGUAGE sql IMMUTABLE;

CREATE OR REPLACE FUNCTION array_union_set(a text[], b text[])
RETURNS text[] AS $$
    SELECT norm_text_array(COALESCE(a, ARRAY[]::text[]) || COALESCE(b, ARRAY[]::text[]));
$$ LANGUAGE sql IMMUTABLE;

CREATE OR REPLACE FUNCTION array_intersect_set(a text[], b text[])
RETURNS text[] AS $$
    SELECT COALESCE(array_agg(x ORDER BY x), ARRAY[]::text[])
    FROM (
        SELECT DISTINCT x
        FROM unnest(norm_text_array(a)) AS x
        WHERE x = ANY(norm_text_array(b))
    ) s;
$$ LANGUAGE sql IMMUTABLE;

CREATE OR REPLACE FUNCTION array_diff_set(a text[], b text[])
RETURNS text[] AS $$
    SELECT COALESCE(array_agg(x ORDER BY x), ARRAY[]::text[])
    FROM (
        SELECT DISTINCT x
        FROM unnest(norm_text_array(a)) AS x
        WHERE NOT x = ANY(norm_text_array(b))
    ) s;
$$ LANGUAGE sql IMMUTABLE;

CREATE OR REPLACE FUNCTION all_attrs()
RETURNS text[] AS $$
    SELECT COALESCE(array_agg(attr_name ORDER BY ordinal), ARRAY[]::text[])
    FROM relation_attr;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION all_subsets(input_attrs text[], include_empty boolean DEFAULT false)
RETURNS TABLE(attrs text[]) AS $$
DECLARE
    a text[] := norm_text_array(input_attrs);
    n int := COALESCE(array_length(norm_text_array(input_attrs), 1), 0);
    mask int;
    max_mask int;
    i int;
    subset text[];
    start_mask int;
BEGIN
    IF n = 0 THEN
        IF include_empty THEN
            attrs := ARRAY[]::text[];
            RETURN NEXT;
        END IF;
        RETURN;
    END IF;

    IF n > 30 THEN
        RAISE EXCEPTION 'Qua nhieu thuoc tinh (%). Tool demo chi ho tro toi da 30 thuoc tinh de tranh 2^n qua lon.', n;
    END IF;

    max_mask := (1 << n) - 1;
    start_mask := CASE WHEN include_empty THEN 0 ELSE 1 END;

    FOR mask IN start_mask..max_mask LOOP
        subset := ARRAY[]::text[];
        FOR i IN 1..n LOOP
            IF ((mask >> (i - 1)) & 1) = 1 THEN
                subset := subset || a[i];
            END IF;
        END LOOP;

        attrs := norm_text_array(subset);
        RETURN NEXT;
    END LOOP;
END;
$$ LANGUAGE plpgsql STABLE;

-- =========================================================
-- 4. TINH BAO DONG X+
-- =========================================================

CREATE OR REPLACE FUNCTION fd_closure(start_attrs text[], custom_fds jsonb DEFAULT NULL)
RETURNS text[] AS $$
DECLARE
    closure_attrs text[] := norm_text_array(start_attrs);
    old_attrs text[] := ARRAY[]::text[];
    fd record;
BEGIN
    WHILE closure_attrs IS DISTINCT FROM old_attrs LOOP
        old_attrs := closure_attrs;

        IF custom_fds IS NULL THEN
            FOR fd IN SELECT lhs, rhs FROM fd_set LOOP
                IF array_contains_all(closure_attrs, fd.lhs) THEN
                    closure_attrs := array_union_set(closure_attrs, fd.rhs);
                END IF;
            END LOOP;
        ELSE
            FOR fd IN
                SELECT
                    ARRAY(SELECT jsonb_array_elements_text(item->'lhs')) AS lhs,
                    ARRAY(SELECT jsonb_array_elements_text(item->'rhs')) AS rhs
                FROM jsonb_array_elements(custom_fds) AS e(item)
            LOOP
                IF array_contains_all(closure_attrs, fd.lhs) THEN
                    closure_attrs := array_union_set(closure_attrs, fd.rhs);
                END IF;
            END LOOP;
        END IF;
    END LOOP;

    RETURN closure_attrs;
END;
$$ LANGUAGE plpgsql STABLE;

-- 5. Kiem tra X -> Y co thuoc F+ hay khong
CREATE OR REPLACE FUNCTION fd_implied(lhs_attrs text[], rhs_attrs text[])
RETURNS boolean AS $$
    SELECT array_contains_all(fd_closure(lhs_attrs), rhs_attrs);
$$ LANGUAGE sql STABLE;

-- =========================================================
-- 3. KIEM TRA DU LIEU CO THOA CAC FD HAY KHONG
-- =========================================================

CREATE OR REPLACE VIEW v_fd_data_check AS
SELECT
    f.fd_id,
    attrs_to_text(f.lhs) || ' -> ' || attrs_to_text(f.rhs) AS fd,
    CASE
        WHEN EXISTS (
            SELECT 1
            FROM relation_tuple t1
            JOIN relation_tuple t2 ON t1.tuple_id < t2.tuple_id
            WHERE NOT EXISTS (
                SELECT 1
                FROM unnest(f.lhs) AS a
                WHERE (t1.vals ->> a) IS DISTINCT FROM (t2.vals ->> a)
            )
            AND EXISTS (
                SELECT 1
                FROM unnest(f.rhs) AS b
                WHERE (t1.vals ->> b) IS DISTINCT FROM (t2.vals ->> b)
            )
        )
        THEN 'VI PHAM'
        ELSE 'THOA'
    END AS ket_qua,
    (
        SELECT 'tuple ' || t1.tuple_id || ' va tuple ' || t2.tuple_id
        FROM relation_tuple t1
        JOIN relation_tuple t2 ON t1.tuple_id < t2.tuple_id
        WHERE NOT EXISTS (
            SELECT 1
            FROM unnest(f.lhs) AS a
            WHERE (t1.vals ->> a) IS DISTINCT FROM (t2.vals ->> a)
        )
        AND EXISTS (
            SELECT 1
            FROM unnest(f.rhs) AS b
            WHERE (t1.vals ->> b) IS DISTINCT FROM (t2.vals ->> b)
        )
        LIMIT 1
    ) AS cap_tuple_vi_pham
FROM fd_set f
ORDER BY f.fd_id;

-- =========================================================
-- 6,7. SUPER KEY VA CANDIDATE KEY
-- =========================================================

CREATE OR REPLACE VIEW v_all_closures AS
SELECT
    attrs_to_text(s.attrs) AS tap_thuoc_tinh,
    s.attrs,
    fd_closure(s.attrs) AS closure_attrs,
    attrs_to_text(fd_closure(s.attrs)) AS bao_dong
FROM all_subsets(all_attrs(), true) s
ORDER BY cardinality(s.attrs), attrs_to_text(s.attrs);

CREATE OR REPLACE VIEW v_super_keys AS
SELECT
    tap_thuoc_tinh,
    attrs,
    bao_dong,
    'Super Key vi ' || tap_thuoc_tinh || '+ = ' || bao_dong || ' chua toan bo R' AS giai_thich
FROM v_all_closures
WHERE array_contains_all(closure_attrs, all_attrs())
  AND cardinality(attrs) > 0
ORDER BY cardinality(attrs), tap_thuoc_tinh;

CREATE OR REPLACE VIEW v_candidate_keys AS
SELECT sk.*
FROM v_super_keys sk
WHERE NOT EXISTS (
    SELECT 1
    FROM v_super_keys smaller
    WHERE cardinality(smaller.attrs) < cardinality(sk.attrs)
      AND array_contains_all(sk.attrs, smaller.attrs)
)
ORDER BY cardinality(attrs), tap_thuoc_tinh;

-- =========================================================
-- 8. PRIME ATTRIBUTE VA NON-PRIME ATTRIBUTE
-- =========================================================

CREATE OR REPLACE VIEW v_prime_attributes AS
WITH prime AS (
    SELECT DISTINCT a
    FROM v_candidate_keys ck
    CROSS JOIN unnest(ck.attrs) AS a
)
SELECT
    r.attr_name,
    CASE WHEN p.a IS NOT NULL THEN 'Prime Attribute' ELSE 'Non-prime Attribute' END AS loai_thuoc_tinh,
    CASE WHEN p.a IS NOT NULL
         THEN 'Nam trong it nhat mot Candidate Key'
         ELSE 'Khong nam trong bat ky Candidate Key nao'
    END AS giai_thich
FROM relation_attr r
LEFT JOIN prime p ON p.a = r.attr_name
ORDER BY r.ordinal;

-- =========================================================
-- 9. MINIMAL COVER
-- =========================================================

CREATE OR REPLACE FUNCTION fds_json_from_table()
RETURNS jsonb AS $$
    SELECT COALESCE(jsonb_agg(jsonb_build_object('lhs', lhs, 'rhs', rhs)), '[]'::jsonb)
    FROM fd_set;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION fds_json_to_text(fds jsonb)
RETURNS text AS $$
    SELECT COALESCE(string_agg(attrs_to_text(lhs) || ' -> ' || attrs_to_text(rhs), '; ' ORDER BY attrs_to_text(lhs), attrs_to_text(rhs)), '')
    FROM (
        SELECT
            ARRAY(SELECT jsonb_array_elements_text(item->'lhs')) AS lhs,
            ARRAY(SELECT jsonb_array_elements_text(item->'rhs')) AS rhs
        FROM jsonb_array_elements(fds) AS e(item)
    ) s;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION closure_with_fds(start_attrs text[], fds jsonb)
RETURNS text[] AS $$
    SELECT fd_closure(start_attrs, fds);
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION remove_fd_at(fds jsonb, remove_idx int)
RETURNS jsonb AS $$
    SELECT COALESCE(jsonb_agg(item ORDER BY idx), '[]'::jsonb)
    FROM jsonb_array_elements(fds) WITH ORDINALITY AS e(item, idx)
    WHERE idx <> remove_idx;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION replace_fd_lhs_at(fds jsonb, replace_idx int, new_lhs text[])
RETURNS jsonb AS $$
    SELECT COALESCE(jsonb_agg(
        CASE WHEN idx = replace_idx
             THEN jsonb_set(item, '{lhs}', to_jsonb(norm_text_array(new_lhs)))
             ELSE item
        END
        ORDER BY idx
    ), '[]'::jsonb)
    FROM jsonb_array_elements(fds) WITH ORDINALITY AS e(item, idx);
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION minimal_cover_json()
RETURNS jsonb AS $$
DECLARE
    fds jsonb := '[]'::jsonb;
    item jsonb;
    lhs text[];
    rhs text[];
    idx int;
    changed boolean;
    test_fds jsonb;
    a text;
    reduced_lhs text[];
BEGIN
    FOR item IN SELECT jsonb_build_object('lhs', fs.lhs, 'rhs', ARRAY[u.r_attr])
                FROM fd_set fs
                CROSS JOIN unnest(fs.rhs) AS u(r_attr) LOOP
        fds := fds || jsonb_build_array(item);
    END LOOP;

    changed := true;
    WHILE changed LOOP
        changed := false;
        idx := 1;
        FOR item IN SELECT value FROM jsonb_array_elements(fds) AS e(value) LOOP
            lhs := ARRAY(SELECT jsonb_array_elements_text(item->'lhs'));
            rhs := ARRAY(SELECT jsonb_array_elements_text(item->'rhs'));

            IF cardinality(lhs) > 1 THEN
                FOREACH a IN ARRAY lhs LOOP
                    reduced_lhs := array_diff_set(lhs, ARRAY[a]);
                    IF array_contains_all(closure_with_fds(reduced_lhs, fds), rhs) THEN
                        fds := replace_fd_lhs_at(fds, idx, reduced_lhs);
                        changed := true;
                        EXIT;
                    END IF;
                END LOOP;
            END IF;

            EXIT WHEN changed;
            idx := idx + 1;
        END LOOP;
    END LOOP;

    changed := true;
    WHILE changed LOOP
        changed := false;
        idx := 1;
        FOR item IN SELECT value FROM jsonb_array_elements(fds) AS e(value) LOOP
            lhs := ARRAY(SELECT jsonb_array_elements_text(item->'lhs'));
            rhs := ARRAY(SELECT jsonb_array_elements_text(item->'rhs'));
            test_fds := remove_fd_at(fds, idx);

            IF array_contains_all(closure_with_fds(lhs, test_fds), rhs) THEN
                fds := test_fds;
                changed := true;
                EXIT;
            END IF;

            idx := idx + 1;
        END LOOP;
    END LOOP;

    RETURN fds;
END;
$$ LANGUAGE plpgsql STABLE;

CREATE OR REPLACE VIEW v_minimal_cover AS
SELECT
    row_number() OVER () AS stt,
    attrs_to_text(ARRAY(SELECT jsonb_array_elements_text(item->'lhs'))) AS lhs,
    attrs_to_text(ARRAY(SELECT jsonb_array_elements_text(item->'rhs'))) AS rhs,
    attrs_to_text(ARRAY(SELECT jsonb_array_elements_text(item->'lhs'))) || ' -> ' ||
    attrs_to_text(ARRAY(SELECT jsonb_array_elements_text(item->'rhs'))) AS fd
FROM jsonb_array_elements(minimal_cover_json()) AS e(item);

-- =========================================================
-- 10. FD CHIEU TREN TUNG QUAN HE CON
-- =========================================================

CREATE OR REPLACE VIEW v_projected_fds AS
SELECT
    d.rel_name,
    attrs_to_text(d.attrs) AS relation_attrs,
    attrs_to_text(x.attrs) AS lhs,
    attrs_to_text(array_diff_set(array_intersect_set(fd_closure(x.attrs), d.attrs), x.attrs)) AS rhs,
    attrs_to_text(x.attrs) || ' -> ' ||
    attrs_to_text(array_diff_set(array_intersect_set(fd_closure(x.attrs), d.attrs), x.attrs)) AS projected_fd
FROM decomposition d
CROSS JOIN LATERAL all_subsets(d.attrs, false) x
WHERE cardinality(array_diff_set(array_intersect_set(fd_closure(x.attrs), d.attrs), x.attrs)) > 0
ORDER BY d.rel_name, cardinality(x.attrs), lhs, rhs;

-- =========================================================
-- 11. KIEM TRA 1NF
-- =========================================================

CREATE OR REPLACE VIEW v_check_1nf AS
SELECT
    CASE
        WHEN EXISTS (
            SELECT 1
            FROM relation_tuple t
            CROSS JOIN relation_attr a
            WHERE jsonb_typeof(t.vals -> a.attr_name) IN ('array', 'object')
        )
        THEN 'KHONG DAT 1NF'
        ELSE 'DAT 1NF'
    END AS ket_qua,
    CASE
        WHEN EXISTS (
            SELECT 1
            FROM relation_tuple t
            CROSS JOIN relation_attr a
            WHERE jsonb_typeof(t.vals -> a.attr_name) IN ('array', 'object')
        )
        THEN 'Co gia tri dang array/object, khong phai atomic.'
        ELSE 'Tat ca gia tri demo la atomic.'
    END AS giai_thich;

-- =========================================================
-- 12,13,14. KIEM TRA 2NF, 3NF, BCNF
-- =========================================================

CREATE OR REPLACE VIEW v_normal_form_fd_analysis AS
WITH mc AS (
    SELECT
        ARRAY(SELECT jsonb_array_elements_text(item->'lhs')) AS lhs,
        ARRAY(SELECT jsonb_array_elements_text(item->'rhs')) AS rhs
    FROM jsonb_array_elements(minimal_cover_json()) AS e(item)
),
prime AS (
    SELECT array_agg(attr_name ORDER BY attr_name) AS attrs
    FROM v_prime_attributes
    WHERE loai_thuoc_tinh = 'Prime Attribute'
),
keys AS (
    SELECT array_agg(attrs_to_text(attrs) ORDER BY cardinality(attrs), attrs_to_text(attrs)) AS keys_text
    FROM v_candidate_keys
)
SELECT
    attrs_to_text(mc.lhs) || ' -> ' || attrs_to_text(mc.rhs) AS fd,
    attrs_to_text(mc.lhs) AS lhs,
    attrs_to_text(mc.rhs) AS rhs,
    array_contains_all(fd_closure(mc.lhs), all_attrs()) AS lhs_is_super_key,
    array_contains_all((SELECT attrs FROM prime), mc.rhs) AS rhs_is_prime,
    EXISTS (
        SELECT 1
        FROM v_candidate_keys ck
        WHERE array_contains_all(ck.attrs, mc.lhs)
          AND NOT array_equal_set(ck.attrs, mc.lhs)
          AND NOT array_contains_all((SELECT attrs FROM prime), mc.rhs)
    ) AS violates_2nf,
    (
        NOT array_contains_all(fd_closure(mc.lhs), all_attrs())
        AND NOT array_contains_all((SELECT attrs FROM prime), mc.rhs)
    ) AS violates_3nf,
    (
        NOT array_contains_all(fd_closure(mc.lhs), all_attrs())
    ) AS violates_bcnf
FROM mc
WHERE NOT array_contains_all(mc.lhs, mc.rhs);

CREATE OR REPLACE VIEW v_check_2nf AS
SELECT
    CASE WHEN EXISTS (SELECT 1 FROM v_normal_form_fd_analysis WHERE violates_2nf)
         THEN 'KHONG DAT 2NF'
         ELSE 'DAT 2NF'
    END AS ket_qua,
    COALESCE((
        SELECT string_agg(fd, '; ')
        FROM v_normal_form_fd_analysis
        WHERE violates_2nf
    ), 'Khong co non-prime attribute phu thuoc bo phan vao khoa.') AS giai_thich;

CREATE OR REPLACE VIEW v_check_3nf AS
SELECT
    CASE WHEN EXISTS (SELECT 1 FROM v_normal_form_fd_analysis WHERE violates_3nf)
         THEN 'KHONG DAT 3NF'
         ELSE 'DAT 3NF'
    END AS ket_qua,
    COALESCE((
        SELECT string_agg(fd, '; ')
        FROM v_normal_form_fd_analysis
        WHERE violates_3nf
    ), 'Moi FD khong tam thuong deu co LHS la super key hoac RHS la prime attribute.') AS giai_thich;

CREATE OR REPLACE VIEW v_check_bcnf AS
SELECT
    CASE WHEN EXISTS (SELECT 1 FROM v_normal_form_fd_analysis WHERE violates_bcnf)
         THEN 'KHONG DAT BCNF'
         ELSE 'DAT BCNF'
    END AS ket_qua,
    COALESCE((
        SELECT string_agg(fd, '; ')
        FROM v_normal_form_fd_analysis
        WHERE violates_bcnf
    ), 'Moi FD khong tam thuong deu co LHS la super key.') AS giai_thich;

-- =========================================================
-- 15. PHAN RA SANG 3NF
-- =========================================================

CREATE OR REPLACE VIEW v_decompose_3nf_raw AS
SELECT
    'S' || row_number() OVER () AS rel_name,
    array_union_set(
        ARRAY(SELECT jsonb_array_elements_text(item->'lhs')),
        ARRAY(SELECT jsonb_array_elements_text(item->'rhs'))
    ) AS attrs
FROM jsonb_array_elements(minimal_cover_json()) AS e(item);

CREATE OR REPLACE VIEW v_decompose_3nf AS
WITH raw AS (
    SELECT * FROM v_decompose_3nf_raw
),
not_subset AS (
    SELECT r.*
    FROM raw r
    WHERE NOT EXISTS (
        SELECT 1
        FROM raw other
        WHERE other.rel_name <> r.rel_name
          AND array_contains_all(other.attrs, r.attrs)
          AND NOT array_equal_set(other.attrs, r.attrs)
    )
),
has_key AS (
    SELECT EXISTS (
        SELECT 1
        FROM not_subset ns
        JOIN v_candidate_keys ck ON array_contains_all(ns.attrs, ck.attrs)
    ) AS ok
),
with_key AS (
    SELECT rel_name, attrs FROM not_subset
    UNION ALL
    SELECT 'S_key', (SELECT attrs FROM v_candidate_keys ORDER BY cardinality(attrs), tap_thuoc_tinh LIMIT 1)
    WHERE NOT (SELECT ok FROM has_key)
)
SELECT
    rel_name,
    attrs_to_text(attrs) AS relation_scheme,
    attrs,
    'Quan he trong ket qua phan ra 3NF' AS giai_thich
FROM with_key
ORDER BY rel_name;

-- =========================================================
-- 16. PHAN RA SANG BCNF
-- =========================================================

CREATE OR REPLACE FUNCTION projected_fds_json_for_attrs(r_attrs text[])
RETURNS jsonb AS $$
    SELECT COALESCE(jsonb_agg(jsonb_build_object('lhs', x.attrs, 'rhs', array_diff_set(array_intersect_set(fd_closure(x.attrs), r_attrs), x.attrs))), '[]'::jsonb)
    FROM all_subsets(r_attrs, false) x
    WHERE cardinality(array_diff_set(array_intersect_set(fd_closure(x.attrs), r_attrs), x.attrs)) > 0;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION bcnf_decompose_json(r_attrs text[], depth int DEFAULT 0)
RETURNS jsonb AS $$
DECLARE
    fd record;
    xplus text[];
    r1 text[];
    r2 text[];
    result jsonb;
BEGIN
    IF depth > 20 THEN
        RETURN jsonb_build_array(jsonb_build_object('attrs', norm_text_array(r_attrs), 'note', 'Dung do qua gioi han de quy'));
    END IF;

    FOR fd IN
        SELECT
            ARRAY(SELECT jsonb_array_elements_text(item->'lhs')) AS lhs,
            ARRAY(SELECT jsonb_array_elements_text(item->'rhs')) AS rhs
        FROM jsonb_array_elements(projected_fds_json_for_attrs(r_attrs)) AS e(item)
    LOOP
        IF NOT array_contains_all(fd.lhs, fd.rhs)
           AND NOT array_contains_all(array_intersect_set(fd_closure(fd.lhs), r_attrs), r_attrs) THEN
            xplus := array_intersect_set(fd_closure(fd.lhs), r_attrs);
            r1 := xplus;
            r2 := array_union_set(fd.lhs, array_diff_set(r_attrs, xplus));

            result := bcnf_decompose_json(r1, depth + 1) || bcnf_decompose_json(r2, depth + 1);
            RETURN result;
        END IF;
    END LOOP;

    RETURN jsonb_build_array(jsonb_build_object('attrs', norm_text_array(r_attrs), 'note', 'BCNF'));
END;
$$ LANGUAGE plpgsql STABLE;

CREATE OR REPLACE VIEW v_decompose_bcnf AS
SELECT
    'B' || row_number() OVER () AS rel_name,
    attrs_to_text(ARRAY(SELECT jsonb_array_elements_text(item->'attrs'))) AS relation_scheme,
    ARRAY(SELECT jsonb_array_elements_text(item->'attrs')) AS attrs,
    item->>'note' AS giai_thich
FROM jsonb_array_elements(bcnf_decompose_json(all_attrs())) AS e(item);

-- =========================================================
-- 17. TAO TABLEAU CHO PHAN RA HIEN TAI
-- =========================================================

CREATE OR REPLACE VIEW v_tableau AS
SELECT
    d.rel_name,
    a.attr_name,
    CASE WHEN a.attr_name = ANY(d.attrs)
         THEN 'a_' || a.attr_name
         ELSE 'b_' || d.rel_name || '_' || a.attr_name
    END AS symbol
FROM decomposition d
CROSS JOIN relation_attr a
ORDER BY d.rel_name, a.ordinal;

-- =========================================================
-- 18. KIEM TRA LOSSLESS JOIN
-- =========================================================

CREATE OR REPLACE FUNCTION chase_lossless_join()
RETURNS TABLE(ket_qua text, giai_thich text) AS $$
DECLARE
    changed boolean;
    fd record;
    pair record;
    rhs_attr text;
    s1 text;
    s2 text;
    new_symbol text;
    has_full_a_row boolean;
BEGIN
    DROP TABLE IF EXISTS tmp_chase_tableau;

    CREATE TEMP TABLE tmp_chase_tableau (
        row_no int,
        rel_name text,
        attr_name text,
        symbol text
    ) ON COMMIT DROP;

    INSERT INTO tmp_chase_tableau(row_no, rel_name, attr_name, symbol)
    SELECT
        dense_rank() OVER (ORDER BY d.rel_name) AS row_no,
        d.rel_name,
        a.attr_name,
        CASE WHEN a.attr_name = ANY(d.attrs)
             THEN 'a_' || a.attr_name
             ELSE 'b_' || d.rel_name || '_' || a.attr_name
        END AS symbol
    FROM decomposition d
    CROSS JOIN relation_attr a;

    LOOP
        changed := false;

        FOR fd IN SELECT lhs, rhs FROM fd_set LOOP
            FOR pair IN
                SELECT DISTINCT x.row_no AS r1, y.row_no AS r2
                FROM tmp_chase_tableau x
                JOIN tmp_chase_tableau y ON x.row_no < y.row_no
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM unnest(fd.lhs) AS a
                    JOIN tmp_chase_tableau sx ON sx.row_no = x.row_no AND sx.attr_name = a
                    JOIN tmp_chase_tableau sy ON sy.row_no = y.row_no AND sy.attr_name = a
                    WHERE sx.symbol IS DISTINCT FROM sy.symbol
                )
            LOOP
                FOREACH rhs_attr IN ARRAY fd.rhs LOOP
                    SELECT symbol INTO s1
                    FROM tmp_chase_tableau
                    WHERE row_no = pair.r1 AND attr_name = rhs_attr;

                    SELECT symbol INTO s2
                    FROM tmp_chase_tableau
                    WHERE row_no = pair.r2 AND attr_name = rhs_attr;

                    IF s1 IS DISTINCT FROM s2 THEN
                        IF s1 = 'a_' || rhs_attr OR s2 = 'a_' || rhs_attr THEN
                            new_symbol := 'a_' || rhs_attr;
                        ELSE
                            new_symbol := LEAST(s1, s2);
                        END IF;

                        UPDATE tmp_chase_tableau
                        SET symbol = new_symbol
                        WHERE attr_name = rhs_attr
                          AND row_no IN (pair.r1, pair.r2);

                        changed := true;
                    END IF;
                END LOOP;
            END LOOP;
        END LOOP;

        EXIT WHEN NOT changed;
    END LOOP;

    SELECT EXISTS (
        SELECT 1
        FROM tmp_chase_tableau t
        GROUP BY t.row_no
        HAVING bool_and(t.symbol = 'a_' || t.attr_name)
    )
    INTO has_full_a_row;

    IF has_full_a_row THEN
        RETURN QUERY SELECT
            'LOSSLESS JOIN',
            'Sau chase tableau, co it nhat mot dong tro thanh toan bo ky hieu a_A. Phan ra bao toan thong tin.';
    ELSE
        RETURN QUERY SELECT
            'LOSSY JOIN',
            'Sau chase tableau, khong co dong nao tro thanh toan bo ky hieu a_A. Phan ra co nguy co mat/du thong tin khi join.';
    END IF;
END;
$$ LANGUAGE plpgsql VOLATILE;

CREATE OR REPLACE VIEW v_check_lossless_join AS
SELECT * FROM chase_lossless_join();

-- =========================================================
-- 19. KIEM TRA DEPENDENCY PRESERVATION
-- =========================================================

CREATE OR REPLACE FUNCTION projected_union_json()
RETURNS jsonb AS $$
    SELECT COALESCE(jsonb_agg(jsonb_build_object('lhs', lhs_arr, 'rhs', rhs_arr)), '[]'::jsonb)
    FROM (
        SELECT
            x.attrs AS lhs_arr,
            array_diff_set(array_intersect_set(fd_closure(x.attrs), d.attrs), x.attrs) AS rhs_arr
        FROM decomposition d
        CROSS JOIN LATERAL all_subsets(d.attrs, false) x
        WHERE cardinality(array_diff_set(array_intersect_set(fd_closure(x.attrs), d.attrs), x.attrs)) > 0
    ) s;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE VIEW v_dependency_preservation_detail AS
SELECT
    f.fd_id,
    attrs_to_text(f.lhs) || ' -> ' || attrs_to_text(f.rhs) AS fd_goc,
    attrs_to_text(closure_with_fds(f.lhs, projected_union_json())) AS closure_theo_projected_fd,
    CASE WHEN array_contains_all(closure_with_fds(f.lhs, projected_union_json()), f.rhs)
         THEN 'BAO TOAN'
         ELSE 'KHONG BAO TOAN'
    END AS ket_qua
FROM fd_set f
ORDER BY f.fd_id;

CREATE OR REPLACE VIEW v_check_dependency_preservation AS
SELECT
    CASE WHEN EXISTS (SELECT 1 FROM v_dependency_preservation_detail WHERE ket_qua = 'KHONG BAO TOAN')
         THEN 'KHONG BAO TOAN PHU THUOC HAM'
         ELSE 'BAO TOAN PHU THUOC HAM'
    END AS ket_qua,
    COALESCE((
        SELECT string_agg(fd_goc, '; ')
        FROM v_dependency_preservation_detail
        WHERE ket_qua = 'KHONG BAO TOAN'
    ), 'Tat ca FD goc deu suy dien duoc tu hop cac FD chieu.') AS giai_thich;

-- =========================================================
-- Da tao xong toan bo dong co (function + view).
-- Buoc tiep theo: chay file 02_input.sql de nhap bai toan va xem ket qua.
-- =========================================================
SELECT 'Engine da san sang. Hay chay file 02_input.sql.' AS thong_bao;
