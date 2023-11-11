# -*- coding=utf-8 -*-
r"""

"""
import re
import typing as t
from ..exceptions import ScriptMissingVariableError


__all__ = ['fill']


__RE_CONTEXT = re.compile(
    # ${VAR}|$VAR|@KEY (note: ${@KEY} is also possible)
    r'\$\{([^}]+?)}|\$(\S+)|(@\S+)',
    re.I
)


def fill(string: str, context: t.Dict[str, t.Any]) -> str:
    def repl(match: re.Match) -> str:
        name = match.group(match.lastindex)
        try:
            value = context[name]
        except KeyError:
            raise ScriptMissingVariableError(name)
        else:
            return "" if value is None else str(value)

    return __RE_CONTEXT.sub(repl=repl, string=string)
