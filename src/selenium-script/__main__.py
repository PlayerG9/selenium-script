# -*- coding=utf-8 -*-
r"""

"""
import logging
import sys
import typing as t
import argparse as ap
from pathlib import Path
from . import (
    __version__ as interpreter_version,
    ScriptEngine,
    LoggingContextFilter,
)
from .exceptions import *


class Namespace:
    debug: bool
    logging: t.Literal["DEBUG", "INFO", "WARN", "WARNING", "ERROR", "CRITICAL"]
    script: Path


parser = ap.ArgumentParser(
    prog="selenium-script", description=__doc__, formatter_class=ap.ArgumentDefaultsHelpFormatter
)
parser.add_argument('-v', '--version', action="version", version=interpreter_version)
parser.add_argument('--logging',
                    choices=["DEBUG", "INFO", "WARN", "WARNING", "ERROR", "CRITICAL"],
                    help="how much information to output")
parser.add_argument('--debug', action=ap.BooleanOptionalAction,
                    help="run in debug mode (shows the browser)")
parser.add_argument('script', type=Path,
                    help="script to run")

args = parser.parse_args(namespace=Namespace())


def configure_logging():
    class LogRecordFactory(logging.LogRecord):
        def __init__(self, *a, **kw):
            super().__init__(*a, **kw)
            self.scriptLine = "---"

    logging.basicConfig(
        format="{asctime} | {levelname:.3} | {scriptLine:>3} | {name:>10} | {message}",
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

    with args.script.open() as script_file:
        script = script_file.read()

    engine = ScriptEngine(script, debug=args.debug)
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
