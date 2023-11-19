# -*- coding=utf-8 -*-
r"""

"""
import os
import io
import typing as t
from ..common import Token


__all__ = ['Compiler']


class Compiler:
    def compile(self, source: t.Union[str, os.PathLike, t.TextIO]) -> t.List[Token]:
        if isinstance(source, (str, os.PathLike)):
            with open(source, 'r') as source_file:
                source = io.StringIO(source_file.read())
        tokens = []

        #

        return tokens

    # ---------------------------------------------------------------------------------------------------------------- #
