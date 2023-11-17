# -*- coding=utf-8 -*-
r"""

"""
import typing as t


__all__ = ['split_list']


def split_list(arguments: t.List[str]) -> t.Tuple[t.List[str], t.Dict[str, str]]:
    args = []
    kwargs = {}

    last_key = None

    for argument in arguments:
        if argument.startswith('--'):
            if last_key:
                kwargs[last_key] = True
            last_key = argument[2:]
        else:
            if last_key:
                kwargs[last_key] = argument
                last_key = None
            else:
                args.append(argument)

    if last_key:
        kwargs[last_key] = True

    return args, kwargs
