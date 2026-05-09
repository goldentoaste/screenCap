
## Build commands


### Windows
* One file upx
nuitka .\screencap\debug\test.py --onefile --onefile-no-compression --enable-plugin=pyside6 --noinclude-dlls=qt6pdf.* --noinclude-dlls=qt6network.*  --nofollow-import-to=PySide6.QtNetwork --python-flag=no_docstrings --python-flag=no_asserts --show-modules --show-modules-output=included_modules.txt --mingw64 --lto=yes  --plugin-enable=upx --upx-binary=D:\Projects\screenCap\upx.exe

* onefile, not upx
nuitka .\screencap\debug\test.py --onefile --enable-plugin=pyside6 --noinclude-dlls=qt6pdf.* --noinclude-dlls=qt6network.*  --nofollow-import-to=PySide6.QtNetwork --python-flag=no_docstrings --python-flag=no_asserts --show-modules --show-modules-output=included_modules.txt --mingw64 --lto=yes

* standalone, no upx
nuitka .\screencap\debug\test.py --standalone --enable-plugin=pyside6 --noinclude-dlls=qt6pdf.* --noinclude-dlls=qt6network.*  --nofollow-import-to=PySide6.QtNetwork --python-flag=no_docstrings --python-flag=no_asserts --show-modules --show-modules-output=included_modules.txt --mingw64 --lto=yes

* standalone, upx
nuitka .\screencap\debug\test.py --standalone --enable-plugin=pyside6 --noinclude-dlls=qt6pdf.* --noinclude-dlls=qt6network.*  --nofollow-import-to=PySide6.QtNetwork --python-flag=no_docstrings --python-flag=no_asserts --show-modules --show-modules-output=included_modules.txt --mingw64 --lto=yes --plugin-enable=upx --upx-binary=D:\Projects\screenCap\upx.exe

* UXP might be worth for standalone (~70mb to 40mb), one file 18mb to 16mb, noticeable start up time.



### Linux (KDE)
nuitka ./screencap/debug/testLinux.py --standalone --enable-plugin=pyside6  --nofollow-import-to=PySide6.QtNetwork --nofollow-import-to=PySide6.QtPdf --python-flag=no_docstrings --python-flag=no_asserts


## Windows
MinGW64 is needed, use "--mingw64" flag

## Linux
* `libxcb-cursor-dev` is needed for xcb (x11 mode), may or may not already be present. Or may not be needed for prod.
* `sudo apt install libclang-dev` is needed for Qt6
* `sudo apt install qt6-base-dev` for Qt6
* `sudo apt install libqt6core6 `
* If poetry appears to be broken, use `poetry config keyring.enabled false`
	+ use -v flag to confirm issue is keyring related

