import typing
import sqlite3
import models


class DbController:
    DB_PARAMS: typing.Dict[str, str]
    db_filename: str = 'sqlite.db'

    def __init__(self):
        self.DB_PARAMS = {
            'database': self.db_filename
        }

    def write_journal(self, journal: models.Journal):
        conn = self._get_connection()
        with conn:
            for day in journal.days:
                for event in day.events:
                    self._write_event(conn, event)

        conn.close()

    def _write_event(self, conn, event: models.Event):
        sql ="""INSERT INTO events (`date`, `address`, `text`) VALUES (?,?,?);"""
        event_to_write = (event.date, event.address, event.text)

        cur = conn.cursor()
        cur.execute(sql, event_to_write)
        conn.commit()

        return cur.lastrowid

    def _get_connection(self):
        """Open connection"""
        conn = None
        try:
            conn = sqlite3.connect(**self.DB_PARAMS)
        except Exception as e:
            print(e)

        return conn
