# screenCap

A Windows(only) program made in python with the intention to replicate a old Japanese program named 'SETUNA', which lacks an English translation and has minor graphics compatibilities issues with modern systems. This program allows you to take screenshots, crop a section of it, and pin it to be always on top, along with many other features for productivity gains.

Here is a [modernized](https://github.com/tylearymf/SETUNA2) version of SETUNA, but it is not in English.(And I rather write my own program instead of translating this one :P)

#
![example](https://i.imgur.com/3e8YwWm.png)


# Features
* Set custom global keyboard shortcut to create a snapshot , snapshots are always on top, borderless, and is not displayed as a proper window(so your task bar wouldn't be cluttered).

* Multiple monitor support. Screen capturing occurs at the monitor the mouse pointer is currently at.

* A 'Recycle Bin' feature to bring back recently closed snapshots

* For each snapshot:
  * Right click to bring up context menu
  * Select 'Crop' to further crop snapshot
  * Select 'Recycle Bin' to open the Recycle Bin menu :v
  * Crtl+C: copy image to clip
  * Ctrl+X: copy and close the selected snapshot
  * Ctrl+V: create a snapshot from image in clipboard
  * Ctrl+S: save image(brings up a save file window)
  * plus or minus key to enlarge or shrink image
  * Double click to minimize the snapshot to save screen space

* Option to start program on system startup.

* Option to minimize program to system tray

# Dependencies

* Pillow, for image processing
* desktopmagic, for advance screen capturing
* pywin32, for interaction with Windows
  * Note: win32ui have issues with python3.9, see this [page](https://github.com/mhammond/pywin32/issues/1593) for a .whl pack to fix this.

* tendo, for tendo.singleton that ensures only 1 instance of the program is running.
  * Note: tendo might not import correctly in recent python versions. ```os.environ["PBR_VERSION"] = "4.0.2"``` is needed before the [import](https://blog.csdn.net/wzh200x/article/details/111185209). 

* pynput, for keyboard handling
  * pynput is a pretty feature rich module, supports both mouse and keyboard handlings. However it is not very intuitive to work with(need some work arounds for non trivial usages)
* infi.systray, for system tray icon
  * Note: infi.systray is not well supported for python3, using the fix mentioned [here](https://github.com/Infinidat/infi.systray/issues/32) is recommended. Also, pystray have better features and is better supported than infi.systray. However pystray can only run the main thread, so everything freezes when the icon starts. Thus infi.systray is used for this project.

* configparser, to handling .ini config

* pythoncom, ctypes, for handling admin permissions

* pyinstaller, to pack the project to exe(the .spec file is included in the project).
  * Note: pynput, tendo, desktopmagic and infi.systray have hiddenimports that needs to be included in the .spec files. The error message should tell you which ones are missing in your own prject.

  * See this [page](https://stackoverflow.com/questions/51264169/pyinstaller-add-folder-with-images-in-exe-file
) on including files in pyinstaller --onefile




# Limitations and issues
* Hotkey recongnized is not intercepted, as in, if the capture hotkey is binded to 'x' for example, screen capturing will start but 'x' is still pressed. This might lead to undesired effects, please choose the hotkey that doesn't have conflicts in your system, I have mine on right ctrl key.

* Hotkeys will not be recongnized if a program that does intercept the specific combinations is currently selected.

* Hotkeys are not recongnized if the selected program has a higher level of privilage, for exmaple task manager, or program started as admin. Check 'start as admin' in the program or in windows properties to work around this.

* The Ui is built with tkinter, so the interface looks pretty utilitarian(ugly), but thankfully the user won't interact much with it. Some ui features wouldn't be implemented due to tkinter limitations.

* Memory usage is slightly higher, and also high cpu usage when dragging snapshots(tkinter does not support draggable window, so a costly work around is used). So this program might choke on very low end systems, maybe.

* gradual decrease in code coherency...

#
please let me know if there are any issues with is program :vv

