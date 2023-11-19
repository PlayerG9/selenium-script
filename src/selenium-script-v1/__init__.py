# -*- coding=utf-8 -*-
r"""

"""

__author__ = "PlayerG9"
__copyright__ = "Copyright 2023, PlayerG9"
__credits__ = ["PlayerG9"]
__license__ = None
__maintainer__ = "PlayerG9"
__email__ = None
__status__ = "Prototype"  # Prototype, Development, Production
__description__ = "selenium-script interpreter"
__version_info__ = (0, 1, 0)
__version__ = '.'.join(map(str, __version_info__))

from .exceptions import *
from .engine import ScriptEngine
from .logging_context import LoggingContextFilter
