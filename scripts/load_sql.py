from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = ROOT / "sql"
FILES = [
    "001_schema.sql",
    "002_lookup_data.sql",
    "003_random_functions.sql",
    "004_pickers.sql",
    "005_formatters.sql",
    "006_generators.sql",
]


def database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit("DATABASE_URL is not configured")
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    return url


def split_sql(script: str) -> list[str]:
    statements: list[str] = []
    buf: list[str] = []
    i = 0
    n = len(script)
    dollar_tag: str | None = None
    in_single = False

    while i < n:
        if dollar_tag is not None:
            if script.startswith(dollar_tag, i):
                buf.append(dollar_tag)
                i += len(dollar_tag)
                dollar_tag = None
                continue
            buf.append(script[i])
            i += 1
            continue

        if in_single:
            if script.startswith("''", i):
                buf.append("''")
                i += 2
                continue
            ch = script[i]
            buf.append(ch)
            if ch == "'":
                in_single = False
            i += 1
            continue

        if script.startswith("--", i):
            end = script.find("\n", i)
            if end == -1:
                break
            i = end + 1
            continue

        if script[i] == "'":
            in_single = True
            buf.append("'")
            i += 1
            continue

        if script[i] == "$":
            match = re.match(r"\$[A-Za-z0-9_]*\$", script[i:])
            if match:
                dollar_tag = match.group(0)
                buf.append(dollar_tag)
                i += len(dollar_tag)
                continue

        if script[i] == ";":
            statement = "".join(buf).strip()
            if statement:
                statements.append(statement)
            buf = []
            i += 1
            continue

        buf.append(script[i])
        i += 1

    tail = "".join(buf).strip()
    if tail:
        statements.append(tail)
    return statements


def main() -> None:
    url = database_url()
    with psycopg.connect(url, autocommit=True) as connection:
        with connection.cursor() as cursor:
            for name in FILES:
                path = SQL_DIR / name
                print(f"Applying {name} ...")
                for statement in split_sql(path.read_text(encoding="utf-8")):
                    cursor.execute(statement)
    print("SQL Faker installed.")
    if "--test" in sys.argv:
        print("Run sql/007_tests.sql in psql for the assertion queries.")


if __name__ == "__main__":
    main()
