from docx import Document
import logging
import re

from .default_parser import DefaultParser
from .models import Journal, Day, Event, MCHSDep, TouristGroups, FireDep, PoliceDep, Weather


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

        journal = Journal(
            name=file_path.split('/')[-1],
            days=[],
            version=self.VERSION
        )
        day = Day(date='', events=[], weather=[])

        self._parse_notes(day, journal, word_doc)

        # tables_mapping = {
        #     0: None,
        #     1: 'events',
        #     2: 'fire',
        #     3: 'police',
        #     4: 'mchs',
        #     5: 'temp',
        # }
        curr_table = 0

        # data = docx2txt.process(file_path)
        for table in word_doc.tables:
            for i, row in enumerate(table.rows):
                text = tuple(cell.text for cell in row.cells)

                # detect table in file
                if i == 0 and text[0] == '№ п/п':
                    curr_table = 1
                elif i == 0 and 'Пожарная' in text[0]:
                    curr_table = 2
                elif i == 0 and 'Полиция' in text[0]:
                    curr_table = 3
                elif i == 0 and 'МЧС' in text[0]:
                    curr_table = 4
                elif i == 0 and 'температура' in text[2]:
                    curr_table = 5

                # resolve event from table
                if i >= 1 and curr_table == 1:
                    datetime = [i.strip() for i in text[1].split('\n')]

                    day.events.append(Event(
                        date=day.date,
                        text=text[4].strip(),
                        address='',
                        datetime=' '.join(datetime),
                        organization=text[2].strip(),
                        injured_fio=text[3].strip(),
                    ))

                # resolve FireDep data from table
                if i == 1 and curr_table == 2:
                    day.fire_dep = FireDep(
                        fires_num=int(text[1]),
                        dead=int(text[3]),
                        injured=int(text[4]),
                    )

                # resolve PoliceDep data from table
                if i == 1 and curr_table == 3:
                    day.police_dep = PoliceDep(
                        incidents_num=text[1].strip(),
                        notes=text[2].strip(),
                    )

                # resolve MCHS data from table
                if i == 2 and curr_table == 4:
                    day.mchs_dep = MCHSDep(
                        tourist_groups=TouristGroups(
                            num=text[1].strip(),
                            persons=text[2].strip(),
                        ),
                        dtp=text[3].strip(),
                        search_jobs=text[4].strip(),
                        save_jobs=text[5].strip(),
                        another=text[6].strip(),
                    )

                # resolve MCHS data from table
                if i >= 1 and curr_table == 5:
                    day.weather.append(Weather(
                        place=text[1].strip(),
                        external_temp=text[2].strip(),
                        in_out_tube_temp=text[3].strip(),
                        in_out_tube_pressure=text[4].strip(),
                    ))

        journal.days.append(day)

        return journal

    def _parse_notes(self, day: Day, journal: Journal, data: Document):
        lines = [para.text for para in data.paragraphs]

        for line in lines:
            # fill person on duty
            if 'дежурный' in line:
                duty_person = line.split()[-2:]
                journal.duty_person = ' '.join(duty_person)

            # fill date
            if re.match(r'.*[0-9]*\.[0-9]*\.[0-9]*', line) and 'На' not in line:
                day.date = line.split()[2]

        # fill notes
        journal.notes = lines[-2].strip()
