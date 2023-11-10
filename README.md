# selenium-script
selenium scripting engine

> currently still under development and not really expected to run at all

```bash
#!/usr/bin/env selection-script
# This is a comment
LOAD .env  # load variables from the .env file
VISIT https://google.com/  # go to google
FOCUS input#query  # select the query input
TYPE $QUERY  # type whats in the $QUERY variable
RETURN  # start the search
```
