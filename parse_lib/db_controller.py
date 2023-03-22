import typing
import sqlite3
from . import models


class DbController:
    DB_PARAMS: typing.Dict[str, str]
    db_filename: str = 'journals.db'

    def __init__(self):
        self.DB_PARAMS = {
            'database': self.db_filename
        }
        self._create_table()

    def _get_connection(self):
        """Open connection"""
        conn = None
        try:
            conn = sqlite3.connect(**self.DB_PARAMS)
        except Exception as e:
            print(e)

        return conn

    def write_journal(self, journal: models.Journal):
        conn = self._get_connection()
        with conn:
            journal_id = self._write_journal(conn, journal.name)

            for day in journal.days:
                for event in day.events:
                    self._write_event(conn, event, journal.version, journal_id)

        conn.close()

    def _write_event(self, conn, event: models.Event, version: str, journal_id: int):
        sql = """
        INSERT INTO events (
            `date`, 
            `address`, 
            `text`, 
            `version`, 
            `journal_id`
        ) VALUES (?,?,?,?,?);
        """
        event_to_write = (event.date, event.address, event.text, version, journal_id)

        cur = conn.cursor()
        cur.execute(sql, event_to_write)
        conn.commit()

        return cur.lastrowid

    def _write_journal(self, conn, journal_name: str):
        sql = f"""
        INSERT OR REPLACE INTO journals (
            `name`
        ) VALUES ('{journal_name}');
        """
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()

        return cur.lastrowid

    def _create_table(self):
        conn = self._get_connection()
        with conn:
            cur = conn.cursor()

            sql = """
            CREATE TABLE IF NOT EXISTS events (
                `id`            INTEGER PRIMARY KEY,
                `date`          TEXT,
                `address`       TEXT,
                `text`          TEXT,
                `version`       TEXT,
                `journal_id`    INTEGER,
                `created_at`    DATETIME DEFAULT current_timestamp
            );
            """
            cur.execute(sql)

            sql = """
            CREATE TABLE IF NOT EXISTS journals (
                `id`            INTEGER PRIMARY KEY,
                `version`       TEXT,
                `name`          TEXT UNIQUE,
                `created_at`    DATETIME DEFAULT current_timestamp
            );
            """
            cur.execute(sql)

            conn.commit()

        conn.close()
