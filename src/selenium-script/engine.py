# -*- coding=utf-8 -*-
r"""

"""
import io
import os
import shlex
import inspect
import logging
import typing as t
from .exceptions import *
from .util import *
from .logging_context import LoggingContext


class ScriptEngine:
    def __init__(self, source: t.Union[str, t.TextIO], *, context: t.Dict[str, t.Any] = None):
        if isinstance(source, str):
            source = io.StringIO(source)
        self.tokens = self.compile(source)
        self.context = dict()
        self.context.update(os.environ)
        if context:
            self.context.update(context)

    def compile(self, source: t.TextIO) -> t.List:
        tokens = []
        any_error = False

        for line_index, line in enumerate(source):
            line: str = line.strip()
            if not line or line.startswith("#"):
                continue
            action_raw, *args = shlex.split(line, comments=True)
            action = format_action(action_raw)
            function = getattr(self, f'action_{action}', None)
            if function is None:
                any_error = True
                logging.error(f"line {line_index + 1}: unknown action {action_raw!r}")
                continue
            signature = inspect.signature(function)
            if (
                len(args) > len(signature.parameters)
                and not any(param.kind == param.VAR_POSITIONAL for param in signature.parameters.values())
            ):
                any_error = True
                logging.error(f"line {line_index + 1}: too many parameters "
                              f"({action} {' '.join(signature.parameters.keys())})")
                continue
            tokens.append((line_index + 1, action, args))

        if any_error:
            logging.critical("Script failed during compilation")
            raise QuietExit(1)
        return tokens

    def execute(self):
        for line, action, args in self.tokens:
            with LoggingContext(scriptLine=line):
                self.call_action(action=action, arguments=args, context=self.context)

    def call_action(self, action: str, arguments: t.Tuple[str, ...], context: t.Dict[str, t.Any]):
        function = getattr(self, f'action_{action}')
        args = []

        signature = inspect.signature(function)

        for index, parameter in enumerate(signature.parameters.values()):
            parameter: inspect.Parameter
            if parameter.annotation == parameter.empty:
                parser = parse_string
            else:
                parser = PARSE_MAP[parameter.annotation]
            if parameter.kind == parameter.VAR_POSITIONAL:
                raws = arguments[index:]
                values = [fill(raw, context=context) for raw in raws]
                args.extend(map(parser, values))
                break
            else:
                raw = arguments[index]
                value = fill(raw, context=context)
                args.append(parser(value))

        return function(*args)

    ####################################################################################################################
    # Actions
    ####################################################################################################################

    # ---------------------------------------------------------------------------------------------------------------- #

    @staticmethod
    def action_debug(*args: str):
        logging.debug(" ".join(args))

    @staticmethod
    def action_info(*args: str):
        logging.info(" ".join(args))

    @staticmethod
    def action_warning(*args: str):
        logging.warning(" ".join(args))

    action_warn = action_warning

    @staticmethod
    def action_error(*args: str):
        logging.error(" ".join(args))

    # ---------------------------------------------------------------------------------------------------------------- #

    def action_default(self, name: str, value: str):
        self.context.setdefault(name, value)

    def action_set(self, name: str, value: str):
        self.context[name] = value
