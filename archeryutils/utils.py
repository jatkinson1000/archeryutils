"""Utility functions for printing version information."""

# This is not integral to the functioning of archeryutils and serves debugging purposes.
# For this reason exclude from tests and coverage checks with `  # pragma: no cover`.

import importlib
import locale
import os
import platform
import struct
import subprocess
import sys


def _get_sys_info() -> list:  # pragma: no cover
    """Return system information as a dict."""
    blob: list = []

    # get full commit hash
    commit = None
    if os.path.isdir(".git") and os.path.isdir("archeryutils"):
        with subprocess.Popen(
            ["/usr/bin/git", "log", '--format="%H"', "-n", "1"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ) as pipe:
            commit_raw, _ = pipe.communicate()
        commit = commit_raw.decode("utf-8").strip().strip('"')

    blob.append(("commit", commit))

    (sysname, _, release, _, machine, processor) = platform.uname()
    blob.extend(
        [
            ("python", sys.version),
            ("python-bits", struct.calcsize("P") * 8),
            ("OS", f"{sysname}"),
            ("OS-release", f"{release}"),
            ("machine", f"{machine}"),
            ("processor", f"{processor}"),
            ("byteorder", f"{sys.byteorder}"),
            ("LC_ALL", f"{os.environ.get('LC_ALL', 'None')}"),
            ("LANG", f"{os.environ.get('LANG', 'None')}"),
            ("LOCALE", f"{locale.getlocale()}"),
        ],
    )

    return blob


def versions() -> None:  # pragma: no cover
    """Print the versions of archeryutils and its dependencies to screen."""
    sys_info = _get_sys_info()

    deps = [
        # (MODULE_NAME, f(mod) -> mod version)
        ("archeryutils", lambda mod: mod.__version__),
        ("numpy", lambda mod: mod.__version__),
        # optionals
        # setup/lint/test
        ("setuptools", lambda mod: mod.__version__),
        ("pip", lambda mod: mod.__version__),
        ("coverage", lambda mod: mod.__version__),
        ("ruff", lambda mod: mod.__version__),
        ("pytest", lambda mod: mod.__version__),
        ("pytest_mock", lambda mod: importlib.metadata.version(mod.__name__)),
        ("mypy", lambda mod: importlib.metadata.version(mod.__name__)),
        # docs
        ("sphinx", lambda mod: mod.__version__),
        ("sphinx_rtd_theme", lambda mod: mod.__version__),
        ("sphinx_toolbox", lambda mod: mod.__version__),
        ("nbsphinx", lambda mod: mod.__version__),
        ("IPython", lambda mod: mod.__version__),
    ]

    deps_blob: list[tuple[str, str | None]] = []
    for modname, ver_f in deps:
        try:
            if modname in sys.modules:
                mod = sys.modules[modname]
            else:
                mod = importlib.import_module(modname)
        except ModuleNotFoundError:
            deps_blob.append((modname, None))
        else:
            try:
                ver = ver_f(mod)
                deps_blob.append((modname, ver))
            except AttributeError:
                deps_blob.append((modname, "installed"))

    print("\nSYSTEM INFORMATION")
    print("------------------")

    for k, stat in sys_info:
        print(f"{k}: {stat}")

    print("")
    print("\nINSTALLED VERSIONS")
    print("------------------")

    for k, stat in deps_blob:
        print(f"{k}: {stat}")
