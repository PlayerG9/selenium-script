# -*- coding=utf-8 -*-
r"""

"""
import re
import typing as t
from ..exceptions import ScriptMissingVariableError


__all__ = ['fill']


__RE_FILL = re.compile(r'\$(?:{(?P<extname>[^}]+?)}|(?P<name>\S+))', re.I)


def fill(string: str, context: t.Dict[str, t.Any]) -> str:
    def repl(match: re.Match) -> str:
        name = match.group("extname") or match.group("name")
        try:
            return str(context[name])
        except KeyError:
            raise ScriptMissingVariableError(name)

    return __RE_FILL.sub(repl=repl, string=string)
