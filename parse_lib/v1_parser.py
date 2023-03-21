import json
import docx2txt
import re

from .default_parser import DefaultParser
from .models import Journal, Day, Event


class V1Parser(DefaultParser):
    DEFAULT_NAME = 'default_v1'

    def read_file(self, file_path: str) -> Journal:
        data = docx2txt.process(file_path)

        journal = Journal(name=self.DEFAULT_NAME, days=[])
        day = None
        curr_date = None

        for line in data.split('\n'):
            if journal.name == self.DEFAULT_NAME:
                journal.name = line
                continue

            if not line:
                continue

            # result = re.match(r'[0-9]*\.[0-9]*\.[0-9]*', line)
            regexp = re.compile(r'[0-9]*\.[0-9]*\.[0-9]*')
            match = regexp.search(line)

            if match:
                if day:
                    journal.days.append(day)

                curr_date = line.split(' ')[0].strip()
                day = Day(date=curr_date, events=[])
                line = line[match.end():].strip()

            day.events.append(
                Event(date=curr_date, address='', text=line)
            )

        return journal

    def check_is_header(self, text: str):
        result = re.match(r'Журнал [0-9]*', text)
        return True if result else False
