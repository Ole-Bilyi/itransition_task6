CREATE OR REPLACE FUNCTION faker.u01(
    p_seed TEXT,
    p_locale TEXT,
    p_user_index BIGINT,
    p_field TEXT
)
RETURNS DOUBLE PRECISION
LANGUAGE SQL
IMMUTABLE
STRICT
AS $$
    SELECT (
        ('x' || substr(
            md5(
                p_seed || '|' ||
                p_locale || '|' ||
                p_user_index::TEXT || '|' ||
                p_field
            ),
            1, 13
        ))::bit(52)::BIGINT
    )::DOUBLE PRECISION / 4503599627370496.0;
$$;

COMMENT ON FUNCTION faker.u01(TEXT, TEXT, BIGINT, TEXT) IS
    'Deterministic U[0,1) value from md5(seed|locale|index|field).';

CREATE OR REPLACE FUNCTION faker.randint(
    p_seed TEXT,
    p_locale TEXT,
    p_user_index BIGINT,
    p_field TEXT,
    p_min INTEGER,
    p_max INTEGER
)
RETURNS INTEGER
LANGUAGE SQL
IMMUTABLE
STRICT
AS $$
    SELECT p_min + floor(
        faker.u01(p_seed, p_locale, p_user_index, p_field)
        * (p_max - p_min + 1)::DOUBLE PRECISION
    )::INTEGER;
$$;

COMMENT ON FUNCTION faker.randint(TEXT, TEXT, BIGINT, TEXT, INTEGER, INTEGER) IS
    'Inclusive integer in [p_min, p_max] derived from faker.u01.';

CREATE OR REPLACE FUNCTION faker.choice_index(
    p_seed TEXT,
    p_locale TEXT,
    p_user_index BIGINT,
    p_field TEXT,
    p_count BIGINT
)
RETURNS BIGINT
LANGUAGE SQL
IMMUTABLE
STRICT
AS $$
    SELECT CASE
        WHEN p_count <= 0 THEN 0
        ELSE floor(
            faker.u01(p_seed, p_locale, p_user_index, p_field)
            * p_count::DOUBLE PRECISION
        )::BIGINT
    END;
$$;

COMMENT ON FUNCTION faker.choice_index(TEXT, TEXT, BIGINT, TEXT, BIGINT) IS
    'Offset in 0..p_count-1 for table lookups.';

CREATE OR REPLACE FUNCTION faker.normal(
    p_seed TEXT,
    p_locale TEXT,
    p_user_index BIGINT,
    p_field TEXT,
    p_mean DOUBLE PRECISION,
    p_stddev DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE SQL
IMMUTABLE
STRICT
AS $$
    SELECT p_mean
        + p_stddev
        * sqrt(-2.0 * ln(greatest(
            faker.u01(
                p_seed, p_locale, p_user_index,
                p_field || '_u1'
            ),
            1e-15
        )))
        * cos(
            2.0 * pi() * faker.u01(
                p_seed, p_locale, p_user_index,
                p_field || '_u2'
            )
        );
$$;

COMMENT ON FUNCTION faker.normal(TEXT, TEXT, BIGINT, TEXT, DOUBLE PRECISION, DOUBLE PRECISION) IS
    'Box–Muller normal sample N(mean, stddev^2), independent u1/u2 fields.';

CREATE OR REPLACE FUNCTION faker.truncated_normal(
    p_seed TEXT,
    p_locale TEXT,
    p_user_index BIGINT,
    p_field TEXT,
    p_mean DOUBLE PRECISION,
    p_stddev DOUBLE PRECISION,
    p_min DOUBLE PRECISION,
    p_max DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE SQL
IMMUTABLE
STRICT
AS $$
    SELECT greatest(
        p_min,
        least(
            p_max,
            faker.normal(
                p_seed, p_locale, p_user_index, p_field,
                p_mean, p_stddev
            )
        )
    );
$$;

COMMENT ON FUNCTION faker.truncated_normal(TEXT, TEXT, BIGINT, TEXT, DOUBLE PRECISION, DOUBLE PRECISION, DOUBLE PRECISION, DOUBLE PRECISION) IS
    'Normal sample clamped to [p_min, p_max]. Clamping thickens the tails.';

CREATE OR REPLACE FUNCTION faker.sphere_longitude(
    p_seed TEXT,
    p_locale TEXT,
    p_user_index BIGINT,
    p_field TEXT
)
RETURNS DOUBLE PRECISION
LANGUAGE SQL
IMMUTABLE
STRICT
AS $$
    SELECT 360.0 * faker.u01(p_seed, p_locale, p_user_index, p_field) - 180.0;
$$;

CREATE OR REPLACE FUNCTION faker.sphere_latitude(
    p_seed TEXT,
    p_locale TEXT,
    p_user_index BIGINT,
    p_field TEXT
)
RETURNS DOUBLE PRECISION
LANGUAGE SQL
IMMUTABLE
STRICT
AS $$
    -- Inverse CDF of the area element on a sphere: lat = asin(2u - 1).
    SELECT degrees(asin(
        2.0 * faker.u01(p_seed, p_locale, p_user_index, p_field) - 1.0
    ));
$$;

COMMENT ON FUNCTION faker.sphere_latitude(TEXT, TEXT, BIGINT, TEXT) IS
    'Latitude with constant PDF on the sphere (not uniform in degrees).';
