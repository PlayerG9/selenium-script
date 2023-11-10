# -*- coding=utf-8 -*-
r"""

"""


__all__ = [
    'QuietExit',
    'SeleniumScriptError',
    'ScriptCompileError',
    'ScriptSyntaxError', 'ScriptUnsupportedTokenError',
    'ScriptRuntimeError',
    'ScriptValueError', 'ScriptMissingVariableError',
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


class ScriptSyntaxError(ScriptCompileError):
    pass


class ScriptUnsupportedTokenError(ScriptCompileError):
    pass


# -------------------------------------------------------------------------------------------------------------------- #


class ScriptRuntimeError(SeleniumScriptError):
    pass


class ScriptValueError(ScriptRuntimeError):
    pass


class ScriptMissingVariableError(ScriptRuntimeError):
    pass
