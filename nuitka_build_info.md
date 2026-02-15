
## Build commands


### Windows
nuitka .\screencap\debug\test.py --standalone --enable-plugin=pyside6 --noinclude-dlls=qt6pdf.* --noinclude-dlls=qt6network.*  --nofollow-import-to=PySide6.QtNetwork --python-flag=no_docstrings --python-flag=no_asserts --show-modules --show-modules-output=included_modules.txt --mingw64


### Linux (KDE)
nuitka ./screencap/debug/testLinux.py --standalone --enable-plugin=pyside6  --nofollow-import-to=PySide6.QtNetwork --nofollow-import-to=PySide6.QtPdf --python-flag=no_docstrings --python-flag=no_asserts


## Windows
MinGW64 is needed, use "--mingw64" flag

## Linux
* `sudo apt install libclang-dev` is needed for Qt6
* `sudo apt install qt6-base-dev` for Qt6
* `sudo apt install libqt6core6 `
* If poetry appears to be broken, use `poetry config keyring.enabled false`
	+ use -v flag to confirm issue is keyring related

