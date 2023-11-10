# -*- coding=utf-8 -*-
r"""

"""
import re
import typing as t
from ..exceptions import ScriptValueError


__all__ = ['parse', 'parse_string', 'parse_int', 'parse_number', 'parse_bool', 'PARSE_MAP']


__RE_INT = re.compile(r'(?P<digits>\d+)')
__RE_NUMBER = re.compile(r'(?P<number>\d*.\d+)')
__RE_BOOLEAN = re.compile(r'(?P<true>true|yes|on)|(?P<false>false|no|off)')


def parse(string: str) -> t.Any:
    int_match = __RE_INT.fullmatch(string)
    if int_match:
        return int(int_match.group('digits'))
    number_match = __RE_NUMBER.fullmatch(string)
    if number_match:
        return float(number_match.group('number'))
    boolean_match = __RE_BOOLEAN.fullmatch(string)
    if boolean_match:
        return boolean_match.group('true') is not None
    return parse_string(string)


def parse_string(string: str) -> str:
    return string


def parse_int(string: str) -> int:
    try:
        return int(string)
    except ValueError:
        raise ScriptValueError(f"Can't parse to integer {string!r}")


def parse_number(string: str) -> float:
    try:
        return float(string)
    except ValueError:
        raise ScriptValueError(f"Can't parse to number {string!r}")


def parse_bool(string: str) -> bool:
    string = string.lower()
    if string in {'true', 'yes', 'on', '1'}:
        return True
    elif string in {'false', 'no', 'off', '0'}:
        return False
    else:
        raise ScriptValueError(f"Can't parse to boolean {string!r}")


PARSE_MAP = {
    str: parse_string,
    int: parse_int,
    float: parse_number,
    bool: parse_bool,
    #
    t.Any: parse,
}
