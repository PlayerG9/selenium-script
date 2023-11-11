# selenium-script
selenium scripting engine

> currently still under development and probably full of errors

```bash
#!/usr/bin/env selection-script
################################################################################
# This script opens google.com and makes a "Lucky" search
################################################################################

INIT Chrome  # initialize a chrom instance
IMPLICITLY-WAIT 5s  # implicitly wait up to 5s while searching for an element
ACTION-DELAY 200ms - 400ms  # wait randomly 100ms-200ms between the actions
VISIT https://google.com/  # go to google

TAB 4  # Tab-Through to Reject-Cookies button (has no identifier to SELECT)
PRESS # Reject Cookies
WAIT-FOR 300ms  # wait 300ms
TAB 4  # Tab-Through to "Feeling Lucky" button (has no identifier to SELECT)
PRESS  # Start random search
WAIT-FOR 30s  # you can interact with the browser here
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
