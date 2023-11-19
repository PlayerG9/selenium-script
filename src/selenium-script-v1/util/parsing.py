# -*- coding=utf-8 -*-
r"""

"""
import re
import typing as t
import datetime as dt
from ..exceptions import ScriptValueError


__all__ = [
    'parse',
    'parse_string', 'parse_int', 'parse_number', 'parse_bool', 'parse_timedelta',
    'PARSE_MAP',
]


def filtertrue(iterable: t.Iterable) -> t.Iterable:
    return (e for e in iterable if e)


UNIT2FACTOR: t.Dict[str, float] = dict(
    ms=1/1000,
    s=1,
    m=60,
    h=60*60,
)

__RE_INT = re.compile(r'(?P<digits>\d+)')
__RE_NUMBER = re.compile(r'(?P<number>\d*.\d+)')
__RE_BOOLEAN = re.compile(r'(?P<true>true|yes|on)|(?P<false>false|no|off)')
__RE_TIMEDELTA = re.compile(rf'(?:(?:\d+|\d*.\d+)(?:{"|".join(UNIT2FACTOR.keys())}))+')
__RE_TIMEDELTA_SPLIT = re.compile(rf'((?:\d+|\d*.\d+)(?:{"|".join(UNIT2FACTOR.keys())}))')
__RE_SINGLE_TIMEDELTA = re.compile(rf'(?P<amount>\d+|\d*.\d+)(?P<unit>(?:{"|".join(UNIT2FACTOR.keys())}))')


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
    timedelta_match = __RE_TIMEDELTA.fullmatch(string)
    if timedelta_match:
        parts = filtertrue(__RE_TIMEDELTA_SPLIT.split(string))
        return dt.timedelta(seconds=sum(
            float(match.group("amount")) * UNIT2FACTOR[match.group("unit")]
            for match in map(__RE_SINGLE_TIMEDELTA.fullmatch, parts)
        ))
    return parse_string(string)


def parse_string(string: str) -> str:
    return string


def parse_int(string: str) -> int:
    try:
        return int(string)
    except ValueError:
        raise ScriptValueError(f"Can't parse to integer: {string!r}")


def parse_number(string: str) -> float:
    try:
        return float(string)
    except ValueError:
        raise ScriptValueError(f"Can't parse to number: {string!r}")


def parse_bool(string: str) -> bool:
    string = string.lower()
    if string in {'true', 'yes', 'on', '1'}:
        return True
    elif string in {'false', 'no', 'off', '0'}:
        return False
    else:
        raise ScriptValueError(f"Can't parse to boolean: {string!r}")


def parse_timedelta(string: str) -> dt.timedelta:
    timedelta_match = __RE_TIMEDELTA.fullmatch(string)
    if timedelta_match is None:
        raise ScriptValueError(f"Can't parse to timedelta: {string!r}")
    parts = filtertrue(__RE_TIMEDELTA_SPLIT.split(string))
    return dt.timedelta(seconds=sum(
        float(match.group("amount")) * UNIT2FACTOR[match.group("unit")]
        for match in map(__RE_SINGLE_TIMEDELTA.fullmatch, parts)
    ))


PARSE_MAP: t.Dict[t.Type, t.Callable[[str], t.Any]] = {
    str: parse_string,
    int: parse_int,
    float: parse_number,
    bool: parse_bool,
    dt.timedelta: parse_timedelta,
    #
    t.Any: parse,
}
