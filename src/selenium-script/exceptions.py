# -*- coding=utf-8 -*-
r"""

"""


__all__ = [
    'QuietExit',
    'SeleniumScriptError',
    'ScriptCompileError',
    'ScriptSyntaxError', 'ScriptUnknownActionError',
    'ScriptRuntimeError',
    'ScriptUnknownVariableError', 'ScriptTypeError', 'ScriptValueParsingError',
]


# -------------------------------------------------------------------------------------------------------------------- #


class QuietExit(BaseException):
    def __init__(self, return_code: int):
        self.return_code = return_code


class SeleniumScriptError(Exception):
    pass


# -------------------------------------------------------------------------------------------------------------------- #


class ScriptCompileError(SeleniumScriptError):
    pass


class ScriptUnknownActionError(ScriptCompileError):
    pass


# -------------------------------------------------------------------------------------------------------------------- #


class ScriptRuntimeError(SeleniumScriptError):
    pass


class ScriptSyntaxError(ScriptRuntimeError):
    pass


class ScriptTypeError(ScriptRuntimeError):
    pass


class ScriptValueParsingError(ScriptRuntimeError):
    pass


class ScriptUnknownVariableError(ScriptRuntimeError):
    pass
