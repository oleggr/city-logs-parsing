import json
import logging
import typing

from parse_lib.db_controller import DbController
from parse_lib.models import EventFromDb


logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s :: %(asctime)s :: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('text_processor')


class TextProcessor:
    result_file_name = 'result.txt'

    def __init__(self):
        self.db = DbController()
        self.words_counter = {}

    @property
    def counted_words_json(self):
        return json.dumps(self.words_counter, indent=2, ensure_ascii=False)

    @property
    def sorted_words_counter(self):
        return sorted(self.words_counter.items(), key=lambda x: x[1], reverse=True)

    def get_events(self):
        events: typing.List[EventFromDb] = []

        rows = self.db.read_events()
        for row in rows:
            events.append(EventFromDb(
                id=row[0],
                date=row[1],
                text=row[3],
                address=row[2],
                datetime=row[4],
                organization=row[5],
                injured_fio=row[6],
                version=row[7],
                journal_id=row[8],
                created_at=row[9],
            ))

        return events

    def run(self):
        """Handle all events and count words inside"""
        events = self.get_events()

        for i, event in enumerate(events):
            words = event.text.lower().split()

            for word in words:
                if len(word) > 2:
                    self.words_counter[word] = self.words_counter.get(word, 0) + 1

        # print(self.counted_words_json)
        for elem in self.sorted_words_counter:
            print(elem)

        self.write_processing_result()
        logger.info(f'Total words: {len(self.words_counter.keys())}')

    def write_processing_result(self):
        f = open(self.result_file_name, 'a')
        for elem in self.sorted_words_counter:
            f.write(f'\'{elem[0]}\': {elem[1]}\n')
        f.close()
