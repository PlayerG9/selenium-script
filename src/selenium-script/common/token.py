# -*- coding=utf-8 -*-
r"""

"""
import typing as t


__all__ = ['Token']


class Token(t.NamedTuple):
    filename: str
    line_number: int
    action: str
    argline: str
