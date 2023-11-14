# Actions

## Logging/Console-output

```bash
DEBUG [message...]
INFO [message...]
WARN/WARNING [message...]
ERROR [message...]
CRITICAL [message...]
# prints a message to the console
```

## Variables

```bash
DEFAULT <name> [value...]
# create the variable `name` with `value` if it doesn't exist
```
```bash
SET <name> [value...]
# create or override the variable `name` with `value`
```
```bash
LOAD <dotenv-file>
# load variables from a dotenv file
```

## Controlling the Browser

```bash
INIT {Chrome|Firefox|Safari|Edge} [--cmd-arguments...]
# initialize the browser windows
# hint: start with --headless to hide it
```
```bash
CLOSE
# close the current window
```
```bash
QUIT
# quit the browser
```
```bash
VISIT <url>
# go to a certain url
```

## Selecting a certain element

## Sending input

## Debugging and Waiting

## Controlling the current page

```bash
REFRESH
# refresh the current page
```
```bash
FORWARD
# goes one step forward in the browser history
```
```bash
BACK
# goes one step backward in the browser history
```

## Element actions

```bash
CLICK [element]
PRESS [element]
# presses the passed (`element`) or `SELECTED` web-element
```
