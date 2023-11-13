# selenium-script

interpreter for the selenium-scripting-language.

Write a script that controls your browser.

> warning: currently still under development and probably full of errors

## Example

`examples/feeling-lucky.ss`
```bash
#!/usr/bin/env selection-script
################################################################################
# This script opens google.com and makes a "Lucky" search
################################################################################

INIT Chrome  # initialize a chrome instance
IMPLICITLY-WAIT 5s  # implicitly wait up to 5s while searching for an element
ACTION-DELAY 200ms - 400ms  # wait randomly 200ms-400ms between the actions
VISIT https://google.com/  # go to google
WAIT-TILL PAGE-LOADED  # ensure page is fully loaded

TAB 4  # Tab-Through to Reject-Cookies button (has no identifier to SELECT)
PRESS # Reject Cookies
WAIT-TILL PAGE-LOADED  # after rejecting the page reloads
TAB 4  # Tab-Through to "Feeling Lucky" button (has no identifier to SELECT)
PRESS  # Start random search
SLEEP 30s  # you can interact with the browser here
QUIT  # close the Browser
```

## Quick-Start

```bash
git clone https://github.com/PlayerG9/selenium-script.git
cd selenium-script/
python3 -m venv .venv
.venv/bin/pip3 install -r requirements.txt
chmod +x ./selenium-script
./selenium-script examples/hello-world.ss
```

or see the [other examples](./examples) or the [documentation](./docs)
