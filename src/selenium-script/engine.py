# -*- coding=utf-8 -*-
r"""

"""
import os
import time
import shlex
import random
import inspect
import logging
import typing as t
import datetime as dt
from dotenv import dotenv_values
from selenium.webdriver import (
    Keys,
    Chrome as ChromeBrowser,
    ChromeOptions,
    Firefox as FirefoxBrowser,
    FirefoxOptions,
    Edge as EdgeBrowser,
    EdgeOptions,
    Safari as SafariBrowser,
    SafariOptions,
    Remote as BrowserType,
)
from selenium.webdriver.remote.webelement import WebElement, By
from selenium.common.exceptions import *
from .exceptions import *
from .util import *
from .logging_context import LoggingContext


KEYS_CONTEXT = {
    f'@{name}': getattr(Keys, name)
    for name in dir(Keys)
    if name.isupper()
}


class ScriptEngine:
    _browser: t.Optional[BrowserType] = None
    _web_element: t.Optional[WebElement] = None
    delay_between_actions: t.Optional[t.Union[float, t.Tuple[float, float]]] = 0.0

    def __init__(self, source: str, *, debug: bool = False, context: t.Dict[str, t.Any] = None):
        self.debug_mode = debug
        self.source = source
        with open(source) as source_file:
            self.tokens = self.compile(source_file)
        self.context = dict()
        self.context.update(KEYS_CONTEXT)
        self.context.update(os.environ)
        if context:
            self.context.update(context)

    # ---------------------------------------------------------------------------------------------------------------- #

    def compile(self, source: t.TextIO) -> t.List:
        tokens = []
        any_error = False

        for line_index, line in enumerate(source):
            line: str = line.strip()
            if not line or line.startswith("#"):
                continue
            action_raw, *args = shlex.split(line, comments=True)
            action = format_action(action_raw)
            function = getattr(self, f'action_{action}', None)
            if function is None:
                any_error = True
                logging.error(f"line {line_index + 1}: unknown action {action_raw!r}")
                continue
            signature = inspect.signature(function)
            if (
                len(args) > len(signature.parameters)
                and not any(param.kind == param.VAR_POSITIONAL for param in signature.parameters.values())
            ):
                any_error = True
                logging.error(f"line {line_index + 1}: too many parameters "
                              f"({action} {' '.join(signature.parameters.keys())})")
                continue
            # this transforms '\\n' to '\n'
            args = tuple(arg.encode('utf-8', 'replace').decode('unicode_escape') for arg in args)
            tokens.append((line_index + 1, action, args))

        if any_error:
            logging.critical("Script failed during compilation")
            raise QuietExit(1)
        return tokens

    # ---------------------------------------------------------------------------------------------------------------- #

    def execute(self):
        try:
            for line, action, args in self.tokens:
                with LoggingContext(scriptLine=line):
                    try:
                        self.call_action(action=action, arguments=args, context=self.context)
                    except ScriptRuntimeError as error:
                        logging.critical(f"{type(error).__name__}: {error}")
                        raise QuietExit(1)
                    except Exception as error:
                        logging.critical(f"Internal Error: {type(error).__name__} ({error})", exc_info=error)
                        raise QuietExit(1)
                self.wait_action_delay()
        finally:
            if self._browser is not None:
                logging.warning("Abnormally quitting the browser")
                self._browser.quit()

    def call_action(self, action: str, arguments: t.Tuple[str, ...], context: t.Dict[str, t.Any]):
        function = getattr(self, f'action_{action}')
        args = []

        signature = inspect.signature(function)

        for index, parameter in enumerate(signature.parameters.values()):
            parameter: inspect.Parameter
            if parameter.annotation == parameter.empty:
                parser = parse_string
            else:
                parser = PARSE_MAP[parameter.annotation]
            if parameter.kind == parameter.VAR_POSITIONAL:
                raws = arguments[index:]
                values = [fill(raw, context=context) for raw in raws]
                args.extend(map(parser, values))
                break
            else:
                raw = arguments[index]
                value = fill(raw, context=context)
                args.append(parser(value))

        return function(*args)

    def wait_action_delay(self):
        if self.delay_between_actions is None:
            return

        if isinstance(self.delay_between_actions, (tuple, list)):
            time.sleep(random.uniform(*self.delay_between_actions))
        else:
            time.sleep(self.delay_between_actions)

    # ---------------------------------------------------------------------------------------------------------------- #

    @property
    def browser(self) -> BrowserType:
        if self._browser is None:
            raise ScriptRuntimeError("you need to run `INIT browser` to initialize the browser")
        return self._browser

    @property
    def web_element(self) -> WebElement:
        if self._web_element is not None:
            return self._web_element
        return self.browser.switch_to.active_element

    ####################################################################################################################
    # Actions
    ####################################################################################################################

    # ---------------------------------------------------------------------------------------------------------------- #

    @staticmethod
    def action_debug(*args: str):
        r"""give the user some feedback"""
        logging.debug(repr(" ".join(args)))

    @staticmethod
    def action_info(*args: str):
        r"""give the user some feedback"""
        logging.info(repr(" ".join(args)))

    @staticmethod
    def action_warning(*args: str):
        r"""give the user some feedback"""
        logging.warning(repr(" ".join(args)))

    action_warn = action_warning

    @staticmethod
    def action_error(*args: str):
        r"""give the user some feedback"""
        logging.error(repr(" ".join(args)))

    # ---------------------------------------------------------------------------------------------------------------- #

    def action_default(self, name: str, value: str):
        r"""sets the variable if not exists"""
        self.context.setdefault(name, value)

    def action_set(self, name: str, value: str):
        r"""set a variable"""
        self.context[name] = value

    def action_load(self, path: str):
        r"""loads a dotenv file"""
        filepath = os.path.join(os.path.dirname(self.source), path)
        if not os.path.isfile(filepath):
            raise ScriptRuntimeError(f"Missing dotenv file: {filepath!r}")
        logging.info(f"Loading: {filepath!r}")
        self.context.update(dotenv_values(filepath))

    # ---------------------------------------------------------------------------------------------------------------- #

    def action_init(self, browser: str, *arguments: str):
        r"""
        initialize the browser

        INIT Firefox --headless

        possible browser options are
        - chrome
        - firefox
        - safari
        - edge

        common arguments could be:
        --headless
        """
        logging.info(f"Initializing {browser!r} browser "
                     f"with {' '.join(map(repr, arguments)) if arguments else 'no arguments'}")
        browsers = dict(
            chrome=(ChromeBrowser, ChromeOptions),
            firefox=(FirefoxBrowser, FirefoxOptions),
            safari=(SafariBrowser, SafariOptions),
            edge=(EdgeBrowser, EdgeOptions),
        )
        try:
            browser_class, options_class = browsers[browser.lower()]
            browser_class: t.Type[ChromeBrowser]
            options_class: t.Type[ChromeOptions]
        except KeyError:
            raise ScriptValueError(f"unknown browser {browser!r} ({'|'.join(browsers.keys())})")
        options = options_class()
        for argument in arguments:
            options.add_argument(argument)
        self._browser = browser_class(
            options=options,
        )

    def action_close(self):
        r"""close the current window"""
        logging.info("Closing the current window")
        self.browser.close()

    def action_quit(self):
        r"""quit the current browser (session)"""
        logging.info("Quitting the browser")
        self.browser.quit()
        self._browser = None

    def action_visit(self, url: str):
        r"""visit a certain url"""
        logging.info(f"Visiting {url!r}")
        self.browser.get(url)

    # ---------------------------------------------------------------------------------------------------------------- #

    def action_select(self, *query: str):
        r"""select an element"""
        if not query:
            self.action_unselect()
        else:
            self._web_element = self.browser.find_element(by=By.CSS_SELECTOR, value=' '.join(query))

    def action_select_name(self, name: str):
        self._web_element = self.browser.find_element(by=By.NAME, value=name)

    def action_select_xpath(self, xpath: str):
        r"""select element by xpath"""
        self._web_element = self.browser.find_element(by=By.XPATH, value=xpath)

    def action_select_link_text(self, *text: str):
        r"""Select link that contains text"""
        self._web_element.find_element(by=By.LINK_TEXT, value=' '.join(text))

    def action_select_link_partial_text(self, *text: str):
        r"""select link that contains partially text"""
        self._web_element.find_element(by=By.PARTIAL_LINK_TEXT, value=' '.join(text))

    def action_unselect(self):
        r"""unselect the current element"""
        self._web_element = None

    def select_child(self, *query: str):
        r"""select a child element"""
        if not query:
            raise ScriptSyntaxError("Missing query selector for SELECT-CHILD")
        self._web_element = self.web_element.find_element(by=By.CSS_SELECTOR, value=' '.join(query))

    # ---------------------------------------------------------------------------------------------------------------- #

    def action_type(self, *keys: str):
        r"""type some keys"""
        self.web_element.send_keys(*keys)

    def action_hotkey(self, *keys: str):
        r"""
        trigger a hotkey event

        - TYPE @CONTROL @SHIFT p
        - HOTKEY CONTROL SHIFT p
        """
        # maybe switch to ActionChains
        self.web_element.send_keys(*(getattr(Keys, key.upper(), key.lower()) for key in keys))

    def action_return(self):
        r"""type @RETURN"""
        self.web_element.send_keys(Keys.RETURN)

    def action_space(self):
        r"""type @SPACE"""
        self.web_element.send_keys(Keys.SPACE)

    def action_backspace(self, times: int = 1):
        r"""type @BACKSPACE x times"""
        for i in range(times):
            if i > 0:
                self.wait_action_delay()
            self.web_element.send_keys(Keys.BACKSPACE)

    action_back_space = action_backspace

    def action_tab(self, times: int = 1):
        r"""type @TAB x times"""
        for i in range(times):
            if i > 0:
                self.wait_action_delay()
            self.web_element.send_keys(Keys.TAB)

    def action_escape(self):
        r"""type @ESCAPE"""
        self.web_element.send_keys(Keys.ESCAPE)

    # ---------------------------------------------------------------------------------------------------------------- #

    def action_breakpoint(self):
        if self.debug_mode:
            logging.debug("Breakpoint")
            input("Press return to continue.")

    @staticmethod
    def action_wait_for(*deltas: dt.timedelta):
        r"""
        wait for x time

        WAIT-FOR 1s 500ms

        time units are:
        - ms - milliseconds
        - s  - seconds
        - m  - minutes
        - h  - hours (why the hell would you need that? but I don't care)
        """
        total = sum(delta.total_seconds() for delta in deltas)
        logging.info(f"Sleeping for {total}s")
        time.sleep(total)

    action_wait = action_wait_for

    def action_action_delay(self, *delays: t.Any):
        r"""
        sets the delay between actions

        - ACTION-DELAY OFF
        - ACTION-DELAY RANDOM
        - ACTION-DELAY 100ms
        - ACTION-DELAY 100ms - 200ms
        """
        if not all(isinstance(delay, (dt.timedelta, str)) for delay in delays):
            raise ScriptValueError("ACTION-DELTA takes only timedelta")

        n_params = len(delays)
        dash_index = delays.index('-') if '-' in delays else -1

        if n_params == 1 and isinstance(delays[0], str) and delays[0].lower() == "off":  # ACTION-DELTA OFF
            self.delay_between_actions = None
        elif n_params == 1 and isinstance(delays[0], str) and delays[0].lower() == "random":  # ACTION-DELTA RANDOM
            self.delay_between_actions = (0.2, 1)  # between 0.2 and 1.0 second
        elif not any(isinstance(delay, str) for delay in delays):  # ACTION-DELTA 000ms
            self.delay_between_actions = sum(delay.total_seconds() for delay in delays)
        elif delays.count('-') == 1 and 0 < dash_index < n_params:  # ACTION-DELTA 000ms - 000ms
            middle = delays.index('-')
            a = sum(delay.total_seconds() for delay in delays[:middle])
            b = sum(delay.total_seconds() for delay in delays[middle+1:])
            self.delay_between_actions = (min(a, b), max(a, b))
        else:
            raise ScriptSyntaxError("Couldn't understand the ACTION-DELAY")

    def action_page_load_timeout(self, *deltas: dt.timedelta):
        r"""
        set the page-load-timeout.

        should only be called once
        """
        total = sum(delta.total_seconds() for delta in deltas)
        self.browser.set_page_load_timeout(total)

    def action_implicitly_wait(self, *deltas: dt.timedelta):
        r"""
        set the implicit wait time when selecting an element

        should only be called once
        """
        total = sum(delta.total_seconds() for delta in deltas)
        self.browser.implicitly_wait(total)

    # ---------------------------------------------------------------------------------------------------------------- #

    def action_refresh(self):
        r"""refresh the current page"""
        logging.info("Refreshing the Page")
        self.browser.refresh()

    def action_forward(self):
        r"""go forwards on page"""
        logging.debug("Going one step forward in the browser history")
        self.browser.forward()

    def action_back(self):
        r"""go backwards on page"""
        logging.debug("Going one step backward in the browser history")
        self.browser.back()

    # ---------------------------------------------------------------------------------------------------------------- #

    def action_click(self, *query: str):
        r"""clicks the current element"""
        if query:
            logging.debug(f"CLICK {' '.join(query)!r}")
            web_element = self.browser.find_element(by=By.CSS_SELECTOR, value=' '.join(query))
        else:
            web_element = self.web_element
        web_element.click()

    action_press = action_click
