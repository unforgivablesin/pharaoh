from os import makedirs, environ
from pathlib import Path

ARCH = "x86_64"
REPOS = ["core", "extra"]

APPLICATION_DIRECTORY = "/var/lib/pharaoh/app/"
EXPORT_DIRECTORY = "/var/lib/pharaoh/export/"
APPLICATION_HOME_DIRECTORY = f"/home/{environ['SUDO_USER']}/.var/app" if environ.get('SUDO_USER') else Path("~/.var/app").expanduser()

try:
    makedirs(APPLICATION_DIRECTORY, exist_ok=True)
    makedirs(EXPORT_DIRECTORY, exist_ok=True)
except PermissionError:
    pass
