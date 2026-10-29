from __future__ import annotations

import os
import sys

import psycopg


def database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit("DATABASE_URL is not configured")
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    return url


def main() -> int:
    failed = 0
    with psycopg.connect(database_url()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT count(*) FROM faker.generate_users('en_US', 'test-seed', 0, 10)"
            )
            count = cursor.fetchone()[0]
            print("Test 1 row_count:", count)
            failed += count != 10

            cursor.execute(
                """
                SELECT count(*) FROM (
                    (
                        SELECT * FROM faker.generate_users('de_DE', 'repeatable', 0, 10)
                        EXCEPT
                        SELECT * FROM faker.generate_users('de_DE', 'repeatable', 0, 10)
                    )
                    UNION ALL
                    (
                        SELECT * FROM faker.generate_users('de_DE', 'repeatable', 0, 10)
                        EXCEPT
                        SELECT * FROM faker.generate_users('de_DE', 'repeatable', 0, 10)
                    )
                ) diffs
                """
            )
            diffs = cursor.fetchone()[0]
            print("Test 2 reproducibility diffs:", diffs)
            failed += diffs != 0

            cursor.execute(
                """
                SELECT
                    bool_and(latitude BETWEEN -90 AND 90),
                    bool_and(longitude >= -180 AND longitude < 180)
                FROM faker.generate_users('en_US', 'geo-test', 0, 100)
                """
            )
            lat_ok, lon_ok = cursor.fetchone()
            print("Test 3 bounds:", lat_ok, lon_ok)
            failed += not (lat_ok and lon_ok)

            cursor.execute(
                """
                SELECT array_agg(user_index ORDER BY user_index)
                FROM faker.generate_users('en_US', 'batch-test', 1, 10)
                """
            )
            indices = cursor.fetchone()[0]
            print("Test 4 indices:", indices)
            failed += list(indices) != list(range(10, 20))

            cursor.execute(
                """
                SELECT
                    bool_and(height_cm BETWEEN 140 AND 210),
                    bool_and(weight_kg BETWEEN 40 AND 150)
                FROM faker.generate_users('de_DE', 'physical-test', 0, 100)
                """
            )
            h_ok, w_ok = cursor.fetchone()
            print("Test 5 physical bounds:", h_ok, w_ok)
            failed += not (h_ok and w_ok)

            cursor.execute(
                "SELECT value FROM faker.meta WHERE key = 'dictionary_version'"
            )
            version = cursor.fetchone()[0]
            print("Test 6 dictionary_version:", version)
            failed += version != "2026.10.1"

    if failed:
        print("FAILED")
        return 1
    print("ALL PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
