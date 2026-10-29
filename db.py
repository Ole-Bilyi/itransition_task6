import os

import psycopg
from psycopg.rows import dict_row


def database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not configured")
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    return url


def get_connection():
    return psycopg.connect(
        database_url(),
        row_factory=dict_row,
        connect_timeout=10,
    )


def generate_users(
    locale: str,
    seed: str,
    batch_index: int,
    batch_size: int = 10,
):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CALL faker.generate_users_cursor(
                    %s, %s, %s, %s, %s
                )
                """,
                (
                    locale,
                    seed,
                    batch_index,
                    batch_size,
                    "fake_users_cursor",
                ),
            )
            cursor.execute('FETCH ALL FROM "fake_users_cursor"')
            return cursor.fetchall()
