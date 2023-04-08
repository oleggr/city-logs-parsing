from abc import abstractmethod
import logging
import os
import typing

from parse_lib import models
from parse_lib.db_controller import DbController


logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s :: %(asctime)s :: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('worker')


class DefaultParser:
    files_dir: str
    files: typing.List[str]
    events: typing.Dict[str, typing.Any]

    VERSION = 'default'
    DEFAULT_NAME = 'default'
    FILE_FORMAT = 'docx'

    def __init__(self, files_dir: str, file_path: str = ''):
        if not files_dir[-1] == '/':
            files_dir += '/'

        self.files_dir = files_dir
        self.file_path = file_path

    def get_files(self):
        self.files = []

        if self.file_path:
            logger.info(f'Skip folder scan. Handle file {self.file_path}')
            self.files.append(self.file_path)
            return

        for path, subdirs, files in os.walk(self.files_dir):
            for name in files:
                if name[-4:] == self.FILE_FORMAT:
                    self.files.append(os.path.join(path, name))

        self.files.sort()

    def run(self):
        self.get_files()

        if not self.files:
            logger.warning('Files dir is empty')

        for file_path in self.files:
            journal = self.read_file(file_path)

            if not journal.days:
                logger.warning(
                    f'Journal {journal.name} is empty. Skip writing.'
                )
                continue

            self.write_journal_to_db(journal)

    @abstractmethod
    def read_file(self, file_path: str) -> models.Journal:
        pass

    def write_journal_to_db(self, journal: models.Journal):
        db = DbController()
        db.write_journal(journal)

    def transform_date(self, date: str):
        """
        Transform date from 18.11.2018 to 2018-11-18
        According to date format YYYY-MM-DD
        """

        try:
            date_parts = date.split('.')

            day = date_parts[0].strip()
            month = date_parts[1].strip()
            year = date_parts[2].strip()
        except Exception as exc:
            logger.error(f'Error while parsing date {date}')
            raise exc

        if len(day) == 1:
            day = '0' + day

        if len(year) == 2:
            year = '20' + year

        return f'{year}-{month}-{day}'
