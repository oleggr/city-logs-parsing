import typing

import docx2txt
from docx import Document
import logging
import os
import re

from .default_parser import DefaultParser
from .models import Journal, Day, Event


logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s :: %(asctime)s :: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('v2_parser')


class V2Parser(DefaultParser):
    VERSION = 'v2'
    DEFAULT_NAME = 'default_v2'
    FILE_FORMAT = 'docx'

    def read_file(self, file_path: str) -> Journal:
        logger.info(f'Start parsing file: {file_path}')

        word_doc = Document(file_path)

        # data = docx2txt.process(file_path)
        for table in word_doc.tables:
            pass

        journal = Journal(
            name=self.DEFAULT_NAME,
            days=[],
            version=self.VERSION
        )

        day = Day(date='', events=[])

        self._parse_notes(day, word_doc)

        print(day)

        # day = None
        # curr_date = None
        #
        # for line in data.split('\n'):
        #     if journal.name == self.DEFAULT_NAME:
        #         journal.name = line
        #         continue
        #
        #     if not line:
        #         continue
        #
        #     regexp = re.compile(r'[0-9]*\.[0-9]*\.[0-9]*')
        #     match = regexp.search(line)
        #
        #     if match:
        #         if day:
        #             journal.days.append(day)
        #
        #         curr_date = line.split(' ')[0].strip()
        #         day = Day(date=curr_date, events=[])
        #         line = self._clear_line(match.end(), line)
        #
        #     day.events.append(
        #         Event(date=curr_date, address='', text=line)
        #     )
        #
        # if not journal.days:
        #     logger.warning(f'Journal is empty')

        return journal

    def _parse_notes(self, day: Day, data: Document):
        lines = [para.text for para in data.paragraphs]

        for line in lines:
            # fill person on duty
            if 'дежурный' in line:
                duty_person = line.split()[-2:]
                day.duty_person = ' '.join(duty_person)

            # fill date
            if re.match(r'.*[0-9]*\.[0-9]*\.[0-9]*', line) and 'На' not in line:
                day.date = line.split()[2]

        # fill notes
        day.notes = lines[-2].strip()
