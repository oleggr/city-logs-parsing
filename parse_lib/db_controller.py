import typing
import sqlite3
from . import models
from .db_queries import DbQueriesMixin


class DbController(DbQueriesMixin):
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
            journal_id = self._write_journal(conn, journal)

            for day in journal.days:
                for event in day.events:
                    self._write_event(conn, event, journal.version, journal_id)

            self._write_fire_data(conn, day, journal_id)
            self._write_police_data(conn, day, journal_id)
            self._write_mchs_data(conn, day, journal_id)
            self._write_weather_data(conn, day, journal_id)

        conn.close()

    def _write_journal(self, conn, journal: models.Journal):
        sql = """
        INSERT OR REPLACE INTO journals (
            `version`,
            `notes`,
            `duty_person`,
            `name`
        ) VALUES (?,?,?,?);
        """
        journal_to_write = (
            journal.version,
            journal.notes,
            journal.duty_person,
            journal.name,
        )

        cur = conn.cursor()
        cur.execute(sql, journal_to_write)
        conn.commit()

        return cur.lastrowid

    def _write_event(self, conn, event: models.Event, version: str, journal_id: int):
        sql = """
        INSERT INTO events (
            `date`, 
            `address`, 
            `text`,
            `datetime`,
            `organization`,
            `injured_fio`,
            `version`, 
            `journal_id`
        ) VALUES (?,?,?,?,?,?,?,?);
        """
        event_to_write = (
            event.date,
            event.address,
            event.text,
            event.datetime,
            event.organization,
            event.injured_fio,
            version,
            journal_id
        )

        cur = conn.cursor()
        cur.execute(sql, event_to_write)
        conn.commit()

        return cur.lastrowid

    def _create_table(self):
        conn = self._get_connection()
        with conn:
            cur = conn.cursor()

            sql = """
            CREATE TABLE IF NOT EXISTS events (
                `id`                        INTEGER PRIMARY KEY,
                `date`                      DATETIME,
                `address`                   TEXT,
                `text`                      TEXT,
                `datetime`                  TEXT,
                `organization`              TEXT,    
                `injured_fio`               TEXT,    
                `version`                   TEXT,
                `journal_id`                INTEGER,
                `created_at`                DATETIME DEFAULT current_timestamp
            );
            """
            cur.execute(sql)

            sql = """
            CREATE TABLE IF NOT EXISTS journals (
                `id`                        INTEGER PRIMARY KEY,
                `version`                   TEXT,
                `notes`                     TEXT,
                `duty_person`               TEXT,
                `name`                      TEXT UNIQUE,
                `created_at`                DATETIME DEFAULT current_timestamp
            );
            """
            cur.execute(sql)

            sql = """
            CREATE TABLE IF NOT EXISTS fire_data (
                `id`                        INTEGER PRIMARY KEY,
                `date`                      DATETIME,
                `fires_num`                 TEXT,          
                `dead`                      TEXT,  
                `injured`                   TEXT,
                `journal_id`                INTEGER,        
                `created_at`                DATETIME DEFAULT current_timestamp
            );
            """
            cur.execute(sql)

            sql = """
            CREATE TABLE IF NOT EXISTS police_data (
                `id`                        INTEGER PRIMARY KEY,
                `date`                      DATETIME,
                `incidents_num`             TEXT,              
                `notes`                     TEXT,      
                `journal_id`                INTEGER,        
                `created_at`                DATETIME DEFAULT current_timestamp
            );
            """
            cur.execute(sql)

            sql = """
            CREATE TABLE IF NOT EXISTS mchs_data (
                `id`                        INTEGER PRIMARY KEY,
                `date`                      DATETIME,
                `tourist_groups_num`        TEXT,
                `tourist_groups_persons`    TEXT,
                `dtp`                       TEXT,        
                `search_jobs`               TEXT,                
                `save_jobs`                 TEXT,            
                `another`                   TEXT,    
                `journal_id`                INTEGER,        
                `created_at`                DATETIME DEFAULT current_timestamp
            );
            """
            cur.execute(sql)

            sql = """
            CREATE TABLE IF NOT EXISTS weather (
                `id`                        INTEGER PRIMARY KEY,
                `date`                      DATETIME,
                `place`                     TEXT,  
                `external_temp`             TEXT,             
                `in_out_tube_temp`          TEXT,              
                `in_out_tube_pressure`      TEXT,                  
                `journal_id`                INTEGER,
                `created_at`                DATETIME DEFAULT current_timestamp
            );
            """
            cur.execute(sql)

            conn.commit()

        conn.close()
