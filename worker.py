import argparse
import logging
import time

from parse_lib.parsing.v1_parser import V1Parser
from parse_lib.parsing.v2_parser import V2Parser
from parse_lib.text_processor import TextProcessor

logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s :: %(asctime)s :: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('worker')

parser_mapping = {
    'v1': V1Parser,
    'v2': V2Parser,
}


def run_parsing(version: str, files_dir: str, file_path: str = ''):
    parser_class = parser_mapping.get(version)
    if parser_class is None:
        logger.warning(f'Parser with version {version} not exist')
        return

    logger.info(f'Start parsing with version {version}')

    parser = parser_class(files_dir=files_dir, file_path=file_path)
    parser.run()


def run_processing():
    """
    классифиировать обращения
    добавить тематуику обращений в таблицу событий, чтобы группировать по ним при запросе
    сделать скрипт, который считает количество упоминаний слов и пар слов
    """

    processor = TextProcessor()
    processor.run()


if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser(description='Cli interface for city journal parsing')
    cli_parser.add_argument("--parse")
    cli_parser.add_argument("--files_dir", default='journals/')
    cli_parser.add_argument("--file_path", default='')

    cli_parser.add_argument("--process", action='store_true')

    args = cli_parser.parse_args()

    start_time = time.time()
    if args.parse:
        run_parsing(args.parse, args.files_dir, args.file_path)

    if args.process:
        run_processing()
    end_time = time.time()
    execution_time = round(end_time - start_time, 3)

    logger.info(f'Time of execution: {execution_time}')
