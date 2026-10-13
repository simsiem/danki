*****
Danki
*****

Spend less time memorizing, more time enjoying.

Danki streamlines vocabulary learning: it directly support your homework for vocabulary and text, personalizes
your repetition schema to you, and makes you successful with less effort.

**Table of Contents**

- [Installation](#installation)
- [License](#license)


Installation
============

```console
pip install danki
```


Development
===========

Changeset verification
----------------------

Run

```bash
hatch check --fix
hatch test
```

to verify your changes follow coding guidelines and avoid regressions.

Pre-commit hook
---------------

The pre-commit hook runs ``hatch check`` and blocks commits unless it passes. To activate the repository's
hook for this clone, run:

```console
git config --local core.hooksPath .githooks
```

This is a one-time setup for each clone. Hatch must be installed and available on ``PATH``. If the check
fails, run ``hatch check --fix`` to apply automatic fixes, then commit again.

For an emergency commit only, Git's ``--no-verify`` option bypasses the hook. Run ``hatch check`` afterward.


Anki Desktop add-on
===================

Build the standalone add-on into a directory under Anki's ``addons21`` directory for each Anki Desktop
installation, then restart Anki:

```console
python scripts/build_anki_addon.py /path/to/addons21/danki_in_text_help
```

Headless UI smoke test
----------------------

Use the dedicated Hatch environment to run the real Qt workflow in offscreen mode without pulling the
heavyweight runtime into ordinary lightweight test runs:

```console
hatch run ui:test --maxfail=1 -q
```

This environment uses ``pytest-anki2==2.2.0`` and Anki/AQT ``26.9.3`` with ``QT_QPA_PLATFORM=offscreen``.
The ``aqt[qt69]`` extra pins a matched Python Qt stack: PyQt6 6.9.1, Qt core 6.9.1,
PyQt6-WebEngine 6.9.0, Qt WebEngine 6.9.0, and PyQt6-sip 13.12.0. Hatch installs these;
do not install separate system Qt bindings.

The runtime also requires host-side libraries, including ALSA, NSPR/NSS, and X11/XCB.
On Ubuntu 24.04, install them via:

```console
sudo apt-get install libasound2t64 libnspr4 libnss3 libxkbcommon-x11-0 libxcb-cursor0 libxcb-icccm4 \
  libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-shape0 \
  libxcb-xinerama0 libxcb-xkb1 libx11-xcb1 libdbus-1-3 libglib2.0-0 libxrender1 libxext6
```

On distributions predating the time64 package transition, the ALSA package is named ``libasound2``
instead of ``libasound2t64``. After changing the dependency configuration, rerun the Hatch command;
Hatch synchronizes the UI environment automatically.

Validated on Ubuntu 24.04.3 x86_64 with CPython 3.12.3 on 2026-10-10 using the exact Qt versions
above. The smoke scenario builds the standalone bundle, installs it before Anki's normal add-on
loader runs, and checks that runtime modules come from that installed bundle. It seeds a temporary
collection, uses the actual menu, deck picker, text list, and navigation buttons, and verifies that
reopening the text in the same session resumes its saved sentence.

The suite lives in ``ui_tests/`` and executes ``docs/features/anki-ui/feat-installed-text-reading.feature``.
Ordinary ``hatch test`` runs only ``tests/`` and neither imports nor skips the UI suite. Additional
arguments to ``ui:test`` never remove the UI-suite path.

pytest-anki2 2.2.0 replaces Anki's initializer with one that omits the target release's startup hook.
The local session fixture retains pytest-anki2's isolated profile management but restores Anki's real
initializer and installs the bundle before its normal ``setupAddons`` method. No add-on workflow or
startup hook is called manually. Because the upstream session context skips teardown when an exception
crosses its yield, the fixture explicitly closes it normally in a finalizer while preserving test failures.
It unloads the collection, waits for backups, drains deferred Qt deletion, and checks removal of the base
directory on success and failure.

A warm run measured 0.83 seconds in pytest and 2.30 seconds wall time including Hatch startup
(dependency installation excluded). An intentionally incorrect text-selection expectation failed explicitly
in 0.91 seconds and still completed teardown without a crash. UI waits are bounded to 10 seconds.
The test covers reopening within one session, not import dialogs or restarting Anki.

This project intentionally leaves the ordinary dev and hatch-test environments lightweight while the UI
environment remains opt-in.


License
=======

Copyright (C) 2026–present Simon Siemens

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General
Public License as published by the Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see
<https://www.gnu.org/licenses/>. 
