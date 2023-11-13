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
WAIT-TILL PAGE-LOADED  # should be clear what it does
INFO "You can now play with the page"  # print an info message
WAIT-FOR-USER-INTERRUPT  # you can interact with the browser here
QUIT  # close the Browser
