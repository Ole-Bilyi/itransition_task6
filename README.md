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

## Installation

Requires PostgreSQL 14+ and Python 3.11+.

If you already have PostgreSQL 18 installed as a Windows service, create
`task6_data` in pgAdmin instead and put your real password in `DATABASE_URL`.
Do not commit that password.

1. Create a database, for example `task6_data`.
2. Set `DATABASE_URL`, then load the library:

```powershell
$env:DATABASE_URL = "postgresql://postgres:YOUR_PASSWORD@localhost:5432/task6_data"
python -m pip install -r requirements.txt
python scripts/generate_lookup_data.py
python scripts/load_sql.py
```

SQL files are applied in this order:

| File | Purpose |
| --- | --- |
| `sql/001_schema.sql` | Schema, locales, lookup tables, indexes |
| `sql/002_lookup_data.sql` | Names, titles, addresses, regions, colors |
| `sql/003_random_functions.sql` | Deterministic RNG, normal, sphere |
| `sql/004_pickers.sql` | Locale-aware table selection |
| `sql/005_formatters.sql` | Name, address, phone, email strings |
| `sql/006_generators.sql` | Batch generator and stored procedure |
| `sql/007_tests.sql` | Correctness checks |

From `psql`:

```text
\i sql/001_schema.sql
\i sql/002_lookup_data.sql
\i sql/003_random_functions.sql
\i sql/004_pickers.sql
\i sql/005_formatters.sql
\i sql/006_generators.sql
```

Run the web app:

```powershell
flask --app app run --debug
```

Open `http://127.0.0.1:5000`.

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

If you insert, delete, or reorder lookup values, the same offset can point at
a different name. Record `faker.meta.dictionary_version` with any release.
This dataset is `2026.10.1`.

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
  100,000–1,000,000 generated users without a 10-surname dictionary.
- Public city and region names.

No real personal emails, phones, or street-level private addresses are stored.

Approximate dictionary sizes after generation (see script output): several
hundred first names and 700+ last names per locale, 100+ cities, 150+ street
words. First × last combinations already exceed one million per locale, before
middle names, titles, and address variants.

## Tests

```sql
-- in psql, after install
\i sql/007_tests.sql
```

Expected:

1. `row_count = 10`
2. empty result (two identical batches)
3. `valid_latitudes` and `valid_longitudes` are true
4. indices 10 through 19
5. height/weight bounds true
6. dictionary version `2026.10.1`

## Benchmark

Measures procedure throughput through the same Python helper the web app uses
(HTML rendering is not included).

```powershell
python benchmark.py --users 10000 --batch-size 100
```

Record database plan, region, Python version, and whether the client is local
or remote. Warm up once; the script does a 10-row warmup by default.

Fill this table after you run it (do not invent numbers):

| Users | Batch size | Locale | Elapsed s | Users/s | Notes |
| --- | --- | --- | --- | --- | --- |
| 10_000 | 100 | en_US |  |  |  |
| 10_000 | 500 | en_US |  |  |  |
| 100_000 | 500 | en_US |  |  | optional |

## Extending the library

1. Insert into `faker.locales`.
2. Add names, titles, address parts, regions, and colors for that locale.
3. Assign dense `seq` values starting at 0 within each `(locale, type)` group.
4. Teach formatters any new postal or phone layout.
5. Bump `dictionary_version` in `faker.meta`.

New numeric attributes should call `faker.u01` / `faker.normal` with a **new**
field id so existing fields stay stable.

To wipe a previous install: run `sql/000_reset.sql`, then `python scripts/load_sql.py` again.

## Deployment (Render)

1. Push this repository (no `.env`, no passwords).
2. Create a Render PostgreSQL instance and a Python web service, or apply
   `render.yaml`.
3. Set `DATABASE_URL` from the database connection string (internal URL if
   the web service and database share a region).
4. **Manually run** `python scripts/load_sql.py` against that database.
   Render does not execute the SQL folder by itself.
5. Start command: `gunicorn --bind 0.0.0.0:$PORT app:app`

## Project layout

```text
app.py                 Flask routes
db.py                  CALL faker.generate_users_cursor
benchmark.py           users/second measurement
requirements.txt
render.yaml
sql/                   schema + library
scripts/generate_lookup_data.py
scripts/load_sql.py
templates/index.html
```
