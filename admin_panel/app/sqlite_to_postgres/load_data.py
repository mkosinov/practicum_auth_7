import os
import sqlite3
from contextlib import closing
from dataclasses import astuple, fields

import psycopg2
import psycopg2.extras
from transferDC import (
    FilmWorkDC,
    GenreDC,
    GenreFilmWorkDC,
    PersonDC,
    PersonFilmWorkDC,
)


DSN = {
    "database": os.environ.get("POSTGRES_DB"),
    "user": os.environ.get("POSTGRES_USER"),
    "password": os.environ.get("POSTGRES_PASSWORD"),
    "host": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
    "port": os.environ.get("POSTGRES_PORT", 5432),
    "options": "-c search_path=" + os.environ.get("DB_SCHEMA", "content"),
}
DB_PATH = os.environ.get("DB_PATH", "db.sqlite")
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", 100))


class SQLiteWorker:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.cur = self.conn.cursor()
        self.cur.row_factory = sqlite3.Row

    def execute_select(self, table_name: str):
        if table_name == "genre":
            self.current_DC = GenreDC
            self.cur.execute(
                "SELECT id, name, description, \
                            created_at AS created, updated_at AS modified FROM genre;"
            )
        elif table_name == "person":
            self.current_DC = PersonDC
            self.cur.execute(
                "SELECT id, full_name, \
                            created_at AS created, updated_at AS modified FROM person;"
            )
        elif table_name == "film_work":
            self.current_DC = FilmWorkDC
            self.cur.execute(
                "SELECT id, title, description, creation_date, file_path, rating, type, \
                            created_at AS created, updated_at AS modified FROM film_work;"
            )
        elif table_name == "genre_film_work":
            self.current_DC = GenreFilmWorkDC
            self.cur.execute(
                "SELECT id, film_work_id, genre_id, \
                            created_at AS created FROM genre_film_work;"
            )
        elif table_name == "person_film_work":
            self.current_DC = PersonFilmWorkDC
            self.cur.execute(
                "SELECT id, film_work_id, person_id, role, \
                            created_at AS created FROM person_film_work;"
            )

    def fetch_rows(self, batch_size: int):
        return self.cur.fetchmany(batch_size)

    def close(self):
        self.cur.close()
        self.conn.close()


class PGWorker:
    def __init__(self, pre_truncate: bool, **conn):
        self.pre_truncate = pre_truncate
        self.conn = psycopg2.connect(
            **conn, cursor_factory=psycopg2.extras.DictCursor
        )
        self.cur = self.conn.cursor()

    def upsert_to_postgres(self, table_name, DC_data):
        column_names = [field.name for field in fields(DC_data[0])]
        fill_s_chars = ", ".join(["%s"] * len(column_names))
        bind_values = [
            self.cur.mogrify(f"({fill_s_chars})", astuple(row)).decode("utf-8")
            for row in DC_data
        ]
        bind_values_str = ",".join(bind_values)
        column_names_str = ", ".join(column_names)
        excluded_column_names_str = ", ".join(
            ["EXCLUDED." + column_name for column_name in column_names]
        )
        query = f"INSERT INTO {table_name} ({column_names_str}) VALUES {bind_values_str} ON CONFLICT (id) DO UPDATE SET\
            ({column_names_str})=({excluded_column_names_str});"
        self.cur.execute(query)

    def truncate_table(self, table_name):
        self.cur.execute(f"TRUNCATE content.{table_name} CASCADE;")

    def prepare_schema(self):
        self.cur.execute(open("create_schema.ddl", "r").read())

    def close(self):
        self.cur.close()
        self.conn.close()


def transfer_process(sq, pg, table_names: list, batch_size: int):
    for table_name in table_names:
        sq.execute_select(table_name)
        DC_rows = [sq.current_DC(**row) for row in sq.fetch_rows(batch_size)]
        if pg.pre_truncate:
            pg.truncate_table(table_name)
        while DC_rows:
            pg.upsert_to_postgres(table_name, DC_rows)
            DC_rows = [
                sq.current_DC(**row) for row in sq.fetch_rows(batch_size)
            ]


if __name__ == "__main__":
    ordered_table_names = [
        "genre",
        "person",
        "film_work",
        "genre_film_work",
        "person_film_work",
    ]
    with closing(SQLiteWorker(db_path=DB_PATH)) as sq, closing(
        PGWorker(pre_truncate=True, **DSN)
    ) as pg:
        with pg.conn:
            transfer_process(sq, pg, ordered_table_names, BATCH_SIZE)
