import json
from typing import Self, Optional

from src.permissions import Permissions, DBusPermissions
from src.desktop import DesktopEntry


class Config:

    def __init__(self,
                 app: str,
                 path: str,
                 icon: str,
                 executable: str,
                 entry: str,
                 permissions: Permissions,
                 seccomp_filter: Optional[str] = None,
                 dbus_app: Optional[str] = None,
                 dbus_permissions: Optional[DBusPermissions] = None) -> None:
        self.app = app
        self.path = path
        self.icon = icon
        self.executable = executable
        self.permissions = permissions
        self.seccomp_filter = seccomp_filter
        self.entry = entry

        self.dbus_app = dbus_app
        self.dbus_permissions = dbus_permissions

    @classmethod
    def from_config(cls, config: str) -> Self:
        data = json.load(open(config))

        return cls(app=data['app'],
                   path=data['path'],
                   icon=data['icon'],
                   executable=data['executable'],
                   entry=data['entry'],
                   permissions=Permissions.from_dict(data['permissions']),
                   seccomp_filter=data['seccomp_filter'],
                   dbus_app=data['dbus_app'],
                   dbus_permissions=DBusPermissions.from_dict(
                       data['dbus_permissions']))


class ConfigBuilder:

    def __init__(self,
                 app: str,
                 executable: str,
                 path: str,
                 entry: DesktopEntry,
                 permissions: Permissions,
                 seccomp_filter: Optional[str] = None,
                 dbus_app: Optional[str] = None,
                 dbus_permissions: DBusPermissions = None) -> None:
        self.app = app
        self.executable = executable
        self.path = path
        self.entry = entry
        self.permissions = permissions
        self.seccomp_filter = seccomp_filter

        self.dbus_app = dbus_app
        self.dbus_permissions = dbus_permissions or DBusPermissions(0)

    def build(self, path) -> None:

        data = {
            "app": self.app,
            "path": self.path,
            "icon": self.entry._icon,
            "executable": self.executable,
            "entry": self.entry._entry,
            "permissions": self.permissions.permissions,
            "seccomp_filter": self.seccomp_filter,
            "dbus_app": self.dbus_app,
            "dbus_permissions": self.dbus_permissions.permissions
        }

        with open(path, "w") as fp:
            fp.write(json.dumps(data, indent=4))
