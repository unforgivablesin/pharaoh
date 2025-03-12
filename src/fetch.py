import requests, random, tarfile, os, pathlib, shutil, subprocess
from pathlib import Path
import zstandard as zstd
from typing import Dict, Self
from clint.textui import progress

from src import ARCH, REPOS, EXPORT_DIRECTORY, APPLICATION_DIRECTORY
from src.config import ConfigBuilder
from src.permissions import Permissions, PermissionList, DBusPermissionList, DBusPermissions
from src.desktop import DesktopEntry, sandboxed_desktop_entry_factory


class Mirror:

    def __init__(self, url):
        self._url = url

    def __str__(self) -> str:
        return self._url

    def __repr__(self) -> str:
        return self._url

    @property
    def url(self) -> str:
        return self._url

    @classmethod
    def from_str(cls, value) -> Self:
        mirror = value.split("Server = ")[1].strip()
        mirror = mirror.replace("$arch", ARCH)

        return cls(url=mirror)


class Package:

    def __init__(self, name: str, filename: str, repo: str, arch: str,
                 depends: str) -> None:
        self._name = name
        self._filename = filename
        self._repo = repo
        self._arch = arch
        self._depends = depends

        self._entry = None

    def __repr__(self) -> str:
        return f"Package(name={repr(self._name)}, filename={repr(self._filename)}, repo={repr(self._repo)}, arch={repr(self._arch)})"

    @property
    def name(self) -> str:
        return self._name

    @property
    def entry(self) -> str:
        return self._entry

    @property
    def depends(self) -> str:
        return self._depends

    @property
    def filename(self) -> str:
        return self._filename

    @property
    def repo(self) -> str:
        return self._repo

    @classmethod
    def from_dict(cls, data) -> Dict[str, str]:
        return cls(name=data['pkgname'],
                   filename=data['filename'],
                   repo=data['repo'],
                   arch=data['arch'],
                   depends=data.get('depends'))


class PackageManager:

    def __init__(self) -> None:
        self._mirrors = self._fetch_mirrors()

    def install(self, package_name: str) -> None:
        app_dir = f"{APPLICATION_DIRECTORY}/{package_name}"
        package = self._find_package(package_name)

        self._download_package(package)
        self._package_package(package, app_dir)
        self._install_package(package, app_dir)

        for depend in package.depends:

            if self._is_installed(depend):
                continue

            package = self._find_package(depend)

            if package:
                print(f"Installing dependency {package.name}")

                self._download_package(package)
                self._package_package(package, app_dir)
                self._install_package(package, app_dir)

    def _install_package(self, package: Package, app_dir: str) -> None:
        entry = DesktopEntry.from_desktop_entry(
            f"{EXPORT_DIRECTORY}/applications/{package.entry}")
        permission_path = f"{app_dir}/{package.name}.json"

        executable = os.listdir(f"{app_dir}/usr/bin")[0]

        config = ConfigBuilder(
            app=package.name,
            executable=f"{app_dir}/usr/bin/{executable}",
            path=app_dir,
            entry=entry,
            dbus_app=f"org.Pharaoh.{package.name}",
            dbus_permissions=DBusPermissions(DBusPermissionList.Notifications),
            permissions=Permissions(PermissionList.Dri | PermissionList.Dbus
                                    | PermissionList.Ipc | PermissionList.Dbus
                                    | PermissionList.Pulseaudio
                                    | PermissionList.Pipewire))

        config.build(path=permission_path)

        sandboxed_desktop_entry_factory(package=package.name,
                                        entry_name=package.entry,
                                        script=f"pharaoh run {package.name}")

    def _package_package(self, package: Package, app_dir: str) -> None:
        os.makedirs(app_dir, exist_ok=True)
        self._decompress_package(package,
                                 app_dir=app_dir,
                                 export_dir=EXPORT_DIRECTORY)

    def _download_package(self, package: Package) -> None:
        mirror = random.choice(self._mirrors)
        repo = mirror.url.replace("$repo", package.repo)
        url = f"{repo}/{package.filename}"

        r = requests.get(url, stream=True)
        with open(package.filename, 'wb') as f:
            total_length = int(r.headers.get('content-length'))
            for chunk in progress.bar(r.iter_content(chunk_size=1024),
                                      expected_size=(total_length / 1024) + 1):
                if chunk:
                    f.write(chunk)
                    f.flush()

    def _decompress_package(self, package: Package, app_dir: str,
                            export_dir: str) -> None:
        input_file = pathlib.Path(package.filename)
        output_path = pathlib.Path(app_dir) / input_file.stem

        with open(input_file, 'rb') as compressed:
            decomp = zstd.ZstdDecompressor()
            with open(output_path, 'wb') as destination:
                decomp.copy_stream(compressed, destination)

        with tarfile.open(output_path, 'r') as tar:
            tar.extractall(path=app_dir)

        os.remove(input_file)
        os.remove(output_path)

        entry = os.listdir(f"{app_dir}/usr/share/applications")[0]
        package._entry = entry

        try:
            shutil.copytree(f"{app_dir}/usr/share",
                            export_dir,
                            dirs_exist_ok=True)
        except shutil.Error:
            pass

    def _fetch_mirrors(self) -> None:

        mirrors = []

        with open("/etc/pacman.d/mirrorlist") as fp:
            for mirror_str in fp:
                if "Server = " in mirror_str and not "#" in mirror_str:
                    mirrors.append(Mirror.from_str(mirror_str.strip()))

        return mirrors

    def _is_installed(self, package) -> bool:
        if ".so" in package:
            return True

        try:
            result = subprocess.check_output(['pacman', '-Qq', package
                                              ]).decode("utf-8").strip()
            return result == package
        except subprocess.CalledProcessError:
            return False

    def _find_package(self, package) -> None:
        for repo in REPOS:
            try:
                r = requests.get(
                    f"https://archlinux.org/packages/{repo}/x86_64/{package}/json/"
                ).json()
                return Package.from_dict(r)
            except requests.exceptions.JSONDecodeError:
                continue
