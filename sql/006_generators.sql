CREATE OR REPLACE FUNCTION faker.generate_users(
    p_locale TEXT,
    p_seed TEXT,
    p_batch_index BIGINT DEFAULT 0,
    p_batch_size INTEGER DEFAULT 10
)
RETURNS TABLE (
    user_index BIGINT,
    full_name TEXT,
    address TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    height_cm DOUBLE PRECISION,
    weight_kg DOUBLE PRECISION,
    eye_color TEXT,
    hair_color TEXT,
    phone TEXT,
    email TEXT
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    i BIGINT;
    idx BIGINT;
BEGIN
    IF p_seed IS NULL OR length(btrim(p_seed)) < 1 OR length(p_seed) > 200 THEN
        RAISE EXCEPTION 'Seed must contain 1 to 200 characters';
    END IF;

    IF p_batch_index < 0 THEN
        RAISE EXCEPTION 'Batch index must be nonnegative';
    END IF;

    IF p_batch_size < 1 OR p_batch_size > 1000 THEN
        RAISE EXCEPTION 'Batch size must be between 1 and 1000';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM faker.locales WHERE locale_code = p_locale
    ) THEN
        RAISE EXCEPTION 'Locale is not configured: %', p_locale;
    END IF;

    FOR i IN 0..(p_batch_size - 1) LOOP
        idx := p_batch_index * p_batch_size + i;

        user_index := idx;
        full_name := faker.format_full_name(p_locale, p_seed, idx);
        address := faker.format_address(p_locale, p_seed, idx);
        latitude := faker.sphere_latitude(p_seed, p_locale, idx, 'latitude');
        longitude := faker.sphere_longitude(p_seed, p_locale, idx, 'longitude');
        height_cm := round(
            faker.truncated_normal(
                p_seed, p_locale, idx, 'height',
                170.0, 10.0, 140.0, 210.0
            )::NUMERIC,
            1
        );
        weight_kg := round(
            faker.truncated_normal(
                p_seed, p_locale, idx, 'weight',
                75.0, 15.0, 40.0, 150.0
            )::NUMERIC,
            1
        );
        eye_color := faker.pick_eye_color(p_locale, p_seed, idx, 'eye');
        hair_color := faker.pick_hair_color(p_locale, p_seed, idx, 'hair');
        phone := faker.format_phone(p_locale, p_seed, idx);
        email := faker.format_email(p_locale, p_seed, idx, full_name);

        RETURN NEXT;
    END LOOP;
END;
$$;

COMMENT ON FUNCTION faker.generate_users(TEXT, TEXT, BIGINT, INTEGER) IS
    'Generate a deterministic batch of fake users for a locale and seed.';

CREATE OR REPLACE PROCEDURE faker.generate_users_cursor(
    IN p_locale TEXT,
    IN p_seed TEXT,
    IN p_batch_index BIGINT,
    IN p_batch_size INTEGER,
    INOUT p_result REFCURSOR
)
LANGUAGE plpgsql
AS $$
BEGIN
    OPEN p_result FOR
        SELECT *
        FROM faker.generate_users(
            p_locale,
            p_seed,
            p_batch_index,
            p_batch_size
        );
END;
$$;

COMMENT ON PROCEDURE faker.generate_users_cursor(TEXT, TEXT, BIGINT, INTEGER, REFCURSOR) IS
    'Stored procedure wrapper that opens a cursor over faker.generate_users().';
