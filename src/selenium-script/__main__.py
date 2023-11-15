# -*- coding=utf-8 -*-
r"""

"""
import sys
import logging
import typing as t
import os.path as p
import argparse as ap
from . import (
    __version__ as interpreter_version,
    ScriptEngine,
    LoggingContextFilter,
)
from .exceptions import *


class Namespace:
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
        handler.addFilter(LoggingContextFilter())


def main():
    configure_logging()
    logging.debug(str(vars(args)))

    engine = ScriptEngine(args.script, debug=args.debug)
    try:
        engine.execute()
    except ScriptRuntimeError as error:
        logging.critical(f"{type(error).__name__}: {error}")
        return 1
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main() or 0)
    except QuietExit as exc:
        sys.exit(exc.return_code)
