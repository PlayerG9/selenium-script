# -*- coding=utf-8 -*-
r"""

"""


__all__ = ['format_action']


def format_action(action: str) -> str:
    return action.lower().replace("-", "_")
