# -*- coding=utf-8 -*-
r"""


"""
import logging
import threading


logging_context_data = threading.local()


class LoggingContextFilter(logging.Filter):
    def filter(self, record):
        for key, value in vars(logging_context_data).items():
            setattr(record, key, value)
        return True


class LoggingContext:
    def __init__(self, **context):
        self.context = context

    def __enter__(self):
        for key, value in self.context.items():
            setattr(logging_context_data, key, value)

    def __exit__(self, exc_type, exc_val, exc_tb):
        for key in self.context.keys():
            delattr(logging_context_data, key)
