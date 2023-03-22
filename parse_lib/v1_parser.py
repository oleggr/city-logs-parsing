import docx2txt
import logging
import re

from .default_parser import DefaultParser
from .models import Journal, Day, Event


logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s :: %(asctime)s :: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('v1_parser')


class V1Parser(DefaultParser):
    VERSION = 'v1'
    DEFAULT_NAME = 'default_v1'
    FILE_FORMAT = 'docx'

    def read_file(self, file_path: str) -> Journal:
        logger.info(f'Start parsing file: {file_path}')

        data = docx2txt.process(file_path)

        journal = Journal(
            name=self.DEFAULT_NAME,
            days=[],
            version=self.VERSION
        )
        day = None
        curr_date = None

        for line in data.split('\n'):
            if journal.name == self.DEFAULT_NAME:
                journal.name = line
                continue

            if not line:
                continue

            regexp = re.compile(r'[0-9]*\.[0-9]*\.[0-9]*')
            match = regexp.search(line)

            if match:
                if day:
                    journal.days.append(day)

                curr_date = self._prepare_date(line)
                day = Day(
                    date=curr_date,
                    events=[]
                )
                line = self._prepare_line(match.end(), line)

            day.events.append(
                Event(date=curr_date, text=line)
            )

        if not journal.days:
            logger.warning(f'Journal is empty')

        return journal

    def _prepare_date(self, line: str):
        """
        handle 1.11.18 to 01.11.2018
        """
        date = line.split(' ')[0].strip()
        day, month, year = date.split('.')

        if len(day) == 1:
            day = '0' + day

        if len(year) == 2:
            year = '20' + year

        return f'{day}.{month}.{year}'

    def _prepare_line(self, pos_to_cut: int, line: str):
        """
        handle ' - smth' to 'smth'
        """
        line = line[pos_to_cut:].strip()

        if line[0] == '–' or line[0] == '-':
            return line[1:].strip()

        return line

    def _check_is_header(self, text: str):
        result = re.match(r'Журнал [0-9]*', text)
        return True if result else False
