# -*- coding=utf-8 -*-
r"""

"""
import typing as t
import inspect
from ..util import *


__all__ = ['call_function_with_arguments']


def call_function_with_arguments(function: t.Callable, arguments: t.List[str]):
    args = []
    signature = inspect.signature(function)

    for index, parameter in enumerate(signature.parameters.values()):
        parameter: inspect.Parameter
        if parameter.annotation == parameter.empty:
            parser = parse_string
        else:
            parser = PARSE_MAP[parameter.annotation]
        if parameter.kind == parameter.VAR_POSITIONAL:
            values = arguments[index:]
            args.extend(map(parser, values))
            break
        else:
            try:
                value = arguments[index]
            except IndexError as error:
                if parameter.default is parameter.empty:
                    raise error
            else:
                args.append(parser(value))

    return function(*args)
