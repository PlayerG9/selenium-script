#!/usr/bin/env selection-script
################################################################################
# This script opens google.com and makes a "Lucky" search
################################################################################

INIT Chrome  # initialize a chrome instance
IMPLICITLY-WAIT 5s  # implicitly wait up to 5s while searching for an element
ACTION-DELAY 200ms - 400ms  # wait randomly 200ms-400ms between the actions
VISIT https://google.com/  # go to google

TAB 4  # Tab-Through to Reject-Cookies button (has no identifier to SELECT)
PRESS # Reject Cookies
WAIT-FOR 300ms  # wait 300ms
TAB 4  # Tab-Through to "Feeling Lucky" button (has no identifier to SELECT)
PRESS  # Start random search
WAIT-FOR 30s  # you can interact with the browser here
QUIT  # close the Browser
