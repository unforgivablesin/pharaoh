import os
from typing import Self

from src import EXPORT_DIRECTORY


class DesktopEntry:

    def __init__(self, filename: str, name: str, exec: str, type: str,
                 icon: str, terminal: str, generic_name: str,
                 start_notify: str, wm_class: str, mime_type: str,
                 categories: str, actions: str, keywords: str,
                 comment: str) -> None:

        self._filename = filename
        self._entry = os.path.basename(filename)
        self._name = name
        self._type = type
        self._exec = exec
        self._icon = icon
        self._terminal = terminal
        self._generic_name = generic_name
        self._start_notify = start_notify
        self._wm_class = wm_class
        self._mime_type = mime_type
        self._categories = categories
        self._actions = actions
        self._keywords = keywords
        self._comment = comment

        self._no_display = False
        self._sandboxed = False

    def __str__(self) -> str:
        return self._filename

    @property
    def name(self) -> str:
        return self._name

    def set_sandbox_name(self) -> None:
        self._name = f"Sandboxed-{self.name}"
        self._sandboxed = True

    def set_exec(self, command: str) -> None:
        self._exec = command

    def set_no_display(self) -> None:
        self._no_display = True

    def add_category(self, category: str) -> None:
        self._categories += category + ";"

    def create_entry(self, entry_name: str) -> None:
        data = "[Desktop Entry]\n"
        data += "Name=" + self._name + "\n" if self._name else ""
        data += "Exec=" + self._exec + "\n" if self._exec else ""
        data += "Type=" + self._type + "\n" if self._type else ""
        data += "Icon=" + self._icon + "\n" if self._icon else ""
        data += "Terminal=" + self._terminal + "\n" if self._terminal else ""
        data += "GenericName=" + self._generic_name + "\n" if self._generic_name else ""
        data += "StartupNotify=" + self._start_notify + "\n" if self._start_notify else ""
        data += "StartupWMClass=" + self._wm_class + "\n" if self._wm_class else ""
        data += "MimeType=" + self._mime_type + "\n" if self._mime_type else ""
        data += "Categories=" + self._categories + "\n" if self._categories else ""
        data += "Actions=" + self._actions + "\n" if self._actions else ""
        data += "Keywords=" + self._keywords + "\n" if self._keywords else ""

        if self._no_display:
            data += "NoDisplay=true"

        filename = f"{EXPORT_DIRECTORY}/applications/{entry_name}"

        with open(filename, "w") as fp:
            fp.write(data)

    @classmethod
    def from_desktop_entry(cls, filename: str) -> Self:

        data = open(filename, "r").read()

        def get_key_value(key: str) -> str:
            for line in data:
                if line[:len(key) + 1] == key + '=':
                    result = line.split(key + "=")
                    return result[1].split("\n")[0]

        name = get_key_value("Name")
        exec = get_key_value("Exec")
        type = get_key_value("Type")
        icon = get_key_value("Icon")
        terminal = get_key_value("Terminal")
        comment = get_key_value("Comment")
        generic_name = get_key_value("GenericName")
        start_notify = get_key_value("StartupNotify")
        wm_class = get_key_value("StartupWMClass")
        mime_type = get_key_value("MimeType")
        categories = get_key_value("Categories")
        actions = get_key_value("Actions")
        keywords = get_key_value("Keywords")

        return cls(filename=filename,
                   name=name,
                   exec=exec,
                   type=type,
                   icon=icon,
                   terminal=terminal,
                   comment=comment,
                   generic_name=generic_name,
                   start_notify=start_notify,
                   wm_class=wm_class,
                   mime_type=mime_type,
                   categories=categories,
                   actions=actions,
                   keywords=keywords)


def sandboxed_desktop_entry_factory(package: str, entry_name: str,
                                    script: str) -> DesktopEntry:
    entry = DesktopEntry.from_desktop_entry(
        filename=f"{EXPORT_DIRECTORY}/applications/{entry_name}")

    #entry.add_category("Sandboxed")
    entry.set_exec(script)
    entry.set_sandbox_name()

    entry.create_entry(entry_name=entry_name)
    #entry.create_symlink()

    return entry
