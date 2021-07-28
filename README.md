# screenCap

A Windows(only) program made in python with the intention to replicate a old Japanese program named 'SETUNA', which lacks an English translation and has minor graphics compatibilities issues with modern systems.

This program allows you to take screenshots, crop a section of it, and pin it to be always on top, along with many other features for productivity gains.

Here is a [modernized](https://github.com/tylearymf/SETUNA2) version of SETUNA, but it is not in English.(And I rather write my own program instead of translating this one :P)

#

![example](https://i.imgur.com/3e8YwWm.png)

![menu](https://i.imgur.com/k2UF41x.png)

# Usage

## Main menu:

- ✔ Run on startup: to run screenCap on system startup. (done by placing a shortcut in ~Users\{user name}\AppData\Roaming\Microsoft\Windows )

- ✔ Minimize to tray: to put program in system instead of exiting when the X button at the upper right corner is pressed.

- ✔ Start minimized: to minimize to sys tray when the program starts.

- ✔ Start as Admin: to restart screenCap with admin privileges, and to automatically get admin privileges in subsequent launches.

- Recycle bin capacity: set the number of recently closed images to keep in a 'recycling bin'. Click the 'Recycling bin' Button to open that menu, and click on any image to summon them back.

- Hotkey for screen capture: click the blank button and press a combination of keys of your choice to set a hotkey to do a screen capture. Click the 'Clear' button to rebind hotkey.

## For each snapshot:

- Right click to bring up context menu (as shown in the image above)

- Select 'Crop' to further crop snapshot

- Select 'Recycle Bin' to open the Recycle Bin menu :v

- Ctrl+C: copy image to clip
- Ctrl+X: copy and close the selected snapshot
- Ctrl+V: create a snapshot from image in clipboard
- Ctrl+S: save image(brings up a save file window)
- plus or minus key to enlarge or shrink image
- Double click to minimize the snapshot to save screen space

# Dependencies

- Pillow, for image processing
- desktopmagic, for advance screen capturing
- pywin32, for interaction with Windows

  - Note: win32ui have issues with python3.9, see this [page](https://github.com/mhammond/pywin32/issues/1593) for a .whl pack to fix this.

- tendo, for tendo.singleton that ensures only 1 instance of the program is running.

  - Note: tendo might not import correctly in recent python versions. `os.environ["PBR_VERSION"] = "4.0.2"` is needed before the [import](https://blog.csdn.net/wzh200x/article/details/111185209).

- pynput, for keyboard handling
  - pynput is a pretty feature rich module, supports both mouse and keyboard handlings. However it is not very intuitive to work with(need some workarounds for non trivial usages)
- infi.systray, for system tray icon

  - Note: infi.systray is not well supported for python3, using the fix mentioned [here](https://github.com/Infinidat/infi.systray/issues/32) is recommended. Also, pystray have better features and is better supported than infi.systray. However pystray can only run the main thread, so everything freezes when the icon starts. Thus infi.systray is used for this project.

- configparser, to handling .ini config

- pythoncom, ctypes, for handling admin permissions

- pyinstaller, to pack the project to exe(the .spec file is included in the project).

  - Note: pynput, tendo, desktopmagic and infi.systray have hiddenimports that needs to be included in the .spec files. The error message should tell you which ones are missing in your own project.

  - See this [page](https://stackoverflow.com/questions/51264169/pyinstaller-add-folder-with-images-in-exe-file) on including files in pyinstaller --onefile

# Limitations and issues

- ~~Hotkey recognized is not intercepted, as in, if the capture hotkey is bind to 'x' for example, screen capturing will start but 'x' is still pressed. This might lead to undesired effects, please choose the hotkey that doesn't have conflicts in your system, I have mine on right ctrl key.~~

- ~~Hotkeys will not be recognized if a program that does intercept the specific combinations is currently selected.~~ (The 2 above issues are now fixed.)

- Hotkeys are not recognized if the selected program has a higher level of privilege, for example task manager, or program started as admin. Check 'start as admin' in the program or in windows properties to work around this.

- The Ui is built with tkinter, so the interface looks pretty utilitarian(ugly), but thankfully the user won't interact much with it. Some ui features couldn't be implemented due to tkinter limitations.

- Memory usage is slightly high, and also high cpu usage when dragging snapshots(tkinter does not support draggable window, so a costly work around is used). So this program might choke on very low end systems, maybe.

- Order of key strokes matters, so for example ctrl + x is not the same as x + ctrl, but this shouldn't cause issues for most users. Also, capital upper and lowercase letters are different, so ctrl + x is not the same as ctrl + X, this occurs when caps lock is enabled too.

# Currently working on:
- rewrite the whole thing in pyqt5 


# ~~Currently working on:~~
- rework resizing snapshots. (drag on corners to scale)
- improve cropping. Entering cropping mode should enlarge snapshot window so that reserving edges is trivial.
- quick sketch on snapshot
- (optional/feature creep) easy way to upload images to some image hosting service, returning the link
- ctrl - z to undo closing a snapshot?
- ~~modify the update() so that only the elements that needs to be updated are updated~~
- ~~add support for windows Ui scaling~~
- ~~test in virtual machine to test for bugs/crashes in different environments
- ~~reduce launch time if possible~~(not possible, most likely)
- add right click to upload to imgur and copy link, to share images when only text is allowed
- bugs to fix: (1.recover zoom level after minimalizing)(2.minimalizing on zoomed snapshot respects zoom)(3.prevent right click on initial crop)
- ~~Suppress keyboard input for last key of hotkey combo, if [possible](https://github.com/moses-palmer/pynput/issues/170).~~
