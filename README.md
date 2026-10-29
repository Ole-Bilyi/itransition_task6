# SQL Faker

PostgreSQL library of stored functions and a stored procedure that generate
reproducible fake contact records. A small Flask app calls the procedure and
renders the results.

Generation never happens in Python. Flask only validates the form, calls
`faker.generate_users_cursor`, and displays the rows.

- Locales: `en_US`, `de_DE`
- Dictionary version: `2026.10.1`
- Library version: `1.0.0`

## Architecture

```
Browser  →  Flask (app.py)  →  PostgreSQL procedure faker.generate_users_cursor
                                      ↓
                            faker.generate_users()
                                      ↓
                     pickers + formatters + random primitives
                                      ↓
                               lookup tables
```

Adding a country means inserting a locale row and lookup values. There are no
per-language tables such as `english_names`.

## How to use the library

### Main stored procedure (what the app calls)

```sql
CALL faker.generate_users_cursor(
    'en_US',          -- locale
    'demo-seed',      -- seed
    0,                -- batch index, zero-based
    10,               -- batch size, 1–1000
    'fake_users_cursor'
);

FETCH ALL FROM "fake_users_cursor";
```

The fifth argument is an `INOUT REFCURSOR`. Fetch it in the same transaction.

### Table-returning function (handy in SQL)

```sql
SELECT *
FROM faker.generate_users('en_US', 'demo-seed', 0, 10);

SELECT *
FROM faker.generate_users('en_US', 'demo-seed', 1, 10);

SELECT *
FROM faker.generate_users('de_DE', 'germany-2026', 0, 10);
```

Batch `k` of size `n` produces global indices `k*n .. k*n+n-1`.

Returned columns:

| Column | Type | Description |
| --- | --- | --- |
| `user_index` | `BIGINT` | Global index of the fake person |
| `full_name` | `TEXT` | Title / middle / hyphen variants |
| `address` | `TEXT` | Locale-formatted synthetic address |
| `latitude` | `DOUBLE PRECISION` | Degrees, uniform on the sphere |
| `longitude` | `DOUBLE PRECISION` | Degrees in `[-180, 180)` |
| `height_cm` | `DOUBLE PRECISION` | Truncated normal, cm |
| `weight_kg` | `DOUBLE PRECISION` | Truncated normal, kg |
| `eye_color` | `TEXT` | Discrete locale label |
| `hair_color` | `TEXT` | Discrete locale label |
| `phone` | `TEXT` | Fictional number, several layouts |
| `email` | `TEXT` | Reserved example / invalid domains |

### Exceptions

- seed empty, null, or longer than 200 characters
- batch index negative
- batch size outside 1–1000
- unknown locale
- empty lookup group for a required type

## Function reference

### `faker.u01(p_seed, p_locale, p_user_index, p_field) → float`

Deterministic value in `[0, 1)`.

Algorithm: `md5(seed|locale|index|field)`, take 13 hex digits, interpret as a
52-bit integer, divide by `2^52` (`4503599627370496`).

The same four arguments always yield the same number. Different `p_field`
values are independent streams, so adding a new attribute does not reshuffle
existing ones.

### `faker.randint(..., p_min, p_max) → int`

Inclusive integer from `u01`.

### `faker.choice_index(..., p_count) → bigint`

Offset in `0 .. p_count-1` used by pickers.

### `faker.normal(..., p_mean, p_stddev) → float`

Box–Muller transform:

1. `u1 = u01(..., field || '_u1')`
2. `u2 = u01(..., field || '_u2')`
3. `z = sqrt(-2 ln u1) * cos(2π u2)`
4. return `mean + stddev * z`

`u1` is clamped away from 0 (`1e-15`) so `ln` is defined.

### `faker.truncated_normal(..., p_min, p_max) → float`

Same as `normal`, then clamped to `[p_min, p_max]`. Clamping is **not** a
true truncated-normal sampler; probability mass from the tails sits on the
bounds. Heights use mean 170 cm, sd 10, clamp `[140, 210]`. Weights use mean
75 kg, sd 15, clamp `[40, 150]`. These are illustrative, not medical.

### `faker.sphere_longitude(...) → float`

`360 * u01 - 180`. Uniform in longitude.

### `faker.sphere_latitude(...) → float`

Uniform distribution **on the sphere surface** is not uniform in latitude
degrees. Area element is proportional to `cos(lat) d lat`. Inverse CDF:

`lat = asin(2u - 1)` (in radians, then converted to degrees).

Sampling two independent uniforms in `[-90, 90]` and `[-180, 180]` would
over-represent the poles.

### Pickers

All pickers map `choice_index` onto a dense `seq` column (`0 .. count-1`) so
selection is an index lookup, not `OFFSET`.

| Function | Source table |
| --- | --- |
| `faker.pick_name(locale, type, seed, index, field)` | `faker.names` |
| `faker.pick_title(...)` | `faker.titles` |
| `faker.pick_address_part(locale, type, ...)` | `faker.address_parts` |
| `faker.pick_region(...)` | `faker.regions` |
| `faker.pick_eye_color(...)` | `faker.eye_colors` |
| `faker.pick_hair_color(...)` | `faker.hair_colors` |
| `faker.pick_email_domain(...)` | `faker.email_domains` |

`name_type` is `first`, `middle`, or `last`. Address `part_type` is
`street_word`, `street` (suffix), or `city`.

### Formatters

#### `faker.format_full_name(locale, seed, index)`

- Always picks first and last name.
- ~38% include a middle name.
- ~28% include a title.
- ~8% hyphenate two last names.
- Style roll: full middle name, middle initial, German `Last, First`, or
  first+last only.

#### `faker.format_address(locale, seed, index)`

Builds `street_word + suffix`, city, region, house number, postal code.

- `en_US`: `123 Oak Street, Austin, TX 78701`, apartment form, or
  street-first form. ZIP is zero-padded.
- `de_DE`: `Hauptstraße 12, 10115 Berlin`, optional house letter, optional
  state code. Postal codes are five digits.

Addresses are formatted like real mail, but they are not validated against
postal databases.

#### `faker.format_phone(locale, seed, index)`

- `en_US`: area code 201–989, exchange **555** (fictional), four-digit line.
  Layouts: `+1-NPA-555-LINE`, `(NPA) 555-LINE`, dotted, spaced.
- `de_DE`: Berlin-style `+49-30-…` and local `030-…` variants. Numbers are
  synthetic, not allocated subscribers.

#### `faker.format_email(locale, seed, index, full_name)`

ASCII-folds the first/last name (`ä→ae`, `ß→ss`, …), then one of:

- `first.last.index@domain`
- `flastindex@domain`
- `firstindex@domain`
- `last.first.index@domain`

Domains are reserved (`example.com`, `example.net`, `example.org`,
`mail.example`, `test.invalid`).

#### `faker.ascii_slug(text)`

Lowercase identifier used in emails.

## Reproducibility contract

A field of a person is a pure function of:

1. locale code
2. seed string
3. global user index (`batch_index * batch_size + offset`)
4. field name (`'first'`, `'height_u1'`, `'phone_style'`, …)
5. **dictionary version** and row `seq` order of lookup tables

Identical arguments on the same dictionary version return identical rows,
including after restarting Flask or PostgreSQL.

## Lookup tables and provenance

Shared tables, distinguished by `locale_code`:

- `faker.locales`
- `faker.names`
- `faker.titles`
- `faker.address_parts`
- `faker.regions` (US states / German Länder)
- `faker.eye_colors`, `faker.hair_colors`
- `faker.email_domains`
- `faker.meta`

`scripts/generate_lookup_data.py` rebuilds `sql/002_lookup_data.sql`.

Sources:

- Common public given names and surnames (census-style frequency lists).
- Extra combinatorial syllable names so the pool is large enough for
  100,000–1,000,000 generated users.
- Public city and region names.

No real personal emails, phones, or street-level private addresses are stored.
