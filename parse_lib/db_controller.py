import logging
import typing
import sqlite3
from parse_lib import models
from parse_lib.db_queries import DbQueriesMixin
from parse_lib.parsing.parsing_config import event_types, addresses


logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s :: %(asctime)s :: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('db_controller')


class DbController(DbQueriesMixin):
    DB_PARAMS: typing.Dict[str, str]
    db_filename: str = 'journals.db'

    def __init__(self):
        self.DB_PARAMS = {
            'database': self.db_filename
        }
        self._create_table()
        self.write_addresses()

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
        INSERT INTO journals (
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

        event_id = cur.lastrowid

        self._write_address_mapping_to_event(event_id, event.addr_mappings)

        return event_id

    def _write_address_mapping_to_event(self, event_id, mappings):
        conn = self._get_connection()

        if not mappings:
            return

        for mapping in mappings:
            sql = """
            INSERT INTO events_to_address_mappings (
                `event_id`,
                `address_id` 
            ) VALUES (?,?);
            """

            cur = conn.cursor()
            cur.execute(sql, (event_id, mapping))
            conn.commit()

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

            sql = """
            CREATE TABLE IF NOT EXISTS addresses (
                `address_id`                INTEGER PRIMARY KEY,
                `address`                   TEXT,  
                `created_at`                DATETIME DEFAULT current_timestamp
            );
            """
            cur.execute(sql)

            sql = """
            CREATE TABLE IF NOT EXISTS events_to_address_mappings (
                `event_id`                  INTEGER,
                `address_id`                INTEGER,
                `created_at`                DATETIME DEFAULT current_timestamp
            );
            """
            cur.execute(sql)

            conn.commit()

        conn.close()

    def read_events(self):
        conn = self._get_connection()
        sql = """SELECT * from events;"""

        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()

        rows = cur.fetchall()

        return rows

    def get_addresses(self):
        conn = self._get_connection()
        sql = """SELECT * from addresses;"""

        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()

        rows = cur.fetchall()

        return rows

    def write_addresses(self):
        addresses_to_write = set()

        for key in addresses:
            addresses_to_write.add(addresses[key])

        conn = self._get_connection()

        if len(self.get_addresses()) > 0:
            logger.warning('Addresses already in db. Skip writing.')

        for address in addresses_to_write:
            sql = f"""
            INSERT INTO addresses (
                `address`
            ) VALUES ('{address}');
            """

            cur = conn.cursor()
            cur.execute(sql)
            conn.commit()
