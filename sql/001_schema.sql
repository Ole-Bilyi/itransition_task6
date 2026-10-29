CREATE SCHEMA IF NOT EXISTS faker;

CREATE TABLE IF NOT EXISTS faker.meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

INSERT INTO faker.meta (key, value)
VALUES
    ('dictionary_version', '2026.10.1'),
    ('library_version', '1.0.0')
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;

CREATE TABLE IF NOT EXISTS faker.locales (
    locale_code TEXT PRIMARY KEY,
    locale_name TEXT NOT NULL
);

INSERT INTO faker.locales (locale_code, locale_name)
VALUES
    ('en_US', 'English (United States)'),
    ('de_DE', 'German (Germany)')
ON CONFLICT (locale_code) DO NOTHING;

CREATE TABLE IF NOT EXISTS faker.names (
    name_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    locale_code TEXT NOT NULL REFERENCES faker.locales(locale_code),
    name_type TEXT NOT NULL
        CHECK (name_type IN ('first', 'middle', 'last')),
    name_value TEXT NOT NULL,
    seq INTEGER NOT NULL,
    UNIQUE (locale_code, name_type, name_value),
    UNIQUE (locale_code, name_type, seq)
);

CREATE TABLE IF NOT EXISTS faker.titles (
    title_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    locale_code TEXT NOT NULL REFERENCES faker.locales(locale_code),
    title_value TEXT NOT NULL,
    seq INTEGER NOT NULL,
    UNIQUE (locale_code, title_value),
    UNIQUE (locale_code, seq)
);

CREATE TABLE IF NOT EXISTS faker.address_parts (
    part_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    locale_code TEXT NOT NULL REFERENCES faker.locales(locale_code),
    part_type TEXT NOT NULL
        CHECK (part_type IN ('street', 'city', 'street_word')),
    part_value TEXT NOT NULL,
    seq INTEGER NOT NULL,
    UNIQUE (locale_code, part_type, part_value),
    UNIQUE (locale_code, part_type, seq)
);

CREATE TABLE IF NOT EXISTS faker.regions (
    region_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    locale_code TEXT NOT NULL REFERENCES faker.locales(locale_code),
    region_code TEXT NOT NULL,
    region_name TEXT NOT NULL,
    seq INTEGER NOT NULL,
    UNIQUE (locale_code, region_code),
    UNIQUE (locale_code, seq)
);

CREATE TABLE IF NOT EXISTS faker.eye_colors (
    color_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    locale_code TEXT NOT NULL REFERENCES faker.locales(locale_code),
    color_value TEXT NOT NULL,
    seq INTEGER NOT NULL,
    UNIQUE (locale_code, color_value),
    UNIQUE (locale_code, seq)
);

CREATE TABLE IF NOT EXISTS faker.hair_colors (
    color_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    locale_code TEXT NOT NULL REFERENCES faker.locales(locale_code),
    color_value TEXT NOT NULL,
    seq INTEGER NOT NULL,
    UNIQUE (locale_code, color_value),
    UNIQUE (locale_code, seq)
);

CREATE TABLE IF NOT EXISTS faker.email_domains (
    domain_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    domain_value TEXT NOT NULL,
    seq INTEGER NOT NULL,
    UNIQUE (domain_value),
    UNIQUE (seq)
);

CREATE INDEX IF NOT EXISTS ix_names_locale_type_seq
    ON faker.names(locale_code, name_type, seq);

CREATE INDEX IF NOT EXISTS ix_titles_locale_seq
    ON faker.titles(locale_code, seq);

CREATE INDEX IF NOT EXISTS ix_address_parts_locale_type_seq
    ON faker.address_parts(locale_code, part_type, seq);

CREATE INDEX IF NOT EXISTS ix_regions_locale_seq
    ON faker.regions(locale_code, seq);

CREATE INDEX IF NOT EXISTS ix_eye_colors_locale_seq
    ON faker.eye_colors(locale_code, seq);

CREATE INDEX IF NOT EXISTS ix_hair_colors_locale_seq
    ON faker.hair_colors(locale_code, seq);
