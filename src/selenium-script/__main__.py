# -*- coding=utf-8 -*-
r"""

"""
import sys
import logging
import typing as t
import os.path as p
import argparse as ap
import better_exceptions
from . import (
    __version__ as interpreter_version,
)
from .exceptions import *


class Namespace:
    def __repr__(self):
        return f"<{vars(self)}>"

    debug: bool
    logging: t.Literal["DEBUG", "INFO", "WARN", "WARNING", "ERROR", "CRITICAL"]
    script: str


parser = ap.ArgumentParser(
    prog="selenium-script", description=__doc__, formatter_class=ap.ArgumentDefaultsHelpFormatter
)
parser.add_argument('-v', '--version', action="version", version=interpreter_version)
parser.add_argument('--logging',
                    choices=["DEBUG", "INFO", "WARN", "WARNING", "ERROR", "CRITICAL"],
                    help="how much information to output")
parser.add_argument('--debug', action=ap.BooleanOptionalAction,
                    help="run in debug mode (shows the browser)")
parser.add_argument('script', type=p.abspath,
                    help="script to run")

args = parser.parse_args(namespace=Namespace())


def configure_logging():
    class LogRecordFactory(logging.LogRecord):
        def __init__(self, *a, **kw):
            super().__init__(*a, **kw)
            self.scriptLine = "---"
            self.scriptName = "<unknown>"

    logging.basicConfig(
        format="{asctime} | {levelname:.3} | {scriptName:>15} | {scriptLine:>3} | {message}",
        style="{",
        level=args.logging or (logging.DEBUG if args.debug else logging.INFO),
    )
    logging.setLogRecordFactory(LogRecordFactory)
    for handler in logging.root.handlers:
        if not args.debug:  # disable logging of other modules if not in debug-mode
            handler.addFilter(logging.Filter(name="root"))
        # handler.addFilter(LoggingContextFilter())
    better_exceptions.log.patch()


def main():
    better_exceptions.hook()
    configure_logging()
    logging.debug(str(args))

    logging.critical("NotImplementedError")

    return 1


if __name__ == '__main__':
    try:
        sys.exit(main() or 0)
    except QuietExit as exc:
        sys.exit(exc.return_code)
