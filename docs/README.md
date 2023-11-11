# Documentation

## "Hello World" Script

```bash
INFO "Hello World"
```
```
XXXX-XX-XX XX:XX:XX,XXX | INF |   1 | 'Hello World'
```

## "Hello World" with a variable

```bash
SET NAME "World"
INFO "Hello $NAME"
```
```
XXXX-XX-XX XX:XX:XX,XXX | INF |   2 | 'Hello World'
```

## Doing something with a browser

```bash
INIT Chrome  # could also be Firefox, Safari or Edge
# stuff is possible here
QUIT  # always run QUIT at the end to remove the warning
```

## Proper minimal script

```bash
#!/usr/bin/env selenium-script
# ^ adding a shebang to make the script executable ^
################################################################################
# This is the header section. Here you can write details about the script
################################################################################
LOAD config  # load the dotenv-file `config`
DEFAULT VAR Value

# initialize a browser (headless is common to prevent user interaction)
INIT Chrome --headless
# set the implicitly-wait time as the PC or Internet could be slow
IMPLICITLY-WAIT 5s
# (optionally) enable random action delay to make it more like a human
#ACTION-DELAY RANDOM
#ACTION-DELAY 200ms - 400ms

VISIT https://website.net/resource
# Script content here

QUIT  # properly QUIT the browser 
```
