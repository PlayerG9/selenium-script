# -*- coding=utf-8 -*-
r"""

"""
import logging
import argparse as ap
from pathlib import Path
from . import __version__ as interpreter_version


parser = ap.ArgumentParser(
    prog="selenium-script", description=__doc__, formatter_class=ap.ArgumentDefaultsHelpFormatter
)
parser.add_argument('-v', '--version', action="version", version=interpreter_version)
parser.add_argument('--logging',
                    choices=['DEBUG', 'INFO', 'WARN', 'WARNING', 'ERROR', 'CRITICAL'],
                    help="how much information to output")
parser.add_argument('--debug', action=ap.BooleanOptionalAction,
                    help="run in debug mode (shows the browser)")
parser.add_argument('script', type=Path,
                    help="script to run")

args = parser.parse_args()


def configure_logging():
    class FallbackFilter(logging.Filter):
        def filter(self, record):
            if not hasattr(record, "scriptLine"):
                record.scriptLine = "---"
            return True

    logging.basicConfig(
        format="{asctime} | {levelname:.3} | {scriptLine:>3} | {message}",
        # format="{asctime} | {levelname:.3} | {module:>15}.{funcName:<20} | {lineno:3} | {message}",
        style="{",
        level=args.logging or (logging.DEBUG if args.debug else logging.INFO),
    )
    # logging.root.addFilter(logging.Filter("__main__"))
    logging.root.addFilter(FallbackFilter())


def main():
    configure_logging()
    logging.debug(str(vars(args)))


if __name__ == '__main__':
    main()
