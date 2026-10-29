CREATE OR REPLACE FUNCTION faker.ascii_slug(p_text TEXT)
RETURNS TEXT
LANGUAGE SQL
IMMUTABLE
STRICT
AS $$
    SELECT lower(regexp_replace(
        translate(
            replace(replace(replace(replace(replace(replace(replace(
                p_text,
                'ß', 'ss'),
                'Ä', 'Ae'), 'Ö', 'Oe'), 'Ü', 'Ue'),
                'ä', 'ae'), 'ö', 'oe'), 'ü', 'ue'),
            'ÁÉÍÓÚáéíóúÀÈÌÒÙàèìòùÂÊÎÔÛâêîôûÑñÇç',
            'AEIOUaeiouAEIOUaeiouAEIOUaeiouNnCc'
        ),
        '[^a-zA-Z0-9]+',
        '',
        'g'
    ));
$$;

CREATE OR REPLACE FUNCTION faker.format_full_name(
    p_locale TEXT,
    p_seed TEXT,
    p_user_index BIGINT
)
RETURNS TEXT
LANGUAGE plpgsql
STABLE
STRICT
AS $$
DECLARE
    v_first TEXT;
    v_middle TEXT;
    v_last TEXT;
    v_title TEXT;
    v_style INTEGER;
    v_hyphen BOOLEAN;
    v_second_last TEXT;
BEGIN
    v_first := faker.pick_name(p_locale, 'first', p_seed, p_user_index, 'first');
    v_last := faker.pick_name(p_locale, 'last', p_seed, p_user_index, 'last');

    v_middle := NULL;
    IF faker.u01(p_seed, p_locale, p_user_index, 'has_middle') < 0.38 THEN
        v_middle := faker.pick_name(
            p_locale, 'middle', p_seed, p_user_index, 'middle'
        );
    END IF;

    v_title := NULL;
    IF faker.u01(p_seed, p_locale, p_user_index, 'has_title') < 0.28 THEN
        v_title := faker.pick_title(p_locale, p_seed, p_user_index, 'title');
    END IF;

    v_hyphen := faker.u01(p_seed, p_locale, p_user_index, 'hyphen_last') < 0.08;
    IF v_hyphen THEN
        v_second_last := faker.pick_name(
            p_locale, 'last', p_seed, p_user_index, 'last2'
        );
        IF v_second_last IS DISTINCT FROM v_last THEN
            v_last := v_last || '-' || v_second_last;
        END IF;
    END IF;

    v_style := faker.randint(
        p_seed, p_locale, p_user_index, 'name_style', 0, 3
    );

    IF v_style = 1 AND v_middle IS NOT NULL THEN
        RETURN concat_ws(
            ' ',
            v_title,
            v_first,
            left(v_middle, 1) || '.',
            v_last
        );
    ELSIF v_style = 2 AND p_locale = 'de_DE' THEN
        RETURN concat_ws(' ', v_title, v_last || ',', v_first, v_middle);
    ELSIF v_style = 3 AND v_title IS NULL THEN
        RETURN concat_ws(' ', v_first, v_last);
    END IF;

    RETURN concat_ws(' ', v_title, v_first, v_middle, v_last);
END;
$$;

CREATE OR REPLACE FUNCTION faker.format_address(
    p_locale TEXT,
    p_seed TEXT,
    p_user_index BIGINT
)
RETURNS TEXT
LANGUAGE plpgsql
STABLE
STRICT
AS $$
DECLARE
    v_word TEXT;
    v_suffix TEXT;
    v_street TEXT;
    v_city TEXT;
    v_house INTEGER;
    v_unit INTEGER;
    v_postal TEXT;
    v_region TEXT;
    v_style INTEGER;
BEGIN
    v_word := faker.pick_address_part(
        p_locale, 'street_word', p_seed, p_user_index, 'street_word'
    );
    v_suffix := faker.pick_address_part(
        p_locale, 'street', p_seed, p_user_index, 'street_suffix'
    );
    v_city := faker.pick_address_part(
        p_locale, 'city', p_seed, p_user_index, 'city'
    );
    v_region := faker.pick_region(p_locale, p_seed, p_user_index, 'region');
    v_style := faker.randint(
        p_seed, p_locale, p_user_index, 'addr_style', 0, 2
    );

    IF p_locale = 'de_DE' THEN
        IF right(v_word, length(v_suffix)) = v_suffix THEN
            v_street := v_word;
        ELSIF v_suffix ~ '^[A-ZÄÖÜ]' THEN
            v_street := v_word || ' ' || v_suffix;
        ELSE
            v_street := v_word || v_suffix;
        END IF;

        v_house := faker.randint(
            p_seed, p_locale, p_user_index, 'house_no', 1, 220
        );
        v_postal := lpad(
            faker.randint(
                p_seed, p_locale, p_user_index, 'postal', 10000, 99999
            )::TEXT,
            5,
            '0'
        );

        IF v_style = 1 THEN
            RETURN format('%s %s, %s %s', v_street, v_house, v_postal, v_city);
        ELSIF v_style = 2 THEN
            RETURN format(
                '%s %s %s, %s %s',
                v_street,
                v_house,
                chr(64 + faker.randint(
                    p_seed, p_locale, p_user_index, 'house_letter', 1, 8
                )),
                v_postal,
                v_city
            );
        END IF;

        RETURN format('%s %s, %s %s (%s)', v_street, v_house, v_postal, v_city, v_region);
    END IF;

    v_street := v_word || ' ' || v_suffix;
    v_house := faker.randint(
        p_seed, p_locale, p_user_index, 'house_no', 1, 9999
    );
    v_postal := lpad(
        faker.randint(
            p_seed, p_locale, p_user_index, 'zip', 0, 99999
        )::TEXT,
        5,
        '0'
    );
    v_unit := faker.randint(
        p_seed, p_locale, p_user_index, 'unit', 1, 40
    );

    IF v_style = 1 THEN
        RETURN format(
            '%s %s, Apt %s, %s, %s %s',
            v_house, v_street, v_unit, v_city, v_region, v_postal
        );
    ELSIF v_style = 2 THEN
        RETURN format(
            '%s, %s %s %s',
            v_street || ' ' || v_house::TEXT, v_city, v_region, v_postal
        );
    END IF;

    RETURN format(
        '%s %s, %s, %s %s',
        v_house, v_street, v_city, v_region, v_postal
    );
END;
$$;

CREATE OR REPLACE FUNCTION faker.format_phone(
    p_locale TEXT,
    p_seed TEXT,
    p_user_index BIGINT
)
RETURNS TEXT
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    v_style INTEGER;
    v_npa INTEGER;
    v_exch INTEGER;
    v_line INTEGER;
    v_de INTEGER;
BEGIN
    v_style := faker.randint(
        p_seed, p_locale, p_user_index, 'phone_style', 0, 3
    );

    IF p_locale = 'en_US' THEN
        v_npa := faker.randint(p_seed, p_locale, p_user_index, 'npa', 201, 989);
        v_exch := 555;
        v_line := faker.randint(p_seed, p_locale, p_user_index, 'line', 1000, 9999);

        IF v_style = 1 THEN
            RETURN format('(%s) %s-%s', v_npa, v_exch, v_line);
        ELSIF v_style = 2 THEN
            RETURN format('%s.%s.%s', v_npa, v_exch, v_line);
        ELSIF v_style = 3 THEN
            RETURN format('+1 %s %s %s', v_npa, v_exch, v_line);
        END IF;

        RETURN format('+1-%s-%s-%s', v_npa, v_exch, v_line);
    END IF;

    v_de := faker.randint(
        p_seed, p_locale, p_user_index, 'de_sub', 1000000, 9999999
    );

    IF v_style = 1 THEN
        RETURN format('030-%s', v_de);
    ELSIF v_style = 2 THEN
        RETURN format('+49 30 %s', v_de);
    ELSIF v_style = 3 THEN
        RETURN format('+49 (0)30 %s', v_de);
    END IF;

    RETURN format('+49-30-%s', v_de);
END;
$$;

CREATE OR REPLACE FUNCTION faker.format_email(
    p_locale TEXT,
    p_seed TEXT,
    p_user_index BIGINT,
    p_full_name TEXT
)
RETURNS TEXT
LANGUAGE plpgsql
STABLE
STRICT
AS $$
DECLARE
    v_first TEXT;
    v_last TEXT;
    v_style INTEGER;
    v_domain TEXT;
    v_local TEXT;
BEGIN
    v_first := faker.ascii_slug(
        faker.pick_name(p_locale, 'first', p_seed, p_user_index, 'first')
    );
    v_last := faker.ascii_slug(
        replace(
            faker.pick_name(p_locale, 'last', p_seed, p_user_index, 'last'),
            '-',
            ''
        )
    );
    v_domain := faker.pick_email_domain(
        p_seed, p_locale, p_user_index, 'email_domain'
    );
    v_style := faker.randint(
        p_seed, p_locale, p_user_index, 'email_style', 0, 3
    );

    IF v_style = 1 THEN
        v_local := left(v_first, 1) || v_last || p_user_index::TEXT;
    ELSIF v_style = 2 THEN
        v_local := v_first || p_user_index::TEXT;
    ELSIF v_style = 3 THEN
        v_local := v_last || '.' || v_first || '.' || p_user_index::TEXT;
    ELSE
        v_local := v_first || '.' || v_last || '.' || p_user_index::TEXT;
    END IF;

    RETURN v_local || '@' || v_domain;
END;
$$;
