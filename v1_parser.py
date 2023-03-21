import docx2txt
import re

from default_parser import DefaultParser
from models import Journal, Day, Event


class V1Parser(DefaultParser):
    def read_file(self, file_path: str) -> Journal:
        data = docx2txt.process(file_path)
        events = {}

        curr_date = '123'
        for line in data.split('\n'):
            result = re.match(r'[0-9]*\.[0-9]*\.[0-9]*', line)
            if result:
                curr_date = line.split(' ')[0].strip()

            events[curr_date] = events.get(curr_date, '') + line

        return Journal(name='default', days=[])
