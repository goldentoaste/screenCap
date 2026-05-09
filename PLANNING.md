# Planning

## Linux Exception HELL
* I AM IN HELL
* only look into ubuntu for now
### Ubuntu/GNOME

#### Screenshot
* x11 screenshot is sandboxed, wayland is also locked down hell
* Use cli utils in a subprocess to screenshot.
    * 2 options, screenshot to disk, in load from disk.
    * Or use some complicated pipesetup, might be over kill

#### Window Positioning/Borderless window.
* investigating.


## Snapshot
### Window Positioning
* Windows
    - native events, processing WM_NCHITTEST events, def over kill.
    - revisit Calc size message in future, maybe, for only overriding some of native window manager.

    
### Crop
* Initial full screen crop seems smooth
* Secondary crop very jank rn
    + crop box is not contained within margin
    + after crop, margin is not hidden
    + significant visual artifact/flicker when margin is shown/hidden

### Context
* Not started, awaiting context menu manager

### Integration with recycle
* not started

### Paint
* Reference and evaluate previous work (screencap/legacy)
* Investigate in performance optimizations, such as quadtrees
* Definitely reduce complexity of code.
* Lots of buttons here:
    + integrate with key manager
    + provide help menu and other visual ques

### Quick Crop
* Confirm crop immediately when user releases press on selection box.
* Make it a toggle, when disable:
    + allow selection repositioning (done)
    + show crop menu buttons
        - ui done
        - positioning?
        - button functionality?

## Dock Widgets
* Investigate ways the app can be used if a keyboard is not present.


## System Tray button
* Use QT builtin solutions as much as possible
* Hopefully not windows exclusive
* Mostly same options as legacy

## Recycle Bin
* Not started
* Consider saving images to disk in another thread to avoid blocking ui, noticeable in case of larger images


## Context Menu Manager
* TBD (to be designed :P)

## Hotkey
### win32
* Done, hotkey for local and global management is implemented.
* Global implemented using `user32.RegisterHotKey`
* Local implemented pure QT

### Linux
* Shares local manager with win32, probs.
* Global, options:
    + key logger, refer to "KeyMaster" project. Need user to manually add itself to the user input group. (Not ideal for this application)
    + investigate wayland exclusive solutions, x11 support not planned.

### MacOs
* TDB, when have access to mac hardware

## Config
* See implementation notes in `Config.py`.
* Mostly happy with the implementation, I consider it done for good.
* Supported config types: `int, float, str, bool, list`, the list can contain any primitives, but no nesting.
* Future:
    + support dict data type?
    + improve write performance by only updating line containing the param that changed during runtime.
    + use python context manager (`with ... as ...:`) to assist with batch updates.


## MISC
* Update dependencies to latest:
    + nuitka: https://nuitka.net/posts/nuitka-release-40.html
    + python 3.14

## Memory saving
* ~~Allow bit depth select~~. This doesn't help, when displayed on screen, the image is converted to monitor's color space anyways
* Allow down sample, in case of large monitor
    + This is promising, save the full image to disk, but display a downscaled image to screen.
    + This should result in less memory use.
