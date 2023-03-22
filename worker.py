import argparse
import logging
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


def run_parsing(version: str, files_dir: str):
    parser_class = parser_mapping.get(version)
    if parser_class is None:
        logger.warning(f'Parser with version {version} not exist')
        return

    logger.info(f'Start parsing with version {version}')

    parser = parser_class(files_dir=files_dir)
    parser.run()


if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser(description='Cli interface for city journal parsing')
    cli_parser.add_argument("--parse")
    cli_parser.add_argument("--files_dir", default='journals/')

    args = cli_parser.parse_args()

    if args.parse:
        run_parsing(args.parse, args.files_dir)
