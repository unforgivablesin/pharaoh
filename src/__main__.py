import sys, os, shutil
from pathlib import Path

from src import APPLICATION_DIRECTORY, APPLICATION_HOME_DIRECTORY
from src.fetch import PackageManager
from src.config import Config
from src.launch import SandboxLauncher


def install_app():

    if os.geteuid() != 0:
        print("You must be root")
        sys.exit(1)

    try:
        app = sys.argv[2]
        print(f"Installing \x1b[91m{app}\x1b[0m!")

        package_manager = PackageManager()
        package_manager.install(app)
    except IndexError:
        print("Please specify an application to install")


def remove_app():

    if os.geteuid() != 0:
        print("You must be root")
        sys.exit(1)

    try:
        app = sys.argv[2]
        print(f"Removing \x1b[91m{app}\x1b[0m!")
        shutil.rmtree(f"{APPLICATION_DIRECTORY}/{app}")
        shutil.rmtree(f"{APPLICATION_HOME_DIRECTORY}/{app}")
    except IndexError:
        print("Please specify an application to remove")


def sandbox_launcher(application: str) -> None:
    config_file_path = f"{APPLICATION_DIRECTORY}/{application}/{application}.json"
    config = Config.from_config(config_file_path)

    SandboxLauncher(executable=config.executable,
                    app=config.app,
                    path=config.path,
                    permissions=config.permissions,
                    seccomp_filter=config.seccomp_filter,
                    dbus_app=config.dbus_app,
                    dbus_permissions=config.dbus_permissions).launch()


if len(sys.argv) < 2:
    print("You must specify an action")
    sys.exit(1)

action = sys.argv[1]

match action:
    case "install":
        install_app()
    case "run":
        print("Running app!")
        sandbox_launcher(sys.argv[2])
    case "remove":
        remove_app()
