import logging
from . import models


logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s :: %(asctime)s :: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('db_queries_mixin')


class DbQueriesMixin:
    def _write_fire_data(self, conn, day: models.Day, journal_id: int):
        if not day.fire_dep:
            logger.warning(f'Empty fire_dep data date:{day.date} journal_id: {journal_id}')
            return

        sql = """
        INSERT INTO fire_data (
            `date`,
            `fires_num`,
            `dead`,
            `injured`,
            `journal_id`
        ) VALUES (?,?,?,?,?);
        """
        data_to_write = (
            day.date,
            day.fire_dep.fires_num,
            day.fire_dep.dead,
            day.fire_dep.injured,
            journal_id
        )

        cur = conn.cursor()
        cur.execute(sql, data_to_write)
        conn.commit()

        return cur.lastrowid

    def _write_police_data(self, conn, day: models.Day, journal_id: int):
        if not day.police_dep:
            logger.warning(f'Empty police_dep data date:{day.date} journal_id: {journal_id}')
            return

        sql = """
        INSERT INTO police_data (
            `date`,
            `incidents_num`,
            `notes`,
            `journal_id`
        ) VALUES (?,?,?,?);
        """
        data_to_write = (
            day.date,
            day.police_dep.incidents_num,
            day.police_dep.notes,
            journal_id
        )

        cur = conn.cursor()
        cur.execute(sql, data_to_write)
        conn.commit()

        return cur.lastrowid

    def _write_mchs_data(self, conn, day: models.Day, journal_id: int):
        if not day.mchs_dep:
            logger.warning(f'Empty mchs_dep data date:{day.date} journal_id: {journal_id}')
            return

        sql = """
        INSERT INTO mchs_data (
            `date`,
            `tourist_groups_num`,
            `tourist_groups_persons`,
            `dtp`,
            `search_jobs`,
            `save_jobs`,
            `another`,
            `journal_id`
        ) VALUES (?,?,?,?,?,?,?,?);
        """
        data_to_write = (
            day.date,
            day.mchs_dep.tourist_groups.num,
            day.mchs_dep.tourist_groups.persons,
            day.mchs_dep.dtp,
            day.mchs_dep.search_jobs,
            day.mchs_dep.save_jobs,
            day.mchs_dep.another,
            journal_id
        )

        cur = conn.cursor()
        cur.execute(sql, data_to_write)
        conn.commit()

        return cur.lastrowid

    def _write_weather_data(self, conn, day: models.Day, journal_id: int):
        if not day.weather:
            logger.warning(f'Empty weather data date:{day.date} journal_id: {journal_id}')
            return

        for row in day.weather:
            sql = """
            INSERT INTO weather (
                `date`,
                `place`,
                `external_temp`,
                `in_out_tube_temp`,
                `in_out_tube_pressure`,
                `journal_id`
            ) VALUES (?,?,?,?,?,?);
            """
            data_to_write = (
                day.date,
                row.place,
                row.external_temp,
                row.in_out_tube_temp,
                row.in_out_tube_pressure,
                journal_id
            )

            cur = conn.cursor()
            cur.execute(sql, data_to_write)
            conn.commit()
