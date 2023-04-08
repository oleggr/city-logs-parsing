import argparse
import logging
import time

from parse_lib.v1_parser import V1Parser
from parse_lib.v2_parser import V2Parser


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


if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser(description='Cli interface for city journal parsing')
    cli_parser.add_argument("--parse")
    cli_parser.add_argument("--files_dir", default='journals/')
    cli_parser.add_argument("--file_path", default='')

    args = cli_parser.parse_args()

    start_time = time.time()
    if args.parse:
        run_parsing(args.parse, args.files_dir, args.file_path)
    end_time = time.time()
    execution_time = round(end_time - start_time, 3)

    logger.info(f'Time of execution: {execution_time}')
