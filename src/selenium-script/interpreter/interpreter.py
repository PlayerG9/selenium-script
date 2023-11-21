# -*- coding=utf-8 -*-
r"""

"""
import io
import os
import re
import typing as t


class Interpreter:
    def execute(self, source: t.Union[str, os.PathLike, t.TextIO]):
        if isinstance(source, (str, os.PathLike)):
            with open(source, 'r') as script_file:
                source = io.StringIO(script_file.read())

        for i, line in enumerate(source):
            # removing comments
            line: str = re.sub(r"#.*$", '', line.strip())
            if not line:
                continue
            print(line)
