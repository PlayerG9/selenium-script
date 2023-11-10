# Tutorial

## Setup

To run these examples you have to clone this repository
```bash
git clone https://github.com/PlayerG9/selenium-script.git
```

### Installation with _pipenv_
```bash
cd selenium-script/
PIPENV_VENV_IN_PROJECT=1 pipenv install
```

### Installation with _venv_ and _pip_
```bash
cd selenium-script/
python3 -m venv .venv
.venv/bin/pip3 install -r requirements.txt
```

### Run examples

```bash
# maybe: chmod +x ./selenium-script
./selenium-script examples/{name}
```

```bash
./selenium-script examples/hello-world.ss
NAME="Selenium" ./selenium-script examples/hello-world.ss
```
