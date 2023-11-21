# -*- coding=utf-8 -*-
r"""

"""
import typing as t
import inspect
from .splitlist import split_list
from .parsing import PARSE_MAP, parse_any


__all__ = ['call_function_with_arguments']


def call_function_with_arguments(function: t.Callable, arguments: t.List[str]):
    raw_args, raw_kwargs = split_list(arguments)
    args, kwargs = [], {}

    signature = inspect.signature(function)

    for index, parameter in enumerate(signature.parameters.values()):
        parameter: inspect.Parameter

        if parameter.annotation == parameter.empty:
            parser = parse_any
        else:
            parser = PARSE_MAP[parameter.annotation]

        if parameter.kind in {parameter.POSITIONAL_ONLY, parameter.POSITIONAL_OR_KEYWORD}:  # everything at the start
            args.append(parser(raw_args[index]))
        elif parameter.kind == parameter.VAR_POSITIONAL:  # *args
            args.extend(map(parser, raw_args[index:]))
        elif parameter.kind == parameter.KEYWORD_ONLY:  # after *args or *
            kwargs[parameter.name] = parser(raw_kwargs[parameter.name])
        elif parameter.kind == parameter.VAR_KEYWORD:  # **kwargs
            kwargs.update({
                key: parser(raw_kwargs[key])
                for key in (set(raw_kwargs) - set(kwargs))
            })

    try:
        bound = signature.bind(*args, **kwargs)
    except TypeError as error:
        raise SyntaxError("Bad parameter") from error
    return function(*bound.args, **bound.kwargs)
