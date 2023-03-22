from abc import abstractmethod
import logging
import os
import typing

from . import models
from .db_controller import DbController


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

    def __init__(self, files_dir: str):
        if not files_dir[-1] == '/':
            files_dir += '/'

        self.files_dir = files_dir

    def get_files(self):
        self.files = []

        for path, subdirs, files in os.walk(self.files_dir):
            for name in files:
                if name[-4:] == self.FILE_FORMAT:
                    self.files.append(os.path.join(path, name))

    def run(self):
        self.get_files()

        if not self.files:
            logger.warning('Files dir is empty')

        for file_path in self.files:
            journal = self.read_file(file_path)
            self.write_journal_to_db(journal)

    @abstractmethod
    def read_file(self, file_path: str) -> models.Journal:
        pass

    def write_journal_to_db(self, journal: models.Journal):
        db = DbController()
        db.write_journal(journal)
