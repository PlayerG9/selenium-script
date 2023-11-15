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
from collections import namedtuple
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
# from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import *
from .exceptions import *
from .util import *
from .callutil import *
from .logging_context import LoggingContext


KEYS_CONTEXT = {
    f'@{name}': getattr(Keys, name)
    for name in dir(Keys)
    if name.isupper()
}
Token = namedtuple("Tokens", ('filename', 'line', 'action', 'arguments'))
MacroFunction = t.Callable[[t.TextIO, int, t.Tuple[str, ...]], t.Optional[t.List[Token]]]
ActionFunction = t.Callable[[t.Any, ...], None]


class ScriptEngine:
    _browser: t.Optional[BrowserType] = None
    _web_element: t.Optional[WebElement] = None
    delay_between_actions: t.Optional[t.Union[float, t.Tuple[float, float]]] = 0.0
    wait_for_timeout: float = 60

    debug_mode: bool
    source: str
    tokens: t.List[Token]
    context: t.Dict[str, t.Any]

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

    def compile(self, source: t.TextIO) -> t.List[Token]:
        tokens: t.List[Token] = []
        any_error = False

        for line_index, line in enumerate(source):
            line_number = line_index + 1
            line: str = line.strip()
            if not line or line.startswith("#"):
                continue
            action_raw, *args = shlex.split(line, comments=True)
            action_name = format_action(action_raw)

            if action_name.startswith("@"):
                macro_name = action_name.removeprefix("@")
                macro: MacroFunction = getattr(self, f'macro_{macro_name}')
                macro_tokens = macro(source, line_number, args)
                if macro_tokens is not None:
                    tokens.extend(macro_tokens)
                else:
                    any_error = True
                continue

            action: ActionFunction = getattr(self, f'action_{action_name}', None)
            if action is None:
                any_error = True
                logging.error(f"line {line_number}: unknown action {action_raw!r}")
                continue
            signature = inspect.signature(action)
            if (
                len(args) > len(signature.parameters)
                and not any(param.kind == param.VAR_POSITIONAL for param in signature.parameters.values())
            ):
                any_error = True
                logging.error(f"line {line_number}: too many parameters "
                              f"({action_name} {' '.join(signature.parameters.keys())})")
                continue
            # this transforms '\\n' to '\n'
            args = tuple(arg.encode('utf-8', 'replace').decode('unicode_escape') for arg in args)
            tokens.append(Token(os.path.basename(source.name), line_number, action_name, args))

        if any_error:
            logging.critical("Script failed during compilation")
            raise QuietExit(1)
        return tokens

    def macro_include(self, source: t.TextIO, line_number: int, args: t.Tuple[str, ...]) -> t.Optional[t.List[Token]]:
        tokens: t.List[Token] = []
        include_fp = os.path.join(os.path.dirname(source.name), *args)
        try:
            with open(include_fp) as included_script:
                tokens.extend(self.compile(included_script))
        except FileNotFoundError:
            logging.error(f"line {line_number}: script {include_fp!r} not found")
            return None
        except QuietExit:
            return None
        return tokens

    # ---------------------------------------------------------------------------------------------------------------- #

    def execute(self):
        try:
            for script_name, current_line, action_name, args in self.tokens:
                with LoggingContext(scriptName=script_name, scriptLine=current_line):
                    try:
                        self.call_action(action_name=action_name, arguments=args, context=self.context)
                    except ScriptRuntimeError as error:
                        logging.critical(f"{type(error).__name__}: {error}")
                        raise QuietExit(1)
                    except Exception as error:
                        logging.critical(f"Internal Error: {type(error).__name__} ({error})", exc_info=error)
                        raise QuietExit(1)
                self.wait_action_delay()
        except BaseException as exception:
            if self.debug_mode:
                import traceback
                traceback.print_exception(type(exception), exception, exception.__traceback__)
            raise exception
        finally:
            if self._browser is not None:
                logging.warning("Abnormally quitting the browser")
                self._browser.quit()

    def call_action(self, action_name: str, arguments: t.Tuple[str, ...], context: t.Dict[str, t.Any]):
        function = getattr(self, f'action_{action_name}')
        filled_arguments = [fill(arg, context=context) for arg in arguments]
        call_function_with_arguments(function=function, arguments=filled_arguments)

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

    def action_default(self, name: str, *parts: str):
        r"""sets the variable if not exists"""
        value = ' '.join(parts)
        self.context.setdefault(name, value)

    def action_set(self, name: str, *parts: str):
        r"""set a variable"""
        value = ' '.join(parts)
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

    def action_select(self, query: str, *extra: str):
        r"""select an element"""
        query = ' '.join((query,) + extra)
        self._web_element = self.browser.find_element(by=By.CSS_SELECTOR, value=query)

    def action_waiting_select(self, query: str, *extra: str):
        r"""Like SELECT but waits for the element"""
        query = ' '.join((query,) + extra)
        self._web_element = WebDriverWait(self.browser, timeout=self.wait_for_timeout).until(
            expected_conditions.presence_of_element_located((By.CSS_SELECTOR, query))
        )

    def action_select_name(self, name: str):
        r"""SELECT '[name="value"]'"""
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
        r"""used for debugging and only with the --debug flag"""
        if self.debug_mode:
            logging.debug("Breakpoint")
            input("Press return to continue.")

    def action_wait_for_user_interrupt(self):
        r"""
        waits for the browser to close or for ctrl+c in the terminal

        *useful if the script make a browser-setup for the user
        """
        logging.info("press `ctrl+c` to continue")
        try:
            for _ in range(60*60):  # 1h max
                time.sleep(1)
                try:
                    self.browser.current_window_handle  # noqa
                except WebDriverException:
                    raise KeyboardInterrupt("Window got closed")
        except KeyboardInterrupt:
            pass

    action_wait_for_user = action_wait_for_user_interrupt

    @staticmethod
    def action_sleep(*deltas: str):
        r"""
        just wait for a bit

        SLEEP 200ms
        SLEEP 200ms - 400ms

        time units are:
        - ms - milliseconds
        - s  - seconds
        - m  - minutes
        - h  - hours (why the hell would you need that? but I don't care)
        """
        line = ''.join(deltas)
        if line.count('-') == 1:
            minimum, maximum = map(parse_timedelta, line.split('-', 1))
            total = random.uniform(minimum.total_seconds(), maximum.total_seconds())
        else:
            total = parse_timedelta(line).total_seconds()
        logging.info(f"Sleeping for {total:.3}s")
        time.sleep(total)

    def action_wait_till(self, what: str, query: str = None):
        r"""
        WAIT-TILL ALERT
        WAIT-TILL NEW-WINDOW
        WAIT-TILL CLICKABLE
        WAIT-TILL VISIBLE
        WAIT-TILL VISIBILITY
        WAIT-TILL INVISIBILITY
        WAIT-TILL URL-CHANGE
        WAIT-TILL URL https://something.com/
        WAIT-TILL URL-TO-BE https://something.com/
        WAIT-TILL INTERACTIVE
        WAIT-TILL PAGE-INTERACTIVE
        WAIT-TILL LOADED
        WAIT-TILL PAGE-LOADED
        """
        web_element = (By.CSS_SELECTOR, query) if query else self.web_element

        timeout_message = shlex.join(("WAIT-TILL", what.upper(), query))

        negate = False
        if what.startswith("!"):
            negate = True
            what = what[2:]

        condition = dict(
            element=expected_conditions.presence_of_element_located(web_element),
            alert=expected_conditions.alert_is_present(),
            new_window=expected_conditions.new_window_is_opened(self.browser.window_handles),
            clickable=expected_conditions.element_to_be_clickable(web_element),
            visible=expected_conditions.visibility_of(web_element),
            visibility=expected_conditions.visibility_of(web_element),
            invisibility=expected_conditions.invisibility_of_element(web_element),
            url_change=expected_conditions.url_changes(self.browser.current_url),
            url=expected_conditions.url_to_be(query),
            url_to_be=expected_conditions.url_to_be(query),
            interactive=lambda driver: driver.execute_script("return document.readyState") == "interactive",
            page_interactive=lambda driver: driver.execute_script("return document.readyState") == "interactive",
            loaded=lambda driver: driver.execute_script("return document.readyState") == "complete",
            page_loaded=lambda driver: driver.execute_script("return document.readyState") == "complete",
        )[what.lower().replace('-', '_')]

        wait = WebDriverWait(self.browser, timeout=self.wait_for_timeout)
        if negate:
            wait.until_not(condition, message=timeout_message)
        else:
            wait.until(condition, message=timeout_message)

    def action_action_delay(self, *parts: str):
        r"""
        sets the delay between actions

        - ACTION-DELAY OFF
        - ACTION-DELAY RANDOM
        - ACTION-DELAY 100ms
        - ACTION-DELAY 100ms - 200ms
        """
        if len(parts) == 1:
            first = parts[0].lower()
            if first == "off":
                self.delay_between_actions = None
                return
            elif first == "random":
                self.delay_between_actions = (0.2, 1)  # between 0.2 and 1.0 second
                return

        joined = ''.join(parts)

        if joined.count('-') == 1:
            minimum, maximum = map(parse_timedelta, joined.split('-', 1))
            self.delay_between_actions = (minimum.total_seconds(), maximum.total_seconds())
        else:
            self.delay_between_actions = parse_timedelta(joined).total_seconds()

    def action_page_load_timeout(self, *deltas: str):
        r"""
        set the page-load-timeout.

        should only be called once
        """
        self.browser.set_page_load_timeout(parse_timedelta(''.join(deltas)).total_seconds())

    def action_implicitly_wait(self, *deltas: str):
        r"""
        set the implicit wait time when selecting an element

        should only be called once
        """
        self.browser.implicitly_wait(parse_timedelta(''.join(deltas)).total_seconds())

    def action_wait_for_timeout(self, *deltas: str):
        self.wait_for_timeout = parse_timedelta(''.join(deltas)).total_seconds()

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
