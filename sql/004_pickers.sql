CREATE OR REPLACE FUNCTION faker.lookup_count(
    p_locale TEXT,
    p_kind TEXT,
    p_subtype TEXT DEFAULT NULL
)
RETURNS BIGINT
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_count BIGINT;
BEGIN
    IF p_kind = 'name' THEN
        SELECT count(*) INTO v_count
        FROM faker.names
        WHERE locale_code = p_locale AND name_type = p_subtype;
    ELSIF p_kind = 'title' THEN
        SELECT count(*) INTO v_count
        FROM faker.titles
        WHERE locale_code = p_locale;
    ELSIF p_kind = 'address' THEN
        SELECT count(*) INTO v_count
        FROM faker.address_parts
        WHERE locale_code = p_locale AND part_type = p_subtype;
    ELSIF p_kind = 'region' THEN
        SELECT count(*) INTO v_count
        FROM faker.regions
        WHERE locale_code = p_locale;
    ELSIF p_kind = 'eye' THEN
        SELECT count(*) INTO v_count
        FROM faker.eye_colors
        WHERE locale_code = p_locale;
    ELSIF p_kind = 'hair' THEN
        SELECT count(*) INTO v_count
        FROM faker.hair_colors
        WHERE locale_code = p_locale;
    ELSIF p_kind = 'email_domain' THEN
        SELECT count(*) INTO v_count FROM faker.email_domains;
    ELSE
        RAISE EXCEPTION 'Unknown lookup kind: %', p_kind;
    END IF;

    RETURN COALESCE(v_count, 0);
END;
$$;

CREATE OR REPLACE FUNCTION faker.pick_name(
    p_locale TEXT,
    p_type TEXT,
    p_seed TEXT,
    p_user_index BIGINT,
    p_field TEXT
)
RETURNS TEXT
LANGUAGE plpgsql
STABLE
STRICT
AS $$
DECLARE
    v_count BIGINT;
    v_offset BIGINT;
    v_value TEXT;
BEGIN
    v_count := faker.lookup_count(p_locale, 'name', p_type);
    IF v_count = 0 THEN
        RAISE EXCEPTION 'No names for locale % and type %', p_locale, p_type;
    END IF;

    v_offset := faker.choice_index(
        p_seed, p_locale, p_user_index, p_field, v_count
    );

    SELECT name_value
    INTO v_value
    FROM faker.names
    WHERE locale_code = p_locale
      AND name_type = p_type
      AND seq = v_offset::INTEGER;

    RETURN v_value;
END;
$$;

CREATE OR REPLACE FUNCTION faker.pick_title(
    p_locale TEXT,
    p_seed TEXT,
    p_user_index BIGINT,
    p_field TEXT
)
RETURNS TEXT
LANGUAGE plpgsql
STABLE
STRICT
AS $$
DECLARE
    v_count BIGINT;
    v_offset BIGINT;
    v_value TEXT;
BEGIN
    v_count := faker.lookup_count(p_locale, 'title');
    IF v_count = 0 THEN
        RETURN NULL;
    END IF;

    v_offset := faker.choice_index(
        p_seed, p_locale, p_user_index, p_field, v_count
    );

    SELECT title_value
    INTO v_value
    FROM faker.titles
    WHERE locale_code = p_locale
      AND seq = v_offset::INTEGER;

    RETURN v_value;
END;
$$;

CREATE OR REPLACE FUNCTION faker.pick_address_part(
    p_locale TEXT,
    p_type TEXT,
    p_seed TEXT,
    p_user_index BIGINT,
    p_field TEXT
)
RETURNS TEXT
LANGUAGE plpgsql
STABLE
STRICT
AS $$
DECLARE
    v_count BIGINT;
    v_offset BIGINT;
    v_value TEXT;
BEGIN
    v_count := faker.lookup_count(p_locale, 'address', p_type);
    IF v_count = 0 THEN
        RAISE EXCEPTION
            'No address parts for locale % and type %',
            p_locale, p_type;
    END IF;

    v_offset := faker.choice_index(
        p_seed, p_locale, p_user_index, p_field, v_count
    );

    SELECT part_value
    INTO v_value
    FROM faker.address_parts
    WHERE locale_code = p_locale
      AND part_type = p_type
      AND seq = v_offset::INTEGER;

    RETURN v_value;
END;
$$;

CREATE OR REPLACE FUNCTION faker.pick_region(
    p_locale TEXT,
    p_seed TEXT,
    p_user_index BIGINT,
    p_field TEXT
)
RETURNS TEXT
LANGUAGE plpgsql
STABLE
STRICT
AS $$
DECLARE
    v_count BIGINT;
    v_offset BIGINT;
    v_value TEXT;
BEGIN
    v_count := faker.lookup_count(p_locale, 'region');
    IF v_count = 0 THEN
        RAISE EXCEPTION 'No regions for locale %', p_locale;
    END IF;

    v_offset := faker.choice_index(
        p_seed, p_locale, p_user_index, p_field, v_count
    );

    SELECT region_code
    INTO v_value
    FROM faker.regions
    WHERE locale_code = p_locale
      AND seq = v_offset::INTEGER;

    RETURN v_value;
END;
$$;

CREATE OR REPLACE FUNCTION faker.pick_eye_color(
    p_locale TEXT,
    p_seed TEXT,
    p_user_index BIGINT,
    p_field TEXT
)
RETURNS TEXT
LANGUAGE plpgsql
STABLE
STRICT
AS $$
DECLARE
    v_count BIGINT;
    v_offset BIGINT;
    v_value TEXT;
BEGIN
    v_count := faker.lookup_count(p_locale, 'eye');
    IF v_count = 0 THEN
        RAISE EXCEPTION 'No eye colors for locale %', p_locale;
    END IF;

    v_offset := faker.choice_index(
        p_seed, p_locale, p_user_index, p_field, v_count
    );

    SELECT color_value
    INTO v_value
    FROM faker.eye_colors
    WHERE locale_code = p_locale
      AND seq = v_offset::INTEGER;

    RETURN v_value;
END;
$$;

CREATE OR REPLACE FUNCTION faker.pick_hair_color(
    p_locale TEXT,
    p_seed TEXT,
    p_user_index BIGINT,
    p_field TEXT
)
RETURNS TEXT
LANGUAGE plpgsql
STABLE
STRICT
AS $$
DECLARE
    v_count BIGINT;
    v_offset BIGINT;
    v_value TEXT;
BEGIN
    v_count := faker.lookup_count(p_locale, 'hair');
    IF v_count = 0 THEN
        RAISE EXCEPTION 'No hair colors for locale %', p_locale;
    END IF;

    v_offset := faker.choice_index(
        p_seed, p_locale, p_user_index, p_field, v_count
    );

    SELECT color_value
    INTO v_value
    FROM faker.hair_colors
    WHERE locale_code = p_locale
      AND seq = v_offset::INTEGER;

    RETURN v_value;
END;
$$;

CREATE OR REPLACE FUNCTION faker.pick_email_domain(
    p_seed TEXT,
    p_locale TEXT,
    p_user_index BIGINT,
    p_field TEXT
)
RETURNS TEXT
LANGUAGE plpgsql
STABLE
STRICT
AS $$
DECLARE
    v_count BIGINT;
    v_offset BIGINT;
    v_value TEXT;
BEGIN
    v_count := faker.lookup_count(p_locale, 'email_domain');
    IF v_count = 0 THEN
        RETURN 'example.com';
    END IF;

    v_offset := faker.choice_index(
        p_seed, p_locale, p_user_index, p_field, v_count
    );

    SELECT domain_value
    INTO v_value
    FROM faker.email_domains
    WHERE seq = v_offset::INTEGER;

    RETURN v_value;
END;
$$;
